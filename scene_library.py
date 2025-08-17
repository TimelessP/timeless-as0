"""
Library Scene - Manage and read collected books
"""
import pygame
import os
from typing import Optional, List, Dict, Any

# Colors
BACKGROUND_COLOR = (20, 20, 30)
TEXT_COLOR = (230, 230, 240)
FOCUS_COLOR = (255, 200, 50)
HEADER_COLOR = (80, 60, 40)  # Brown for library theme
BOOK_LIST_COLOR = (40, 40, 50)
SELECTED_BOOK_COLOR = (120, 100, 60)
BUTTON_COLOR = (60, 60, 80)
BUTTON_FOCUSED = (90, 90, 130)

class LibraryScene:
    def __init__(self, simulator):
        self.simulator = simulator
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focus_index = 0
        self.books = []  # List of book filenames
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
            
            # Book management buttons
            {"id": "read_book", "type": "button", "position": [20, 250], "size": [80, 24], "text": "Read Book", "focused": False},
            {"id": "move_to_cargo", "type": "button", "position": [120, 250], "size": [100, 24], "text": "Move to Cargo", "focused": False},
        ]

    def _refresh_book_list(self):
        """Refresh the list of books from the simulator"""
        self.books = self.simulator.get_library_books()
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
        # Remove .md extension and convert underscores to spaces
        name = filename.replace('.md', '').replace('-', ' ').replace('_', ' ')
        # Capitalize words
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
                elif event.key == pygame.K_RETURN:
                    return self._read_selected_book()
                elif event.key == pygame.K_SPACE:
                    self._move_book_to_cargo()
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

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check button clicks
            for i, widget in enumerate(self.widgets):
                x, y = widget["position"]
                w, h = widget["size"]
                if x <= event.pos[0] <= x + w and y <= event.pos[1] <= y + h:
                    self.focus_index = i
                    self._update_focus()
                    return self._activate_focused()
            
            # Check book list clicks
            list_area_y = 60
            list_area_height = 180
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
        # If in book list, move to first button
        if self.focus_index >= len(self.widgets):
            self.focus_index = 0
        else:
            self.focus_index = (self.focus_index + 1) % len(self.widgets)
        self._update_focus()

    def _focus_prev(self):
        if self.focus_index == 0:
            # Move to book list if there are books
            self.focus_index = len(self.widgets) if self.books else len(self.widgets) - 1
        else:
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
        if widget["id"] == "prev_scene":
            return self._get_prev_scene()
        elif widget["id"] == "next_scene":
            return self._get_next_scene()
        elif widget["id"] == "read_book":
            return self._read_selected_book()
        elif widget["id"] == "move_to_cargo":
            self._move_book_to_cargo()
        return None

    def _read_selected_book(self) -> Optional[str]:
        if not self.books or self.selected_book_index >= len(self.books):
            return None
        selected_book = self.books[self.selected_book_index]
        return f"scene_book:{selected_book}"

    def _move_book_to_cargo(self):
        if not self.books or self.selected_book_index >= len(self.books):
            return
        selected_book = self.books[self.selected_book_index]
        if self.simulator.remove_book_from_library(selected_book):
            self._refresh_book_list()

    def _get_prev_scene(self) -> str:
        return "scene_cargo"
    
    def _get_next_scene(self) -> str:
        return "scene_communications"

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

        # Header
        header_text = "SHIP'S LIBRARY"
        header_surface = self.font.render(header_text, self.is_text_antialiased, TEXT_COLOR)
        header_rect = header_surface.get_rect(center=(160, 20))
        screen.blit(header_surface, header_rect)

        # Book count
        count_text = f"Books: {len(self.books)}"
        count_surface = self.font.render(count_text, self.is_text_antialiased, TEXT_COLOR)
        screen.blit(count_surface, (20, 40))

        # Book list area
        list_area = pygame.Rect(20, 60, 280, 180)
        pygame.draw.rect(screen, BOOK_LIST_COLOR, list_area)
        pygame.draw.rect(screen, TEXT_COLOR, list_area, 1)

        # Render visible books
        if self.books:
            for i in range(self.max_visible_books):
                book_index = self.scroll_offset + i
                if book_index >= len(self.books):
                    break
                
                y = 60 + i * 20
                book_filename = self.books[book_index]
                book_name = self._get_book_display_name(book_filename)
                
                # Highlight selected book
                if book_index == self.selected_book_index:
                    highlight_rect = pygame.Rect(22, y + 2, 276, 16)
                    color = FOCUS_COLOR if self.focus_index >= len(self.widgets) else SELECTED_BOOK_COLOR
                    pygame.draw.rect(screen, color, highlight_rect)
                
                # Render book name (truncate if too long)
                if len(book_name) > 35:
                    book_name = book_name[:32] + "..."
                
                text_surface = self.font.render(book_name, self.is_text_antialiased, TEXT_COLOR)
                screen.blit(text_surface, (25, y + 3))
        else:
            # No books message
            no_books_text = "No books in library."
            no_books_surface = self.font.render(no_books_text, self.is_text_antialiased, TEXT_COLOR)
            text_rect = no_books_surface.get_rect(center=(160, 150))
            screen.blit(no_books_surface, text_rect)
            
            help_text = "Use book crates in cargo to add books."
            help_surface = self.font.render(help_text, self.is_text_antialiased, TEXT_COLOR)
            help_rect = help_surface.get_rect(center=(160, 170))
            screen.blit(help_surface, help_rect)

        # Scroll indicators
        if self.books and len(self.books) > self.max_visible_books:
            # Up arrow
            if self.scroll_offset > 0:
                pygame.draw.polygon(screen, TEXT_COLOR, [(310, 70), (315, 60), (320, 70)])
            
            # Down arrow
            if self.scroll_offset + self.max_visible_books < len(self.books):
                pygame.draw.polygon(screen, TEXT_COLOR, [(310, 230), (315, 240), (320, 230)])

        # Render buttons
        for widget in self.widgets:
            self._render_button(screen, widget)

        # Instructions
        if self.books:
            if self.focus_index >= len(self.widgets):
                instr_text = "↑↓: Select book  Enter: Read  Space: Move to Cargo  Tab: Buttons"
            else:
                instr_text = "↑↓: Navigate buttons  Enter: Activate  Tab: Book list"
        else:
            instr_text = "Collect book crates and use them to add books to your library"
        
        instr_surface = self.font.render(instr_text, self.is_text_antialiased, TEXT_COLOR)
        instr_rect = instr_surface.get_rect(center=(160, 275))
        screen.blit(instr_surface, instr_rect)

    def _render_button(self, screen, widget):
        """Render a button widget"""
        x, y = widget["position"]
        w, h = widget["size"]
        
        # Button background
        color = BUTTON_FOCUSED if widget.get("focused") else BUTTON_COLOR
        pygame.draw.rect(screen, color, (x, y, w, h))
        pygame.draw.rect(screen, TEXT_COLOR, (x, y, w, h), 1)
        
        # Button text
        text_surface = self.font.render(widget["text"], self.is_text_antialiased, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
        screen.blit(text_surface, text_rect)
