"""
Cargo Management Scene - Physics-based winch and crate management mini-game
"""
import pygame
import random
import math
from typing import Optional, Dict, List, Tuple

# Colors
BACKGROUND_COLOR = (20, 20, 30)
TEXT_COLOR = (255, 255, 255)
FOCUS_COLOR = (255, 200, 50)
CARGO_HEADER_COLOR = (120, 100, 60)  # Beige-brown for cargo scene
GRID_COLOR = (40, 40, 50)  # Subtle grid lines
WINCH_COLOR = (150, 150, 150)
CABLE_COLOR = (120, 120, 120)
CARGO_HOLD_COLOR = (30, 50, 40)  # Dark green tint
LOADING_BAY_COLOR = (50, 40, 30)  # Dark brown tint
AREA_BORDER_COLOR = (80, 80, 80)
SELECTED_CRATE_COLOR = (255, 255, 100)  # Yellow highlight
VALID_PLACEMENT_COLOR = (100, 255, 100)  # Green for valid placement
INVALID_PLACEMENT_COLOR = (255, 100, 100)  # Red for invalid placement

# Layout constants
GRID_SIZE = 10  # pixels per grid cell
CARGO_HOLD_AREA = {"x": 8, "y": 60, "width": 150, "height": 200}
LOADING_BAY_AREA = {"x": 162, "y": 60, "width": 150, "height": 200}
WINCH_RAIL_Y = 40
WINCH_RAIL_START_X = 8
WINCH_RAIL_END_X = 312

