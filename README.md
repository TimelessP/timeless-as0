# 🎈 Airship Zero - Steam & Copper Dreams

> **A comprehensive airship simulation with realistic physics, professional documentation, and brutally simple 320x320 pixel UI**

## Overview

Airship Zero is a steampunk-aesthetic flight simulator built with Python and Pygame featuring realistic atmospheric physics, comprehensive systems simulation, and a complete operational manual suite. The game maintains a fixed 320x320 logical resolution that scales beautifully to any window size while delivering pixel-perfect rendering and professional-grade simulation depth.

## TL;DR Quickstart

```bash
uv tool run --from git+https://github.com/TimelessP/timeless-as0 airshipzero
```

## Features

### ✅ **Fully Implemented Systems**

#### 🛩️ **Realistic Flight Physics**
- **Atmospheric Modeling** - Realistic air density effects with altitude
- **Engine Performance** - Power loss (~3% per 1000 ft), mixture optimization
- **Propeller Dynamics** - Pitch-dependent efficiency, altitude compensation
- **True Airspeed** - Proper IAS/TAS calculations with atmospheric correction
- **Smooth Autopilot** - Multi-phase altitude control with realistic climb/descent rates

#### 🎮 **Complete Scene System**
- **Bridge** - Primary flight controls with attitude indicator and autopilot
- **Engine Room** - Comprehensive engine monitoring and control
- **Navigation** - Interactive world map with position tracking
- **Fuel Management** - Dual-tank system with transfer and emergency dump
- **Additional Scenes** - Cargo, Communications, Crew, Camera, Missions

#### ⚙️ **Advanced Engine Simulation**
- **Realistic Parameters** - RPM, manifold pressure, temperatures, fuel flow
- **Altitude Effects** - Proper atmospheric pressure and density modeling
- **Mixture Control** - Altitude-dependent optimal mixture calculation
- **Propeller Load** - Variable pitch effects on engine performance
- **Fuel System** - Pressure-sensitive performance, starvation modeling

#### 🗺️ **Professional Navigation**
- **World Map** - High-resolution 640x320 interactive display
- **Position Tracking** - Real-time GPS-style coordinate display
- **Zoom Control** - 0.25x to 4.0x with smooth mouse/keyboard operation
- **Autopilot Integration** - Heading hold, altitude hold, route following
- **Manual Controls** - Precise rudder input with visual feedback

#### ⛽ **Comprehensive Fuel Management**
- **Dual-Tank System** - 180-gallon forward/aft tanks (360 total capacity)
- **Independent Feed Control** - Per-tank engine feed switches
- **Inter-Tank Transfer** - Real-time fuel balancing for optimal CG
- **Emergency Dump** - Overboard fuel jettison with safety controls
- **Weight & Balance** - Visual pitch effects and CG management

#### 💾 **Advanced Save System**
- **Auto-Save** - Automatic save on menu return and application exit
- **Complete State** - Full game state persistence with format validation
- **Resume Capability** - Seamless game continuation with all systems intact
- **Cross-Platform** - OS-appropriate app data directories (Windows/macOS/Linux)
- **Portable** - Saves persist regardless of where game is run from

#### 📚 **Professional Documentation**
- **Complete User Manuals** - Bridge, Engine Room, Navigation, Fuel Management
- **Operational Procedures** - Step-by-step flight operations guide
- **Emergency Procedures** - Comprehensive emergency response protocols
- **Technical Reference** - Detailed system specifications and limits

### 🎛️ **User Interface Excellence**
- **Fixed Logical Resolution** - Everything designed for 320x320, then scaled
- **Pixel-Perfect Rendering** - Anti-aliased fonts with nearest-neighbor scaling
- **Professional HMI** - Aviation-grade interface design and layout
- **Consistent Navigation** - Tab-based focus system across all scenes
- **Mouse & Keyboard** - Full input support with keyboard shortcuts
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

