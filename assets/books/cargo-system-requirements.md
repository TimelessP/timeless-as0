# Cargo System Requirements

## Overview

The cargo management system is a physics-based mini-game that simulates loading and unloading cargo using a ceiling-mounted winch system. Players must strategically arrange cargo within limited space while managing weight distribution and center of gravity.

## Core Components

### 1. Winch System

**Physical Properties:**
- Travels along a horizontal ceiling rail spanning both cargo hold and loading bay
- Cable can extend/retract vertically
- Can attach/detach to compatible cargo items
- Position and state persist in game save data

**Controls:**
- **Left/Right Movement**: Press-and-hold buttons (mouse click-hold or keyboard Enter/Space-hold with focus)
- **Up/Down Cable**: Press-and-hold buttons for cable extension/retraction
- **Attach/Detach**: Toggle buttons for cargo connection

**State Persistence:**
```json
"cargo": {
  "winch": {
    "position": {"x": 160, "y": 50},
    "cableLength": 0,
    "attachedCrate": null,
    "movementState": {"left": false, "right": false, "up": false, "down": false}
  }
}
```

### 2. Cargo Areas

**Cargo Hold (Left Side):**
- Permanent storage area
- Cargo here affects ship weight and balance
- Items contribute to center of gravity calculations
- No automatic clearing

**Loading Bay (Right Side):**
- Temporary staging area for available cargo
- Items appear via "Refresh" button
- Automatically cleared when ship moves (>0.1 kts)
- Refresh disabled while ship is moving
- Items here do not affect ship performance

**Area Definitions:**
```json
"cargoAreas": {
  "cargoHold": {"x": 8, "y": 60, "width": 150, "height": 200},
  "loadingBay": {"x": 162, "y": 60, "width": 150, "height": 200}
}
```

### 3. Crate System

**Crate Properties:**
**Type**: Defines contents and behavior (e.g., "fuel_drum", "books", "supplies")

**Crate Types:**
```json
"crateTypes": {
  "fuel_drum": {
    "name": "Fuel Drum",
    "dimensions": {"width": 2, "height": 3},
    "contents": {"amount": 44, "unit": "gallons"},
    "colors": {"outline": "#FFFFFF", "fill": "#FF4444"},
    "usable": true,
    "useAction": "transfer_fuel"
  },
  "books": {
    "name": "Books",
    "dimensions": {"width": 1, "height": 1},
    "contents": {"amount": 1, "unit": "book"},
    "colors": {"outline": "#8B4513", "fill": "#DEB887"},
    "usable": false
  },
  "medical_supplies": {
    "name": "Medical Kit",
    "dimensions": {"width": 2, "height": 2},
    "contents": {"amount": 1, "unit": "kit"},
    "colors": {"outline": "#FF0000", "fill": "#FFE4E1"},
    "usable": true,
    "useAction": "add_medical_supplies"
  },
  "food_rations": {
    "name": "Food Rations",
    "dimensions": {"width": 3, "height": 1},
    "contents": {"amount": 7, "unit": "days"},
    "colors": {"outline": "#228B22", "fill": "#90EE90"},
    "usable": true,
    "useAction": "add_food"
  },
  "spare_parts": {
    "name": "Engine Parts",
    "dimensions": {"width": 2, "height": 2},
    "contents": {"amount": 1, "unit": "set"},
    "colors": {"outline": "#696969", "fill": "#D3D3D3"},
    "usable": false
  },
  "luxury_goods": {
    "name": "Luxury Items",
    "dimensions": {"width": 1, "height": 2},
    "contents": {"amount": 1, "unit": "crate"},
    "colors": {"outline": "#FFD700", "fill": "#FFFACD"},
    "usable": false
  }
}
```

**Crate Instance Structure:**
```json
"crate": {
  "id": "crate_001",
  "type": "fuel_drum",
  "position": {"x": 10, "y": 100},
  "area": "loadingBay",
  "contents": {"amount": 44.0, "unit": "gallons"}
}
```

### 4. Physics and Collision System

**Grid-Based Positioning:**
- Cargo areas divided into grid cells (e.g., 10x10 pixel cells)
- Crates snap to grid alignment
- Collision detection prevents overlapping

**Placement Rules:**
- Crates must be fully within designated areas (cargo hold or loading bay)
- No overlapping between crates
- Crates can only be detached when properly positioned
- Crates "fall" to lowest available position when detached

**Stability System:**
- Crates need support: floor contact OR crates under both bottom corners
- Unsupported crates cannot be detached (remain attached to winch)
- Visual feedback for valid/invalid placement positions

### 5. Game State Integration

**Core Simulator Data Structure:**
```json
"cargo": {
  "winch": {
    "position": {"x": 160, "y": 50},
    "cableLength": 0,
    "attachedCrate": null,
    "movementState": {"left": false, "right": false, "up": false, "down": false}
  },
  "cargoHold": [
    {
      "id": "crate_001",
      "type": "fuel_canister",
      "position": {"x": 20, "y": 200},
      "contents": {"amount": 1.0, "unit": "gallon"}
    }
  ],
  "loadingBay": [
    {
      "id": "crate_002", 
      "type": "books",
      "position": {"x": 180, "y": 220},
      "contents": {"amount": 1, "unit": "book"}
    }
  ],
  "totalWeight": 145.8,
  "centerOfGravity": {"x": 156.2, "y": 100.0},
  "maxCapacity": 500.0,
  "refreshAvailable": true
}
```

**Weight and Balance Calculations:**
- Each crate type has associated weight per unit
- Total weight = sum of all cargo hold items
- Center of gravity calculated from cargo hold item positions and weights
- Loading bay items do not affect ship performance

### 6. User Interface Design

