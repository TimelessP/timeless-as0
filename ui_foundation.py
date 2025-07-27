#!/usr/bin/env python3
"""
UI Foundation for Airship Zero
Foundational UI architecture with modal input handling and responsive layout.
"""

import pygame
import os
from typing import Optional, List, Dict, Tuple, Any, Callable
from abc import ABC, abstractmethod
from enum import Enum


class InputMode(Enum):
    """Input handling modes for different interface contexts."""
    GLOBAL = "global"
    BRIDGE = "bridge" 
    ENGINE_ROOM = "engine_room"
    LIBRARY = "library"
    CREW_QUARTERS = "crew_quarters"
    COMMS = "comms"
    TEXT_ENTRY = "text_entry"


class Widget(ABC):
    """Base class for all UI widgets with hierarchical layout and input handling."""
    
    def __init__(self, parent: Optional['Widget'] = None):
        self.parent = parent
        self.children: List['Widget'] = []
        self.visible = True
        self.enabled = True
        
        # Layout properties
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.min_width = 0
        self.min_height = 0
        self.layout_dirty = True  # Flag to indicate layout needs recalculation
        
        # Style properties (inherited from parent if not set)
        self.font: Optional[pygame.font.Font] = None
        self.bg_color: Optional[Tuple[int, int, int]] = None
        self.text_color: Optional[Tuple[int, int, int]] = None
        self.border_color: Optional[Tuple[int, int, int]] = None
        self.padding = 4
        
        # Input handling
        self.input_mode: Optional[InputMode] = None
        self.focusable = False
        self.has_focus = False
        
        if parent:
            parent.add_child(self)
    
    def add_child(self, child: 'Widget'):
        """Add a child widget."""
        if child not in self.children:
            self.children.append(child)
            child.parent = self
    
    def remove_child(self, child: 'Widget'):
        """Remove a child widget."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def get_inherited_font(self) -> pygame.font.Font:
        """Get font, inheriting from parent if not set."""
        if self.font:
            return self.font
        elif self.parent:
            return self.parent.get_inherited_font()
        else:
            # Fallback to root container font
            return RootContainer.get_instance().default_font
    
    def get_inherited_bg_color(self) -> Tuple[int, int, int]:
        """Get background color, inheriting from parent if not set."""
        if self.bg_color:
            return self.bg_color
        elif self.parent:
            return self.parent.get_inherited_bg_color()
        else:
            return (30, 30, 30)  # Default dark background
    
    def get_inherited_text_color(self) -> Tuple[int, int, int]:
        """Get text color, inheriting from parent if not set."""
        if self.text_color:
            return self.text_color
        elif self.parent:
            return self.parent.get_inherited_text_color()
        else:
            return (220, 220, 220)  # Default light text
    
    def measure_text(self, text: str) -> Tuple[int, int]:
        """Measure text dimensions using inherited font."""
        font = self.get_inherited_font()
        return font.size(text)
    
    def set_bounds(self, x: int, y: int, width: int, height: int):
        """Set widget bounds and trigger layout of children."""
        # Check if bounds actually changed to avoid unnecessary recalculation
        if self.x != x or self.y != y or self.width != width or self.height != height:
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.mark_layout_dirty()
    
    def mark_layout_dirty(self):
        """Mark this widget and its children as needing layout recalculation."""
        self.layout_dirty = True
        for child in self.children:
            child.mark_layout_dirty()
    
    def ensure_layout(self):
        """Ensure layout is up to date, recalculating if dirty."""
        if self.layout_dirty:
            self.layout_children()
            self.layout_dirty = False
    
    @abstractmethod
    def layout_children(self):
        """Layout child widgets within this widget's bounds."""
        pass
    
    @abstractmethod
    def render(self, surface: pygame.Surface):
        """Render this widget to the given surface."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input event. Returns True if event was consumed.
        Override in subclasses for custom input handling.
        """
        # Pass to focused child first
        for child in reversed(self.children):  # Top-to-bottom rendering order
            if child.visible and child.handle_event(event):
                return True
        return False
    
    def get_widget_at(self, x: int, y: int) -> Optional['Widget']:
        """Get the topmost widget at screen coordinates."""
        # Check if point is within our bounds
        if not (self.x <= x < self.x + self.width and self.y <= y < self.y + self.height):
            return None
        
        # Check children first (top-to-bottom)
        for child in reversed(self.children):
            if child.visible:
                result = child.get_widget_at(x, y)
                if result:
                    return result
        
        # Return self if no child claimed the point
        return self


