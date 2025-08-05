"""
Crew Scene - Personal log, library, and crew management
Handles logbook entries, personal library, and crew status
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
CREW_HEADER_COLOR = (20, 60, 40)  # Green for crew scene

class CrewScene:
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
        """Initialize crew management widgets"""
        self.widgets = [
            # Navigation buttons
            {"id": "prev_scene", "type": "button", "position": [8, 290], "size": [60, 24], "text": "< [", "focused": True},
            {"id": "next_scene", "type": "button", "position": [252, 290], "size": [60, 24], "text": "] >", "focused": False},
            
            # Captain info
            {"id": "captain_name", "type": "label", "position": [8, 40], "size": [200, 16], "text": "Captain: Sarah Mitchell", "focused": False},
            {"id": "medical_status", "type": "label", "position": [8, 60], "size": [200, 16], "text": "Medical: Current", "focused": False},
            {"id": "flight_phase", "type": "label", "position": [8, 80], "size": [150, 16], "text": "Phase: Cruise", "focused": False},
            
            # Logbook controls
            {"id": "view_logbook", "type": "button", "position": [8, 110], "size": [80, 16], "text": "Logbook", "focused": False},
            {"id": "add_entry", "type": "button", "position": [100, 110], "size": [80, 16], "text": "Add Entry", "focused": False},
            
            # Personal library
            {"id": "library_slots", "type": "label", "position": [8, 140], "size": [150, 16], "text": "Library: 8/12 books", "focused": False},
            {"id": "current_book", "type": "label", "position": [8, 160], "size": [200, 16], "text": "Reading: Flight Manual", "focused": False},
            {"id": "read_book", "type": "button", "position": [8, 180], "size": [60, 16], "text": "Read", "focused": False},
            
            # Inventory
            {"id": "inventory_slots", "type": "label", "position": [8, 210], "size": [150, 16], "text": "Inventory: 2/4 slots", "focused": False},
            {"id": "item_1", "type": "label", "position": [8, 230], "size": [150, 16], "text": "- Camera gear", "focused": False},
            {"id": "item_2", "type": "label", "position": [8, 250], "size": [150, 16], "text": "- Navigation tools", "focused": False},
        ]
        
        # Set initial focus
        if self.widgets:
            self.widgets[self.focused_widget]["focused"] = True
    
    def update(self, dt: float):
        """Update crew display with current simulator data"""
        if not self.simulator:
            return
            
        state = self.simulator.get_state()
        crew = state.get("crew", {})
        
        # Update captain info
        captain = crew.get("captain", {})
        name = captain.get("name", "Unknown")
        self.widgets[2]["text"] = f"Captain: {name}"
        
        # Update medical status
        last_medical = captain.get("lastMedical", "")
        if last_medical:
            self.widgets[3]["text"] = f"Medical: Current"
        else:
            self.widgets[3]["text"] = f"Medical: Unknown"
        
        # Update flight phase
        current_phase = crew.get("currentPhase", "cruise")
        self.widgets[4]["text"] = f"Phase: {current_phase.title()}"
        
        # Update library info
        library = crew.get("personalLibrary", {})
        max_books = library.get("maxBookSlots", 12)
        current_books = 8  # Stub data
        self.widgets[7]["text"] = f"Library: {current_books}/{max_books} books"
        
        # Update inventory
        inventory = crew.get("inventory", {})
        max_slots = inventory.get("maxSlots", 4)
        available = inventory.get("availableSlots", 2)
        used = max_slots - available
        self.widgets[10]["text"] = f"Inventory: {used}/{max_slots} slots"
    
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
        return "scene_camera"
    
    def _get_next_scene(self) -> str:
        """Get the next scene in circular order"""
        return "scene_missions"
    
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
        elif widget_id == "view_logbook":
            # TODO: Open logbook interface
            pass
        elif widget_id == "add_entry":
            # TODO: Add logbook entry
            pass
        elif widget_id == "read_book":
            # TODO: Open reading interface
            pass
            
        return None
    
    def render(self, surface):
        """Render the crew scene"""
        # Clear background
        surface.fill(BACKGROUND_COLOR)
        
        if not self.font:
            return
        
        # Draw colored title header
        pygame.draw.rect(surface, CREW_HEADER_COLOR, (0, 0, 320, 24))
        pygame.draw.rect(surface, TEXT_COLOR, (0, 0, 320, 24), 1)
        
        # Centered title
        title = self.font.render("CREW MANAGEMENT", self.is_text_antialiased, TEXT_COLOR)
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
            text_color = FOCUS_COLOR if focused else TEXT_COLOR
            text_surface = self.font.render(text, self.is_text_antialiased, text_color)
            surface.blit(text_surface, (x, y))
