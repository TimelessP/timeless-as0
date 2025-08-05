"""
Missions Scene - Mission briefings, progress, and objectives
Handles mission system, objectives, and completion tracking
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
WARNING_COLOR = (255, 100, 100)
CAUTION_COLOR = (255, 200, 100)
MISSION_HEADER_COLOR = (60, 20, 20)  # Red for missions scene

class MissionsScene:
    def __init__(self, simulator):
        self.simulator = simulator
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focused_widget = 0
        
        self._init_widgets()
    
    def set_font(self, font, is_text_antialiased=False):
        """Set the font for this scene"""
        self.font = font
        self.is_text_antialiased = is_text_antialiased
    
    def _init_widgets(self):
        """Initialize missions widgets"""
        self.widgets = [
            # Navigation buttons
            {"id": "prev_scene", "type": "button", "position": [8, 290], "size": [60, 24], "text": "< [", "focused": True},
            {"id": "next_scene", "type": "button", "position": [252, 290], "size": [60, 24], "text": "] >", "focused": False},
            
            # Current mission
            {"id": "mission_title", "type": "label", "position": [8, 40], "size": [250, 16], "text": "Photo Survey - Mountain Region", "focused": False},
            {"id": "mission_status", "type": "label", "position": [8, 60], "size": [150, 16], "text": "Status: IN PROGRESS", "focused": False},
            {"id": "progress", "type": "label", "position": [8, 80], "size": [150, 16], "text": "Progress: 60%", "focused": False},
            
            # Objectives
            {"id": "obj_1", "type": "label", "position": [8, 110], "size": [200, 16], "text": "✓ Reach Hudson Valley", "focused": False},
            {"id": "obj_2", "type": "label", "position": [8, 130], "size": [200, 16], "text": "→ Photo Survey Points", "focused": False},
            {"id": "obj_3", "type": "label", "position": [8, 150], "size": [200, 16], "text": "○ Return to Base", "focused": False},
            
            # Mission controls
            {"id": "view_briefing", "type": "button", "position": [8, 180], "size": [80, 16], "text": "Briefing", "focused": False},
            {"id": "waypoints", "type": "button", "position": [100, 180], "size": [80, 16], "text": "Waypoints", "focused": False},
            {"id": "abort_mission", "type": "button", "position": [190, 180], "size": [80, 16], "text": "Abort", "focused": False},
            
            # Rewards/Payment
            {"id": "payment", "type": "label", "position": [8, 210], "size": [150, 16], "text": "Payment: $2,500", "focused": False},
            {"id": "bonus", "type": "label", "position": [8, 230], "size": [150, 16], "text": "Time Bonus: $500", "focused": False},
            
            # Next mission preview
            {"id": "next_mission", "type": "label", "position": [8, 260], "size": [200, 16], "text": "Next: Cargo Delivery", "focused": False},
        ]
        
        # Set initial focus
        if self.widgets:
            self.widgets[self.focused_widget]["focused"] = True
    
    def update(self, dt: float):
        """Update missions display with current simulator data"""
        if not self.simulator:
            return
            
        state = self.simulator.get_state()
        game_info = state.get("gameInfo", {})
        missions = state.get("missions", {})
        
        # Update current mission
        current_mission = game_info.get("currentMission", "none")
        if current_mission == "photo_survey_mountains":
            self.widgets[2]["text"] = "Photo Survey - Mountain Region"
            self.widgets[3]["text"] = "Status: IN PROGRESS"
            self.widgets[4]["text"] = "Progress: 60%"
            
            # Update objectives
            self.widgets[5]["text"] = "✓ Reach Hudson Valley"
            self.widgets[6]["text"] = "→ Photo Survey Points"
            self.widgets[7]["text"] = "○ Return to Base"
        else:
            self.widgets[2]["text"] = "No Active Mission"
            self.widgets[3]["text"] = "Status: AVAILABLE"
            self.widgets[4]["text"] = "Progress: 0%"
    
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
        return "scene_crew"
    
    def _get_next_scene(self) -> str:
        """Get the next scene in circular order - back to bridge"""
        return "scene_bridge"
    
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
        elif widget_id == "view_briefing":
            # TODO: Show mission briefing
            pass
        elif widget_id == "waypoints":
            # Jump to navigation scene to show waypoints
            return "scene_navigation"
        elif widget_id == "abort_mission":
            # TODO: Abort current mission
            pass
            
        return None
    
    def render(self, surface):
        """Render the missions scene"""
        # Clear background
        surface.fill(BACKGROUND_COLOR)
        
        if not self.font:
            return
        
        # Draw colored title header
        pygame.draw.rect(surface, MISSION_HEADER_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(surface, TEXT_COLOR, (0, 0, 320, 24), 1)
        
        # Centered title
        title = self.font.render("MISSION CONTROL", self.is_text_antialiased, TEXT_COLOR)
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
        
        # Color coding for objectives
        if widget["id"].startswith("obj_"):
            if text.startswith("✓"):
                text_color = GOOD_COLOR
            elif text.startswith("→"):
                text_color = CAUTION_COLOR
            elif text.startswith("○"):
                text_color = TEXT_COLOR
            else:
                text_color = FOCUS_COLOR if focused else TEXT_COLOR
        else:
            text_color = FOCUS_COLOR if focused else TEXT_COLOR
        
        if widget_type == "button":
            # Draw button background
            color = BUTTON_FOCUSED_COLOR if focused else BUTTON_COLOR
            pygame.draw.rect(surface, color, (x, y, w, h))
            pygame.draw.rect(surface, TEXT_COLOR, (x, y, w, h), 1)
            
            # Draw button text
            text_color = FOCUS_COLOR if focused else TEXT_COLOR
            text_surface = self.font.render(text, self.is_text_antialiased, text_color)
            text_x = x + (w - text_surface.get_width()) // 2
            text_y = y + (h - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
            
        elif widget_type == "label":
            # Draw label text
            text_surface = self.font.render(text, self.is_text_antialiased, text_color)
            surface.blit(text_surface, (x, y))