#### Option 1: Direct Run (No Installation)
```bash
# Run directly from GitHub
uv tool run --from git+https://github.com/TimelessP/timeless-as0 airshipzero
```

#### Option 2: Install as Tool (Recommended for Repeated Use)
```bash
# Install once
uv tool install git+https://github.com/TimelessP/timeless-as0

# Run anytime after installation
airshipzero
```

#### Option 3: Development (Local Clone)
```bash
# Quick launch
./run.sh

# Or directly
uv run python main.py
```

### Command-Line Options

All run methods support custom save file locations:

```bash
# Default location (OS app data directory)
airshipzero
uv tool run --from git+https://github.com/TimelessP/timeless-as0 airshipzero
python main.py

# Custom save file
airshipzero --save-file my_campaign.json
python main.py --save-file /path/to/saves/pilot_training.json

# Short form
airshipzero -s custom_game.json

# Get help
airshipzero --help
python main.py --help
```

## Controls

### Universal Navigation
- **Tab / Shift+Tab** - Cycle through UI widgets in all scenes
- **Enter / Space** - Activate focused widget
- **Escape** - Return to main menu (auto-saves game state)
- **[ / ]** - Navigate between scenes (circular order)

### Bridge Scene (Primary Flight Controls)
- **← / →** - Manual rudder control (manual mode only)
- **+ / -** - Adjust target altitude (40-foot increments)
- **Mouse Click** - Activate widgets, drag altitude slider
- **Text Input** - Enter target heading in heading textbox

### Navigation Scene (World Map)
- **Arrow Keys** - Pan the map in 20-pixel increments
- **+ / -** - Zoom in/out (0.25x to 4.0x range)
- **Mouse Wheel** - Smooth zoom control
- **Click & Drag** - Intuitive map panning
- **C** - Center view on current airship position

### Engine Room Scene
- **Mouse Click** - Adjust throttle, mixture, propeller sliders
- **Keyboard** - Fine-tune controls with keyboard shortcuts
- **Real-time** - All changes immediately affect flight performance

### Fuel Management Scene
- **Mouse Click** - Toggle feed switches, adjust transfer/dump rates
- **Vertical Sliders** - Precise fuel transfer and dump control
- **Real-time** - Live fuel quantity updates and weight/balance effects

## Game Systems

### Realistic Flight Physics

#### Atmospheric Modeling
- **Altitude Effects** - Exponential air density decrease with altitude
- **Engine Performance** - ~3% power loss per 1000 feet of altitude
- **Propeller Efficiency** - Altitude-compensated prop performance
- **True Airspeed** - Proper IAS to TAS conversion based on air density

#### Advanced Engine Simulation
- **Mixture Optimization** - Altitude-dependent optimal mixture settings
- **RPM Response** - Realistic engine acceleration/deceleration
- **Temperature Modeling** - CHT, EGT, oil temperature simulation
- **Fuel Pressure** - Pressure-sensitive engine performance
- **Propeller Load** - Variable pitch effects on engine RPM and power

#### Smooth Autopilot System
- **Multi-Phase Altitude Control** - 150/80/30/10 ft/min rates with easing
- **Precision Approach** - Smooth approach to target altitude within 1 foot
- **Heading Hold** - Discrete 2° rudder adjustments every 0.5 seconds
- **Manual Override** - Instant disengagement for emergency control

### Comprehensive Fuel System
- **Dual Tanks** - 180-gallon forward and aft tanks (360 total capacity)
- **Independent Feeds** - Per-tank engine feed control
- **Real-time Transfer** - Inter-tank fuel movement for weight/balance
- **Emergency Dump** - Overboard fuel jettison with safety protocols
- **CG Management** - Visual pitch effects from fuel distribution

