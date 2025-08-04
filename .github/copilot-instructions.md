# Airship Zero - Project Structure & Guidelines

## Project Overview

Airship Zero is a retro-inspired airship simulation game built with Python and Pygame. The game features a steampunk aesthetic with a brutally simple 320x320 pixel UI system that scales to any window size while maintaining pixel-perfect rendering.

## Architecture

### Core Design Principles

- **Fixed Logical Resolution**: Everything is designed for 320x320 pixels, then scaled
- **Scene-Based Architecture**: Each major game area is a separate scene
- **Centralized Simulation**: Single `core_simulator.py` manages all game state
- **No Anti-aliasing on Final Scale**: Fonts use anti-aliasing, but final scaling is pixel-perfect
- **Retro Aesthetics**: Pixelify Sans font, low-resolution graphics, steam-punk color palette

### File Structure

```
/
├── main.py                 # Application entry point and scene management
├── core_simulator.py       # Centralized game state and physics simulation
├── scene_main_menu.py      # Main menu and game start
├── scene_bridge.py         # Primary flight interface
├── scene_engine_room.py    # Engine controls and monitoring
├── scene_navigation.py     # World map and navigation
├── assets/
│   ├── fonts/              # Pixelify Sans font files
│   └── png/                # World map and other images
├── tests/                  # Test files
├── pyproject.toml         # UV project configuration
├── uv.lock               # Locked dependencies
└── run.sh                # Quick launch script
```

## Scene System

### Scene Responsibilities

Each scene is self-contained and handles:
- **Event Handling**: Keyboard, mouse, and focus management
- **Widget Management**: Buttons, labels, sliders, text boxes
- **Rendering**: Drawing UI elements to the logical 320x320 surface
- **State Updates**: Synchronizing with the central simulator

### Widget System

All scenes use a consistent widget system:
- **Buttons**: Clickable controls with focus states
- **Labels**: Read-only text displays
- **Sliders**: Value adjustment controls
- **Text Boxes**: Text input with cursor

Widget Properties:
```python
{
    "id": "unique_identifier",
    "type": "button|label|slider|textbox",
    "position": [x, y],
    "size": [width, height],
    "text": "display_text",
    "focused": True/False,
    "enabled": True/False  # Optional
}
```

### Scene Transitions

Scenes communicate through return values:
- `"scene_bridge"` → Switch to bridge
- `"scene_engine_room"` → Switch to engine room
- `"scene_navigation"` → Switch to navigation
- `"scene_main_menu"` → Return to main menu
- `"new_game"` → Start new game (handled by main.py)
- `"quit"` → Exit application
- `None` → No action

## Simulation System

### Core Simulator (`core_simulator.py`)

The simulator is a singleton that manages:
- **Navigation State**: Position, heading, speed, altitude
- **Engine State**: Boiler pressure, temperature, fuel levels
- **Game State**: Running status, time tracking

Access Pattern:
```python
from core_simulator import get_simulator
simulator = get_simulator()
state = simulator.get_state()
```

### State Structure

```python
{
    "navigation": {
        "position": {"latitude": float, "longitude": float, "altitude": float, "heading": float},
        "motion": {"groundSpeed": float, "verticalSpeed": float, "angularVelocity": float}
    },
    "engines": {
        "boiler": {"pressure": float, "temperature": float, "fuelLevel": float, "waterLevel": float},
        "throttle": float,
        "efficiency": float
    },
    "time": {"gameTime": float, "realTime": float}
}
```

## Rendering System

### Coordinate System

- **Logical Coordinates**: Always 320x320 pixels
- **Screen Coordinates**: Variable window size, automatically scaled
- **Conversion**: `main.py` handles screen→logical coordinate conversion

### Font Rendering

- **Primary Font**: Pixelify Sans (bitmap-style)
- **Anti-aliasing**: Use `True` for font.render() calls
- **No Final AA**: Scaling uses nearest-neighbor (pixel-perfect)

### Color Palette

