"""
Cargo Management Scene - Physics-based winch and crate management mini-game
"""
import pygame
import random
import math
import time
from typing import Optional, Dict, List, Tuple
from theme import (
    BACKGROUND_COLOR,
    TEXT_COLOR,
    FOCUS_COLOR,
    CARGO_HEADER_COLOR,
    GRID_COLOR,
    WINCH_COLOR,
    CABLE_COLOR,
    CARGO_HOLD_COLOR,
    LOADING_BAY_COLOR,
    AREA_BORDER_COLOR,
    SELECTED_CRATE_COLOR,
    VALID_PLACEMENT_COLOR,
    INVALID_PLACEMENT_COLOR,
    BUTTON_COLOR,
    BUTTON_FOCUSED_COLOR,
    BUTTON_DISABLED_COLOR,
    BUTTON_BORDER_COLOR,
    BUTTON_BORDER_DISABLED_COLOR,
    BUTTON_BORDER_FOCUSED_COLOR,
    BUTTON_TEXT_DISABLED_COLOR,
    BUTTON_TEXT_COLOR,
    BUTTON_TEXT_FOCUSED_COLOR,
    # BUTTON_BG_FOCUSED,
    # BUTTON_BG,
    # BUTTON_BORDER_DISABLED,
    # BUTTON_TEXT_DISABLED,
    DEFAULT_GRAY
)

# Layout constants
# Reduced grid size to create vertical space for top title and bottom margins
GRID_SIZE = 8  # pixels per grid cell
CARGO_HOLD_AREA = {"x": 8, "y": 60, "width": 150, "height": 180}
LOADING_BAY_AREA = {"x": 162, "y": 60, "width": 150, "height": 180}
# Move the rail down a bit so top buttons don't overlap it
WINCH_RAIL_Y = 52
WINCH_RAIL_START_X = 8
WINCH_RAIL_END_X = 312