class CargoScene:
    def __init__(self, simulator):
        self.font = None
        self.is_text_antialiased = False
        self.simulator = simulator
        self.widgets = []
        self.focused_widget = 0
        self.selected_crate = None  # Currently selected crate for interaction
        self.mouse_held = False  # Track mouse button state
        self.mouse_hold_start_time = 0.0  # For continuous movement
        self.button_hold_times = {}  # Track button hold times
        self.last_update_time = 0.0

        self._init_widgets()

    def set_font(self, font, is_text_antialiased=False):
        """Set the font for this scene"""
        self.font = font
        self.is_text_antialiased = is_text_antialiased

    def _init_widgets(self):
        """Initialize all interactive widgets"""
        self.widgets = [
            # Winch movement controls (top row)
            {"id": "winch_left", "type": "button", "position": [20, 8], "size": [50, 24], "text": "◀ Left", "focused": True, "holdable": True},
            {"id": "winch_right", "type": "button", "position": [80, 8], "size": [50, 24], "text": "Right ▶", "focused": False, "holdable": True},
            {"id": "winch_up", "type": "button", "position": [140, 8], "size": [40, 24], "text": "▲ Up", "focused": False, "holdable": True},
            {"id": "winch_down", "type": "button", "position": [190, 8], "size": [50, 24], "text": "Down ▼", "focused": False, "holdable": True},
            
            # Action buttons (bottom area)
            {"id": "attach", "type": "button", "position": [20, 270], "size": [60, 20], "text": "Attach", "focused": False, "holdable": False},
            {"id": "detach", "type": "button", "position": [90, 270], "size": [60, 20], "text": "Detach", "focused": False, "holdable": False},
            {"id": "use_crate", "type": "button", "position": [160, 270], "size": [60, 20], "text": "Use", "focused": False, "holdable": False},
            {"id": "refresh", "type": "button", "position": [230, 270], "size": [60, 20], "text": "Refresh", "focused": False, "holdable": False},
            
            # Navigation controls
            {"id": "prev_scene", "type": "button", "position": [8, 290], "size": [60, 24], "text": "< [", "focused": False, "holdable": False},
            {"id": "next_scene", "type": "button", "position": [252, 290], "size": [60, 24], "text": "] >", "focused": False, "holdable": False},
        ]

    def handle_event(self, event) -> Optional[str]:
        """Handle input events"""
        import time
        current_time = time.time()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "scene_main_menu"
            elif event.key == pygame.K_LEFTBRACKET:  # [
                return "scene_fuel"
            elif event.key == pygame.K_RIGHTBRACKET:  # ]
                return "scene_communications"
            elif event.key == pygame.K_TAB:
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self._cycle_focus(-1)
                else:
                    self._cycle_focus(1)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return self._activate_focused()
            # Arrow keys for winch movement when focused on winch controls
            elif event.key == pygame.K_LEFT and self._is_winch_control_focused():
                self._handle_winch_movement("left", True)
            elif event.key == pygame.K_RIGHT and self._is_winch_control_focused():
                self._handle_winch_movement("right", True)
            elif event.key == pygame.K_UP and self._is_winch_control_focused():
                self._handle_winch_movement("up", True)
            elif event.key == pygame.K_DOWN and self._is_winch_control_focused():
                self._handle_winch_movement("down", True)
                
        elif event.type == pygame.KEYUP:
            # Stop winch movement on key release
            if event.key == pygame.K_LEFT:
                self._handle_winch_movement("left", False)
            elif event.key == pygame.K_RIGHT:
                self._handle_winch_movement("right", False)
            elif event.key == pygame.K_UP:
                self._handle_winch_movement("up", False)
            elif event.key == pygame.K_DOWN:
                self._handle_winch_movement("down", False)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                logical_pos = event.pos  # Already converted by main.py
                clicked_widget = self._get_widget_at_pos(logical_pos)
                clicked_crate = self._get_crate_at_pos(logical_pos)
                
                if clicked_widget is not None:
                    self._set_focus(clicked_widget)
                    widget = self.widgets[clicked_widget]
                    if widget.get("holdable", False):
                        # Start continuous movement for holdable buttons
                        self.mouse_held = True
                        self.mouse_hold_start_time = current_time
                        self.button_hold_times[widget["id"]] = current_time
                        return self._handle_button_hold(widget["id"])
                    else:
                        return self._activate_focused()
                elif clicked_crate is not None:
                    self.selected_crate = clicked_crate
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.mouse_held = False
                # Stop all winch movements
                for direction in ["left", "right", "up", "down"]:
                    self._handle_winch_movement(direction, False)
                self.button_hold_times.clear()
                
        return None

    def render(self, surface):
        """Render the cargo management scene"""
        # Clear background
        surface.fill(BACKGROUND_COLOR)

        if not self.font:
            return

        # Draw colored title header
        pygame.draw.rect(surface, CARGO_HEADER_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(surface, TEXT_COLOR, (0, 0, 320, 24), 1)

        # Centered title
        title = self.font.render("CARGO MANAGEMENT", self.is_text_antialiased, TEXT_COLOR)
        title_x = (320 - title.get_width()) // 2
        surface.blit(title, (title_x, 4))

        # Draw winch rail
        self._render_winch_rail(surface)
        
        # Draw cargo areas with grid
        self._render_cargo_areas(surface)
        
        # Draw all crates
        self._render_crates(surface)
        
        # Draw winch and cable
        self._render_winch_system(surface)
        
        # Draw info panel
        self._render_info_panel(surface)

        # Render widgets
        for widget in self.widgets:
            self._render_widget(surface, widget)

    def _render_winch_rail(self, surface):
        """Draw the horizontal winch rail"""
        rail_y = WINCH_RAIL_Y
        # Rail line
        pygame.draw.line(surface, WINCH_COLOR, (WINCH_RAIL_START_X, rail_y), (WINCH_RAIL_END_X, rail_y), 3)
        # Rail supports
        for x in range(WINCH_RAIL_START_X, WINCH_RAIL_END_X + 1, 50):
            pygame.draw.line(surface, WINCH_COLOR, (x, rail_y - 5), (x, rail_y + 5), 2)

    def _render_cargo_areas(self, surface):
        """Draw cargo hold and loading bay areas with grid"""
        # Cargo hold (left side)
        hold_rect = (CARGO_HOLD_AREA["x"], CARGO_HOLD_AREA["y"], 
                    CARGO_HOLD_AREA["width"], CARGO_HOLD_AREA["height"])
        pygame.draw.rect(surface, CARGO_HOLD_COLOR, hold_rect)
        pygame.draw.rect(surface, AREA_BORDER_COLOR, hold_rect, 2)
        
        # Loading bay (right side)
        bay_rect = (LOADING_BAY_AREA["x"], LOADING_BAY_AREA["y"],
                   LOADING_BAY_AREA["width"], LOADING_BAY_AREA["height"])
        pygame.draw.rect(surface, LOADING_BAY_COLOR, bay_rect)
        pygame.draw.rect(surface, AREA_BORDER_COLOR, bay_rect, 2)
        
        # Draw grid lines
        self._render_grid(surface, CARGO_HOLD_AREA)
        self._render_grid(surface, LOADING_BAY_AREA)
        
        # Area labels
        if self.font:
            hold_label = self.font.render("CARGO HOLD", self.is_text_antialiased, TEXT_COLOR)
            surface.blit(hold_label, (CARGO_HOLD_AREA["x"] + 5, CARGO_HOLD_AREA["y"] - 15))
            
            bay_label = self.font.render("LOADING BAY", self.is_text_antialiased, TEXT_COLOR)
            surface.blit(bay_label, (LOADING_BAY_AREA["x"] + 5, LOADING_BAY_AREA["y"] - 15))

    def _render_grid(self, surface, area):
        """Draw grid lines within an area"""
        for x in range(area["x"], area["x"] + area["width"], GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (x, area["y"]), (x, area["y"] + area["height"]), 1)
        for y in range(area["y"], area["y"] + area["height"], GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (area["x"], y), (area["x"] + area["width"], y), 1)

    def _render_crates(self, surface):
        """Draw all crates in both areas"""
        cargo_state = self.simulator.get_cargo_state()
        crate_types = cargo_state.get("crateTypes", {})
        
        # Draw cargo hold crates
        for crate in cargo_state.get("cargoHold", []):
            self._render_single_crate(surface, crate, crate_types, "cargoHold")
        
        # Draw loading bay crates
        for crate in cargo_state.get("loadingBay", []):
            self._render_single_crate(surface, crate, crate_types, "loadingBay")

    def _render_single_crate(self, surface, crate, crate_types, area):
        """Render an individual crate"""
        crate_type = crate_types.get(crate["type"], {})
        dimensions = crate_type.get("dimensions", {"width": 1, "height": 1})
        colors = crate_type.get("colors", {"outline": "#FFFFFF", "fill": "#808080"})
        
        # Convert color strings to RGB tuples
        outline_color = self._hex_to_rgb(colors["outline"])
        fill_color = self._hex_to_rgb(colors["fill"])
        
        # Calculate pixel position and size
        x = int(crate["position"]["x"])
        y = int(crate["position"]["y"])
        width = dimensions["width"] * GRID_SIZE
        height = dimensions["height"] * GRID_SIZE
        
        # Highlight selected crate
        if self.selected_crate and self.selected_crate["id"] == crate["id"]:
            # Draw selection highlight
            pygame.draw.rect(surface, SELECTED_CRATE_COLOR, (x - 2, y - 2, width + 4, height + 4), 2)
        
        # Draw crate body
        pygame.draw.rect(surface, fill_color, (x, y, width, height))
        pygame.draw.rect(surface, outline_color, (x, y, width, height), 2)
        
        # Draw X pattern for structural detail
        pygame.draw.line(surface, outline_color, (x, y), (x + width, y + height), 1)
        pygame.draw.line(surface, outline_color, (x + width, y), (x, y + height), 1)

    def _render_winch_system(self, surface):
        """Draw winch trolley and cable"""
        cargo_state = self.simulator.get_cargo_state()
        winch = cargo_state.get("winch", {})
        position = winch.get("position", {"x": 160, "y": 50})
        cable_length = winch.get("cableLength", 0)
        
        winch_x = int(position["x"])
        winch_y = WINCH_RAIL_Y
        
        # Draw winch trolley
        trolley_width = 12
        trolley_height = 8
        trolley_rect = (winch_x - trolley_width // 2, winch_y - trolley_height // 2,
                       trolley_width, trolley_height)
        pygame.draw.rect(surface, WINCH_COLOR, trolley_rect)
        pygame.draw.rect(surface, TEXT_COLOR, trolley_rect, 1)
        
        # Draw cable
        if cable_length > 0:
            cable_end_y = winch_y + cable_length
            pygame.draw.line(surface, CABLE_COLOR, (winch_x, winch_y), (winch_x, cable_end_y), 2)
            
            # Draw hook at end of cable
            hook_size = 4
            pygame.draw.circle(surface, CABLE_COLOR, (winch_x, int(cable_end_y)), hook_size)
            
            # If crate is attached, show connection
            attached_crate_id = winch.get("attachedCrate")
            if attached_crate_id:
                # Find the attached crate and draw connection line
                all_crates = cargo_state.get("cargoHold", []) + cargo_state.get("loadingBay", [])
                for crate in all_crates:
                    if crate["id"] == attached_crate_id:
                        crate_x = int(crate["position"]["x"])
                        crate_y = int(crate["position"]["y"])
                        pygame.draw.line(surface, FOCUS_COLOR, (winch_x, int(cable_end_y)), 
                                       (crate_x + 5, crate_y), 3)
                        break

    def _render_info_panel(self, surface):
        """Draw information panel at bottom"""
        if not self.font:
            return
            
        info_y = 300
        cargo_state = self.simulator.get_cargo_state()
        
        # Selected crate info
        if self.selected_crate:
            crate_types = cargo_state.get("crateTypes", {})
            crate_type_info = crate_types.get(self.selected_crate["type"], {})
            name = crate_type_info.get("name", "Unknown")
            dims = crate_type_info.get("dimensions", {"width": 1, "height": 1})
            contents = self.selected_crate.get("contents", {"amount": 0, "unit": "units"})
            
            info_text = f"Selected: {name}, {dims['width']}x{dims['height']}, {contents['amount']} {contents['unit']}"
            info_surface = self.font.render(info_text, self.is_text_antialiased, TEXT_COLOR)
            surface.blit(info_surface, (8, info_y))
        else:
            # General cargo info
            total_weight = cargo_state.get("totalWeight", 0.0)
            max_capacity = cargo_state.get("maxCapacity", 500.0)
            info_text = f"Total Weight: {total_weight:.1f} / {max_capacity:.0f} lbs"
            info_surface = self.font.render(info_text, self.is_text_antialiased, TEXT_COLOR)
            surface.blit(info_surface, (8, info_y))

    def _render_widget(self, surface, widget):
        """Render a single widget"""
        if not self.font:
            return

        x, y = widget["position"]
        w, h = widget["size"]
        focused = widget["focused"]
        text = widget["text"]
        widget_id = widget["id"]
        
        # Check if widget should be enabled
        enabled = self._is_widget_enabled(widget_id)

        # Button colors - disabled buttons are darker
        if enabled:
            bg_color = (80, 100, 120) if focused else (60, 80, 100)
            border_color = FOCUS_COLOR if focused else (120, 120, 120)
            text_color = FOCUS_COLOR if focused else TEXT_COLOR
        else:
            bg_color = (40, 40, 50)
            border_color = (60, 60, 60)
            text_color = (100, 100, 100)

        # Draw button background
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        pygame.draw.rect(surface, border_color, (x, y, w, h), 1)

        # Draw button text
        text_surface = self.font.render(text, self.is_text_antialiased, text_color)
        text_x = x + (w - text_surface.get_width()) // 2
        text_y = y + (h - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))

    def _is_widget_enabled(self, widget_id: str) -> bool:
        """Check if a widget should be enabled based on game state"""
        cargo_state = self.simulator.get_cargo_state()
        winch = cargo_state.get("winch", {})
        
        if widget_id == "attach":
            # Can attach if winch is near a crate and nothing is attached
            return winch.get("attachedCrate") is None and self._can_attach_to_nearby_crate()
        elif widget_id == "detach":
            # Can detach if something is attached and can be placed
            return winch.get("attachedCrate") is not None
        elif widget_id == "use_crate":
            # Can use if a usable crate is selected
            return self.selected_crate is not None and self._is_crate_usable(self.selected_crate)
        elif widget_id == "refresh":
            # Can refresh if available and ship is not moving
            return cargo_state.get("refreshAvailable", True)
        else:
            # All other widgets (movement, navigation) are always enabled
            return True

    def _can_attach_to_nearby_crate(self) -> bool:
        """Check if winch can attach to a nearby crate"""
        cargo_state = self.simulator.get_cargo_state()
        winch = cargo_state.get("winch", {})
        winch_pos = winch.get("position", {"x": 160, "y": 50})
        cable_length = winch.get("cableLength", 0)
        
        # Calculate hook position
        hook_x = winch_pos["x"]
        hook_y = WINCH_RAIL_Y + cable_length
        
        # Check all crates for proximity
        all_crates = cargo_state.get("cargoHold", []) + cargo_state.get("loadingBay", [])
        for crate in all_crates:
            crate_x = crate["position"]["x"]
            crate_y = crate["position"]["y"]
            
            # Check if hook is within reasonable distance of crate center
            distance = math.sqrt((hook_x - crate_x) ** 2 + (hook_y - crate_y) ** 2)
            if distance < 15:  # Within 15 pixels
                return True
        
        return False

    def _is_crate_usable(self, crate) -> bool:
        """Check if a crate can be used"""
        if not crate:
            return False
        cargo_state = self.simulator.get_cargo_state()
        crate_types = cargo_state.get("crateTypes", {})
        crate_type = crate_types.get(crate["type"], {})
        return crate_type.get("usable", False)

    def _get_widget_at_pos(self, pos):
        """Find widget at given position"""
        x, y = pos
        for i, widget in enumerate(self.widgets):
            wx, wy = widget["position"]
            ww, wh = widget["size"]
            if wx <= x <= wx + ww and wy <= y <= wy + wh:
                return i
        return None

    def _get_crate_at_pos(self, pos) -> Optional[Dict]:
        """Find crate at given position"""
        x, y = pos
        cargo_state = self.simulator.get_cargo_state()
        crate_types = cargo_state.get("crateTypes", {})
        
        # Check all crates (loading bay first for priority)
        all_crates = cargo_state.get("loadingBay", []) + cargo_state.get("cargoHold", [])
        
        for crate in all_crates:
            crate_type = crate_types.get(crate["type"], {})
            dimensions = crate_type.get("dimensions", {"width": 1, "height": 1})
            
            crate_x = crate["position"]["x"]
            crate_y = crate["position"]["y"]
            crate_w = dimensions["width"] * GRID_SIZE
            crate_h = dimensions["height"] * GRID_SIZE
            
            if crate_x <= x <= crate_x + crate_w and crate_y <= y <= crate_y + crate_h:
                return crate
        
        return None

    def _set_focus(self, widget_index):
        """Set focus to specific widget"""
        # Clear current focus
        for widget in self.widgets:
            widget["focused"] = False

        # Set new focus
        if 0 <= widget_index < len(self.widgets):
            self.focused_widget = widget_index
            self.widgets[widget_index]["focused"] = True

    def _cycle_focus(self, direction):
        """Cycle focus through widgets"""
        if not self.widgets:
            return
            
        self.widgets[self.focused_widget]["focused"] = False
        self.focused_widget = (self.focused_widget + direction) % len(self.widgets)
        self.widgets[self.focused_widget]["focused"] = True

    def _is_winch_control_focused(self) -> bool:
        """Check if a winch control widget is currently focused"""
        if 0 <= self.focused_widget < len(self.widgets):
            widget_id = self.widgets[self.focused_widget]["id"]
            return widget_id in ["winch_left", "winch_right", "winch_up", "winch_down"]
        return False

    def _handle_winch_movement(self, direction: str, active: bool):
        """Handle winch movement in specified direction"""
        self.simulator.set_winch_movement_state(direction, active)

    def _handle_button_hold(self, button_id: str) -> Optional[str]:
        """Handle continuous button hold actions"""
        if button_id == "winch_left":
            self._handle_winch_movement("left", True)
        elif button_id == "winch_right":
            self._handle_winch_movement("right", True)
        elif button_id == "winch_up":
            self._handle_winch_movement("up", True)
        elif button_id == "winch_down":
            self._handle_winch_movement("down", True)
        return None

    def _activate_focused(self) -> Optional[str]:
        """Activate the currently focused widget"""
        if 0 <= self.focused_widget < len(self.widgets):
            widget = self.widgets[self.focused_widget]
            widget_id = widget["id"]
            
            # Check if widget is enabled
            if not self._is_widget_enabled(widget_id):
                return None
            
            if widget_id == "prev_scene":
                return "scene_fuel"
            elif widget_id == "next_scene":
                return "scene_communications"
            elif widget_id == "attach":
                self.simulator.attach_crate("")  # Attach to nearest crate
            elif widget_id == "detach":
                self.simulator.detach_crate()
            elif widget_id == "use_crate":
                if self.selected_crate:
                    success = self.simulator.use_crate(self.selected_crate["id"])
                    if success:
                        self.selected_crate = None  # Clear selection after use
            elif widget_id == "refresh":
                self.simulator.refresh_loading_bay()
            elif widget_id in ["winch_left", "winch_right", "winch_up", "winch_down"]:
                # For holdable buttons, start movement
                direction = widget_id.replace("winch_", "")
                self._handle_winch_movement(direction, True)
                
        return None

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except (ValueError, IndexError):
            return (128, 128, 128)  # Default gray

    def update(self, dt: float):
        """Update the scene with game state"""
        import time
        current_time = time.time()
        self.last_update_time = current_time
        
        # Handle continuous button holds
        if self.mouse_held:
            for button_id, start_time in self.button_hold_times.items():
                # Continue the action if button is still held
                if current_time - start_time > 0.1:  # Small delay before continuous action
                    self._handle_button_hold(button_id)
