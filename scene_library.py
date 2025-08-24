"""
Library Scene - Manage and read collected books
"""
import pygame
import os
import shutil
import sys
from typing import Optional, List, Dict, Any
from theme import (
    BACKGROUND_COLOR,
    TEXT_COLOR,
    FOCUS_COLOR,
    LIBRARY_HEADER_COLOR,
    BOOK_LIST_COLOR,
    SELECTED_BOOK_COLOR,
    BOOK_LIST_FOCUSED_COLOR,
    BUTTON_COLOR,
    BUTTON_FOCUSED_COLOR,
    BUTTON_DISABLED_COLOR,
    BUTTON_TEXT_DISABLED_COLOR,
    BUTTON_TEXT_COLOR,
    BUTTON_TEXT_FOCUSED_COLOR,
    BUTTON_BORDER_COLOR,
    BUTTON_BORDER_FOCUSED_COLOR,
    BUTTON_BORDER_DISABLED_COLOR,
    DISABLED_TEXT_COLOR,
    BOOK_LIST_EDIT_TEXT_COLOR,
    BOOK_LIST_EDIT_TEXT_COLOR_SELECTED,
    BOOK_LIST_EDIT_BG_COLOR_SELECTED
)

class LibraryScene:
    def __init__(self, simulator):
        self.simulator = simulator
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focus_index = 0
        self.books = []  # List of dicts: {"filename": str, "origin": "game"|"user"}
        self.selected_book_index = 0
        self.scroll_offset = 0
        self.max_visible_books = 8  # Number of books visible in the list
        self._last_book_count = 0  # Track changes to auto-refresh
        
        self._init_widgets()
        self._refresh_book_list()

    def set_font(self, font, is_text_antialiased=False):
        self.font = font
        self.is_text_antialiased = is_text_antialiased

    def _init_widgets(self):
        """Initialize widgets"""
        self.widgets = [
            # Navigation buttons
            {"id": "prev_scene", "type": "button", "position": [8, 290], "size": [60, 24], "text": "< [", "focused": True},
            {"id": "next_scene", "type": "button", "position": [252, 290], "size": [60, 24], "text": "] >", "focused": False},
            # Book management buttons (order: Read, Edit, Move)
            {"id": "read_book", "type": "button", "position": [20, 250], "size": [80, 24], "text": "Read Book", "focused": False},
            {"id": "edit_book", "type": "button", "position": [110, 250], "size": [80, 24], "text": "Edit", "focused": False},
            {"id": "move_to_cargo", "type": "button", "position": [210, 250], "size": [90, 24], "text": "Move to Cargo", "focused": False},
        ]

    def _get_user_books_dir(self):
        """Return the path to the user's custom books directory, cross-platform."""
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

    def _refresh_book_list(self):
        """Refresh the list of books from the simulator and user's custom books dir."""
        # Get in-game books from simulator
        game_books = self.simulator.get_library_books()
        books = []
        for filename in game_books:
            books.append({"filename": filename, "origin": "game"})

        # Get user custom books from Documents/AirshipZero/books/
        user_books_dir = self._get_user_books_dir()
        if user_books_dir and os.path.isdir(user_books_dir):
            for fname in sorted(os.listdir(user_books_dir)):
                if fname.endswith(".md") and os.path.isfile(os.path.join(user_books_dir, fname)):
                    # Only add if not already present as a user book (allow duplicate names from game)
                    books.append({"filename": fname, "origin": "user"})
        self.books = books
        self._last_book_count = len(self.books)
        # Ensure selected index is valid
        if self.selected_book_index >= len(self.books):
            self.selected_book_index = max(0, len(self.books) - 1)
        # Adjust scroll if needed
        self._adjust_scroll()

    def _adjust_scroll(self):
        """Adjust scroll offset to keep selected book visible"""
        if not self.books:
            self.scroll_offset = 0
            return
        
        # If selected book is above visible area, scroll up
        if self.selected_book_index < self.scroll_offset:
            self.scroll_offset = self.selected_book_index
        
        # If selected book is below visible area, scroll down
        elif self.selected_book_index >= self.scroll_offset + self.max_visible_books:
            self.scroll_offset = self.selected_book_index - self.max_visible_books + 1
        
        # Ensure scroll offset is valid
        self.scroll_offset = max(0, min(self.scroll_offset, max(0, len(self.books) - self.max_visible_books)))

    def _get_book_display_name(self, filename: str) -> str:
        """Get a display-friendly name for a book filename"""
        name = filename.replace('.md', '').replace('-', ' ').replace('_', ' ')
        return ' '.join(word.capitalize() for word in name.split())

    def handle_event(self, event) -> Optional[str]:
        if not pygame:
            return None
            
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            
            # Scene navigation & exit
            if event.key == pygame.K_ESCAPE:
                return "scene_main_menu"
            elif event.key == pygame.K_LEFTBRACKET:  # '[' previous scene
                return self._get_prev_scene()
            elif event.key == pygame.K_RIGHTBRACKET:  # ']' next scene
                return self._get_next_scene()

            # Focus cycling
            if event.key == pygame.K_TAB:
                if mods & pygame.KMOD_SHIFT:
                    self._focus_prev()
                else:
                    self._focus_next()
                return None

            # Book list navigation (when not focused on buttons)
            if self.focus_index >= len(self.widgets):  # In book list area
                if event.key == pygame.K_UP:
                    self._select_prev_book()
                elif event.key == pygame.K_DOWN:
                    self._select_next_book()
                elif event.key == pygame.K_PAGEUP:
                    self._select_prev_book(5)
                elif event.key == pygame.K_PAGEDOWN:
                    self._select_next_book(5)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_r:
                    return self._read_selected_book()
                elif event.key == pygame.K_e:
                    return self._edit_selected_book()
                elif event.key == pygame.K_m:
                    # Only allow if move to cargo is available
                    if self._is_move_to_cargo_available():
                        self._move_book_to_cargo()
                # Note: Space key removed - no longer moves books
                elif event.key == pygame.K_TAB:
                    self.focus_index = 0
                    self._update_focus()
            else:
                # Button navigation
                if event.key == pygame.K_UP:
                    self._focus_prev()
                elif event.key == pygame.K_DOWN:
                    self._focus_next()
                elif event.key == pygame.K_RETURN:
                    return self._activate_focused()

        elif event.type == pygame.MOUSEWHEEL:
            # Mousewheel scrolling for book list
            if self.books:
                if event.y > 0:  # Scroll up
                    self._select_prev_book()
                elif event.y < 0:  # Scroll down
                    self._select_next_book()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check button clicks
            for i, widget in enumerate(self.widgets):
                x, y = widget["position"]
                w, h = widget["size"]
                if x <= event.pos[0] <= x + w and y <= event.pos[1] <= y + h:
                    self.focus_index = i
                    self._update_focus()
                    return self._activate_focused()
            
            # Check book list clicks (adjusted for header)
            list_area_y = 50
            list_area_height = 190
            if 20 <= event.pos[0] <= 300 and list_area_y <= event.pos[1] <= list_area_y + list_area_height:
                # Click in book list area
                relative_y = event.pos[1] - list_area_y
                book_index = self.scroll_offset + relative_y // 20
                if 0 <= book_index < len(self.books):
                    self.selected_book_index = book_index
                    self.focus_index = len(self.widgets)  # Focus on book list
                    self._update_focus()

        return None

    def _focus_next(self):
        # Cycle through buttons first, then book list (if books exist)
        if self.focus_index < len(self.widgets) - 1:
            # Move to next button
            self.focus_index += 1
        elif self.focus_index == len(self.widgets) - 1:
            # On last button, move to book list if books exist, otherwise wrap to first button
            if self.books:
                self.focus_index = len(self.widgets)  # Move to book list
            else:
                self.focus_index = 0  # No books, wrap to first button
        else:
            # In book list, wrap back to first button
            self.focus_index = 0
        self._update_focus()

    def _focus_prev(self):
        # Reverse of _focus_next logic
        if self.focus_index == 0:
            # Move to book list if there are books, otherwise to last button
            if self.books:
                self.focus_index = len(self.widgets)
            else:
                self.focus_index = len(self.widgets) - 1
        elif self.focus_index > len(self.widgets):  # In book list
            self.focus_index = len(self.widgets) - 1  # Last button
        else:  # In buttons
            self.focus_index -= 1
        self._update_focus()

    def _update_focus(self):
        """Update focus state of widgets"""
        for widget in self.widgets:
            widget["focused"] = False
        if 0 <= self.focus_index < len(self.widgets):
            self.widgets[self.focus_index]["focused"] = True

    def _select_next_book(self, count=1):
        if not self.books:
            return
        self.selected_book_index = min(len(self.books) - 1, self.selected_book_index + count)
        self._adjust_scroll()

    def _select_prev_book(self, count=1):
        if not self.books:
            return
        self.selected_book_index = max(0, self.selected_book_index - count)
        self._adjust_scroll()

    def _activate_focused(self) -> Optional[str]:
        if self.focus_index >= len(self.widgets):
            return self._read_selected_book()
        
        widget = self.widgets[self.focus_index]
        widget_id = widget["id"]
        
        # Check if button is enabled before activating
        if widget_id == "move_to_cargo" and not self._is_move_to_cargo_available():
            return None
        elif widget_id == "read_book" and not self.books:
            return None
        elif widget_id == "edit_book" and not self.books:
            return None
        
        if widget_id == "prev_scene":
            return self._get_prev_scene()
        elif widget_id == "next_scene":
            return self._get_next_scene()
        elif widget_id == "read_book":
            return self._read_selected_book()
        elif widget_id == "edit_book":
            return self._edit_selected_book()
        elif widget_id == "move_to_cargo":
            self._move_book_to_cargo()
        return None

    def _edit_selected_book(self) -> Optional[dict]:
        # Edit handler: if game book, copy to user dir and select new user book; if user book, just open for edit
        if not self.books or self.selected_book_index >= len(self.books):
            return None
        book = self.books[self.selected_book_index]
        if book["origin"] == "user":
            # Already a user book, just open for edit
            return {"scene": "scene_edit", "book": dict(book)}
        # If game book, copy to user dir
        user_books_dir = self._get_user_books_dir()
        if not user_books_dir:
            return None
        try:
            os.makedirs(user_books_dir, exist_ok=True)
        except Exception:
            return None
        # Copy the book asset to user dir if not already present
        src_path = os.path.join(os.path.dirname(__file__), "assets", "books", book["filename"])
        dst_path = os.path.join(user_books_dir, book["filename"])
        # If file already exists, don't overwrite
        if not os.path.exists(dst_path):
            try:
                shutil.copyfile(src_path, dst_path)
            except Exception:
                return None
        # Refresh book list and select the new user book
        self._refresh_book_list()
        # Find the new user book index
        for idx, b in enumerate(self.books):
            if b["filename"] == book["filename"] and b["origin"] == "user":
                self.selected_book_index = idx
                break
        return {"scene": "scene_edit", "book": {"filename": book["filename"], "origin": "user"}}

    def _read_selected_book(self) -> Optional[dict]:
        if not self.books or self.selected_book_index >= len(self.books):
            return None
        book = self.books[self.selected_book_index]
        # Pass as dict for main.py to handle
        return {"scene": "scene_book", "book": dict(book)}

    def _move_book_to_cargo(self):
        if not self.books or self.selected_book_index >= len(self.books):
            return
        # Only allow moving in-game books (not user books)
        book = self.books[self.selected_book_index]
        if book["origin"] != "game":
            return
        # Check if winch is busy before attempting to move
        cargo_state = self.simulator.get_cargo_state()
        winch = cargo_state.get("winch", {})
        if winch.get("attachedCrate"):
            # Winch is busy - cannot move book
            return False
        if self.simulator.remove_book_from_library(book["filename"]):
            self._refresh_book_list()
            return True
        return False

    def _is_move_to_cargo_available(self) -> bool:
        """Check if move to cargo is available (winch is free, books exist, and selected book is not a user book)"""
        if not self.books:
            return False
        # Only allow for in-game books
        book = self.books[self.selected_book_index]
        if book["origin"] != "game":
            return False
        # Check if winch is busy
        cargo_state = self.simulator.get_cargo_state()
        winch = cargo_state.get("winch", {})
        return not winch.get("attachedCrate")

    def _get_prev_scene(self) -> str:
        return "scene_cargo"

    def _get_next_scene(self) -> str:
        return "scene_bridge"

    def update(self, dt: float):
        """Update the scene"""
        self.simulator.update(dt)
        
        # Check if library has changed (books added from other scenes)
        current_book_count = len(self.simulator.get_library_books())
        if current_book_count != self._last_book_count:
            self._refresh_book_list()

    def render(self, screen):
        if not pygame or not self.font:
            return

        # Clear screen
        screen.fill(BACKGROUND_COLOR)

        # Header background box (like other scenes)
        pygame.draw.rect(screen, LIBRARY_HEADER_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(screen, TEXT_COLOR, (0, 0, 320, 24), 1)

        # Header text
        header_text = "SHIP'S LIBRARY"
        header_surface = self.font.render(header_text, self.is_text_antialiased, TEXT_COLOR)
        header_rect = header_surface.get_rect(center=(160, 12))
        screen.blit(header_surface, header_rect)

        # Book count
        count_text = f"Books: {len(self.books)}"
        count_surface = self.font.render(count_text, self.is_text_antialiased, TEXT_COLOR)
        screen.blit(count_surface, (20, 30))

        # Book list area (adjusted for header)
        list_area = pygame.Rect(20, 50, 280, 190)
        pygame.draw.rect(screen, BOOK_LIST_COLOR, list_area)
        
        # Show focus indicator when book list is focused
        if self.focus_index >= len(self.widgets):
            # Draw focused border in focus color
            pygame.draw.rect(screen, FOCUS_COLOR, list_area, 2)
        else:
            # Normal border
            pygame.draw.rect(screen, TEXT_COLOR, list_area, 1)

        # Render visible books
        if self.books:
            for i in range(self.max_visible_books):
                book_index = self.scroll_offset + i
                if book_index >= len(self.books):
                    break
                y = 50 + i * 20  # Adjusted for header
                book = self.books[book_index]
                book_name = self._get_book_display_name(book["filename"])
                # Highlight selected book with better colors
                if book_index == self.selected_book_index:
                    highlight_rect = pygame.Rect(22, y + 2, 276, 16)
                    # User book: use custom color, else normal
                    if book["origin"] == "user":
                        color = BOOK_LIST_EDIT_BG_COLOR_SELECTED
                    elif self.focus_index >= len(self.widgets):
                        color = BOOK_LIST_FOCUSED_COLOR
                    else:
                        color = SELECTED_BOOK_COLOR
                    pygame.draw.rect(screen, color, highlight_rect)
                # Render book name (truncate if too long)
                if len(book_name) > 35:
                    book_name = book_name[:32] + "..."
                # User book: use custom text color
                if book["origin"] == "user":
                    if book_index == self.selected_book_index:
                        text_color = BOOK_LIST_EDIT_TEXT_COLOR_SELECTED
                    else:
                        text_color = BOOK_LIST_EDIT_TEXT_COLOR
                else:
                    text_color = TEXT_COLOR
                text_surface = self.font.render(book_name, self.is_text_antialiased, text_color)
                screen.blit(text_surface, (25, y + 3))
        else:
            # No books message (adjusted for header)
            no_books_text = "No books in library."
            no_books_surface = self.font.render(no_books_text, self.is_text_antialiased, TEXT_COLOR)
            text_rect = no_books_surface.get_rect(center=(160, 140))
            screen.blit(no_books_surface, text_rect)
            
            help_text = "Use book crates in cargo to add books."
            help_surface = self.font.render(help_text, self.is_text_antialiased, TEXT_COLOR)
            help_rect = help_surface.get_rect(center=(160, 160))
            screen.blit(help_surface, help_rect)

        # Scroll indicators (adjusted for header)
        if self.books and len(self.books) > self.max_visible_books:
            # Up arrow
            if self.scroll_offset > 0:
                pygame.draw.polygon(screen, TEXT_COLOR, [(310, 60), (315, 50), (320, 60)])
            
            # Down arrow
            if self.scroll_offset + self.max_visible_books < len(self.books):
                pygame.draw.polygon(screen, TEXT_COLOR, [(310, 220), (315, 230), (320, 220)])

        # Render buttons
        for widget in self.widgets:
            self._render_button(screen, widget)

    def _render_button(self, screen, widget):
        """Render a button widget"""
        x, y = widget["position"]
        w, h = widget["size"]

        # Check if button should be enabled
        enabled = True
        if widget["id"] == "move_to_cargo":
            enabled = self._is_move_to_cargo_available()
        elif widget["id"] == "read_book":
            enabled = bool(self.books)

        # Button background and border
        if enabled:
            color = BUTTON_FOCUSED_COLOR if widget.get("focused") else BUTTON_COLOR
            if widget.get("focused"):
                text_color = BUTTON_TEXT_FOCUSED_COLOR
                border_color = BUTTON_BORDER_FOCUSED_COLOR
            else:
                text_color = BUTTON_TEXT_COLOR
                border_color = BUTTON_BORDER_COLOR
        else:
            color = BUTTON_DISABLED_COLOR
            text_color = BUTTON_TEXT_DISABLED_COLOR
            border_color = BUTTON_BORDER_DISABLED_COLOR

        pygame.draw.rect(screen, color, (x, y, w, h))
        pygame.draw.rect(screen, border_color, (x, y, w, h), 1)

        # Button text
        text_surface = self.font.render(widget["text"], self.is_text_antialiased, text_color)
        text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
        screen.blit(text_surface, text_rect)
