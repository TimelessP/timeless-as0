"""
Cargo Management Scene - Placeholder
"""
import pygame
from typing import Optional

# Colors
BACKGROUND_COLOR = (20, 20, 30)
TEXT_COLOR = (255, 255, 255)
FOCUS_COLOR = (255, 200, 50)
CARGO_HEADER_COLOR = (120, 100, 60)  # Beige-brown for cargo scene

class CargoScene:
    def __init__(self, simulator):
        self.font = None
        self.is_text_antialiased = False
        self.simulator = simulator
        self.widgets = []
        self.focused_widget = 0

        self._init_widgets()

    def set_font(self, font, is_text_antialiased=False):
        """Set the font for this scene"""
        self.font = font
        self.is_text_antialiased = is_text_antialiased

    def _init_widgets(self):
        """Initialize navigation widgets"""
        self.widgets = [
            {"id": "prev_scene", "type": "button", "position": [8, 290], "size": [60, 24], "text": "< [", "focused": True},
            {"id": "next_scene", "type": "button", "position": [252, 290], "size": [60, 24], "text": "] >", "focused": False},
        ]

    def handle_event(self, event) -> Optional[str]:
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "scene_main_menu"
            elif event.key == pygame.K_LEFTBRACKET:  # [
                return "scene_fuel"
            elif event.key == pygame.K_RIGHTBRACKET:  # ]
                return "scene_communications"
            elif event.key == pygame.K_TAB:
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self._cycle_focus(-1)
                else:
                    self._cycle_focus(1)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return self._activate_focused()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                logical_pos = event.pos  # Already converted by main.py
                clicked_widget = self._get_widget_at_pos(logical_pos)
                if clicked_widget is not None:
                    self._set_focus(clicked_widget)
                    return self._activate_focused()

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
        text = widget["text"]

        # Button colors matching bridge scene
        bg_color = (80, 100, 120) if focused else (60, 80, 100)
        border_color = FOCUS_COLOR if focused else (120, 120, 120)
        text_color = FOCUS_COLOR if focused else TEXT_COLOR

        # Draw button background
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        pygame.draw.rect(surface, border_color, (x, y, w, h), 1)

        # Draw button text
        text_surface = self.font.render(text, self.is_text_antialiased, text_color)
        text_x = x + (w - text_surface.get_width()) // 2
        text_y = y + (h - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))

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
        if 0 <= self.focused_widget < len(self.widgets):
            widget = self.widgets[self.focused_widget]
            widget_id = widget["id"]
            
            if widget_id == "prev_scene":
                return "scene_fuel"
            elif widget_id == "next_scene":
                return "scene_communications"
                
        return None

    def update(self, dt: float):
        """Update the scene with game state"""
        # Placeholder for future cargo state updates
        pass
