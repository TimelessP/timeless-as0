# Airship Zero - Bridge User Manual

**Steam & Copper Dreams Edition**  
*The Complete Guide to Flight Operations*

---

## Table of Contents

1. [Overview](#overview)
2. [Bridge Layout](#bridge-layout)
3. [Flight Instruments](#flight-instruments)
4. [Engine Monitoring](#engine-monitoring)
5. [System Status](#system-status)
6. [Navigation Controls](#navigation-controls)
7. [Flight Controls](#flight-controls)
8. [Attitude Indicator](#attitude-indicator)
9. [Autopilot Operations](#autopilot-operations)
10. [Altitude Control](#altitude-control)
11. [Emergency Procedures](#emergency-procedures)
12. [Tips for Realistic Flight](#tips-for-realistic-flight)

---

## Overview

The Bridge is your primary flight control interface, where you monitor all critical systems and control your airship's flight. This centralized command station provides real-time information about navigation, engine performance, and system status, while offering both manual and automated flight controls.

**Key Features:**
- Real-time flight instruments
- Engine performance monitoring
- Integrated autopilot system
- Manual flight controls
- System status monitoring
- Altitude control with smooth automation

---

## Bridge Layout

The bridge interface is organized into logical sections for efficient operation:

```
┌─────────────── BRIDGE ───────────────┐
│ ALT: 1250 ft    IAS: 85 kts   HDG: 045° │
│ RPM: 2650      MAP: 24.5"    FF: 12.8  │
│ [BAT A: ON]   [PUMPS: AUTO]  [A/P: OFF] │
│ [NAV: MANUAL]              [HDG: 045]  │
│ RUD: +2.5°                             │
│ ALTITUDE ━━━━━━━━━━━━━━━━ 1250 ft       │
│                                        │
│    ┌─── Attitude Indicator ───┐        │
│    │        ═══════════       │        │
│    │    ┌─────┬─────┐         │        │
│    │    │ SKY │     │         │        │
│    │ ───┼─────┼─────┼─── ←── │        │
│    │    │     │GRND │         │        │
│    │    └─────┴─────┘         │        │
│    │       P:+2.1°            │        │
│    └─────────────────────────┘        │
│                                        │
│ [< [ ]                        [ ] >]   │
└────────────────────────────────────────┘
```

---

## Flight Instruments

### Primary Navigation Display

**ALT: 1250 ft** - Current Altitude
- Shows your airship's height above sea level
- Critical for navigation and performance planning
- Affects engine performance and air density

**IAS: 85 kts** - Indicated Airspeed
- Airspeed as measured by pitot-static system
- Does not account for altitude/density effects
- Primary reference for flight operations

**HDG: 045°** - Current Heading
- Magnetic heading (0-360°)
- Updates in real-time based on rudder input
- Essential for navigation and autopilot

### True Airspeed Considerations

While not displayed on the bridge, your True Airspeed (TAS) differs from Indicated Airspeed at altitude:
- **Sea Level**: TAS ≈ IAS
- **5,000 ft**: TAS ~6% higher than IAS
- **10,000 ft**: TAS ~11% higher than IAS
- **15,000 ft**: TAS ~17% higher than IAS

---

## Engine Monitoring

### Engine Performance Indicators

**RPM: 2650** - Engine Revolutions Per Minute
- Normal cruise: 2200-2700 RPM
- Maximum: 2800 RPM
- Affected by throttle, propeller pitch, and altitude

**MAP: 24.5"** - Manifold Absolute Pressure
- Measures engine power output
- Decreases with altitude
- Normal cruise: 20-28" Hg

**FF: 12.8** - Fuel Flow (Gallons Per Hour)
- Current engine fuel consumption
- Varies with throttle, mixture, and engine load
- Typical cruise: 8-15 GPH

### Engine Performance vs. Altitude

As you climb higher, you'll notice:
- **RPM**: May increase due to reduced prop load
- **MAP**: Decreases with atmospheric pressure
- **Power**: Significant reduction above 5,000 ft
- **Fuel Flow**: Generally decreases with reduced power

---

## System Status

### Battery Status
**[BAT A: ON]** - Battery A Switch
- Click to toggle battery power
- Essential for all electrical systems
- Monitor voltage and capacity in Engine Room

### Fuel System Status
**[FEED: FA]** - Fuel Feed Status
- **F**: Forward tank feeding engine
- **A**: Aft tank feeding engine
- **--**: No tanks feeding (emergency!)
- Control individual tank feeds in Fuel Scene

### Autopilot Status
**[A/P: OFF]** - Autopilot Engagement
- Click to engage/disengage autopilot
- Works with current navigation mode
- Provides smooth altitude and heading control

---

## Navigation Controls

### Navigation Mode Selection
**[NAV: MANUAL]** - Current Navigation Mode

**Available Modes:**
- **MANUAL**: Full manual control via rudder
- **HEADING HOLD**: Autopilot maintains heading
- **ROUTE FOLLOW**: Follow programmed route (future)

### Heading Control
**[HDG: 045]** - Target Heading Entry
- Click to activate text input
- Enter desired heading (0-360°)
- Press Enter to confirm, Escape to cancel
- Automatically engages heading hold when set

---

## Flight Controls

### Manual Rudder Control
**RUD: +2.5°** - Current Rudder Position
- **Range**: -30° to +30°
- **Left Arrow**: Apply left rudder (-2°)
- **Right Arrow**: Apply right rudder (+2°)
- Only active in MANUAL navigation mode

### Rudder Response
- **Immediate**: In manual mode
- **Gradual**: When autopilot engaged
- **Speed Dependent**: More effective at higher speeds

---

## Altitude Control

### Altitude Slider
**ALTITUDE ━━━━━━━━━━━━━━━━ 1250 ft**

**Range**: 0 to 4,000 feet above sea level

**Control Methods:**
- **Mouse**: Click and drag slider
- **Keyboard**: Plus (+) and Minus (-) keys
- **Precision**: 40-foot increments

### Automatic Altitude Control

When you set a new altitude target:
1. **Autopilot Engages**: Automatically enables altitude hold
2. **Smooth Approach**: Uses realistic climb/descent rates
3. **Smart Easing**: Slows approach near target altitude

**Climb/Descent Rates:**
- **Far from target (>200 ft)**: 150 ft/min
- **Medium distance (50-200 ft)**: 80 ft/min
- **Close approach (10-50 ft)**: 30 ft/min
- **Final approach (<10 ft)**: 10 ft/min with easing
- **Precision lock**: Snaps to target within 1 foot

---

## Attitude Indicator

The artificial horizon shows your airship's attitude relative to the natural horizon.

### Visual Elements

**Sky/Ground Display:**
- **Blue**: Sky (upper portion)
- **Brown**: Ground (lower portion)
- **White Line**: Artificial horizon

**Aircraft Symbol:**
- **Golden Wings**: Fixed aircraft reference
- **Center Dot**: Aircraft center point

**Pitch Ladder:**
- **Tick Marks**: Every 5° of pitch
- **Numbers**: Every 10° (5, 10, 15)
- **Range**: ±15° display

### Reading the Display

**Pitch Indication:**
- **Horizon Above Center**: Nose down attitude
- **Horizon Below Center**: Nose up attitude
- **P:+2.1°**: Numeric pitch readout (bottom-left)

**Fuel Balance Effects:**
- **Forward Heavy**: Nose down pitch
- **Aft Heavy**: Nose up pitch
- **Balanced**: Level flight attitude

---

## Autopilot Operations

### Engaging Autopilot

1. **Set Navigation Mode**: Choose HEADING HOLD or ROUTE FOLLOW
2. **Set Targets**: Enter desired heading and/or altitude
3. **Engage**: Click [A/P: OFF] to activate

### Autopilot Behavior

**Heading Hold:**
- Makes discrete 2° rudder adjustments every 0.5 seconds
- More aggressive corrections for large heading errors
- Gradually centers rudder as target is approached

**Altitude Hold:**
- Uses smooth, realistic climb/descent rates
- Automatically adjusts for optimal approach
- Maintains altitude within ±1 foot of target

### Manual Override

- **Rudder Input**: Only works when autopilot disengaged
- **Emergency**: Press [A/P: ON] to immediately disengage
- **Mode Change**: Switching to MANUAL disables autopilot

---

## Emergency Procedures

### Engine Failure
1. **Monitor RPM**: Watch for dropping RPM
2. **Check Fuel**: Verify fuel feed status
3. **Glide Configuration**: Reduce drag, maintain airspeed
4. **Emergency Landing**: Find suitable landing area

### Fuel Starvation
1. **Feed Status**: Check [FEED: --] display
2. **Fuel Scene**: Navigate to fuel controls
3. **Tank Selection**: Enable feed from available tanks
4. **Engine Restart**: May require engine restart

### Electrical Failure
1. **Battery Check**: Verify [BAT A: ON] status
2. **Engine Room**: Check alternator output
3. **Load Shedding**: Turn off non-essential systems
4. **Battery Conservation**: Prepare for emergency landing

### Autopilot Malfunction
1. **Immediate**: Press [A/P: ON] to disengage
2. **Manual Mode**: Switch to [NAV: MANUAL]
3. **Hand Flying**: Use arrow keys for rudder control
4. **Gradual Movements**: Avoid aggressive control inputs

---

## Tips for Realistic Flight

### Altitude Management
- **Climb Gradually**: Avoid rapid altitude changes
- **Monitor Performance**: Watch for power loss at altitude
- **Mixture Adjustment**: Engine room mixture may need leaning
- **Weather Considerations**: Higher altitudes may have different winds

### Engine Operations
- **Power Settings**: Reduce power before altitude changes
- **Temperature Monitoring**: Watch CHT and EGT in engine room
- **Propeller Pitch**: Optimize for altitude and airspeed
- **Fuel Planning**: Higher altitudes reduce fuel flow

### Navigation Techniques
- **Small Corrections**: Use small rudder inputs for precise navigation
- **Anticipate Winds**: Account for wind drift in navigation
- **Autopilot Usage**: Let autopilot handle routine flying
- **Manual Practice**: Practice manual flying for emergencies

### System Management
- **Regular Monitoring**: Scan all instruments regularly
- **Fuel Balance**: Monitor fuel distribution between tanks
- **Electrical Load**: Keep battery charges healthy
- **Preventive Maintenance**: Address warnings promptly

### Performance Optimization
- **Altitude Selection**: Choose altitude for best performance/winds
- **Speed Management**: Balance speed vs. fuel consumption
- **Weight Distribution**: Use fuel transfer for optimal balance
- **Weather Routing**: Avoid adverse weather when possible

---

## Keyboard Shortcuts

| Key | Function |
|-----|----------|
| **←** | Left rudder (manual mode only) |
| **→** | Right rudder (manual mode only) |
| **+** | Increase target altitude |
| **-** | Decrease target altitude |
| **Tab** | Cycle widget focus forward |
| **Shift+Tab** | Cycle widget focus backward |
| **Enter** | Activate focused widget |
| **Space** | Activate focused widget |
| **[** | Previous scene (circular navigation) |
| **]** | Next scene (circular navigation) |
| **Esc** | Return to main menu (if no active widgets) |

---

## Scene Navigation

The bridge connects to all other airship stations:

- **Previous ([)**: Missions Scene
- **Next (])**: Engine Room Scene
- **Direct Access**: Use scene selection buttons or keyboard shortcuts

Navigate between scenes to access specialized controls for engine management, fuel systems, navigation planning, and other airship operations.

---

*Safe flying, Captain! The skies await your command.*

**Airship Zero Development Team**  
*Steam & Copper Dreams Edition - 2025*
