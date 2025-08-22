"""
Main Menu Scene for Airship Zero
Brutally simple 320x320 UI system
"""

import pygame
import sys
from typing import List, Dict, Any, Optional
from theme import (
    LOGICAL_SIZE,
    BACKGROUND_COLOR,
    TEXT_COLOR,
    FOCUS_COLOR,
    BUTTON_COLOR,
    BUTTON_FOCUSED_COLOR,
    BUTTON_DISABLED_COLOR,
    BUTTON_TEXT_DISABLED_COLOR,
    BUTTON_TEXT_COLOR,
    BUTTON_TEXT_FOCUSED_COLOR,
    BUTTON_BORDER_COLOR,
    BUTTON_BORDER_FOCUSED_COLOR,
    BUTTON_BORDER_DISABLED_COLOR,
    SUBTITLE_COLOR,
    DISABLED_TEXT_COLOR,
    CAUTION_COLOR
)

class MainMenuScene:
    def __init__(self):
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focus_index = 0
        self.game_exists = False  # Set to True when there's a saved/running game
        self.update_available = False  # Set to True when update is available
        self.latest_version = None  # Store the latest available version
        
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
                "focused": not self.game_exists  # Focus on new game only if no saved game
            },
            {
                "id": "resume_game",
                "type": "button", 
                "position": [80, 150],
                "size": [160, 24],
                "text": "Resume Game",
                "focused": self.game_exists,  # Focus on resume if saved game exists
                "enabled": self.game_exists
            },
            {
                "id": "updates",
                "type": "button",
                "position": [80, 180],
                "size": [160, 24],
                "text": "Updates",
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
        
        # Set focus index based on which button is focused
        for i, widget in enumerate(self.widgets):
            if widget.get("focused", False):
                self.focus_index = i
                break
        
    def set_font(self, font, is_text_antialiased=False):
        """Set the font for rendering text"""
        self.font = font
        self.is_text_antialiased = is_text_antialiased
        
    def set_game_exists(self, exists: bool):
        """Enable/disable the Resume Game button and update focus"""
        self.game_exists = exists
        
        # Re-initialize widgets to update focus based on new game existence status
        self._init_widgets()
    
    def set_update_available(self, available: bool, latest_version: str = None):
        """Set whether an update is available"""
        self.update_available = available
        self.latest_version = latest_version
        
        # Update the Updates button text if there's an update
        for widget in self.widgets:
            if widget["id"] == "updates":
                if available and latest_version:
                    widget["text"] = f"Updates (v{latest_version})"
                else:
                    widget["text"] = "Updates"
                break
                
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
                    if clicked_widget is not None:
                        self._set_focus(clicked_widget)
                        return self._activate_focused()
                        
        return None
        
    def _screen_to_logical(self, screen_pos) -> Optional[tuple]:
        """Convert screen coordinates to logical 320x320 coordinates"""
        # Coordinates are already converted by main.py
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
                return "new_game"  # Start new game
            elif widget_id == "resume_game":
                return "resume_game"  # Resume saved game
            elif widget_id == "updates":
                return "scene_update"  # Go to updates
            elif widget_id == "quit":
                return "quit"
                
        return None
        
    def render(self, surface):
        """Render the main menu to the logical surface"""
        # Clear background
        surface.fill(BACKGROUND_COLOR)

        # Draw title and subtitle
        if self.font:
            title_text = self.font.render("AIRSHIP ZERO", self.is_text_antialiased, TEXT_COLOR)
            title_x = (LOGICAL_SIZE - title_text.get_width()) // 2
            surface.blit(title_text, (title_x, 80))

            subtitle_text = self.font.render("Steam & Copper Dreams", self.is_text_antialiased, SUBTITLE_COLOR)  # Subtitle is intentionally silver-grey
            subtitle_x = (LOGICAL_SIZE - subtitle_text.get_width()) // 2
            surface.blit(subtitle_text, (subtitle_x, 100))

            # Draw update notification if available
            if self.update_available and self.latest_version:
                update_text = f"Update v{self.latest_version} available!"
                update_surface = self.font.render(update_text, self.is_text_antialiased, CAUTION_COLOR)
                update_x = (LOGICAL_SIZE - update_surface.get_width()) // 2
                surface.blit(update_surface, (update_x, 260))

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

        # Choose theme colors
        if not enabled:
            bg_color = BUTTON_DISABLED_COLOR
            text_color = BUTTON_TEXT_DISABLED_COLOR
            border_color = BUTTON_BORDER_DISABLED_COLOR
        elif focused:
            bg_color = BUTTON_FOCUSED_COLOR
            text_color = BUTTON_TEXT_FOCUSED_COLOR
            border_color = BUTTON_BORDER_FOCUSED_COLOR
        else:
            bg_color = BUTTON_COLOR
            text_color = BUTTON_TEXT_COLOR
            border_color = BUTTON_BORDER_COLOR

        # Draw button background
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        pygame.draw.rect(surface, border_color, (x, y, w, h), 1)

        # Draw button text
        if self.font:
            text_surface = self.font.render(widget["text"], self.is_text_antialiased, text_color)
            text_rect = text_surface.get_rect()
            text_x = x + (w - text_rect.width) // 2
            text_y = y + (h - text_rect.height) // 2
            surface.blit(text_surface, (text_x, text_y))