### Professional Save System
- **Complete State Persistence** - All flight parameters, fuel levels, system states
- **Auto-Save Triggers** - Menu return, application exit, scene transitions
- **Format Validation** - Automatic checking for save file integrity
- **Cross-Platform Storage** - OS-appropriate app data directories
  - **Windows**: `%APPDATA%\AirshipZero\saved_game.json`
  - **macOS**: `~/Library/Application Support/AirshipZero/saved_game.json`
  - **Linux**: `~/.local/share/AirshipZero/saved_game.json`
- **Custom Save Locations** - Override default path via command line
  ```bash
  # Use default OS-appropriate location
  python main.py
  uv tool run --from git+https://github.com/TimelessP/timeless-as0 airshipzero
  
  # Use custom file in current directory
  python main.py --save-file my_game.json
  uv tool run --from git+https://github.com/TimelessP/timeless-as0 airshipzero --save-file my_game.json
  
  # Use absolute path
  python main.py --save-file /path/to/saves/campaign.json
  
  # Use relative directory (creates if needed)
  python main.py --save-file saves/pilot_training.json
  ```
- **Seamless Resume** - Perfect game state restoration with all systems active

## Documentation

### Professional User Manuals

The game includes comprehensive operational manuals for all major systems:

#### 📖 **Bridge Operations Manual** (`assets/books/user-manual-bridge.md`)
- **Flight Instruments** - Altitude, airspeed, heading displays and interpretation
- **Engine Monitoring** - RPM, manifold pressure, fuel flow analysis
- **System Status** - Battery, fuel feed, autopilot operational states
- **Flight Controls** - Manual rudder control and autopilot integration
- **Altitude Management** - Smooth altitude control with realistic climb/descent
- **Emergency Procedures** - Engine failure, fuel starvation, electrical failure
- **Professional Techniques** - Realistic flight operations and best practices

#### 🔧 **Engine Room Manual** (`assets/books/user-manual-engine-room.md`)
- **Engine Controls** - Throttle, mixture, propeller pitch optimization
- **Performance Monitoring** - Temperature, pressure, fuel system analysis
- **Altitude Effects** - Engine performance degradation and compensation
- **Mixture Management** - Optimal settings for different flight conditions
- **Electrical Systems** - Battery, alternator, and load management
- **Maintenance Procedures** - System checks and troubleshooting
- **Emergency Operations** - Engine failure response and restart procedures

#### 🗺️ **Navigation Manual** (`assets/books/user-manual-navigation.md`)
- **World Map Operations** - Interactive map control and position tracking
- **Navigation Techniques** - Visual navigation, dead reckoning, route planning
- **Position Information** - GPS-style coordinate display and interpretation
- **Map Controls** - Zoom, pan, centering operations and shortcuts
- **Professional Navigation** - Wind effects, course planning, emergency navigation
- **Interface Reference** - Complete keyboard and mouse control guide

#### ⛽ **Fuel Management Manual** (`assets/books/user-manual-fuel.md`)
- **Dual-Tank System** - Forward/aft tank configuration and operation
- **Feed Controls** - Engine feed management and selection strategies
- **Transfer Operations** - Inter-tank fuel movement for weight and balance
- **Emergency Procedures** - Fuel dumping, leak response, contamination handling
- **Weight & Balance** - CG management through fuel distribution
- **Consumption Planning** - Range calculation and fuel management strategy

### Technical Documentation
- **Development Guidelines** - Complete development standards in `.github/copilot-instructions.md`
- **Architecture Overview** - Scene system, simulator integration, widget patterns
- **API Reference** - Core simulator methods and state management
- **Code Standards** - Consistent coding patterns and best practices

## Architecture

### Design Principles
- **Realistic Simulation** - Authentic atmospheric physics and flight dynamics
- **Professional Interface** - Aviation-grade HMI design and operational procedures
- **Fixed Logical Resolution** - Everything designed for 320x320 pixels, then scaled
- **Scene-Based Architecture** - Each major area is self-contained with clear responsibilities
- **Centralized Simulation** - Single `core_simulator.py` manages all physics and state
- **Comprehensive Documentation** - Professional operational manuals for all systems
- **Pixel-Perfect Rendering** - Anti-aliased fonts with nearest-neighbor final scaling