**Layout (320x320 pixel screen):**
```
[0,0]                                    [320,0]
┌─────────────────────────────────────────────┐
│ CARGO MANAGEMENT (header)                   │
├─────────────────────────────────────────────┤
│      WINCH RAIL                             │
│  ◀ Left │ Right ▶  │  ▲ Up │ Down ▼        │
│         │         │        │               │
│ CARGO HOLD        │  LOADING BAY           │
│ ┌─────────────────┐ ┌─────────────────┐     │
│ │                 │ │                 │     │
│ │   [crates]      │ │   [crates]      │     │
│ │                 │ │                 │     │
│ │                 │ │                 │     │
│ └─────────────────┘ └─────────────────┘     │
│                                             │
│ [Attach] [Detach] [Use] [Refresh]           │
│                                             │
│ Selected: Fuel Drum, 2x3, 44 gallons     │
├─────────────────────────────────────────────┤
│ < [                           ] >           │
└─────────────────────────────────────────────┘
[0,320]                                [320,320]
```

**Widget Layout:**
- **Winch Controls**: 4 directional buttons (top area)
- **Action Buttons**: Attach, Detach, Use, Refresh (bottom area)
- **Info Panel**: Selected crate details (bottom area)
- **Visual Areas**: Cargo hold and loading bay with grid overlay

**Visual Elements:**
- **Winch**: Small rectangle with cable line extending down
- **Crates**: Filled rectangles with outline and X-pattern for structure
- **Grid**: Subtle grid lines for alignment reference
- **Selection**: Highlighted border for focused/selected crates

### 7. Control Schemes

**Mouse Controls:**
- **Click-and-hold** on directional buttons for continuous movement
- **Click** on crates to select them
- **Click** on action buttons for immediate actions

**Keyboard Controls:**
- **Tab/Shift+Tab**: Cycle focus through all interactive elements
- **Enter/Space**: Activate focused button (hold for continuous movement)
- **Arrow Keys**: Alternative winch movement (when winch controls focused)
- **Escape**: Return to main menu

**Focus Management:**
- Winch movement buttons support hold-to-move functionality
- Crates are focusable and show selection when focused
- Action buttons become enabled/disabled based on context

### 8. Game Mechanics

**Cargo Loading Process:**
1. Press "Refresh" to populate loading bay with random cargo
2. Position winch over desired crate
3. Lower cable to crate level
4. Press "Attach" to connect cable to crate
5. Raise cable to lift crate
6. Move winch horizontally to desired location
7. Lower cable to place crate
8. Press "Detach" when crate is properly supported

**Cargo Usage:**
- Select crate (click or focus with Tab)
- Press "Use" button if available for that crate type
- Fuel drums: Transfer contents to fuel tanks (aft first, then forward)
- Medical supplies: Add to ship's medical inventory
- Food rations: Extend crew supply duration

**Restriction System:**
- Loading bay refresh disabled when ship moving (>0.1 kts)
- Loading bay auto-clears when ship starts moving
- Winch cannot detach crates outside valid areas
- Crates cannot be placed in overlapping positions

### 9. Technical Implementation

**Scene Architecture:**
- Extends existing scene framework with mouse handling
- Integrates with core simulator for state persistence
- Updates ship weight/balance calculations in real-time

**Collision Detection:**
```python
def check_collision(crate1_pos, crate1_size, crate2_pos, crate2_size):
    # AABB collision detection for rectangular crates
    return not (crate1_pos.x + crate1_size.width <= crate2_pos.x or
                crate2_pos.x + crate2_size.width <= crate1_pos.x or
                crate1_pos.y + crate1_size.height <= crate2_pos.y or
                crate2_pos.y + crate2_size.height <= crate1_pos.y)
```

**Physics Updates:**
```python
def update_cargo_physics(dt):
    # Update winch position based on movement state
    # Check for cable attachment/detachment conditions
    # Calculate crate support and stability
    # Update ship weight and center of gravity
```

**Rendering Pipeline:**
```python
def render_cargo_scene(surface):
    # Draw cargo areas with grid overlay
    # Render all crates with type-specific colors
    # Draw winch and cable system
    # Highlight selected/focused elements
    # Show UI controls and info panels
```

### 10. Integration Points

**Core Simulator Methods:**
```python
# Cargo management
def get_cargo_state() -> dict
def set_winch_position(x: float, y: float)
def set_cable_length(length: float)
def attach_crate(crate_id: str) -> bool
def detach_crate() -> bool
def move_crate(crate_id: str, area: str, position: dict)
def use_crate(crate_id: str) -> bool
def refresh_loading_bay()
def calculate_cargo_weight_and_balance()

# Ship state queries
def get_ground_speed() -> float
def add_fuel_to_tanks(gallons: float)
def add_medical_supplies(amount: int)
def add_food_rations(days: int)
```

**Save/Load Integration:**
- All cargo state persists in main game save file
- Winch position and attached crates maintained across sessions
- Loading bay contents cleared on game load (temporary staging only)

## Success Criteria

1. **Functional Winch System**: Smooth movement along rail with cable control
2. **Intuitive Controls**: Both mouse and keyboard control schemes work reliably
3. **Collision Detection**: Prevents overlapping cargo placement
4. **Physics Simulation**: Realistic crate support and stability requirements
5. **State Persistence**: All cargo arrangements saved and loaded correctly
6. **Performance Integration**: Cargo affects ship weight and balance calculations
7. **Visual Polish**: Clear visual feedback for all interactions and states
8. **Accessibility**: Full keyboard navigation with proper focus management

This cargo system provides a challenging yet enjoyable mini-game that integrates seamlessly with the broader airship simulation while adding strategic depth to resource management.
