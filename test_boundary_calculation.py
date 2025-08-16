#!/usr/bin/env python3
"""
Debug exact boundary calculations
"""

import pygame
import numpy as np
import math
from sound import AirshipSoundEngine
from core_simulator import get_simulator

def test_boundary_calculation():
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.set_engine_control("throttle", 0.6)
    simulator.set_engine_control("mixture", 0.8)
    simulator.update(0.1)
    
    sound_engine = AirshipSoundEngine(simulator)
    sound_engine.update_from_simulator()
    
    duration = 0.023  # 23ms buffer
    sample_rate = sound_engine.sample_rate
    dt = 1.0 / sample_rate
    num_samples = int(duration * sample_rate)
    
    # Calculate frequencies
    prop_frequency = (sound_engine.current_rpm / 60.0) * 2
    omega_fundamental = 2 * math.pi * prop_frequency
    omega_harmonic2 = omega_fundamental * 2
    omega_harmonic3 = omega_fundamental * 3
    
    pitch_amplitude = 0.2 + (sound_engine.current_pitch * 0.6)
    
    print(f"RPM: {sound_engine.current_rpm:.1f}")
    print(f"Prop frequency: {prop_frequency:.1f} Hz")
    print(f"Sample rate: {sample_rate}")
    print(f"Samples per buffer: {num_samples}")
    print(f"Buffer duration: {duration:.3f}s")
    print()
    
    # Calculate manually what the last sample of buffer 1 should be
    print("=== Manual calculation for buffer 1 last sample ===")
    last_sample_time = (num_samples - 1) * dt
    print(f"Last sample time in buffer: {last_sample_time:.6f}s")
    
    # Starting from phase 0 (first buffer)
    phase_start = 0.0
    phase_fund = phase_start + omega_fundamental * last_sample_time
    phase_h2 = phase_start + omega_harmonic2 * last_sample_time  
    phase_h3 = phase_start + omega_harmonic3 * last_sample_time
    
    fund = math.sin(phase_fund)
    h2 = 0.3 * math.sin(phase_h2)
    h3 = 0.15 * math.sin(phase_h3)
    manual_last = (fund + h2 + h3) * pitch_amplitude
    
    print(f"Phase fund: {phase_fund:.6f}")
    print(f"Phase h2: {phase_h2:.6f}")  
    print(f"Phase h3: {phase_h3:.6f}")
    print(f"Manual last sample: {manual_last:.6f}")
    
    # What should the phases be after buffer 1?
    expected_phase_fund = omega_fundamental * duration
    expected_phase_h2 = omega_harmonic2 * duration
    expected_phase_h3 = omega_harmonic3 * duration
    
    print(f"Expected phase updates: fund={expected_phase_fund:.6f}, h2={expected_phase_h2:.6f}, h3={expected_phase_h3:.6f}")
    
    # Calculate what buffer 2 first sample should be
    print("\n=== Manual calculation for buffer 2 first sample ===")
    
    # Buffer 2 starts with updated phases
    buffer2_phase_fund = expected_phase_fund % (2 * math.pi)
    buffer2_phase_h2 = expected_phase_h2 % (2 * math.pi)
    buffer2_phase_h3 = expected_phase_h3 % (2 * math.pi)
    
    # First sample of buffer 2 (t=0 in new buffer)
    first_sample_time = 0.0
    phase_fund_2 = buffer2_phase_fund + omega_fundamental * first_sample_time
    phase_h2_2 = buffer2_phase_h2 + omega_harmonic2 * first_sample_time
    phase_h3_2 = buffer2_phase_h3 + omega_harmonic3 * first_sample_time
    
    fund_2 = math.sin(phase_fund_2)
    h2_2 = 0.3 * math.sin(phase_h2_2)
    h3_2 = 0.15 * math.sin(phase_h3_2)
    manual_first = (fund_2 + h2_2 + h3_2) * pitch_amplitude
    
    print(f"Buffer 2 starting phases: fund={buffer2_phase_fund:.6f}, h2={buffer2_phase_h2:.6f}, h3={buffer2_phase_h3:.6f}")
    print(f"Manual first sample: {manual_first:.6f}")
    print(f"Manual boundary jump: {abs(manual_first - manual_last):.6f}")
    
    print("\n=== Actual generation test ===")
    
    # Now test actual generation
    buffer1 = sound_engine.generate_propeller_wave(duration)
    print(f"Actual buffer 1 last: {buffer1[-1]:.6f}")
    print(f"Phases after buffer 1: fund={sound_engine.phase_accumulator:.6f}, h2={sound_engine.phase_harmonic2:.6f}, h3={sound_engine.phase_harmonic3:.6f}")
    
    buffer2 = sound_engine.generate_propeller_wave(duration)
    print(f"Actual buffer 2 first: {buffer2[0]:.6f}")
    print(f"Actual boundary jump: {abs(buffer2[0] - buffer1[-1]):.6f}")
    
    pygame.quit()

if __name__ == "__main__":
    test_boundary_calculation()
