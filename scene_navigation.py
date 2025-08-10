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
        length = max(abs(dx), abs(dy), 1)
        
        # Create a temporary surface large enough for the line
        temp_surface = pygame.Surface((length + width * 2, length + width * 2), pygame.SRCALPHA)
        
        # Offset coordinates for the temporary surface
        offset_x = width
        offset_y = width
        start_temp = (start_pos[0] - start_pos[0] + offset_x, start_pos[1] - start_pos[1] + offset_y)
        end_temp = (end_pos[0] - start_pos[0] + offset_x, end_pos[1] - start_pos[1] + offset_y)
        
        # Draw the line on the temporary surface
        pygame.draw.line(temp_surface, (*color, alpha), start_temp, end_temp, width)
        
        # Blit to the main surface
        surface.blit(temp_surface, (start_pos[0] - offset_x, start_pos[1] - offset_y))
    
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
        
        # Draw current position on map
        self._draw_position_indicator(surface)
        
        # Draw waypoint on map
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
        """Draw current position on the map using overlay subsurface"""
        game_state = self.simulator.get_state()
        position = game_state["navigation"]["position"]
        motion = game_state["navigation"]["motion"]
        
        # Create transparent overlay subsurface for navigation elements
        display_w = LOGICAL_SIZE - 16   # 304 pixels
        display_h = 290 - 56            # 234 pixels
        overlay = pygame.Surface((display_w, display_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))  # Fully transparent background
        
        # Get ship's absolute position in map coordinates
        ship_map_x, ship_map_y = self._lat_lon_to_map_coords(position["latitude"], position["longitude"])
        
        # Get the current viewport
        map_rect = self._get_visible_map_rect()
        
        # Calculate ship position relative to the visible map area (can be outside viewport)
        rel_x = (ship_map_x - map_rect.x) / map_rect.width
        rel_y = (ship_map_y - map_rect.y) / map_rect.height
        
        # Convert to overlay coordinates (can be negative or > display size)
        overlay_ship_x = rel_x * display_w
        overlay_ship_y = rel_y * display_h
        
        # Draw 12-hour travel range using proper great circle navigation
        current_speed = motion.get("groundSpeed", 0)  # knots
        travel_distance_nm = current_speed * 12  # 12 hours of travel in nautical miles
        
        if travel_distance_nm > 0:
            # Calculate destination using great circle navigation
            current_lat = position["latitude"]
            current_lon = position["longitude"]
            bearing = position["heading"]
            
            # Calculate end position after 12 hours of travel on great circle
            end_lat, end_lon = self._calculate_destination(current_lat, current_lon, bearing, travel_distance_nm)
            
            # Convert end position to map coordinates
            end_map_x, end_map_y = self._lat_lon_to_map_coords(end_lat, end_lon)
            
            # Calculate end position relative to the visible map area (can be outside viewport)
            end_rel_x = (end_map_x - map_rect.x) / map_rect.width
            end_rel_y = (end_map_y - map_rect.y) / map_rect.height
            
            # Convert to overlay coordinates
            overlay_end_x = end_rel_x * display_w
            overlay_end_y = end_rel_y * display_h
            
            # Calculate actual distance in overlay pixels for range circle
            dx = overlay_end_x - overlay_ship_x
            dy = overlay_end_y - overlay_ship_y
            range_pixels = math.sqrt(dx*dx + dy*dy)
            
            # Draw range circle outline only using calculated radius
            if range_pixels > 5:  # Only draw if reasonably visible
                self._draw_transparent_circle_outline(overlay, AIRSHIP_RANGE_COLOR, 
                                                     (int(overlay_ship_x), int(overlay_ship_y)), 
                                                     int(range_pixels), 64)  # 25% opacity (64/255)
                
                # Draw heading line to range circle edge (not to end position)
                heading_rad = math.radians(bearing)
                line_end_x = overlay_ship_x + math.sin(heading_rad) * range_pixels
                line_end_y = overlay_ship_y - math.cos(heading_rad) * range_pixels
                
                self._draw_transparent_line(overlay, AIRSHIP_RANGE_COLOR,
                                          (int(overlay_ship_x) - 1, int(overlay_ship_y) - 1), 
                                          (int(line_end_x) - 1, int(line_end_y) - 1), 1, 128)  # 50% opacity, 1px width
        
        # Draw position marker (centered on ship position)
        marker_radius = 3  # 7 pixel diameter (odd number)
        self._draw_transparent_circle(overlay, AIRSHIP_COLOR, 
                                    (int(overlay_ship_x), int(overlay_ship_y)), 
                                    marker_radius, 191)  # 75% opacity (191/255)
        
        # Blit the overlay onto the main surface
        surface.blit(overlay, (8, 56))
                           
    def _draw_waypoint_indicator(self, surface):
        """Draw waypoint on the map using overlay subsurface"""
        waypoint = self.simulator.get_waypoint()
        if not waypoint:
            return
        
        # Create transparent overlay subsurface for waypoint elements
        display_w = LOGICAL_SIZE - 16   # 304 pixels
        display_h = 290 - 56            # 234 pixels
        overlay = pygame.Surface((display_w, display_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))  # Fully transparent background
            
        # Get waypoint position in map coordinates
        waypoint_map_x, waypoint_map_y = self._lat_lon_to_map_coords(
            waypoint["latitude"], waypoint["longitude"]
        )
        
        # Get the current viewport
        map_rect = self._get_visible_map_rect()
        
        # Calculate waypoint position relative to the visible map area (can be outside viewport)
        rel_x = (waypoint_map_x - map_rect.x) / map_rect.width
        rel_y = (waypoint_map_y - map_rect.y) / map_rect.height
        
        # Convert to overlay coordinates
        overlay_waypoint_x = rel_x * display_w
        overlay_waypoint_y = rel_y * display_h
        
        # Get ship position for dashed line
        game_state = self.simulator.get_state()
        position = game_state["navigation"]["position"]
        ship_map_x, ship_map_y = self._lat_lon_to_map_coords(position["latitude"], position["longitude"])
        
        # Calculate ship position in overlay coordinates
        ship_rel_x = (ship_map_x - map_rect.x) / map_rect.width
        ship_rel_y = (ship_map_y - map_rect.y) / map_rect.height
        overlay_ship_x = ship_rel_x * display_w
        overlay_ship_y = ship_rel_y * display_h
        
        # Draw dashed line from ship to waypoint (bottom layer, 25% opacity)
        self._draw_dashed_line(overlay, AIRSHIP_RANGE_COLOR,
                              (int(overlay_ship_x), int(overlay_ship_y)),
                              (int(overlay_waypoint_x), int(overlay_waypoint_y)),
                              1, 64, dash_length=8)  # 25% opacity, 8px dashes
        
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
        
        # Blit the overlay onto the main surface
        surface.blit(overlay, (8, 56))
    
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
