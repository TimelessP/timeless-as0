#!/usr/bin/env python3
"""
Deep dive into propeller phase continuity issues
"""

import pygame
import numpy as np
import math
from sound import AirshipSoundEngine
from core_simulator import get_simulator

def test_propeller_phase_detail():
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.set_engine_control("throttle", 0.6)
    simulator.set_engine_control("mixture", 0.8)
    simulator.update(0.1)
    
    sound_engine = AirshipSoundEngine(simulator)
    sound_engine.update_from_simulator()
    
    print("=== PROPELLER PHASE CONTINUITY DEEP DIVE ===")
    print(f"RPM: {sound_engine.current_rpm:.6f}")
    
    # Calculate exact frequencies
    prop_freq = (sound_engine.current_rpm / 60.0) * 2
    omega_fundamental = 2 * math.pi * prop_freq
    omega_harmonic2 = omega_fundamental * 2
    omega_harmonic3 = omega_fundamental * 3
    
    print(f"Propeller frequency: {prop_freq:.6f} Hz")
    print(f"Omega fundamental: {omega_fundamental:.6f} rad/s")
    print(f"Omega harmonic 2: {omega_harmonic2:.6f} rad/s")
    print(f"Omega harmonic 3: {omega_harmonic3:.6f} rad/s")
    
    duration = 0.023  # 23ms buffer
    
    # Reset phases
    sound_engine.phase_accumulator = 0.0
    sound_engine.phase_harmonic2 = 0.0
    sound_engine.phase_harmonic3 = 0.0
    
    print(f"\nBuffer duration: {duration:.6f}s")
    print(f"Expected phase changes:")
    print(f"  Fundamental: {omega_fundamental * duration:.6f} rad")
    print(f"  Harmonic 2: {omega_harmonic2 * duration:.6f} rad")
    print(f"  Harmonic 3: {omega_harmonic3 * duration:.6f} rad")
    
    # Manual calculation of last sample vs first sample of next buffer
    num_samples = int(duration * sound_engine.sample_rate)
    dt = 1.0 / sound_engine.sample_rate
    last_sample_time = (num_samples - 1) * dt
    
    print(f"\nBuffer has {num_samples} samples")
    print(f"Last sample time: {last_sample_time:.6f}s")
    
    # Calculate what the last sample of buffer 1 should be
    print(f"\n=== MANUAL BUFFER 1 LAST SAMPLE ===")
    phase_fund_last = omega_fundamental * last_sample_time
    phase_h2_last = omega_harmonic2 * last_sample_time
    phase_h3_last = omega_harmonic3 * last_sample_time
    
    print(f"Phases at last sample:")
    print(f"  Fundamental: {phase_fund_last:.6f} rad")
    print(f"  Harmonic 2: {phase_h2_last:.6f} rad")
    print(f"  Harmonic 3: {phase_h3_last:.6f} rad")
    
    pitch_amplitude = 0.2 + (sound_engine.current_pitch * 0.6)
    
    fund_last = math.sin(phase_fund_last)
    h2_last = 0.3 * math.sin(phase_h2_last)
    h3_last = 0.15 * math.sin(phase_h3_last)
    manual_last = (fund_last + h2_last + h3_last) * pitch_amplitude
    
    print(f"Component values at last sample:")
    print(f"  Fundamental: {fund_last:.6f}")
    print(f"  Harmonic 2: {h2_last:.6f}")
    print(f"  Harmonic 3: {h3_last:.6f}")
    print(f"  Combined: {manual_last:.6f}")
    
    # Now calculate the first sample of buffer 2
    print(f"\n=== MANUAL BUFFER 2 FIRST SAMPLE ===")
    # After buffer 1, phases should be updated by omega * duration
    phase_fund_buffer2_start = (omega_fundamental * duration) % (2 * math.pi)
    phase_h2_buffer2_start = (omega_harmonic2 * duration) % (2 * math.pi)
    phase_h3_buffer2_start = (omega_harmonic3 * duration) % (2 * math.pi)
    
    print(f"Buffer 2 starting phases (after modulo):")
    print(f"  Fundamental: {phase_fund_buffer2_start:.6f} rad")
    print(f"  Harmonic 2: {phase_h2_buffer2_start:.6f} rad")
    print(f"  Harmonic 3: {phase_h3_buffer2_start:.6f} rad")
    
    # First sample of buffer 2 (t=0)
    fund_first = math.sin(phase_fund_buffer2_start)
    h2_first = 0.3 * math.sin(phase_h2_buffer2_start)
    h3_first = 0.15 * math.sin(phase_h3_buffer2_start)
    manual_first = (fund_first + h2_first + h3_first) * pitch_amplitude
    
    print(f"Component values at first sample of buffer 2:")
    print(f"  Fundamental: {fund_first:.6f}")
    print(f"  Harmonic 2: {h2_first:.6f}")
    print(f"  Harmonic 3: {h3_first:.6f}")
    print(f"  Combined: {manual_first:.6f}")
    
    manual_jump = abs(manual_first - manual_last)
    print(f"\nManual calculated jump: {manual_jump:.6f}")
    
    # Compare with actual generation
    print(f"\n=== ACTUAL GENERATION TEST ===")
    buffer1 = sound_engine.generate_propeller_wave(duration)
    actual_last = buffer1[-1]
    
    print(f"Actual last sample of buffer 1: {actual_last:.6f}")
    print(f"Manual vs actual last: {abs(actual_last - manual_last):.8f} (should be ~0)")
    
    buffer2 = sound_engine.generate_propeller_wave(duration)
    actual_first = buffer2[0]
    
    print(f"Actual first sample of buffer 2: {actual_first:.6f}")
    print(f"Manual vs actual first: {abs(actual_first - manual_first):.8f} (should be ~0)")
    
    actual_jump = abs(actual_first - actual_last)
    print(f"Actual jump: {actual_jump:.6f}")
    print(f"Manual vs actual jump: {abs(actual_jump - manual_jump):.8f}")
    
    # Check if the issue is in the harmonic phase relationships
    print(f"\n=== HARMONIC ANALYSIS ===")
    print(f"Fundamental period: {2 * math.pi / omega_fundamental:.6f}s")
    print(f"Harmonic 2 period: {2 * math.pi / omega_harmonic2:.6f}s")
    print(f"Harmonic 3 period: {2 * math.pi / omega_harmonic3:.6f}s")
    
    # Check if buffer duration creates phase wrapping issues
    fund_cycles = (omega_fundamental * duration) / (2 * math.pi)
    h2_cycles = (omega_harmonic2 * duration) / (2 * math.pi)
    h3_cycles = (omega_harmonic3 * duration) / (2 * math.pi)
    
    print(f"Cycles per buffer:")
    print(f"  Fundamental: {fund_cycles:.6f} cycles")
    print(f"  Harmonic 2: {h2_cycles:.6f} cycles")
    print(f"  Harmonic 3: {h3_cycles:.6f} cycles")
    
    pygame.quit()

if __name__ == "__main__":
    test_propeller_phase_detail()
