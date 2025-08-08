# Airship Zero - Engine Room User Manual

**Steam & Copper Dreams Edition**  
*The Complete Guide to Engine Operations*

---

## Table of Contents

1. [Overview](#overview)
2. [Engine Room Layout](#engine-room-layout)
3. [Engine Status Displays](#engine-status-displays)
4. [Temperature Monitoring](#temperature-monitoring)
5. [Pressure Monitoring](#pressure-monitoring)
6. [Engine Controls](#engine-controls)
7. [Engine Operation](#engine-operation)
8. [Engine Schematic](#engine-schematic)
9. [Altitude Effects](#altitude-effects)
10. [Engine Management](#engine-management)
11. [Troubleshooting](#troubleshooting)
12. [Performance Optimization](#performance-optimization)

---

## Overview

The Engine Room is your primary engine management interface, providing comprehensive monitoring and control of your airship's powerplant. This station allows you to monitor all critical engine parameters, adjust engine controls for optimal performance, and diagnose engine problems.

**Key Features:**
- Real-time engine parameter monitoring
- Full engine control capability
- Visual engine schematic display
- Temperature and pressure monitoring
- Altitude-compensated performance tracking
- Engine start/stop controls

---

## Engine Room Layout

The engine room interface is organized for efficient engine management:

```
┌─────────── ENGINE ROOM ─────────────┐
│ ENGINE: RUNNING   RPM: 2650   MP: 24.5 │
│ OIL TEMP: 185°F  CHT: 320°F  EGT: 1450°F │
│ OIL PRESS: 65 PSI FUEL PRESS: 22 PSI    │
│                             FLOW: 12.8 GPH │
│                                          │
│ THROTTLE ████████████░░░░ 75%           │
│ MIXTURE  ████████████████░ 85%          │
│ PROP PITCH ██████████████░░ 80%         │
│                                          │
│ [START]  [STOP]                         │
│                                          │
│     ┌─── Engine Schematic ───┐          │
│     │    ○ ─── [████] ~~~ ~~~│          │
│     │  PROP    ENGINE   EXHAUST         │
│     │         ●                        │
│     │       TEMP                       │
│     └─────────────────────────┘          │
│                                          │
│ [< [ ]                      [ ] >]       │
└──────────────────────────────────────────┘
```

---

## Engine Status Displays

### Primary Engine Status

**ENGINE: RUNNING** - Engine Operating State
- **RUNNING**: Engine is operating normally
- **STOPPED**: Engine is shut down
- Updates immediately based on engine state

**RPM: 2650** - Engine Revolutions Per Minute
- **Range**: 0-2800 RPM
- **Normal Cruise**: 2200-2700 RPM
- **Maximum**: 2800 RPM
- **Affected by**: Throttle, propeller pitch, altitude, fuel flow

**MP: 24.5** - Manifold Absolute Pressure (inches Hg)
- **Sea Level Range**: 14.7-29.9" Hg
- **Cruise Range**: 20-28" Hg
- **Decreases with altitude**
- **Indicates engine power output**

### Engine Performance Factors

**Altitude Effects on RPM:**
- **Higher Altitude**: Engine may achieve higher RPM due to reduced propeller load
- **Thinner Air**: Less air resistance on propeller blades
- **Power Loss**: Overall engine power decreases with altitude

**Throttle Response:**
- **Immediate**: RPM responds quickly to throttle changes
- **Load Dependent**: High propeller pitch creates more load
- **Altitude Dependent**: Performance varies with air density

---

## Temperature Monitoring

### Oil Temperature
**OIL TEMP: 185°F** - Engine Oil Temperature

**Normal Ranges:**
- **Cold Engine**: 100-140°F (startup/warmup)
- **Normal Operating**: 160-220°F
- **Caution Range**: 220-240°F (yellow indicator)
- **Warning Range**: Above 240°F (red indicator)

**Factors Affecting Oil Temperature:**
- Engine load (throttle setting)
- Ambient air temperature
- Oil circulation and cooling
- Engine health and condition

### Cylinder Head Temperature
**CHT: 320°F** - Cylinder Head Temperature

**Normal Ranges:**
- **Normal Operating**: 250-400°F
- **Optimal Cruise**: 300-350°F
- **Caution Range**: 400-420°F
- **Warning Range**: Above 420°F

**Factors Affecting CHT:**
- Engine power setting
- Mixture setting (lean mixtures run hotter)
- Airflow and cooling
- Fuel quality and octane rating

### Exhaust Gas Temperature
**EGT: 1450°F** - Exhaust Gas Temperature

**Normal Ranges:**
- **Normal Operating**: 1200-1600°F
- **Lean Mixture**: Higher EGT (hotter)
- **Rich Mixture**: Lower EGT (cooler)
- **Warning Range**: Above 1650°F

**Mixture Tuning Guide:**
- **Peak EGT**: Maximum temperature = optimal power mixture
- **50°F Rich of Peak**: Best power setting
- **50°F Lean of Peak**: Best economy setting
- **100°F+ Lean**: Danger zone - avoid sustained operation

---

## Pressure Monitoring

### Oil Pressure
**OIL PRESS: 65 PSI** - Engine Oil Pressure

**Normal Ranges:**
- **Idle (low RPM)**: 25-40 PSI
- **Normal Operating**: 50-75 PSI
- **High RPM**: 60-80 PSI
- **Warning**: Below 25 PSI at any RPM above idle

**Factors Affecting Oil Pressure:**
- Engine RPM (higher RPM = higher pressure)
- Oil temperature (hot oil = lower pressure)
- Oil condition and viscosity
- Engine wear and bearing condition

### Fuel Pressure
**FUEL PRESS: 22 PSI** - Engine Fuel Pressure

**Normal Ranges:**
- **Normal Operating**: 18-25 PSI
- **Minimum Required**: 15 PSI for reliable operation
- **Warning**: Below 10 PSI (severe power loss)
- **Critical**: Below 5 PSI (engine failure imminent)

**Factors Affecting Fuel Pressure:**
- Fuel tank levels and feed status
- Fuel pump operation
- Fuel line restrictions or blockages
- Altitude (mechanical fuel pumps affected by air density)

### Fuel Flow
**FLOW: 12.8 GPH** - Fuel Flow Rate (Gallons Per Hour)

**Typical Flow Rates:**
- **Idle**: 3-6 GPH
- **Normal Cruise**: 8-15 GPH
- **Full Power**: 15-20 GPH
- **Economy Cruise**: 6-10 GPH

**Factors Affecting Fuel Flow:**
- Throttle setting
- Mixture setting (rich = higher flow)
- Engine load and RPM
- Altitude and air density

---

## Engine Controls

### Throttle Control
**THROTTLE ████████████░░░░ 75%**

**Function**: Controls engine power output
- **Range**: 0% (idle) to 100% (full power)
- **Mouse**: Click and drag to adjust
- **Keyboard**: +/- keys when focused
- **Effect**: Directly affects manifold pressure and RPM

**Throttle Settings:**
- **Idle**: 0-15% (ground operations, taxi)
- **Cruise**: 60-80% (normal flight operations)
- **Climb**: 85-95% (maximum continuous power)
- **Emergency**: 100% (short duration only)

### Mixture Control
**MIXTURE ████████████████░ 85%**

**Function**: Controls fuel-to-air ratio
- **Range**: 50% (very lean) to 100% (full rich)
- **Sea Level Optimal**: ~85%
- **High Altitude Optimal**: ~70-75%
- **Effect**: Affects power, fuel consumption, and temperatures

**Mixture Settings:**
- **Full Rich (100%)**: Startup, takeoff, emergency
- **Cruise Lean (70-85%)**: Normal flight operations
- **Economy Lean (65-75%)**: Maximum fuel efficiency
- **Emergency Rich (95-100%)**: Cooling for emergencies

### Propeller Pitch Control
**PROP PITCH ██████████████░░ 80%**

**Function**: Controls propeller blade angle
- **Range**: 20% (fine/flat pitch) to 100% (coarse/high pitch)
- **Low Pitch**: Better acceleration, lower top speed
- **High Pitch**: Better efficiency at cruise, higher top speed
- **Effect**: Affects engine load and RPM capability

**Pitch Settings:**
- **Fine Pitch (20-40%)**: Takeoff, climb, acceleration
- **Cruise Pitch (60-80%)**: Normal flight operations
- **Coarse Pitch (80-100%)**: High-speed cruise, descent
- **Optimal Pitch**: Varies with airspeed and altitude

---

## Engine Operation

### Engine Startup Procedure

1. **Pre-Start Checks**:
   - Verify fuel feed enabled (check Bridge fuel status)
   - Ensure battery power available
   - Set mixture to full rich (100%)
   - Set propeller to fine pitch (20-30%)
   - Set throttle to slightly open (10-15%)

2. **Engine Start**:
   - Click [START] button
   - Monitor oil pressure rise
   - Watch for stable RPM increase
   - Check all temperature gauges

3. **Post-Start Checks**:
   - Verify oil pressure above 25 PSI
   - Monitor temperature rise
   - Adjust throttle for desired RPM
   - Lean mixture for efficient operation

### Engine Shutdown Procedure

1. **Pre-Shutdown**:
   - Reduce throttle to idle (0-10%)
   - Allow engine to cool for 1-2 minutes
   - Set mixture to full rich (100%)
   - Monitor temperature decrease

2. **Engine Stop**:
   - Click [STOP] button
   - Monitor RPM decay to zero
   - Verify all pressures drop to zero
   - Set propeller to fine pitch for next start

### Normal Operation Monitoring

**Every 30 Seconds**:
- Scan all temperature gauges
- Check oil and fuel pressures
- Verify fuel flow appropriate for power setting
- Monitor RPM for stability

**Every 5 Minutes**:
- Adjust mixture for altitude changes
- Optimize propeller pitch for current conditions
- Check for any warning indications
- Compare actual vs. expected performance

---

## Engine Schematic

The visual engine schematic provides an at-a-glance view of engine status:

### Schematic Elements

**Propeller (○)**: 
- **Green**: Normal operation
- **Red**: Feathered or malfunction
- **Rotation speed**: Indicates RPM visually

**Engine Block ([████])**:
- **Green**: Engine running normally
- **Gray**: Engine stopped
- **Red**: Engine malfunction or overheat

**Connecting Line (───)**:
- Shows power transmission from engine to propeller
- Visual representation of mechanical connection

**Exhaust (~~~)**:
- **Visible**: Engine running (exhaust gases present)
- **Animated**: Indicates active combustion
- **Intensity**: Varies with engine power

**Temperature Indicator (●)**:
- **Green**: Normal operating temperature
- **Yellow**: Caution range temperatures
- **Red**: Warning range temperatures

---

## Altitude Effects

### Engine Performance vs. Altitude

**Sea Level to 5,000 ft**:
- **Power Loss**: ~3% per 1,000 feet
- **Mixture**: May need slight leaning
- **RPM**: Slight increase possible due to reduced prop load
- **Fuel Flow**: Gradual decrease

**5,000 to 10,000 ft**:
- **Power Loss**: Becomes more noticeable
- **Mixture**: Requires leaning for optimal performance
- **Manifold Pressure**: Significant decrease
- **Temperature**: May run leaner and hotter

**Above 10,000 ft**:
- **Power Loss**: Severe (30%+ loss at 15,000 ft)
- **Mixture**: Requires significant leaning
- **Performance**: Markedly reduced climb and cruise performance
- **Fuel Economy**: May improve due to required power reduction

### Altitude Compensation Techniques

**Mixture Leaning**:
- **Start Rich**: Begin with current mixture setting
- **Lean Gradually**: Reduce mixture in small increments
- **Monitor EGT**: Watch for peak exhaust gas temperature
- **Set for Conditions**: 50°F rich of peak for power, lean of peak for economy

**Propeller Optimization**:
- **Higher Altitude**: May benefit from slightly finer pitch
- **Reduced Air Density**: Propeller encounters less resistance
- **Speed vs. Efficiency**: Balance acceleration vs. top speed needs

---

## Engine Management

### Power Management Strategies

**Cruise Power Setting**:
- **Throttle**: 65-75% for normal cruise
- **Mixture**: Leaned for current altitude
- **Propeller**: Adjusted for optimal efficiency
- **Monitor**: All parameters within normal ranges

**Climb Power Setting**:
- **Throttle**: 85-95% for maximum continuous power
- **Mixture**: Rich enough to keep temperatures normal
- **Propeller**: Fine pitch for better acceleration
- **Watch**: CHT and EGT carefully during sustained climbs

**Descent Power Setting**:
- **Throttle**: Reduced to maintain desired descent rate
- **Mixture**: May need enriching if throttle very low
- **Propeller**: Coarse pitch to maintain engine load
- **Avoid**: Shock cooling from rapid power reductions

### Fuel Efficiency Optimization

**Mixture Leaning Technique**:
1. **Establish Cruise**: Stabilize at desired altitude and airspeed
2. **Current Settings**: Note current fuel flow
3. **Lean Gradually**: Reduce mixture slowly while monitoring EGT
4. **Find Peak**: Note highest EGT temperature
5. **Set Operating Point**: 25-75°F lean of peak for economy

**Propeller Optimization**:
1. **Current Performance**: Note current airspeed and fuel flow
2. **Adjust Pitch**: Try slightly coarser setting
3. **Monitor Results**: Check if fuel flow decreases for same airspeed
4. **Fine Tune**: Make small adjustments for optimal efficiency

---

## Troubleshooting

### High Oil Temperature

**Possible Causes**:
- Excessive engine load (high throttle setting)
- Low oil level or poor oil circulation
- Blocked oil cooler or inadequate cooling airflow
- Engine internal problems

**Corrective Actions**:
1. **Reduce Power**: Lower throttle to reduce engine load
2. **Enrich Mixture**: Cooler-running mixture for temporary relief
3. **Increase Airspeed**: Better cooling airflow
4. **Monitor Closely**: Watch for continued temperature rise
5. **Land If Necessary**: Don't operate with oil temp above 240°F

### Low Oil Pressure

**Possible Causes**:
- Low oil level
- High oil temperature (hot oil = low pressure)
- Oil pump malfunction
- Engine bearing wear

**Corrective Actions**:
1. **Reduce Power**: Lower RPM to minimum required
2. **Monitor Temperature**: Check if oil overheating
3. **Land Immediately**: Low oil pressure can cause engine seizure
4. **Avoid**: High power settings or sustained operation

### Engine Roughness

**Possible Causes**:
- Improper mixture setting
- Fuel contamination or starvation
- Ignition system problems
- Mechanical engine issues

**Corrective Actions**:
1. **Check Mixture**: Try slightly richer setting
2. **Verify Fuel**: Check fuel pressure and flow
3. **Change Power**: Try different throttle setting
4. **Monitor**: Watch all engine parameters closely
5. **Land**: If roughness persists or worsens

### High Fuel Flow

**Possible Causes**:
- Over-rich mixture setting
- Fuel system malfunction
- Engine internal problems

**Corrective Actions**:
1. **Check Mixture**: Verify appropriate setting for altitude
2. **Lean Carefully**: Reduce mixture if over-rich
3. **Monitor Performance**: Watch for power loss
4. **Calculate Range**: Determine if fuel sufficient for flight

---

## Performance Optimization

### Power Setting Charts

**Sea Level Performance**:
- **75% Power**: 24-26" MP, 2400-2600 RPM, 12-14 GPH
- **65% Power**: 22-24" MP, 2200-2400 RPM, 10-12 GPH
- **55% Power**: 20-22" MP, 2000-2200 RPM, 8-10 GPH

**5,000 ft Performance**:
- **75% Power**: 22-24" MP, 2400-2600 RPM, 11-13 GPH
- **65% Power**: 20-22" MP, 2200-2400 RPM, 9-11 GPH
- **55% Power**: 18-20" MP, 2000-2200 RPM, 7-9 GPH

**10,000 ft Performance**:
- **75% Power**: 19-21" MP, 2400-2600 RPM, 10-12 GPH
- **65% Power**: 17-19" MP, 2200-2400 RPM, 8-10 GPH
- **55% Power**: 15-17" MP, 2000-2200 RPM, 6-8 GPH

### Engine Limitations

**Temperature Limits**:
- **Oil Temperature**: Maximum 240°F
- **Cylinder Head Temperature**: Maximum 420°F
- **Exhaust Gas Temperature**: Maximum 1650°F

**Pressure Limits**:
- **Oil Pressure**: Minimum 25 PSI above idle
- **Fuel Pressure**: Minimum 15 PSI for reliable operation
- **Manifold Pressure**: Maximum 29.9" Hg (sea level)

**RPM Limits**:
- **Maximum**: 2800 RPM
- **Normal Maximum**: 2700 RPM for sustained operation
- **Minimum**: 600 RPM for stable idle

---

## Keyboard Shortcuts

| Key | Function |
|-----|----------|
| **+** | Increase focused slider value |
| **-** | Decrease focused slider value |
| **Tab** | Cycle widget focus forward |
| **Shift+Tab** | Cycle widget focus backward |
| **Enter** | Activate focused widget |
| **Space** | Activate focused widget |
| **[** | Previous scene (Bridge) |
| **]** | Next scene (Navigation) |
| **Esc** | Return to main menu |

---

## Scene Navigation

The engine room connects to all other airship stations:

- **Previous ([)**: Bridge Scene
- **Next (])**: Navigation Scene
- **Direct Access**: Use scene selection buttons or keyboard shortcuts

Monitor engine parameters continuously, but don't forget to check other systems regularly for complete situational awareness.

---

## Emergency Engine Procedures

### Engine Fire

1. **Immediate Actions**:
   - Throttle to idle
   - Mixture to idle cutoff (minimum)
   - Fuel feed off (Bridge or Fuel scene)
   - Click [STOP] button

2. **Continuing Actions**:
   - Maintain airspeed for glide
   - Prepare for emergency landing
   - Monitor restart possibility after fire extinguished

### Engine Failure in Flight

1. **Immediate Actions**:
   - Maintain flying airspeed
   - Check fuel feed status
   - Verify mixture and throttle settings
   - Attempt restart if cause identified

2. **Restart Procedure**:
   - Mixture full rich
   - Throttle cracked open
   - Click [START] button
   - Monitor oil pressure and temperatures

### Power Loss

1. **Troubleshooting**:
   - Check fuel pressure and flow
   - Verify mixture not too lean
   - Confirm throttle response
   - Look for temperature abnormalities

2. **Corrective Actions**:
   - Adjust mixture for current altitude
   - Verify fuel tank feed status
   - Consider power reduction if overheating
   - Prepare for emergency landing if no improvement

---

*Master your engine, master your destiny in the skies!*

**Airship Zero Development Team**  
*Steam & Copper Dreams Edition - 2025*
