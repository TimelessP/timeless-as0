# Airship Zero - Cargo Management User Manual

**Steam & Copper Dreams Edition**  
*The Complete Guide to Cargo Operations*

---

## Table of Contents

1. [Overview](#overview)
2. [System Layout](#system-layout)
3. [Winch Operations](#winch-operations)
4. [Cargo Areas](#cargo-areas)
5. [Crate Types](#crate-types)
6. [Loading Procedures](#loading-procedures)
7. [Unloading Operations](#unloading-operations)
8. [Cargo Usage](#cargo-usage)
9. [Weight and Balance](#weight-and-balance)
10. [Emergency Procedures](#emergency-procedures)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)

---

## Overview

The Cargo Management system provides precise control over your airship's freight operations through a sophisticated winch-based loading system. This physics-based mini-game challenges pilots to strategically arrange cargo while maintaining proper weight distribution and operational efficiency.

**Key Features:**
- Ceiling-mounted winch with rail system
- Dual cargo areas (Hold & Loading Bay)
- Six distinct crate types with unique properties
- Real-time physics simulation with collision detection
- Integrated weight and balance calculations
- Cargo usage system for consumable items

**Safety Notice:** Improper cargo loading can significantly affect flight characteristics. Always maintain proper weight distribution and secure all cargo before flight operations.

---

## System Layout

The cargo management interface provides complete control over freight operations:

```
┌─────────────── CARGO MANAGEMENT ───────────────┐
│ [< Left] [Right >] [^ Up] [Down v]              │
│ ────────────────── WINCH RAIL ──────────────────│
│ ◊                     |                       ◊ │
│                       ▼ (cable)                 │
│ ┌──── CARGO HOLD ────┐ ┌─── LOADING BAY ────┐   │
│ │ ░░░░░░░░░░░░░░░░░░░ │ │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │   │
│ │ ░ ┌──┐      ┌───┐ ░ │ │ ▓ ┌─┐  ┌──┐  ┌─┐ ▓ │   │
│ │ ░ │FU│      │FOO│ ░ │ │ ▓ │B│  │ME│  │S│ ▓ │   │
│ │ ░ │EL│      │ODS│ ░ │ │ ▓ │K│  │DI│  │P│ ▓ │   │
│ │ ░ └──┘      └───┘ ░ │ │ ▓ └─┘  │CA│  │A│ ▓ │   │
│ │ ░                 ░ │ │ ▓      │L │  │R│ ▓ │   │
│ │ ░░░░░░░░░░░░░░░░░░░ │ │ ▓      └──┘  │T│ ▓ │   │
│ └───────────────────┘ └─────────────└─┘─────┘   │
│                                                 │
│ [Attach] [Detach] [Use] [Refresh]               │
│                                                 │
│ Selected: Fuel Canister, 2x3, 1.0 gallon       │
│ [< [                                  ] >]      │
└─────────────────────────────────────────────────┘
```

**Interface Elements:**
- **Winch Controls**: Directional movement buttons
- **Winch Rail**: Horizontal track spanning both cargo areas
- **Cargo Hold**: Permanent storage (left, green tint)
- **Loading Bay**: Temporary staging (right, brown tint)
- **Action Buttons**: Attach, Detach, Use, Refresh
- **Info Panel**: Selected crate details
- **Navigation**: Scene transition controls

---

## Winch Operations

### Winch System Components

**Rail System**
- **Span**: Covers both cargo hold and loading bay
- **Travel**: 304 pixels of horizontal movement
- **Position**: Ceiling-mounted at 52 pixels from top
- **Supports**: Structural mounting points every 50 pixels

**Winch Trolley**
- **Size**: 12x8 pixel unit
- **Movement**: Smooth horizontal travel along rail
- **Cable**: Extends vertically from trolley center
- **Speed**: Variable based on input duration

**Cable System**
- **Extension**: Up to 200+ pixels vertical reach
- **Retraction**: Returns to zero length
- **Attachment**: Connects to crate top-center
- **Visual**: Gray line from trolley to hook point

### Movement Controls

**Horizontal Movement**
- **[< Left]**: Moves winch left along rail
- **[Right >]**: Moves winch right along rail
- **Speed**: ~50 pixels per second
- **Range**: Full span of both cargo areas
- **Control**: Press-and-hold for continuous movement

**Vertical Movement**
- **[^ Up]**: Retracts cable (raises attached cargo)
- **[Down v]**: Extends cable (lowers hook/cargo)
- **Speed**: ~40 pixels per second
- **Range**: 0 to 200+ pixels extension
- **Control**: Press-and-hold for continuous movement

### Control Methods

**Mouse Operation**
- **Click-and-Hold**: Press and hold movement buttons
- **Release**: Stops movement immediately
- **Precision**: Hold briefly for fine adjustments
- **Continuous**: Hold longer for extended movement

**Keyboard Operation**
- **Tab Navigation**: Cycle focus to winch controls
- **Enter/Space**: Activate focused button (hold for continuous)
- **Arrow Keys**: Alternative movement when focused
- **Fine Control**: Brief key presses for precision

---

## Cargo Areas

### Cargo Hold (Permanent Storage)

**Location**: Left side of cargo bay
**Dimensions**: 150x180 pixels (18x22 grid cells)
**Purpose**: Long-term cargo storage
**Visual**: Green tint background with grid overlay

**Characteristics:**
- **Permanent**: Cargo remains until manually moved
- **Weight Impact**: All cargo affects ship performance
- **Balance**: Contributes to center of gravity calculations
- **Capacity**: Unlimited items within physical constraints
- **Access**: Load/unload via winch operations only

**Cargo Hold Grid:**
```
   0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17
 0 ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
 1 ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
 2 ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
...
21 └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘
```

### Loading Bay (Temporary Staging)

**Location**: Right side of cargo bay
**Dimensions**: 150x180 pixels (18x22 grid cells)
**Purpose**: Temporary cargo staging and resupply
**Visual**: Brown tint background with grid overlay

**Characteristics:**
- **Temporary**: Cleared when ship moves (>0.1 kts indicated airspeed)
- **No Weight Impact**: Does not affect ship performance
- **Resupply**: Populated via [Refresh] button
- **Motion Sensitive**: Automatically empties during flight
- **Staging**: Intermediate area for cargo transfer

**Refresh System:**
- **[Refresh] Button**: Generates random cargo selection
- **Availability**: Only when ship is stationary
- **Disabled State**: Grayed out during ship movement
- **Auto-Clear**: Contents lost when ship starts moving
- **Variety**: Random selection from all crate types

---

## Crate Types

The cargo system supports six distinct crate types, each with unique properties and uses:

### Fuel Canister (Usable)
**Dimensions**: 2x3 grid cells (16x24 pixels)
**Weight**: 8.0 lbs per canister
**Contents**: 1.0 gallon aviation fuel
**Colors**: White outline, Red fill
**Usage**: Transfer fuel to aircraft tanks

**Properties:**
- **Usable**: Yes (transfer contents)
- **Action**: "transfer_fuel"
- **Priority**: High value cargo
- **Handling**: Fragile - avoid impacts
- **Storage**: Store in cool, dry area of cargo hold

### Books (Non-Usable)
**Dimensions**: 1x1 grid cell (8x8 pixels)
**Weight**: 2.0 lbs per crate
**Contents**: 1 book collection
**Colors**: Brown outline, Tan fill
**Usage**: Cargo only (historical/educational value)

**Properties:**
- **Usable**: No (decorative cargo)
- **Compact**: Smallest crate type
- **Value**: Cultural/educational worth
- **Handling**: Delicate - protect from moisture
- **Storage**: Can fill small spaces efficiently

### Medical Supplies (Usable)
**Dimensions**: 2x2 grid cells (16x16 pixels)
**Weight**: 5.0 lbs per kit
**Contents**: 1 complete medical kit
**Colors**: Red outline, Light pink fill
**Usage**: Add to ship's medical inventory

**Properties:**
- **Usable**: Yes (add medical supplies)
- **Action**: "add_medical_supplies"
- **Critical**: Emergency medical equipment
- **Handling**: Fragile - contains glass vials
- **Storage**: Accessible location recommended

### Food Rations (Usable)
**Dimensions**: 3x1 grid cells (24x8 pixels)
**Weight**: 12.0 lbs per crate
**Contents**: 7 days crew rations
**Colors**: Green outline, Light green fill
**Usage**: Extend crew supply duration

**Properties:**
- **Usable**: Yes (add food supplies)
- **Action**: "add_food"
- **Essential**: Crew survival supplies
- **Handling**: Heavy - use caution
- **Storage**: Keep dry and secure

### Spare Parts (Non-Usable)
**Dimensions**: 2x2 grid cells (16x16 pixels)
**Weight**: 15.0 lbs per set
**Contents**: 1 engine parts set
**Colors**: Gray outline, Light gray fill
**Usage**: Cargo only (maintenance supplies)

**Properties:**
- **Usable**: No (maintenance cargo)
- **Heavy**: Heaviest standard crate
- **Value**: Critical for maintenance
- **Handling**: Robust - metal components
- **Storage**: Secure against shifting

### Luxury Goods (Non-Usable)
**Dimensions**: 1x2 grid cells (8x16 pixels)
**Weight**: 3.0 lbs per crate
**Contents**: 1 luxury item crate
**Colors**: Gold outline, Light yellow fill
**Usage**: Cargo only (high-value trade goods)

**Properties:**
- **Usable**: No (trade cargo)
- **Valuable**: High monetary worth
- **Compact**: Efficient use of space
- **Handling**: Delicate - valuable contents
- **Storage**: Secure location preferred

---

## Loading Procedures

### Standard Loading Operation

**Step 1: Cargo Identification**
1. **Refresh Loading Bay**: Press [Refresh] when stationary
2. **Survey Available Cargo**: Review crate types and quantities
3. **Plan Arrangement**: Consider weight distribution
4. **Select Priority Items**: Focus on usable cargo first

**Step 2: Winch Positioning**
1. **Move to Cargo**: Position winch over desired crate
2. **Fine Adjustment**: Use brief button presses for precision
3. **Vertical Alignment**: Extend cable to crate level
4. **Proximity Check**: Ensure hook is near crate center

**Step 3: Attachment Process**
1. **Select Crate**: Click on target crate to highlight
2. **Position Hook**: Lower cable to crate top surface
3. **Press [Attach]**: Connect cable to selected crate
4. **Verify Connection**: Check for attachment confirmation

**Step 4: Transfer Operation**
1. **Lift Cargo**: Retract cable to raise attached crate
2. **Horizontal Movement**: Move winch to cargo hold area
3. **Position Carefully**: Plan placement location
4. **Lower to Position**: Extend cable to place crate

**Step 5: Detachment Process**
1. **Verify Support**: Ensure crate has stable support
2. **Check Clearance**: No overlapping with existing cargo
3. **Press [Detach]**: Release cable from crate
4. **Confirm Placement**: Verify crate is properly positioned

### Advanced Loading Techniques

**Stacking Strategy**
- **Bottom Layer**: Place largest, heaviest crates first
- **Support Check**: Ensure adequate support for upper layers
- **Stability**: Verify each layer before adding next
- **Balance**: Maintain left-right weight distribution

**Space Optimization**
- **Tetris Principle**: Fit crates together efficiently
- **Gap Minimization**: Reduce wasted space
- **Access Planning**: Keep usable crates accessible
- **Future Loading**: Reserve space for additional cargo

**Weight Distribution**
- **Center Balance**: Keep heavy items near center
- **Lateral Balance**: Balance left-right loading
- **Forward/Aft**: Consider longitudinal weight distribution
- **Center of Gravity**: Monitor ship balance effects

---

## Unloading Operations

### Selective Unloading

**Cargo Access**
1. **Identify Target**: Select crate to be unloaded
2. **Check Accessibility**: Ensure clear path for winch
3. **Remove Obstructions**: Unload blocking cargo first
4. **Plan Sequence**: Work from top to bottom

**Systematic Unloading**
1. **Top Layer First**: Remove uppermost crates
2. **Maintain Stability**: Don't destabilize remaining cargo
3. **Transfer to Loading Bay**: Use as temporary staging
4. **Final Positioning**: Place for easy retrieval

### Emergency Unloading

**Rapid Weight Reduction**
1. **Priority Assessment**: Identify non-essential cargo
2. **Quick Access**: Focus on easily accessible items
3. **Bulk Removal**: Remove largest, heaviest items first
4. **Safety First**: Maintain safe loading practices

**Critical Situation Unloading**
- **Emergency Landing**: Reduce landing weight quickly
- **Damage Control**: Remove damaged or hazardous cargo
- **Center of Gravity**: Correct dangerous balance conditions
- **Time Critical**: Work efficiently but safely

---

## Cargo Usage

### Usable Cargo Types

**Fuel Canisters**
- **Location**: Must be in cargo hold
- **Condition**: Not attached to winch
- **Action**: Select crate and press [Use]
- **Effect**: Transfers 1.0 gallon to fuel tanks
- **Priority**: Aft tank filled first, then forward
- **Result**: Crate disappears after use

**Medical Supplies**
- **Location**: Must be in cargo hold
- **Condition**: Not attached to winch  
- **Action**: Select crate and press [Use]
- **Effect**: Adds medical kit to ship inventory
- **Benefit**: Enhances crew health and safety
- **Result**: Crate disappears after use

**Food Rations**
- **Location**: Must be in cargo hold
- **Condition**: Not attached to winch
- **Action**: Select crate and press [Use]
- **Effect**: Extends crew food supply by 7 days
- **Benefit**: Increases mission endurance
- **Result**: Crate disappears after use

### Usage Restrictions

**Location Requirements**
- **Cargo Hold Only**: Usable items must be in permanent storage
- **Loading Bay Exclusion**: Cannot use items in staging area
- **Accessibility**: Crates must be selectable

**State Requirements**
- **Not Attached**: Cannot use crates attached to winch
- **Stable Position**: Crates must be properly placed
- **System Status**: Ship systems must be operational

**Usage Button States**
- **Enabled**: Yellow text, clickable
- **Disabled**: Gray text, no function
- **Conditions**: All requirements must be met

---

## Weight and Balance

### Center of Gravity Effects

**Cargo Loading Impact**
- **Forward Loading**: Shifts CG forward (nose-heavy)
- **Aft Loading**: Shifts CG aft (tail-heavy)
- **Lateral Loading**: Affects roll characteristics
- **Vertical Loading**: Influences stability

**Flight Characteristics**
- **Forward CG**: More stable, requires up elevator
- **Aft CG**: Less stable, can become uncontrollable
- **Balanced CG**: Optimal handling and fuel efficiency
- **Extreme CG**: Dangerous flight characteristics

### Loading Strategy for Balance

**Balanced Loading** (Preferred)
- **Center Placement**: Keep heavy items near center
- **Symmetrical**: Balance left and right sides
- **Progressive**: Add cargo gradually
- **Monitor**: Watch for handling changes

**Corrective Loading**
- **Forward Heavy**: Add cargo to aft section
- **Aft Heavy**: Add cargo to forward section
- **Roll Tendency**: Balance lateral loading
- **Weight Limits**: Stay within maximum capacity

### Weight Calculations

**Individual Crate Weights:**
- **Fuel Canister**: 8.0 lbs
- **Books**: 2.0 lbs  
- **Medical Supplies**: 5.0 lbs
- **Food Rations**: 12.0 lbs
- **Spare Parts**: 15.0 lbs
- **Luxury Goods**: 3.0 lbs

**Total Cargo Considerations:**
- **Maximum Capacity**: 500 lbs total cargo
- **Performance Impact**: Heavier loads reduce performance
- **Fuel Consumption**: More weight = higher fuel burn
- **Range Reduction**: Heavy cargo reduces maximum range

---

## Emergency Procedures

### Cargo Shift Emergency

**Symptoms:**
- Sudden handling changes during flight
- Unusual roll or pitch tendencies
- Cargo noise or movement sounds
- Difficulty maintaining altitude/heading

**Immediate Actions:**
1. **Reduce Speed**: Minimize cargo shift forces
2. **Gentle Maneuvers**: Avoid abrupt control inputs
3. **Level Flight**: Maintain straight and level if possible
4. **Land Soon**: Plan immediate landing

**Post-Landing Assessment:**
1. **Inspect Cargo**: Check for shifted or damaged items
2. **Redistribute**: Reload cargo properly
3. **Secure Items**: Ensure proper placement
4. **Test Flight**: Brief test before continuing

### Winch System Failure

**Cable Failure:**
1. **Stop Movement**: Immediately halt winch operations
2. **Assess Damage**: Determine extent of failure
3. **Manual Recovery**: Attempt manual cable retrieval
4. **Alternative Methods**: Use external loading equipment

**Rail System Jam:**
1. **Stop Operations**: Cease winch movement
2. **Check Obstruction**: Look for physical blockages
3. **Manual Movement**: Try gentle manual positioning
4. **System Reset**: Restart cargo scene if needed

**Power Failure:**
1. **Check Electrical**: Verify power to cargo systems
2. **Battery Status**: Ensure adequate power supply
3. **Manual Override**: Use manual controls if available
4. **Emergency Lighting**: Ensure adequate workspace lighting

### Hazardous Cargo Situations

**Fuel Canister Leak:**
1. **Immediate Isolation**: Remove from other cargo
2. **Ventilation**: Ensure good air circulation
3. **Fire Prevention**: Eliminate ignition sources
4. **Safe Disposal**: Remove from aircraft safely

**Medical Supply Contamination:**
1. **Isolate Affected Items**: Separate contaminated supplies
2. **Assess Remaining**: Check other medical supplies
3. **Document Loss**: Note reduced medical capability
4. **Replacement Priority**: Seek replacement supplies

**Damaged Spare Parts:**
1. **Assess Damage**: Determine if parts are still usable
2. **Sort Components**: Separate damaged from good parts
3. **Alternative Sources**: Identify replacement options
4. **Mission Impact**: Evaluate effect on maintenance capability

---

## Troubleshooting

### Winch Movement Issues

**Winch Not Moving:**
- **Check Focus**: Ensure winch control buttons are focused
- **Button State**: Verify buttons are enabled
- **Power System**: Check electrical system status
- **Obstruction**: Look for physical blockages on rail

**Slow Movement:**
- **Button Hold**: Ensure continuous button press
- **System Load**: Check if other systems are active
- **Mechanical Issues**: Listen for unusual sounds
- **Calibration**: Movement speed may vary

**Erratic Movement:**
- **Input Method**: Try different control method
- **System Refresh**: Exit and re-enter cargo scene
- **Focus Issues**: Cycle through widget focus
- **Mouse vs Keyboard**: Switch input methods

### Attachment Problems

**Cannot Attach to Crate:**
- **Crate Selection**: Ensure crate is properly selected
- **Hook Position**: Verify cable is at crate level
- **Proximity**: Hook must be near crate center
- **System State**: Check if winch already has attachment

**Attachment Fails:**
- **Crate Access**: Ensure crate is not obstructed
- **Cable Extension**: Verify adequate cable length
- **System Status**: Check for error messages
- **Retry Process**: Try attachment sequence again

**Unexpected Detachment:**
- **Support Issues**: Crate may lack proper support
- **Collision**: Crate may be overlapping others
- **System Glitch**: Restart cargo scene
- **Valid Position**: Ensure crate is in valid area

### Cargo Placement Issues

**Cannot Place Crate:**
- **Area Boundaries**: Ensure placement within cargo areas
- **Collision Check**: Verify no overlap with existing cargo
- **Support Requirements**: Bottom must be supported
- **Space Available**: Confirm adequate space

**Crate Falls Through Floor:**
- **Physics Update**: System may need physics refresh
- **Invalid Position**: Crate placed outside valid area
- **Collision Detection**: System may have missed collision
- **Restart Scene**: Exit and re-enter cargo scene

**Visual Display Problems:**
- **Rendering Issues**: Graphics may need refresh
- **Z-Order Problems**: Crates may appear in wrong layer
- **Color Display**: Check monitor color settings
- **Scaling Issues**: UI may have scaling problems

### Usage System Problems

**Use Button Disabled:**
- **Location Check**: Crate must be in cargo hold
- **Attachment Status**: Crate cannot be attached to winch
- **Crate Type**: Only usable crates can be used
- **System State**: Check overall system status

**Use Action Fails:**
- **Inventory Full**: Target system may be at capacity
- **Crate Missing**: Selected crate may have disappeared
- **System Error**: Try reselecting crate
- **Game State**: Check overall game status

**Phantom Crate Issues:**
- **Restart Scene**: Exit and re-enter cargo management
- **Save/Load**: Save game and reload
- **System Reset**: Restart entire application
- **State Cleanup**: Use refresh to clear loading bay

---

## Best Practices

### Pre-Flight Planning

**Cargo Selection Strategy:**
1. **Mission Requirements**: Select cargo based on flight goals
2. **Usable Items Priority**: Load fuel, medical, food first
3. **Weight Considerations**: Balance performance vs. cargo load
4. **Space Efficiency**: Plan cargo arrangement for optimal use
5. **Emergency Supplies**: Always carry medical and food

**Loading Sequence:**
1. **Heavy Items First**: Load spare parts and food rations early
2. **Bottom Layer**: Establish stable foundation
3. **Progressive Loading**: Add layers systematically
4. **Balance Monitoring**: Check weight distribution continuously
5. **Final Verification**: Confirm all cargo is secure

### Operational Efficiency

**Winch Operation:**
- **Smooth Movements**: Use steady, controlled motions
- **Plan Ahead**: Think several moves in advance
- **Minimize Repositioning**: Reduce unnecessary movements
- **Practice Precision**: Develop fine control skills
- **Safety First**: Always prioritize safe operations

**Cargo Arrangement:**
- **Accessibility**: Keep frequently used items accessible
- **Stability**: Ensure all cargo is properly supported
- **Protection**: Shield delicate items from damage
- **Emergency Access**: Plan for emergency unloading
- **Weight Distribution**: Maintain proper balance

### Maintenance and Care

**System Maintenance:**
- **Regular Inspection**: Check winch and rail system
- **Lubrication**: Ensure smooth movement
- **Cable Condition**: Inspect cable for wear
- **Electrical Systems**: Verify power connections
- **Safety Equipment**: Test emergency procedures

**Cargo Care:**
- **Handling Procedures**: Follow proper lifting techniques
- **Storage Conditions**: Maintain appropriate environment
- **Inventory Management**: Track cargo contents and condition
- **Documentation**: Record cargo movements and usage
- **Quality Control**: Monitor for damage or deterioration

### Advanced Techniques

**Expert Loading:**
- **3D Thinking**: Consider vertical stacking opportunities
- **Tetris Skills**: Develop spatial arrangement abilities
- **Physics Understanding**: Learn collision and support rules
- **Speed Loading**: Practice for emergency situations
- **Creative Solutions**: Think outside conventional arrangements

**Optimization Strategies:**
- **Weight-to-Value**: Prioritize high-value, low-weight cargo
- **Multi-Mission Planning**: Load cargo for multiple stops
- **Fuel Efficiency**: Balance cargo load with fuel consumption
- **Performance Envelope**: Understand aircraft limitations
- **Contingency Planning**: Always have backup arrangements

### Safety Reminders

**Critical Safety Rules:**
1. **Never operate winch during flight**
2. **Always secure cargo before takeoff**
3. **Monitor weight and balance continuously**
4. **Keep emergency supplies accessible**
5. **Inspect cargo regularly during flight**

**Emergency Preparedness:**
- **Know your limits**: Understand maximum cargo capacity
- **Plan escape routes**: Ensure emergency access to critical controls
- **Practice procedures**: Regular emergency drills
- **Backup plans**: Always have alternative arrangements
- **Communication**: Keep crew informed of cargo status

The cargo management system is a powerful tool for airship operations when used properly. Master these procedures to maximize your aircraft's cargo capability while maintaining safe flight operations.

---

*End of Manual*

**Remember:** Proper cargo management is essential for safe and efficient airship operations. When in doubt, prioritize safety over cargo capacity.
