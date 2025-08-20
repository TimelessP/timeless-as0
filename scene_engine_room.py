"""
Engine Room Scene for Airship Zero
Engine monitoring and control interface
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
    CAUTION_COLOR,
    ENGINE_HEADER_COLOR,
    ENGINE_BUTTON_BG_FOCUSED,
    ENGINE_BUTTON_BG,
    ENGINE_BUTTON_BORDER_DISABLED,
    ENGINE_BUTTON_EMERGENCY_BG,
    ENGINE_SLIDER_BG
)

class EngineRoomScene:
    def __init__(self, simulator):
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focus_index = 0
        self.simulator = simulator
        self.all_widgets_inactive = True
        self.dragging_widget: Optional[int] = None  # For mouse drag support
        
        self._init_widgets()
        
    def _init_widgets(self):
        """Initialize engine room widgets"""
        self.widgets = [
            # Engine status displays (shifted down for header)
            {
                "id": "engine_status",
                "type": "label",
                "position": [8, 32],
                "size": [120, 16],
                "text": "ENGINE: RUNNING",
                "focused": False
            },
            {
                "id": "rpm_display",
                "type": "label",
                "position": [140, 32],
                "size": [100, 16],
                "text": "RPM: 2650",
                "focused": False
            },
            {
                "id": "manifold_pressure",
                "type": "label",
                "position": [250, 32],
                "size": [60, 16],
                "text": "MP: 24.5",
                "focused": False
            },
            
            # Temperature gauges
            {
                "id": "oil_temp",
                "type": "label",
                "position": [8, 56],
                "size": [100, 16],
                "text": "OIL TEMP: 185°F",
                "focused": False
            },
            {
                "id": "cyl_head_temp",
                "type": "label",
                "position": [120, 56],
                "size": [100, 16],
                "text": "CHT: 320°F",
                "focused": False
            },
            {
                "id": "exhaust_temp",
                "type": "label",
                "position": [230, 56],
                "size": [80, 16],
                "text": "EGT: 1450°F",
                "focused": False
            },
            
            # Pressure gauges
            {
                "id": "oil_pressure",
                "type": "label",
                "position": [8, 80],
                "size": [100, 16],
                "text": "OIL PRESS: 65 PSI",
                "focused": False
            },
            {
                "id": "fuel_pressure",
                "type": "label",
                "position": [120, 80],
                "size": [100, 16],
                "text": "FUEL PRESS: 22 PSI",
                "focused": False
            },
            {
                "id": "fuel_flow",
                "type": "label",
                "position": [230, 80],
                "size": [80, 16],
                "text": "FLOW: 12.8 GPH",
                "focused": False
            },
            
            # Engine controls
            {
                "id": "throttle_control",
                "type": "slider",
                "position": [8, 110],
                "size": [150, 20],
                "value": 0.75,
                "focused": True,
                "label": "THROTTLE"
            },
            {
                "id": "mixture_control",
                "type": "slider",
                "position": [168, 110],
                "size": [140, 20],
                "value": 0.85,
                "focused": False,
                "label": "MIXTURE"
            },
            
            # Propeller controls
            {
                "id": "prop_control",
                "type": "slider",
                "position": [8, 145],
                "size": [150, 20],
                "value": 0.80,
                "focused": False,
                "label": "PROP PITCH"
            },
            
            # Engine start/stop
            {
                "id": "engine_start",
                "type": "button",
                "position": [8, 180],
                "size": [80, 24],
                "text": "START",
                "focused": False
            },
            {
                "id": "engine_stop",
                "type": "button",
                "position": [98, 180],
                "size": [80, 24],
                "text": "STOP",
                "focused": False
            },
            
            # Navigation - circular navigation
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
                if self.all_widgets_inactive:
                    return "scene_main_menu"
                else:
                    self._deactivate_all_widgets()
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
            elif event.key == pygame.K_MINUS:
                self._adjust_focused_slider(-0.05)
            elif event.key == pygame.K_EQUALS:  # Plus key
                self._adjust_focused_slider(0.05)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                logical_pos = self._screen_to_logical(event.pos)
                if logical_pos:
                    clicked_widget = self._get_widget_at_pos(logical_pos)
                    if clicked_widget is not None:
                        self._set_focus(clicked_widget)
                        widget = self.widgets[clicked_widget]
                        if widget["type"] == "slider":
                            # Start dragging for sliders
                            self.dragging_widget = clicked_widget
                            self._set_slider_value_from_mouse(clicked_widget, logical_pos)
                        else:
                            return self._activate_focused()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.dragging_widget = None
        
        elif event.type == pygame.MOUSEMOTION and self.dragging_widget is not None:
            # Update slider value while dragging
            logical_pos = self._screen_to_logical(event.pos)
            if logical_pos:
                self._set_slider_value_from_mouse(self.dragging_widget, logical_pos)
                        
        return None
        
    def _deactivate_all_widgets(self):
        """Deactivate all active widgets"""
        self.all_widgets_inactive = True
        
    def _adjust_focused_slider(self, delta: float):
        """Adjust the focused slider value"""
        if 0 <= self.focus_index < len(self.widgets):
            widget = self.widgets[self.focus_index]
            if widget["type"] == "slider":
                widget["value"] = max(0.0, min(1.0, widget["value"] + delta))
                self._apply_slider_change(widget)
    
    def _set_slider_value_from_mouse(self, widget_index: int, pos):
        """Set slider value from mouse position"""
        if 0 <= widget_index < len(self.widgets):
            widget = self.widgets[widget_index]
            if widget["type"] == "slider":
                x, y = pos
                wx, wy = widget["position"]
                ww, wh = widget["size"]
                
                # Calculate relative position within slider
                rel_x = (x - wx) / ww
                rel_x = max(0.0, min(1.0, rel_x))  # Clamp to [0, 1]
                
                widget["value"] = rel_x
                self._apply_slider_change(widget)
    
    def _apply_slider_change(self, widget):
        """Apply slider value change to simulator"""
        widget_id = widget["id"]
        value = widget["value"]
        
        if widget_id == "throttle_control":
            self.simulator.set_engine_control("throttle", value)
        elif widget_id == "mixture_control":
            self.simulator.set_engine_control("mixture", value)
        elif widget_id == "prop_control":
            self.simulator.set_engine_control("propeller", value)
                
    def _apply_slider_value(self, widget):
        """Apply slider value to game state"""
        widget_id = widget["id"]
        value = widget["value"]
        
        if widget_id == "throttle_control":
            self.simulator.set_engine_control("throttle", value)
        elif widget_id == "mixture_control":
            self.simulator.set_engine_control("mixture", value)
        elif widget_id == "prop_control":
            self.simulator.set_engine_control("propeller", value)
            
    def _screen_to_logical(self, screen_pos) -> Optional[tuple]:
        """Convert screen coordinates to logical coordinates"""
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
                if widget_id == "prev_scene":
                    return self._get_prev_scene()
                elif widget_id == "next_scene":
                    return self._get_next_scene()
                elif widget_id == "engine_start":
                    self._start_engine()
                elif widget_id == "engine_stop":
                    self._stop_engine()
        return None
        
    def _get_prev_scene(self) -> str:
        """Get the previous scene in circular order"""
        return "scene_bridge"

    def _get_next_scene(self) -> str:
        """Get the next scene in circular order"""
        return "scene_navigation"
        
    def _start_engine(self):
        """Start the engine"""
        # Use the simulator's toggle method if engine is currently off
        game_state = self.simulator.get_state()
        if not game_state["engine"]["running"]:
            self.simulator.toggle_engine()
            
    def _stop_engine(self):
        """Stop the engine normally"""
        # Use the simulator's toggle method if engine is currently on
        game_state = self.simulator.get_state()
        if game_state["engine"]["running"]:
            self.simulator.toggle_engine()
        
        
    def _feather_prop(self):
        """Feather the propeller"""
        self.simulator.game_state["engine"]["propellerFeathered"] = True
        
    def _unfeather_prop(self):
        """Unfeather the propeller"""
        self.simulator.game_state["engine"]["propellerFeathered"] = False
        
    def update(self, dt: float):
        """Update the scene"""
        # Get current state from simulator
        game_state = self.simulator.get_state()
        engine = game_state["engine"]
        
        # Update engine displays
        status = "RUNNING" if engine["running"] else "STOPPED"
        self._update_widget_text("engine_status", f"ENGINE: {status}")
        self._update_widget_text("rpm_display", f"RPM: {engine['rpm']:.0f}")
        self._update_widget_text("manifold_pressure", f"MP: {engine['manifoldPressure']:.1f}")
        
        # Update temperature displays with color coding
        oil_temp = engine["oilTemperature"]
        self._update_widget_text("oil_temp", f"OIL TEMP: {oil_temp:.0f}°F")
        
        cht = engine["cylinderHeadTemp"]
        self._update_widget_text("cyl_head_temp", f"CHT: {cht:.0f}°F")
        
        egt = engine["exhaustGasTemp"]
        self._update_widget_text("exhaust_temp", f"EGT: {egt:.0f}°F")
        
        # Update pressure displays
        oil_press = engine["oilPressure"]
        self._update_widget_text("oil_pressure", f"OIL PRESS: {oil_press:.0f} PSI")
        
        fuel_press = engine.get("fuelPressure", 22.0)
        self._update_widget_text("fuel_pressure", f"FUEL PRESS: {fuel_press:.0f} PSI")
        
        fuel_flow = engine["fuelFlow"]
        self._update_widget_text("fuel_flow", f"FLOW: {fuel_flow:.1f} GPH")
        
        # Update control positions from game state
        controls = engine.get("controls", {})
        throttle_pos = controls.get("throttle", 0.75)
        self._update_widget_value("throttle_control", throttle_pos)
        
        mixture_pos = controls.get("mixture", 0.85)
        self._update_widget_value("mixture_control", mixture_pos)
        
        prop_pos = controls.get("propeller", 0.80)
        self._update_widget_value("prop_control", prop_pos)
        
    def _update_widget_text(self, widget_id: str, new_text: str):
        """Update the text of a specific widget"""
        for widget in self.widgets:
            if widget["id"] == widget_id:
                widget["text"] = new_text
                break
                
    def _update_widget_value(self, widget_id: str, new_value: float):
        """Update the value of a specific widget"""
        for widget in self.widgets:
            if widget["id"] == widget_id:
                widget["value"] = new_value
                break
                
    def render(self, surface):
        """Render the engine room scene"""
        surface.fill(BACKGROUND_COLOR)
        
        # Draw colored title header
        pygame.draw.rect(surface, ENGINE_HEADER_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(surface, TEXT_COLOR, (0, 0, 320, 24), 1)
        
        # Centered title
        if self.font:
            title_text = self.font.render("ENGINE ROOM", self.is_text_antialiased, TEXT_COLOR)
            title_x = (320 - title_text.get_width()) // 2
            surface.blit(title_text, (title_x, 4))
            
            # Draw engine schematic (shifted down for header)
            self._draw_engine_schematic(surface, 50, 220, 220, 60)
        
        # Draw all widgets
        for widget in self.widgets:
            self._render_widget(surface, widget)
            
    def _draw_engine_schematic(self, surface, x, y, w, h):
        """Draw a simple engine schematic"""
        game_state = self.simulator.get_state()
        engine = game_state["engine"]
        
        # Engine block
        block_color = GOOD_COLOR if engine["running"] else (100, 100, 100)
        pygame.draw.rect(surface, block_color, (x + 60, y + 10, 80, 40))
        pygame.draw.rect(surface, TEXT_COLOR, (x + 60, y + 10, 80, 40), 1)
        
        # Propeller
        prop_color = GOOD_COLOR if engine["running"] and not engine.get("propellerFeathered", False) else WARNING_COLOR
        pygame.draw.circle(surface, prop_color, (x + 20, y + 30), 15, 2)
        pygame.draw.line(surface, prop_color, (x + 5, y + 30), (x + 35, y + 30), 2)
        pygame.draw.line(surface, prop_color, (x + 20, y + 15), (x + 20, y + 45), 2)
        
        # Connecting line
        pygame.draw.line(surface, TEXT_COLOR, (x + 35, y + 30), (x + 60, y + 30), 2)
        
        # Exhaust
        if engine["running"]:
            for i in range(3):
                exhaust_x = x + 150 + i * 20
                pygame.draw.circle(surface, (255, 100, 100), (exhaust_x, y + 30), 3)
                
        # Temperature indicators
        oil_temp = engine["oilTemperature"]
        temp_color = WARNING_COLOR if oil_temp > 220 else CAUTION_COLOR if oil_temp > 200 else GOOD_COLOR
        pygame.draw.circle(surface, temp_color, (x + 100, y + 5), 3)
        
    def _render_widget(self, surface, widget):
        """Render a single widget"""
        if widget["type"] == "label":
            self._render_label(surface, widget)
        elif widget["type"] == "button":
            self._render_button(surface, widget)
        elif widget["type"] == "slider":
            self._render_slider(surface, widget)
            
    def _render_label(self, surface, widget):
        """Render a label widget"""
        if self.font:
            # Determine color based on content
            text = widget["text"]
            color = TEXT_COLOR
            
            # Color code based on content
            if "TEMP:" in text and "°F" in text:
                try:
                    temp_value = float(text.split(":")[1].replace("°F", "").strip())
                    if "OIL" in text:
                        color = WARNING_COLOR if temp_value > 220 else CAUTION_COLOR if temp_value > 200 else GOOD_COLOR
                    elif "CHT" in text:
                        color = WARNING_COLOR if temp_value > 400 else CAUTION_COLOR if temp_value > 350 else GOOD_COLOR
                except:
                    pass
            elif "PRESS:" in text and "PSI" in text:
                try:
                    press_value = float(text.split(":")[1].replace("PSI", "").strip())
                    if "OIL" in text:
                        color = WARNING_COLOR if press_value < 20 else CAUTION_COLOR if press_value < 40 else GOOD_COLOR
                except:
                    pass
                    
            if widget.get("focused", False):
                color = FOCUS_COLOR
                
            text_surface = self.font.render(text, self.is_text_antialiased, color)
            surface.blit(text_surface, widget["position"])
            
    def _render_button(self, surface, widget):
        """Render a button widget"""
        x, y = widget["position"]
        w, h = widget["size"]
        focused = widget.get("focused", False)
        
        # Special coloring for emergency stop
        if widget["id"] == "emergency_stop":
            bg_color = WARNING_COLOR if focused else ENGINE_BUTTON_EMERGENCY_BG
            text_color = TEXT_COLOR
            border_color = FOCUS_COLOR if focused else ENGINE_BUTTON_BORDER_DISABLED
        else:
            bg_color = ENGINE_BUTTON_BG_FOCUSED if focused else ENGINE_BUTTON_BG
            text_color = FOCUS_COLOR if focused else TEXT_COLOR
            border_color = FOCUS_COLOR if focused else ENGINE_BUTTON_BORDER_DISABLED
        
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
            
    def _render_slider(self, surface, widget):
        """Render a slider widget"""
        x, y = widget["position"]
        w, h = widget["size"]
        value = widget["value"]
        focused = widget.get("focused", False)
        label = widget.get("label", "")
        
        # Colors
        bg_color = ENGINE_SLIDER_BG
        fill_color = FOCUS_COLOR if focused else GOOD_COLOR
        border_color = FOCUS_COLOR if focused else (120, 120, 120)
        
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
                
            # Value percentage
            value_text = f"{value * 100:.0f}%"
            value_surface = self.font.render(value_text, self.is_text_antialiased, text_color)
            value_rect = value_surface.get_rect()
            value_x = x + w - value_rect.width
            value_y = y - 14
            surface.blit(value_surface, (value_x, value_y))