class CargoScene:
    def _get_prev_scene(self) -> str:
        return "scene_fuel"

    def _get_next_scene(self) -> str:
        return "scene_library"
    def __init__(self, simulator):
        self.font = None
        self.is_text_antialiased = False
        self.simulator = simulator
        self.widgets = []
        self.focused_widget = 0
        self.selected_crate = None  # Currently selected crate for interaction
        self.crate_widgets = []  # Virtual widgets for crates (for Tab cycling)
        self.mouse_held = False  # Track mouse button state
        self.mouse_hold_start_time = 0.0  # For continuous movement
        self.button_hold_times = {}  # Track button hold times
        self.last_update_time = 0.0

        self._init_widgets()

        # On scene init, ensure Refresh availability matches ship motion
        # Force a cargo system update to sync refresh state with current ship speed
        # Use indicated airspeed instead of ground speed to avoid wind drift issues
        nav_motion = self.simulator.game_state.get("navigation", {}).get("motion", {})
        indicated_airspeed = nav_motion.get("indicatedAirspeed", 0.0)
        cargo_state = self.simulator.get_cargo_state()
        
        if indicated_airspeed > 0.1:
            cargo_state["refreshAvailable"] = False
            # Clear loading bay if ship is moving
            if cargo_state.get("loadingBay"):
                cargo_state["loadingBay"] = []
        else:
            cargo_state["refreshAvailable"] = True
            
        # Initialize crate widgets for tab cycling
        self._update_crate_widgets()

    def set_font(self, font, is_text_antialiased=False):
        """Set the font for this scene"""
        self.font = font
        self.is_text_antialiased = is_text_antialiased

    def _init_widgets(self):
        """Initialize all interactive widgets"""
        self.widgets = [
            # Winch movement controls (top row)
            {"id": "winch_left", "type": "button", "position": [16, 28], "size": [54, 18], "text": "< Left", "focused": True, "holdable": True},
            {"id": "winch_right", "type": "button", "position": [76, 28], "size": [62, 18], "text": "Right >", "focused": False, "holdable": True},
            {"id": "winch_up", "type": "button", "position": [144, 28], "size": [48, 18], "text": "^ Up", "focused": False, "holdable": True},
            {"id": "winch_down", "type": "button", "position": [198, 28], "size": [68, 18], "text": "Down v", "focused": False, "holdable": True},
            
            # Action buttons (bottom area) - adjusted for smaller cargo area
            {"id": "attach", "type": "button", "position": [20, 245], "size": [60, 20], "text": "Attach", "focused": False, "holdable": False},
            {"id": "detach", "type": "button", "position": [90, 245], "size": [60, 20], "text": "Detach", "focused": False, "holdable": False},
            {"id": "use_crate", "type": "button", "position": [160, 245], "size": [60, 20], "text": "Use", "focused": False, "holdable": False},
            {"id": "refresh", "type": "button", "position": [230, 245], "size": [60, 20], "text": "Refresh", "focused": False, "holdable": False},
            
            # Navigation controls
            # Move up to match other scenes: y=290 for height 24
            {"id": "prev_scene", "type": "button", "position": [8, 290], "size": [60, 24], "text": "< [", "focused": False, "holdable": False},
            {"id": "next_scene", "type": "button", "position": [252, 290], "size": [60, 24], "text": "] >", "focused": False, "holdable": False},
        ]

    def _update_crate_widgets(self):
        """Update virtual crate widgets for Tab cycling"""
        self.crate_widgets = []
        cargo_state = self.simulator.get_cargo_state()
        
        # Add all crates as virtual widgets for tab cycling
        for crate in cargo_state.get("cargoHold", []) + cargo_state.get("loadingBay", []):
            self.crate_widgets.append({
                "id": f"crate_{crate['id']}",
                "type": "crate",
                "crate_data": crate,
                "focused": False
            })

    def handle_event(self, event) -> Optional[str]:
        """Handle input events"""
        import time
        current_time = time.time()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # If a crate is selected, deselect it first, otherwise go to main menu
                if self.selected_crate is not None:
                    self.selected_crate = None
                else:
                    return "scene_main_menu"
            elif event.key == pygame.K_LEFTBRACKET:
                return "scene_fuel"
            elif event.key == pygame.K_RIGHTBRACKET:
                return "scene_library"
            elif event.key == pygame.K_TAB:
                if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]:
                    self._cycle_focus(-1)
                else:
                    self._cycle_focus(1)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return self._activate_focused()
            
            # Arrow keys for winch movement (always available, not just when focused)
            elif event.key == pygame.K_LEFT:
                self._handle_winch_movement("left", True)
            elif event.key == pygame.K_RIGHT:
                self._handle_winch_movement("right", True)
            elif event.key == pygame.K_UP:
                self._handle_winch_movement("up", True)
            elif event.key == pygame.K_DOWN:
                self._handle_winch_movement("down", True)
            
            # Hotkeys for cargo actions (check if buttons are enabled first)
            elif event.key == pygame.K_a and self._is_widget_enabled("attach"):
                nearest = self._find_nearest_crate_to_hook()
                if nearest:
                    self.simulator.attach_crate(nearest["id"])
            elif event.key == pygame.K_d and self._is_widget_enabled("detach"):
                self.simulator.detach_crate()
            elif event.key == pygame.K_r and self._is_widget_enabled("refresh"):
                self.simulator.refresh_loading_bay()
            elif event.key == pygame.K_u and self._is_widget_enabled("use_crate"):
                if self.selected_crate:
                    success = self.simulator.use_crate(self.selected_crate["id"])
                    if success:
                        self.selected_crate = None
                
        elif event.type == pygame.KEYUP:
            # Stop winch movement on key release (always available)
            if event.key == pygame.K_LEFT:
                self._handle_winch_movement("left", False)
            elif event.key == pygame.K_RIGHT:
                self._handle_winch_movement("right", False)
            elif event.key == pygame.K_UP:
                self._handle_winch_movement("up", False)
            elif event.key == pygame.K_DOWN:
                self._handle_winch_movement("down", False)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                # Stop winch movement when Enter/Space is released from holdable buttons
                if 0 <= self.focused_widget < len(self.widgets):
                    widget = self.widgets[self.focused_widget]
                    if widget.get("holdable", False) and widget["id"].startswith("winch_"):
                        direction = widget["id"].replace("winch_", "")
                        self._handle_winch_movement(direction, False)
                
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
                    # Toggle crate selection
                    if self.selected_crate and self.selected_crate["id"] == clicked_crate["id"]:
                        self.selected_crate = None  # Deselect if same crate
                    else:
                        self.selected_crate = clicked_crate  # Select new crate
                        
                    # Also set focus to this crate for keyboard navigation consistency
                    for i, crate_widget in enumerate(self.crate_widgets):
                        if crate_widget["crate_data"]["id"] == clicked_crate["id"]:
                            self._set_focus(len(self.widgets) + i)
                            break
                else:
                    # Clicked empty space - clear crate selection
                    self.selected_crate = None
                    
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
        """Draw all crates in both areas and attached to winch"""
        cargo_state = self.simulator.get_cargo_state()
        crate_types = cargo_state.get("crateTypes", {})
        
        # Draw cargo hold crates
        for crate in cargo_state.get("cargoHold", []):
            self._render_single_crate(surface, crate, crate_types, "cargoHold")
        
        # Draw loading bay crates
        for crate in cargo_state.get("loadingBay", []):
            self._render_single_crate(surface, crate, crate_types, "loadingBay")
            
        # Draw attached crate hanging from winch
        winch = cargo_state.get("winch", {})
        attached_crate_id = winch.get("attachedCrate")
        if attached_crate_id:
            attached_crate_data = cargo_state.get("attachedCrateData", {})
            if attached_crate_id in attached_crate_data:
                attached_crate = attached_crate_data[attached_crate_id]
                # Calculate position at end of winch cable
                winch_pos = winch.get("position", {"x": 160, "y": 50})
                cable_length = winch.get("cableLength", 0)
                winch_x = int(winch_pos["x"])
                hook_y = WINCH_RAIL_Y + cable_length
                
                # Create a temporary crate dict with calculated position for rendering
                crate_type = crate_types.get(attached_crate["type"], {})
                dims = crate_type.get("dimensions", {"width": 1, "height": 1})
                crate_width = dims["width"] * GRID_SIZE
                
                # Position crate centered horizontally on the hook
                temp_crate = attached_crate.copy()
                temp_crate["position"] = {
                    "x": winch_x - crate_width // 2,
                    "y": hook_y
                }
                
                self._render_single_crate(surface, temp_crate, crate_types, "attached")

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
        
        # Check if this crate is focused via Tab cycling
        crate_focused = self._is_crate_focused(crate["id"])
        
        # Highlight selected crate
        if self.selected_crate and self.selected_crate["id"] == crate["id"]:
            # Draw selection highlight
            pygame.draw.rect(surface, SELECTED_CRATE_COLOR, (x - 2, y - 2, width + 4, height + 4), 2)
        elif crate_focused:
            # Draw focus highlight (different from selection)
            pygame.draw.rect(surface, FOCUS_COLOR, (x - 1, y - 1, width + 2, height + 2), 1)
        
        # Draw crate body
        pygame.draw.rect(surface, fill_color, (x, y, width, height))
        pygame.draw.rect(surface, outline_color, (x, y, width, height), 2)
        
        # Draw X pattern for structural detail (keep lines within crate bounds)
        pygame.draw.line(surface, outline_color, (x, y), (x + width - 1, y + height - 1), 1)
        pygame.draw.line(surface, outline_color, (x + width - 1, y), (x, y + height - 1), 1)

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
            
            # If a crate is attached, preview its placement rectangle in green/red
            attached_crate_id = winch.get("attachedCrate")
            if attached_crate_id:
                crate = None
                crate_types = cargo_state.get("crateTypes", {})
                
                # First check attachedCrateData for crates that are currently attached
                attached_crate_data = cargo_state.get("attachedCrateData", {})
                if attached_crate_id in attached_crate_data:
                    crate = attached_crate_data[attached_crate_id]
                else:
                    # Fallback: check physical areas (for backwards compatibility)
                    for c in cargo_state.get("cargoHold", []) + cargo_state.get("loadingBay", []):
                        if c["id"] == attached_crate_id:
                            crate = c
                            break
                            
                if crate:
                    cinfo = crate_types.get(crate["type"], {})
                    dims = cinfo.get("dimensions", {"width": 1, "height": 1})
                    w = dims["width"] * GRID_SIZE
                    h = dims["height"] * GRID_SIZE
                    # Position crate with top edge at hook level (not above it)
                    x = int(round((winch_x - w // 2) / GRID_SIZE) * GRID_SIZE)
                    y = int(round(cable_end_y / GRID_SIZE) * GRID_SIZE)
                    # Determine validity via simulator
                    can_place = False
                    try:
                        can_place = bool(getattr(self.simulator, "can_place_attached_crate")())
                    except Exception:
                        can_place = False
                    color = VALID_PLACEMENT_COLOR if can_place else INVALID_PLACEMENT_COLOR
                    pygame.draw.rect(surface, color, (x, y, w, h), 2)

    def _render_info_panel(self, surface):
        """Draw information panel at bottom"""
        if not self.font:
            return
            
        info_y = 270  # Moved up to avoid overlap with navigation buttons
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

        # Button colors using theme
        if enabled:
            bg_color = BUTTON_FOCUSED_COLOR if focused else BUTTON_COLOR
            if focused:
                border_color = BUTTON_BORDER_FOCUSED_COLOR
                text_color = BUTTON_TEXT_FOCUSED_COLOR
            else:
                border_color = BUTTON_BORDER_COLOR
                text_color = BUTTON_TEXT_COLOR
        else:
            bg_color = BUTTON_DISABLED_COLOR
            border_color = BUTTON_BORDER_DISABLED_COLOR
            text_color = BUTTON_TEXT_DISABLED_COLOR

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
            # Can detach if something is attached and placement would be valid
            if winch.get("attachedCrate") is None:
                return False
            # Ask simulator for validity
            try:
                return bool(getattr(self.simulator, "can_place_attached_crate")())
            except Exception:
                return True  # fallback
        elif widget_id == "use_crate":
            # Can use if a usable crate is selected, it's in cargo hold, and not attached to winch
            if self.selected_crate is None:
                return False
            if not self._is_crate_usable(self.selected_crate):
                return False
            # Check if crate is attached to winch (can't use attached crates)
            attached_crate_id = winch.get("attachedCrate")
            if attached_crate_id == self.selected_crate.get("id"):
                return False
            # Check if crate is in cargo hold (can't use crates in loading bay)
            cargo_hold = cargo_state.get("cargoHold", [])
            crate_in_cargo_hold = any(c.get("id") == self.selected_crate.get("id") for c in cargo_hold)
            return crate_in_cargo_hold
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
        crate_types = cargo_state.get("crateTypes", {})
        
        for crate in all_crates:
            # Calculate crate top middle edge position (attachment point)
            crate_type = crate_types.get(crate["type"], {})
            dimensions = crate_type.get("dimensions", {"width": 1, "height": 1})
            
            crate_x = crate["position"]["x"] + (dimensions["width"] * GRID_SIZE) / 2  # Middle of top edge
            crate_y = crate["position"]["y"]  # Top edge of crate
            
            # Check if hook is within reasonable distance of crate top middle edge
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
        """Set focus to specific widget, skipping disabled widgets for buttons"""
        # Clear current focus from all widgets and crates
        for widget in self.widgets:
            widget["focused"] = False
        for crate_widget in self.crate_widgets:
            crate_widget["focused"] = False

        total_items = len(self.widgets) + len(self.crate_widgets)
        if total_items == 0:
            self.focused_widget = 0
            return

        # If focusing a button, skip disabled ones
        if 0 <= widget_index < len(self.widgets):
            if not self._is_widget_enabled(self.widgets[widget_index]["id"]):
                # Try to find next enabled widget
                enabled_indices = [i for i, w in enumerate(self.widgets) if self._is_widget_enabled(w["id"])]
                if enabled_indices:
                    self.focused_widget = enabled_indices[0]
                    self.widgets[self.focused_widget]["focused"] = True
                else:
                    self.focused_widget = 0
                return
            self.focused_widget = widget_index
            self.widgets[widget_index]["focused"] = True
        elif len(self.widgets) <= widget_index < len(self.widgets) + len(self.crate_widgets):
            # Focus is on a crate
            crate_index = widget_index - len(self.widgets)
            self.focused_widget = widget_index
            self.crate_widgets[crate_index]["focused"] = True

    def _cycle_focus(self, direction):
        """Cycle focus through enabled widgets and crates (Tab/Shift-Tab)"""
        total_items = len(self.widgets) + len(self.crate_widgets)
        if total_items == 0:
            return

        # Build list of focusable indices: enabled widgets and all crates
        focusable_indices = [i for i, w in enumerate(self.widgets) if self._is_widget_enabled(w["id"])]
        focusable_indices += list(range(len(self.widgets), total_items))  # All crates always focusable
        if not focusable_indices:
            return  # Nothing to focus

        # Find current index in focusable list
        try:
            current_focusable_idx = focusable_indices.index(self.focused_widget)
        except ValueError:
            # If current focus is not focusable, start at first
            current_focusable_idx = 0

        # Move to next/previous focusable
        next_idx = (current_focusable_idx + direction) % len(focusable_indices)
        new_focus = focusable_indices[next_idx]

        # Clear current focus
        if self.focused_widget < len(self.widgets):
            self.widgets[self.focused_widget]["focused"] = False
        else:
            crate_index = self.focused_widget - len(self.widgets)
            if 0 <= crate_index < len(self.crate_widgets):
                self.crate_widgets[crate_index]["focused"] = False

        # Set new focus
        if new_focus < len(self.widgets):
            self.focused_widget = new_focus
            self.widgets[self.focused_widget]["focused"] = True
        else:
            crate_index = new_focus - len(self.widgets)
            self.focused_widget = new_focus
            if 0 <= crate_index < len(self.crate_widgets):
                self.crate_widgets[crate_index]["focused"] = True

    def _is_crate_focused(self, crate_id: str) -> bool:
        """Check if a specific crate is currently focused via Tab cycling"""
        if self.focused_widget >= len(self.widgets):
            crate_index = self.focused_widget - len(self.widgets)
            if 0 <= crate_index < len(self.crate_widgets):
                focused_crate = self.crate_widgets[crate_index]
                return focused_crate["crate_data"]["id"] == crate_id
        return False

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
        """Activate the currently focused widget or crate"""
        total_items = len(self.widgets) + len(self.crate_widgets)
        if not (0 <= self.focused_widget < total_items):
            return None
            
        # Handle crate activation (selection)
        if self.focused_widget >= len(self.widgets):
            crate_index = self.focused_widget - len(self.widgets)
            if 0 <= crate_index < len(self.crate_widgets):
                crate_data = self.crate_widgets[crate_index]["crate_data"]
                # Toggle crate selection - but sync with focus
                if self.selected_crate and self.selected_crate["id"] == crate_data["id"]:
                    self.selected_crate = None  # Deselect if same crate
                else:
                    self.selected_crate = crate_data  # Select the focused crate
            return None
            
        # Handle widget activation
        widget = self.widgets[self.focused_widget]
        widget_id = widget["id"]
        
        # Check if widget is enabled
        if not self._is_widget_enabled(widget_id):
            return None
        
        if widget_id == "prev_scene":
            return "scene_fuel"
        elif widget_id == "next_scene":
            return "scene_library"
        elif widget_id == "attach":
            # Attach to nearest crate (no ID means find nearest)
            nearest = self._find_nearest_crate_to_hook()
            if nearest:
                self.simulator.attach_crate(nearest["id"]) 
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

    def _find_nearest_crate_to_hook(self) -> Optional[Dict]:
        cargo_state = self.simulator.get_cargo_state()
        winch = cargo_state.get("winch", {})
        winch_pos = winch.get("position", {"x": 160, "y": 50})
        cable_length = winch.get("cableLength", 0)
        hook_x = winch_pos["x"]
        hook_y = WINCH_RAIL_Y + cable_length
        best = None
        best_d2 = 1e9
        
        crate_types = cargo_state.get("crateTypes", {})
        
        for crate in cargo_state.get("loadingBay", []) + cargo_state.get("cargoHold", []):
            # Calculate crate top middle edge position (attachment point)
            crate_type = crate_types.get(crate["type"], {})
            dimensions = crate_type.get("dimensions", {"width": 1, "height": 1})
            
            cx = crate["position"]["x"] + (dimensions["width"] * GRID_SIZE) / 2  # Middle of top edge
            cy = crate["position"]["y"]  # Top edge of crate
            
            d2 = (cx - hook_x) ** 2 + (cy - hook_y) ** 2
            if d2 < best_d2:
                best_d2 = d2
                best = crate
        # Within reasonable proximity (<= 20 px)
        if best is not None and best_d2 <= 20 * 20:
            return best
        return None

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except (ValueError, IndexError):
            return DEFAULT_GRAY  # Default gray

    def update(self, dt: float):
        """Update the scene with game state"""
        import time
        current_time = time.time()
        self.last_update_time = current_time

        # Update crate widgets for tab cycling (in case cargo state changed)
        self._update_crate_widgets()

        # If currently focused widget is now disabled, move focus to next enabled widget (if any)
        if self.focused_widget < len(self.widgets):
            if not self._is_widget_enabled(self.widgets[self.focused_widget]["id"]):
                # Only move focus if there is at least one enabled widget or crate
                total_items = len(self.widgets) + len(self.crate_widgets)
                focusable_indices = [i for i, w in enumerate(self.widgets) if self._is_widget_enabled(w["id"])]
                focusable_indices += list(range(len(self.widgets), total_items))
                if focusable_indices:
                    self._cycle_focus(1)

        # Handle continuous button holds
        if self.mouse_held:
            for button_id, start_time in self.button_hold_times.items():
                # Continue the action if button is still held
                if current_time - start_time > 0.1:  # Small delay before continuous action
                    self._handle_button_hold(button_id)
