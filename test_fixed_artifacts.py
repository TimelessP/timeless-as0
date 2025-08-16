#!/usr/bin/env python3
"""
Test audio artifacts with the fixed sound engine
"""

import pygame
import numpy as np
from sound import AirshipSoundEngine
from core_simulator import get_simulator

def test_fixed_artifacts():
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.set_engine_control("throttle", 0.6)
    simulator.set_engine_control("mixture", 0.8)
    simulator.update(0.1)
    
    sound_engine = AirshipSoundEngine(simulator)
    
    print("=== Testing Fixed Sound Engine ===")
    
    # Simulate the game loop behavior: update_audio() calls update_from_simulator()
    sound_engine.update_audio()
    
    print(f"Engine running: {sound_engine.is_engine_running}")
    print(f"RPM: {sound_engine.current_rpm:.1f}")
    print(f"Airspeed: {sound_engine.current_airspeed:.1f}")
    
    # Now test multiple consecutive buffer generations without intermediate updates
    duration = 0.023
    
    print(f"\nInitial phases: fund={sound_engine.phase_accumulator:.6f}")
    
    # Generate 3 consecutive buffers like the audio system would
    buffers = []
    for i in range(3):
        buffer = sound_engine.generate_audio_buffer(duration)
        buffers.append(buffer[:, 0])  # Just left channel
        print(f"Buffer {i+1} phases: fund={sound_engine.phase_accumulator:.6f}")
        if i > 0:
            # Check boundary continuity
            prev_last = buffers[i-1][-1]
            current_first = buffers[i][0]
            jump = abs(current_first - prev_last)
            print(f"  Boundary jump {i}: {jump:.6f}")
            if jump > 0.01:
                print(f"  ⚠️  DISCONTINUITY between buffers {i} and {i+1}")
            else:
                print(f"  ✅ Good continuity between buffers {i} and {i+1}")
    
    # Test the amplitude levels
    all_audio = np.concatenate(buffers)
    max_amplitude = np.max(np.abs(all_audio))
    rms_amplitude = np.sqrt(np.mean(all_audio**2))
    
    print(f"\nAmplitude analysis:")
    print(f"  Max amplitude: {max_amplitude:.6f}")
    print(f"  RMS amplitude: {rms_amplitude:.6f}")
    
    if max_amplitude > 0.95:
        print("  ⚠️  Potential clipping detected")
    else:
        print("  ✅ Amplitude levels look good")
    
    pygame.quit()

if __name__ == "__main__":
    test_fixed_artifacts()
