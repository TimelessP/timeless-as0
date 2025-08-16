#!/usr/bin/env python3
"""
Final test showing the improvement in audio continuity
"""

import pygame
import numpy as np
from sound import AirshipSoundEngine
from core_simulator import get_simulator

def test_final_improvement():
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.set_engine_control("throttle", 0.6)
    simulator.set_engine_control("mixture", 0.8)
    simulator.update(0.1)
    
    sound_engine = AirshipSoundEngine(simulator)
    sound_engine.update_from_simulator()
    
    print("=== FINAL AUDIO CONTINUITY TEST ===")
    print(f"Engine running: {sound_engine.is_engine_running}")
    print(f"RPM: {sound_engine.current_rpm:.1f}")
    print(f"Airspeed: {sound_engine.current_airspeed:.1f}")
    
    # Test complete audio buffer generation (the way it's used in the game)
    duration = 0.023  # 23ms buffer
    num_test_buffers = 5
    
    # Reset phases for consistent testing
    sound_engine.phase_accumulator = 0.0
    sound_engine.phase_harmonic2 = 0.0
    sound_engine.phase_harmonic3 = 0.0
    sound_engine.engine_phase = 0.0
    sound_engine.rumble_phase = 0.0
    sound_engine.noise_phase = 0.0
    
    print(f"\nGenerating {num_test_buffers} consecutive audio buffers...")
    
    buffers = []
    boundary_jumps = []
    
    for i in range(num_test_buffers):
        # Generate buffer manually (without calling update_from_simulator)
        # This simulates the fixed behavior where parameters don't change between buffers
        propeller = sound_engine.generate_propeller_wave(duration)
        engine = sound_engine.generate_engine_wave(duration)
        wind = sound_engine.generate_wind_noise(duration)
        
        # Mix components
        mixed = propeller + engine + wind
        mixed = mixed * sound_engine.volume
        mixed = sound_engine.apply_soft_limiter(mixed, threshold=0.80)
        
        # Convert to stereo
        num_samples = len(mixed)
        stereo_buffer = np.zeros((num_samples, 2), dtype=np.float32)
        stereo_buffer[:, 0] = mixed
        stereo_buffer[:, 1] = mixed
        
        buffers.append(stereo_buffer)
        
        if i > 0:
            # Check boundary continuity
            prev_last = buffers[i-1][-1, 0]  # Last sample of previous buffer (left channel)
            current_first = buffers[i][0, 0]  # First sample of current buffer (left channel)
            jump = abs(current_first - prev_last)
            boundary_jumps.append(jump)
            
            status = "✅ GOOD" if jump < 0.01 else "⚠️  DISCONTINUITY"
            print(f"  Buffer {i} boundary jump: {jump:.6f} {status}")
    
    # Calculate statistics
    max_jump = max(boundary_jumps)
    avg_jump = sum(boundary_jumps) / len(boundary_jumps)
    
    print(f"\n=== SUMMARY ===")
    print(f"Maximum boundary jump: {max_jump:.6f}")
    print(f"Average boundary jump: {avg_jump:.6f}")
    print(f"Number of good boundaries (< 0.01): {sum(1 for j in boundary_jumps if j < 0.01)}/{len(boundary_jumps)}")
    
    # Amplitude analysis
    all_audio = np.concatenate([buf[:, 0] for buf in buffers])
    max_amplitude = np.max(np.abs(all_audio))
    rms_amplitude = np.sqrt(np.mean(all_audio**2))
    
    print(f"\n=== AMPLITUDE ANALYSIS ===")
    print(f"Max amplitude: {max_amplitude:.6f}")
    print(f"RMS amplitude: {rms_amplitude:.6f}")
    
    clipping_status = "⚠️  POTENTIAL CLIPPING" if max_amplitude > 0.95 else "✅ NO CLIPPING"
    print(f"Clipping status: {clipping_status}")
    
    # Overall assessment
    print(f"\n=== OVERALL ASSESSMENT ===")
    if avg_jump < 0.01:
        print("✅ EXCELLENT: Audio continuity is very good")
    elif avg_jump < 0.02:
        print("✅ GOOD: Audio continuity is acceptable")
    elif avg_jump < 0.05:
        print("⚠️  FAIR: Some minor artifacts may be audible")
    else:
        print("❌ POOR: Significant audio artifacts present")
    
    pygame.quit()

if __name__ == "__main__":
    test_final_improvement()
