"""
Navigation Scene for Airship Zero
World map display with position and route planning
"""
import pygame
import math
import os
from typing import List, Dict, Any, Optional

# Constants
LOGICAL_SIZE = 320
BACKGROUND_COLOR = (10, 20, 30)  # Dark blue
TEXT_COLOR = (255, 255, 255)
FOCUS_COLOR = (255, 200, 50)
POSITION_COLOR = (255, 100, 100)  # Red for current position (legacy)
AIRSHIP_COLOR = (120, 30, 30)     # Dark red for airship position marker
AIRSHIP_RANGE_COLOR = (120, 30, 30)  # Dark red for range ring (same base color)
ROUTE_COLOR = (100, 255, 100)     # Green for route
WAYPOINT_TEXT_COLOR = (90, 60, 40)  # Desaturated dark brown for waypoint text
NAV_HEADER_COLOR = (40, 60, 100)  # Blue for navigation scene

class NavigationScene:
    def __init__(self, simulator):
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focus_index = 0
        self.simulator = simulator
        self.world_map = None
        self.map_surface = None

        # Initialize with default values - will load from simulator on first update
        self.zoom_level = 1.0
        self.map_offset_x = 0.0
        self.map_offset_y = 0.0

        # Flag to track if we've loaded saved settings yet
        self.settings_loaded = False

        # Mouse dragging state
        self.is_dragging = False
        self.drag_start_pos = None
        self.drag_start_offset = None
        self.has_dragged = False  # Track if any actual dragging occurred
        self.last_drag_pos = None  # Track last mouse position during drag (logical coords)

        # Initialize widgets
        self._init_widgets()
            
    def _init_widgets(self):
        """Initialize navigation widgets"""
        self.widgets = [
            {
                "id": "position_label",
                "type": "label",
                "position": [8, 32],
                "size": [150, 16],
                "text": "POS: 40.7128°N 74.0060°W",
                "focused": False
            },
            {
                "id": "heading_label",
                "type": "label",
                "position": [170, 32],
                "size": [100, 16],
                "text": "HDG: 045°",
                "focused": False
            },
            {
                "id": "ground_speed_label",
                "type": "label",
                "position": [280, 32],
                "size": [32, 16],
                "text": "GS: 82",
                "focused": False
            },
            # Controls - circular navigation
            {
                "id": "prev_scene",
                "type": "button",
                "position": [8, 290],
                "size": [60, 24],
                "text": "< [",
                "focused": True
            },
            {
                "id": "next_scene",
                "type": "button",
                "position": [252, 290],
                "size": [60, 24],
                "text": "] >",
                "focused": False
            },
            # Zoom controls (moved up to make room)
            {
                "id": "zoom_in",
                "type": "button",
                "position": [76, 290],
                "size": [30, 24],
                "text": "+",
                "focused": False
            },
            {
                "id": "zoom_out",
                "type": "button",
                "position": [114, 290],
                "size": [30, 24],
                "text": "-",
                "focused": False
            },
            {
                "id": "center_pos",
                "type": "button",
                "position": [152, 290],
                "size": [50, 24],
                "text": "Center",
                "focused": False
            }
        ]
        
    def set_font(self, font, is_text_antialiased=False):
        """Set the font for rendering text"""
        self.font = font
        self.is_text_antialiased = is_text_antialiased
        
    def _load_world_map(self):
        """Load the world map image"""
        try:
            # Import the global assets directory function
            from main import get_assets_dir
            assets_dir = get_assets_dir()
            map_path = os.path.join(assets_dir, "png", "world-map.png")
            
            self.world_map = pygame.image.load(map_path)
            print(f"✅ Loaded world map: {self.world_map.get_size()}")
        except Exception as e:
            print(f"❌ Failed to load world map: {e}")
            # Create a simple placeholder map
            self.world_map = pygame.Surface((640, 320))
            self.world_map.fill((0, 50, 100))  # Dark blue ocean
            # Draw simple continents
            pygame.draw.rect(self.world_map, (50, 80, 50), (100, 80, 200, 120))  # North America
            pygame.draw.rect(self.world_map, (50, 80, 50), (350, 100, 150, 100))  # Europe
            
    def _lat_lon_to_map_coords(self, lat: float, lon: float) -> tuple:
        """Convert latitude/longitude to map pixel coordinates"""
        if not self.world_map:
            return (160, 160)
            
        map_w, map_h = self.world_map.get_size()
        
        # Convert to normalized coordinates (0-1)
        # Longitude: -180 to +180 -> 0 to 1
        x_norm = (lon + 180.0) / 360.0
        # Latitude: +90 to -90 -> 0 to 1 (inverted because screen Y increases downward)
        y_norm = (90.0 - lat) / 180.0
        
        # Map to pixel coordinates
        map_x = int(x_norm * map_w)
        map_y = int(y_norm * map_h)
        
        return (map_x, map_y)
        
    def _map_coords_to_lat_lon(self, map_x: int, map_y: int) -> tuple:
        """Convert map pixel coordinates to latitude/longitude"""
        if not self.world_map:
            return (0.0, 0.0)
            
        map_w, map_h = self.world_map.get_size()
        
        # Normalize coordinates (0-1)
        x_norm = map_x / map_w
        y_norm = map_y / map_h
        
        # Convert to lat/lon
        lon = (x_norm * 360.0) - 180.0  # -180 to +180
        lat = 90.0 - (y_norm * 180.0)   # +90 to -90
        
        return (lat, lon)
        
    def _screen_to_map_coords(self, screen_x: int, screen_y: int) -> Optional[tuple]:
        """Convert screen coordinates to map coordinates"""
        # Check if click is in map area (56 to 290 for Y, 8 to 312 for X)
        if not (8 <= screen_x <= LOGICAL_SIZE - 8 and 56 <= screen_y <= 290):
            return None
            
        # Convert screen coords to map area relative coords
        map_area_w = LOGICAL_SIZE - 16  # 304 pixels wide
        map_area_h = 290 - 56           # 234 pixels high
        
        rel_x = (screen_x - 8) / map_area_w
        rel_y = (screen_y - 56) / map_area_h
        
        # Get current viewport
        map_rect = self._get_visible_map_rect()
        
        # Convert relative position to actual map coordinates
        map_x = map_rect.x + (rel_x * map_rect.width)
        map_y = map_rect.y + (rel_y * map_rect.height)
        
        return (int(map_x), int(map_y))
        
    def _is_near_waypoint(self, screen_x: int, screen_y: int, threshold: int = 10) -> bool:
        """Check if screen coordinates are near the current waypoint"""
        waypoint = self.simulator.get_waypoint()
        if not waypoint:
            return False
            
        # Convert waypoint to screen coordinates
        waypoint_map_x, waypoint_map_y = self._lat_lon_to_map_coords(
            waypoint["latitude"], waypoint["longitude"]
        )
        
        # Get current viewport
        map_rect = self._get_visible_map_rect()
        
        # Check if waypoint is visible
        if not map_rect.collidepoint(waypoint_map_x, waypoint_map_y):
            return False
            
        # Convert waypoint to screen coordinates
        rel_x = (waypoint_map_x - map_rect.x) / map_rect.width
        rel_y = (waypoint_map_y - map_rect.y) / map_rect.height
        
        waypoint_screen_x = 8 + rel_x * (LOGICAL_SIZE - 16)
        waypoint_screen_y = 56 + rel_y * (290 - 56)
        
        # Check distance
        distance = math.sqrt((screen_x - waypoint_screen_x)**2 + (screen_y - waypoint_screen_y)**2)
        return distance <= threshold
        
    def _get_visible_map_rect(self) -> pygame.Rect:
        """Get the rectangle of the map that should be visible"""
        if not self.world_map:
            return pygame.Rect(0, 0, LOGICAL_SIZE, LOGICAL_SIZE)
            
        map_w, map_h = self.world_map.get_size()
        
        # Available space for map (from info area to controls)
        map_area_w = LOGICAL_SIZE - 16  # 8px margin on each side (304 pixels)
        map_area_h = 290 - 56           # From end of info area to start of controls (234 pixels)
        
        # Calculate map viewport size based on zoom
        viewport_w = int(map_area_w / self.zoom_level)
        viewport_h = int(map_area_h / self.zoom_level)
        
        # Ensure viewport is at least 1 pixel and not larger than map
        viewport_w = max(1, min(map_w, viewport_w))
        viewport_h = max(1, min(map_h, viewport_h))
        
        # Get current position to center on
        game_state = self.simulator.get_state()
        pos = game_state["navigation"]["position"]
        ship_map_x, ship_map_y = self._lat_lon_to_map_coords(pos["latitude"], pos["longitude"])
        
        # Apply manual pan offsets to the ship position
        center_x = ship_map_x + self.map_offset_x
        center_y = ship_map_y + self.map_offset_y
        
        # Calculate viewport rectangle centered on the (potentially offset) position
        view_x = center_x - viewport_w / 2
        view_y = center_y - viewport_h / 2
        
        # Clamp to map bounds
        view_x = max(0, min(map_w - viewport_w, view_x))
        view_y = max(0, min(map_h - viewport_h, view_y))
        
        # Round to nearest integer for pixel-perfect positioning
        return pygame.Rect(round(view_x), round(view_y), viewport_w, viewport_h)
        
    def handle_event(self, event) -> Optional[str]:
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "scene_main_menu"
            elif event.key == pygame.K_LEFTBRACKET:  # [
                return self._get_prev_scene()
            elif event.key == pygame.K_RIGHTBRACKET:  # ]
                return self._get_next_scene()
            elif event.key == pygame.K_TAB:
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self._focus_previous()
                else:
                    self._focus_next()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return self._activate_focused()
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                self._zoom_in()
            elif event.key == pygame.K_MINUS:
                self._zoom_out()
            elif event.key == pygame.K_c:
                self._center_on_position()
            # Arrow keys for map panning
            elif event.key == pygame.K_LEFT:
                self.map_offset_x = self._clamp_offset_x(self.map_offset_x - 20 / self.zoom_level)
                self._save_view_settings()
            elif event.key == pygame.K_RIGHT:
                self.map_offset_x = self._clamp_offset_x(self.map_offset_x + 20 / self.zoom_level)
                self._save_view_settings()
            elif event.key == pygame.K_UP:
                self.map_offset_y = self._clamp_offset_y(self.map_offset_y - 20 / self.zoom_level)
                self._save_view_settings()
            elif event.key == pygame.K_DOWN:
                self.map_offset_y = self._clamp_offset_y(self.map_offset_y + 20 / self.zoom_level)
                self._save_view_settings()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                logical_pos = event.pos  # Already converted by main.py
                clicked_widget = self._get_widget_at_pos(logical_pos)
                if clicked_widget is not None:
                    self._set_focus(clicked_widget)
                    return self._activate_focused()
                else:
                    # Check if clicking on map area
                    x, y = logical_pos
                    if 8 <= x <= LOGICAL_SIZE - 8 and 56 <= y <= 290:
                        # Start drag mode (don't set waypoint yet - wait for mouse up)
                        self.is_dragging = True
                        self.drag_start_pos = logical_pos
                        self.drag_start_offset = (self.map_offset_x, self.map_offset_y)
                        self.last_drag_pos = logical_pos
                        self.has_dragged = False  # Reset drag tracking
            elif event.button == 3:  # Right click
                logical_pos = event.pos
                x, y = logical_pos
                # Check if right-clicking near waypoint to remove it
                if self._is_near_waypoint(x, y):
                    self.simulator.clear_waypoint()
            elif event.button == 4:  # Mouse wheel up - zoom in
                self._zoom_in()
            elif event.button == 5:  # Mouse wheel down - zoom out
                self._zoom_out()
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                # Check if this was a drag or a click
                if self.is_dragging and self.drag_start_pos:
                    # Determine if this was a drag based on cumulative distance
                    if not self.has_dragged:
                        # This was a click, not a drag - set waypoint now
                        x, y = self.drag_start_pos
                        if 8 <= x <= LOGICAL_SIZE - 8 and 56 <= y <= 290:
                            map_coords = self._screen_to_map_coords(x, y)
                            if map_coords:
                                # Convert map coordinates to lat/lon and set waypoint
                                lat, lon = self._map_coords_to_lat_lon(map_coords[0], map_coords[1])
                                self.simulator.set_waypoint(lat, lon)
                    else:
                        # This was a drag - save settings after dragging is complete
                        self._save_view_settings()
                
                self.is_dragging = False
                self.drag_start_pos = None
                self.drag_start_offset = None
                self.last_drag_pos = None
                self.has_dragged = False  # Reset drag tracking
                
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging and self.last_drag_pos and self.drag_start_pos and self.drag_start_offset:
                # Calculate incremental drag delta from last position (more robust with quantized coords)
                current_pos = event.pos
                step_dx = current_pos[0] - self.last_drag_pos[0]
                step_dy = current_pos[1] - self.last_drag_pos[1]

                if step_dx != 0 or step_dy != 0:
                    # Convert screen delta to map delta (accounting for zoom)
                    map_dx = step_dx / self.zoom_level
                    map_dy = step_dy / self.zoom_level

                    # Update map offset incrementally with bounds checking
                    new_offset_x = self.map_offset_x - map_dx
                    new_offset_y = self.map_offset_y - map_dy
                    
                    # Apply bounds checking to prevent invalid offsets
                    self.map_offset_x = self._clamp_offset_x(new_offset_x)
                    self.map_offset_y = self._clamp_offset_y(new_offset_y)

                    # Update last position
                    self.last_drag_pos = current_pos

                    # Determine cumulative movement from the start for click-vs-drag
                    total_dx = current_pos[0] - self.drag_start_pos[0]
                    total_dy = current_pos[1] - self.drag_start_pos[1]
                    if abs(total_dx) > 2 or abs(total_dy) > 2:
                        self.has_dragged = True
                    
        return None
        
    def _zoom_in(self):
        """Zoom in on the map"""
        self.zoom_level = min(4.0, self.zoom_level * 1.5)
        self._save_view_settings()
        
    def _zoom_out(self):
        """Zoom out on the map"""
        self.zoom_level = max(0.25, self.zoom_level / 1.5)
        self._save_view_settings()
        
    def _center_on_position(self):
        """Center the map on current position"""
        self.map_offset_x = 0
        self.map_offset_y = 0
        self._save_view_settings()
        
    def _save_view_settings(self):
        """Save current zoom and pan settings to simulator"""
        self.simulator.set_navigation_view(self.zoom_level, self.map_offset_x, self.map_offset_y)
        
    def _load_view_settings(self):
        """Load zoom and pan settings from simulator (called on first update)"""
        if not self.settings_loaded:
            nav_view = self.simulator.get_navigation_view()
            self.zoom_level = nav_view["zoomLevel"]
            # Apply bounds checking to loaded offsets in case saved data is invalid
            self.map_offset_x = self._clamp_offset_x(nav_view["offsetX"])
            self.map_offset_y = self._clamp_offset_y(nav_view["offsetY"])
            self.settings_loaded = True
    
    def _clamp_offset_x(self, offset_x: float) -> float:
        """Clamp horizontal offset to valid bounds"""
        if not self.world_map:
            return 0.0
            
        map_w, map_h = self.world_map.get_size()
        viewport_w = int((LOGICAL_SIZE - 16) / self.zoom_level)
        viewport_w = max(1, min(map_w, viewport_w))
        
        # Get ship position
        game_state = self.simulator.get_state()
        pos = game_state["navigation"]["position"]
        ship_map_x, ship_map_y = self._lat_lon_to_map_coords(pos["latitude"], pos["longitude"])
        
        # Calculate bounds to keep viewport within map
        # center_x = ship_x + offset_x, viewport goes from center_x ± viewport_w/2
        min_offset = viewport_w/2 - ship_map_x  # Keeps left edge at 0
        max_offset = map_w - viewport_w/2 - ship_map_x  # Keeps right edge at map_w
        
        return max(min_offset, min(max_offset, offset_x))
    
    def _clamp_offset_y(self, offset_y: float) -> float:
        """Clamp vertical offset to valid bounds"""
        if not self.world_map:
            return 0.0
            
        map_w, map_h = self.world_map.get_size()
        viewport_h = int((290 - 56) / self.zoom_level)
        viewport_h = max(1, min(map_h, viewport_h))
        
        # Get ship position
        game_state = self.simulator.get_state()
        pos = game_state["navigation"]["position"]
        ship_map_x, ship_map_y = self._lat_lon_to_map_coords(pos["latitude"], pos["longitude"])
        
        # Calculate bounds to keep viewport within map
        # center_y = ship_y + offset_y, viewport goes from center_y ± viewport_h/2
        min_offset = viewport_h/2 - ship_map_y  # Keeps top edge at 0
        max_offset = map_h - viewport_h/2 - ship_map_y  # Keeps bottom edge at map_h
        
        return max(min_offset, min(max_offset, offset_y))
        
    def _get_widget_at_pos(self, pos) -> Optional[int]:
        """Get widget index at logical position"""
        x, y = pos
        for i, widget in enumerate(self.widgets):
            wx, wy = widget["position"]
            ww, wh = widget["size"]
            if wx <= x <= wx + ww and wy <= y <= wy + wh:
                return i
        return None
        
    def _set_focus(self, widget_index: Optional[int]):
        """Set focus to specific widget"""
        if widget_index is not None:
            # Clear old focus
            for widget in self.widgets:
                widget["focused"] = False
            # Set new focus
            if 0 <= widget_index < len(self.widgets):
                self.widgets[widget_index]["focused"] = True
                self.focus_index = widget_index
                
    def _focus_next(self):
        """Move focus to next widget"""
        current = self.focus_index
        next_index = (current + 1) % len(self.widgets)
        self._set_focus(next_index)
        
    def _focus_previous(self):
        """Move focus to previous widget"""
        current = self.focus_index
        prev_index = (current - 1) % len(self.widgets)
        self._set_focus(prev_index)
        
    def _activate_focused(self) -> Optional[str]:
        """Activate the currently focused widget"""
        if 0 <= self.focus_index < len(self.widgets):
            widget = self.widgets[self.focus_index]
            widget_id = widget["id"]
            
            if widget_id == "prev_scene":
                return self._get_prev_scene()
            elif widget_id == "next_scene":
                return self._get_next_scene()
            elif widget_id == "zoom_in":
                self._zoom_in()
            elif widget_id == "zoom_out":
                self._zoom_out()
            elif widget_id == "center_pos":
                self._center_on_position()
                
        return None
        
    def _get_prev_scene(self) -> str:
        """Get the previous scene in circular order"""
        return "scene_engine_room"
    
    def _get_next_scene(self) -> str:
        """Get the next scene in circular order"""
        return "scene_fuel"
        
    def update(self, dt: float):
        """Update the scene with game state"""
        # Load saved settings on first update (after game state is loaded)
        self._load_view_settings()
        
        # Ensure map is loaded
        if self.world_map is None:
            self._load_world_map()
            
        # Get current state from simulator
        game_state = self.simulator.get_state()
        nav = game_state["navigation"]
        position = nav["position"]
        motion = nav["motion"]
        
        # Update position display
        lat_str = f"{abs(position['latitude']):.4f}°{'N' if position['latitude'] >= 0 else 'S'}"
        lon_str = f"{abs(position['longitude']):.4f}°{'E' if position['longitude'] >= 0 else 'W'}"
        self._update_widget_text("position_label", f"POS: {lat_str} {lon_str}")
        
        # Update heading and speed
        self._update_widget_text("heading_label", f"HDG: {position['heading']:03.0f}°")
        self._update_widget_text("ground_speed_label", f"GS: {motion['groundSpeed']:.0f}")
        
    def _update_widget_text(self, widget_id: str, new_text: str):
        """Update widget text"""
        for widget in self.widgets:
            if widget["id"] == widget_id:
                widget["text"] = new_text
                break
    
    def _calculate_destination(self, lat1, lon1, bearing, distance_nm):
        """
        Calculate destination coordinates using great circle navigation
        
        Args:
            lat1: Starting latitude in degrees
            lon1: Starting longitude in degrees  
            bearing: True bearing in degrees (0-360)
            distance_nm: Distance in nautical miles
            
        Returns:
            tuple: (end_latitude, end_longitude) in degrees
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        bearing_rad = math.radians(bearing)
        
        # Earth's radius in nautical miles (approximately)
        earth_radius_nm = 3440.065  # nautical miles
        
        # Angular distance
        angular_distance = distance_nm / earth_radius_nm
        
        # Calculate destination latitude
        lat2_rad = math.asin(
            math.sin(lat1_rad) * math.cos(angular_distance) +
            math.cos(lat1_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
        )
        
        # Calculate destination longitude
        delta_lon_rad = math.atan2(
            math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat1_rad),
            math.cos(angular_distance) - math.sin(lat1_rad) * math.sin(lat2_rad)
        )
        
        lon2_rad = lon1_rad + delta_lon_rad
        
        # Normalize longitude to [-180, 180] range
        lon2_rad = ((lon2_rad + 3 * math.pi) % (2 * math.pi)) - math.pi
        
        # Convert back to degrees
        lat2 = math.degrees(lat2_rad)
        lon2 = math.degrees(lon2_rad)
        
        return lat2, lon2

    def _generate_great_circle_arc(self, lat1, lon1, lat2, lon2, num_points=50):
        """
        Generate points along a great circle arc between two points
        
        Args:
            lat1, lon1: Start point in degrees
            lat2, lon2: End point in degrees
            num_points: Number of interpolated points to generate
            
        Returns:
            list: List of (lat, lon) tuples along the great circle
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Calculate the angular distance between points
        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        angular_distance = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        points = []
        
        for i in range(num_points + 1):
            fraction = i / num_points
            
            # Spherical linear interpolation (slerp)
            if angular_distance == 0:
                # Points are the same
                lat_rad = lat1_rad
                lon_rad = lon1_rad
            else:
                A = math.sin((1 - fraction) * angular_distance) / math.sin(angular_distance)
                B = math.sin(fraction * angular_distance) / math.sin(angular_distance)
                
                x = A * math.cos(lat1_rad) * math.cos(lon1_rad) + B * math.cos(lat2_rad) * math.cos(lon2_rad)
                y = A * math.cos(lat1_rad) * math.sin(lon1_rad) + B * math.cos(lat2_rad) * math.sin(lon2_rad)
                z = A * math.sin(lat1_rad) + B * math.sin(lat2_rad)
                
                lat_rad = math.atan2(z, math.sqrt(x*x + y*y))
                lon_rad = math.atan2(y, x)
            
            # Convert back to degrees and normalize longitude
            lat = math.degrees(lat_rad)
            lon = math.degrees(lon_rad)
            lon = ((lon + 180) % 360) - 180  # Normalize to [-180, 180]
            
            points.append((lat, lon))
        
        return points

    def _generate_range_ring_points(self, center_lat, center_lon, range_nm, num_points=72):
        """
        Generate points around a range ring on the sphere
        
        Args:
            center_lat, center_lon: Center point in degrees
            range_nm: Range in nautical miles
            num_points: Number of points around the circle (default 72 = 5° intervals)
            
        Returns:
            list: List of (lat, lon) tuples around the range ring
        """
        points = []
        
        for i in range(num_points):
            bearing = (i * 360.0) / num_points  # Bearing in degrees
            lat, lon = self._calculate_destination(center_lat, center_lon, bearing, range_nm)
            points.append((lat, lon))
        
        # Close the ring by adding the first point again
        if points:
            points.append(points[0])
            
        return points

    def _calculate_day_night_boundary(self, utc_time_hours):
        """
        Calculate the day/night terminator line for a given UTC time
        
        Args:
            utc_time_hours: UTC time as decimal hours (0-24)
            
        Returns:
            list: List of (lat, lon) tuples defining the terminator
        """
        import time
        import datetime
        
        # Calculate sun's longitude based on UTC time
        # Sun's longitude = -15 * (UTC_hours - 12) degrees
        # At UTC 12:00, sun is at longitude 0° (Greenwich)
        sun_longitude = -15.0 * (utc_time_hours - 12.0)
        sun_longitude = ((sun_longitude + 180) % 360) - 180  # Normalize to [-180, 180]
        
        # For simplicity, assume sun's declination is 0° (equinox)
        # In reality, this varies seasonally between ±23.44°
        sun_declination = 0.0
        
        # Generate terminator points
        terminator_points = []
        
        # Generate points along the terminator (90° from sun position)
        for lat in range(-90, 91, 5):  # Every 5 degrees of latitude
            lat_rad = math.radians(lat)
            sun_decl_rad = math.radians(sun_declination)
            
            # Calculate longitude where sun angle is 90° (terminator)
            # This is a simplified calculation - the actual terminator is more complex
            try:
                cos_hour_angle = -math.tan(lat_rad) * math.tan(sun_decl_rad)
                
                if cos_hour_angle > 1:
                    # Polar night
                    hour_angle = math.pi
                elif cos_hour_angle < -1:
                    # Polar day
                    hour_angle = 0
                else:
                    hour_angle = math.acos(cos_hour_angle)
                
                # Convert hour angle to longitude offset from sun
                lon_offset = math.degrees(hour_angle)
                
                # Two points on terminator (sunrise and sunset longitudes)
                lon1 = sun_longitude + lon_offset
                lon2 = sun_longitude - lon_offset
                
                # Normalize longitudes
                lon1 = ((lon1 + 180) % 360) - 180
                lon2 = ((lon2 + 180) % 360) - 180
                
                terminator_points.append((lat, lon1))
                terminator_points.append((lat, lon2))
                
            except (ValueError, ZeroDivisionError):
                # Handle edge cases at poles
                continue
        
        # Sort points to create a continuous boundary
        terminator_points.sort(key=lambda p: (p[1], p[0]))  # Sort by longitude, then latitude
        
        return terminator_points

    def _draw_spherical_line_segments(self, surface, color, lat_lon_points, width, alpha, map_rect, display_w, display_h, max_range):
        """
        Draw a series of connected line segments from spherical coordinates
        
        Args:
            surface: Surface to draw on (should be the large overlay)
            color: Line color (RGB tuple)
            lat_lon_points: List of (lat, lon) tuples
            width: Line width in pixels
            alpha: Alpha transparency (0-255)
            map_rect: Current map viewport rectangle
            display_w, display_h: Display area dimensions
            max_range: Margin size for overlay
        """
        if len(lat_lon_points) < 2:
            return
            
        # Convert all lat/lon points to overlay coordinates
        overlay_points = []
        for lat, lon in lat_lon_points:
            map_x, map_y = self._lat_lon_to_map_coords(lat, lon)
            
            # Calculate position relative to viewport (can be outside)
            rel_x = (map_x - map_rect.x) / map_rect.width
            rel_y = (map_y - map_rect.y) / map_rect.height
            
            # Convert to overlay coordinates
            overlay_x = rel_x * display_w + max_range
            overlay_y = rel_y * display_h + max_range
            
            overlay_points.append((overlay_x, overlay_y))
        
        # Draw connected line segments
        for i in range(len(overlay_points) - 1):
            start_pos = overlay_points[i]
            end_pos = overlay_points[i + 1]
            
            # Skip segments that are too long (likely wrapping around the world)
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            segment_length = math.sqrt(dx*dx + dy*dy)
            
            # If segment is very long, it's probably wrapping - skip it
            # This prevents drawing lines across the entire map
            max_segment_length = max(display_w, display_h) * 0.5
            if segment_length < max_segment_length:
                self._draw_transparent_line(surface, color, 
                                          (int(start_pos[0]), int(start_pos[1])),
                                          (int(end_pos[0]), int(end_pos[1])),
                                          width, alpha)

    def _draw_day_night_overlay(self, surface):
        """
        Draw day/night shading overlay on the map
        """
        import time
        
        # Get current UTC time
        utc_time = time.gmtime()
        utc_hours = utc_time.tm_hour + utc_time.tm_min / 60.0 + utc_time.tm_sec / 3600.0
        
        # Create overlay surface for day/night shading
        display_w = LOGICAL_SIZE - 16   # 304 pixels
        display_h = 290 - 56            # 234 pixels
        
        # Create an overlay that matches the current map viewport
        overlay = pygame.Surface((display_w, display_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))  # Fully transparent
        
        # Get current map viewport
        map_rect = self._get_visible_map_rect()
        
        # Calculate day/night regions
        terminator_points = self._calculate_day_night_boundary(utc_hours)
        
        if len(terminator_points) > 3:
            # Convert terminator points to screen coordinates
            screen_points = []
            for lat, lon in terminator_points:
                map_x, map_y = self._lat_lon_to_map_coords(lat, lon)
                
                # Check if point is in viewport
                if map_rect.collidepoint(map_x, map_y):
                    rel_x = (map_x - map_rect.x) / map_rect.width
                    rel_y = (map_y - map_rect.y) / map_rect.height
                    
                    screen_x = rel_x * display_w
                    screen_y = rel_y * display_h
                    screen_points.append((int(screen_x), int(screen_y)))
            
            # Draw night-time shading (simplified - just shade the western hemisphere)
            # This is a placeholder - a proper implementation would need more sophisticated
            # polygon filling based on the terminator curve
            if len(screen_points) > 0:
                # Create a simple night overlay - shade areas west of the sun
                night_surface = pygame.Surface((display_w, display_h), pygame.SRCALPHA)
                night_surface.fill((0, 0, 50, 25))  # Dark blue with 10% opacity
                
                # For now, apply uniform shading - in a real implementation,
                # you'd calculate which areas are in shadow based on the terminator
                overlay.blit(night_surface, (0, 0))
        
        # Blit the day/night overlay to the main surface
        surface.blit(overlay, (8, 56))

    def _draw_transparent_circle(self, surface, color, center, radius, alpha):
        """Draw a circle with transparency"""
        # Create a temporary surface with per-pixel alpha
        temp_surface = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
        # Draw the circle on the temporary surface
        pygame.draw.circle(temp_surface, (*color, alpha), (radius + 1, radius + 1), radius)
        # Blit to the main surface
        surface.blit(temp_surface, (center[0] - radius - 1, center[1] - radius - 1))
    
    def _draw_transparent_line(self, surface, color, start_pos, end_pos, width, alpha):
        """Draw a line with transparency"""
        # Calculate line dimensions
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # Calculate bounding box for the line (accounting for negative deltas)
        min_x = min(0, dx) - width
        max_x = max(0, dx) + width
        min_y = min(0, dy) - width
        max_y = max(0, dy) + width
        
        temp_width = int(max_x - min_x) + 1
        temp_height = int(max_y - min_y) + 1
        
        # Create a temporary surface large enough for the line in any direction
        temp_surface = pygame.Surface((temp_width, temp_height), pygame.SRCALPHA)
        
        # Calculate positions in the temporary surface
        start_temp = (-min_x, -min_y)
        end_temp = (dx - min_x, dy - min_y)
        
        # Draw the line on the temporary surface
        pygame.draw.line(temp_surface, (*color, alpha), start_temp, end_temp, width)
        
        # Blit to the main surface at the correct position
        surface.blit(temp_surface, (start_pos[0] + min_x, start_pos[1] + min_y))
    
    def _draw_transparent_circle_outline(self, surface, color, center, radius, alpha):
        """Draw a circle outline with transparency"""
        # Create a temporary surface with per-pixel alpha
        temp_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        # Draw the circle outline on the temporary surface
        pygame.draw.circle(temp_surface, (*color, alpha), (radius + 2, radius + 2), radius, 1)
        # Blit to the main surface
        surface.blit(temp_surface, (center[0] - radius - 2, center[1] - radius - 2))
                
    def render(self, surface):
        """Render the navigation scene"""
        surface.fill(BACKGROUND_COLOR)
        
        # Draw colored title header
        pygame.draw.rect(surface, NAV_HEADER_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(surface, TEXT_COLOR, (0, 0, 320, 24), 1)
        
        # Centered title
        if self.font:
            title_text = self.font.render("NAVIGATION", self.is_text_antialiased, TEXT_COLOR)
            title_x = (320 - title_text.get_width()) // 2
            surface.blit(title_text, (title_x, 4))
        
        # Draw world map (shifted down for header)
        if self.world_map:
            self._draw_world_map(surface)
        
        # Draw day/night overlay (optional - can be enabled/disabled)
        # self._draw_day_night_overlay(surface)
        
        # Draw current position on map (with spherical geometry)
        self._draw_position_indicator(surface)
        
        # Draw waypoint on map (with spherical geometry)
        self._draw_waypoint_indicator(surface)
        
        # Draw widgets
        for widget in self.widgets:
            self._render_widget(surface, widget)
            
    def _draw_world_map(self, surface):
        """Draw the world map with current zoom and position"""
        map_rect = self._get_visible_map_rect()
        
        # Validate map rect
        if map_rect.width <= 0 or map_rect.height <= 0:
            return
            
        # Extract the visible portion of the map
        try:
            map_section = self.world_map.subsurface(map_rect)
        except (ValueError, pygame.error):
            # Handle edge case where rect is outside map bounds or invalid
            # Create a fallback surface
            map_section = pygame.Surface((max(1, map_rect.width), max(1, map_rect.height)))
            map_section.fill((0, 50, 100))  # Ocean blue
            
        # Scale to fit the display area
        display_w = LOGICAL_SIZE - 16   # 304 pixels
        display_h = 290 - 56            # 234 pixels
        
        if map_section.get_width() > 0 and map_section.get_height() > 0:
            scaled_map = pygame.transform.scale(map_section, (display_w, display_h))
            # Draw to surface (shifted down for header)
            surface.blit(scaled_map, (8, 56))
        
    def _draw_position_indicator(self, surface):
        """Draw current position on the map using spherical geometry"""
        game_state = self.simulator.get_state()
        position = game_state["navigation"]["position"]
        motion = game_state["navigation"]["motion"]
        
        # Create larger overlay subsurface to accommodate lines extending in all directions
        display_w = LOGICAL_SIZE - 16   # 304 pixels
        display_h = 290 - 56            # 234 pixels
        
        # Make overlay larger to accommodate range lines extending beyond visible area
        max_range = 500  # Maximum possible range pixels we might need
        overlay_w = display_w + max_range * 2  # Extra space on both sides
        overlay_h = display_h + max_range * 2  # Extra space top and bottom
        
        overlay = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))  # Fully transparent background
        
        # Get ship's position
        current_lat = position["latitude"]
        current_lon = position["longitude"]
        bearing = position["heading"]
        current_speed = motion.get("groundSpeed", 0)  # knots
        travel_distance_nm = current_speed * 12  # 12 hours of travel in nautical miles
        
        # Get the current viewport
        map_rect = self._get_visible_map_rect()
        
        # Calculate ship position in overlay coordinates
        ship_map_x, ship_map_y = self._lat_lon_to_map_coords(current_lat, current_lon)
        rel_x = (ship_map_x - map_rect.x) / map_rect.width
        rel_y = (ship_map_y - map_rect.y) / map_rect.height
        overlay_ship_x = rel_x * display_w + max_range
        overlay_ship_y = rel_y * display_h + max_range
        
        if travel_distance_nm > 0:
            # Draw spherical range ring using interpolated points
            range_ring_points = self._generate_range_ring_points(current_lat, current_lon, travel_distance_nm, 72)
            self._draw_spherical_line_segments(overlay, AIRSHIP_RANGE_COLOR, range_ring_points, 
                                             1, 64, map_rect, display_w, display_h, max_range)  # 25% opacity
            
            # Draw great circle heading line using interpolated points
            end_lat, end_lon = self._calculate_destination(current_lat, current_lon, bearing, travel_distance_nm)
            heading_line_points = self._generate_great_circle_arc(current_lat, current_lon, end_lat, end_lon, 25)
            self._draw_spherical_line_segments(overlay, AIRSHIP_RANGE_COLOR, heading_line_points,
                                             1, 64, map_rect, display_w, display_h, max_range)  # 25% opacity
        
        # Draw position marker (centered on ship position)
        marker_radius = 3  # 7 pixel diameter (odd number)
        self._draw_transparent_circle(overlay, AIRSHIP_COLOR, 
                                    (int(overlay_ship_x), int(overlay_ship_y)), 
                                    marker_radius, 191)  # 75% opacity (191/255)
        
        # Blit only the visible portion of the overlay onto the main surface
        # Extract the display-sized portion from the center of the larger overlay
        visible_rect = pygame.Rect(max_range, max_range, display_w, display_h)
        visible_portion = overlay.subsurface(visible_rect)
        surface.blit(visible_portion, (8, 56))
                           
    def _draw_waypoint_indicator(self, surface):
        """Draw waypoint on the map using spherical geometry"""
        waypoint = self.simulator.get_waypoint()
        if not waypoint:
            return
        
        # Create larger overlay subsurface for waypoint elements (matching position indicator)
        display_w = LOGICAL_SIZE - 16   # 304 pixels
        display_h = 290 - 56            # 234 pixels
        
        # Make overlay larger to accommodate dashed lines extending beyond visible area
        max_range = 500  # Maximum possible range pixels we might need
        overlay_w = display_w + max_range * 2  # Extra space on both sides
        overlay_h = display_h + max_range * 2  # Extra space top and bottom
        
        overlay = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))  # Fully transparent background
        
        # Get current positions
        game_state = self.simulator.get_state()
        position = game_state["navigation"]["position"]
        ship_lat = position["latitude"]
        ship_lon = position["longitude"]
        waypoint_lat = waypoint["latitude"]
        waypoint_lon = waypoint["longitude"]
        
        # Get the current viewport
        map_rect = self._get_visible_map_rect()
        
        # Calculate waypoint position in overlay coordinates
        waypoint_map_x, waypoint_map_y = self._lat_lon_to_map_coords(waypoint_lat, waypoint_lon)
        rel_x = (waypoint_map_x - map_rect.x) / map_rect.width
        rel_y = (waypoint_map_y - map_rect.y) / map_rect.height
        overlay_waypoint_x = rel_x * display_w + max_range
        overlay_waypoint_y = rel_y * display_h + max_range
        
        # Draw great circle dashed line from ship to waypoint using interpolated points
        great_circle_points = self._generate_great_circle_arc(ship_lat, ship_lon, waypoint_lat, waypoint_lon, 30)
        self._draw_spherical_dashed_line(overlay, AIRSHIP_RANGE_COLOR, great_circle_points,
                                       1, 64, map_rect, display_w, display_h, max_range, dash_length=8)  # 25% opacity
        
        # Draw waypoint marker using consistent dark red colors
        # Outer circle with transparency (same as range ring)
        self._draw_transparent_circle(overlay, AIRSHIP_RANGE_COLOR, 
                                    (int(overlay_waypoint_x), int(overlay_waypoint_y)), 
                                    5, 64)  # 25% opacity (same as range elements)
        
        # Inner circle with higher opacity (same as ship dot)
        self._draw_transparent_circle(overlay, AIRSHIP_COLOR, 
                                    (int(overlay_waypoint_x), int(overlay_waypoint_y)), 
                                    3, 191)  # 75% opacity (same as ship dot)
        
        # Draw waypoint information with semi-transparent dark brown text
        if self.font:
            distance = self.simulator.calculate_distance_to_waypoint()
            bearing = self.simulator.calculate_bearing_to_waypoint()
            
            # Distance and bearing above the waypoint
            if distance is not None and bearing is not None:
                label_above = f"{distance:.1f}nm {bearing:03.0f}°"
                self._render_transparent_text(overlay, label_above, 
                                            (int(overlay_waypoint_x), int(overlay_waypoint_y - 20)), 
                                            WAYPOINT_TEXT_COLOR, 128, centered=True)
            
            # Lat/lon below the waypoint
            lat_str = f"{abs(waypoint['latitude']):.3f}°{'N' if waypoint['latitude'] >= 0 else 'S'}"
            lon_str = f"{abs(waypoint['longitude']):.3f}°{'E' if waypoint['longitude'] >= 0 else 'W'}"
            label_below = f"{lat_str} {lon_str}"
            self._render_transparent_text(overlay, label_below, 
                                        (int(overlay_waypoint_x), int(overlay_waypoint_y + 8)), 
                                        WAYPOINT_TEXT_COLOR, 128, centered=True)
        
        # Blit only the visible portion of the overlay onto the main surface
        # Extract the display-sized portion from the center of the larger overlay
        visible_rect = pygame.Rect(max_range, max_range, display_w, display_h)
        visible_portion = overlay.subsurface(visible_rect)
        surface.blit(visible_portion, (8, 56))
    
    def _draw_spherical_dashed_line(self, surface, color, lat_lon_points, width, alpha, map_rect, display_w, display_h, max_range, dash_length=10):
        """
        Draw a dashed line along spherical coordinates
        
        Args:
            surface: Surface to draw on (should be the large overlay)
            color: Line color (RGB tuple)
            lat_lon_points: List of (lat, lon) tuples defining the path
            width: Line width in pixels
            alpha: Alpha transparency (0-255)
            map_rect: Current map viewport rectangle
            display_w, display_h: Display area dimensions
            max_range: Margin size for overlay
            dash_length: Length of each dash in pixels
        """
        if len(lat_lon_points) < 2:
            return
            
        # Convert all lat/lon points to overlay coordinates
        overlay_points = []
        for lat, lon in lat_lon_points:
            map_x, map_y = self._lat_lon_to_map_coords(lat, lon)
            
            # Calculate position relative to viewport (can be outside)
            rel_x = (map_x - map_rect.x) / map_rect.width
            rel_y = (map_y - map_rect.y) / map_rect.height
            
            # Convert to overlay coordinates
            overlay_x = rel_x * display_w + max_range
            overlay_y = rel_y * display_h + max_range
            
            overlay_points.append((overlay_x, overlay_y))
        
        # Calculate cumulative distances along the path
        cumulative_distances = [0]
        for i in range(1, len(overlay_points)):
            dx = overlay_points[i][0] - overlay_points[i-1][0]
            dy = overlay_points[i][1] - overlay_points[i-1][1]
            segment_length = math.sqrt(dx*dx + dy*dy)
            
            # Skip segments that are too long (likely wrapping around the world)
            max_segment_length = max(display_w, display_h) * 0.5
            if segment_length > max_segment_length:
                # Reset distance tracking to handle world wrapping
                cumulative_distances.append(cumulative_distances[-1])
            else:
                cumulative_distances.append(cumulative_distances[-1] + segment_length)
        
        total_distance = cumulative_distances[-1]
        if total_distance == 0:
            return
        
        # Draw dashes along the path
        gap_length = dash_length  # Same length for gaps
        current_distance = 0
        drawing_dash = True  # Start with a dash
        
        while current_distance < total_distance:
            # Find segment containing current distance
            segment_index = 0
            for i in range(len(cumulative_distances) - 1):
                if cumulative_distances[i] <= current_distance <= cumulative_distances[i + 1]:
                    segment_index = i
                    break
            
            if segment_index >= len(overlay_points) - 1:
                break
                
            # Calculate position within the current segment
            segment_start_dist = cumulative_distances[segment_index]
            segment_end_dist = cumulative_distances[segment_index + 1]
            segment_total_length = segment_end_dist - segment_start_dist
            
            if segment_total_length > 0:
                segment_progress = (current_distance - segment_start_dist) / segment_total_length
                
                # Interpolate position within segment
                start_point = overlay_points[segment_index]
                end_point = overlay_points[segment_index + 1]
                
                current_x = start_point[0] + segment_progress * (end_point[0] - start_point[0])
                current_y = start_point[1] + segment_progress * (end_point[1] - start_point[1])
                
                if drawing_dash:
                    # Calculate dash end position
                    dash_end_distance = min(current_distance + dash_length, total_distance)
                    
                    # Find dash end position
                    end_segment_index = segment_index
                    for i in range(segment_index, len(cumulative_distances) - 1):
                        if cumulative_distances[i] <= dash_end_distance <= cumulative_distances[i + 1]:
                            end_segment_index = i
                            break
                    
                    if end_segment_index < len(overlay_points) - 1:
                        end_segment_start = cumulative_distances[end_segment_index]
                        end_segment_end = cumulative_distances[end_segment_index + 1]
                        end_segment_length = end_segment_end - end_segment_start
                        
                        if end_segment_length > 0:
                            end_progress = (dash_end_distance - end_segment_start) / end_segment_length
                            end_start_point = overlay_points[end_segment_index]
                            end_end_point = overlay_points[end_segment_index + 1]
                            
                            dash_end_x = end_start_point[0] + end_progress * (end_end_point[0] - end_start_point[0])
                            dash_end_y = end_start_point[1] + end_progress * (end_end_point[1] - end_start_point[1])
                            
                            # Draw the dash
                            self._draw_transparent_line(surface, color,
                                                      (int(current_x), int(current_y)),
                                                      (int(dash_end_x), int(dash_end_y)),
                                                      width, alpha)
                    
                    current_distance += dash_length
                else:
                    # Skip gap
                    current_distance += gap_length
                
                drawing_dash = not drawing_dash
            else:
                # Skip zero-length segments
                current_distance += 1

    def _render_transparent_text(self, surface, text, position, color, alpha, centered=False):
        """Render transparent text on a surface"""
        if not self.font:
            return
            
        text_surface = self.font.render(text, self.is_text_antialiased, color)
        text_surface.set_alpha(alpha)
        
        x, y = position
        if centered:
            x = x - text_surface.get_width() // 2
            
        surface.blit(text_surface, (x, y))
    
    def _draw_dashed_line(self, surface, color, start_pos, end_pos, width, alpha, dash_length=10):
        """Draw a dashed line with transparency"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Calculate line length and direction
        dx = x2 - x1
        dy = y2 - y1
        line_length = math.sqrt(dx*dx + dy*dy)
        
        if line_length == 0:
            return
            
        # Normalize direction vector
        dx_norm = dx / line_length
        dy_norm = dy / line_length
        
        # Draw dashes
        current_distance = 0
        gap_length = dash_length  # Same length for gaps
        
        while current_distance < line_length:
            # Start of current dash
            dash_start_x = x1 + dx_norm * current_distance
            dash_start_y = y1 + dy_norm * current_distance
            
            # End of current dash
            dash_end_distance = min(current_distance + dash_length, line_length)
            dash_end_x = x1 + dx_norm * dash_end_distance
            dash_end_y = y1 + dy_norm * dash_end_distance
            
            # Draw the dash
            self._draw_transparent_line(surface, color,
                                      (int(dash_start_x), int(dash_start_y)),
                                      (int(dash_end_x), int(dash_end_y)),
                                      width, alpha)
            
            # Move to next dash (skip the gap)
            current_distance += dash_length + gap_length
                           
    def _render_widget(self, surface, widget):
        """Render a single widget"""
        if widget["type"] == "label":
            self._render_label(surface, widget)
        elif widget["type"] == "button":
            self._render_button(surface, widget)
            
    def _render_label(self, surface, widget):
        """Render a label widget"""
        if self.font:
            color = FOCUS_COLOR if widget.get("focused", False) else TEXT_COLOR
            text_surface = self.font.render(widget["text"], self.is_text_antialiased, color)
            surface.blit(text_surface, widget["position"])
            
    def _render_button(self, surface, widget):
        """Render a button widget"""
        x, y = widget["position"]
        w, h = widget["size"]
        focused = widget.get("focused", False)
        
        # Button colors
        bg_color = (60, 60, 80) if not focused else (80, 80, 120)
        border_color = FOCUS_COLOR if focused else (128, 128, 128)
        text_color = FOCUS_COLOR if focused else TEXT_COLOR
        
        # Draw button
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        pygame.draw.rect(surface, border_color, (x, y, w, h), 1)
        
        # Draw text
        if self.font:
            text_surface = self.font.render(widget["text"], self.is_text_antialiased, text_color)
            text_rect = text_surface.get_rect()
            text_x = x + (w - text_rect.width) // 2
            text_y = y + (h - text_rect.height) // 2
            surface.blit(text_surface, (text_x, text_y))