class RootContainer(Widget):
    """
    Top-level container that manages the pygame surface and window events.
    Singleton pattern - there can be only one root container.
    """
    
    _instance: Optional['RootContainer'] = None
    
    def __init__(self, width: int = 1920, height: int = 1080):
        if RootContainer._instance is not None:
            raise RuntimeError("Only one RootContainer instance allowed")
        
        super().__init__(parent=None)
        RootContainer._instance = self
        
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        
        # Load default font
        font_path = os.path.join("assets", "fonts", "Roboto_Mono", "RobotoMono-Regular.ttf")
        if os.path.exists(font_path):
            self.default_font = pygame.font.Font(font_path, 14)
        else:
            self.default_font = pygame.font.Font(None, 14)
        
        # Create pygame surface
        self.surface = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Airship Zero")
        
        # Set initial bounds to fill surface
        self.set_bounds(0, 0, width, height)
        
        # Default styling
        self.font = self.default_font
        self.bg_color = (20, 20, 20)  # Very dark background
        self.text_color = (220, 220, 220)  # Light text
        
        # Input handling
        self.input_stack: List[InputMode] = [InputMode.GLOBAL]
        self.focused_widget: Optional[Widget] = None
        
        # Running state
        self.running = True
        self.clock = pygame.time.Clock()
    
    @classmethod
    def get_instance(cls) -> 'RootContainer':
        """Get the singleton instance."""
        if cls._instance is None:
            raise RuntimeError("RootContainer not initialized")
        return cls._instance
    
    def push_input_mode(self, mode: InputMode):
        """Push a new input mode onto the stack."""
        if mode not in self.input_stack:
            self.input_stack.append(mode)
    
    def pop_input_mode(self, mode: InputMode):
        """Remove an input mode from the stack."""
        if mode in self.input_stack and len(self.input_stack) > 1:
            self.input_stack.remove(mode)
    
    def get_current_input_mode(self) -> InputMode:
        """Get the current top-level input mode."""
        return self.input_stack[-1]
    
    def handle_window_resize(self, width: int, height: int):
        """Handle window resize events."""
        self.set_bounds(0, 0, width, height)
        # Surface will be automatically updated by pygame
    
    def layout_children(self):
        """Layout children to fill the entire container."""
        for child in self.children:
            child.set_bounds(0, 0, self.width, self.height)
    
    def render(self, surface: pygame.Surface):
        """Render the root container and all children."""
        # Ensure layout is current before rendering
        self.ensure_layout()
        
        # Fill background
        surface.fill(self.get_inherited_bg_color())
        
        # Render all children
        for child in self.children:
            if child.visible:
                child.ensure_layout()  # Ensure each child's layout is current
                child.render(surface)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events with modal input processing."""
        # Handle window events first
        if event.type == pygame.QUIT:
            self.running = False
            return True
        elif event.type == pygame.VIDEORESIZE:
            self.handle_window_resize(event.w, event.h)
            return True
        
        # Pass to widget hierarchy
        return super().handle_event(event)
    
    def main_loop(self):
        """Main application loop."""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                self.handle_event(event)
            
            # Render
            self.render(self.surface)
            pygame.display.flip()
            
            # Control frame rate
            self.clock.tick(60)
        
        pygame.quit()


class Label(Widget):
    """Simple text label widget."""
    
    def __init__(self, text: str = "", parent: Optional[Widget] = None):
        super().__init__(parent)
        self.text = text
        self.text_align = "left"  # "left", "center", "right"
        
    def layout_children(self):
        """Labels have no children to layout."""
        pass
    
    def get_content_size(self) -> Tuple[int, int]:
        """Get the natural size of the label content."""
        if not self.text:
            return (0, 0)
        return self.measure_text(self.text)
    
    def render(self, surface: pygame.Surface):
        """Render the label text."""
        if not self.text or not self.visible:
            return
        
        font = self.get_inherited_font()
        text_color = self.get_inherited_text_color()
        
        # Render text
        text_surface = font.render(self.text, True, text_color)
        text_width, text_height = text_surface.get_size()
        
        # Calculate position based on alignment
        if self.text_align == "center":
            text_x = self.x + (self.width - text_width) // 2
        elif self.text_align == "right":
            text_x = self.x + self.width - text_width - self.padding
        else:  # left
            text_x = self.x + self.padding
        
        text_y = self.y + (self.height - text_height) // 2
        
        surface.blit(text_surface, (text_x, text_y))


class Timer(Widget):
    """Non-rendering timer component for time-based events."""
    
    def __init__(self, duration_ms: int, callback: Callable[[], None], 
                 repeat: bool = False, parent: Optional[Widget] = None):
        super().__init__(parent)
        self.duration_ms = duration_ms
        self.callback = callback
        self.repeat = repeat
        self.elapsed_ms = 0
        self.active = True
        self.visible = False  # Timers don't render
        
    def update(self, delta_ms: int):
        """Update timer state. Call this from the main loop."""
        if not self.active:
            return
            
        self.elapsed_ms += delta_ms
        
        if self.elapsed_ms >= self.duration_ms:
            self.callback()
            
            if self.repeat:
                self.elapsed_ms = 0
            else:
                self.active = False
    
    def reset(self):
        """Reset timer to start over."""
        self.elapsed_ms = 0
        self.active = True
    
    def stop(self):
        """Stop the timer."""
        self.active = False
    
    def layout_children(self):
        """Timers have no children and no layout."""
        pass
    
    def render(self, surface: pygame.Surface):
        """Timers don't render anything."""
        pass


