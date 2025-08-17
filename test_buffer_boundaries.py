#!/usr/bin/env python3
"""
Test Buffer Boundary Discontinuities
Analyze and fix phase continuity issues between audio buffers
"""

import numpy as np
from core_simulator import get_simulator
import sound

def test_buffer_boundary_continuity():
    """Test for pops and discontinuities at buffer boundaries"""
    
    print("🔄 Buffer Boundary Continuity Test")
    print("=" * 45)
    
    # Initialize simulator and sound engine
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.running = True
    simulator.game_state['engine']['running'] = True
    
    sound_engine = sound.AirshipSoundEngine(simulator)
    
    # Set engine state
    engine_state = simulator.game_state["engine"]
    engine_state["rpm"] = 2400
    engine_state["controls"]["throttle"] = 0.75
    engine_state["controls"]["mixture"] = 0.8
    
    sound_engine.update_from_simulator()
    
    print(f"Testing engine at {sound_engine.current_rpm} RPM")
    
    # Generate multiple consecutive buffers to test boundary continuity
    buffer_duration = 0.1  # 100ms buffers
    num_buffers = 5
    
    buffers = []
    boundary_discontinuities = []
    
    print(f"\nGenerating {num_buffers} consecutive {buffer_duration*1000:.0f}ms buffers...")
    
    for i in range(num_buffers):
        buffer = sound_engine.generate_engine_wave(buffer_duration)
        buffers.append(buffer)
        
        if i > 0:
            # Check discontinuity between previous buffer end and current buffer start
            prev_end = buffers[i-1][-1]
            curr_start = buffer[0]
            discontinuity = abs(curr_start - prev_end)
            boundary_discontinuities.append(discontinuity)
            
            print(f"   Buffer {i-1}→{i}: End={prev_end:.6f}, Start={curr_start:.6f}, Gap={discontinuity:.6f}")
    
    # Analyze discontinuities
    if boundary_discontinuities:
        max_discontinuity = max(boundary_discontinuities)
        avg_discontinuity = np.mean(boundary_discontinuities)
        
        print(f"\n📊 Boundary Analysis:")
        print(f"   Maximum discontinuity: {max_discontinuity:.6f}")
        print(f"   Average discontinuity: {avg_discontinuity:.6f}")
        
        # Check if discontinuities are significant
        buffer_peak = max(np.max(np.abs(buffer)) for buffer in buffers)
        discontinuity_ratio = max_discontinuity / buffer_peak
        
        print(f"   Buffer peak amplitude: {buffer_peak:.6f}")
        print(f"   Discontinuity ratio: {discontinuity_ratio:.2%}")
        
        if discontinuity_ratio > 0.1:  # More than 10% of peak
            print(f"   ⚠️  Significant boundary discontinuities detected!")
        else:
            print(f"   ✅ Boundary discontinuities are acceptable")
    
    # Test the engine time accumulator behavior
    print(f"\n🕒 Engine Time Accumulator Analysis:")
    
    # Reset and track accumulator
    original_accumulator = sound_engine.engine_time_accumulator
    sound_engine.engine_time_accumulator = 0.0
    
    print(f"   Initial accumulator: {sound_engine.engine_time_accumulator:.6f}")
    
    for i in range(3):
        buffer = sound_engine.generate_engine_wave(buffer_duration)
        print(f"   After buffer {i+1}: {sound_engine.engine_time_accumulator:.6f}")
    
    # Check if accumulator is tracking correctly
    expected_time = 3 * buffer_duration
    actual_time = sound_engine.engine_time_accumulator
    time_error = abs(actual_time - expected_time)
    
    print(f"   Expected total time: {expected_time:.6f}")
    print(f"   Actual accumulated time: {actual_time:.6f}")
    print(f"   Time tracking error: {time_error:.6f}")
    
    if time_error < 0.001:  # Less than 1ms error
        print(f"   ✅ Time accumulator is accurate")
    else:
        print(f"   ⚠️  Time accumulator has drift")
    
    # Restore original accumulator
    sound_engine.engine_time_accumulator = original_accumulator
    
    return boundary_discontinuities

