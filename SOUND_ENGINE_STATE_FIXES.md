# Sound Engine State Behavior Fixes

## Issues Identified and Fixed

### Issue 1: Sound at 0 RPM with Engine On
**Problem**: When throttle was at 0 but engine was on, sound was still audible even though RPM should be near 0.

**Root Cause**: RPM threshold was too low (10 RPM), but actual engine behavior has no idle RPM - 0 throttle = 0 RPM.

**Fix**: Increased RPM threshold from 10 to 50 RPM for both propeller and engine wave generators.

### Issue 2: No Wind Sound When Engine Off
**Problem**: When engine was turned off, complete silence occurred even with significant airspeed.

**Root Cause**: The `update_from_simulator()` method was setting `self.current_airspeed = 0.0` when engine was off, preventing wind noise generation.

**Fix**: 
1. Always read airspeed from simulator regardless of engine state
2. Modified `generate_audio_buffer()` to handle engine and wind sounds independently
3. Wind noise now generates based on airspeed even when engine is off

## Code Changes

### sound.py Line ~83
```python
# BEFORE
# Extract audio-relevant parameters only if engine is running
if self.is_engine_running:
    self.current_rpm = engine.get("rpm", 0.0)
    self.current_pitch = controls.get("propeller", 0.0)
    self.current_mixture = controls.get("mixture", 0.0)
    self.current_airspeed = motion.get("indicatedAirspeed", 0.0)
else:
    # Engine off - no sound parameters
    self.current_rpm = 0.0
    self.current_pitch = 0.0
    self.current_mixture = 0.0
    self.current_airspeed = 0.0  # ❌ This was the bug!

# AFTER
# Always read airspeed (needed for wind noise regardless of engine state)
self.current_airspeed = motion.get("indicatedAirspeed", 0.0)

# Extract engine-relevant parameters only if engine is running
if self.is_engine_running:
    self.current_rpm = engine.get("rpm", 0.0)
    self.current_pitch = controls.get("propeller", 0.0)
    self.current_mixture = controls.get("mixture", 0.0)
else:
    # Engine off - no engine sound parameters
    self.current_rpm = 0.0
    self.current_pitch = 0.0
    self.current_mixture = 0.0
```

### sound.py Line ~309
```python
# BEFORE
# If simulation is paused or engine is off, return silence
if self.is_simulation_paused or not self.is_engine_running or self.volume <= 0.0:
    stereo_audio = np.zeros((num_samples, 2), dtype=np.float32)
    return stereo_audio

# Generate individual sound components
propeller_audio = self.generate_propeller_wave(duration)
engine_audio = self.generate_engine_wave(duration)
wind_audio = self.generate_wind_noise(duration)

# AFTER
# If simulation is paused or volume is off, return complete silence
if self.is_simulation_paused or self.volume <= 0.0:
    stereo_audio = np.zeros((num_samples, 2), dtype=np.float32)
    return stereo_audio

# Generate individual sound components based on engine and motion state
if self.is_engine_running:
    propeller_audio = self.generate_propeller_wave(duration)
    engine_audio = self.generate_engine_wave(duration)
else:
    # Engine is off - no propeller or engine sounds
    propeller_audio = np.zeros(num_samples, dtype=np.float32)
    engine_audio = np.zeros(num_samples, dtype=np.float32)

# Wind noise is always generated based on airspeed (independent of engine state)
wind_audio = self.generate_wind_noise(duration)
```

### RPM Threshold Updates
```python
# BEFORE
if self.current_rpm <= 10.0:  # Effectively silent below 10 RPM

# AFTER  
if self.current_rpm <= 50.0:  # Effectively silent below 50 RPM
```

## Test Results

After fixes:
- ✅ Engine OFF at 35 knots: Wind noise audible, no engine sounds
- ✅ Engine OFF at 3 knots: Very light wind noise, no engine sounds  
- ✅ Engine OFF stationary: Complete silence
- ✅ Engine ON, 0 throttle: Only wind noise (no engine sounds due to 0 RPM)
- ✅ Simulation paused: Complete silence regardless of state

## Behavioral Summary

The sound engine now correctly handles:

1. **Engine States**: Engine/propeller sounds only when engine is running AND RPM > 50
2. **Wind Independence**: Wind noise based purely on airspeed, regardless of engine state
3. **Pause Behavior**: Complete silence when simulation is paused
4. **Volume Control**: Respects master volume setting
5. **Realistic Physics**: No sound when stationary, appropriate wind noise during motion

This provides a much more realistic and immersive audio experience that properly reflects the game's physical state.
