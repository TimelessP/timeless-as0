"""
Observatory Scene for Airship Zero
360-degree horizon view from the airship's position with true 3D terrain mesh rendering
Features elevation data integration and texture mapping from world map colors
"""
from typing import List, Dict, Any, Optional
import pygame
import math
from theme import (
    LOGICAL_SIZE,
    FOCUS_COLOR,
    BACKGROUND_COLOR,
    TEXT_COLOR,
    BUTTON_COLOR,
    BUTTON_FOCUSED_COLOR,
    BUTTON_DISABLED_COLOR,
    BUTTON_BORDER_COLOR,
    BUTTON_BORDER_DISABLED_COLOR,
    BUTTON_BORDER_FOCUSED_COLOR,
    BUTTON_TEXT_DISABLED_COLOR,
    BUTTON_TEXT_COLOR,
    BUTTON_TEXT_FOCUSED_COLOR,
    NAV_HEADER_COLOR,
    SKY_COLOR,
    GROUND_COLOR,
    HORIZON_LINE_COLOR
)
from scenery import Scenery
from terrain_mesh import TerrainMesh, Camera3D, create_camera_from_airship_state
from heightmap import HeightMap

class ObservatoryScene:
    def __init__(self, simulator):
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focus_index = 0
        self.simulator = simulator
        
        # Observatory-specific state
        self.view_angle = 0.0  # Player's viewing angle (0-360 degrees)
        self.tilt_angle = 0.0  # Vertical tilt angle (-30 to +30 degrees)
        self.viewport_surface = pygame.Surface((304, 200))  # Main viewport area
        
        # 3D terrain mesh system
        self.terrain_mesh = None
        self.camera_3d = None
        self.mesh_last_update_pos = None
        self.use_3d_rendering = True  # Toggle between 3D mesh and 2D fallback
        
        # Initialize scenery renderer (fallback for 2D mode)
        self.scenery = Scenery()
        
        # Load world map for texture mapping
        self.world_map = None
        import os
        try:
            from main import get_assets_dir
            assets_dir = get_assets_dir()
            world_map_path = os.path.join(assets_dir, "png", "world-map.png")
            print(f"Observatory: Looking for world map at: {world_map_path}")
            print(f"Observatory: Current working directory: {os.getcwd()}")
            print(f"Observatory: Assets directory: {assets_dir}")
            print(f"Observatory: World map exists: {os.path.exists(world_map_path)}")
            if os.path.exists(assets_dir):
                print(f"Observatory: Assets directory contents: {os.listdir(assets_dir)}")
                png_dir = os.path.join(assets_dir, "png")
                if os.path.exists(png_dir):
                    png_files = os.listdir(png_dir)[:10]  # First 10 files
                    print(f"Observatory: PNG directory contents: {png_files}")
            
            self.world_map = pygame.image.load(world_map_path)
            print(f"Observatory: Successfully loaded world map: {self.world_map.get_size()}")
        except Exception as e:
            print(f"Observatory: Could not load world-map.png: {e}")
            import traceback
            traceback.print_exc()
        
        # Initialize terrain mesh if heightmap is available
        self._init_terrain_mesh()
        
        # Initialize widgets
        self._init_widgets()
        # Set initial focus to first focussable widget (not a label)
        self._set_focus(self._find_first_focussable_widget())

    def _find_first_focussable_widget(self) -> int:
        """Return the index of the first focussable (non-label, enabled) widget, or 0 if none found."""
        for i, widget in enumerate(self.widgets):
            if widget["type"] != "label" and widget.get("enabled", True):
                return i
        return 0
    
    def _init_terrain_mesh(self):
        """Initialize 3D terrain mesh system"""
        try:
            # Try to get heightmap from simulator
            if hasattr(self.simulator, 'heightmap') and self.simulator.heightmap:
                heightmap = self.simulator.heightmap
                print("Observatory: Using heightmap from simulator")
            else:
                # Create heightmap instance if not available
                print("Observatory: Creating new HeightMap instance")
                heightmap = HeightMap()
                print("Observatory: HeightMap created successfully")
            
            if self.world_map and heightmap:
                print(f"Observatory: World map size: {self.world_map.get_size()}")
                self.terrain_mesh = TerrainMesh(heightmap, self.world_map)
                print("Observatory: 3D terrain mesh system initialized")
            else:
                missing = []
                if not self.world_map:
                    missing.append("world map")
                if not heightmap:
                    missing.append("heightmap")
                print(f"Observatory: Falling back to 2D rendering (missing: {', '.join(missing)})")
                self.use_3d_rendering = False
        except Exception as e:
            print(f"Observatory: Error initializing terrain mesh: {e}")
            import traceback
            traceback.print_exc()
            self.use_3d_rendering = False
            
    def _init_widgets(self):
        """Initialize observatory widgets"""
        self.widgets = [
            {
                "id": "viewport",
                "type": "viewport",
                "position": [8, 32],
                "size": [304, 200],
                "focused": True
            },
            {
                "id": "view_angle_label",
                "type": "label",
                "position": [8, 240],
                "size": [150, 16],
                "text": "VIEW: 000°",
                "focused": False
            },
            {
                "id": "position_label",
                "type": "label",
                "position": [170, 240],
                "size": [142, 16],
                "text": "POS: 40.7128°N 74.0060°W",
                "focused": False
            },
            {
                "id": "altitude_label",
                "type": "label",
                "position": [8, 256],
                "size": [100, 16],
                "text": "ALT: 1250 ft",
                "focused": False
            },
            {
                "id": "tilt_label",
                "type": "label",
                "position": [120, 256],
                "size": [100, 16],
                "text": "TILT: 0.0°",
                "focused": False
            },
            {
                "id": "heading_label",
                "type": "label",
                "position": [230, 256],
                "size": [82, 16],
                "text": "HDG: 045°",
                "focused": False
            },
            {
                "id": "sun_label",
                "type": "label",
                "position": [8, 272],
                "size": [150, 16],
                "text": "SUN: 23.4°N 45.0°W",
                "focused": False
            },
            {
                "id": "prev_scene",
                "type": "button",
                "position": [8, 290],
                "size": [60, 24],
                "text": "< [",
                "focused": False
            },
            {
                "id": "next_scene",
                "type": "button",
                "position": [252, 290],
                "size": [60, 24],
                "text": "] >",
                "focused": False
            }
        ]
        
    def set_font(self, font, is_text_antialiased=False):
        """Set the font for rendering text"""
        self.font = font
        self.is_text_antialiased = is_text_antialiased
        
    def handle_event(self, event) -> Optional[str]:
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "scene_main_menu"
            elif event.key == pygame.K_LEFTBRACKET:
                return self._get_prev_scene()
            elif event.key == pygame.K_RIGHTBRACKET:
                return self._get_next_scene()
            elif event.key == pygame.K_TAB:
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self._focus_previous()
                else:
                    self._focus_next()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return self._activate_focused()
            elif event.key == pygame.K_LEFT:
                if self._is_viewport_focused():
                    self._rotate_view(-5.0)
            elif event.key == pygame.K_RIGHT:
                if self._is_viewport_focused():
                    self._rotate_view(5.0)
            elif event.key == pygame.K_UP:
                if self._is_viewport_focused():
                    self._tilt_view(2.0)
            elif event.key == pygame.K_DOWN:
                if self._is_viewport_focused():
                    self._tilt_view(-2.0)
            elif event.key == pygame.K_r:
                # Regenerate 3D mesh for testing
                if self._is_viewport_focused():
                    self._regenerate_mesh()
            elif event.key == pygame.K_m:
                # Toggle 3D/2D rendering mode
                if self._is_viewport_focused():
                    self._toggle_rendering_mode()
            elif event.key == pygame.K_i:
                # Print mesh info for debugging
                if self._is_viewport_focused():
                    self._print_mesh_info()
            elif event.key == pygame.K_c:
                # Center camera view on ship's heading
                if self._is_viewport_focused():
                    self._center_view_on_heading()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                logical_pos = self._screen_to_logical(event.pos)
                if logical_pos:
                    widget_index = self._get_widget_at_pos(logical_pos)
                    if widget_index is not None:
                        self._set_focus(widget_index)
                        if self.widgets[widget_index]["type"] == "button":
                            return self._activate_focused()
        elif event.type == pygame.MOUSEMOTION:
            if self._is_viewport_focused():
                # Use absolute mouse position within viewport for camera control
                logical_pos = self._screen_to_logical(event.pos)
                if logical_pos:
                    self._update_camera_from_mouse_pos(logical_pos)
        elif event.type == pygame.MOUSEWHEEL:
            if self._is_viewport_focused():
                # Mouse wheel changes tilt angle instead of rotation
                self._tilt_view(event.y * 2.0)  # Scroll up = tilt up
                
        return None
        
    def _is_viewport_focused(self) -> bool:
        """Check if the viewport widget is currently focused"""
        if 0 <= self.focus_index < len(self.widgets):
            return self.widgets[self.focus_index]["id"] == "viewport"
        return False
        
    def _rotate_view(self, delta_degrees: float):
        """Rotate the view angle by the specified amount"""
        self.view_angle = (self.view_angle + delta_degrees) % 360.0
    
    def _tilt_view(self, delta_degrees: float):
        """Tilt the view up/down by the specified amount"""
        self.tilt_angle = max(-30.0, min(30.0, self.tilt_angle + delta_degrees))
    
    def _center_view_on_heading(self):
        """Center the camera view to face the airship's current heading"""
        game_state = self.simulator.get_state()
        ship_heading = game_state["navigation"]["position"]["heading"]
        self.view_angle = 0.0  # Reset to forward (relative to ship heading)
        self.tilt_angle = 0.0  # Reset tilt to level
        print(f"Observatory: Camera centered on ship's heading ({ship_heading:.1f}°)")
    
    def _update_camera_from_mouse_pos(self, logical_pos):
        """Update camera angles based on absolute mouse position within viewport"""
        # Get viewport widget dimensions
        viewport_widget = next((w for w in self.widgets if w["id"] == "viewport"), None)
        if not viewport_widget:
            return
            
        vp_x, vp_y = viewport_widget["position"]
        vp_w, vp_h = viewport_widget["size"]
        
        # Check if mouse is within viewport
        mouse_x, mouse_y = logical_pos
        if not (vp_x <= mouse_x <= vp_x + vp_w and vp_y <= mouse_y <= vp_y + vp_h):
            return
            
        # Calculate relative position within viewport (0.0 to 1.0)
        rel_x = (mouse_x - vp_x) / vp_w
        rel_y = (mouse_y - vp_y) / vp_h
        
        # Get current airship heading to use as reference
        game_state = self.simulator.get_state()
        ship_heading = game_state["navigation"]["position"]["heading"]
        
        # Convert to camera angles relative to ship heading
        # Center of viewport (0.5, 0.5) should be ship's forward direction (heading + 0°)
        max_rotation = 90.0  # Maximum rotation in either direction
        max_tilt = 30.0      # Maximum tilt up/down
        
        # View angle is relative to ship heading: center = ship_heading, left/right = ±90°
        relative_angle = (rel_x - 0.5) * 2.0 * max_rotation  # -90° to +90° relative to ship
        self.view_angle = relative_angle  # Store relative angle, not absolute
        self.tilt_angle = -(rel_y - 0.5) * 2.0 * max_tilt     # -30° to +30° (inverted Y)
    
    def _regenerate_mesh(self):
        """Force regeneration of dual-LOD terrain mesh for current position"""
        if self.terrain_mesh and self.use_3d_rendering:
            game_state = self.simulator.get_state()
            position = game_state["navigation"]["position"]
            current_lat = position["latitude"]
            current_lon = position["longitude"]
            current_alt = position["altitude"]
            time_info = game_state.get("environment", {}).get("time", {})
            
            print(f"Observatory: Regenerating dual-LOD terrain mesh around {current_lat:.3f}°, {current_lon:.3f}° at {current_alt:.0f}m")
            self.terrain_mesh.generate_dual_lod_mesh_around_position(current_lat, current_lon, current_alt)
            
            # Generate 3D sun
            self.terrain_mesh.generate_3d_sun(current_lat, current_lon, current_alt, time_info)
            
            self.mesh_last_update_pos = (current_lat, current_lon, current_alt)
            
            # Print mesh statistics
            stats = self.terrain_mesh.get_mesh_statistics()
            print(f"Observatory: Generated {stats['inner_total']} inner triangles ({stats['inner_land_triangles']} land, {stats['inner_sea_triangles']} sea)")
            print(f"Observatory: Generated {stats['outer_total']} outer triangles ({stats['outer_land_triangles']} land, {stats['outer_sea_triangles']} sea)")
            if stats['sun_triangles'] > 0:
                print(f"Observatory: Generated 3D sun with {stats['sun_triangles']} triangles")
            print(f"Observatory: Total triangles: {stats['total_triangles']}")
            print(f"Observatory: Altitude reference: {current_alt:.0f}m, Vertical scale: {stats['scale_vertical']:.1f}x")
    
    def _toggle_rendering_mode(self):
        """Toggle between 3D mesh and 2D fallback rendering"""
        if self.terrain_mesh:
            self.use_3d_rendering = not self.use_3d_rendering
            mode = "3D MESH" if self.use_3d_rendering else "2D FALLBACK"
            print(f"Observatory: Switched to {mode} rendering mode")
        else:
            print("Observatory: 3D terrain mesh not available")
    
    def _print_mesh_info(self):
        """Print detailed mesh information for debugging"""
        if self.terrain_mesh:
            stats = self.terrain_mesh.get_mesh_statistics()
            print("Observatory: Mesh Statistics:")
            print(f"  Land triangles: {stats['land_triangles']}")
            print(f"  Sea triangles: {stats['sea_triangles']}")
            print(f"  Total triangles: {stats['total_triangles']}")
            print(f"  Mesh resolution: {stats['mesh_resolution']}x{stats['mesh_resolution']}")
            print(f"  Sea level: {stats['sea_level']}m")
            print(f"  Horizontal scale: {stats['scale_horizontal']:.0f}m/deg")
            print(f"  Vertical scale: {stats['scale_vertical']:.0f}x")
            print(f"  Rendering mode: {'3D MESH' if self.use_3d_rendering else '2D FALLBACK'}")
        else:
            print("Observatory: No terrain mesh available")
        
    def _screen_to_logical(self, screen_pos) -> Optional[tuple]:
        """Convert screen coordinates to logical 320x320 coordinates"""
        # TODO: Implement proper coordinate conversion based on scaling
        return screen_pos
        
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
        """Set focus to specific widget (only if not a label and enabled)"""
        if widget_index is not None and 0 <= widget_index < len(self.widgets):
            widget = self.widgets[widget_index]
            if widget["type"] != "label" and widget.get("enabled", True):
                for w in self.widgets:
                    w["focused"] = False
                widget["focused"] = True
                self.focus_index = widget_index
                
    def _focus_next(self):
        """Move focus to next focussable widget (skip labels and disabled)"""
        n = len(self.widgets)
        start = self.focus_index
        for offset in range(1, n+1):
            idx = (start + offset) % n
            widget = self.widgets[idx]
            if widget["type"] != "label" and widget.get("enabled", True):
                self._set_focus(idx)
                break
        
    def _focus_previous(self):
        """Move focus to previous focussable widget (skip labels and disabled)"""
        n = len(self.widgets)
        start = self.focus_index
        for offset in range(1, n+1):
            idx = (start - offset) % n
            widget = self.widgets[idx]
            if widget["type"] != "label" and widget.get("enabled", True):
                self._set_focus(idx)
                break
        
    def _activate_focused(self) -> Optional[str]:
        """Activate the currently focused widget"""
        if 0 <= self.focus_index < len(self.widgets):
            widget = self.widgets[self.focus_index]
            widget_id = widget["id"]
            
            if widget["type"] == "button":
                if widget_id == "prev_scene":
                    return self._get_prev_scene()
                elif widget_id == "next_scene":
                    return self._get_next_scene()
                
        return None
        
    def _get_prev_scene(self) -> str:
        """Get the previous scene in circular order"""
        return "scene_library"

    def _get_next_scene(self) -> str:
        """Get the next scene in circular order"""
        return "scene_bridge"
        
    def update(self, dt: float):
        """Update the scene with game state"""
        # Get current state from simulator
        game_state = self.simulator.get_state()
        nav = game_state["navigation"]
        position = nav["position"]
        motion = nav["motion"]
        
        # Update position display
        lat_str = f"{abs(position['latitude']):.4f}°{'N' if position['latitude'] >= 0 else 'S'}"
        lon_str = f"{abs(position['longitude']):.4f}°{'E' if position['longitude'] >= 0 else 'W'}"
        self._update_widget_text("position_label", f"POS: {lat_str} {lon_str}")
        
        # Update other displays
        self._update_widget_text("view_angle_label", f"VIEW: {self.view_angle:03.0f}°")
        self._update_widget_text("altitude_label", f"ALT: {position['altitude']:.0f} ft")
        self._update_widget_text("heading_label", f"HDG: {position['heading']:03.0f}°")
        
        # Update tilt display (combine pitch and manual tilt)
        total_tilt = motion.get("pitch", 0.0) + self.tilt_angle
        self._update_widget_text("tilt_label", f"TILT: {total_tilt:+.1f}°")
        
        # Update sun position display
        time_info = game_state.get("environment", {}).get("time", {})
        sun_lat, sun_lon = self.scenery.calculate_sun_position(time_info)
        sun_lat_str = f"{abs(sun_lat):.1f}°{'N' if sun_lat >= 0 else 'S'}"
        sun_lon_str = f"{abs(sun_lon):.1f}°{'E' if sun_lon >= 0 else 'W'}"
        self._update_widget_text("sun_label", f"SUN: {sun_lat_str} {sun_lon_str}")
        
        # Update 3D terrain mesh if position has changed significantly
        if self.use_3d_rendering and self.terrain_mesh:
            current_lat = position["latitude"]
            current_lon = position["longitude"]
            current_alt = position["altitude"]
            
            # Check if we need to regenerate mesh (moved more than 0.5 degree or significant altitude change)
            if (self.mesh_last_update_pos is None or 
                abs(current_lat - self.mesh_last_update_pos[0]) > 0.5 or
                abs(current_lon - self.mesh_last_update_pos[1]) > 0.5 or
                abs(current_alt - self.mesh_last_update_pos[2]) > 500):  # 500m altitude change
                
                time_info = game_state.get("environment", {}).get("time", {})
                print(f"Observatory: Updating dual-LOD terrain mesh for position {current_lat:.3f}°, {current_lon:.3f}° at {current_alt:.0f}m")
                self.terrain_mesh.generate_dual_lod_mesh_around_position(current_lat, current_lon, current_alt)
                
                # Generate 3D sun
                self.terrain_mesh.generate_3d_sun(current_lat, current_lon, current_alt, time_info)
                
                self.mesh_last_update_pos = (current_lat, current_lon, current_alt)
        
        # Render the horizon viewport using 3D mesh or 2D fallback
        self._render_horizon_viewport(game_state)
        
    def _update_widget_text(self, widget_id: str, new_text: str):
        """Update widget text"""
        for widget in self.widgets:
            if widget["id"] == widget_id:
                widget["text"] = new_text
                break
    
    def _render_horizon_viewport(self, game_state):
        """Render the 360-degree horizon view using 3D terrain mesh or 2D fallback"""
        position = game_state["navigation"]["position"]
        motion = game_state["navigation"]["motion"]
        fuel_state = game_state.get("fuel", {})
        time_info = game_state.get("environment", {}).get("time", {})
        
        # Clear viewport surface
        self.viewport_surface.fill(SKY_COLOR)
        
        if self.use_3d_rendering and self.terrain_mesh:
            # Use 3D terrain mesh rendering
            try:
                # Create 3D camera based on current view
                total_tilt = motion.get("pitch", 0.0) + self.tilt_angle
                self.camera_3d = create_camera_from_airship_state(game_state, self.view_angle, total_tilt)
                
                # Render 3D terrain mesh to viewport
                viewport_w, viewport_h = self.viewport_surface.get_size()
                self.terrain_mesh.render_to_surface(
                    self.viewport_surface, 
                    self.camera_3d,
                    0, 0, viewport_w, viewport_h
                )
                    
            except Exception as e:
                print(f"Observatory: 3D rendering error: {e}")
                # Fall back to 2D rendering
                self._render_2d_fallback(game_state)
        else:
            # Use 2D fallback rendering
            self._render_2d_fallback(game_state)
        
        # Draw overlays on top
        self._draw_forward_indicator(game_state)
        # Note: Sun is now rendered as 3D geometry, not as overlay
        self._draw_crosshair()
    
    def _render_2d_fallback(self, game_state):
        """Render using 2D scenery system as fallback"""
        position = game_state["navigation"]["position"]
        motion = game_state["navigation"]["motion"]
        fuel_state = game_state.get("fuel", {})
        time_info = game_state.get("environment", {}).get("time", {})
        
        # Use the scenery renderer for 2D horizon rendering
        self.scenery.render_horizon_360(
            self.viewport_surface,
            self.view_angle,
            position,
            motion,
            fuel_state,
            time_info,
            field_of_view=120.0  # Wide field of view for observatory
        )
        
        # Draw forward direction indicator on top
        self._draw_forward_indicator(game_state)
        
        # Draw sun position indicator
        self._draw_sun_indicator(game_state)
        
    def _draw_forward_indicator(self, game_state):
        """Draw indicator showing forward direction of airship"""
        # Since view_angle is now relative to ship heading,
        # forward direction is at view_angle = 0 (center when mouse is centered)
        forward_angle = -self.view_angle  # Negative because we want relative position on screen
        
        # Convert to screen position (assuming 90-degree field of view)
        fov = 120.0  # Wider field of view for better coverage
        if forward_angle > 180:
            forward_angle -= 360  # Convert to -180 to +180 range
            
        if -fov/2 <= forward_angle <= fov/2:
            # Forward direction is visible in current view
            screen_x = int(self.viewport_surface.get_width() * (forward_angle + fov/2) / fov)
            
            # Draw prominent downward-pointing triangle at top of viewport
            triangle_size = 10
            triangle_y = 8
            triangle_points = [
                (screen_x, triangle_y + triangle_size),
                (screen_x - triangle_size//2, triangle_y),
                (screen_x + triangle_size//2, triangle_y)
            ]
            
            # Draw triangle with border for better visibility
            pygame.draw.polygon(self.viewport_surface, FOCUS_COLOR, triangle_points)
            pygame.draw.polygon(self.viewport_surface, HORIZON_LINE_COLOR, triangle_points, 2)
            
            # Add "FWD" label below the triangle
            if self.font:
                fwd_text = self.font.render("FWD", self.is_text_antialiased, HORIZON_LINE_COLOR)
                fwd_x = screen_x - fwd_text.get_width() // 2
                fwd_y = triangle_y + triangle_size + 2
                # Ensure text stays within viewport bounds
                fwd_x = max(0, min(fwd_x, self.viewport_surface.get_width() - fwd_text.get_width()))
                if fwd_y + fwd_text.get_height() < self.viewport_surface.get_height():
                    self.viewport_surface.blit(fwd_text, (fwd_x, fwd_y))
                    
    def _draw_sun_indicator(self, game_state):
        """Draw indicator showing sun position"""
        position = game_state["navigation"]["position"]
        time_info = game_state.get("environment", {}).get("time", {})
        
        # Calculate sun position
        sun_lat, sun_lon = self.scenery.calculate_sun_position(time_info)
        
        # Calculate sun bearing from current position
        current_lat = position["latitude"]
        current_lon = position["longitude"]
        sun_bearing = self.scenery._calculate_bearing(current_lat, current_lon, sun_lat, sun_lon)
        
        # Calculate where the sun appears in our view
        # Since view_angle is now relative to ship heading, we need to convert to absolute world coordinates
        ship_heading = position["heading"]
        absolute_view_angle = (ship_heading + self.view_angle) % 360.0
        sun_angle = (sun_bearing - absolute_view_angle) % 360.0
        
        # Convert to screen position
        fov = 120.0  # Match scenery field of view
        if sun_angle > 180:
            sun_angle -= 360  # Convert to -180 to +180 range
            
        if -fov/2 <= sun_angle <= fov/2:
            # Sun is visible in current view
            screen_x = int(self.viewport_surface.get_width() * (sun_angle + fov/2) / fov)
            
            # Draw sun indicator - yellow circle at top
            sun_radius = 6
            sun_y = 20
            sun_center = (screen_x, sun_y)
            
            # Draw yellow sun with rays
            sun_color = (255, 255, 100)
            pygame.draw.circle(self.viewport_surface, sun_color, sun_center, sun_radius)
            pygame.draw.circle(self.viewport_surface, (255, 255, 255), sun_center, sun_radius, 1)
            
            # Draw sun rays
            for angle in range(0, 360, 45):
                ray_angle = math.radians(angle)
                start_x = screen_x + int(math.cos(ray_angle) * (sun_radius + 2))
                start_y = sun_y + int(math.sin(ray_angle) * (sun_radius + 2))
                end_x = screen_x + int(math.cos(ray_angle) * (sun_radius + 6))
                end_y = sun_y + int(math.sin(ray_angle) * (sun_radius + 6))
                pygame.draw.line(self.viewport_surface, sun_color, (start_x, start_y), (end_x, end_y), 2)
            
            # Add "SUN" label below
            if self.font:
                sun_text = self.font.render("SUN", self.is_text_antialiased, sun_color)
                sun_text_x = screen_x - sun_text.get_width() // 2
                sun_text_y = sun_y + sun_radius + 8
                # Ensure text stays within viewport bounds
                sun_text_x = max(0, min(sun_text_x, self.viewport_surface.get_width() - sun_text.get_width()))
                if sun_text_y + sun_text.get_height() < self.viewport_surface.get_height():
                    self.viewport_surface.blit(sun_text, (sun_text_x, sun_text_y))
    
    def _draw_crosshair(self):
        """Draw center crosshair for viewport reference"""
        viewport_w, viewport_h = self.viewport_surface.get_size()
        center_x = viewport_w // 2
        center_y = viewport_h // 2
        
        # Draw crosshair lines
        crosshair_color = (200, 200, 200, 128)  # Semi-transparent white
        line_length = 20
        
        # Horizontal line
        pygame.draw.line(self.viewport_surface, HORIZON_LINE_COLOR, 
                        (center_x - line_length, center_y), 
                        (center_x + line_length, center_y), 1)
        
        # Vertical line  
        pygame.draw.line(self.viewport_surface, HORIZON_LINE_COLOR,
                        (center_x, center_y - line_length),
                        (center_x, center_y + line_length), 1)
        
        # Center dot
        pygame.draw.circle(self.viewport_surface, HORIZON_LINE_COLOR, (center_x, center_y), 2)
            
    def render(self, surface):
        """Render the observatory scene to the logical surface"""
        surface.fill(BACKGROUND_COLOR)
        
        # Draw colored title header
        pygame.draw.rect(surface, NAV_HEADER_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(surface, TEXT_COLOR, (0, 0, 320, 24), 1)
        
        # Observatory title and compass heading
        if self.font:
            title_text = self.font.render("OBSERVATORY", self.is_text_antialiased, TEXT_COLOR)
            title_x = 8
            surface.blit(title_text, (title_x, 4))
            
            # Show current view direction as compass heading (absolute direction)
            game_state = self.simulator.get_state()
            ship_heading = game_state["navigation"]["position"]["heading"]
            absolute_view_angle = (ship_heading + self.view_angle) % 360.0
            view_compass = self._angle_to_compass(absolute_view_angle)
            compass_text = self.font.render(f"VIEW: {view_compass}", self.is_text_antialiased, TEXT_COLOR)
            compass_x = 320 - compass_text.get_width() - 8
            surface.blit(compass_text, (compass_x, 4))
        
        # Render viewport
        viewport_widget = next((w for w in self.widgets if w["id"] == "viewport"), None)
        if viewport_widget:
            x, y = viewport_widget["position"]
            
            # Draw viewport border
            border_color = FOCUS_COLOR if viewport_widget["focused"] else TEXT_COLOR
            pygame.draw.rect(surface, border_color, (x-1, y-1, 306, 202), 1)
            
            # Blit the horizon viewport
            surface.blit(self.viewport_surface, (x, y))
        
        # Draw all other widgets
        for widget in self.widgets:
            if widget["id"] != "viewport":
                self._render_widget(surface, widget)
                
    def _angle_to_compass(self, angle):
        """Convert angle to compass direction string"""
        # Normalize angle to 0-360
        angle = angle % 360
        
        # Convert to compass directions
        if angle < 11.25 or angle >= 348.75:
            return "N"
        elif angle < 33.75:
            return "NNE"
        elif angle < 56.25:
            return "NE"
        elif angle < 78.75:
            return "ENE"
        elif angle < 101.25:
            return "E"
        elif angle < 123.75:
            return "ESE"
        elif angle < 146.25:
            return "SE"
        elif angle < 168.75:
            return "SSE"
        elif angle < 191.25:
            return "S"
        elif angle < 213.75:
            return "SSW"
        elif angle < 236.25:
            return "SW"
        elif angle < 258.75:
            return "WSW"
        elif angle < 281.25:
            return "W"
        elif angle < 303.75:
            return "WNW"
        elif angle < 326.25:
            return "NW"
        else:
            return "NNW"
            
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
        enabled = widget.get("enabled", True)

        # Button colors using theme
        if not enabled:
            bg_color = BUTTON_DISABLED_COLOR
            text_color = BUTTON_TEXT_DISABLED_COLOR
            border_color = BUTTON_BORDER_DISABLED_COLOR
        elif focused:
            bg_color = BUTTON_FOCUSED_COLOR
            text_color = BUTTON_TEXT_FOCUSED_COLOR
            border_color = BUTTON_BORDER_FOCUSED_COLOR
        else:
            bg_color = BUTTON_COLOR
            text_color = BUTTON_TEXT_COLOR
            border_color = BUTTON_BORDER_COLOR

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
