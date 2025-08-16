#!/usr/bin/env python3
"""
Simple phase tracking test
"""

import pygame
import numpy as np
from sound import AirshipSoundEngine
from core_simulator import get_simulator

def test_simple_phase():
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    sound_engine = AirshipSoundEngine(simulator)
    
    # Force RPM to be non-zero
    sound_engine.current_rpm = 2400.0
    print(f"Set RPM to: {sound_engine.current_rpm}")
    
    print(f"Initial phases: fund={sound_engine.phase_accumulator:.6f}, h2={sound_engine.phase_harmonic2:.6f}, h3={sound_engine.phase_harmonic3:.6f}")
    
    # Generate a short buffer
    duration = 0.01  # 10ms
    print(f"Generating {duration} seconds of audio...")
    
    # Check if RPM is still set before generation
    print(f"RPM before generation: {sound_engine.current_rpm}")
    
    buffer = sound_engine.generate_propeller_wave(duration)
    
    print(f"After generation phases: fund={sound_engine.phase_accumulator:.6f}, h2={sound_engine.phase_harmonic2:.6f}, h3={sound_engine.phase_harmonic3:.6f}")
    
    # Calculate expected phase change
    prop_freq = (sound_engine.current_rpm / 60.0) * 2
    omega = 2 * np.pi * prop_freq
    expected_change = omega * duration
    
    print(f"Propeller frequency: {prop_freq:.1f} Hz")
    print(f"Expected phase change: {expected_change:.6f} radians")
    print(f"Expected after modulo 2π: {expected_change % (2 * np.pi):.6f} radians")
    
    # Check if audio was actually generated
    max_amp = np.max(np.abs(buffer))
    print(f"Generated buffer max amplitude: {max_amp:.6f}")
    
    pygame.quit()

if __name__ == "__main__":
    test_simple_phase()
