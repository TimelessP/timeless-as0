# Airship Zero - Fuel Management User Manual

**Steam & Copper Dreams Edition**  
*The Complete Guide to Fuel System Operations*

---

## Table of Contents

1. [Overview](#overview)
2. [Fuel System Layout](#fuel-system-layout)
3. [Tank Configuration](#tank-configuration)
4. [Feed Controls](#feed-controls)
5. [Transfer Operations](#transfer-operations)
6. [Fuel Dumping](#fuel-dumping)
7. [Fuel Management Strategy](#fuel-management-strategy)
8. [Weight and Balance](#weight-and-balance)
9. [Emergency Procedures](#emergency-procedures)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

---

## Overview

The Fuel Management system controls your airship's two-tank fuel configuration, providing precise control over fuel distribution, engine feed, and emergency operations. Proper fuel management is critical for maintaining optimal weight and balance, ensuring continuous engine operation, and managing flight duration.

**Key Features:**
- Dual-tank system (Forward & Aft)
- Independent tank feed controls
- Inter-tank transfer capability
- Emergency fuel dumping
- Real-time fuel quantity display
- Weight and balance optimization

---

## Fuel System Layout

The fuel system interface provides centralized control of both fuel tanks:

```
┌────────────── FUEL ──────────────┐
│ [FWD FEED]              [AFT FEED] │
│                                   │
│    ┌──────┐              ┌──────┐ │
│    │ FWD  │              │ AFT  │ │
│    │      │              │      │ │
│    │██████│              │██████│ │
│    │██████│              │██████│ │
│    │██████│              │██████│ │
│    │██████│              │██████│ │
│    └──────┘              └──────┘ │
│  140.00/180g            140.00/180g │
│                                   │
│  [XFER] [DUMP]        [DUMP] [XFER] │
│    │     │              │     │   │
│    ▓     ▓              ▓     ▓   │
│    ▓     ▓              ▓     ▓   │
│    ▓     ▓              ▓     ▓   │
│    █     █              █     █   │
│                                   │
│ [< [ ]                    [ ] >]  │
└───────────────────────────────────┘
```

**Layout Elements:**
- **Tank Displays**: Visual fuel level indicators
- **Feed Toggles**: Engine feed enable/disable
- **Transfer Sliders**: Cross-tank fuel transfer
- **Dump Sliders**: Emergency fuel jettison
- **Quantity Displays**: Precise fuel readings

---

## Tank Configuration

### Dual-Tank System

**Forward Tank**
- **Capacity**: 180 gallons
- **Position**: Front of airship
- **Effect**: Forward weight bias when full

**Aft Tank**
- **Capacity**: 180 gallons  
- **Position**: Rear of airship
- **Effect**: Aft weight bias when full

**Total System Capacity**: 360 gallons

### Fuel Quantity Display

Each tank shows real-time fuel information:
- **Format**: `140.00/180g` (Current/Capacity in gallons)
- **Precision**: Hundredths of gallons
- **Updates**: Real-time during all operations
- **Critical Levels**: Visual warnings when low

### Visual Fuel Gauges

**Tank Representation:**
- **Empty Space**: Dark background
- **Fuel Level**: Orange/amber fill
- **Full Scale**: Bottom-to-top fill pattern
- **Proportional**: Visual height matches actual percentage

---

## Feed Controls

### Engine Feed Toggles

**[FWD FEED]** - Forward Tank Feed
- **ON**: Forward tank supplies engine
- **OFF**: Forward tank isolated from engine
- **Color**: Highlighted when active

**[AFT FEED]** - Aft Tank Feed  
- **ON**: Aft tank supplies engine
- **OFF**: Aft tank isolated from engine
- **Color**: Highlighted when active

### Feed Configuration Strategies

**Both Tanks ON** (Normal Operations)
- Engine draws from both tanks simultaneously
- Automatic load balancing
- Maximum fuel availability
- Recommended for most flight phases

**Single Tank Operation**
- Use during fuel balancing operations
- Emergency isolation of contaminated tank
- Testing individual tank systems
- Maintenance operations

**Both Tanks OFF** (Emergency Only)
- **WARNING**: Engine will starve and stop!
- Used only for emergency engine shutdown
- Fuel system maintenance
- Fire suppression procedures

### Feed Status Integration

The Bridge scene displays current feed status:
- **[FEED: FA]**: Both Forward and Aft feeding
- **[FEED: F-]**: Only Forward feeding
- **[FEED: -A]**: Only Aft feeding  
- **[FEED: --]**: No tanks feeding (CRITICAL!)

---

## Transfer Operations

### Inter-Tank Transfer System

**XFER Sliders** - Transfer Rate Control
- **Range**: 0-100% transfer rate
- **Direction**: OUT of the tank (to the other tank)
- **Rate**: Gallons per minute based on percentage
- **Bidirectional**: Each tank can transfer to the other

### Transfer Controls

**Forward Tank Transfer [XFER]**
- **Function**: Transfers fuel FROM forward TO aft tank
- **Rate Control**: Vertical slider (0-100%)
- **Maximum Rate**: ~50 gallons per minute at 100%
- **Use**: Move fuel aft for weight balance

**Aft Tank Transfer [XFER]**  
- **Function**: Transfers fuel FROM aft TO forward tank
- **Rate Control**: Vertical slider (0-100%)
- **Maximum Rate**: ~50 gallons per minute at 100%
- **Use**: Move fuel forward for weight balance

### Transfer Procedures

**Basic Transfer Operation:**
1. **Identify Need**: Determine desired fuel distribution
2. **Set Rate**: Adjust transfer slider to appropriate rate
3. **Monitor**: Watch fuel quantities in real-time
4. **Stop Transfer**: Return slider to zero when complete

**Continuous Monitoring Required:**
- Transfer continues until manually stopped
- No automatic shutoff at empty/full
- Risk of completely draining source tank
- Monitor to prevent fuel imbalance

---

## Fuel Dumping

### Emergency Jettison System

**DUMP Sliders** - Emergency Fuel Release
- **Range**: 0-100% dump rate
- **Direction**: Overboard (lost forever)
- **Rate**: Gallons per minute based on percentage
- **Emergency Use**: Weight reduction, fire suppression

### Dump Controls

**Forward Tank Dump [DUMP]**
- **Function**: Jettisons fuel FROM forward tank overboard
- **Rate Control**: Vertical slider (0-100%)
- **Maximum Rate**: ~75 gallons per minute at 100%
- **Color**: Red slider fill (danger indication)

**Aft Tank Dump [DUMP]**
- **Function**: Jettisons fuel FROM aft tank overboard
- **Rate Control**: Vertical slider (0-100%)  
- **Maximum Rate**: ~75 gallons per minute at 100%
- **Color**: Red slider fill (danger indication)

### Emergency Dump Procedures

**When to Use Fuel Dumping:**
- **Emergency Landing**: Reduce landing weight
- **Fire Suppression**: Remove fuel from fire area
- **Structural Limits**: Exceed maximum gross weight
- **Performance**: Improve climb performance

**Dump Operation:**
1. **Assess Situation**: Confirm dump is necessary
2. **Select Tank**: Choose appropriate tank(s)
3. **Set Rate**: Higher rates for urgent situations
4. **Monitor Altitude**: Ensure safe fuel disposal
5. **Stop Dump**: Return slider to zero when sufficient

**Safety Considerations:**
- **Environmental**: Avoid populated areas
- **Altitude**: Maintain safe height for fuel dispersion
- **Balance**: Dump symmetrically when possible
- **Reserve**: Retain fuel for landing approach

---

## Fuel Management Strategy

### Optimal Fuel Distribution

**Balanced Configuration** (Preferred)
- **Forward**: 90 gallons (50% capacity)
- **Aft**: 90 gallons (50% capacity)
- **Benefits**: Neutral pitch attitude, optimal CG

**Forward Heavy Configuration**
- **Use**: Cargo loading, equipment placement
- **Effect**: Nose-down pitch attitude
- **Correction**: Transfer fuel aft

**Aft Heavy Configuration**  
- **Use**: Engine maintenance, forward cargo
- **Effect**: Nose-up pitch attitude
- **Correction**: Transfer fuel forward

### Flight Phase Management

**Takeoff**
- **Configuration**: Balanced or slightly forward heavy
- **Fuel Load**: Based on planned flight time + reserves
- **Feed**: Both tanks ON

**Climb**
- **Monitor**: Engine performance vs. fuel consumption
- **Adjust**: May transfer fuel for optimal CG
- **Performance**: Higher fuel flow during climb power

**Cruise**
- **Efficiency**: Maintain balanced configuration
- **Monitoring**: Regular fuel quantity checks
- **Planning**: Calculate remaining flight time

**Descent**
- **Preparation**: Plan approach fuel requirements
- **Balance**: Adjust for landing configuration
- **Reserves**: Ensure adequate fuel for approach/landing

**Landing**
- **Configuration**: Slightly forward heavy preferred
- **Reserves**: Maintain minimum fuel for go-around
- **Safety**: Keep feed ON until shutdown

---

## Weight and Balance

### Center of Gravity Effects

**Fuel Distribution Impact:**
- **Forward Tank Full**: CG moves forward
- **Aft Tank Full**: CG moves aft
- **Balanced Tanks**: CG remains centered

**Flight Characteristics:**
- **Forward CG**: More stable, nose-heavy, requires up elevator
- **Aft CG**: Less stable, tail-heavy, requires down elevator
- **Balanced CG**: Optimal handling characteristics

### Transfer for Balance

**Correcting Forward Heavy:**
1. Monitor pitch attitude on bridge
2. Transfer fuel from forward to aft tank
3. Use 25-50% transfer rate
4. Stop when attitude normalizes

**Correcting Aft Heavy:**
1. Monitor pitch attitude on bridge  
2. Transfer fuel from aft to forward tank
3. Use 25-50% transfer rate
4. Stop when attitude normalizes

**Fuel Planning:**
- Plan fuel distribution for entire flight
- Account for fuel consumption patterns
- Anticipate CG shift as fuel burns
- Use transfer to maintain optimal balance

---

## Emergency Procedures

### Engine Fuel Starvation

**Symptoms:**
- Dropping RPM on bridge display
- Decreasing fuel flow
- Engine roughness or stopping

**Immediate Actions:**
1. **Check Feed Status**: Verify tank feed switches
2. **Enable Feeds**: Turn ON both [FWD FEED] and [AFT FEED]
3. **Check Quantities**: Verify fuel available in tanks
4. **Transfer If Needed**: Move fuel to feeding tank
5. **Monitor Engine**: Watch for RPM recovery

### Fuel System Fire

**Forward Tank Fire:**
1. **Isolate**: Turn OFF [FWD FEED]
2. **Dump**: Use forward [DUMP] slider at 100%
3. **Transfer**: Stop any transfers TO forward tank
4. **Monitor**: Watch fuel quantity drop to minimum

**Aft Tank Fire:**
1. **Isolate**: Turn OFF [AFT FEED]  
2. **Dump**: Use aft [DUMP] slider at 100%
3. **Transfer**: Stop any transfers TO aft tank
4. **Monitor**: Watch fuel quantity drop to minimum

### Fuel Leak

**Suspected Leak:**
1. **Monitor Quantities**: Watch for unexplained fuel loss
2. **Isolate Suspect Tank**: Turn OFF feed from leaking tank
3. **Transfer Fuel**: Move fuel from leaking tank to good tank
4. **Calculate Range**: Reassess flight planning with remaining fuel

### Fuel Contamination

**Contaminated Tank:**
1. **Isolate**: Turn OFF feed from contaminated tank
2. **Single Tank Operation**: Continue on good tank only
3. **Plan Landing**: Reduce flight time/distance
4. **Dump If Necessary**: Jettison contaminated fuel safely

---

## Troubleshooting

### Transfer System Issues

**Transfer Not Working:**
- **Check Slider Position**: Ensure slider not at zero
- **Verify Tank Levels**: Source tank must have fuel
- **Destination Capacity**: Target tank must have space
- **System Power**: Check electrical system status

**Transfer Too Slow:**
- **Increase Rate**: Move slider higher (50-100%)
- **Check Fuel Viscosity**: Cold fuel transfers slower
- **System Health**: Verify pump operation

**Unwanted Transfer:**
- **Check Sliders**: Ensure all transfer sliders at zero
- **Stop Transfer**: Move active slider to zero position
- **Balance Check**: Verify no automatic balancing active

### Feed System Problems

**Engine Starving Despite Fuel:**
- **Feed Switches**: Verify [FWD FEED] and/or [AFT FEED] ON
- **Fuel Quantity**: Check actual fuel in feeding tanks
- **Transfer Active**: Stop any transfers OUT of feeding tanks
- **Bridge Status**: Check [FEED: --] display on bridge

**Feed Status Incorrect:**
- **Switch Position**: Toggle feed switches OFF and ON
- **System Refresh**: Change scenes and return
- **Electrical Issues**: Check battery and alternator status

### Dump System Issues

**Dump Not Working:**
- **Slider Position**: Ensure dump slider not at zero
- **Tank Quantity**: Verify fuel available to dump
- **Safety Lock**: Some systems have dump inhibits

**Accidental Dumping:**
- **Immediate**: Return dump slider to ZERO
- **Calculate Loss**: Note fuel quantity dumped
- **Flight Planning**: Recalculate range with remaining fuel

---

## Best Practices

### Pre-Flight Planning

**Fuel Load Calculation:**
1. **Flight Time**: Planned flight duration
2. **Fuel Consumption**: ~12-15 GPH average
3. **Reserve Requirements**: Minimum 30-60 minutes
4. **Weather Contingency**: Extra fuel for headwinds/diversions
5. **Total Required**: Flight fuel + reserves + contingency

**Distribution Planning:**
- **Takeoff**: Balanced or slightly forward heavy
- **Cruise**: Maintain balance through transfers
- **Landing**: Slightly forward heavy preferred
- **Emergency**: Plan dump procedures if needed

### In-Flight Management

**Regular Monitoring:**
- **Check Quantities**: Every 15-30 minutes
- **Monitor Balance**: Watch pitch attitude on bridge
- **Feed Status**: Verify both tanks feeding normally
- **Consumption Rate**: Calculate remaining flight time

**Proactive Transfers:**
- **Before Imbalance**: Transfer before attitude changes
- **Small Adjustments**: Use 25% transfer rate for minor corrections
- **Monitor Progress**: Watch fuel quantities during transfer
- **Stop Promptly**: Don't over-correct balance

### System Maintenance

**Operational Checks:**
- **Feed Toggle Test**: Verify switches operate correctly
- **Transfer Test**: Brief transfer operation check
- **Quantity Accuracy**: Compare with known fuel load
- **System Response**: Verify real-time updates

**Between Flights:**
- **Tank Inspection**: Visual check for fuel contamination
- **System Cleaning**: Drain water/sediment if needed
- **Feed Line Check**: Verify no blockages
- **Transfer System**: Test pump operation

### Emergency Preparedness

**Know Your Numbers:**
- **Tank Capacities**: 180 gallons each
- **Transfer Rates**: ~50 GPH maximum
- **Dump Rates**: ~75 GPH maximum
- **Consumption**: ~12-15 GPH cruise

**Practice Procedures:**
- **Feed Isolation**: Quick switch operations
- **Emergency Dump**: Rapid fuel jettison
- **Single Tank Ops**: Operation on one tank only
- **Balance Correction**: Rapid CG adjustment

**Emergency Equipment:**
- **Backup Systems**: Manual fuel transfer if needed
- **Fuel Quality Test**: Check for contamination
- **Leak Detection**: Visual inspection capability
- **Communication**: Report fuel emergencies promptly

---

## Operational Limits

### Fuel System Constraints

**Minimum Fuel Levels:**
- **Engine Operation**: 5-10 gallons per tank minimum
- **Feed Reliability**: 20+ gallons recommended
- **Transfer Operation**: 10+ gallons in source tank
- **Reserve**: Never plan to land with less than 30 gallons total

**Maximum Transfer Rates:**
- **Normal Operations**: 25-50% recommended
- **Emergency**: 100% acceptable for short periods
- **Continuous**: Avoid sustained high-rate transfers
- **Temperature**: Cold fuel reduces maximum rates

**Dump Limitations:**
- **Environmental**: Follow local regulations
- **Altitude**: Minimum safe height for dispersion
- **Rate Limits**: Don't exceed system capacity
- **Quantity**: Retain minimum fuel for safe landing

### System Integration

**Engine Dependencies:**
- **Feed Required**: Engine stops without fuel feed
- **Pressure Sensitive**: Low fuel pressure affects performance
- **Balance Critical**: CG affects engine cooling airflow
- **Electrical**: Fuel system requires electrical power

**Weight and Balance:**
- **CG Limits**: Stay within approved CG range
- **Gross Weight**: Don't exceed maximum weight limits
- **Load Distribution**: Consider other cargo/equipment
- **Performance**: Heavy/unbalanced affects flight characteristics

---

## Keyboard Shortcuts

| Key | Function |
|-----|----------|
| **Tab** | Cycle widget focus forward |
| **Shift+Tab** | Cycle widget focus backward |
| **Enter** | Activate focused widget |
| **Space** | Activate focused widget |
| **↑/↓** | Adjust focused slider |
| **Page Up/Down** | Large slider adjustments |
| **[** | Previous scene (Navigation) |
| **]** | Next scene (Cargo) |
| **Esc** | Return to main menu (if no active widgets) |

---

## Scene Navigation

The Fuel Management scene connects to the complete airship operation suite:

- **Previous ([)**: Navigation Scene
- **Next (])**: Cargo Scene  
- **Bridge Access**: Monitor feed status and fuel consumption
- **Engine Room**: Monitor fuel pressure and consumption rates

Navigate between scenes for comprehensive airship management and monitoring.

---

## Fuel Consumption Reference

### Typical Consumption Rates

**Power Setting vs. Fuel Flow:**
- **Idle/Ground**: 3-5 GPH
- **Taxi**: 5-8 GPH
- **Takeoff Power**: 18-22 GPH
- **Climb Power**: 15-18 GPH
- **Cruise Power**: 10-15 GPH
- **Descent**: 8-12 GPH
- **Approach**: 12-16 GPH

**Altitude Effects:**
- **Sea Level**: Maximum fuel flow
- **5,000 ft**: ~90% of sea level flow
- **10,000 ft**: ~80% of sea level flow
- **15,000 ft**: ~70% of sea level flow

**Load Factor Effects:**
- **Light Load**: Reduced fuel consumption
- **Heavy Load**: Increased fuel consumption
- **Balanced CG**: Optimal fuel efficiency
- **Unbalanced**: Increased consumption due to control inputs

### Range Planning

**Fuel Range Estimation:**
- **Total Capacity**: 360 gallons
- **Usable Fuel**: ~340 gallons (reserve some unusable)
- **Cruise Consumption**: 12 GPH average
- **No-Wind Range**: ~28 hours flight time
- **Reserve**: Plan for 30-60 minutes additional

**Factors Affecting Range:**
- **Wind**: Headwinds reduce range significantly
- **Altitude**: Higher altitudes may improve efficiency
- **Weight**: Heavier loads increase consumption
- **Weather**: Cold temperatures, turbulence affect efficiency

---

*Master your fuel system for safe and efficient airship operations!*

**Airship Zero Development Team**  
*Steam & Copper Dreams Edition - 2025*
