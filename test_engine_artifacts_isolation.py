#!/usr/bin/env python3
"""
Isolate engine artifacts by testing propeller and engine components separately
"""

import pygame
import numpy as np
from sound import AirshipSoundEngine
from core_simulator import get_simulator

def test_engine_artifacts():
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.set_engine_control("throttle", 0.6)
    simulator.set_engine_control("mixture", 0.8)
    simulator.update(0.1)
    
    sound_engine = AirshipSoundEngine(simulator)
    sound_engine.update_from_simulator()
    
    print("=== ENGINE ARTIFACT ISOLATION TEST ===")
    print(f"RPM: {sound_engine.current_rpm:.1f}")
    print(f"Engine running: {sound_engine.is_engine_running}")
    
    duration = 0.023  # 23ms buffer
    num_test_buffers = 3
    
    # Test 1: Propeller ONLY
    print("\n1. Testing PROPELLER ONLY (no engine, no wind):")
    sound_engine.phase_accumulator = 0.0
    sound_engine.phase_harmonic2 = 0.0
    sound_engine.phase_harmonic3 = 0.0
    
    prop_buffers = []
    for i in range(num_test_buffers):
        prop_buffer = sound_engine.generate_propeller_wave(duration)
        prop_buffers.append(prop_buffer)
        
        if i > 0:
            jump = abs(prop_buffers[i][0] - prop_buffers[i-1][-1])
            status = "✅ GOOD" if jump < 0.01 else "⚠️  ARTIFACT"
            print(f"  Propeller buffer {i} jump: {jump:.6f} {status}")
    
    # Test 2: Engine ONLY
    print("\n2. Testing ENGINE ONLY (no propeller, no wind):")
    sound_engine.engine_phase = 0.0
    sound_engine.rumble_phase = 0.0
    
    engine_buffers = []
    for i in range(num_test_buffers):
        engine_buffer = sound_engine.generate_engine_wave(duration)
        engine_buffers.append(engine_buffer)
        
        if i > 0:
            jump = abs(engine_buffers[i][0] - engine_buffers[i-1][-1])
            status = "✅ GOOD" if jump < 0.01 else "⚠️  ARTIFACT"
            print(f"  Engine buffer {i} jump: {jump:.6f} {status}")
    
    # Test 3: Propeller + Engine (no wind)
    print("\n3. Testing PROPELLER + ENGINE (no wind):")
    sound_engine.phase_accumulator = 0.0
    sound_engine.phase_harmonic2 = 0.0
    sound_engine.phase_harmonic3 = 0.0
    sound_engine.engine_phase = 0.0
    sound_engine.rumble_phase = 0.0
    
    mixed_buffers = []
    for i in range(num_test_buffers):
        prop = sound_engine.generate_propeller_wave(duration)
        engine = sound_engine.generate_engine_wave(duration)
        mixed = prop + engine
        mixed_buffers.append(mixed)
        
        if i > 0:
            jump = abs(mixed_buffers[i][0] - mixed_buffers[i-1][-1])
            status = "✅ GOOD" if jump < 0.01 else "⚠️  ARTIFACT"
            print(f"  Mixed (prop+engine) buffer {i} jump: {jump:.6f} {status}")
    
    # Test 4: Check for specific engine firing artifacts
    print("\n4. Detailed ENGINE FIRING analysis:")
    
    # Generate a longer engine buffer to check for firing artifacts
    long_duration = 0.1  # 100ms to capture multiple firing cycles
    sound_engine.engine_phase = 0.0
    sound_engine.rumble_phase = 0.0
    
    engine_long = sound_engine.generate_engine_wave(long_duration)
    
    # Look for sudden amplitude changes (firing artifacts)
    max_sample_to_sample_change = 0.0
    artifact_locations = []
    
    for i in range(1, len(engine_long)):
        change = abs(engine_long[i] - engine_long[i-1])
        if change > max_sample_to_sample_change:
            max_sample_to_sample_change = change
        if change > 0.1:  # Threshold for suspicious changes
            artifact_locations.append((i, change))
    
    print(f"  Max sample-to-sample change: {max_sample_to_sample_change:.6f}")
    print(f"  Suspicious changes (>0.1): {len(artifact_locations)}")
    
    if artifact_locations:
        print("  Artifact locations (sample, magnitude):")
        for loc, magnitude in artifact_locations[:5]:  # Show first 5
            time_ms = (loc / sound_engine.sample_rate) * 1000
            print(f"    Sample {loc} ({time_ms:.1f}ms): {magnitude:.6f}")
    
    # Test 5: Wind noise only (improved version)
    print("\n5. Testing IMPROVED WIND NOISE (no engine):")
    sound_engine.noise_phase = 0.0
    # Temporarily set airspeed for wind test
    original_airspeed = sound_engine.current_airspeed
    sound_engine.current_airspeed = 85.0
    
    wind_buffers = []
    for i in range(num_test_buffers):
        wind_buffer = sound_engine.generate_wind_noise(duration)
        wind_buffers.append(wind_buffer)
        
        if i > 0:
            jump = abs(wind_buffers[i][0] - wind_buffers[i-1][-1])
            status = "✅ GOOD" if jump < 0.01 else "⚠️  ARTIFACT"
            print(f"  Wind buffer {i} jump: {jump:.6f} {status}")
    
    # Restore original airspeed
    sound_engine.current_airspeed = original_airspeed
    
    # Test 6: Frequency analysis
    print("\n6. FREQUENCY ANALYSIS:")
    
    # Calculate expected frequencies
    prop_freq = (sound_engine.current_rpm / 60.0) * 2  # 2-blade prop
    engine_firing_freq = (sound_engine.current_rpm / 60.0) * 6  # 6 cylinders
    engine_rumble_freq = sound_engine.current_rpm / 60.0  # Engine rotation
    
    print(f"  Propeller frequency: {prop_freq:.1f} Hz")
    print(f"  Engine firing frequency: {engine_firing_freq:.1f} Hz") 
    print(f"  Engine rumble frequency: {engine_rumble_freq:.1f} Hz")
    
    # Check if frequencies are creating beating patterns
    prop_harmonics = [prop_freq, prop_freq * 2, prop_freq * 3]
    print(f"  Propeller harmonics: {[f'{f:.1f}' for f in prop_harmonics]} Hz")
    
    # Check for potential beating between propeller and engine
    beat_freq = abs(prop_freq - engine_firing_freq)
    print(f"  Beat frequency (prop vs engine firing): {beat_freq:.1f} Hz")
    
    if beat_freq < 20:
        print(f"  ⚠️  Low beat frequency may cause audible beating artifacts")
    else:
        print(f"  ✅ Beat frequency high enough to avoid artifacts")
    
    pygame.quit()

if __name__ == "__main__":
    test_engine_artifacts()
