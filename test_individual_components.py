#!/usr/bin/env python3
"""
Test each audio component individually for phase continuity
"""

import pygame
import numpy as np
from sound import AirshipSoundEngine
from core_simulator import get_simulator

def test_individual_components():
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    
    sound_engine = AirshipSoundEngine(simulator)
    
    # Set fixed parameters
    sound_engine.current_rpm = 2400.0
    sound_engine.current_pitch = 0.8
    sound_engine.current_mixture = 0.85
    sound_engine.current_airspeed = 85.0
    sound_engine.is_engine_running = True
    sound_engine.is_simulation_paused = False
    sound_engine.volume = 0.5
    
    duration = 0.023
    num_buffers = 3
    
    print("=== Testing Individual Component Continuity ===")
    
    # Test 1: Propeller waves
    print("\n1. Testing Propeller Wave Continuity:")
    sound_engine.phase_accumulator = 0.0
    sound_engine.phase_harmonic2 = 0.0  
    sound_engine.phase_harmonic3 = 0.0
    
    prop_buffers = []
    for i in range(num_buffers):
        prop = sound_engine.generate_propeller_wave(duration)
        prop_buffers.append(prop)
        if i > 0:
            jump = abs(prop_buffers[i][0] - prop_buffers[i-1][-1])
            print(f"  Propeller jump {i}: {jump:.6f}")
    
    # Test 2: Engine waves
    print("\n2. Testing Engine Wave Continuity:")
    sound_engine.engine_phase = 0.0
    sound_engine.rumble_phase = 0.0
    
    engine_buffers = []
    for i in range(num_buffers):
        engine = sound_engine.generate_engine_wave(duration)
        engine_buffers.append(engine)
        if i > 0:
            jump = abs(engine_buffers[i][0] - engine_buffers[i-1][-1])
            print(f"  Engine jump {i}: {jump:.6f}")
    
    # Test 3: Wind noise
    print("\n3. Testing Wind Noise Continuity:")
    sound_engine.noise_phase = 0.0
    
    wind_buffers = []
    for i in range(num_buffers):
        wind = sound_engine.generate_wind_noise(duration)
        wind_buffers.append(wind)
        if i > 0:
            jump = abs(wind_buffers[i][0] - wind_buffers[i-1][-1])
            print(f"  Wind jump {i}: {jump:.6f}")
    
    # Test 4: Mixed but before volume/limiting
    print("\n4. Testing Raw Mixed Audio (before volume/limiting):")
    # Reset all phases
    sound_engine.phase_accumulator = 0.0
    sound_engine.phase_harmonic2 = 0.0
    sound_engine.phase_harmonic3 = 0.0
    sound_engine.engine_phase = 0.0
    sound_engine.rumble_phase = 0.0
    sound_engine.noise_phase = 0.0
    
    raw_mixed_buffers = []
    for i in range(num_buffers):
        prop = sound_engine.generate_propeller_wave(duration)
        engine = sound_engine.generate_engine_wave(duration)
        wind = sound_engine.generate_wind_noise(duration)
        raw_mixed = prop + engine + wind
        raw_mixed_buffers.append(raw_mixed)
        if i > 0:
            jump = abs(raw_mixed_buffers[i][0] - raw_mixed_buffers[i-1][-1])
            print(f"  Raw mixed jump {i}: {jump:.6f}")
    
    # Test 5: After volume scaling
    print("\n5. Testing After Volume Scaling:")
    volume_scaled_buffers = []
    for i, raw_mixed in enumerate(raw_mixed_buffers):
        volume_scaled = raw_mixed * sound_engine.volume
        volume_scaled_buffers.append(volume_scaled)
        if i > 0:
            jump = abs(volume_scaled_buffers[i][0] - volume_scaled_buffers[i-1][-1])
            print(f"  Volume scaled jump {i}: {jump:.6f}")
    
    # Test 6: After soft limiting
    print("\n6. Testing After Soft Limiting:")
    limited_buffers = []
    for i, volume_scaled in enumerate(volume_scaled_buffers):
        limited = sound_engine.apply_soft_limiter(volume_scaled, threshold=0.80)
        limited_buffers.append(limited)
        if i > 0:
            jump = abs(limited_buffers[i][0] - limited_buffers[i-1][-1])
            print(f"  Soft limited jump {i}: {jump:.6f}")
    
    pygame.quit()

if __name__ == "__main__":
    test_individual_components()