```python
BACKGROUND_COLOR = (20, 20, 30)      # Dark blue-grey
TEXT_COLOR = (255, 255, 255)         # White
FOCUS_COLOR = (255, 200, 50)         # Golden highlight
BUTTON_COLOR = (60, 60, 80)          # Button background
BUTTON_FOCUSED_COLOR = (80, 80, 120) # Focused button
WARNING_COLOR = (255, 100, 100)      # Red warning
CAUTION_COLOR = (255, 200, 100)      # Yellow caution
GOOD_COLOR = (100, 255, 100)         # Green good
```

## Navigation Scene Features

### Map System

- **World Map**: 640x320 pixel image showing Earth
- **Zoom Levels**: 0.25x to 4.0x zoom range
- **Panning**: Click and drag to pan the view
- **Position Tracking**: Red indicator shows current airship position

### Controls

- **Mouse**: Click and drag to pan map
- **Keyboard**: 
  - `+/-` keys for zoom
  - Arrow keys for panning
  - `C` to center on position
  - `Esc` to return to bridge
  - `Tab/Shift+Tab` for widget focus cycling

## Development Guidelines

### Code Style

- **Docstrings**: Use clear docstrings for all methods
- **Type Hints**: Use Optional, List, Dict imports from typing
- **Constants**: Define colors and sizes as module-level constants
- **Error Handling**: Graceful fallbacks for missing assets

### Focus Management

- **Consistent Controls**: Only `Tab` and `Shift+Tab` cycle widget focus across all scenes
- **Arrow Keys**: Reserved for scene-specific functionality (navigation panning, etc.)
- **Scene-Specific**: Each scene can define its own arrow key behavior without conflicts

### Event Handling Pattern

```python
def handle_event(self, event) -> Optional[str]:
    if event.type == pygame.KEYDOWN:
        # Handle keyboard
    elif event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Left click
            logical_pos = event.pos  # Already converted by main.py
            clicked_widget = self._get_widget_at_pos(logical_pos)
            if clicked_widget is not None:
                self._set_focus(clicked_widget)
                return self._activate_focused()
    return None
```

### Widget Click Detection

**Critical**: Use `if clicked_widget is not None:` instead of `if clicked_widget:` because widget index 0 is falsy but valid.

### Asset Loading

- **Graceful Fallbacks**: Always provide fallbacks for missing assets
- **Path Handling**: Use relative paths from project root
- **Error Messages**: Clear console output for debugging

## Testing

### Manual Testing

- **Scene Transitions**: Verify all navigation works
- **Widget Focus**: Tab through all controls
- **Mouse Interaction**: Click all buttons and draggable areas
- **Edge Cases**: Test zoom limits, map boundaries

### Launch

```bash
# Quick development launch
./run.sh

# Direct launch
uv run python main.py
```

## Common Patterns

### Adding New Widgets

1. Add to `_init_widgets()` method
2. Update `_get_widget_at_pos()` if needed
3. Handle in `_activate_focused()` if interactive
4. Add rendering in `_render_widget()`

### Adding New Scenes

1. Create new scene file following existing pattern
2. Import in `main.py`
3. Add to `_init_scenes()` in main.py
4. Add transition handling in `_transition_to_scene()`

### Simulator Integration

1. Get state: `game_state = self.simulator.get_state()`
2. Update displays in scene's `update()` method
3. Send commands via simulator methods
4. Handle state changes in real-time

## Known Issues & Limitations

- **World Map**: Placeholder map included, high-res version needed
- **Sound**: No audio system currently
- **Animations**: Static UI, no smooth transitions

## Save System

### Auto-Save Features

- **Game saves automatically** when returning to main menu via Escape
- **Game saves automatically** on application exit
- **Single save slot** system for simplicity
- **Resume button** automatically enabled when save file exists

### Save File

- **Location**: `saved_game.json` in project root
- **Format**: JSON with complete game state
- **Persistence**: Survives application restarts
- **Validation**: Automatic format checking on load

## Future Enhancements

- **Weather System**: Wind, storms affecting navigation
- **Cargo Management**: Loading, delivery missions
- **Multiplayer**: Network support for multiple airships
- **Advanced Navigation**: Waypoint system, autopilot
