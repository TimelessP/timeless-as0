"""
Book Reading Scene - Display markdown books with simple formatting and images
"""
import pygame
import os
import tempfile
import shutil
import base64
import urllib.request
import urllib.parse
from typing import Optional, List, Dict, Any, Tuple
from core_simulator import get_assets_path

# Colors (import from theme, but keep book ink and paper as is)
from theme import (
    BACKGROUND_COLOR,
    BOOKMARK_COLOR,
    BOOKMARK_PLACEHOLDER_COLOR,
    PAGE_BORDER_COLOR,
    PAPER_COLOR,
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
TEXT_COLOR = (60, 50, 40)  # Book ink (keep as is)

# Global image cache for cleanup on exit
_image_cache_dir = None
_cached_images = {}

def cleanup_image_cache():
    """Clean up temporary image cache directory"""
    global _image_cache_dir
    if _image_cache_dir and os.path.exists(_image_cache_dir):
        shutil.rmtree(_image_cache_dir, ignore_errors=True)
        _image_cache_dir = None

def get_image_cache_dir():
    """Get or create temporary image cache directory"""
    global _image_cache_dir
    if _image_cache_dir is None or not os.path.exists(_image_cache_dir):
        _image_cache_dir = tempfile.mkdtemp(prefix="airship_book_images_")
    return _image_cache_dir

class BookScene:
    def __init__(self, simulator, book_filename: str):
        self.simulator = simulator
        self.book_filename = book_filename
        self.font = None
        self.is_text_antialiased = False
        self.widgets = []
        self.focus_index = 0
        
        # Book content
        self.book_title = ""
        self.pages = []  # List of pages, each page is a list of (text, x, y, is_bold) tuples
        self.current_page = 0
        
        # Page layout settings
        self.page_margin = 8  # Reduced from 20 to ~1 character width
        self.line_height = 18
        self.page_width = 280
        self.page_height = 225  # Increased from 200 to use more available space
        self.page_x = 20
        self.page_y = 30  # Adjusted for header box
        
        self._init_widgets()
        self._load_book()

    def set_font(self, font, is_text_antialiased=False):
        self.font = font
        self.is_text_antialiased = is_text_antialiased
        # Re-flow pages when font changes
        if self.font:
            self._parse_and_layout_book()

    def _init_widgets(self):
        """Initialize widgets"""
        self.widgets = [
            {"id": "close", "type": "button", "position": [8, 290], "size": [60, 20], "text": "Close", "focused": True},
            {"id": "prev_page", "type": "button", "position": [100, 260], "size": [80, 20], "text": "< Previous", "focused": False},
            {"id": "next_page", "type": "button", "position": [200, 260], "size": [80, 20], "text": "Next >", "focused": False},
            {"id": "bookmark", "type": "bookmark", "position": [285, 25], "size": [12, 20], "text": "", "focused": False},
        ]

    def _load_book(self):
        """Load and parse the book content"""
        book_path = os.path.join(get_assets_path("books"), self.book_filename)
        
        try:
            with open(book_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from first heading or filename
            lines = content.split('\n')
            self.book_title = self._get_book_title(lines)
            
            # Parse and layout the book if font is available
            if self.font:
                self._parse_and_layout_book(content)
            else:
                # Store content for later parsing
                self._raw_content = content
        
        except Exception as e:
            self.book_title = "Error Loading Book"
            self.pages = [[("Could not load book: " + str(e), 0, 0, False)]]

    def _get_book_title(self, lines: List[str]) -> str:
        """Extract book title from content"""
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        # Fallback to filename
        title = self.book_filename.replace('.md', '').replace('-', ' ').replace('_', ' ')
        return ' '.join(word.capitalize() for word in title.split())

    def _parse_and_layout_book(self, content: str = None):
        """Parse markdown content and layout pages"""
        if not self.font:
            return
        
        if content is None:
            if hasattr(self, '_raw_content'):
                content = self._raw_content
            else:
                return
        
        # Parse markdown into word list with formatting
        words = self._parse_markdown(content)
        
        # Layout words into pages
        self.pages = self._layout_pages(words)
        
        # Ensure current page is valid
        if self.current_page >= len(self.pages):
            self.current_page = max(0, len(self.pages) - 1)

    def _parse_markdown(self, content: str) -> List[Dict[str, Any]]:
        """Parse simple markdown into word list with formatting"""
        words = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Empty line creates paragraph break
                words.append({"text": "\n\n", "is_bold": False, "is_heading": False, "is_image": False})
                continue
            
            # Check for image syntax: ![alt text](image_path)
            if line.startswith('![') and '](' in line and line.endswith(')'):
                # Parse image markdown
                alt_start = line.find('[') + 1
                alt_end = line.find(']')
                url_start = line.find('(') + 1
                url_end = line.find(')')
                
                if alt_start < alt_end and url_start < url_end:
                    alt_text = line[alt_start:alt_end]
                    image_url = line[url_start:url_end]
                    
                    # Add image as special word type
                    words.append({
                        "text": alt_text,
                        "is_bold": False,
                        "is_heading": False,
                        "is_image": True,
                        "image_url": image_url
                    })
                    continue
            
            is_heading = line.startswith('#')
            if is_heading:
                # Remove markdown heading syntax
                line = line.lstrip('#').strip()
                is_bold = True
            else:
                is_bold = False
            
            # Split line into words
            line_words = line.split()
            for i, word in enumerate(line_words):
                words.append({
                    "text": word,
                    "is_bold": is_bold,
                    "is_heading": is_heading,
                    "is_image": False
                })
                
                # Add space after word (except last word in line)
                if i < len(line_words) - 1:
                    words.append({
                        "text": " ",
                        "is_bold": is_bold,
                        "is_heading": is_heading,
                        "is_image": False
                    })
            
            # Add line break after each line (except headings which get extra space)
            if is_heading:
                words.append({"text": "\n\n", "is_bold": False, "is_heading": False, "is_image": False})
            else:
                words.append({"text": "\n", "is_bold": False, "is_heading": False, "is_image": False})
        
        return words

    def _fetch_image(self, image_url: str) -> Optional[pygame.Surface]:
        """Fetch and cache an image from URL or data URI"""
        global _cached_images
        
        # Check cache first
        if image_url in _cached_images:
            return _cached_images[image_url]
        
        try:
            if image_url.startswith('data:'):
                # Handle data URI
                surface = self._load_data_uri_image(image_url)
            else:
                # Handle file path or URL
                surface = self._load_file_image(image_url)
            
            # Cache the result (even if None)
            _cached_images[image_url] = surface
            return surface
            
        except Exception as e:
            print(f"Error loading image {image_url}: {e}")
            _cached_images[image_url] = None
            return None

    def _load_data_uri_image(self, data_uri: str) -> Optional[pygame.Surface]:
        """Load image from data URI"""
        try:
            # Parse data URI: data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...
            if ';base64,' not in data_uri:
                return None
            
            header, data = data_uri.split(';base64,', 1)
            image_data = base64.b64decode(data)
            
            # Create temporary file
            cache_dir = get_image_cache_dir()
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=cache_dir, suffix='.png')
            temp_file.write(image_data)
            temp_file.close()
            
            # Load with pygame
            surface = pygame.image.load(temp_file.name)
            return surface.convert_alpha()
            
        except Exception as e:
            print(f"Error loading data URI image: {e}")
            return None

    def _load_file_image(self, image_path: str) -> Optional[pygame.Surface]:
        """Load image from file path or URL"""
        try:
            if image_path.startswith('http://') or image_path.startswith('https://'):
                # Download from URL
                cache_dir = get_image_cache_dir()
                filename = os.path.basename(urllib.parse.urlparse(image_path).path) or 'image.png'
                local_path = os.path.join(cache_dir, filename)
                
                urllib.request.urlretrieve(image_path, local_path)
                surface = pygame.image.load(local_path)
                return surface.convert_alpha()
            else:
                # Local file path - resolve relative to the markdown file
                if not os.path.isabs(image_path):
                    # Get the directory containing the markdown file
                    book_path = os.path.join(get_assets_path("books"), self.book_filename)
                    book_dir = os.path.dirname(book_path)
                    
                    # Resolve the relative path
                    full_path = os.path.normpath(os.path.join(book_dir, image_path))
                    
                    # Security check: ensure the resolved path is within the assets directory
                    assets_root = os.path.normpath(os.path.dirname(get_assets_path("")))
                    try:
                        # Check if the resolved path is within assets directory
                        os.path.relpath(full_path, assets_root)
                        if not full_path.startswith(assets_root):
                            print(f"Security error: Image path '{image_path}' resolves outside assets directory")
                            return None
                    except ValueError:
                        # os.path.relpath raises ValueError if paths are on different drives (Windows)
                        print(f"Security error: Image path '{image_path}' is invalid")
                        return None
                else:
                    # Absolute paths are not allowed for security
                    print(f"Security error: Absolute image paths not allowed: {image_path}")
                    return None
                
                if os.path.exists(full_path):
                    surface = pygame.image.load(full_path)
                    return surface.convert_alpha()
                else:
                    print(f"Image file not found: {full_path}")
                    return None
                    
        except Exception as e:
            print(f"Error loading file image {image_path}: {e}")
            return None

    def _get_word_dimensions(self, word_data: Dict[str, Any]) -> Tuple[int, int]:
        """Get width and height of a word or image when rendered"""
        if word_data.get("is_image", False):
            # Handle image dimensions
            image_surface = self._fetch_image(word_data.get("image_url", ""))
            if image_surface:
                # Calculate scaled dimensions to fit page
                img_w, img_h = image_surface.get_size()
                max_width = self.page_width - 2 * self.page_margin
                max_height = self.page_height - 2 * self.page_margin
                
                # Scale proportionally to fit
                scale_w = max_width / img_w if img_w > max_width else 1
                scale_h = max_height / img_h if img_h > max_height else 1
                scale = min(scale_w, scale_h)
                
                return int(img_w * scale), int(img_h * scale)
            else:
                # Fallback for failed image load
                return 200, 20  # Placeholder dimensions
        else:
            # Handle text dimensions
            text = word_data["text"]
            
            # Create a temporary surface to measure text
            if word_data.get("is_bold") or word_data.get("is_heading"):
                # For bold text, we'll render it normally but return slightly larger dimensions
                surface = self.font.render(text, self.is_text_antialiased, TEXT_COLOR)
                w, h = surface.get_size()
                return w, h
            else:
                surface = self.font.render(text, self.is_text_antialiased, TEXT_COLOR)
                return surface.get_size()
        """Get width and height of a word when rendered"""
        text = word_data["text"]
        
        # Create a temporary surface to measure text
        if word_data.get("is_bold") or word_data.get("is_heading"):
            # For bold text, we'll render it normally but return slightly larger dimensions
            surface = self.font.render(text, self.is_text_antialiased, TEXT_COLOR)
            w, h = surface.get_size()
            return w, h
        else:
            surface = self.font.render(text, self.is_text_antialiased, TEXT_COLOR)
            return surface.get_size()

    def _layout_pages(self, words: List[Dict[str, Any]]) -> List[List[Tuple[str, int, int, bool, bool, str]]]:
        """Layout words into pages"""
        if not words:
            return []
        
        pages = []
        current_page = []
        
        x = self.page_margin
        y = self.page_margin
        max_width = self.page_width - 2 * self.page_margin
        max_height = self.page_height - 2 * self.page_margin
        
        for word_data in words:
            text = word_data["text"]
            is_bold = word_data.get("is_bold", False)
            is_heading = word_data.get("is_heading", False)
            is_image = word_data.get("is_image", False)
            image_url = word_data.get("image_url", "")
            
            # Handle special characters
            if text == "\n":
                # Line break
                x = self.page_margin
                y += self.line_height
                continue
            elif text == "\n\n":
                # Paragraph break
                x = self.page_margin
                y += self.line_height * 2
                continue
            
            # Get word/image dimensions
            word_width, word_height = self._get_word_dimensions(word_data)
            
            if is_image:
                # Images always start on a new line and take full width
                if x > self.page_margin:  # If not at start of line, go to next line
                    x = self.page_margin
                    y += self.line_height
                
                # Check if image fits on current page
                if y + word_height > max_height:
                    # Start new page for image
                    if current_page:
                        pages.append(current_page)
                    current_page = []
                    x = self.page_margin
                    y = self.page_margin
                
                # Add image to current page
                current_page.append((text, x, y, is_bold, is_image, image_url))
                
                # Move to next line after image
                x = self.page_margin
                y += word_height + self.line_height  # Add some space after image
            else:
                # Handle text
                # Check if word fits on current line
                if x + word_width > max_width and x > self.page_margin:
                    # Wrap to next line
                    x = self.page_margin
                    y += self.line_height
                
                # Check if we need a new page
                if y + word_height > max_height:
                    # Start new page
                    if current_page:
                        pages.append(current_page)
                    current_page = []
                    x = self.page_margin
                    y = self.page_margin
                
                # Add word to current page
                current_page.append((text, x, y, is_bold, is_image, image_url))
                
                # Move x position for next word
                x += word_width
        
        # Add final page if it has content
        if current_page:
            pages.append(current_page)
        
        return pages if pages else [[("No content", self.page_margin, self.page_margin, False, False, "")]]

    def handle_event(self, event) -> Optional[str]:
        if not pygame:
            return None
            
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            
            # Always allow escape to close
            if event.key == pygame.K_ESCAPE:
                return "scene_library"
            
            # Page navigation
            if event.key == pygame.K_LEFT or event.key == pygame.K_PAGEUP:
                self._prev_page()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_PAGEDOWN:
                self._next_page()
            elif event.key == pygame.K_HOME:
                self.current_page = 0
            elif event.key == pygame.K_END:
                self.current_page = max(0, len(self.pages) - 1)
            
            # Bookmark shortcuts
            elif event.key == pygame.K_b:
                self._toggle_bookmark()
            elif event.key == pygame.K_g:
                self._goto_bookmark()
            
            # Button navigation
            elif event.key == pygame.K_TAB:
                if mods & pygame.KMOD_SHIFT:
                    self._focus_prev()
                else:
                    self._focus_next()
            elif event.key == pygame.K_UP:
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
                    
                    # Special handling for bookmark
                    if widget["id"] == "bookmark":
                        current_bookmark = self.simulator.get_bookmark(self.book_filename)
                        if current_bookmark is not None and current_bookmark != self.current_page:
                            # Go to bookmark if bookmark exists and we're not on bookmarked page
                            self._goto_bookmark()
                        else:
                            # Toggle bookmark if on bookmarked page, or set bookmark if none exists
                            self._toggle_bookmark()
                        return None  # Don't call _activate_focused for bookmarks
                    else:
                        return self._activate_focused()
            
            # Page area clicks for navigation
            page_rect = pygame.Rect(self.page_x, self.page_y, self.page_width, self.page_height)
            if page_rect.contains(pygame.Rect(event.pos[0], event.pos[1], 1, 1)):
                if event.pos[0] < self.page_x + self.page_width // 2:
                    self._prev_page()
                else:
                    self._next_page()

        return None

    def _focus_next(self):
        self.focus_index = (self.focus_index + 1) % len(self.widgets)
        self._update_focus()

    def _focus_prev(self):
        self.focus_index = (self.focus_index - 1) % len(self.widgets)
        self._update_focus()

    def _update_focus(self):
        """Update focus state of widgets"""
        for widget in self.widgets:
            widget["focused"] = False
        if 0 <= self.focus_index < len(self.widgets):
            self.widgets[self.focus_index]["focused"] = True

    def _activate_focused(self) -> Optional[str]:
        widget = self.widgets[self.focus_index]
        if widget["id"] == "close":
            return "scene_library"
        elif widget["id"] == "prev_page":
            self._prev_page()
        elif widget["id"] == "next_page":
            self._next_page()
        elif widget["id"] == "bookmark":
            self._toggle_bookmark()
        return None

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1

    def _next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1

    def _toggle_bookmark(self):
        """Toggle bookmark for current page"""
        current_bookmark = self.simulator.get_bookmark(self.book_filename)
        
        if current_bookmark is not None:
            # Remove bookmark
            self.simulator.remove_bookmark(self.book_filename)
        else:
            # Add bookmark
            self.simulator.set_bookmark(self.book_filename, self.current_page)

    def _goto_bookmark(self):
        """Go to bookmarked page"""
        bookmark_page = self.simulator.get_bookmark(self.book_filename)
        if bookmark_page is not None and 0 <= bookmark_page < len(self.pages):
            self.current_page = bookmark_page

    def update(self, dt: float):
        """Update the scene"""
        self.simulator.update(dt)

    def render(self, screen):
        if not pygame or not self.font:
            return

        # Clear screen
        screen.fill(BACKGROUND_COLOR)

        # Header background box (like other scenes)
        pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(screen, BUTTON_TEXT_COLOR, (0, 0, 320, 24), 1)

        # Title in header box
        title_surface = self.font.render(self.book_title, self.is_text_antialiased, BUTTON_TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(160, 12))
        screen.blit(title_surface, title_rect)

        # Page background
        page_rect = pygame.Rect(self.page_x, self.page_y, self.page_width, self.page_height)
        pygame.draw.rect(screen, PAPER_COLOR, page_rect)
        pygame.draw.rect(screen, PAGE_BORDER_COLOR, page_rect, 2)

        # Render current page content
        if self.pages and 0 <= self.current_page < len(self.pages):
            current_page_words = self.pages[self.current_page]
            
            for item in current_page_words:
                if len(item) == 6:
                    text, x, y, is_bold, is_image, image_url = item
                else:
                    # Backwards compatibility with old tuple format
                    text, x, y, is_bold = item
                    is_image, image_url = False, ""
                
                if is_image:
                    # Render image
                    image_surface = self._fetch_image(image_url)
                    if image_surface:
                        # Scale image to fit
                        img_w, img_h = image_surface.get_size()
                        max_width = self.page_width - 2 * self.page_margin
                        max_height = self.page_height - 2 * self.page_margin
                        
                        # Calculate scale
                        scale_w = max_width / img_w if img_w > max_width else 1
                        scale_h = max_height / img_h if img_h > max_height else 1
                        scale = min(scale_w, scale_h)
                        
                        if scale < 1:
                            # Scale down the image
                            new_w = int(img_w * scale)
                            new_h = int(img_h * scale)
                            scaled_surface = pygame.transform.scale(image_surface, (new_w, new_h))
                        else:
                            scaled_surface = image_surface
                        
                        screen.blit(scaled_surface, (self.page_x + x, self.page_y + y))
                    else:
                        # Render placeholder for failed images
                        placeholder_text = f"[Image: {text}]"
                        text_surface = self.font.render(placeholder_text, self.is_text_antialiased, TEXT_COLOR)
                        screen.blit(text_surface, (self.page_x + x, self.page_y + y))
                else:
                    # Render text
                    if text.strip():  # Skip empty strings
                        # Render text (we'll simulate bold by rendering slightly offset)
                        if is_bold:
                            # Render bold by drawing text twice with slight offset
                            text_surface = self.font.render(text, self.is_text_antialiased, TEXT_COLOR)
                            screen.blit(text_surface, (self.page_x + x, self.page_y + y))
                            screen.blit(text_surface, (self.page_x + x + 1, self.page_y + y))
                        else:
                            text_surface = self.font.render(text, self.is_text_antialiased, TEXT_COLOR)
                            screen.blit(text_surface, (self.page_x + x, self.page_y + y))

        # Page number
        if self.pages:
            page_info = f"Page {self.current_page + 1} of {len(self.pages)}"
            page_surface = self.font.render(page_info, self.is_text_antialiased, BUTTON_TEXT_COLOR)
            page_rect = page_surface.get_rect(center=(160, 285))
            screen.blit(page_surface, page_rect)

        # Render bookmark
        self._render_bookmark(screen)

        # Render buttons
        for widget in self.widgets:
            if widget["id"] != "bookmark":  # Don't render bookmark as regular button
                self._render_button(screen, widget)

    def _render_button(self, screen, widget):
        """Render a button widget"""
        x, y = widget["position"]
        w, h = widget["size"]

        # Determine enabled state (all buttons enabled in book scene for now)
        enabled = True
        # If you add disabled logic, set enabled = False as needed

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

    def _render_bookmark(self, screen):
        """Render the bookmark"""
        bookmark_page = self.simulator.get_bookmark(self.book_filename)
        
        # Get bookmark widget position and size
        bookmark_widget = None
        for widget in self.widgets:
            if widget["id"] == "bookmark":
                bookmark_widget = widget
                break
        
        if not bookmark_widget:
            return
        
        x, y = bookmark_widget["position"]
        w, h = bookmark_widget["size"]
        
        # Check if bookmark is focused
        focused = bookmark_widget.get("focused", False)
        
        # Always show some kind of bookmark indicator
        if bookmark_page is not None:
            # Create bookmark shape - rectangle with triangle cut out bottom
            bookmark_points = [
                (x, y),                    # Top left
                (x + w, y),                # Top right
                (x + w, y + h - 6),        # Right side, above triangle
                (x + w//2, y + h),         # Bottom point (triangle point)
                (x, y + h - 6),            # Left side, above triangle
            ]
            
            # Use proper bookmark color regardless of focus
            bookmark_color = BOOKMARK_COLOR if not focused else BUTTON_FOCUSED_COLOR
            border_color = BUTTON_BORDER_FOCUSED_COLOR if focused else BUTTON_BORDER_COLOR
            border_width = 1
            
            # If we're on the bookmarked page, show the full bookmark with ribbon end
            if bookmark_page == self.current_page:
                # Draw full bookmark with ribbon cut
                pygame.draw.polygon(screen, bookmark_color, bookmark_points)
                pygame.draw.polygon(screen, border_color, bookmark_points, border_width)
            else:
                # Show just the rectangle part (sticking out from page)
                rect_points = [
                    (x, y),
                    (x + w, y),
                    (x + w, y + h - 6),
                    (x, y + h - 6),
                ]
                pygame.draw.polygon(screen, bookmark_color, rect_points)
                pygame.draw.polygon(screen, border_color, rect_points, border_width)
        else:
            # Show grey placeholder bookmark (just the rectangle part)
            placeholder_color = BOOKMARK_PLACEHOLDER_COLOR
            border_color = BUTTON_BORDER_FOCUSED_COLOR if focused else BUTTON_BORDER_COLOR
            border_width = 1
            
            rect_points = [
                (x, y),
                (x + w, y),
                (x + w, y + h - 6),
                (x, y + h - 6),
            ]
            pygame.draw.polygon(screen, placeholder_color, rect_points)
            pygame.draw.polygon(screen, border_color, rect_points, border_width)
