"""
Book Editing Scene - Edit markdown books in user's Documents/AirshipZero/books/
"""

import pygame
import sys
import os
import pyperclip
from typing import Optional, List
from theme import (
    BACKGROUND_COLOR,
    EDIT_HEADER_COLOR,
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

from scene_book import TEXT_COLOR, PAPER_COLOR, PAGE_BORDER_COLOR

class EditBookScene:
    def __init__(self, simulator, book_filename: str):
        self.simulator = simulator
        self.book_filename = book_filename
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focus_index = 0
        self.scroll_offset = 0  # Line offset for source view
        self.cursor_pos = 0  # Offset in text buffer
        self.text_lines: List[str] = []
        self.text_buffer = ""
        self._init_widgets()
        self._load_book()
        self._update_lines_from_buffer()
        # Default focus to textarea
        self.focus_index = len(self.widgets)

    def set_font(self, font, is_text_antialiased=False):
        self.font = font
        self.is_text_antialiased = is_text_antialiased

    def _init_widgets(self):
        self.widgets = [
            {"id": "close", "type": "button", "position": [8, 290], "size": [60, 20], "text": "Close", "focused": True},
        ]

    def _load_book(self):
        # Only ever loads from user books dir
        user_books_dir = self._get_user_books_dir()
        book_path = os.path.join(user_books_dir, self.book_filename)
        if os.path.isfile(book_path):
            with open(book_path, "r", encoding="utf-8") as f:
                self.text_buffer = f.read()
        else:
            self.text_buffer = ""
        self.cursor_pos = len(self.text_buffer)

    def _save_book(self):
        user_books_dir = self._get_user_books_dir()
        book_path = os.path.join(user_books_dir, self.book_filename)
        with open(book_path, "w", encoding="utf-8") as f:
            f.write(self.text_buffer)

    def _get_user_books_dir(self):
        if sys.platform == "win32":
            home = os.environ.get("USERPROFILE")
            docs = os.path.join(home, "Documents") if home else None
        elif sys.platform == "darwin":
            home = os.environ.get("HOME")
            docs = os.path.join(home, "Documents") if home else None
        else:
            home = os.environ.get("HOME")
            docs = os.path.join(home, "Documents") if home else None
        if docs:
            return os.path.join(docs, "AirshipZero", "books")
        return None

    def _update_lines_from_buffer(self):
        self.text_lines = self.text_buffer.split("\n")

    def _update_buffer_from_lines(self):
        self.text_buffer = "\n".join(self.text_lines)


    def handle_event(self, event) -> Optional[str]:
        if not pygame:
            return None
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if event.key == pygame.K_ESCAPE:
                self._save_book()
                return "scene_library"
            elif event.key == pygame.K_TAB:
                if mods & pygame.KMOD_SHIFT:
                    self._focus_prev()
                else:
                    self._focus_next()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self._activate_focused()
            elif self.focus_index >= len(self.widgets):
                # Editing keys only when text area is focused
                return self._handle_text_edit_event(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, widget in enumerate(self.widgets):
                x, y = widget["position"]
                w, h = widget["size"]
                rect = pygame.Rect(x, y, w, h)
                if rect.collidepoint(event.pos):
                    self.focus_index = i
                    self._update_focus()
                    return self._activate_focused()
            # Click in text area to focus (source mode)
            text_area = pygame.Rect(20, 30, 280, 250)
            if text_area.collidepoint(event.pos):
                self.focus_index = len(self.widgets)  # Focus text area
                self._update_focus()
        elif event.type == pygame.MOUSEWHEEL:
            self._scroll_source(event.y)
        return None

    def _handle_text_edit_event(self, event):
        mods = pygame.key.get_mods()
        # Navigation
        if event.key == pygame.K_LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
        elif event.key == pygame.K_RIGHT:
            if self.cursor_pos < len(self.text_buffer):
                self.cursor_pos += 1
        elif event.key == pygame.K_UP:
            self._move_cursor_vertically(-1)
        elif event.key == pygame.K_DOWN:
            self._move_cursor_vertically(1)
        elif event.key == pygame.K_HOME:
            if mods & pygame.KMOD_CTRL:
                self.cursor_pos = 0
            else:
                self.cursor_pos = self._line_start(self.cursor_pos)
        elif event.key == pygame.K_END:
            if mods & pygame.KMOD_CTRL:
                self.cursor_pos = len(self.text_buffer)
            else:
                self.cursor_pos = self._line_end(self.cursor_pos)
        elif event.key == pygame.K_BACKSPACE:
            if self.cursor_pos > 0:
                self.text_buffer = self.text_buffer[:self.cursor_pos-1] + self.text_buffer[self.cursor_pos:]
                self.cursor_pos -= 1
                self._update_lines_from_buffer()
        elif event.key == pygame.K_DELETE:
            if self.cursor_pos < len(self.text_buffer):
                self.text_buffer = self.text_buffer[:self.cursor_pos] + self.text_buffer[self.cursor_pos+1:]
                self._update_lines_from_buffer()
        elif event.key == pygame.K_RETURN:
            self.text_buffer = self.text_buffer[:self.cursor_pos] + "\n" + self.text_buffer[self.cursor_pos:]
            self.cursor_pos += 1
            self._update_lines_from_buffer()
        elif event.key == pygame.K_v and mods & pygame.KMOD_CTRL:
            paste = pyperclip.paste()
            if paste:
                self.text_buffer = self.text_buffer[:self.cursor_pos] + paste + self.text_buffer[self.cursor_pos:]
                self.cursor_pos += len(paste)
                self._update_lines_from_buffer()
        elif event.unicode and len(event.unicode) == 1 and not (mods & pygame.KMOD_CTRL):
            self.text_buffer = self.text_buffer[:self.cursor_pos] + event.unicode + self.text_buffer[self.cursor_pos:]
            self.cursor_pos += 1
            self._update_lines_from_buffer()
    # No rendered mode, so no reflow needed
        return None

    def _move_cursor_vertically(self, direction):
        # Move cursor up/down by line
        line, col = self._get_cursor_line_col()
        new_line = max(0, min(len(self.text_lines)-1, line + direction))
        new_col = col
        new_line_len = len(self.text_lines[new_line])
        new_col = min(new_col, new_line_len)
        # Compute new cursor_pos
        pos = 0
        for l in range(new_line):
            pos += len(self.text_lines[l]) + 1  # +1 for \n
        self.cursor_pos = pos + new_col

    def _get_cursor_line_col(self):
        # Returns (line, col) for current cursor_pos
        pos = 0
        for i, line in enumerate(self.text_lines):
            if self.cursor_pos <= pos + len(line):
                return i, self.cursor_pos - pos
            pos += len(line) + 1  # +1 for \n
        return len(self.text_lines)-1, len(self.text_lines[-1]) if self.text_lines else (0, 0)

    def _line_start(self, pos):
        # Returns buffer index of start of line containing pos
        idx = 0
        for line in self.text_lines:
            if pos <= idx + len(line):
                return idx
            idx += len(line) + 1
        return 0

    def _line_end(self, pos):
        # Returns buffer index of end of line containing pos
        idx = 0
        for line in self.text_lines:
            if pos <= idx + len(line):
                return idx + len(line)
            idx += len(line) + 1
        return len(self.text_buffer)

    def _focus_next(self):
        # Cycle: buttons -> textarea -> first button
        if self.focus_index < len(self.widgets):
            self.focus_index += 1
        else:
            self.focus_index = 0
        self._update_focus()

    def _focus_prev(self):
        # Cycle: textarea -> last button -> ...
        if self.focus_index == 0:
            self.focus_index = len(self.widgets)
        else:
            self.focus_index -= 1
        self._update_focus()

    def _update_focus(self):
        for widget in self.widgets:
            widget["focused"] = False
        if 0 <= self.focus_index < len(self.widgets):
            self.widgets[self.focus_index]["focused"] = True
        # No visual for textarea focus, but logic is correct

    def _activate_focused(self) -> Optional[str]:
        if self.focus_index >= len(self.widgets):
            # Text area focused, do nothing
            return None
        widget = self.widgets[self.focus_index]
        if widget["id"] == "close":
            self._save_book()
            return "scene_library"
        return None

    def _scroll_source(self, y):
        # Mousewheel: y > 0 is up, < 0 is down
        lines_visible = 13  # About 250px / 18px per line
        if y > 0:
            self.scroll_offset = max(0, self.scroll_offset - 2)
        elif y < 0:
            self.scroll_offset = min(max(0, len(self.text_lines) - lines_visible), self.scroll_offset + 2)

    def update(self, dt: float):
        self.simulator.update(dt)

    def render(self, screen):
        if not pygame or not self.font:
            return
        # Clear screen
        screen.fill(BACKGROUND_COLOR)
        # Header background box (scene-specific color)
        pygame.draw.rect(screen, EDIT_HEADER_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(screen, BUTTON_TEXT_COLOR, (0, 0, 320, 24), 1)
        # Title in header box
        title = f"EDITING: {self.book_filename}"
        title_surface = self.font.render(title, self.is_text_antialiased, BUTTON_TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(160, 12))
        screen.blit(title_surface, title_rect)
        # Render buttons
        for widget in self.widgets:
            self._render_button(screen, widget)
        # Render text area
        text_area = pygame.Rect(20, 30, 280, 250)
        pygame.draw.rect(screen, PAPER_COLOR, text_area)
        pygame.draw.rect(screen, PAGE_BORDER_COLOR, text_area, 2)
        self._render_source_view(screen, text_area)

    def _render_source_view(self, screen, text_area):
        # Draw text lines with cursor and scrolling
        lines_visible = 13
        start = self.scroll_offset
        end = min(len(self.text_lines), start + lines_visible)
        y = text_area.y + 4
        cursor_line, cursor_col = self._get_cursor_line_col()
        for i in range(start, end):
            line = self.text_lines[i]
            text_surface = self.font.render(line, self.is_text_antialiased, TEXT_COLOR)
            screen.blit(text_surface, (text_area.x + 6, y))
            # Draw cursor if on this line and text area is focused
            if self.focus_index >= len(self.widgets) and i == cursor_line:
                cursor_x = text_area.x + 6 + self.font.size(line[:cursor_col])[0]
                pygame.draw.line(screen, (255, 200, 50), (cursor_x, y), (cursor_x, y + self.font.get_height()), 2)
            y += self.font.get_height() + 2
        # Draw scrollbar
        self._render_scrollbar(screen, text_area, lines_visible)

    def _render_scrollbar(self, screen, text_area, lines_visible):
        total_lines = max(1, len(self.text_lines))
        bar_height = max(20, int(text_area.height * min(1.0, lines_visible / total_lines)))
        max_scroll = max(0, total_lines - lines_visible)
        if max_scroll == 0:
            bar_y = text_area.y
        else:
            bar_y = text_area.y + int((self.scroll_offset / max_scroll) * (text_area.height - bar_height))
        bar_rect = pygame.Rect(text_area.right - 8, bar_y, 6, bar_height)
        pygame.draw.rect(screen, BUTTON_COLOR, bar_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, bar_rect, 1)

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
