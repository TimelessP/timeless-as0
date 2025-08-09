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
POSITION_COLOR = (255, 100, 100)  # Red for current position
ROUTE_COLOR = (100, 255, 100)     # Green for route
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
        
    def _get_visible_map_rect(self) -> pygame.Rect:
        """Get the rectangle of the map that should be visible"""
        if not self.world_map:
            return pygame.Rect(0, 0, LOGICAL_SIZE, LOGICAL_SIZE)
            
        map_w, map_h = self.world_map.get_size()
        
        # Available space for map (minus UI areas and header)
        map_area_w = LOGICAL_SIZE - 16  # 8px margin on each side
        map_area_h = LOGICAL_SIZE - 92  # Leave space for header (32), top info (24), bottom margin (8), and bottom controls (28)
        
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
        view_x = center_x - viewport_w // 2
        view_y = center_y - viewport_h // 2
        
        # Clamp to map bounds
        view_x = max(0, min(map_w - viewport_w, view_x))
        view_y = max(0, min(map_h - viewport_h, view_y))
        
        return pygame.Rect(int(view_x), int(view_y), viewport_w, viewport_h)
        
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
                self.map_offset_x -= 20 / self.zoom_level
                self._save_view_settings()
            elif event.key == pygame.K_RIGHT:
                self.map_offset_x += 20 / self.zoom_level
                self._save_view_settings()
            elif event.key == pygame.K_UP:
                self.map_offset_y -= 20 / self.zoom_level
                self._save_view_settings()
            elif event.key == pygame.K_DOWN:
                self.map_offset_y += 20 / self.zoom_level
                self._save_view_settings()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                logical_pos = event.pos  # Already converted by main.py
                clicked_widget = self._get_widget_at_pos(logical_pos)
                if clicked_widget is not None:
                    self._set_focus(clicked_widget)
                    return self._activate_focused()
                else:
                    # Check if clicking on map area for dragging
                    x, y = logical_pos
                    if 8 <= x <= LOGICAL_SIZE - 8 and 32 <= y <= LOGICAL_SIZE - 28:
                        self.is_dragging = True
                        self.drag_start_pos = logical_pos
                        self.drag_start_offset = (self.map_offset_x, self.map_offset_y)
            elif event.button == 4:  # Mouse wheel up - zoom in
                self._zoom_in()
            elif event.button == 5:  # Mouse wheel down - zoom out
                self._zoom_out()
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                if self.is_dragging:
                    # Save settings after dragging is complete
                    self._save_view_settings()
                self.is_dragging = False
                self.drag_start_pos = None
                self.drag_start_offset = None
                
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging and self.drag_start_pos and self.drag_start_offset:
                # Calculate drag delta
                current_pos = event.pos
                dx = current_pos[0] - self.drag_start_pos[0]
                dy = current_pos[1] - self.drag_start_pos[1]
                
                # Convert screen delta to map delta (accounting for zoom)
                map_dx = dx / self.zoom_level
                map_dy = dy / self.zoom_level
                
                # Update map offset (don't save during drag for performance)
                self.map_offset_x = self.drag_start_offset[0] - map_dx
                self.map_offset_y = self.drag_start_offset[1] - map_dy
                    
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
            self.map_offset_x = nav_view["offsetX"]
            self.map_offset_y = nav_view["offsetY"]
            self.settings_loaded = True
        
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
            
        # Scale to fit the display area (adjusted for header)
        display_w = LOGICAL_SIZE - 16
        display_h = LOGICAL_SIZE - 92  # Same calculation as map_area_h
        
        if map_section.get_width() > 0 and map_section.get_height() > 0:
            scaled_map = pygame.transform.scale(map_section, (display_w, display_h))
            # Draw to surface (shifted down for header)
            surface.blit(scaled_map, (8, 56))
        
    def _draw_position_indicator(self, surface):
        """Draw current position on the map"""
        game_state = self.simulator.get_state()
        position = game_state["navigation"]["position"]
        
        # Get ship's absolute position in map coordinates
        ship_map_x, ship_map_y = self._lat_lon_to_map_coords(position["latitude"], position["longitude"])
        
        # Get the current viewport
        map_rect = self._get_visible_map_rect()
        
        # Check if ship position is within the visible viewport
        if map_rect.collidepoint(ship_map_x, ship_map_y):
            # Calculate ship position relative to the visible map area
            rel_x = (ship_map_x - map_rect.x) / map_rect.width
            rel_y = (ship_map_y - map_rect.y) / map_rect.height
            
            # Convert to screen coordinates (adjusted for header and UI)
            display_w = LOGICAL_SIZE - 16
            display_h = LOGICAL_SIZE - 92  # Same calculation as map_area_h
            screen_x = 8 + rel_x * display_w
            screen_y = 56 + rel_y * display_h  # 56 = 32 (header) + 24 (info area)
            
            # Draw position marker
            pygame.draw.circle(surface, POSITION_COLOR, (int(screen_x), int(screen_y)), 3)
            
            # Draw heading indicator
            heading_rad = math.radians(position["heading"])
            end_x = screen_x + math.sin(heading_rad) * 12
            end_y = screen_y - math.cos(heading_rad) * 12
            pygame.draw.line(surface, POSITION_COLOR, 
                           (int(screen_x), int(screen_y)), 
                           (int(end_x), int(end_y)), 2)
                           
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
