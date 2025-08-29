"""
Scenery renderer for Observatory Scene
Provides terrain color sampling and horizon rendering with sun shading
"""
import pygame
import math
import os
from typing import Tuple, Optional
from theme import (
    SKY_COLOR,
    GROUND_COLOR,
    HORIZON_LINE_COLOR,
    NAV_OCEAN_COLOR,
    NAV_LAND_COLOR,
    NAV_MAP_FILTER_PARAMS
)

class Scenery:
    def __init__(self):
        self.world_map = None
        self.map_width = 640
        self.map_height = 320
        self._load_world_map()
        
    def _load_world_map(self):
        """Load the world map for terrain color sampling"""
        try:
            from main import get_assets_dir
            assets_dir = get_assets_dir()
            map_path = os.path.join(assets_dir, "png", "world-map.png")
            self.world_map = pygame.image.load(map_path).convert()
            self.map_width, self.map_height = self.world_map.get_size()
            print(f"✅ Scenery: Loaded world map for terrain sampling: {self.world_map.get_size()}")
        except Exception as e:
            print(f"❌ Scenery: Failed to load world map: {e}")
            # Create fallback map
            self.world_map = pygame.Surface((640, 320))
            self.world_map.fill(NAV_OCEAN_COLOR)
            # Add some basic land masses
            pygame.draw.rect(self.world_map, NAV_LAND_COLOR, (100, 80, 200, 120))  # North America
            pygame.draw.rect(self.world_map, NAV_LAND_COLOR, (350, 100, 150, 100))  # Europe
            
    def _lat_lon_to_map_coords(self, lat: float, lon: float) -> Tuple[int, int]:
        """Convert latitude/longitude to map pixel coordinates"""
        # Simple cylindrical projection (same as navigation scene)
        # Longitude: -180 to +180 maps to 0 to map_width
        x = int((lon + 180.0) * self.map_width / 360.0)
        # Latitude: +90 to -90 maps to 0 to map_height  
        y = int((90.0 - lat) * self.map_height / 180.0)
        
        # Clamp to map bounds
        x = max(0, min(x, self.map_width - 1))
        y = max(0, min(y, self.map_height - 1))
        
        return x, y
        
    def sample_terrain_color(self, lat: float, lon: float) -> Tuple[int, int, int]:
        """Sample terrain color from world map at given coordinates"""
        if not self.world_map:
            return GROUND_COLOR
            
        try:
            x, y = self._lat_lon_to_map_coords(lat, lon)
            color = self.world_map.get_at((x, y))
            return (color.r, color.g, color.b)
        except:
            return GROUND_COLOR
            
    def calculate_sun_position(self, time_info: dict) -> Tuple[float, float]:
        """Calculate sun position (subsolar point latitude/longitude)"""
        import time
        import datetime
        
        # Get current UTC time
        utc_time = time.gmtime()
        utc_hours = utc_time.tm_hour + utc_time.tm_min / 60.0 + utc_time.tm_sec / 3600.0
        utc_date = datetime.date(utc_time.tm_year, utc_time.tm_mon, utc_time.tm_mday)
        
        # Solar longitude (15 degrees per hour westward from Greenwich)
        subsolar_lon = -15.0 * (utc_hours - 12.0)
        subsolar_lon = ((subsolar_lon + 180) % 360) - 180  # Normalize to [-180, 180]
        
        # Solar latitude based on Earth's axial tilt and day of year
        max_declination = 23.44  # Earth's axial tilt in degrees
        day_of_year = utc_date.timetuple().tm_yday
        
        # Summer solstice is approximately day 172 (June 21st)
        declination_angle = (day_of_year - 172) * (2 * math.pi / 365.25)
        subsolar_lat = max_declination * math.cos(declination_angle)
        
        return subsolar_lat, subsolar_lon
        
    def calculate_tilt_from_fuel(self, fuel_state: dict) -> float:
        """Calculate airship tilt based on fuel distribution"""
        tanks = fuel_state.get("tanks", {})
        forward_tank = tanks.get("forward", {})
        aft_tank = tanks.get("aft", {})
        
        forward_level = forward_tank.get("level", 0.0)
        aft_level = aft_tank.get("level", 0.0)
        
        # Calculate weight difference (assuming equal tank capacities)
        # Positive tilt = nose up, negative = nose down
        weight_diff = aft_level - forward_level
        
        # Scale to reasonable tilt range (±15 degrees max)
        max_tilt = 15.0
        tilt = weight_diff * max_tilt / 100.0  # Assuming levels are 0-100%
        
        return max(-max_tilt, min(max_tilt, tilt))
        
    def render_horizon_360(self, surface: pygame.Surface, view_angle: float, 
                          position: dict, motion: dict, fuel_state: dict, 
                          time_info: dict, field_of_view: float = 120.0):
        """Render 360-degree horizon view with terrain colors and sun shading"""
        viewport_width = surface.get_width()
        viewport_height = surface.get_height()
        
        # Calculate sun position for shading
        sun_lat, sun_lon = self.calculate_sun_position(time_info)
        
        # Calculate airship tilt from fuel distribution
        fuel_tilt = self.calculate_tilt_from_fuel(fuel_state)
        
        # Get pitch from motion (if available) and combine with fuel tilt
        motion_pitch = motion.get("pitch", 0.0)
        total_tilt = motion_pitch + fuel_tilt
        
        # Base horizon position
        base_horizon_y = viewport_height // 2
        
        # Clear with sky color
        surface.fill(self._calculate_sky_color(time_info, sun_lat))
        
        # Generate terrain horizon line
        terrain_points = []
        num_samples = viewport_width // 2  # Sample every 2 pixels for performance
        
        current_lat = position["latitude"]
        current_lon = position["longitude"]
        
        for i in range(num_samples + 1):
            x = i * 2
            if x >= viewport_width:
                x = viewport_width - 1
                
            # Calculate viewing direction for this x position
            angle_offset = (x / viewport_width - 0.5) * field_of_view
            sample_angle = (view_angle + angle_offset) % 360.0
            
            # Sample terrain at a distance (simulate horizon distance)
            horizon_distance = 0.5  # degrees of lat/lon (about 55km)
            sample_lat, sample_lon = self._calculate_point_at_bearing(
                current_lat, current_lon, sample_angle, horizon_distance)
            
            # Get terrain color and calculate height variation
            terrain_color = self.sample_terrain_color(sample_lat, sample_lon)
            terrain_height = self._terrain_color_to_height(terrain_color)
            
            # Calculate sun shading for this direction
            shade_factor = self._calculate_sun_shading(sample_angle, sun_lat, sun_lon, 
                                                     current_lat, current_lon)
            
            # Apply tilt effect to horizon
            tilt_offset = int(total_tilt * 3)  # Scale tilt to pixels
            horizon_y = base_horizon_y + int(terrain_height) + tilt_offset
            
            terrain_points.append((x, horizon_y, terrain_color, shade_factor))
        
        # Draw terrain polygons with shaded colors
        self._draw_shaded_terrain(surface, terrain_points)
        
    def _calculate_sky_color(self, time_info: dict, sun_lat: float) -> Tuple[int, int, int]:
        """Calculate sky color based on sun position"""
        # Simple time-of-day based sky coloring
        # Could be enhanced with sun elevation angle
        base_sky = SKY_COLOR
        
        # Darken sky based on how far north/south the sun is (winter/summer effect)
        brightness_factor = 1.0 - abs(sun_lat) / 30.0  # Darker when sun is far from equator
        brightness_factor = max(0.3, min(1.0, brightness_factor))
        
        return (int(base_sky[0] * brightness_factor),
                int(base_sky[1] * brightness_factor),
                int(base_sky[2] * brightness_factor))
        
    def _calculate_point_at_bearing(self, lat: float, lon: float, 
                                   bearing: float, distance: float) -> Tuple[float, float]:
        """Calculate lat/lon at given bearing and distance from a point"""
        # Convert to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        distance_rad = math.radians(distance)
        
        # Calculate destination using great circle math
        dest_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(distance_rad) +
            math.cos(lat_rad) * math.sin(distance_rad) * math.cos(bearing_rad)
        )
        
        dest_lon_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(distance_rad) * math.cos(lat_rad),
            math.cos(distance_rad) - math.sin(lat_rad) * math.sin(dest_lat_rad)
        )
        
        # Convert back to degrees
        dest_lat = math.degrees(dest_lat_rad)
        dest_lon = math.degrees(dest_lon_rad)
        
        # Normalize longitude
        dest_lon = ((dest_lon + 180) % 360) - 180
        
        return dest_lat, dest_lon
        
    def _terrain_color_to_height(self, color: Tuple[int, int, int]) -> float:
        """Convert terrain color to height variation for horizon"""
        # Use color brightness to simulate elevation
        brightness = (color[0] + color[1] + color[2]) / 3.0
        
        # Ocean/water = lower, land = higher
        if self._is_water_color(color):
            return -5.0  # Below base horizon
        else:
            # Land height based on brightness
            return (brightness - 128) / 25.0  # ±5 pixel variation
            
    def _is_water_color(self, color: Tuple[int, int, int]) -> bool:
        """Determine if a color represents water/ocean"""
        r, g, b = color
        # Simple heuristic: blue-dominant colors are water
        return b > r and b > g and b > 80
        
    def _calculate_sun_shading(self, view_angle: float, sun_lat: float, sun_lon: float,
                              observer_lat: float, observer_lon: float) -> float:
        """Calculate sun shading factor for a viewing direction"""
        # Calculate sun bearing from observer position
        sun_bearing = self._calculate_bearing(observer_lat, observer_lon, sun_lat, sun_lon)
        
        # Calculate angle difference between view direction and sun direction
        angle_diff = abs(view_angle - sun_bearing)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
            
        # Shade factor: 1.0 = full sun, 0.5 = full shade
        max_shade_angle = 120.0  # Degrees from sun for full shade
        if angle_diff <= max_shade_angle:
            shade_factor = 0.5 + 0.5 * (1.0 - angle_diff / max_shade_angle)
        else:
            shade_factor = 0.5
            
        return shade_factor
        
    def _calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing from point 1 to point 2"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlon_rad = math.radians(lon2 - lon1)
        
        y = math.sin(dlon_rad) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))
        
        bearing_rad = math.atan2(y, x)
        bearing = math.degrees(bearing_rad)
        
        return (bearing + 360) % 360
        
    def _draw_shaded_terrain(self, surface: pygame.Surface, terrain_points: list):
        """Draw terrain with shading applied"""
        viewport_width = surface.get_width()
        viewport_height = surface.get_height()
        
        if len(terrain_points) < 2:
            return
            
        # Create ground polygon with shaded colors
        for i in range(len(terrain_points) - 1):
            x1, y1, color1, shade1 = terrain_points[i]
            x2, y2, color2, shade2 = terrain_points[i + 1]
            
            # Create trapezoid from horizon to bottom of screen
            points = [
                (x1, y1),
                (x2, y2),
                (x2, viewport_height),
                (x1, viewport_height)
            ]
            
            # Average the colors and shading
            avg_color = (
                int((color1[0] + color2[0]) / 2),
                int((color1[1] + color2[1]) / 2),
                int((color1[2] + color2[2]) / 2)
            )
            avg_shade = (shade1 + shade2) / 2
            
            # Apply shading to color
            shaded_color = (
                int(avg_color[0] * avg_shade),
                int(avg_color[1] * avg_shade),
                int(avg_color[2] * avg_shade)
            )
            
            # Draw the terrain segment
            try:
                pygame.draw.polygon(surface, shaded_color, points)
            except:
                # Fallback to simple rectangle if polygon fails
                pygame.draw.rect(surface, shaded_color, 
                               (x1, min(y1, y2), x2 - x1, viewport_height - min(y1, y2)))
                
        # Draw horizon line over terrain
        if len(terrain_points) > 1:
            horizon_points = [(x, y) for x, y, _, _ in terrain_points]
            try:
                pygame.draw.lines(surface, HORIZON_LINE_COLOR, False, horizon_points, 2)
            except:
                pass  # Skip horizon line if drawing fails
