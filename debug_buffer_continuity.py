#!/usr/bin/env python3
"""
Debug script to isolate the buffer boundary discontinuity issue
"""

import pygame
import numpy as np
import time
from core_simulator import get_simulator
from sound import AirshipSoundEngine

def debug_buffer_continuity():
    """Debug the buffer boundary issue"""
    print("🔧 Debug: Buffer Boundary Continuity")
    print("=" * 50)
    
    # Initialize pygame
    pygame.init()
    
    # Create simulator and sound engine
    simulator = get_simulator()
    simulator.start_new_game()
    sound_engine = AirshipSoundEngine(simulator)
    
    # Set consistent state
    state = simulator.get_state()
    state["engine"]["running"] = True
    state["engine"]["rpm"] = 2400
    state["engine"]["controls"]["throttle"] = 0.75
    state["engine"]["controls"]["mixture"] = 0.85
    state["engine"]["controls"]["propeller"] = 0.8
    state["navigation"]["motion"]["indicatedAirspeed"] = 85.0
    
    print("Fixed simulator state for consistent testing")
    
    # Test: Direct component generation (no state updates)
    print("\n1. Testing direct component generation (no update_from_simulator):")
    
    # Manually set sound engine parameters to avoid state changes
    sound_engine.current_rpm = 2400
    sound_engine.current_pitch = 0.8
    sound_engine.current_mixture = 0.85
    sound_engine.current_airspeed = 85.0
    sound_engine.is_engine_running = True
    sound_engine.is_simulation_paused = False
    sound_engine.volume = 0.5
    
    buffer_duration = 0.1  # 100ms
    
    # Generate multiple buffers WITHOUT calling update_from_simulator
    direct_buffers = []
    for i in range(3):
        # Generate components directly
        prop = sound_engine.generate_propeller_wave(buffer_duration)
        engine = sound_engine.generate_engine_wave(buffer_duration)
        wind = sound_engine.generate_wind_noise(buffer_duration)
        
        # Mix manually
        mixed = (prop + engine + wind) * sound_engine.volume
        mixed = sound_engine.apply_soft_limiter(mixed)
        
        direct_buffers.append(mixed)
        
        # Check end value
        print(f"   Buffer {i}: ends at {mixed[-1]:.6f}")
    
    # Check direct buffer continuity
    for i in range(len(direct_buffers) - 1):
        end_val = direct_buffers[i][-1]
        start_val = direct_buffers[i+1][0]
        jump = abs(end_val - start_val)
        print(f"   Direct buffer {i}->{i+1} jump: {jump:.6f}")
    
    print("\n2. Testing via generate_audio_buffer (with update_from_simulator):")
    
    # Reset phases to compare
    sound_engine.phase_accumulator = 0.0
    sound_engine.phase_harmonic2 = 0.0
    sound_engine.phase_harmonic3 = 0.0
    sound_engine.engine_phase = 0.0
    sound_engine.rumble_phase = 0.0
    sound_engine.noise_phase = 0.0
    
    # Generate buffers via the normal method
    normal_buffers = []
    for i in range(3):
        buffer = sound_engine.generate_audio_buffer(buffer_duration)
        mono_buffer = buffer[:, 0]  # Left channel
        normal_buffers.append(mono_buffer)
        print(f"   Buffer {i}: ends at {mono_buffer[-1]:.6f}")
    
    # Check normal buffer continuity
    for i in range(len(normal_buffers) - 1):
        end_val = normal_buffers[i][-1]
        start_val = normal_buffers[i+1][0]
        jump = abs(end_val - start_val)
        print(f"   Normal buffer {i}->{i+1} jump: {jump:.6f}")
    
    print("\n3. Testing individual component phase continuity:")
    
    # Reset and test propeller phase continuity
    sound_engine.phase_accumulator = 0.0
    sound_engine.phase_harmonic2 = 0.0
    sound_engine.phase_harmonic3 = 0.0
    
    print("   Propeller wave phase continuity:")
    prop_buffers = []
    for i in range(3):
        prop_buffer = sound_engine.generate_propeller_wave(buffer_duration)
        prop_buffers.append(prop_buffer)
        print(f"     Buffer {i}: ends at {prop_buffer[-1]:.6f}")
        print(f"     Phase state: fund={sound_engine.phase_accumulator:.3f}, h2={sound_engine.phase_harmonic2:.3f}, h3={sound_engine.phase_harmonic3:.3f}")
    
    for i in range(len(prop_buffers) - 1):
        end_val = prop_buffers[i][-1]
        start_val = prop_buffers[i+1][0]
        jump = abs(end_val - start_val)
        print(f"     Prop buffer {i}->{i+1} jump: {jump:.6f}")
    
    # Test engine phase continuity
    sound_engine.engine_phase = 0.0
    sound_engine.rumble_phase = 0.0
    
    print("   Engine wave phase continuity:")
    engine_buffers = []
    for i in range(3):
        engine_buffer = sound_engine.generate_engine_wave(buffer_duration)
        engine_buffers.append(engine_buffer)
        print(f"     Buffer {i}: ends at {engine_buffer[-1]:.6f}")
        print(f"     Phase state: firing={sound_engine.engine_phase:.3f}, rumble={sound_engine.rumble_phase:.3f}")
    
    for i in range(len(engine_buffers) - 1):
        end_val = engine_buffers[i][-1]
        start_val = engine_buffers[i+1][0]
        jump = abs(end_val - start_val)
        print(f"     Engine buffer {i}->{i+1} jump: {jump:.6f}")
    
    print("\n4. Phase accumulator behavior test:")
    
    # Test what happens to phases over time
    sound_engine.phase_accumulator = 0.0
    sound_engine.phase_harmonic2 = 0.0
    sound_engine.phase_harmonic3 = 0.0
    
    rpm = 2400
    prop_freq = (rpm / 60.0) * 2  # 80 Hz
    omega = 2 * np.pi * prop_freq
    
    for i in range(5):
        phase_before = sound_engine.phase_accumulator
        prop_buffer = sound_engine.generate_propeller_wave(buffer_duration)
        phase_after = sound_engine.phase_accumulator
        
        expected_phase_change = omega * buffer_duration
        actual_phase_change = phase_after - phase_before
        
        print(f"   Step {i}: phase {phase_before:.3f} -> {phase_after:.3f}")
        print(f"            expected change: {expected_phase_change:.3f}, actual: {actual_phase_change:.3f}")
        
        # Check if phase is wrapping properly
        if actual_phase_change < 0:
            print(f"            (wrapped around 2π)")
    
    pygame.quit()

def main():
    debug_buffer_continuity()

if __name__ == "__main__":
    main()
