#!/usr/bin/env python3
"""
Audio Artifact Diagnostic Tool
Analyzes audio generation for clipping, discontinuities, and other artifacts
"""

import pygame
import numpy as np
import time
from core_simulator import get_simulator
from sound import AirshipSoundEngine

def analyze_audio_artifacts():
    """Analyze audio for potential artifacts and issues"""
    print("🔍 Audio Artifact Analysis")
    print("=" * 50)
    
    # Initialize pygame (required for audio)
    pygame.init()
    
    # Create simulator and sound engine
    simulator = get_simulator()
    simulator.start_new_game()
    sound_engine = AirshipSoundEngine(simulator)
    
    # Set up a realistic flight scenario with engine running
    state = simulator.get_state()
    state["engine"]["running"] = True
    state["engine"]["rpm"] = 2400
    state["engine"]["controls"]["throttle"] = 0.75
    state["engine"]["controls"]["mixture"] = 0.85
    state["engine"]["controls"]["propeller"] = 0.8
    state["navigation"]["motion"]["indicatedAirspeed"] = 85.0
    
    print("Test scenario: Cruise flight (2400 RPM, 85 kts)")
    print("Analyzing potential audio artifacts...\n")
    
    # Generate audio buffers to analyze
    test_duration = 1.0  # 1 second of audio
    
    # Generate individual components for analysis
    propeller_audio = sound_engine.generate_propeller_wave(test_duration)
    engine_audio = sound_engine.generate_engine_wave(test_duration)
    wind_audio = sound_engine.generate_wind_noise(test_duration)
    
    # Generate mixed audio
    mixed_audio_raw = propeller_audio + engine_audio + wind_audio
    
    # Apply volume and normalization like the real generate_audio_buffer
    mixed_audio_vol = mixed_audio_raw * sound_engine.volume
    
    # Check for clipping before normalization
    max_before_norm = np.max(np.abs(mixed_audio_vol))
    
    # Apply normalization if needed
    if max_before_norm > 0.85:
        normalize_factor = 0.85 / max_before_norm
        mixed_audio_final = mixed_audio_vol * normalize_factor
        print(f"⚠️  Normalization applied: factor = {normalize_factor:.3f}")
    else:
        mixed_audio_final = mixed_audio_vol
        print(f"✅ No normalization needed: max = {max_before_norm:.3f}")
    
    print(f"\n📊 Audio Analysis Results:")
    print(f"   Sample rate: {sound_engine.sample_rate} Hz")
    print(f"   Duration: {test_duration:.1f} seconds")
    print(f"   Samples: {len(mixed_audio_final)}")
    
    # Component amplitude analysis
    prop_max = np.max(np.abs(propeller_audio))
    prop_rms = np.sqrt(np.mean(propeller_audio**2))
    engine_max = np.max(np.abs(engine_audio))
    engine_rms = np.sqrt(np.mean(engine_audio**2))
    wind_max = np.max(np.abs(wind_audio))
    wind_rms = np.sqrt(np.mean(wind_audio**2))
    
    print(f"\n🔊 Component Analysis:")
    print(f"   Propeller: Max={prop_max:.4f}, RMS={prop_rms:.4f}")
    print(f"   Engine:    Max={engine_max:.4f}, RMS={engine_rms:.4f}")
    print(f"   Wind:      Max={wind_max:.4f}, RMS={wind_rms:.4f}")
    
    # Mixed audio analysis
    mixed_max = np.max(np.abs(mixed_audio_final))
    mixed_rms = np.sqrt(np.mean(mixed_audio_final**2))
    mixed_min = np.min(mixed_audio_final)
    mixed_max_pos = np.max(mixed_audio_final)
    
    print(f"\n📈 Mixed Audio Analysis:")
    print(f"   Max amplitude: {mixed_max:.4f}")
    print(f"   RMS amplitude: {mixed_rms:.4f}")
    print(f"   Range: {mixed_min:.4f} to {mixed_max_pos:.4f}")
    print(f"   Dynamic range: {20 * np.log10(mixed_max / mixed_rms):.1f} dB")
    
    # Check for clipping (values at or near ±1.0)
    clipping_threshold = 0.99
    clipped_samples = np.sum(np.abs(mixed_audio_final) >= clipping_threshold)
    clipping_percentage = (clipped_samples / len(mixed_audio_final)) * 100
    
    if clipped_samples > 0:
        print(f"⚠️  CLIPPING DETECTED: {clipped_samples} samples ({clipping_percentage:.2f}%)")
    else:
        print(f"✅ No clipping detected")
    
    # Check for DC offset
    dc_offset = np.mean(mixed_audio_final)
    if abs(dc_offset) > 0.01:
        print(f"⚠️  DC offset detected: {dc_offset:.4f}")
    else:
        print(f"✅ No significant DC offset: {dc_offset:.6f}")
    
    # Analyze discontinuities (large sample-to-sample jumps)
    diffs = np.diff(mixed_audio_final)
    max_diff = np.max(np.abs(diffs))
    large_jumps = np.sum(np.abs(diffs) > 0.1)  # Arbitrary threshold
    
    print(f"\n🔗 Continuity Analysis:")
    print(f"   Max sample difference: {max_diff:.4f}")
    print(f"   Large jumps (>0.1): {large_jumps}")
    
    if max_diff > 0.2:
        print(f"⚠️  Potential discontinuity: max jump = {max_diff:.4f}")
    else:
        print(f"✅ Smooth audio signal")
    
    # Frequency analysis (basic)
    # Check for unexpected DC or very low frequency content
    fft = np.fft.fft(mixed_audio_final)
    freqs = np.fft.fftfreq(len(mixed_audio_final), 1/sound_engine.sample_rate)
    magnitude = np.abs(fft)
    
    # Check DC component
    dc_magnitude = magnitude[0] / len(mixed_audio_final)
    print(f"\n🌊 Frequency Analysis:")
    print(f"   DC component magnitude: {dc_magnitude:.6f}")
    
    # Find dominant frequencies
    positive_freqs = freqs[:len(freqs)//2]
    positive_magnitudes = magnitude[:len(magnitude)//2]
    
    # Exclude DC (index 0)
    dominant_indices = np.argsort(positive_magnitudes[1:])[-5:] + 1
    dominant_freqs = positive_freqs[dominant_indices]
    dominant_mags = positive_magnitudes[dominant_indices]
    
    print(f"   Top frequencies:")
    for i, (freq, mag) in enumerate(zip(dominant_freqs, dominant_mags)):
        print(f"     {i+1}: {freq:.1f} Hz (magnitude: {mag:.0f})")
    
    # Expected frequencies for verification
    rpm = state["engine"]["rpm"]
    prop_freq = (rpm / 60.0) * 2  # 2-blade propeller
    engine_freq = (rpm / 60.0) * 6  # 6-cylinder engine
    
    print(f"\n🎯 Expected Frequencies:")
    print(f"   Propeller fundamental: {prop_freq:.1f} Hz")
    print(f"   Engine firing rate: {engine_freq:.1f} Hz")
    
    # Generate multiple consecutive buffers to check for buffer boundary artifacts
    print(f"\n🔄 Buffer Continuity Test:")
    buffer_duration = sound_engine.buffer_size / sound_engine.sample_rate
    print(f"   Buffer duration: {buffer_duration*1000:.1f} ms")
    
    # Generate 3 consecutive buffers
    buffers = []
    for i in range(3):
        buffer = sound_engine.generate_audio_buffer(buffer_duration)[:, 0]  # Just left channel
        buffers.append(buffer)
    
    # Check continuity between buffers
    for i in range(len(buffers) - 1):
        end_val = buffers[i][-1]
        start_val = buffers[i+1][0]
        boundary_jump = abs(end_val - start_val)
        print(f"   Buffer {i}->{i+1} boundary jump: {boundary_jump:.6f}")
        
        if boundary_jump > 0.1:
            print(f"     ⚠️  Large boundary discontinuity detected!")
        else:
            print(f"     ✅ Smooth buffer transition")
    
    # Test with different amplitude levels to see if artifacts scale
    print(f"\n🔊 Volume Level Artifact Test:")
    volume_levels = [0.2, 0.5, 0.8, 1.0]
    
    for vol in volume_levels:
        sound_engine.volume = vol
        test_buffer = sound_engine.generate_audio_buffer(0.1)[:, 0]  # 100ms test
        max_amp = np.max(np.abs(test_buffer))
        rms_amp = np.sqrt(np.mean(test_buffer**2))
        
        # Check for distortion indicators
        crest_factor = max_amp / rms_amp if rms_amp > 0 else 0
        
        print(f"   Volume {vol:.1f}: Max={max_amp:.4f}, RMS={rms_amp:.4f}, Crest={crest_factor:.1f}")
        
        if crest_factor > 10:
            print(f"     ⚠️  High crest factor - possible impulsive artifacts")
        elif max_amp > 0.95:
            print(f"     ⚠️  Near-clipping levels")
        else:
            print(f"     ✅ Clean audio levels")
    
    print(f"\n🏁 Artifact Analysis Complete!")
    print(f"\nRecommendations:")
    
    if clipped_samples > 0:
        print("• CLIPPING: Reduce component amplitudes or lower normalization threshold")
    
    if max_diff > 0.2:
        print("• DISCONTINUITIES: Check phase continuity across buffer boundaries")
    
    if abs(dc_offset) > 0.01:
        print("• DC OFFSET: Add high-pass filtering or check component DC bias")
    
    # Reset volume
    sound_engine.volume = 0.5
    
    pygame.quit()

def main():
    try:
        analyze_audio_artifacts()
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
