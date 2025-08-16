#!/usr/bin/env python3
"""
Test without simulator updates between buffers
"""

import pygame
import numpy as np
from sound import AirshipSoundEngine
from core_simulator import get_simulator

def test_without_updates():
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.set_engine_control("throttle", 0.6)
    simulator.set_engine_control("mixture", 0.8)
    simulator.update(0.1)
    
    sound_engine = AirshipSoundEngine(simulator)
    
    # Do the initial update once
    sound_engine.update_from_simulator()
    
    print("=== Testing WITHOUT update_from_simulator between buffers ===")
    print(f"Engine running: {sound_engine.is_engine_running}")
    print(f"RPM: {sound_engine.current_rpm:.6f}")
    print(f"Airspeed: {sound_engine.current_airspeed:.6f}")
    
    duration = 0.023
    num_samples = int(duration * sound_engine.sample_rate)
    
    # Generate buffer 1 manually (without calling generate_audio_buffer)
    print(f"\nInitial phases: fund={sound_engine.phase_accumulator:.6f}, h2={sound_engine.phase_harmonic2:.6f}, h3={sound_engine.phase_harmonic3:.6f}")
    
    # Generate components manually (no updates)
    propeller_audio1 = sound_engine.generate_propeller_wave(duration)
    engine_audio1 = sound_engine.generate_engine_wave(duration)
    wind_audio1 = sound_engine.generate_wind_noise(duration)
    
    # Mix manually
    mixed1 = propeller_audio1 + engine_audio1 + wind_audio1
    mixed1 = mixed1 * sound_engine.volume
    mixed1 = sound_engine.apply_soft_limiter(mixed1, threshold=0.80)
    
    # Convert to stereo manually
    buffer1 = np.zeros((num_samples, 2), dtype=np.float32)
    buffer1[:, 0] = mixed1
    buffer1[:, 1] = mixed1
    
    print(f"After buffer 1 phases: fund={sound_engine.phase_accumulator:.6f}, h2={sound_engine.phase_harmonic2:.6f}, h3={sound_engine.phase_harmonic3:.6f}")
    print(f"Buffer 1 end value: {buffer1[-1][0]:.6f}")
    print(f"RPM still: {sound_engine.current_rpm:.6f}")
    
    # Generate buffer 2 manually (no updates)
    propeller_audio2 = sound_engine.generate_propeller_wave(duration)
    engine_audio2 = sound_engine.generate_engine_wave(duration)
    wind_audio2 = sound_engine.generate_wind_noise(duration)
    
    # Mix manually
    mixed2 = propeller_audio2 + engine_audio2 + wind_audio2
    mixed2 = mixed2 * sound_engine.volume
    mixed2 = sound_engine.apply_soft_limiter(mixed2, threshold=0.80)
    
    # Convert to stereo manually
    buffer2 = np.zeros((num_samples, 2), dtype=np.float32)
    buffer2[:, 0] = mixed2
    buffer2[:, 1] = mixed2
    
    print(f"After buffer 2 phases: fund={sound_engine.phase_accumulator:.6f}, h2={sound_engine.phase_harmonic2:.6f}, h3={sound_engine.phase_harmonic3:.6f}")
    print(f"Buffer 2 start value: {buffer2[0][0]:.6f}")
    
    boundary_jump = abs(buffer2[0][0] - buffer1[-1][0])
    print(f"\nBoundary jump magnitude: {boundary_jump:.6f}")
    
    if boundary_jump > 0.01:
        print("⚠️  DISCONTINUITY DETECTED!")
    else:
        print("✅ Good continuity")
    
    pygame.quit()

if __name__ == "__main__":
    test_without_updates()