### File Structure
```
/
├── main.py                 # Application entry point and scene management
├── core_simulator.py       # Centralized physics simulation with realistic modeling
├── scene_bridge.py         # Primary flight interface with autopilot
├── scene_engine_room.py    # Engine controls and performance monitoring
├── scene_navigation.py     # Interactive world map with position tracking
├── scene_fuel.py          # Dual-tank fuel management system
├── scene_*.py             # Additional operational scenes
├── assets/
│   ├── fonts/              # Pixelify Sans and alternative fonts
│   ├── png/               # World map and graphical assets
│   └── books/             # Complete user manual library
│       ├── user-manual-bridge.md
│       ├── user-manual-engine-room.md
│       ├── user-manual-navigation.md
│       └── user-manual-fuel.md
├── pyproject.toml         # UV project configuration
├── uv.lock               # Locked dependencies
└── run.sh                # Quick launch script
```

### Core Systems

#### Simulation Engine (`core_simulator.py`)
- **Atmospheric Physics** - Realistic air density modeling with altitude
- **Engine Performance** - Multi-parameter engine simulation with altitude effects
- **Flight Dynamics** - True airspeed calculation, autopilot control
- **Fuel System** - Dual-tank management with transfer and dump capabilities
- **State Management** - Complete game state persistence and restoration

#### Scene System
- **Bridge Scene** - Flight control with attitude indicator and smooth autopilot
- **Engine Room** - Comprehensive engine monitoring and control
- **Navigation Scene** - Interactive world map with zoom and position tracking
- **Fuel Scene** - Professional fuel management with weight/balance control
- **Extensible Design** - Easy addition of new scenes and capabilities

## Development

### Getting Started
The project uses modern Python tooling with UV package manager for dependency management and virtual environment handling.

### Adding New Features
See `.github/copilot-instructions.md` for comprehensive development guidelines including:
- **Widget System Patterns** - Consistent UI component implementation
- **Scene Transition Handling** - Proper scene navigation and state management
- **Simulator Integration** - How to interact with the central physics simulation
- **Physics Modeling** - Adding realistic atmospheric and flight effects
- **Documentation Standards** - Professional manual writing and technical documentation
- **Code Style Standards** - Consistent Python coding patterns

### Key Development Patterns

#### Scene Implementation
- **Widget Management** - Consistent focus cycling, mouse interaction, rendering
- **State Synchronization** - Real-time updates from central simulator
- **Event Handling** - Keyboard, mouse, and focus management patterns
- **Transition Logic** - Scene navigation and return value handling

#### Simulator Integration
- **State Access** - `simulator.get_state()` for read operations
- **Control Methods** - Specific methods for each control system
- **Physics Updates** - Real-time simulation in `update()` method
- **State Persistence** - Auto-save integration and game state management

#### Professional Documentation
- **User Manual Standards** - Comprehensive operational procedures
- **Technical Accuracy** - Realistic aviation procedures and limits
- **Safety Emphasis** - Emergency procedures and best practices
- **Complete Coverage** - All interface elements and operational modes

### Dependencies
- **pygame** - Graphics, input handling, and surface management
- **Python 3.12+** - Modern Python features and type hints
- **UV** - Fast, reliable Python package management

### Development Commands
```bash
# Install once as a tool for easy access
uv tool install git+https://github.com/TimelessP/timeless-as0

# Run the installed tool
airshipzero

# Or run directly without installation
uv tool run --from git+https://github.com/TimelessP/timeless-as0 airshipzero

# Development mode (local clone)
# Install dependencies and set up environment
uv sync

# Run the game in development mode
uv run python main.py

# Quick launch with automatic dependency management
./run.sh

# Run tests (if implemented)
uv run python -m pytest

# Check code formatting
uv run python -m black .
```

