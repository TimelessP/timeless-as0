"""
Tests for the UI foundation widget system.
"""

import pytest
import pygame
from unittest.mock import Mock, patch
import os
import sys

# Add parent directory to path so we can import ui_foundation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui_foundation import (
    Widget, RootContainer, Label, Timer, BlinkenLight, InputMode, 
    FlowContainer, VerticalFlowContainer, HorizontalFlowContainer
)


class TestWidget:
    """Test the base Widget class functionality."""
    
    def setup_method(self):
        """Reset any singleton state before each test."""
        RootContainer._instance = None
    
    def test_widget_parent_child_relationship(self):
        """Test that parent-child relationships work correctly."""
        # Create a mock widget class for testing
        class MockWidget(Widget):
            def layout_children(self):
                pass
            def render(self, surface):
                pass
        
        parent = MockWidget()
        child = MockWidget(parent)
        
        assert child.parent == parent
        assert child in parent.children
        assert len(parent.children) == 1
    
    def test_widget_inheritance_chain(self):
        """Test property inheritance through widget hierarchy."""
        # We need to mock pygame.font to avoid initialization issues
        with patch('pygame.font.Font') as mock_font:
            mock_font_instance = Mock()
            mock_font.return_value = mock_font_instance
            mock_font_instance.size.return_value = (100, 20)
            
            class MockWidget(Widget):
                def layout_children(self):
                    pass
                def render(self, surface):
                    pass
            
            # Create root with specific styling
            root = MockWidget()
            root.font = mock_font_instance
            root.text_color = (255, 255, 255)
            root.bg_color = (50, 50, 50)
            
            # Create child without explicit styling
            child = MockWidget(root)
            
            # Child should inherit parent's properties
            assert child.get_inherited_font() == mock_font_instance
            assert child.get_inherited_text_color() == (255, 255, 255)
            assert child.get_inherited_bg_color() == (50, 50, 50)
    
    def test_widget_bounds_and_layout(self):
        """Test widget bounds setting and layout triggering."""
        class MockWidget(Widget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.layout_called = False
            
            def layout_children(self):
                self.layout_called = True
            
            def render(self, surface):
                pass
        
        widget = MockWidget()
        widget.set_bounds(10, 20, 100, 50)
        
        assert widget.x == 10
        assert widget.y == 20
        assert widget.width == 100
        assert widget.height == 50
        assert widget.layout_dirty is True  # Should be marked dirty
    
    def test_widget_layout_dirty_propagation(self):
        """Test that layout dirty flags propagate to children."""
        class MockWidget(Widget):
            def layout_children(self):
                pass
            def render(self, surface):
                pass
        
        parent = MockWidget()
        child1 = MockWidget(parent)
        child2 = MockWidget(parent)
        
        # Clear dirty flags
        parent.layout_dirty = False
        child1.layout_dirty = False
        child2.layout_dirty = False
        
        # Mark parent dirty - should cascade to children
        parent.mark_layout_dirty()
        
        assert parent.layout_dirty is True
        assert child1.layout_dirty is True
        assert child2.layout_dirty is True
    
    def test_widget_ensure_layout(self):
        """Test that ensure_layout only calls layout_children when dirty."""
        class MockWidget(Widget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.layout_call_count = 0
            
            def layout_children(self):
                self.layout_call_count += 1
            
            def render(self, surface):
                pass
        
        widget = MockWidget()
        widget.layout_dirty = True
        
        # First call should trigger layout
        widget.ensure_layout()
        assert widget.layout_call_count == 1
        assert widget.layout_dirty is False
        
        # Second call should not trigger layout (not dirty)
        widget.ensure_layout()
        assert widget.layout_call_count == 1


class TestLabel:
    """Test the Label widget."""
    
    def setup_method(self):
        """Reset singleton state."""
        RootContainer._instance = None
    
    def test_label_creation(self):
        """Test basic label creation and properties."""
        label = Label("Test Text")
        assert label.text == "Test Text"
        assert label.text_align == "left"
    
    def test_label_content_size(self):
        """Test label content size calculation."""
        with patch('pygame.font.Font') as mock_font:
            mock_font_instance = Mock()
            mock_font.return_value = mock_font_instance
            mock_font_instance.size.return_value = (80, 16)
            
            label = Label("Test")
            label.font = mock_font_instance
            
            width, height = label.get_content_size()
            assert width == 80
            assert height == 16


class TestTimer:
    """Test the Timer widget."""
    
    def test_timer_creation_and_callback(self):
        """Test timer creation and callback execution."""
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        timer = Timer(1000, test_callback, repeat=False)
        assert timer.duration_ms == 1000
        assert timer.active is True
        assert callback_called is False
        
        # Simulate time passing
        timer.update(500)
        assert callback_called is False  # Not enough time passed
        
        timer.update(500)
        assert callback_called is True  # Callback should be called
        assert timer.active is False  # Non-repeating timer should stop
    
    def test_timer_repeat(self):
        """Test repeating timer functionality."""
        call_count = 0
        
        def test_callback():
            nonlocal call_count
            call_count += 1
        
        timer = Timer(100, test_callback, repeat=True)
        
        # First trigger
        timer.update(100)
        assert call_count == 1
        assert timer.active is True
        
        # Second trigger
        timer.update(100)
        assert call_count == 2
        assert timer.active is True


@pytest.mark.ui
class TestBlinkenLight:
    """Test the BlinkenLight widget."""
    
    def test_blinkenlight_creation(self):
        """Test BlinkenLight creation and initial state."""
        light = BlinkenLight("ENGINE", 500, (255, 100, 0))
        assert light.label == "ENGINE"
        assert light.blink_rate_ms == 500
        assert light.light_color == (255, 100, 0)
        assert light.is_on is True
        assert light.blinking is True
    
    def test_blinkenlight_toggle_behavior(self):
        """Test blinking behavior."""
        light = BlinkenLight("TEST", 200, (255, 0, 0))
        
        initial_state = light.is_on
        light._toggle_light()
        assert light.is_on != initial_state
        
        # Toggle again
        light._toggle_light()
        assert light.is_on == initial_state
    
    def test_blinkenlight_solid_modes(self):
        """Test solid on/off modes."""
        light = BlinkenLight("TEST", 200, (255, 0, 0))
        
        light.set_solid_on()
        assert light.blinking is False
        assert light.is_on is True
        
        light.set_solid_off()
        assert light.blinking is False
        assert light.is_on is False
    
    def test_blinkenlight_minimum_size_calculation(self):
        """Test that BlinkenLight calculates proper minimum dimensions."""
        # Test with no label
        light_no_label = BlinkenLight("", 500, (255, 0, 0))
        width, height = light_no_label.get_content_size()
        
        # Should have minimum width for LED + margins, minimum height of 24px
        assert width >= 20  # LED margin + diameter + padding
        assert height >= 24  # Minimum height
        
        # Test with label
        with patch('ui_foundation.Widget.measure_text') as mock_measure:
            mock_measure.return_value = (50, 16)  # 50px wide, 16px tall text
            
            light_with_label = BlinkenLight("ENGINE", 500, (255, 100, 0))
            width, height = light_with_label.get_content_size()
            
            # Width should include LED + spacing + text width + padding
            # 5 (margin) + 16 (LED diameter) + 8 (spacing) + 50 (text) + 4 (padding) = 83
            assert width >= 80  # Should be around 83
            
            # Height should be max of LED height (22) or text height (24) or minimum (24)
            assert height >= 24
    
    def test_blinkenlight_content_size_recalculation(self):
        """Test that get_content_size recalculates dimensions dynamically."""
        light = BlinkenLight("TEST", 500, (255, 0, 0))
        
        # Mock the measure_text method to return different values
        with patch.object(light, 'measure_text') as mock_measure:
            # First measurement
            mock_measure.return_value = (30, 14)
            size1 = light.get_content_size()
            
            # Second measurement with different text size
            mock_measure.return_value = (60, 18)
            size2 = light.get_content_size()
            
            # Sizes should be different (recalculated)
            assert size1 != size2
            assert size2[0] > size1[0]  # Width should be larger


class TestFlowContainer:
    """Test the FlowContainer layout system."""
    
    def setup_method(self):
        """Reset singleton state."""
        RootContainer._instance = None
    
    def test_vertical_flow_container_creation(self):
        """Test VerticalFlowContainer basic creation."""
        container = VerticalFlowContainer(spacing=10)
        assert container.direction == "vertical"
        assert container.spacing == 10
        assert container.padding == 10
    
    def test_horizontal_flow_container_creation(self):
        """Test HorizontalFlowContainer basic creation."""
        container = HorizontalFlowContainer(spacing=15)
        assert container.direction == "horizontal"
        assert container.spacing == 15
        assert container.padding == 10
    
    def test_child_preferred_size_calculation(self):
        """Test that FlowContainer calculates child preferred sizes correctly."""
        container = VerticalFlowContainer()
        
        # Create a mock child with get_content_size
        class MockChild(Widget):
            def __init__(self):
                super().__init__()
                self.min_width = 20
                self.min_height = 15
                self.padding = 4
            
            def get_content_size(self):
                return (40, 25)
            
            def layout_children(self):
                pass
            
            def render(self, surface):
                pass
        
        child = MockChild()
        pref_w, pref_h = container.get_child_preferred_size(child)
        
        # Should be max of (content_size + padding*2) or min_size
        # Content: 40x25, padding: 4*2=8, so 48x33
        # Min: 20x15
        # Result should be max(48,20) x max(33,15) = 48x33
        assert pref_w == 48
        assert pref_h == 33
    
    def test_vertical_layout_positioning(self):
        """Test that vertical flow container positions children correctly."""
        container = VerticalFlowContainer(spacing=5)
        container.set_bounds(0, 0, 200, 300)
        
        # Create mock children
        class MockChild(Widget):
            def __init__(self, content_size):
                super().__init__()
                self._content_size = content_size
                self.padding = 2
            
            def get_content_size(self):
                return self._content_size
            
            def layout_children(self):
                pass
            
            def render(self, surface):
                pass
        
        child1 = MockChild((50, 30))
        child2 = MockChild((60, 40))
        child3 = MockChild((40, 20))
        
        container.add_child(child1)
        container.add_child(child2)
        container.add_child(child3)
        
        container.layout_children()
        
        # Check that children are positioned vertically with proper spacing
        assert child1.y == 10  # container padding
        assert child2.y > child1.y + child1.height  # Below first child
        assert child3.y > child2.y + child2.height  # Below second child
        
        # All children should span the full width (minus padding)
        expected_width = 200 - (10 * 2)  # Container width minus padding
        assert child1.width == expected_width
        assert child2.width == expected_width
        assert child3.width == expected_width
    
    def test_horizontal_layout_positioning(self):
        """Test that horizontal flow container positions children correctly."""
        container = HorizontalFlowContainer(spacing=10)
        container.set_bounds(0, 0, 400, 100)
        
        # Create mock children
        class MockChild(Widget):
            def __init__(self, content_size):
                super().__init__()
                self._content_size = content_size
                self.padding = 2
            
            def get_content_size(self):
                return self._content_size
            
            def layout_children(self):
                pass
            
            def render(self, surface):
                pass
        
        child1 = MockChild((50, 30))
        child2 = MockChild((60, 25))
        
        container.add_child(child1)
        container.add_child(child2)
        
        container.layout_children()
        
        # Check that children are positioned horizontally
        assert child1.x == 10  # container padding
        assert child2.x > child1.x + child1.width  # To the right of first child
        
        # All children should span the full height (minus padding)
        expected_height = 100 - (10 * 2)  # Container height minus padding
        assert child1.height == expected_height
        assert child2.height == expected_height
    
    def test_layout_with_invisible_children(self):
        """Test that invisible children are ignored in layout."""
        container = VerticalFlowContainer()
        container.set_bounds(0, 0, 200, 200)
        
        class MockChild(Widget):
            def __init__(self, content_size, visible=True):
                super().__init__()
                self._content_size = content_size
                self.visible = visible
                self.padding = 2
            
            def get_content_size(self):
                return self._content_size
            
            def layout_children(self):
                pass
            
            def render(self, surface):
                pass
        
        child1 = MockChild((50, 30), visible=True)
        child2 = MockChild((60, 40), visible=False)  # Invisible
        child3 = MockChild((40, 20), visible=True)
        
        container.add_child(child1)
        container.add_child(child2)
        container.add_child(child3)
        
        container.layout_children()
        
        # Child2 should not affect layout
        # Child3 should be positioned right after child1
        assert child1.y == 10  # padding
        expected_child3_y = child1.y + child1.height + container.spacing
        assert child3.y == expected_child3_y


class TestWindowSizing:
    """Test layout behavior with various window sizes and edge cases."""
    
    def setup_method(self):
        """Reset singleton state."""
        RootContainer._instance = None
    
    def test_vertical_container_in_small_window(self):
        """Test vertical flow container behavior in a very small window."""
        # Simulate a tiny window - mobile phone size
        container = VerticalFlowContainer(spacing=5)
        container.set_bounds(0, 0, 320, 200)  # Very small
        
        class MockChild(Widget):
            def __init__(self, content_size):
                super().__init__()
                self._content_size = content_size
                self.padding = 2
            
            def get_content_size(self):
                return self._content_size
            
            def layout_children(self):
                pass
            
            def render(self, surface):
                pass
        
        # Add children that would normally fit comfortably
        child1 = MockChild((100, 30))  # Normal size
        child2 = MockChild((150, 25))  # Wider than window!
        child3 = MockChild((80, 20))   # Normal size
        
        container.add_child(child1)
        container.add_child(child2)
        container.add_child(child3)
        
        container.layout_children()
        
        # All children should be constrained to available width
        available_width = 320 - (10 * 2)  # Container width minus padding
        assert child1.width == available_width
        assert child2.width == available_width  # Constrained, not 150!
        assert child3.width == available_width
        
        # Children should still be positioned vertically
        assert child1.y == 10  # padding
        assert child2.y > child1.y
        assert child3.y > child2.y
    
    def test_horizontal_container_in_narrow_window(self):
        """Test horizontal flow container with insufficient width."""
        # Very narrow window
        container = HorizontalFlowContainer(spacing=10)
        container.set_bounds(0, 0, 150, 400)  # Narrow but tall
        
        class MockChild(Widget):
            def __init__(self, content_size):
                super().__init__()
                self._content_size = content_size
                self.padding = 2
            
            def get_content_size(self):
                return self._content_size
            
            def layout_children(self):
                pass
            
            def render(self, surface):
                pass
        
        # Add children that require more width than available
        child1 = MockChild((60, 30))
        child2 = MockChild((70, 25))
        child3 = MockChild((50, 35))
        
        container.add_child(child1)
        container.add_child(child2)
        container.add_child(child3)
        
        container.layout_children()
        
        # Children should be positioned horizontally even in tight space
        assert child1.x == 10  # padding
        assert child2.x > child1.x
        assert child3.x > child2.x
        
        # All children should span full height
        available_height = 400 - (10 * 2)  # Container height minus padding
        assert child1.height == available_height
        assert child2.height == available_height
        assert child3.height == available_height
    
    def test_blinkenlight_minimum_height_enforcement(self):
        """Test that BlinkenLights maintain minimum height even in cramped containers."""
        # Create a very short container
        container = VerticalFlowContainer(spacing=2)
        container.set_bounds(0, 0, 200, 60)  # Very short height
        
        # Add BlinkenLights that should maintain minimum height
        engine_light = BlinkenLight("ENGINE", 500, (255, 100, 0))
        fuel_light = BlinkenLight("LOW FUEL WARNING", 800, (255, 50, 50))  # Long text
        
        container.add_child(engine_light)
        container.add_child(fuel_light)
        
        container.layout_children()
        
        # Both lights should maintain at least 24px height
        assert engine_light.height >= 24
        assert fuel_light.height >= 24
        
        # Lights should not overlap vertically
        assert fuel_light.y >= engine_light.y + engine_light.height
    
    def test_blinkenlight_width_calculation_with_long_text(self):
        """Test BlinkenLight width calculation with various text lengths."""
        # Test with progressively longer labels
        test_cases = [
            ("", 0),  # No label
            ("OK", 2),  # Short
            ("ENGINE", 6),  # Medium
            ("LOW FUEL WARNING", 17),  # Long
            ("CRITICAL SYSTEM FAILURE DETECTED", 33),  # Very long
        ]
        
        for label, expected_chars in test_cases:
            light = BlinkenLight(label, 500, (255, 0, 0))
            width, height = light.get_content_size()
            
            # Width should account for LED + spacing + text
            # Minimum components: 5 (margin) + 16 (LED) + 8 (spacing) + 4 (padding) = 33
            min_width_without_text = 33
            
            if label:
                # Should be wider than minimum to accommodate text
                assert width > min_width_without_text
                # Should be roughly proportional to text length (with fallbacks)
                # This is a rough estimate - exact calculation depends on font
                assert width >= min_width_without_text + (expected_chars * 6)
            else:
                # No text, should be close to minimum
                assert width >= min_width_without_text
            
            # Height should always be at least 24px
            assert height >= 24
    
    def test_mixed_container_nesting_in_small_window(self):
        """Test nested containers (vertical + horizontal) in constrained space."""
        # Small window
        main_container = VerticalFlowContainer(spacing=5)
        main_container.set_bounds(0, 0, 300, 150)  # Small window
        
        # Create nested horizontal container
        lights_container = HorizontalFlowContainer(spacing=10)
        main_container.add_child(lights_container)
        
        # Add a label to the main container
        class MockLabel(Widget):
            def __init__(self, text):
                super().__init__()
                self.text = text
                self.padding = 2
            
            def get_content_size(self):
                return (len(self.text) * 8, 16)  # Rough text measurement
            
            def layout_children(self):
                pass
            
            def render(self, surface):
                pass
        
        header = MockLabel("SYSTEM STATUS")
        main_container.add_child(header)
        
        # Add BlinkenLights to the horizontal container
        engine_light = BlinkenLight("ENGINE", 300, (255, 100, 0))
        fuel_light = BlinkenLight("FUEL", 800, (255, 50, 50))
        
        lights_container.add_child(engine_light)
        lights_container.add_child(fuel_light)
        
        # Layout the entire hierarchy
        main_container.layout_children()
        
        # Verify the nested structure is positioned correctly
        # Children are positioned in order added: lights_container first, then header
        assert lights_container.y == 10  # Main container padding
        assert header.y > lights_container.y + lights_container.height  # Header comes after lights
        
        # Lights should be positioned horizontally within their container
        assert engine_light.x >= lights_container.x + lights_container.padding
        assert fuel_light.x > engine_light.x + engine_light.width
        
        # Everything should fit within the small window bounds
        assert header.x + header.width <= main_container.width
        assert lights_container.x + lights_container.width <= main_container.width
    
    def test_zero_sized_container_handling(self):
        """Test edge case of zero or negative sized containers."""
        # Zero-width container
        container = HorizontalFlowContainer()
        container.set_bounds(0, 0, 0, 100)  # Zero width
        
        child = BlinkenLight("TEST", 500, (255, 0, 0))
        container.add_child(child)
        
        # Should not crash, child should get minimal space
        container.layout_children()
        
        # Child width should be constrained but not negative
        assert child.width >= 0
        
        # Zero-height container
        container2 = VerticalFlowContainer()
        container2.set_bounds(0, 0, 200, 0)  # Zero height
        
        child2 = BlinkenLight("TEST2", 500, (255, 0, 0))
        container2.add_child(child2)
        
        # Should not crash
        container2.layout_children()
        
        # Child height should be constrained but not negative
        assert child2.height >= 0


if __name__ == "__main__":
    pytest.main([__file__])
