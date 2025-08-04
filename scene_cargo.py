"""
Cargo Management Scene - Weight and balance management
Handles cargo loading, weight distribution, and center of gravity
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

class CargoScene:
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
        """Initialize cargo management widgets"""
        self.widgets = [
            # Navigation buttons
            {"id": "prev_scene", "type": "button", "position": [8, 290], "size": [60, 24], "text": "← [", "focused": True},
            {"id": "next_scene", "type": "button", "position": [252, 290], "size": [60, 24], "text": "] →", "focused": False},
            
            # Weight display
            {"id": "total_weight", "type": "label", "position": [8, 40], "size": [150, 16], "text": "Total: 145.8 lbs", "focused": False},
            {"id": "max_weight", "type": "label", "position": [8, 60], "size": [150, 16], "text": "Max: 500.0 lbs", "focused": False},
            {"id": "remaining", "type": "label", "position": [8, 80], "size": [150, 16], "text": "Available: 354.2 lbs", "focused": False},
            
            # Compartments
            {"id": "main_cabin", "type": "label", "position": [8, 110], "size": [150, 16], "text": "Main Cabin: 89.3 lbs", "focused": False},
            {"id": "rear_compartment", "type": "label", "position": [8, 130], "size": [150, 16], "text": "Rear: 56.5 lbs", "focused": False},
            
            # CG status
            {"id": "cg_position", "type": "label", "position": [8, 160], "size": [200, 16], "text": "CG: 156.2\" (NORMAL)", "focused": False},
            
            # Load/unload controls (stub)
            {"id": "load_cargo", "type": "button", "position": [180, 110], "size": [60, 16], "text": "Load", "focused": False},
            {"id": "unload_cargo", "type": "button", "position": [250, 110], "size": [60, 16], "text": "Unload", "focused": False},
        ]
        
        # Set initial focus
        if self.widgets:
            self.widgets[self.focused_widget]["focused"] = True
    
    def update(self):
        """Update cargo display with current simulator data"""
        if not self.simulator:
            return
            
        state = self.simulator.get_state()
        cargo_data = state.get("cargo", {})
        
        # Update weight info
        total_weight = cargo_data.get("totalWeight", 0)
        max_capacity = cargo_data.get("maxCapacity", 500)
        remaining = max_capacity - total_weight
        
        self.widgets[2]["text"] = f"Total: {total_weight:.1f} lbs"
        self.widgets[3]["text"] = f"Max: {max_capacity:.1f} lbs"
        self.widgets[4]["text"] = f"Available: {remaining:.1f} lbs"
        
        # Update compartments
        compartments = cargo_data.get("compartments", [])
        if len(compartments) >= 2:
            self.widgets[5]["text"] = f"Main Cabin: {compartments[0].get('currentWeight', 0):.1f} lbs"
            self.widgets[6]["text"] = f"Rear: {compartments[1].get('currentWeight', 0):.1f} lbs"
        
        # Update CG
        cg_data = cargo_data.get("centerOfGravity", {})
        cg_pos = cg_data.get("position", 0)
        within_limits = cg_data.get("withinLimits", True)
        status = "NORMAL" if within_limits else "WARNING"
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
        return "scene_fuel"
    
    def _get_next_scene(self) -> str:
        """Get the next scene in circular order"""
        return "scene_communications"
    
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
        elif widget_id in ["load_cargo", "unload_cargo"]:
            # TODO: Implement cargo loading logic
            pass
            
        return None
    
    def render(self, surface):
        """Render the cargo management scene"""
        # Clear background
        surface.fill(BACKGROUND_COLOR)
        
        if not self.font:
            return
        
        # Title
        title = self.font.render("CARGO MANAGEMENT", True, TEXT_COLOR)
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
