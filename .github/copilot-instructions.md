# Airship Zero - Project Structure & Guidelines

## Project Overview

Airship Zero is a retro-inspired airship simulation game built with Python and Pygame. The game features a steampunk aesthetic with a brutally simple 320x320 pixel UI system that scales to any window size while maintaining pixel-perfect rendering.

**GitHub Repository**: https://github.com/TimelessP/timeless-as0

## Architecture

### Core Design Principles

- **Fixed Logical Resolution**: Everything is designed for 320x320 pixels, then scaled
- **Scene-Based Architecture**: Each major game area is a separate scene
- **Centralized Simulation**: Single `core_simulator.py` manages all game state and physics
- **No Anti-aliasing on Final Scale**: Fonts use anti-aliasing, but final scaling is pixel-perfect
- **Retro Aesthetics**: Pixelify Sans font, low-resolution graphics, steam-punk color palette
- **UV Package Management**: All dependencies managed via UV, requires virtual environment

### File Structure

```
/
├── main.py                    # Application entry point and scene management
├── core_simulator.py          # Centralized game state and physics simulation
├── scene_main_menu.py         # Main menu and game start
├── scene_bridge.py            # Primary flight interface and autopilot
├── scene_engine_room.py       # Engine controls and monitoring
├── scene_navigation.py        # World map and navigation
├── scene_fuel.py              # Fuel system management
├── scene_cargo.py             # Physics-based cargo management mini-game
├── scene_communications.py    # Radio and communications
├── scene_camera.py            # External view camera
├── scene_crew.py              # Crew management
├── scene_missions.py          # Mission system
├── assets/
│   ├── fonts/                 # Pixelify Sans and other font files
│   ├── png/                   # World map and other images
│   └── books/                 # In-game documentation and manuals (Markdown)
├── tests/                     # Test files (pytest structure)
├── .venv/                     # Virtual environment (UV managed)
├── pyproject.toml            # UV project configuration
├── uv.lock                   # Locked dependencies
├── run.sh                    # Quick launch script
└── saved_game.json           # Auto-save game state
```

## Scene System

### Complete Scene Inventory

The game uses a modular scene-based architecture with the following scenes:

- **`scene_main_menu.py`**: Game startup, save/load, settings
- **`scene_bridge.py`**: Primary flight interface, autopilot controls, critical instruments
- **`scene_engine_room.py`**: Engine management, temperature, RPM, manifold pressure
- **`scene_navigation.py`**: World map with zoom/pan, position tracking, waypoints
- **`scene_fuel.py`**: Fuel system management, tank levels, pump controls, transfers
- **`scene_cargo.py`**: Physics-based cargo management with winch mechanics
- **`scene_communications.py`**: Radio communications, messaging
- **`scene_camera.py`**: External view camera system
- **`scene_crew.py`**: Crew management and assignments
- **`scene_missions.py`**: Mission system and objectives

### Scene Responsibilities

Each scene is self-contained and handles:
- **Event Handling**: Keyboard, mouse, and focus management
- **Widget Management**: Buttons, labels, sliders, text boxes
- **Rendering**: Drawing UI elements to the logical 320x320 surface
- **State Updates**: Synchronizing with the central simulator
- **Scene-Specific Logic**: Mini-games, specialized controls

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

The simulator is a singleton that manages ALL game state and physics:
- **Navigation State**: Position, heading, speed, altitude, autopilot
- **Engine State**: Boiler pressure, temperature, fuel levels, RPM, manifold pressure
- **Fuel System**: Tank levels, pump states, transfers, engine feed
- **Cargo System**: Winch position, cable length, crate physics, placement
- **Game State**: Running status, time tracking, save/load
- **Environmental Systems**: Weather, electrical, monitoring

