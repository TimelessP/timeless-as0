"""
Communications Scene - Radio and transponder controls
Handles radio frequencies, communications log, and transponder settings
"""
import pygame
from typing import Optional

# Colors
BACKGROUND_COLOR = (20, 20, 30)
TEXT_COLOR = (255, 255, 255)
FOCUS_COLOR = (255, 200, 50)
BUTTON_COLOR = (60, 60, 80)
BUTTON_FOCUSED_COLOR = (80, 80, 120)
GOOD_COLOR = (100, 255, 100)

class CommunicationsScene:
    def __init__(self, simulator):
        self.simulator = simulator
        self.font = None
        self.widgets = []
        self.focused_widget = 0
        
        self._init_widgets()
    
    def set_font(self, font):
        """Set the font for this scene"""
        self.font = font
    
    def _init_widgets(self):
        """Initialize communications widgets"""
        self.widgets = [
            # Navigation buttons
            {"id": "prev_scene", "type": "button", "position": [8, 290], "size": [60, 24], "text": "← [", "focused": True},
            {"id": "next_scene", "type": "button", "position": [252, 290], "size": [60, 24], "text": "] →", "focused": False},
            
            # Radio displays
            {"id": "com1_freq", "type": "label", "position": [8, 40], "size": [120, 16], "text": "COM1: 121.500", "focused": False},
            {"id": "com1_standby", "type": "label", "position": [8, 60], "size": [120, 16], "text": "STBY: 120.900", "focused": False},
            {"id": "com2_freq", "type": "label", "position": [140, 40], "size": [120, 16], "text": "COM2: 122.800", "focused": False},
            {"id": "com2_standby", "type": "label", "position": [140, 60], "size": [120, 16], "text": "STBY: 123.050", "focused": False},
            
            # Transponder
            {"id": "xpdr_code", "type": "label", "position": [8, 90], "size": [100, 16], "text": "XPDR: 1200", "focused": False},
            {"id": "xpdr_mode", "type": "label", "position": [120, 90], "size": [100, 16], "text": "Mode: STBY", "focused": False},
            
            # Volume controls (stub)
            {"id": "com1_vol", "type": "button", "position": [8, 120], "size": [50, 16], "text": "Vol", "focused": False},
            {"id": "com2_vol", "type": "button", "position": [70, 120], "size": [50, 16], "text": "Vol", "focused": False},
            
            # Recent messages
            {"id": "msg_1", "type": "label", "position": [8, 160], "size": [300, 16], "text": "Tower: Contact approach 120.9", "focused": False},
            {"id": "msg_2", "type": "label", "position": [8, 180], "size": [300, 16], "text": "Approach: Level 1250", "focused": False},
        ]
        
        # Set initial focus
        if self.widgets:
            self.widgets[self.focused_widget]["focused"] = True
    
    def update(self):
        """Update communications display with current simulator data"""
        if not self.simulator:
            return
            
        state = self.simulator.get_state()
        comms = state.get("communications", {})
        radio = comms.get("radio", {})
        
        # Update COM1
        com1 = radio.get("com1", {})
        self.widgets[2]["text"] = f"COM1: {com1.get('frequency', 121.500):.3f}"
        self.widgets[3]["text"] = f"STBY: {com1.get('standby', 120.900):.3f}"
        
        # Update COM2  
        com2 = radio.get("com2", {})
        self.widgets[4]["text"] = f"COM2: {com2.get('frequency', 122.800):.3f}"
        self.widgets[5]["text"] = f"STBY: {com2.get('standby', 123.050):.3f}"
        
        # Update transponder
        xpdr = comms.get("transponder", {})
        self.widgets[6]["text"] = f"XPDR: {xpdr.get('code', '1200')}"
        self.widgets[7]["text"] = f"Mode: {xpdr.get('mode', 'standby').upper()}"
        
        # Update recent messages
        log = comms.get("log", [])
        if len(log) >= 2:
            self.widgets[10]["text"] = log[-1].get("message", "")[:40]
            self.widgets[11]["text"] = log[-2].get("message", "")[:40]
    
    def handle_event(self, event) -> Optional[str]:
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "scene_main_menu"
            elif event.key == pygame.K_LEFTBRACKET:  # [
                return self._get_prev_scene()
            elif event.key == pygame.K_RIGHTBRACKET:  # ]
                return self._get_next_scene()
            elif event.key == pygame.K_TAB:
                if event.mod & pygame.KMOD_SHIFT:
                    self._cycle_focus(-1)
                else:
                    self._cycle_focus(1)
            elif event.key == pygame.K_RETURN:
                return self._activate_focused()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                clicked_widget = self._get_widget_at_pos(event.pos)
                if clicked_widget is not None:
                    self._set_focus(clicked_widget)
                    return self._activate_focused()
        
        return None
    
    def _get_prev_scene(self) -> str:
        """Get the previous scene in circular order"""
        return "scene_cargo"
    
    def _get_next_scene(self) -> str:
        """Get the next scene in circular order"""
        return "scene_camera"
    
    def _get_widget_at_pos(self, pos):
        """Find widget at given position"""
        x, y = pos
        for i, widget in enumerate(self.widgets):
            wx, wy = widget["position"]
            ww, wh = widget["size"]
            if wx <= x <= wx + ww and wy <= y <= wy + wh:
                return i
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
    
    def _activate_focused(self) -> Optional[str]:
        """Activate the currently focused widget"""
        if not self.widgets:
            return None
            
        widget = self.widgets[self.focused_widget]
        widget_id = widget["id"]
        
        if widget_id == "prev_scene":
            return self._get_prev_scene()
        elif widget_id == "next_scene":
            return self._get_next_scene()
        elif widget_id in ["com1_vol", "com2_vol"]:
            # TODO: Implement volume controls
            pass
            
        return None
    
    def render(self, surface):
        """Render the communications scene"""
        # Clear background
        surface.fill(BACKGROUND_COLOR)
        
        if not self.font:
            return
        
        # Title
        title = self.font.render("COMMUNICATIONS", True, TEXT_COLOR)
        surface.blit(title, (8, 8))
        
        # Render widgets
        for widget in self.widgets:
            self._render_widget(surface, widget)
    
    def _render_widget(self, surface, widget):
        """Render a single widget"""
        if not self.font:
            return
            
        x, y = widget["position"]
        w, h = widget["size"]
        focused = widget["focused"]
        widget_type = widget["type"]
        text = widget["text"]
        
        if widget_type == "button":
            # Draw button background
            color = BUTTON_FOCUSED_COLOR if focused else BUTTON_COLOR
            pygame.draw.rect(surface, color, (x, y, w, h))
            pygame.draw.rect(surface, TEXT_COLOR, (x, y, w, h), 1)
            
            # Draw button text
            text_color = FOCUS_COLOR if focused else TEXT_COLOR
            text_surface = self.font.render(text, True, text_color)
            text_x = x + (w - text_surface.get_width()) // 2
            text_y = y + (h - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
            
        elif widget_type == "label":
            # Draw label text
            text_color = FOCUS_COLOR if focused else TEXT_COLOR
            text_surface = self.font.render(text, True, text_color)
            surface.blit(text_surface, (x, y))
