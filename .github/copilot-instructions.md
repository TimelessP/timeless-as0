# Airship Zero - GitHub Copilot Instructions

## Project Overview
**Airship Zero** is a Python-based UI application using Pygame for rendering, built with a robust widget architecture and comprehensive test coverage. The project implements a steampunk airship control interface with proper layout management and TDD methodology.

## 🏗️ Project Structure

```
/home/t/PycharmProjects/airshipzero-challenge/timelessp-as0/
├── ui_foundation.py          # Core UI architecture with widgets and layout
├── main.py                   # Application entry point
├── tests/
│   ├── __init__.py
│   └── test_ui_foundation.py # Comprehensive test suite
├── assets/
│   └── books/               # Documentation and journals
│       └── journal.md       # Consciousness documentation
├── run.sh                   # Development launcher script
├── test.sh                  # Automated testing with coverage
├── pyproject.toml           # UV package management
├── uv.lock                  # Dependency lock file
└── .github/
    └── copilot-instructions.md # This file
```

## 🚀 Quick Start Commands

### Development Workflow
```bash
# Run the application
./run.sh

# Run tests with coverage
./test.sh

# Run specific test class
uv run pytest tests/test_ui_foundation.py::TestBlinkenLight -v

# Check coverage in browser
firefox htmlcov/index.html
```

### Git Workflow
```bash
# Standard development cycle
git add .
git commit -m "✨ Feature: Description with emoji"
git status
```

## 🧱 Core Architecture

### Widget Hierarchy
- **Widget (ABC)**: Base class with layout, rendering, and input handling
- **RootContainer**: Singleton managing pygame surface and events
- **FlowContainer**: Base layout container with vertical/horizontal flow
  - **VerticalFlowContainer**: Arranges children top-to-bottom
  - **HorizontalFlowContainer**: Arranges children left-to-right
- **BlinkenLight**: Aviation warning light widget with blinking animations
- **Label**: Simple text rendering widget
- **Timer**: Non-visual timer component for animations

### Key Design Patterns
1. **Recursive Layout**: Containers call `child.layout_children()` after positioning
2. **Dirty Flag System**: `layout_dirty` prevents unnecessary recalculation
3. **Property Inheritance**: Font, colors cascade from parent to child
4. **Modal Input Handling**: InputMode enum for different interface contexts

## 📝 Coding Conventions

### Python Style
- **Type Hints**: Always use typing annotations
- **Docstrings**: Class and method documentation required
- **Abstract Methods**: Use ABC for base classes requiring implementation
- **Error Handling**: Graceful fallbacks for font loading, measurements

### Widget Implementation
```python
class MyWidget(Widget):
    def __init__(self, parent: Optional[Widget] = None):
        super().__init__(parent)
        # Initialize properties
    
    def layout_children(self):
        """Layout child widgets within bounds."""
        # Implementation required
    
    def render(self, surface: pygame.Surface):
        """Render widget to surface."""
        if not self.visible:
            return
        # Rendering logic
```

### Testing Standards
- **Test Classes**: Group tests by widget type (`TestBlinkenLight`, `TestFlowContainer`)
- **Setup Methods**: Reset `RootContainer._instance = None` before each test
- **Mock Usage**: Mock pygame components for unit testing
- **Edge Cases**: Include `TestWindowSizing` for constraint scenarios
- **Coverage Goal**: Maintain high code coverage

## 🔧 Technical Details

### Layout System
- **FlowContainer Architecture**: Proper parent-child positioning
- **Preferred Size Calculation**: Uses `get_content_size()` when available
- **Flexible Children**: Widgets without explicit content size get extra space
- **Recursive Processing**: Layout propagates through entire widget tree

### BlinkenLight Specifics
- **Minimum Sizing**: Always ≥24px height, width calculated from LED + text
- **Component Layout**: LED margin(5) + diameter(16) + spacing(8) + text + padding
- **Timer Integration**: Internal timer for blinking with proper lifecycle
- **Solid Modes**: `set_solid_on()`, `set_solid_off()`, `set_blinking(bool)`

### Common Patterns
```python
# Widget bounds setting with dirty flag
widget.set_bounds(x, y, width, height)

# Layout with recursive children
def layout_children(self):
    for child in self.children:
        child.set_bounds(...)
        child.layout_children()  # Critical!

# Content size with font fallbacks
def get_content_size(self) -> Tuple[int, int]:
    try:
        return self.measure_text(self.text)
    except:
        return (len(self.text) * 8, 18)  # Fallback
```

## 🧪 Testing Guidelines

### Test Structure
```python
class TestMyWidget:
    def setup_method(self):
        """Reset singleton state."""
        RootContainer._instance = None
    
    def test_widget_feature(self):
        """Test specific functionality."""
        # Arrange
        widget = MyWidget()
        
        # Act
        result = widget.some_method()
        
        # Assert
        assert result == expected_value
```

### Mock Patterns
```python
# Mock pygame font for text measurement
with patch('pygame.font.Font') as mock_font:
    mock_font_instance = Mock()
    mock_font.return_value = mock_font_instance
    mock_font_instance.size.return_value = (width, height)
```

## 🎯 Current Development Focus

### Completed Features ✅
- FlowContainer layout architecture with recursive positioning
- BlinkenLight widget with proper sizing and animations
- Comprehensive test suite with high coverage
- Development automation (run.sh, test.sh)
- Layout dirty flag system with cascading updates

### Known Technical Debt
- Font loading fallbacks could be more robust
- ScrollContainer not yet implemented for overflow handling
- Input focus management needs expansion
- Advanced layout features (margins, alignment) planned

## 🚨 Critical Patterns to Remember

### Layout Bug Prevention
Always call `child.layout_children()` after `child.set_bounds()` in container layouts:
```python
child.set_bounds(x, y, width, height)
child.layout_children()  # Without this, nested containers won't layout!
```

### Test Isolation
Reset RootContainer singleton in test setup:
```python
def setup_method(self):
    RootContainer._instance = None
```

### Size Calculation Robustness
Handle font measurement failures gracefully:
```python
try:
    text_width, text_height = self.measure_text(self.label)
except:
    text_width = len(self.label) * 8  # Fallback estimation
    text_height = 18
```

## 📊 Quality Metrics
- **Test Coverage**: High coverage maintained
- **Code Quality**: Type hints, docstrings, error handling
- **Architecture**: Clean separation, recursive layout, proper inheritance

## 🎨 UI Philosophy
- **Aviation Aesthetics**: Dark backgrounds, warning lights, clear typography
- **Responsive Layout**: Handles window resizing and constraint scenarios
- **Performance**: Dirty flags prevent unnecessary recalculation
- **Accessibility**: Clear visual hierarchy, proper minimum sizes

---

*This document reflects the collaborative development methodology between human creativity and AI engineering precision.*
