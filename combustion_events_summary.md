🔥 Combustion Event Engine Audio Implementation Summary
========================================================

## Discrete Combustion Events Approach

### What Changed
Transformed engine audio from **continuous tone generation** to **discrete combustion event simulation**:

**Before (v0.2.58)**: Continuous sine wave generation per cylinder
**After (v0.2.60)**: Timeline-based combustion pressure wave events

### Technical Implementation

#### Core Concept
```python
# Each cylinder fires once per engine revolution
# 6 cylinders = 6 discrete events per engine cycle
# Events are placed in timeline with proper spacing
# Each event has fixed 80ms duration regardless of RPM
```

#### Key Features
1. **Discrete Combustion Events**:
   - 80ms fixed duration (RPM-independent)
   - Fast attack phase: 5ms (exponential rise)
   - Slow decay phase: 75ms (exponential decay)

2. **Timeline-Based Placement**:
   - Engine time accumulator tracks absolute time
   - Each cylinder has cycle offset (0/6, 1/6, 2/6, etc.)
   - Events placed at correct intervals regardless of RPM

3. **Per-Cylinder Audio Tracks**:
   - Each cylinder generates its own audio track
   - Within-track overlaps handled with max() function
   - Natural handling of fast RPM overlapping events

4. **Realistic Pressure Wave Shape**:
   ```python
   if t_combustion < attack_duration:
       envelope = attack_progress ** 0.3  # Fast rise
   else:
       envelope = math.exp(-decay_progress * 3.0)  # Exponential decay
   ```

### Firing Interval Mathematics

For a 6-cylinder engine:
- **Engine period** = 60 seconds / RPM 
- **Cylinder interval** = Engine period / 6 cylinders

Examples:
- **1000 RPM**: 60ms engine period → 10ms between cylinder firings
- **2400 RPM**: 25ms engine period → 4.17ms between cylinder firings  
- **3000 RPM**: 20ms engine period → 3.33ms between cylinder firings

### Audio Processing Chain
1. **Generate separate cylinder tracks** (6 tracks)
2. **Place combustion events** in timeline for each track
3. **Apply max() within each track** for overlap handling
4. **Sum all cylinder tracks** (linear addition)
5. **Add engine rumble** (low-frequency vibration)
6. **Apply HDR logarithmic normalization**
7. **Apply hull filtering** (if enabled)
8. **Apply volume and soft limiting**

### Benefits Achieved

#### ✅ Eliminated Phase Continuity Issues
- No more sine wave phase tracking per cylinder
- Timeline-based events naturally maintain continuity
- Engine time accumulator ensures smooth progression

#### ✅ Authentic Combustion Character
- Sharp attack mimics ignition pressure spike
- Long decay mimics exhaust and resonance
- Fixed duration independent of RPM (realistic)

#### ✅ Natural Overlap Handling
- Fast RPM automatically creates overlapping events
- max() within cylinder tracks prevents unrealistic stacking
- Linear addition between cylinders preserves natural mixing

#### ✅ RPM-Responsive Firing Rate
- **Low RPM**: Distinct individual combustion events audible
- **High RPM**: Events blend into continuous rumble naturally
- Firing rate scales correctly: 6 × (RPM/60) Hz

### Code Architecture

#### State Management
```python
# Track absolute engine time instead of phases
self.engine_time_accumulator = 0.0

# Track next firing times per cylinder
self.cylinder_next_firing_times = [0.0, 0.167, 0.333, 0.5, 0.667, 0.833]
```

#### Event Generation
```python
# Calculate firing times within buffer
current_engine_cycles = self.engine_time_accumulator / engine_period
current_cycle_position = current_engine_cycles - math.floor(current_engine_cycles)

# Find next firing for this cylinder
next_firing_cycle_position = cylinder_cycle_offset
if next_firing_cycle_position <= current_cycle_position:
    next_firing_cycle_position += 1.0
```

#### Pressure Wave Synthesis
```python
# Fast attack phase (5ms)
envelope = attack_progress ** 0.3

# Slow decay phase (75ms)  
envelope = math.exp(-decay_progress * 3.0)

# Apply to cylinder track with max() for overlaps
cylinder_track[sample_idx] = max(cylinder_track[sample_idx], pressure_wave)
```

### Testing Results

#### Audio Characteristics (v0.2.60)
- **Peak amplitude**: Controlled within HDR range
- **DC offset**: ~0.000000 (excellent centering)
- **Dynamic range**: 4.5-7.6 (natural variation with RPM)
- **Phase continuity**: Smooth transitions between buffers

#### Event Detection
- **1000 RPM**: Clear discrete events detectable
- **2400+ RPM**: Events blend naturally (as expected)
- **Timing accuracy**: Matches expected cylinder intervals

### Integration Status
- **Version**: 0.2.60
- **Game Integration**: ✅ Active and tested
- **HDR Processing**: ✅ Logarithmic normalization applied
- **Hull Filtering**: ✅ Compatible and functional
- **Phase Continuity**: ✅ Smooth timeline-based tracking

### Future Enhancements Possible
1. **Variable combustion character** based on mixture richness
2. **Cylinder-specific variations** (engine wear simulation)
3. **Altitude effects** on combustion efficiency
4. **Backfire events** for rich mixture conditions

## Summary

The combustion event approach successfully transforms engine audio from **mathematical tone generation** to **physics-based combustion simulation**. Each cylinder now fires discrete pressure wave events with authentic attack/decay characteristics, placed correctly in a timeline that automatically handles RPM scaling and event overlaps.

This eliminates phase continuity artifacts while providing more realistic and immersive engine audio that responds naturally to all flight conditions.
