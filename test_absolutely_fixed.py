#!/usr/bin/env python3
"""
Test phase continuity with absolutely fixed parameters
"""

import pygame
import numpy as np
import math
from sound import AirshipSoundEngine
from core_simulator import get_simulator

def test_absolutely_fixed():
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    
    sound_engine = AirshipSoundEngine(simulator)
    
    # Manually set fixed parameters that won't change
    sound_engine.current_rpm = 2400.0
    sound_engine.current_pitch = 0.8
    sound_engine.current_mixture = 0.85
    sound_engine.current_airspeed = 85.0
    sound_engine.is_engine_running = True
    sound_engine.is_simulation_paused = False
    sound_engine.volume = 0.5
    
    print("=== Testing with absolutely fixed parameters ===")
    print(f"RPM: {sound_engine.current_rpm}")
    print(f"Pitch: {sound_engine.current_pitch}")
    print(f"Mixture: {sound_engine.current_mixture}")
    print(f"Airspeed: {sound_engine.current_airspeed}")
    
    duration = 0.023
    
    # Test propeller wave continuity (the main culprit)
    print(f"\nTesting propeller wave continuity:")
    print(f"Initial phases: fund={sound_engine.phase_accumulator:.6f}, h2={sound_engine.phase_harmonic2:.6f}, h3={sound_engine.phase_harmonic3:.6f}")
    
    # Generate 3 propeller buffers
    prop_buffers = []
    for i in range(3):
        prop_buffer = sound_engine.generate_propeller_wave(duration)
        prop_buffers.append(prop_buffer)
        print(f"Buffer {i+1} phases: fund={sound_engine.phase_accumulator:.6f}, h2={sound_engine.phase_harmonic2:.6f}, h3={sound_engine.phase_harmonic3:.6f}")
        
        if i > 0:
            prev_last = prop_buffers[i-1][-1]
            current_first = prop_buffers[i][0]
            jump = abs(current_first - prev_last)
            print(f"  Propeller boundary jump {i}: {jump:.6f}")
            if jump > 0.01:
                print(f"  ⚠️  PROPELLER DISCONTINUITY")
            else:
                print(f"  ✅ Good propeller continuity")
    
    # Reset phases and test complete audio buffer continuity
    print(f"\n" + "="*50)
    print("Testing complete audio buffer continuity:")
    
    # Reset all phases
    sound_engine.phase_accumulator = 0.0
    sound_engine.phase_harmonic2 = 0.0
    sound_engine.phase_harmonic3 = 0.0
    sound_engine.engine_phase = 0.0
    sound_engine.rumble_phase = 0.0
    sound_engine.noise_phase = 0.0
    
    # Generate complete audio buffers WITHOUT calling update_from_simulator
    audio_buffers = []
    for i in range(3):
        # Generate individual components
        prop = sound_engine.generate_propeller_wave(duration)
        engine = sound_engine.generate_engine_wave(duration)
        wind = sound_engine.generate_wind_noise(duration)
        
        # Mix manually exactly like generate_audio_buffer does
        mixed = prop + engine + wind
        mixed = mixed * sound_engine.volume
        mixed = sound_engine.apply_soft_limiter(mixed, threshold=0.80)
        
        audio_buffers.append(mixed)
        
        print(f"Complete buffer {i+1} phases: fund={sound_engine.phase_accumulator:.6f}")
        
        if i > 0:
            prev_last = audio_buffers[i-1][-1]
            current_first = audio_buffers[i][0]
            jump = abs(current_first - prev_last)
            print(f"  Complete boundary jump {i}: {jump:.6f}")
            if jump > 0.01:
                print(f"  ⚠️  COMPLETE AUDIO DISCONTINUITY")
            else:
                print(f"  ✅ Good complete audio continuity")
    
    pygame.quit()

if __name__ == "__main__":
    test_absolutely_fixed()
