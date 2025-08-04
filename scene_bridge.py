"""
Bridge Scene for Airship Zero
The primary flight interface showing critical flight instruments and controls
"""
import pygame
import math
from typing import List, Dict, Any, Optional
import pygame
import math
from typing import List, Dict, Any, Optional

# Constants
LOGICAL_SIZE = 320
BACKGROUND_COLOR = (15, 25, 35)  # Dark navy
TEXT_COLOR = (255, 255, 255)
FOCUS_COLOR = (255, 200, 50)
INSTRUMENT_COLOR = (40, 60, 80)
WARNING_COLOR = (220, 60, 60)
GOOD_COLOR = (60, 180, 60)

class BridgeScene:
    def __init__(self, simulator):
        self.font = None
        self.widgets = []
        self.focus_index = 0
        self.simulator = simulator
        self.all_widgets_inactive = True
        
        # Initialize widgets
        self._init_widgets()
        
    def _init_widgets(self):
        """Initialize the bridge widgets"""
        self.widgets = [
            # Navigation display
            {
                "id": "altitude",
                "type": "label",
                "position": [8, 8],
                "size": [100, 16],
                "text": "ALT: 1250 ft",
                "focused": False
            },
            {
                "id": "airspeed",
                "type": "label", 
                "position": [120, 8],
                "size": [100, 16],
                "text": "IAS: 85 kts",
                "focused": False
            },
            {
                "id": "heading",
                "type": "label",
                "position": [240, 8],
                "size": [72, 16],
                "text": "HDG: 045°",
                "focused": False
            },
            
            # Engine instruments
            {
                "id": "engine_rpm",
                "type": "label",
                "position": [8, 32],
                "size": [100, 16],
                "text": "RPM: 2650",
                "focused": False
            },
            {
                "id": "manifold_pressure",
                "type": "label",
                "position": [120, 32],
                "size": [100, 16],
                "text": "MAP: 24.5\"",
                "focused": False
            },
            {
                "id": "fuel_flow",
                "type": "label",
                "position": [240, 32],
                "size": [72, 16],
                "text": "FF: 12.8",
                "focused": False
            },
            
            # System status
            {
                "id": "battery_status",
                "type": "button",
                "position": [8, 56],
                "size": [100, 20],
                "text": "BAT A: ON",
                "focused": False
            },
            {
                "id": "fuel_pumps",
                "type": "button",
                "position": [120, 56],
                "size": [100, 20],
                "text": "PUMPS: AUTO",
                "focused": False
            },
            {
                "id": "autopilot",
                "type": "button",
                "position": [240, 56],
                "size": [72, 20],
                "text": "A/P: OFF",
                "focused": False
            },
            
            # Navigation controls
            {
                "id": "nav_mode",
                "type": "button",
                "position": [8, 84],
                "size": [120, 20],
                "text": "NAV: MANUAL",
                "focused": True
            },
            {
                "id": "altitude_set",
                "type": "textbox",
                "position": [140, 84],
                "size": [80, 20],
                "text": "1250",
                "focused": False,
                "active": False
            },
            {
                "id": "heading_set",
                "type": "textbox",
                "position": [232, 84],
                "size": [80, 20],
                "text": "045",
                "focused": False,
                "active": False
            },
            
            # Scene navigation buttons
            {
                "id": "engine_room",
                "type": "button",
                "position": [8, 280],
                "size": [95, 24],
                "text": "Engine Room",
                "focused": False
            },
            {
                "id": "fuel_system",
                "type": "button",
                "position": [113, 280],
                "size": [95, 24],
                "text": "Fuel System",
                "focused": False
            },
            {
                "id": "navigation",
                "type": "button",
                "position": [218, 280],
                "size": [95, 24],
                "text": "Navigation",
                "focused": False
            }
        ]
        
    def set_font(self, font):
        """Set the font for rendering text"""
        self.font = font
        
    def handle_event(self, event) -> Optional[str]:
        """
        Handle pygame events
        Returns: scene transition command or None
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Check if all widgets are inactive
                if self.all_widgets_inactive:
                    return "scene_main_menu"
                else:
                    # Deactivate any active widgets
                    self._deactivate_all_widgets()
                    
            elif event.key == pygame.K_TAB:
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self._focus_previous()
                else:
                    self._focus_next()
            elif event.key == pygame.K_UP:
                self._focus_previous()
            elif event.key == pygame.K_DOWN:
                self._focus_next()
            elif event.key == pygame.K_LEFT:
                self._focus_previous()
            elif event.key == pygame.K_RIGHT:
                self._focus_next()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return self._activate_focused()
            else:
                # Handle typing for active textboxes
                self._handle_text_input(event)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                logical_pos = self._screen_to_logical(event.pos)
                if logical_pos:
                    clicked_widget = self._get_widget_at_pos(logical_pos)
                    if clicked_widget is not None:
                        self._set_focus(clicked_widget)
                        return self._activate_focused()
                        
        return None
        
    def _deactivate_all_widgets(self):
        """Deactivate all active widgets"""
        for widget in self.widgets:
            if widget["type"] == "textbox":
                widget["active"] = False
        self._update_all_widgets_inactive_status()
        
    def _update_all_widgets_inactive_status(self):
        """Update the all_widgets_inactive flag"""
        self.all_widgets_inactive = True
        for widget in self.widgets:
            if widget["type"] == "textbox" and widget.get("active", False):
                self.all_widgets_inactive = False
                break
                
    def _handle_text_input(self, event):
        """Handle text input for active textboxes"""
        focused_widget = self.widgets[self.focus_index] if 0 <= self.focus_index < len(self.widgets) else None
        if focused_widget and focused_widget["type"] == "textbox" and focused_widget.get("active", False):
            if event.key == pygame.K_BACKSPACE:
                focused_widget["text"] = focused_widget["text"][:-1]
            elif event.key == pygame.K_RETURN:
                focused_widget["active"] = False
                self._update_all_widgets_inactive_status()
                self._apply_textbox_value(focused_widget)
            elif event.unicode and event.unicode.isprintable():
                # Limit text length based on widget size
                if len(focused_widget["text"]) < 10:  # Reasonable limit
                    focused_widget["text"] += event.unicode
                    
    def _apply_textbox_value(self, widget):
        """Apply the textbox value to game state"""
        widget_id = widget["id"]
        try:
            value = widget["text"]
            if widget_id == "altitude_set":
                self.simulator.set_autopilot_target("altitude", float(value))
            elif widget_id == "heading_set":
                self.simulator.set_autopilot_target("heading", float(value) % 360)
        except ValueError:
            # Invalid input, revert to current value
            pass
            
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
        """Set focus to specific widget"""
        if widget_index is not None:
            for widget in self.widgets:
                widget["focused"] = False
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
            
            if widget["type"] == "button":
                # Handle button activations
                if widget_id == "engine_room":
                    return "scene_engine_room"
                elif widget_id == "fuel_system":
                    return "scene_fuel_system"
                elif widget_id == "navigation":
                    return "scene_navigation"
                elif widget_id == "battery_status":
                    self._toggle_battery()
                elif widget_id == "fuel_pumps":
                    self._toggle_fuel_pumps()
                elif widget_id == "autopilot":
                    self._toggle_autopilot()
                elif widget_id == "nav_mode":
                    self._cycle_nav_mode()
                    
            elif widget["type"] == "textbox":
                # Activate textbox for editing
                widget["active"] = True
                self._update_all_widgets_inactive_status()
                
        return None
        
    def _toggle_battery(self):
        """Toggle battery A status"""
        self.simulator.toggle_battery("A")
        
    def _toggle_fuel_pumps(self):
        """Toggle fuel pump mode"""
        self.simulator.toggle_fuel_pump_mode()
        
    def _toggle_autopilot(self):
        """Toggle autopilot"""
        self.simulator.toggle_main_autopilot()
        
    def _cycle_nav_mode(self):
        """Cycle through navigation modes"""
        game_state = self.simulator.get_state()
        navigation = game_state["navigation"]
        modes = ["manual", "heading_hold", "route_follow"]
        current = navigation.get("mode", "manual")
        current_index = modes.index(current) if current in modes else 0
        new_mode = modes[(current_index + 1) % len(modes)]
        self.simulator.set_nav_mode(new_mode)
        
    def update(self, dt: float):
        """Update the scene with game state"""
        # Get current state from simulator
        game_state = self.simulator.get_state()
        nav = game_state["navigation"]
        engine = game_state["engine"]
        electrical = game_state["electrical"]
        fuel = game_state["fuel"]
        
        # Update navigation displays
        self._update_widget_text("altitude", f"ALT: {nav['position']['altitude']:.0f} ft")
        self._update_widget_text("airspeed", f"IAS: {nav['motion']['indicatedAirspeed']:.0f} kts")
        self._update_widget_text("heading", f"HDG: {nav['position']['heading']:03.0f}°")
        
        # Update engine displays
        self._update_widget_text("engine_rpm", f"RPM: {engine['rpm']:.0f}")
        self._update_widget_text("manifold_pressure", f"MAP: {engine['manifoldPressure']:.1f}\"")
        self._update_widget_text("fuel_flow", f"FF: {engine['fuelFlow']:.1f}")
        
        # Update system status
        battery_status = "ON" if electrical["batteryBusA"]["switch"] else "OFF"
        self._update_widget_text("battery_status", f"BAT A: {battery_status}")
        
        pump_mode = fuel["pumpMode"].upper()
        self._update_widget_text("fuel_pumps", f"PUMPS: {pump_mode}")
        
        ap_status = "ON" if nav["autopilot"]["engaged"] else "OFF"
        self._update_widget_text("autopilot", f"A/P: {ap_status}")
        
        nav_mode = nav.get("mode", "manual").replace("_", " ").upper()
        self._update_widget_text("nav_mode", f"NAV: {nav_mode}")
        
    def _update_widget_text(self, widget_id: str, new_text: str):
        """Update the text of a specific widget"""
        for widget in self.widgets:
            if widget["id"] == widget_id:
                widget["text"] = new_text
                break
                
    def render(self, surface):
        """Render the bridge scene to the logical surface"""
        surface.fill(BACKGROUND_COLOR)
        
        # Draw title
        if self.font:
            title_text = self.font.render("BRIDGE", False, TEXT_COLOR)
            surface.blit(title_text, (8, 120))
            
            # Draw artificial horizon
            self._draw_artificial_horizon(surface, 160, 180, 140, 80)
        
        # Draw all widgets
        for widget in self.widgets:
            self._render_widget(surface, widget)
            
    def _draw_artificial_horizon(self, surface, x, y, w, h):
        """Draw a simple artificial horizon display"""
        # Get pitch and roll from game state
        game_state = self.simulator.get_state()
        nav = game_state["navigation"] 
        motion = nav.get("motion", {})
        pitch = motion.get("pitch", 0.0)  # degrees
        roll = motion.get("roll", 0.0)    # degrees
        
        # Draw background
        pygame.draw.rect(surface, (40, 60, 80), (x, y, w, h))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, w, h), 1)
        
        # Draw sky (blue) and ground (brown) 
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Simple horizon line
        horizon_y = center_y + int(pitch * 2)  # 2 pixels per degree pitch
        
        # Sky (above horizon)
        if horizon_y > y:
            sky_rect = pygame.Rect(x + 1, y + 1, w - 2, min(horizon_y - y, h - 2))
            pygame.draw.rect(surface, (100, 150, 255), sky_rect)
            
        # Ground (below horizon)
        if horizon_y < y + h:
            ground_rect = pygame.Rect(x + 1, max(horizon_y, y + 1), w - 2, (y + h - 1) - max(horizon_y, y + 1))
            pygame.draw.rect(surface, (139, 69, 19), ground_rect)
            
        # Horizon line
        pygame.draw.line(surface, (255, 255, 255), (x + 1, horizon_y), (x + w - 1, horizon_y), 2)
        
        # Aircraft symbol (center reference)
        pygame.draw.line(surface, (255, 255, 0), (center_x - 15, center_y), (center_x + 15, center_y), 3)
        pygame.draw.line(surface, (255, 255, 0), (center_x, center_y - 5), (center_x, center_y + 5), 3)
        if horizon_y > y:
            sky_rect = (x + 1, y + 1, w - 2, min(horizon_y - y, h - 2))
            pygame.draw.rect(surface, (50, 100, 150), sky_rect)
            
        # Ground (below horizon)
        if horizon_y < y + h:
            ground_y = max(horizon_y, y + 1)
            ground_rect = (x + 1, ground_y, w - 2, y + h - ground_y - 1)
            pygame.draw.rect(surface, (100, 70, 50), ground_rect)
            
        # Draw horizon line
        pygame.draw.line(surface, (255, 255, 255), (x + 10, horizon_y), (x + w - 10, horizon_y), 2)
        
        # Draw aircraft symbol (fixed in center)
        aircraft_size = 8
        pygame.draw.line(surface, (255, 200, 50), 
                        (center_x - aircraft_size, center_y), 
                        (center_x + aircraft_size, center_y), 3)
        pygame.draw.line(surface, (255, 200, 50),
                        (center_x, center_y - aircraft_size//2),
                        (center_x, center_y + aircraft_size//2), 3)
            
    def _render_widget(self, surface, widget):
        """Render a single widget"""
        if widget["type"] == "label":
            self._render_label(surface, widget)
        elif widget["type"] == "button":
            self._render_button(surface, widget)
        elif widget["type"] == "textbox":
            self._render_textbox(surface, widget)
            
    def _render_label(self, surface, widget):
        """Render a label widget"""
        if self.font:
            color = FOCUS_COLOR if widget.get("focused", False) else TEXT_COLOR
            text_surface = self.font.render(widget["text"], False, color)
            surface.blit(text_surface, widget["position"])
            
    def _render_button(self, surface, widget):
        """Render a button widget"""
        x, y = widget["position"]
        w, h = widget["size"]
        focused = widget.get("focused", False)
        
        # Button colors
        bg_color = (80, 100, 120) if focused else (60, 80, 100)
        border_color = FOCUS_COLOR if focused else (120, 120, 120)
        text_color = FOCUS_COLOR if focused else TEXT_COLOR
        
        # Draw button
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        pygame.draw.rect(surface, border_color, (x, y, w, h), 1)
        
        # Draw text
        if self.font:
            text_surface = self.font.render(widget["text"], False, text_color)
            text_rect = text_surface.get_rect()
            text_x = x + (w - text_rect.width) // 2
            text_y = y + (h - text_rect.height) // 2
            surface.blit(text_surface, (text_x, text_y))
            
    def _render_textbox(self, surface, widget):
        """Render a textbox widget"""
        x, y = widget["position"]
        w, h = widget["size"]
        focused = widget.get("focused", False)
        active = widget.get("active", False)
        
        # Textbox colors
        if active:
            bg_color = (40, 60, 40)
            border_color = GOOD_COLOR
            text_color = TEXT_COLOR
        elif focused:
            bg_color = (50, 50, 80)
            border_color = FOCUS_COLOR
            text_color = TEXT_COLOR
        else:
            bg_color = (30, 30, 50)
            border_color = (100, 100, 100)
            text_color = (180, 180, 180)
            
        # Draw textbox
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        pygame.draw.rect(surface, border_color, (x, y, w, h), 1)
        
        # Draw text
        if self.font:
            text_surface = self.font.render(widget["text"], False, text_color)
            surface.blit(text_surface, (x + 4, y + (h - text_surface.get_height()) // 2))
            
            # Draw cursor if active
            if active:
                cursor_x = x + 4 + text_surface.get_width() + 2
                cursor_y = y + 2
                pygame.draw.line(surface, text_color, (cursor_x, cursor_y), (cursor_x, cursor_y + h - 4), 1)