class FlowContainer(Widget):
    """Base container for flowing layout of child widgets."""
    
    def __init__(self, direction: str = "vertical", spacing: int = 5, parent: Optional[Widget] = None):
        super().__init__(parent)
        self.direction = direction  # "vertical" or "horizontal"
        self.spacing = spacing
        self.padding = 10  # Internal padding from container edges
    
    def get_child_preferred_size(self, child: Widget) -> Tuple[int, int]:
        """Get the preferred size for a child widget."""
        if hasattr(child, 'get_content_size'):
            content_w, content_h = child.get_content_size()
            return (max(content_w + child.padding * 2, child.min_width),
                   max(content_h + child.padding * 2, child.min_height))
        else:
            return (max(50, child.min_width), max(20, child.min_height))
    
    def layout_children(self):
        """Layout children in flowing arrangement."""
        if not self.children:
            return
        
        # Calculate available space
        available_width = self.width - (self.padding * 2)
        available_height = self.height - (self.padding * 2)
        
        if self.direction == "vertical":
            self._layout_vertical(available_width, available_height)
        else:
            self._layout_horizontal(available_width, available_height)
    
    def _layout_vertical(self, available_width: int, available_height: int):
        """Layout children vertically, top to bottom."""
        current_y = self.y + self.padding
        
        # Calculate total preferred height and flexible children
        total_preferred_height = 0
        flexible_children = []
        
        for child in self.children:
            if not child.visible:
                continue
            pref_w, pref_h = self.get_child_preferred_size(child)
            total_preferred_height += pref_h
            # Children that don't have explicit preferred height are flexible
            if not hasattr(child, 'get_content_size') or pref_h <= child.min_height:
                flexible_children.append(child)
        
        # Add spacing
        spacing_total = self.spacing * max(0, len([c for c in self.children if c.visible]) - 1)
        total_preferred_height += spacing_total
        
        # Calculate extra space for flexible children
        extra_space = max(0, available_height - total_preferred_height)
        extra_per_flexible = extra_space // max(1, len(flexible_children)) if flexible_children else 0
        
        # Position each child
        for child in self.children:
            if not child.visible:
                continue
                
            pref_w, pref_h = self.get_child_preferred_size(child)
            
            # Width fills available space
            child_width = available_width
            
            # Height is preferred + extra if flexible
            child_height = pref_h
            if child in flexible_children:
                child_height += extra_per_flexible
            
            child.set_bounds(self.x + self.padding, current_y, child_width, child_height)
            child.layout_children()  # Recursively layout child's children
            current_y += child_height + self.spacing
    
    def _layout_horizontal(self, available_width: int, available_height: int):
        """Layout children horizontally, left to right."""
        current_x = self.x + self.padding
        
        # Calculate total preferred width and flexible children
        total_preferred_width = 0
        flexible_children = []
        
        for child in self.children:
            if not child.visible:
                continue
            pref_w, pref_h = self.get_child_preferred_size(child)
            total_preferred_width += pref_w
            # Children that don't have explicit preferred width are flexible
            if not hasattr(child, 'get_content_size') or pref_w <= child.min_width:
                flexible_children.append(child)
        
        # Add spacing
        spacing_total = self.spacing * max(0, len([c for c in self.children if c.visible]) - 1)
        total_preferred_width += spacing_total
        
        # Calculate extra space for flexible children
        extra_space = max(0, available_width - total_preferred_width)
        extra_per_flexible = extra_space // max(1, len(flexible_children)) if flexible_children else 0
        
        # Position each child
        for child in self.children:
            if not child.visible:
                continue
                
            pref_w, pref_h = self.get_child_preferred_size(child)
            
            # Height fills available space
            child_height = available_height
            
            # Width is preferred + extra if flexible
            child_width = pref_w
            if child in flexible_children:
                child_width += extra_per_flexible
            
            child.set_bounds(current_x, self.y + self.padding, child_width, child_height)
            child.layout_children()  # Recursively layout child's children
            current_x += child_width + self.spacing
    
    def render(self, surface: pygame.Surface):
        """Render container background and all children."""
        if not self.visible:
            return
        
        # Ensure layout is current before rendering
        self.ensure_layout()
        
        # Optional: draw container background for debugging
        # pygame.draw.rect(surface, (40, 40, 50), (self.x, self.y, self.width, self.height), 1)
        
        # Render all children
        for child in self.children:
            if child.visible:
                child.ensure_layout()
                child.render(surface)


