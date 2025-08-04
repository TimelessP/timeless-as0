"""
Main Menu Scene for Airship Zero
Brutally simple 320x320 UI system
"""
import pygame
import sys
from typing import List, Dict, Any, Optional

# Constants
LOGICAL_SIZE = 320
BACKGROUND_COLOR = (20, 20, 30)  # Dark blue-grey
TEXT_COLOR = (255, 255, 255)
FOCUS_COLOR = (255, 200, 50)  # Golden highlight
BUTTON_COLOR = (60, 60, 80)
BUTTON_FOCUSED_COLOR = (80, 80, 120)

class MainMenuScene:
    def __init__(self):
        self.font = None
        self.widgets = []
        self.focus_index = 0
        self.game_exists = False  # Set to True when there's a saved/running game
        
        # Initialize widgets
        self._init_widgets()
        
    def _init_widgets(self):
        """Initialize the main menu widgets"""
        self.widgets = [
            {
                "id": "new_game",
                "type": "button",
                "position": [80, 120],
                "size": [160, 24],
                "text": "New Game",
                "focused": True
            },
            {
                "id": "resume_game",
                "type": "button", 
                "position": [80, 150],
                "size": [160, 24],
                "text": "Resume Game",
                "focused": False,
                "enabled": self.game_exists
            },
            {
                "id": "settings",
                "type": "button",
                "position": [80, 180],
                "size": [160, 24],
                "text": "Settings",
                "focused": False
            },
            {
                "id": "quit",
                "type": "button",
                "position": [80, 210],
                "size": [160, 24],
                "text": "Quit",
                "focused": False
            }
        ]
        
    def set_font(self, font):
        """Set the font for rendering text"""
        self.font = font
        
    def set_game_exists(self, exists: bool):
        """Enable/disable the Resume Game button"""
        self.game_exists = exists
        for widget in self.widgets:
            if widget["id"] == "resume_game":
                widget["enabled"] = exists
                
    def handle_event(self, event) -> Optional[str]:
        """
        Handle pygame events
        Returns: scene transition command or None
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self._focus_previous()
                else:
                    self._focus_next()
            elif event.key == pygame.K_UP:
                self._focus_previous()
            elif event.key == pygame.K_DOWN:
                self._focus_next()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return self._activate_focused()
            elif event.key == pygame.K_ESCAPE:
                return "quit"
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Convert screen coordinates to logical coordinates
                logical_pos = self._screen_to_logical(event.pos)
                if logical_pos:
                    clicked_widget = self._get_widget_at_pos(logical_pos)
                    if clicked_widget:
                        self._set_focus(clicked_widget)
                        return self._activate_focused()
                        
        return None
        
    def _screen_to_logical(self, screen_pos) -> Optional[tuple]:
        """Convert screen coordinates to logical 320x320 coordinates"""
        # This will need to be implemented based on the actual scaling
        # For now, assume direct mapping
        return screen_pos
        
    def _get_widget_at_pos(self, pos) -> Optional[int]:
        """Get widget index at logical position"""
        x, y = pos
        for i, widget in enumerate(self.widgets):
            wx, wy = widget["position"]
            ww, wh = widget["size"]
            if wx <= x <= wx + ww and wy <= y <= wy + wh:
                if widget.get("enabled", True):
                    return i
        return None
        
    def _set_focus(self, widget_index: Optional[int]):
        """Set focus to specific widget"""
        if widget_index is not None:
            # Clear old focus
            for widget in self.widgets:
                widget["focused"] = False
            # Set new focus
            if 0 <= widget_index < len(self.widgets):
                self.widgets[widget_index]["focused"] = True
                self.focus_index = widget_index
                
    def _focus_next(self):
        """Move focus to next enabled widget"""
        current = self.focus_index
        for i in range(len(self.widgets)):
            next_index = (current + 1 + i) % len(self.widgets)
            if self.widgets[next_index].get("enabled", True):
                self._set_focus(next_index)
                break
                
    def _focus_previous(self):
        """Move focus to previous enabled widget"""
        current = self.focus_index
        for i in range(len(self.widgets)):
            prev_index = (current - 1 - i) % len(self.widgets)
            if self.widgets[prev_index].get("enabled", True):
                self._set_focus(prev_index)
                break
                
    def _activate_focused(self) -> Optional[str]:
        """Activate the currently focused widget"""
        if 0 <= self.focus_index < len(self.widgets):
            widget = self.widgets[self.focus_index]
            if not widget.get("enabled", True):
                return None
                
            widget_id = widget["id"]
            if widget_id == "new_game":
                return "scene_bridge"  # Start new game on bridge
            elif widget_id == "resume_game":
                return "scene_bridge"  # Resume game on bridge
            elif widget_id == "settings":
                return "scene_settings"  # Go to settings
            elif widget_id == "quit":
                return "quit"
                
        return None
        
    def render(self, surface):
        """Render the main menu to the logical surface"""
        # Clear background
        surface.fill(BACKGROUND_COLOR)
        
        # Draw title
        if self.font:
            title_text = self.font.render("AIRSHIP ZERO", False, TEXT_COLOR)
            title_rect = title_text.get_rect()
            title_x = (LOGICAL_SIZE - title_rect.width) // 2
            surface.blit(title_text, (title_x, 60))
            
            subtitle_text = self.font.render("Steam & Copper Dreams", False, (180, 180, 180))
            subtitle_rect = subtitle_text.get_rect()
            subtitle_x = (LOGICAL_SIZE - subtitle_rect.width) // 2
            surface.blit(subtitle_text, (subtitle_x, 80))
        
        # Draw widgets
        for widget in self.widgets:
            self._render_widget(surface, widget)
            
    def _render_widget(self, surface, widget):
        """Render a single widget"""
        if widget["type"] == "button":
            self._render_button(surface, widget)
            
    def _render_button(self, surface, widget):
        """Render a button widget"""
        x, y = widget["position"]
        w, h = widget["size"]
        enabled = widget.get("enabled", True)
        focused = widget.get("focused", False)
        
        # Choose colors
        if not enabled:
            bg_color = (40, 40, 50)
            text_color = (100, 100, 100)
        elif focused:
            bg_color = BUTTON_FOCUSED_COLOR
            text_color = FOCUS_COLOR
        else:
            bg_color = BUTTON_COLOR
            text_color = TEXT_COLOR
            
        # Draw button background
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        
        # Draw button border
        border_color = FOCUS_COLOR if focused else (100, 100, 100)
        pygame.draw.rect(surface, border_color, (x, y, w, h), 1)
        
        # Draw button text
        if self.font and enabled:
            text_surface = self.font.render(widget["text"], False, text_color)
            text_rect = text_surface.get_rect()
            text_x = x + (w - text_rect.width) // 2
            text_y = y + (h - text_rect.height) // 2
            surface.blit(text_surface, (text_x, text_y))
