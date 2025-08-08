# Airship Zero - Navigation User Manual

**Steam & Copper Dreams Edition**  
*The Complete Guide to Navigation Operations*

---

## Table of Contents

1. [Overview](#overview)
2. [Navigation Interface Layout](#navigation-interface-layout)
3. [Position Information](#position-information)
4. [World Map Display](#world-map-display)
5. [Map Controls](#map-controls)
6. [Navigation Techniques](#navigation-techniques)
7. [Position Tracking](#position-tracking)
8. [Map Interaction](#map-interaction)
9. [Navigation Planning](#navigation-planning)
10. [Dead Reckoning](#dead-reckoning)
11. [Wind Effects](#wind-effects)
12. [Navigation Tips](#navigation-tips)

---

## Overview

The Navigation scene provides comprehensive geographic navigation capabilities for your airship. This station displays a detailed world map with your current position, heading, and movement tracking. Use this interface for route planning, position monitoring, and geographic awareness during flight operations.

**Key Features:**
- Real-time world map display
- Current position and heading indicator
- Interactive map controls (zoom, pan, center)
- Ground speed and track monitoring
- Wind drift visualization
- Geographic coordinate display
- Route planning capabilities (future enhancement)

---

## Navigation Interface Layout

The navigation interface centers around the world map with essential information displays:

```
┌─────────── NAVIGATION ─────────────┐
│ POS: 40.7128°N 74.0060°W  HDG: 045°  GS: 82 │
│                                        │
│     ┌──── World Map Display ────┐     │
│     │                           │     │
│     │         ▲ ●               │     │
│     │      HEADING SHIP          │     │
│     │                           │     │
│     │   ~~~~ OCEAN ~~~~        │     │
│     │                           │     │
│     │  ████ CONTINENTS ████     │     │
│     │                           │     │
│     │                           │     │
│     └───────────────────────────┘     │
│                                        │
│ [< [  [+]  [-]  [Center]      ] >]    │
└────────────────────────────────────────┘
```

---

## Position Information

### Geographic Coordinates
**POS: 40.7128°N 74.0060°W** - Current Position

**Coordinate Format:**
- **Latitude**: North/South position (±90°)
  - **N**: North of equator (positive)
  - **S**: South of equator (negative)
- **Longitude**: East/West position (±180°)
  - **E**: East of Prime Meridian (positive)
  - **W**: West of Prime Meridian (negative)

**Precision**: Displayed to 4 decimal places (~10 meter accuracy)

### Heading Information
**HDG: 045°** - Current Magnetic Heading

**Heading Reference:**
- **000°**: North
- **090°**: East  
- **180°**: South
- **270°**: West

**Updates**: Real-time based on rudder input and autopilot commands

### Speed Information
**GS: 82** - Ground Speed (knots)

**Speed Components:**
- **True Airspeed**: Actual speed through air mass
- **Wind Component**: Wind effect on ground track
- **Ground Speed**: Actual speed over ground (displayed)

**Factors Affecting Ground Speed:**
- Engine power and airspeed
- Wind direction and velocity
- Air density (altitude effects)

---

## World Map Display

### Map Features

**Geographic Elements:**
- **Ocean Areas**: Dark blue regions representing water bodies
- **Continental Masses**: Brown/green regions showing land masses
- **Coastlines**: Boundaries between land and sea
- **Major Geographic Features**: Simplified representation of Earth

**Position Indicators:**
- **Red Dot (●)**: Current airship position
- **Heading Line (▲)**: Current heading direction (12-pixel length)
- **Movement Trail**: Historical track (future enhancement)

### Map Coordinate System

**Projection**: Simplified cylindrical projection
- **Longitude**: -180° to +180° (left to right across map)
- **Latitude**: +90° to -90° (top to bottom of map)
- **Map Size**: 640x320 pixels (2:1 aspect ratio)

**Coverage**: Global coverage of Earth's surface
- **Full World**: All continents and oceans represented
- **Real Coordinates**: Accurate latitude/longitude mapping

---

## Map Controls

### Zoom Controls

**[+] Zoom In**
- **Function**: Increases map magnification
- **Range**: 0.25x to 4.0x zoom levels
- **Increment**: 1.5x per zoom step
- **Keyboard**: `+` or `=` key
- **Mouse**: Mouse wheel up

**[-] Zoom Out**
- **Function**: Decreases map magnification  
- **Range**: 0.25x to 4.0x zoom levels
- **Decrement**: 1/1.5x per zoom step
- **Keyboard**: `-` key
- **Mouse**: Mouse wheel down

### Pan Controls

**Mouse Dragging**:
1. **Click and Hold**: Left mouse button on map area
2. **Drag**: Move mouse to pan map view
3. **Release**: Stop panning operation

**Keyboard Panning**:
- **Left Arrow**: Pan west (20 pixels/zoom level)
- **Right Arrow**: Pan east (20 pixels/zoom level)  
- **Up Arrow**: Pan north (20 pixels/zoom level)
- **Down Arrow**: Pan south (20 pixels/zoom level)

### Center Control

**[Center] Button**
- **Function**: Centers map on current airship position
- **Keyboard**: `C` key
- **Effect**: Resets pan offsets to zero
- **Usage**: Quick return to current location

---

## Navigation Techniques

### Visual Navigation

**Landmark Identification**:
- **Coastlines**: Major navigation references
- **Continental Boundaries**: Large-scale position references
- **Ocean Crossings**: Open water navigation
- **Geographic Features**: Major landmasses for orientation

**Position Estimation**:
- **Dead Reckoning**: Calculate position from known starting point
- **Pilotage**: Navigate by visual reference to landmarks
- **Electronic Position**: Use displayed coordinates
- **Cross-Reference**: Compare multiple navigation methods

### Route Planning

**Basic Navigation Planning**:
1. **Current Position**: Note starting coordinates
2. **Destination**: Identify target location on map
3. **Course Line**: Determine great circle or rhumb line route
4. **Distance**: Estimate total distance
5. **Wind Consideration**: Account for wind effects
6. **Waypoints**: Identify intermediate navigation points

**Navigation Calculations**:
- **Heading**: Direction to steer accounting for wind
- **Time**: Estimated flight time based on ground speed
- **Fuel**: Required fuel for route plus reserves
- **Weather**: Wind and weather considerations

---

## Position Tracking

### Real-Time Tracking

**Position Updates**:
- **Frequency**: Continuous real-time updates
- **Accuracy**: Based on simulated GPS precision
- **Display**: Red dot indicator on map
- **Coordinates**: Numeric display in header

**Heading Indication**:
- **Visual**: Red line extending from position dot
- **Length**: 12 pixels indicating direction
- **Updates**: Real-time based on actual heading
- **Reference**: Magnetic heading direction

### Movement Monitoring

**Ground Speed Tracking**:
- **Calculation**: True airspeed plus wind component
- **Display**: Real-time numeric readout
- **Units**: Knots (nautical miles per hour)
- **Accuracy**: Updates with engine and wind changes

**Track vs. Heading**:
- **Heading**: Direction airship is pointed
- **Track**: Actual path over ground (affected by wind)
- **Drift**: Difference between heading and track
- **Correction**: Adjust heading to maintain desired track

---

## Map Interaction

### Zoom Operations

**Zoom Levels**:
- **0.25x**: Maximum zoom out (entire world visible)
- **0.5x**: Continental scale view
- **1.0x**: Regional scale view (default)
- **2.0x**: Local area detail
- **4.0x**: Maximum zoom in (high detail)

**Zoom Behavior**:
- **Center Point**: Zoom centers on current view center
- **Smooth Steps**: 1.5x increments for natural feel
- **Limits**: Automatic limits prevent over-zoom
- **Performance**: Map rendering optimized for all zoom levels

### Panning Operations

**Pan Sensitivity**:
- **Mouse**: Direct 1:1 pixel relationship
- **Keyboard**: 20 pixels per keypress
- **Zoom Compensation**: Larger map movements at lower zoom
- **Smooth Response**: Immediate visual feedback

**Pan Limits**:
- **Map Boundaries**: Cannot pan beyond world map edges
- **Viewport Clipping**: Ensures map always fills display area
- **Auto-Centering**: Center button returns to ship position

### Mouse Interaction

**Click Detection**:
- **Widget Areas**: Buttons and controls respond to clicks
- **Map Area**: Non-widget clicks initiate pan operations
- **Drag Detection**: Distinguish between clicks and drags
- **Multi-Button**: Left click for pan, wheel for zoom

---

## Navigation Planning

### Course Planning

**Great Circle Navigation**:
- **Shortest Distance**: Most direct route between two points
- **Course Changes**: Heading changes along route
- **Distance Calculation**: True distance over Earth's surface
- **Implementation**: Future enhancement for route planning

**Rhumb Line Navigation**:
- **Constant Heading**: Single heading maintained throughout flight
- **Longer Distance**: Greater distance than great circle
- **Simpler Navigation**: Easier to fly and navigate
- **Current Method**: Manual heading selection on Bridge

### Waypoint Navigation

**Navigation Points** (Future Enhancement):
- **Departure Point**: Starting location
- **Intermediate Waypoints**: Course change points
- **Destination**: Final arrival point
- **Alternate**: Emergency/weather alternate destinations

**Navigation Aids**:
- **Visual Landmarks**: Coastlines, major geographic features
- **Electronic Position**: Coordinate-based navigation
- **Dead Reckoning**: Time/distance/heading calculations
- **Wind Triangles**: Wind effect calculations

---

## Dead Reckoning

### Basic Dead Reckoning

**Required Information**:
- **Starting Position**: Known departure coordinates
- **Time**: Elapsed time since departure
- **Heading**: Average heading maintained
- **Speed**: Average ground speed

**DR Calculation**:
1. **Distance**: Ground speed × time = distance traveled
2. **Course**: Convert heading to true course
3. **Position**: Plot distance and direction from start point
4. **Update**: Regular position updates and corrections

### Wind Triangle Navigation

**Wind Effect Calculation**:
- **True Airspeed**: Speed through air mass
- **Wind Vector**: Wind direction and velocity
- **Ground Speed**: Resultant speed over ground
- **Drift Angle**: Difference between heading and track

**Wind Correction**:
- **Crab Angle**: Heading adjustment to maintain track
- **Track**: Desired path over ground
- **Heading**: Actual direction to point airship
- **Ground Speed**: Resultant forward progress

---

## Wind Effects

### Wind Display

**Current Wind Information** (Bridge Scene):
- **Wind Speed**: Displayed in environment data
- **Wind Direction**: Meteorological convention (direction FROM)
- **Wind Component**: Effect on current heading
- **Ground Speed**: Resultant speed including wind

### Wind Triangles

**Wind Components**:
- **Headwind**: Reduces ground speed
- **Tailwind**: Increases ground speed  
- **Crosswind**: Causes drift off course
- **Variable Wind**: Changes with altitude and time

**Navigation Solutions**:
- **Crab Correction**: Point into wind to maintain track
- **Wind Allowance**: Pre-flight planning for wind effects
- **Course Correction**: Adjust heading during flight
- **Time Estimation**: Adjust ETAs for wind effects

---

## Navigation Tips

### Efficient Navigation

**Map Usage**:
- **Regular Monitoring**: Check position frequently
- **Zoom Appropriately**: Use detail level suited to navigation phase
- **Pan for Context**: View surrounding area for landmarks
- **Center Frequently**: Keep current position in view

**Position Awareness**:
- **Coordinate Monitoring**: Watch numeric position display
- **Heading Tracking**: Monitor heading changes
- **Speed Awareness**: Note ground speed variations
- **Wind Effects**: Observe drift from wind

### Navigation Best Practices

**Pre-Flight Planning**:
- **Route Study**: Examine proposed route on map
- **Landmark Identification**: Note prominent geographic features
- **Distance Estimation**: Calculate approximate flight time
- **Weather Consideration**: Account for wind in planning

**In-Flight Navigation**:
- **Regular Position Checks**: Verify position every 5-10 minutes
- **Course Corrections**: Make small heading adjustments
- **Wind Updates**: Monitor ground speed for wind changes
- **Landmark Verification**: Cross-check position with visual references

### Emergency Navigation

**Lost Position Procedures**:
1. **Last Known Position**: Recall last confirmed position
2. **Time Factor**: Calculate maximum possible distance traveled
3. **Search Pattern**: Systematic search for landmarks
4. **Electronic Backup**: Use coordinate display for position
5. **Help Resources**: Consider emergency navigation aids

**Navigation Backup**:
- **Multiple Methods**: Use both visual and electronic navigation
- **Regular Updates**: Frequent position confirmations
- **Landmark Chain**: Continuous landmark identification
- **Communication**: Radio navigation aids (future enhancement)

---

## Keyboard Shortcuts

| Key | Function |
|-----|----------|
| **+** or **=** | Zoom in |
| **-** | Zoom out |
| **C** | Center map on position |
| **←** | Pan west |
| **→** | Pan east |
| **↑** | Pan north |
| **↓** | Pan south |
| **Tab** | Cycle widget focus forward |
| **Shift+Tab** | Cycle widget focus backward |
| **Enter** | Activate focused widget |
| **Space** | Activate focused widget |
| **[** | Previous scene (Engine Room) |
| **]** | Next scene (Fuel) |
| **Esc** | Return to main menu |

---

## Mouse Controls

| Action | Function |
|--------|----------|
| **Left Click** | Select widget or start map pan |
| **Click + Drag** | Pan map view |
| **Mouse Wheel Up** | Zoom in |
| **Mouse Wheel Down** | Zoom out |
| **Release Click** | End pan operation |

---

## Scene Navigation

The navigation scene connects to all other airship stations:

- **Previous ([)**: Engine Room Scene
- **Next (])**: Fuel Scene  
- **Direct Access**: Use scene selection buttons or keyboard shortcuts

Use navigation for route planning and position awareness, then return to other scenes for flight operations and system management.

---

## Navigation Reference

### Coordinate Examples

**Major Cities**:
- **New York**: 40.7128°N, 74.0060°W
- **London**: 51.5074°N, 0.1278°W
- **Tokyo**: 35.6762°N, 139.6503°E
- **Sydney**: 33.8688°S, 151.2093°E

**Geographic Features**:
- **Equator**: 0° Latitude
- **Prime Meridian**: 0° Longitude
- **North Pole**: 90°N Latitude
- **South Pole**: 90°S Latitude

### Navigation Formulas

**Distance Calculation** (Approximate):
- **Latitude**: 1° ≈ 60 nautical miles
- **Longitude**: 1° ≈ 60 × cos(latitude) nautical miles
- **Nautical Mile**: 1,852 meters
- **Statute Mile**: 1.15 × nautical miles

**Time/Speed/Distance**:
- **Time = Distance ÷ Speed**
- **Distance = Speed × Time**  
- **Speed = Distance ÷ Time**

---

## Future Enhancements

**Planned Features**:
- **Waypoint System**: Set and navigate to specific coordinates
- **Route Planning**: Pre-planned multi-waypoint routes
- **Navigation Aids**: Radio beacons and navigation stations
- **Weather Overlay**: Wind and weather pattern display
- **Track History**: Historical flight path display
- **Chart Symbols**: Aviation navigation symbols and markers

**Advanced Navigation**:
- **GPS Precision**: Enhanced coordinate accuracy
- **Electronic Charts**: Detailed aviation charts
- **Approach Procedures**: Landing approach guidance
- **Traffic Display**: Other aircraft position display (multiplayer)

---

*Navigate with confidence across the vast skies!*

**Airship Zero Development Team**  
*Steam & Copper Dreams Edition - 2025*