class BlinkenLight(Widget):
    """A blinking light widget for aviation warning indicators."""
    
    def __init__(self, label: str = "", blink_rate_ms: int = 500, 
                 color: Tuple[int, int, int] = (255, 50, 50), 
                 parent: Optional[Widget] = None):
        super().__init__(parent)
        self.label = label
        self.blink_rate_ms = blink_rate_ms
        self.light_color = color
        self.is_on = True
        self.blinking = True
        
        # Create internal timer for blinking
        self.blink_timer = Timer(blink_rate_ms, self._toggle_light, repeat=True, parent=self)
        
        # Calculate proper minimum size including all components
        self._calculate_min_size()
    
    def _calculate_min_size(self):
        """Calculate minimum size based on LED, spacing, and text dimensions."""
        # LED component sizing
        led_radius = 8  # Standard LED radius
        led_margin = 5  # Margin before LED
        led_spacing = 8  # Space between LED and text
        
        # Text sizing - be more robust about font availability
        text_width = 0
        text_height = 16  # Safe fallback
        if self.label:
            try:
                # Try to measure text with current font
                text_width, text_height = self.measure_text(self.label)
            except:
                # More conservative fallback estimation
                text_width = len(self.label) * 8  # Slightly wider per character
                text_height = 18  # Slightly taller fallback
        
        # Total width: margin + LED diameter + spacing + text + right padding
        total_width = led_margin + (led_radius * 2) + led_spacing + text_width + self.padding
        
        # Height MUST accommodate both LED and text comfortably
        led_height = (led_radius * 2) + 6  # LED diameter + vertical margin
        text_height_with_padding = text_height + (self.padding * 2)
        
        # Use the larger of LED height or text height, with a reasonable minimum
        total_height = max(led_height, text_height_with_padding, 24)  # Never smaller than 24px
        
        self.min_width = int(total_width)
        self.min_height = int(total_height)
    
    def get_content_size(self) -> Tuple[int, int]:
        """Get the natural content size for layout calculations."""
        # Recalculate in case font context has changed
        self._calculate_min_size()
        return (self.min_width, self.min_height)
        
    def _toggle_light(self):
        """Internal callback to toggle light state."""
        if self.blinking:
            self.is_on = not self.is_on
    
    def set_blinking(self, blinking: bool):
        """Enable or disable blinking."""
        self.blinking = blinking
        if not blinking:
            self.is_on = True  # Stay on when not blinking
    
    def set_solid_on(self):
        """Set light to solid on (not blinking)."""
        self.blinking = False
        self.is_on = True
    
    def set_solid_off(self):
        """Set light to solid off (not blinking)."""
        self.blinking = False
        self.is_on = False
    
    def update(self, delta_ms: int):
        """Update the blink timer."""
        self.blink_timer.update(delta_ms)
    
    def layout_children(self):
        """Layout the internal timer (which doesn't render)."""
        pass
    
    def render(self, surface: pygame.Surface):
        """Render the blinking light."""
        if not self.visible:
            return
        
        # Draw background
        bg_color = (40, 40, 40) if not self.is_on else (60, 60, 60)
        pygame.draw.rect(surface, bg_color, (self.x, self.y, self.width, self.height))
        
        # Draw border
        border_color = (100, 100, 100)
        pygame.draw.rect(surface, border_color, (self.x, self.y, self.width, self.height), 2)
        
        # Draw light indicator (circular)
        light_radius = min(8, self.height // 3)
        light_x = self.x + light_radius + 5
        light_y = self.y + self.height // 2
        
        if self.is_on:
            # Bright light color when on
            pygame.draw.circle(surface, self.light_color, (light_x, light_y), light_radius)
            # Add glow effect
            glow_color = tuple(min(255, c + 50) for c in self.light_color)
            pygame.draw.circle(surface, glow_color, (light_x, light_y), light_radius + 2, 2)
        else:
            # Dim color when off
            dim_color = tuple(c // 4 for c in self.light_color)
            pygame.draw.circle(surface, dim_color, (light_x, light_y), light_radius)
        
        # Draw label if provided
        if self.label:
            font = self.get_inherited_font()
            text_color = self.get_inherited_text_color()
            text_surface = font.render(self.label, True, text_color)
            
            text_x = light_x + light_radius + 8
            text_y = self.y + (self.height - text_surface.get_height()) // 2
            
            surface.blit(text_surface, (text_x, text_y))


# Enhanced RootContainer with timer support
class EnhancedRootContainer(RootContainer):
    """Root container with built-in timer update support."""
    
    def __init__(self, width: int = 1920, height: int = 1080):
        super().__init__(width, height)
        self.last_update_time = pygame.time.get_ticks()
    
    def update_timers(self, widget: Widget, delta_ms: int):
        """Recursively update all timer-enabled widgets."""
        if hasattr(widget, 'update'):
            widget.update(delta_ms)
        
        for child in widget.children:
            self.update_timers(child, delta_ms)
    
    def main_loop(self):
        """Enhanced main loop with timer updates."""
        while self.running:
            current_time = pygame.time.get_ticks()
            delta_ms = current_time - self.last_update_time
            self.last_update_time = current_time
            
            # Handle events
            for event in pygame.event.get():
                self.handle_event(event)
            
            # Update all timers
            self.update_timers(self, delta_ms)
            
            # Render
            self.render(self.surface)
            pygame.display.flip()
            
            # Control frame rate
            self.clock.tick(60)
        
        pygame.quit()


class VerticalFlowContainer(FlowContainer):
    """Container that arranges children vertically."""
    
    def __init__(self, spacing: int = 5, parent: Optional[Widget] = None):
        super().__init__("vertical", spacing, parent)


class HorizontalFlowContainer(FlowContainer):
    """Container that arranges children horizontally."""
    
    def __init__(self, spacing: int = 5, parent: Optional[Widget] = None):
        super().__init__("horizontal", spacing, parent)


# Demo harness for testing UI components
if __name__ == "__main__":
    # Create enhanced root container
    root = EnhancedRootContainer(800, 600)
    
    # Create a proper layout container instead of dumping everything in root
    main_layout = VerticalFlowContainer(spacing=15, parent=root)
    main_layout.set_bounds(0, 0, 800, 600)
    
    # Header section
    status_label = Label("AIRSHIP ZERO - SYSTEM STATUS", main_layout)
    status_label.text_align = "center"
    
    # Create a horizontal container for the warning lights
    lights_container = HorizontalFlowContainer(spacing=20, parent=main_layout)
    
    # Create warning lights in the horizontal container
    engine_warning = BlinkenLight("ENGINE", 300, (255, 100, 0), lights_container)  # Orange, fast blink
    fuel_warning = BlinkenLight("LOW FUEL", 800, (255, 50, 50), lights_container)  # Red, slow blink  
    battery_ok = BlinkenLight("BATTERY", 0, (50, 255, 50), lights_container)  # Green, solid
    battery_ok.set_solid_on()
    
    # Start main loop
    root.main_loop()
