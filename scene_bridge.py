"""
Bridge Scene for Airship Zero
The primary flight interface showing critical flight instruments and controls
"""
import pygame
import math
from typing import List, Dict, Any, Optional
from theme import (
    LOGICAL_SIZE,
    BACKGROUND_COLOR,
    TEXT_COLOR,
    FOCUS_COLOR,
    WARNING_COLOR,
    GOOD_COLOR,
    BRIDGE_HEADER_COLOR,
    INSTRUMENT_BG_COLOR,
    INSTRUMENT_BORDER_COLOR,
    SKY_COLOR,
    GROUND_COLOR,
    HORIZON_LINE_COLOR,
    PITCH_TICK_COLOR,
    PITCH_LABEL_COLOR,
    PITCH_TEXT_COLOR,
    WIDGET_BG_COLOR,
    WIDGET_BORDER_DISABLED_COLOR,
    BUTTON_BG_FOCUSED,
    BUTTON_BG,
    TEXTBOX_BG_ACTIVE,
    TEXTBOX_BG_FOCUSED,
    TEXTBOX_BG_DISABLED,
    TEXTBOX_BORDER_DISABLED,
    TEXTBOX_TEXT_DISABLED
)

class BridgeScene:
    def __init__(self, simulator):
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focus_index = 0
        self.simulator = simulator
        self.all_widgets_inactive = True
        self.dragging_slider: Optional[int] = None  # For mouse drag support
        
        # Initialize widgets
        self._init_widgets()
        
    def _init_widgets(self):
        """Initialize the bridge widgets"""
        self.widgets = [
            # Navigation display (shifted down for header)
            {
                "id": "altitude",
                "type": "label",
                "position": [8, 32],
                "size": [100, 16],
                "text": "ALT: 1250 ft",
                "focused": False
            },
            {
                "id": "airspeed",
                "type": "label", 
                "position": [120, 32],
                "size": [100, 16],
                "text": "IAS: 85 kts",
                "focused": False
            },
            {
                "id": "heading",
                "type": "label",
                "position": [240, 32],
                "size": [72, 16],
                "text": "HDG: 045°",
                "focused": False
            },
            
            # Engine instruments
            {
                "id": "engine_rpm",
                "type": "label",
                "position": [8, 56],
                "size": [100, 16],
                "text": "RPM: 2650",
                "focused": False
            },
            {
                "id": "manifold_pressure",
                "type": "label",
                "position": [120, 56],
                "size": [100, 16],
                "text": "MAP: 24.5\"",
                "focused": False
            },
            {
                "id": "fuel_flow",
                "type": "label",
                "position": [240, 56],
                "size": [72, 16],
                "text": "FF: 12.8",
                "focused": False
            },
            
            # System status
            {
                "id": "battery_status",
                "type": "button",
                "position": [8, 80],
                "size": [100, 20],
                "text": "BAT A: ON",
                "focused": False
            },
            {
                "id": "fuel_pumps",
                "type": "button",
                "position": [120, 80],
                "size": [100, 20],
                "text": "PUMPS: AUTO",
                "focused": False
            },
            {
                "id": "autopilot",
                "type": "button",
                "position": [240, 80],
                "size": [72, 20],
                "text": "A/P: OFF",
                "focused": False
            },
            
            # Navigation controls (shifted down to avoid overlap)
            {
                "id": "nav_mode",
                "type": "button",
                "position": [8, 108],
                "size": [120, 20],
                "text": "NAV: MANUAL",
                "focused": True
            },
            # Altitude slider (after rudder label, wide)
            {
                "id": "altitude_slider",
                "type": "slider",
                "position": [8, 160],
                "size": [304, 20],  # 320 - 2*8px margin
                "value": 0.3125,  # Default: 1250/4000
                "focused": False,
                "label": "ALTITUDE"
            },
            {
                "id": "heading_set",
                "type": "textbox",
                "position": [232, 108],
                "size": [80, 20],
                "text": "045",
                "focused": False,
                "active": False
            },
            
            # Rudder indicator
            {
                "id": "rudder_indicator",
                "type": "label",
                "position": [8, 136],
                "size": [120, 16],
                "text": "RUD: 0.0°",
                "focused": False
            },
            
            # Scene navigation buttons - circular navigation
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
        """
        Handle pygame events
        Returns: scene transition command or None
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.all_widgets_inactive:
                    return "scene_main_menu"
                else:
                    self._deactivate_all_widgets()
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
                self._handle_rudder_input("left")
            elif event.key == pygame.K_RIGHT:
                self._handle_rudder_input("right")
            elif event.key == pygame.K_MINUS:
                self._adjust_altitude_slider(-0.01)
            elif event.key == pygame.K_EQUALS:
                self._adjust_altitude_slider(0.01)
            else:
                self._handle_text_input(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                logical_pos = self._screen_to_logical(event.pos)
                if logical_pos:
                    clicked_widget = self._get_widget_at_pos(logical_pos)
                    if clicked_widget is not None:
                        self._set_focus(clicked_widget)
                        widget = self.widgets[clicked_widget]
                        if widget["id"] == "altitude_slider":
                            self.dragging_slider = clicked_widget
                            self._set_altitude_slider_from_mouse(clicked_widget, logical_pos)
                        else:
                            return self._activate_focused()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_slider = None
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_slider is not None:
                logical_pos = self._screen_to_logical(event.pos)
                if logical_pos:
                    self._set_altitude_slider_from_mouse(self.dragging_slider, logical_pos)
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
            elif event.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                # Both Enter and Escape deactivate editing but keep focus
                focused_widget["active"] = False
                self._update_all_widgets_inactive_status()
                # Apply value only on Enter, not Escape
                if event.key == pygame.K_RETURN:
                    self._apply_textbox_value(focused_widget)
            elif event.unicode and event.unicode.isprintable():
                # Limit text length based on widget size
                if len(focused_widget["text"]) < 10:  # Reasonable limit
                    focused_widget["text"] += event.unicode
                    
    def _handle_rudder_input(self, direction: str):
        """Handle rudder input for manual flight control"""
        game_state = self.simulator.get_state()
        nav_mode = game_state["navigation"].get("mode", "manual")
        
        # Only allow manual rudder control in manual mode
        if nav_mode == "manual":
            if direction == "left":
                self.simulator.adjust_rudder(-2.0)  # Left rudder by 2 degrees
            elif direction == "right":
                self.simulator.adjust_rudder(2.0)   # Right rudder by 2 degrees
                
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

    def _adjust_altitude_slider(self, delta: float):
        """Adjust the altitude slider value with keyboard +/-"""
        altitude_slider = next((w for w in self.widgets if w["id"] == "altitude_slider"), None)
        if altitude_slider:
            altitude_slider["value"] = max(0.0, min(1.0, altitude_slider["value"] + delta))
            self.simulator.set_autopilot_target("altitude", int(altitude_slider["value"] * 4000))
            
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
                if widget_id == "prev_scene":
                    return self._get_prev_scene()
                elif widget_id == "next_scene":
                    return self._get_next_scene()
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
        
    def _get_prev_scene(self) -> str:
        """Get the previous scene in circular order"""
        return "scene_library"

    def _get_next_scene(self) -> str:
        """Get the next scene in circular order"""
        return "scene_engine_room"
        
    def _toggle_battery(self):
        """Toggle battery A status"""
        self.simulator.toggle_battery("A")
        
    def _toggle_fuel_pumps(self):
        """Legacy fuel pumps button (no-op after refactor to per-tank feed)."""
        pass
        
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
        
        # Show feed status instead of legacy pump mode
        fwd_feed = fuel.get("tanks", {}).get("forward", {}).get("feed", True)
        aft_feed = fuel.get("tanks", {}).get("aft", {}).get("feed", True)
        if fuel.get("engineFeedCut"):
            feed_label = "FEED: --"
        else:
            feed_label = f"FEED: { 'F' if fwd_feed else '-' }{ 'A' if aft_feed else '-' }"
        self._update_widget_text("fuel_pumps", feed_label)
        
        ap_status = "ON" if nav["autopilot"]["engaged"] else "OFF"
        self._update_widget_text("autopilot", f"A/P: {ap_status}")
        
        nav_mode = nav.get("mode", "manual").replace("_", " ").upper()
        self._update_widget_text("nav_mode", f"NAV: {nav_mode}")
        
        # Update rudder indicator
        rudder_angle = nav["controls"].get("rudder", 0.0)
        self._update_widget_text("rudder_indicator", f"RUD: {rudder_angle:+4.1f}°")

        # Update altitude slider value from target altitude
        altitude_slider = next((w for w in self.widgets if w["id"] == "altitude_slider"), None)
        if altitude_slider:
            target_alt = nav["targets"].get("altitude", nav["position"]["altitude"])
            slider_value = max(0.0, min(1.0, target_alt / 4000.0))
            altitude_slider["value"] = slider_value

        heading_widget = next((w for w in self.widgets if w["id"] == "heading_set"), None)
        if heading_widget and not heading_widget.get("active", False):
            target_hdg = nav["targets"].get("heading", nav["position"]["heading"])
            heading_widget["text"] = f"{target_hdg:03.0f}"
        
    def _update_widget_text(self, widget_id: str, new_text: str):
        """Update the text of a specific widget"""
        for widget in self.widgets:
            if widget["id"] == widget_id:
                widget["text"] = new_text
                break
                
    def render(self, surface):
        """Render the bridge scene to the logical surface"""
        surface.fill(BACKGROUND_COLOR)
        
        # Draw colored title header
        pygame.draw.rect(surface, BRIDGE_HEADER_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(surface, TEXT_COLOR, (0, 0, 320, 24), 1)
        
        # Centered title
        if self.font:
            title_text = self.font.render("BRIDGE", self.is_text_antialiased, TEXT_COLOR)
            title_x = (320 - title_text.get_width()) // 2
            surface.blit(title_text, (title_x, 4))
            
            # Draw artificial horizon (shifted down for header)
            self._draw_artificial_horizon(surface, 160, 200, 140, 80)
        
        # Draw all widgets
        for widget in self.widgets:
            self._render_widget(surface, widget)
            
    def _draw_artificial_horizon(self, surface, x, y, w, h):
        """Draw attitude indicator: sky/ground, horizon, pitch scale, numeric pitch."""
        game_state = self.simulator.get_state()
        motion = game_state.get("navigation", {}).get("motion", {})
        pitch = float(motion.get("pitch", 0.0))  # degrees nose up +
        # (Roll placeholder for future; kept at 0 for now)
        # Clamp pitch to visual range
        display_pitch = max(-15.0, min(15.0, pitch))

        # Base rectangle
        pygame.draw.rect(surface, INSTRUMENT_BG_COLOR, (x, y, w, h))
        pygame.draw.rect(surface, INSTRUMENT_BORDER_COLOR, (x, y, w, h), 1)

        center_x = x + w // 2
        center_y = y + h // 2
        pixels_per_deg = 2  # visual scale
        horizon_y = center_y + int(display_pitch * pixels_per_deg)

        # Sky (upper)
        if horizon_y > y:
            sky_h = min(horizon_y - y, h)
            if sky_h > 0:
                pygame.draw.rect(surface, SKY_COLOR, (x + 1, y + 1, w - 2, sky_h - 1))
        # Ground (lower)
        if horizon_y < y + h:
            ground_y = max(horizon_y, y + 1)
            ground_h = (y + h - 1) - ground_y
            if ground_h > 0:
                pygame.draw.rect(surface, GROUND_COLOR, (x + 1, ground_y, w - 2, ground_h))

        # Horizon line (shortened) with brighter contrast
        pygame.draw.line(surface, HORIZON_LINE_COLOR, (x + 8, horizon_y), (x + w - 8, horizon_y), 2)

        # Pitch ladder (every 5°)
        font = self.font
        if font:
            for deg in range(-15, 20, 5):
                if deg == 0:
                    continue  # horizon already drawn
                line_y = center_y + int(deg * pixels_per_deg) - int(display_pitch * pixels_per_deg) + (horizon_y - center_y)
                if y + 4 <= line_y <= y + h - 4:
                    tick_len = 10 if deg % 10 == 0 else 6
                    pygame.draw.line(surface, PITCH_TICK_COLOR, (center_x - tick_len, line_y), (center_x + tick_len, line_y), 1)
                    if deg % 10 == 0:
                        label = f"{abs(deg)}"
                        txt = font.render(label, self.is_text_antialiased, PITCH_LABEL_COLOR)
                        surface.blit(txt, (center_x - tick_len - txt.get_width() - 2, line_y - txt.get_height() // 2))
                        surface.blit(txt, (center_x + tick_len + 2, line_y - txt.get_height() // 2))

        # Aircraft reference symbol
        wing_span = 24
        from theme import FOCUS_COLOR
        pygame.draw.line(surface, FOCUS_COLOR, (center_x - wing_span//2, center_y), (center_x + wing_span//2, center_y), 3)
        pygame.draw.line(surface, FOCUS_COLOR, (center_x, center_y - 6), (center_x, center_y + 6), 3)

        # Numeric pitch indicator bottom-left of instrument
        if font:
            pitch_text = font.render(f"P:{pitch:+.1f}°", self.is_text_antialiased, PITCH_TEXT_COLOR)
            surface.blit(pitch_text, (x + 6, y + h - pitch_text.get_height() - 4))
            
    def _render_widget(self, surface, widget):
        """Render a single widget"""
        if widget["type"] == "label":
            self._render_label(surface, widget)
        elif widget["type"] == "button":
            self._render_button(surface, widget)
        elif widget["type"] == "textbox":
            self._render_textbox(surface, widget)
        elif widget["type"] == "slider":
            self._render_slider(surface, widget)

    def _render_slider(self, surface, widget):
        """Render a slider widget (for altitude control)"""
        x, y = widget["position"]
        w, h = widget["size"]
        value = widget["value"]
        focused = widget.get("focused", False)
        label = widget.get("label", "")

        # Colors
        bg_color = WIDGET_BG_COLOR
        fill_color = FOCUS_COLOR if focused else GOOD_COLOR
        border_color = FOCUS_COLOR if focused else WIDGET_BORDER_DISABLED_COLOR

        # Draw background
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        # Draw filled portion
        fill_width = int(w * value)
        if fill_width > 0:
            pygame.draw.rect(surface, fill_color, (x, y, fill_width, h))
        # Draw border
        pygame.draw.rect(surface, border_color, (x, y, w, h), 1)

        # Draw label and value
        if self.font:
            text_color = FOCUS_COLOR if focused else TEXT_COLOR
            # Label
            if label:
                label_surface = self.font.render(label, self.is_text_antialiased, text_color)
                surface.blit(label_surface, (x, y - 14))
            # Value (altitude)
            altitude_val = int(value * 4000)
            value_text = f"{altitude_val} ft"
            value_surface = self.font.render(value_text, self.is_text_antialiased, text_color)
            value_rect = value_surface.get_rect()
            value_x = x + w - value_rect.width
            value_y = y - 14
            surface.blit(value_surface, (value_x, value_y))
            
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
        bg_color = BUTTON_BG_FOCUSED if focused else BUTTON_BG
        border_color = FOCUS_COLOR if focused else WIDGET_BORDER_DISABLED_COLOR
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
            
    def _render_textbox(self, surface, widget):
        """Render a textbox widget"""
        x, y = widget["position"]
        w, h = widget["size"]
        focused = widget.get("focused", False)
        active = widget.get("active", False)
        
        # Textbox colors
        if active:
            bg_color = TEXTBOX_BG_ACTIVE
            border_color = GOOD_COLOR
            text_color = TEXT_COLOR
        elif focused:
            bg_color = TEXTBOX_BG_FOCUSED
            border_color = FOCUS_COLOR
            text_color = TEXT_COLOR
        else:
            bg_color = TEXTBOX_BG_DISABLED
            border_color = TEXTBOX_BORDER_DISABLED
            text_color = TEXTBOX_TEXT_DISABLED
            
        # Draw textbox
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        pygame.draw.rect(surface, border_color, (x, y, w, h), 1)
        
        # Draw text
        if self.font:
            text_surface = self.font.render(widget["text"], self.is_text_antialiased, text_color)
            surface.blit(text_surface, (x + 4, y + (h - text_surface.get_height()) // 2))
            
            # Draw cursor if active
            if active:
                cursor_x = x + 4 + text_surface.get_width() + 2
                cursor_y = y + 2
                pygame.draw.line(surface, text_color, (cursor_x, cursor_y), (cursor_x, cursor_y + h - 4), 1)
                
    def _set_altitude_slider_from_mouse(self, widget_index: int, pos):
        """Set altitude slider value from mouse position"""
        widget = self.widgets[widget_index]
        if widget["id"] == "altitude_slider":
            x, y = pos
            wx, wy = widget["position"]
            ww, wh = widget["size"]
            rel_x = (x - wx) / ww
            rel_x = max(0.0, min(1.0, rel_x))
            widget["value"] = rel_x
            self.simulator.set_autopilot_target("altitude", int(rel_x * 4000))
