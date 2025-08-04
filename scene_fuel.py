"""
Fuel Management Scene - Tank balancing and transfer controls
Handles fuel system mini-game and center of gravity management
"""
import pygame
from typing import Optional

# Colors
BACKGROUND_COLOR = (20, 20, 30)
TEXT_COLOR = (255, 255, 255)
FOCUS_COLOR = (255, 200, 50)
BUTTON_COLOR = (60, 60, 80)
BUTTON_FOCUSED_COLOR = (80, 80, 120)
WARNING_COLOR = (255, 100, 100)
GOOD_COLOR = (100, 255, 100)
FUEL_HEADER_COLOR = (80, 40, 20)  # Brown for fuel scene

class FuelScene:
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
        """Initialize fuel management widgets"""
        self.widgets = [
            # Navigation buttons
            {"id": "prev_scene", "type": "button", "position": [8, 290], "size": [60, 24], "text": "< [", "focused": True},
            {"id": "next_scene", "type": "button", "position": [252, 290], "size": [60, 24], "text": "] >", "focused": False},
            
            # Tank display
            {"id": "forward_tank", "type": "label", "position": [8, 40], "size": [100, 16], "text": "Forward: 58.3 gal", "focused": False},
            {"id": "center_tank", "type": "label", "position": [8, 60], "size": [100, 16], "text": "Center: 64.8 gal", "focused": False},
            {"id": "aft_tank", "type": "label", "position": [8, 80], "size": [100, 16], "text": "Aft: 63.4 gal", "focused": False},
            
            # Transfer controls (stub)
            {"id": "transfer_fwd", "type": "button", "position": [120, 40], "size": [80, 16], "text": "Transfer", "focused": False},
            {"id": "transfer_aft", "type": "button", "position": [120, 80], "size": [80, 16], "text": "Transfer", "focused": False},
            
            # Balance display
            {"id": "cg_status", "type": "label", "position": [8, 120], "size": [200, 16], "text": "CG: 156.2\" (NORMAL)", "focused": False},
        ]
        
        # Set initial focus
        if self.widgets:
            self.widgets[self.focused_widget]["focused"] = True
    
    def update(self, dt: float):
        """Update fuel display with current simulator data"""
        if not self.simulator:
            return
            
        state = self.simulator.get_state()
        fuel_data = state.get("engines", {}).get("fuel", {})
        
        # Update tank levels
        tanks = fuel_data.get("tanks", [])
        if len(tanks) >= 3:
            self.widgets[2]["text"] = f"Forward: {tanks[0].get('level', 0):.1f} gal"
            self.widgets[3]["text"] = f"Center: {tanks[1].get('level', 0):.1f} gal" 
            self.widgets[4]["text"] = f"Aft: {tanks[2].get('level', 0):.1f} gal"
            
        # Update CG status
        balance = fuel_data.get("balance", {})
        cg_pos = balance.get("centerOfBalance", 0)
        status = balance.get("balanceStatus", "unknown").upper()
        self.widgets[7]["text"] = f"CG: {cg_pos:.1f}\" ({status})"
    
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
        return "scene_navigation"
    
    def _get_next_scene(self) -> str:
        """Get the next scene in circular order"""
        return "scene_cargo"
    
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
        elif widget_id in ["transfer_fwd", "transfer_aft"]:
            # TODO: Implement fuel transfer logic
            pass
            
        return None
    
    def render(self, surface):
        """Render the fuel management scene"""
        # Clear background
        surface.fill(BACKGROUND_COLOR)
        
        if not self.font:
            return
        
        # Draw colored title header
        pygame.draw.rect(surface, FUEL_HEADER_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(surface, TEXT_COLOR, (0, 0, 320, 24), 1)
        
        # Centered title
        title = self.font.render("FUEL MANAGEMENT", True, TEXT_COLOR)
        title_x = (320 - title.get_width()) // 2
        surface.blit(title, (title_x, 4))
        
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
