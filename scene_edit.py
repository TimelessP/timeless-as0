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
    BUTTON_BORDER_DISABLED_COLOR,
    CURSOR_COLOR
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
        # Caching for wrapped/rendered lines (must be before any method that uses it)
        self._wrap_cache = {
            'text_buffer': None,
            'font': None,
            'wrap_width': None,
            'wrapped_lines': [],
            'line_map': [],
            'surfaces': []
        }
        self._init_widgets()
        self._load_book()
        self._update_lines_from_buffer()
        # Default focus to textarea and cursor at start
        self.focus_index = len(self.widgets)
        self._update_focus()
        self.cursor_pos = 0
        # Key repeat state
        self._repeat_key = None
        self._repeat_key_down = False
        self._repeat_time = 0
        self._repeat_interval = 0.05  # seconds between repeats
        self._repeat_delay = 0.35  # initial delay before repeat

    def set_font(self, font, is_text_antialiased=False):
        self.font = font
        self.is_text_antialiased = is_text_antialiased
        self._invalidate_wrap_cache()

    def _init_widgets(self):
        self.widgets = [
            {"id": "close", "type": "button", "position": [8, 290], "size": [60, 20], "text": "Close", "focused": False},
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
        self._invalidate_wrap_cache()
    def _invalidate_wrap_cache(self):
        self._wrap_cache['text_buffer'] = None
        self._wrap_cache['font'] = None
        self._wrap_cache['wrap_width'] = None
        self._wrap_cache['wrapped_lines'] = []
        self._wrap_cache['line_map'] = []
        self._wrap_cache['surfaces'] = []

    def _update_buffer_from_lines(self):
        self.text_buffer = "\n".join(self.text_lines)


    def handle_event(self, event) -> Optional[str]:
        if not pygame:
            return None
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            nav_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_HOME, pygame.K_END]
            # Start key repeat for navigation keys
            if event.key in nav_keys and self.focus_index >= len(self.widgets):
                self._repeat_key = event.key
                self._repeat_key_down = True
                self._repeat_time = 0
            if event.key == pygame.K_ESCAPE:
                self._save_book()
                return "scene_library"
            elif event.key == pygame.K_TAB:
                if mods & pygame.KMOD_SHIFT:
                    self._focus_prev()
                else:
                    self._focus_next()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.focus_index < len(self.widgets):
                    return self._activate_focused()
                else:
                    # Insert newline in textarea
                    self.text_buffer = self.text_buffer[:self.cursor_pos] + "\n" + self.text_buffer[self.cursor_pos:]
                    self.cursor_pos += 1
                    self._update_lines_from_buffer()
                    self._scroll_cursor_into_view()
            elif self.focus_index >= len(self.widgets):
                # Editing keys only when text area is focused
                result = self._handle_text_edit_event(event)
                self._scroll_cursor_into_view()
                return result
        elif event.type == pygame.KEYUP:
            # Stop key repeat
            if self._repeat_key == event.key:
                self._repeat_key_down = False
                self._repeat_key = None
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
                # Move cursor to click position
                self._move_cursor_to_mouse(event.pos, text_area)
        elif event.type == pygame.MOUSEWHEEL:
            self._scroll_source(event.y)
        return None

    def _move_cursor_to_mouse(self, mouse_pos, text_area):
        """Move the cursor to the position in the text buffer closest to the mouse click."""
        cache = self._wrap_cache
        wrapped_lines = cache['wrapped_lines']
        line_map = cache['line_map']
        font = self.font
        if not wrapped_lines or not line_map or not font:
            return
        x, y = mouse_pos
        # Calculate which wrapped line was clicked
        rel_y = y - (text_area.y + 4)
        line_height = font.get_height() + 2
        wrap_idx = rel_y // line_height
        if wrap_idx < 0:
            wrap_idx = 0
        if wrap_idx >= len(wrapped_lines):
            wrap_idx = len(wrapped_lines) - 1
        # Now, for that wrapped line, find the closest char
        line_text = wrapped_lines[wrap_idx]
        line_x0 = text_area.x + 6
        rel_x = x - line_x0
        # Find closest char index in line_text
        min_dist = float('inf')
        best_col = 0
        for col in range(len(line_text)+1):
            char_x = font.size(line_text[:col])[0]
            dist = abs(char_x - rel_x)
            if dist < min_dist:
                min_dist = dist
                best_col = col
        # Map back to buffer position
        orig_idx, start_col, end_col = line_map[wrap_idx]
        buffer_line = orig_idx
        buffer_col = start_col + best_col
        # Clamp to line length
        if buffer_col > len(self.text_lines[buffer_line]):
            buffer_col = len(self.text_lines[buffer_line])
        # Compute buffer position
        pos = 0
        for i in range(buffer_line):
            pos += len(self.text_lines[i]) + 1  # +1 for \n
        pos += buffer_col
        self.cursor_pos = pos

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
        elif event.key == pygame.K_PAGEUP:
            self._move_cursor_page(-1)
        elif event.key == pygame.K_PAGEDOWN:
            self._move_cursor_page(1)
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
        return None

    def _move_cursor_page(self, direction):
        # direction: -1 for PgUp, 1 for PgDn
        lines_visible = 13
        line, col = self._get_cursor_line_col()
        new_line = max(0, min(len(self.text_lines)-1, line + direction * lines_visible))
        new_col = min(col, len(self.text_lines[new_line]))
        pos = 0
        for l in range(new_line):
            pos += len(self.text_lines[l]) + 1
        self.cursor_pos = pos + new_col

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
        # Only one widget can be focused at a time, textarea never visually focused
        for i, widget in enumerate(self.widgets):
            widget["focused"] = (i == self.focus_index and self.focus_index < len(self.widgets))

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
        # Key repeat logic (one repeat per frame, no while loop)
        if self._repeat_key is not None and self._repeat_key_down and self.focus_index >= len(self.widgets):
            self._repeat_time += dt
            if self._repeat_time >= self._repeat_delay:
                fake_event = pygame.event.Event(pygame.KEYDOWN, key=self._repeat_key, unicode="", mod=pygame.key.get_mods())
                self._handle_text_edit_event(fake_event)
                self._scroll_cursor_into_view()
                self._repeat_time -= self._repeat_interval  # allow some drift, but only one repeat per frame

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
        # Soft wrap lines for rendering, with caching
        lines_visible = 13
        wrap_width = text_area.width - 16  # 6px left, 8px scrollbar, 2px border
        cache = self._wrap_cache
        cache_invalid = (
            cache['text_buffer'] != self.text_buffer or
            cache['font'] != self.font or
            cache['wrap_width'] != wrap_width or
            not cache['wrapped_lines']
        )
        if cache_invalid:
            wrapped_lines = []
            line_map = []
            surfaces = []
            for idx, line in enumerate(self.text_lines):
                start = 0
                line_len = len(line)
                while start < line_len:
                    # Find max substring that fits
                    end = line_len
                    if self.font.size(line[start:end])[0] <= wrap_width:
                        pass  # whole rest of line fits
                    else:
                        # Binary search for fit
                        lo = start + 1
                        hi = end
                        while lo < hi:
                            mid = (lo + hi) // 2
                            if self.font.size(line[start:mid])[0] <= wrap_width:
                                lo = mid + 1
                            else:
                                hi = mid
                        end = lo - 1 if lo > start + 1 else lo
                    if end <= start:
                        end = start + 1  # Always advance at least one char
                    substr = line[start:end]
                    wrapped_lines.append(substr)
                    line_map.append((idx, start, end))
                    surfaces.append(self.font.render(substr, self.is_text_antialiased, TEXT_COLOR))
                    start = end
                if line_len == 0:
                    wrapped_lines.append("")
                    line_map.append((idx, 0, 0))
                    surfaces.append(self.font.render("", self.is_text_antialiased, TEXT_COLOR))
            cache['text_buffer'] = self.text_buffer
            cache['font'] = self.font
            cache['wrap_width'] = wrap_width
            cache['wrapped_lines'] = wrapped_lines
            cache['line_map'] = line_map
            cache['surfaces'] = surfaces
        wrapped_lines = cache['wrapped_lines']
        line_map = cache['line_map']
        surfaces = cache['surfaces']
        # Find cursor's wrapped line/col
        cursor_line, cursor_col = self._get_cursor_line_col()
        cursor_wrap_idx = 0
        for i, (orig_idx, start, end) in enumerate(line_map):
            if orig_idx == cursor_line and start <= cursor_col <= end:
                cursor_wrap_idx = i
                break
        # Draw visible lines
        start_idx = self.scroll_offset
        end_idx = min(len(wrapped_lines), start_idx + lines_visible)
        y = text_area.y + 4
        for i in range(start_idx, end_idx):
            screen.blit(surfaces[i], (text_area.x + 6, y))
            # Draw cursor if on this wrapped line and text area is focused
            if self.focus_index >= len(self.widgets) and i == cursor_wrap_idx:
                cursor_x = text_area.x + 6 + self.font.size(wrapped_lines[i][:cursor_col - line_map[i][1]])[0]
                pygame.draw.line(screen, CURSOR_COLOR, (cursor_x, y), (cursor_x, y + self.font.get_height()), 2)
            y += self.font.get_height() + 2
        # Draw scrollbar
        self._render_scrollbar(screen, text_area, lines_visible, total_lines=len(wrapped_lines))

    def _scroll_cursor_into_view(self):
        # After moving cursor, scroll so it's visible
        # Use cached wrap/line_map
        cache = self._wrap_cache
        wrapped_lines = cache['wrapped_lines']
        line_map = cache['line_map']
        cursor_line, cursor_col = self._get_cursor_line_col()
        cursor_wrap_idx = 0
        for i, (orig_idx, start, end) in enumerate(line_map):
            if orig_idx == cursor_line and start <= cursor_col <= end:
                cursor_wrap_idx = i
                break
        lines_visible = 13
        if cursor_wrap_idx < self.scroll_offset:
            self.scroll_offset = cursor_wrap_idx
        elif cursor_wrap_idx >= self.scroll_offset + lines_visible:
            self.scroll_offset = cursor_wrap_idx - lines_visible + 1

    def _render_scrollbar(self, screen, text_area, lines_visible, total_lines=None):
        if total_lines is None:
            total_lines = max(1, len(self.text_lines))
        else:
            total_lines = max(1, total_lines)
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