### Testing
- **Manual Testing** - Scene transitions, widget interactions, physics accuracy
- **Integration Testing** - Save/load functionality, state persistence
- **Physics Validation** - Atmospheric modeling, engine performance curves
- **User Experience** - Professional aviation interface standards

## Future Enhancements

### Simulation Improvements
- **Weather System** - Dynamic wind, turbulence, weather effects on flight
- **Advanced Physics** - Detailed atmospheric modeling, seasonal variations
- **Performance Modeling** - More sophisticated engine and propeller curves
- **Navigation Aids** - VOR, NDB, GPS waypoint navigation systems

### Operational Features
- **Mission System** - Cargo delivery, passenger transport, search and rescue
- **Flight Planning** - Route optimization, fuel planning, weather routing
- **Communication** - Radio procedures, air traffic control simulation
- **Crew Management** - Multi-crew operations, role specialization

### Technical Enhancements
- **Sound System** - Engine sounds, ambient audio, radio chatter
- **Enhanced Graphics** - Higher-resolution maps, weather visualization
- **Multiplayer Support** - Network functionality for multiple airships
- **Advanced Autopilot** - VNAV, LNAV, approach coupling

### User Experience
- **Settings Menu** - Graphics options, control configuration, audio settings
- **Multiple Save Slots** - Campaign progression, different airship configurations
- **Tutorial System** - Interactive training for complex procedures
- **Performance Analytics** - Flight logging, efficiency tracking, skill development

### Platform Support
- **Cross-Platform** - Windows, macOS, Linux compatibility
- **Mobile Adaptation** - Touch-friendly interface for tablets
- **Web Version** - Browser-based deployment for accessibility
- **VR Integration** - Immersive cockpit experience

## Performance Characteristics

### Realistic Flight Envelope

#### Altitude Performance
- **Service Ceiling** - 4,000 feet maximum operational altitude
- **Optimal Cruise** - 1,000-2,500 feet for best efficiency
- **Engine Power Loss** - ~3% per 1,000 feet of altitude gain
- **Prop Efficiency** - Automatically compensated for altitude effects

#### Speed Performance
- **Cruise Speed** - 75-90 knots indicated airspeed
- **Maximum Speed** - 110 knots (structural/engine limits)
- **Minimum Speed** - 45 knots (stall characteristics)
- **True Airspeed** - Increases ~6% per 5,000 feet altitude

#### Fuel Specifications
- **Total Capacity** - 360 gallons (180 per tank)
- **Cruise Consumption** - 10-15 GPH depending on power setting
- **Maximum Range** - ~28 hours no-wind operation
- **Reserve Requirements** - 30-60 minutes minimum for safe operations

#### Engine Parameters
- **Maximum RPM** - 2,800 (avoid sustained operation)
- **Cruise RPM** - 2,200-2,700 typical
- **Manifold Pressure** - 20-28" Hg cruise, decreases with altitude
- **Operating Temperatures** - CHT 250-400°F, EGT 1200-1600°F

## License

MIT License - see [`LICENSE`](LICENSE) file for details.

## Acknowledgments

- **Realistic Physics Modeling** - Based on authentic atmospheric and aviation principles
- **Professional Documentation** - Inspired by real aviation operational manuals
- **Steampunk Aesthetics** - Retro-futuristic design with modern simulation accuracy
- **Python Gaming Community** - Built with pygame and modern Python tooling

---

**Experience professional airship operations with realistic physics simulation and comprehensive documentation!**

*Master the skies with Steam & Copper Dreams...*

**Features Summary:**
✅ Realistic atmospheric physics and engine modeling  
✅ Professional-grade autopilot with smooth altitude control  
✅ Comprehensive fuel management with weight/balance effects  
✅ Interactive world navigation with precision controls  
✅ Complete user manual suite for all major systems  
✅ Auto-save system with full state persistence  
✅ Pixel-perfect 320x320 retro aesthetic  

**Ready for takeoff, Captain!** 🎈