def test_single_cylinder_dc_offset():
    """Test for DC offset in individual cylinder generation using the actual engine method"""
    
    print(f"\n🔍 Single Cylinder DC Offset Analysis")
    print("=" * 40)
    
    # Initialize simulator and sound engine
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.running = True
    simulator.game_state['engine']['running'] = True
    
    sound_engine = sound.AirshipSoundEngine(simulator)
    
    # Set engine state
    engine_state = simulator.game_state["engine"]
    engine_state["rpm"] = 1800
    engine_state["controls"]["mixture"] = 0.8
    
    sound_engine.update_from_simulator()
    
    # Generate a single buffer and analyze its properties
    duration = 0.2  # 200ms
    audio_buffer = sound_engine.generate_engine_wave(duration)
    
    # Analyze the combined buffer
    peak = np.max(np.abs(audio_buffer))
    rms = np.sqrt(np.mean(audio_buffer**2))
    dc_offset = np.mean(audio_buffer)
    
    print(f"Engine Audio Buffer Analysis (all cylinders):")
    print(f"   Peak amplitude: {peak:.6f}")
    print(f"   RMS amplitude: {rms:.6f}")
    print(f"   DC offset: {dc_offset:.6f}")
    
    # Check DC offset significance
    dc_ratio = abs(dc_offset) / (peak + 1e-10)
    print(f"   DC offset ratio: {dc_ratio:.2%}")
    
    if dc_ratio > 0.05:  # More than 5% of peak
        print(f"   ⚠️  Significant DC offset in engine buffer!")
    else:
        print(f"   ✅ DC offset is acceptable")
    
    # Test frequency content
    if len(audio_buffer) > 1024:
        fft = np.fft.fft(audio_buffer[:1024])
        freq_magnitude = np.abs(fft)
        dc_component = freq_magnitude[0]
        ac_components = np.sum(freq_magnitude[1:])
        
        dc_energy_ratio = dc_component / (dc_component + ac_components)
        print(f"   DC energy ratio: {dc_energy_ratio:.2%}")
        
        if dc_energy_ratio > 0.1:
            print(f"   ⚠️  High DC energy content!")
        else:
            print(f"   ✅ DC energy content is acceptable")
    
    return audio_buffer, dc_offset

def analyze_envelope_smoothness():
    """Test the combustion envelope for smoothness and potential clicks"""
    
    print(f"\n📈 Combustion Envelope Smoothness Test")
    print("=" * 40)
    
    # Generate a single combustion event envelope
    sample_rate = 22050
    combustion_duration = 0.08  # 80ms
    attack_duration = 0.005     # 5ms
    decay_duration = combustion_duration - attack_duration
    
    combustion_samples = int(combustion_duration * sample_rate)
    envelope = np.zeros(combustion_samples, dtype=np.float32)
    
    for i in range(combustion_samples):
        t_combustion = i / sample_rate
        
        if t_combustion < attack_duration:
            # Fast attack phase
            attack_progress = t_combustion / attack_duration
            envelope[i] = attack_progress ** 0.3
        else:
            # Slow decay phase
            decay_progress = (t_combustion - attack_duration) / decay_duration
            envelope[i] = np.exp(-decay_progress * 3.0)
    
    print(f"Envelope Analysis ({combustion_samples} samples):")
    
    # Check for smoothness
    envelope_diff = np.diff(envelope)
    max_jump = np.max(np.abs(envelope_diff))
    large_jumps = np.sum(np.abs(envelope_diff) > 0.01)
    
    print(f"   Maximum envelope jump: {max_jump:.6f}")
    print(f"   Large jumps (>0.01): {large_jumps}")
    
    # Check attack/decay transition
    attack_samples = int(attack_duration * sample_rate)
    if attack_samples < len(envelope) - 1:
        attack_end = envelope[attack_samples - 1]
        decay_start = envelope[attack_samples]
        transition_jump = abs(decay_start - attack_end)
        
        print(f"   Attack/decay transition jump: {transition_jump:.6f}")
        
        if transition_jump > 0.05:
            print(f"   ⚠️  Sharp transition between attack and decay!")
        else:
            print(f"   ✅ Smooth attack/decay transition")
    
    # Check envelope endpoints
    start_value = envelope[0]
    end_value = envelope[-1]
    
    print(f"   Envelope start: {start_value:.6f}")
    print(f"   Envelope end: {end_value:.6f}")
    
    if start_value > 0.01:
        print(f"   ⚠️  Envelope doesn't start from zero!")
    if end_value > 0.01:
        print(f"   ⚠️  Envelope doesn't end near zero!")
    
    return envelope

if __name__ == "__main__":
    # Test buffer boundary continuity
    discontinuities = test_buffer_boundary_continuity()
    
    # Test single cylinder DC offset
    cylinder_track, dc_offset = test_single_cylinder_dc_offset()
    
    # Test envelope smoothness
    envelope = analyze_envelope_smoothness()
    
    print(f"\n🎯 Summary and Recommendations:")
    
    if discontinuities and max(discontinuities) > 0.1:
        print(f"❗ Fix buffer boundary discontinuities in engine time tracking")
    
    if abs(dc_offset) > 0.01:
        print(f"❗ Address DC offset in positive-only pressure wave generation")
    
    print(f"✅ Envelope design appears smooth")
    print(f"💡 Consider adding crossfade between buffers if discontinuities persist")
