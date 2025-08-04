# 🎈 Airship Zero - Steam & Copper Dreams

> **A retro-inspired airship simulation game with brutally simple 320x320 pixel UI**

## Overview

Airship Zero is a steampunk-aesthetic flight simulator built with Python and Pygame. The game features a fixed 320x320 logical resolution that scales beautifully to any window size while maintaining crisp, pixel-perfect rendering.

## Features

### ✅ **Currently Implemented**
- 🎮 **Complete Scene System** - Main menu, bridge, engine room, navigation
- 🗺️ **Interactive Navigation** - Zoomable world map with click/drag panning and mousewheel zoom
- ⚡ **Real-time Engine Simulation** - Boiler pressure, temperature, fuel management
- 💾 **Auto-Save System** - Game saves automatically when returning to menu or exiting
- 🎯 **Tab-based Focus** - Consistent UI navigation across all scenes
- 🎨 **Retro Aesthetics** - Pixelify Sans font, steampunk color palette, pixel-perfect scaling

### 🛩️ **Flight Systems**
- **Navigation Display** - Real-time position, heading, and speed indicators
- **Engine Monitoring** - Throttle control, boiler management, system diagnostics  
- **World Map** - Interactive navigation with zoom levels from 0.25x to 4.0x
- **Centralized Simulator** - Single source of truth for all game state

### 🎛️ **User Interface**
- **Fixed Logical Resolution** - Everything designed for 320x320, then scaled
- **Anti-aliased Fonts** - Crisp text rendering with pixel-perfect final scaling
- **Mouse & Keyboard Support** - Click, drag, zoom, and keyboard shortcuts
- **Scene-based Architecture** - Clean separation between game areas
## Quick Start

### Requirements

- **Python 3.12+**
- **UV package manager** (recommended)

### Installation

**Install UV (if you don't have it):**

Linux/macOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Running the Game

```bash
# Quick launch
./run.sh

# Or directly
uv run python main.py
```

## Controls

### Universal
- **Tab / Shift+Tab** - Cycle through UI widgets
- **Enter / Space** - Activate focused widget
- **Escape** - Return to main menu (auto-saves)

### Navigation Scene
- **Arrow Keys** - Pan the map
- **+/-** - Zoom in/out
- **Mouse Wheel** - Zoom in/out
- **Click & Drag** - Pan the map
- **C** - Center on current position

## Game Systems

### Save System
- **Auto-save** when returning to main menu
- **Auto-save** on application exit
- **Resume Game** button appears when save file exists
- Single save slot in `saved_game.json`

### Navigation
- **World Map** - 640x320 pixel world view
- **Position Tracking** - Real-time lat/lon display
- **Zoom Levels** - 0.25x to 4.0x magnification
- **Click & Drag** - Intuitive map exploration
- **Position Indicator** - Red marker with heading arrow

### Engine Room
- **Boiler Management** - Pressure and temperature monitoring
- **Throttle Control** - Engine power adjustment
- **System Diagnostics** - Real-time status displays

## Architecture

### Design Principles
- **Fixed Logical Resolution** - Everything designed for 320x320 pixels, then scaled
- **Scene-Based Architecture** - Each major area is a separate, self-contained scene
- **Centralized Simulation** - Single `core_simulator.py` manages all game state
- **Anti-aliasing on Fonts** - Crisp text rendering, pixel-perfect final scaling
- **Retro Aesthetics** - Pixelify Sans font, steampunk color palette

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
├── pyproject.toml         # UV project configuration
├── uv.lock               # Locked dependencies
└── run.sh                # Quick launch script
```

## Development

### Adding New Features
See `.github/copilot-instructions.md` for detailed development guidelines including:
- Widget system patterns
- Scene transition handling
- Simulator integration
- Code style standards

### Dependencies
- **pygame** - Graphics and input handling
- **Python 3.12+** - Modern Python features

### Development Commands
```bash
# Install dependencies
uv sync

# Run the game
uv run python main.py

# Quick launch
./run.sh
```

## Future Enhancements

### Planned Features
- **Weather System** - Wind, storms affecting navigation
- **Cargo Management** - Loading, delivery missions  
- **Advanced Navigation** - Waypoint system, autopilot
- **Sound System** - Engine sounds, ambient audio
- **Enhanced Graphics** - Improved world map, animations

### Technical Improvements  
- **Multiplayer Support** - Network functionality
- **Save Slots** - Multiple save files
- **Settings Menu** - Graphics, audio, control options
- **Performance** - Optimized rendering, larger maps

## License

MIT License - see [`LICENSE`](LICENSE) file for details.

---

**Experience the golden age of airship travel in glorious 320x320 pixels!** 

*Steam & Copper Dreams await...*
