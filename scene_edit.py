"""
Book Editing Scene - Edit markdown books in user's Documents/AirshipZero/books/
"""
import pygame
from typing import Optional
from theme import (
    BACKGROUND_COLOR,
    BUTTON_COLOR,
    BUTTON_FOCUSED_COLOR,
    BUTTON_DISABLED_COLOR,
    BUTTON_TEXT_COLOR,
    BUTTON_TEXT_FOCUSED_COLOR,
    BUTTON_TEXT_DISABLED_COLOR,
    BUTTON_BORDER_COLOR,
    BUTTON_BORDER_FOCUSED_COLOR,
    BUTTON_BORDER_DISABLED_COLOR
)

class EditBookScene:
    def __init__(self, simulator, book_filename: str):
        self.simulator = simulator
        self.book_filename = book_filename
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focus_index = 0
        self._init_widgets()

    def set_font(self, font, is_text_antialiased=False):
        self.font = font
        self.is_text_antialiased = is_text_antialiased

    def _init_widgets(self):
        self.widgets = [
            {"id": "close", "type": "button", "position": [8, 290], "size": [60, 20], "text": "Close", "focused": True},
        ]

    def handle_event(self, event) -> Optional[str]:
        if not pygame:
            return None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "scene_library"
            elif event.key == pygame.K_TAB:
                self._focus_next()
            elif event.key == pygame.K_RETURN:
                return self._activate_focused()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, widget in enumerate(self.widgets):
                x, y = widget["position"]
                w, h = widget["size"]
                rect = pygame.Rect(x, y, w, h)
                if rect.collidepoint(event.pos):
                    self.focus_index = i
                    self._update_focus()
                    return self._activate_focused()
        return None

    def _focus_next(self):
        self.focus_index = (self.focus_index + 1) % len(self.widgets)
        self._update_focus()

    def _update_focus(self):
        for widget in self.widgets:
            widget["focused"] = False
        if 0 <= self.focus_index < len(self.widgets):
            self.widgets[self.focus_index]["focused"] = True

    def _activate_focused(self) -> Optional[str]:
        widget = self.widgets[self.focus_index]
        if widget["id"] == "close":
            return "scene_library"
        return None

    def update(self, dt: float):
        self.simulator.update(dt)

    def render(self, screen):
        if not pygame or not self.font:
            return
        # Clear screen
        screen.fill(BACKGROUND_COLOR)
        # Header background box
        pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(screen, BUTTON_TEXT_COLOR, (0, 0, 320, 24), 1)
        # Title in header box
        title = f"EDITING: {self.book_filename}"
        title_surface = self.font.render(title, self.is_text_antialiased, BUTTON_TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(160, 12))
        screen.blit(title_surface, title_rect)
        # Render buttons
        for widget in self.widgets:
            self._render_button(screen, widget)

    def _render_button(self, screen, widget):
        x, y = widget["position"]
        w, h = widget["size"]
        enabled = True
        color = BUTTON_FOCUSED_COLOR if widget.get("focused") else BUTTON_COLOR
        border_color = BUTTON_BORDER_FOCUSED_COLOR if widget.get("focused") else BUTTON_BORDER_COLOR
        text_color = BUTTON_TEXT_FOCUSED_COLOR if widget.get("focused") else BUTTON_TEXT_COLOR
        pygame.draw.rect(screen, color, (x, y, w, h))
        pygame.draw.rect(screen, border_color, (x, y, w, h), 1)
        text_surface = self.font.render(widget["text"], self.is_text_antialiased, text_color)
        text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
        screen.blit(text_surface, text_rect)