**CRITICAL**: All game data flows through `core_simulator.py`. Scenes do NOT maintain state - they only display and send commands to the simulator.

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
        "motion": {"indicatedAirspeed": float, "groundSpeed": float, "verticalSpeed": float, "angularVelocity": float}
    },
    "engine": {
        "running": bool, "rpm": float, "manifoldPressure": float, "fuelFlow": float,
        "controls": {"throttle": float, "mixture": float, "propeller": float}
    },
    "fuel": {
        "tanks": {"forward": {"level": float, "feed": bool}, "aft": {"level": float, "feed": bool}},
        "currentLevel": float, "totalCapacity": float
    },
    "cargo": {
        "winch": {"position": {"x": int, "y": int}, "cableLength": int, "attachedCrate": str},
        "cargoHold": [{"id": str, "type": str, "position": {"x": int, "y": int}}],
        "loadingBay": [...]
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

## Development Environment

### Python Environment Setup

**CRITICAL**: This project uses UV for Python package management. You MUST activate the virtual environment before any development work.

#### For Development (Local Clone)

```bash
# Quick development launch
./run.sh

# Manual environment activation (required for development)
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# Install dependencies (UV manages this automatically)
uv sync

# Run with UV (recommended for development)
uv run python main.py

# Direct launch (requires activated venv)
python main.py
```

#### For End Users (Direct Installation)

```bash
# Install and run directly from GitHub (once published)
uv tool run --from git+https://github.com/TimelessP/timeless-as0 airshipzero

# Or install as a tool for repeated use
uv tool install git+https://github.com/TimelessP/timeless-as0
airshipzero  # Run after installation
```

### Testing and Validation

```bash
# Run tests (when implemented)
uv run pytest

# Coverage testing
uv run pytest --cov=. --cov-report=html

# Launch game for manual testing (development)
uv run python main.py

# Launch game for manual testing (tool installation)
uv tool run --from git+https://github.com/TimelessP/timeless-as0 airshipzero
```

## Assets and Documentation

### In-Game Documentation

The `assets/books/` directory contains Markdown files that serve as in-game manuals and lore:

- **`user-manual-bridge.md`**: Bridge controls and autopilot
- **`user-manual-engine-room.md`**: Engine management procedures  
- **`user-manual-fuel.md`**: Fuel system operations
- **`user-manual-navigation.md`**: Navigation and map usage
- **`user-manual-cargo-system.md`**: Cargo winch and placement
- **`cargo-system-requirements.md`**: Technical cargo specifications
- **`dreaming-of-steam-and-copper.md`**: Game lore and backstory
- **`journal.md`**: In-character diary entries

These files are both documentation AND in-game content that players can read within the game world.

### Asset Structure

```
assets/
├── fonts/                     # Typography
│   ├── Pixelify_Sans/        # Primary game font (retro pixel style)
│   ├── Roboto_Condensed/     # Secondary font
│   └── Tiny5/                # Micro text font
├── png/                      # Images and graphics
│   └── world-map.png         # Navigation world map
└── books/                    # Markdown documentation (in-game readable)
    ├── user-manual-*.md      # System operation manuals
    └── *.md                  # Lore and story content
```

## Scene-Specific Features

### Navigation Scene
- **World Map**: 640x320 pixel image with zoom/pan capabilities (0.25x to 4.0x)
- **Position Tracking**: Real-time airship position display with red indicator
- **Controls**: Mouse drag to pan, +/- keys for zoom, C to center, arrow keys for manual pan

### Cargo Scene
- **Physics-Based Management**: Winch system with horizontal rail and cable-operated crate handling
- **Dual Areas**: Cargo hold (internal, flight-accessible) vs loading bay (external, ground-only)
- **Movement Restrictions**: Loading bay operations blocked when IAS > 0.1 knots for flight safety
- **Crate Physics**: Gravity-based dropping with collision detection and support requirements
- **Keyboard Controls**: Arrow keys for winch/cable, R=refresh bay, A=attach, D=detach
- **Enhanced Navigation**: Tab cycles through widgets AND crates for full keyboard accessibility

### Bridge Scene
- **Flight Instruments**: Comprehensive flight data with autopilot controls
- **Critical Systems**: Engine monitoring, navigation aids, system status
- **Autopilot Modes**: Heading hold, altitude hold, airspeed management

### Engine Room Scene
- **Engine Management**: RPM, manifold pressure, temperature monitoring
- **Throttle Controls**: Mixture, propeller, and throttle adjustments
- **System Health**: Visual indicators for engine performance and issues

### Fuel Scene
- **Tank Management**: Forward/aft tank levels with individual feed controls
- **Transfer System**: Pump controls for fuel balancing and transfer operations
- **Flight Safety**: Fuel flow monitoring and low-fuel warnings

## Development Guidelines

### Code Style

- **Docstrings**: Use clear docstrings for all methods
- **Type Hints**: Use Optional, List, Dict imports from typing
- **Constants**: Define colors and sizes as module-level constants
- **Error Handling**: Graceful fallbacks for missing assets

### Version Management

- **CRITICAL**: After ANY code changes, always bump the version in `pyproject.toml`
- **Multiple Bumps**: If making consecutive changes, bump the version each time
- **Release Readiness**: The product might be pushed/released at any time, so every change should have a new version
- **Semantic Versioning**: Use patch increments (0.2.1 → 0.2.2) for fixes, minor increments (0.2.0 → 0.3.0) for features

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

### Centralized State Management

**CRITICAL PRINCIPLE**: All game state must flow through `core_simulator.py`
- Scenes are stateless display layers only
- Use `get_simulator()` to access the central state manager
- Never store game data in scene classes
- All physics, game logic, and state changes happen in the simulator
- Scenes send commands to simulator, simulator updates state, scenes display current state

Example Pattern:
```python
# CORRECT - Scene sends command to simulator
simulator.set_winch_position(x, y)
cargo_state = simulator.get_cargo_state()  # Get current state to display

# WRONG - Scene maintains its own state
self.winch_position = (x, y)  # Don't do this!
```

## Save System

### Auto-Save Features

- **Game saves automatically** when returning to main menu via Escape
- **Game saves automatically** on application exit
- **Single save slot** system for simplicity
- **Resume button** automatically enabled when save file exists

### Save File Locations

- **Default Location**: OS-appropriate application data directory
  - **Windows**: `%APPDATA%\AirshipZero\saved_game.json`
  - **macOS**: `~/Library/Application Support/AirshipZero/saved_game.json`
  - **Linux**: `~/.local/share/AirshipZero/saved_game.json`
- **Custom Locations**: Override via command-line arguments
  ```bash
  # Custom file in current directory
  python main.py --save-file my_game.json
  
  # Absolute path
  python main.py --save-file /path/to/saves/campaign.json
  
  # Relative directory (auto-created)
  python main.py --save-file saves/pilot_training.json
  
  # Short form
  python main.py -s custom.json
  ```
- **Format**: JSON with complete game state
- **Persistence**: Survives application restarts and runs from any directory
- **Validation**: Automatic format checking on load

### Command-Line Interface

`main.py` uses argparse to accept optional save file path override:
- Read once at startup, never re-read during execution
- Custom path takes precedence over OS app data directory
- Supports both files and directories (auto-appends filename for directories)
- All save/load operations use the configured path throughout the session

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

# Direct launch (requires activated .venv)
uv run python main.py

# Tool-based launch (from GitHub)
uv tool run --from git+https://github.com/TimelessP/timeless-as0 airshipzero
```

### Environment Requirements

**MANDATORY**: Always activate virtual environment first:
```bash
# Before any development work
source .venv/bin/activate

# Then use uv commands or direct python
uv run python main.py
python main.py  # Only after .venv activated
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

## Important Development Notes

### Project Distribution
- **UV Tool Packaging**: Project is packaged as `airshipzero` tool via `pyproject.toml`
- **GitHub Repository**: https://github.com/TimelessP/timeless-as0
- **Entry Point**: `main:main` function for tool installation
- **Direct Installation**: `uv tool install git+https://github.com/TimelessP/timeless-as0`

### Virtual Environment
- **ALWAYS** activate `.venv` before development: `source .venv/bin/activate`
- Use `uv run` commands for dependency management
- Never commit without testing in the proper environment

### State Management
- All game state lives in `core_simulator.py` - scenes are view-only
- Use `get_simulator()` to access the central singleton
- Never duplicate game state in scene classes

### Scene Architecture  
- Each scene is self-contained with its own event handling
- Use consistent widget patterns across scenes
- Focus management with Tab/Shift+Tab cycling
- Return proper scene transition strings from `handle_event()`

### Asset Guidelines
- Fonts support anti-aliasing but final scaling is pixel-perfect
- Use relative paths from project root for all assets
- In-game documentation lives in `assets/books/` as Markdown files
- All images designed for 320x320 logical resolution

### Testing Strategy
- Manual testing via `./run.sh` for full game validation
- Test scene transitions, widget focus, and edge cases
- Validate cargo physics, movement restrictions, and flight mechanics

## Save System

### Auto-Save Features

- **Game saves automatically** when returning to main menu via Escape
- **Game saves automatically** on application exit
- **Single save slot** system for simplicity
- **Resume button** automatically enabled when save file exists

### Save File

- **Location**: OS-appropriate application data directory
  - **Windows**: `%APPDATA%\AirshipZero\saved_game.json`
  - **macOS**: `~/Library/Application Support/AirshipZero/saved_game.json`
  - **Linux**: `~/.local/share/AirshipZero/saved_game.json`
- **Format**: JSON with complete game state
- **Persistence**: Survives application restarts and runs from any directory
- **Validation**: Automatic format checking on load

## Future Enhancements

- **Weather System**: Wind, storms affecting navigation
- **Cargo Management**: Loading, delivery missions
- **Multiplayer**: Network support for multiple airships
- **Advanced Navigation**: Waypoint system, autopilot
