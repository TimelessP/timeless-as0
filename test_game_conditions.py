#!/usr/bin/env python3
"""
Test phase continuity with actual game simulation running
"""

import pygame
import numpy as np
from sound import AirshipSoundEngine
from core_simulator import get_simulator

def test_game_conditions():
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    
    # Start the engine and set RPM like in actual gameplay
    simulator.set_engine_control("throttle", 0.6)  # Set some throttle
    simulator.set_engine_control("mixture", 0.8)   # Set mixture for engine running
    
    # Let the simulator run for a moment to establish state
    simulator.update(0.1)
    
    sound_engine = AirshipSoundEngine(simulator)
    
    print("=== Testing with game simulation conditions ===")
    
    # Update sound engine from simulator (like the game loop does)
    sound_engine.update_from_simulator()
    
    print(f"Engine running: {sound_engine.is_engine_running}")
    print(f"Current RPM: {sound_engine.current_rpm}")
    print(f"Current airspeed: {sound_engine.current_airspeed}")
    
    print(f"Initial phases: fund={sound_engine.phase_accumulator:.6f}, h2={sound_engine.phase_harmonic2:.6f}, h3={sound_engine.phase_harmonic3:.6f}")
    
    # Generate two consecutive buffers like the audio system would
    duration = 0.023  # Typical buffer duration (23ms)
    
    print(f"\nGenerating first buffer ({duration:.3f}s)...")
    buffer1 = sound_engine.generate_audio_buffer(duration)
    
    print(f"After buffer 1 phases: fund={sound_engine.phase_accumulator:.6f}, h2={sound_engine.phase_harmonic2:.6f}, h3={sound_engine.phase_harmonic3:.6f}")
    print(f"Buffer 1 end values: {buffer1[-3:]}")
    
    print(f"\nGenerating second buffer ({duration:.3f}s)...")
    buffer2 = sound_engine.generate_audio_buffer(duration)
    
    print(f"After buffer 2 phases: fund={sound_engine.phase_accumulator:.6f}, h2={sound_engine.phase_harmonic2:.6f}, h3={sound_engine.phase_harmonic3:.6f}")
    print(f"Buffer 2 start values: {buffer2[:3]}")
    
    # Check continuity
    boundary_jump = abs(buffer2[0][0] - buffer1[-1][0])  # Extract scalar values
    print(f"\nBoundary jump magnitude: {boundary_jump:.6f}")
    
    print(f"Buffer 1 last value: {buffer1[-1][0]:.6f}")
    print(f"Buffer 2 first value: {buffer2[0][0]:.6f}")
    
    if boundary_jump > 0.01:
        print("⚠️  DISCONTINUITY DETECTED!")
    else:
        print("✅ Good continuity")
    
    # Calculate expected phase changes
    if sound_engine.current_rpm > 50:
        prop_freq = (sound_engine.current_rpm / 60.0) * 2
        omega = 2 * np.pi * prop_freq
        expected_change = omega * duration
        print(f"\nExpected phase change per buffer: {expected_change:.6f} radians")
        print(f"Expected change after modulo 2π: {expected_change % (2 * np.pi):.6f} radians")
    
    pygame.quit()

if __name__ == "__main__":
    test_game_conditions()
