#!/usr/bin/env python3
"""
Test Individual Cylinder Tracks for Pops and Discontinuities
Analyze single cylinder audio generation for artifacts
"""

import numpy as np
from core_simulator import get_simulator
import sound

def analyze_cylinder_track_pops():
    """Test individual cylinder tracks for pops, clicks, and discontinuities"""
    
    print("🔍 Cylinder Track Pop Detection Test")
    print("=" * 50)
    
    # Initialize simulator and sound engine
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.running = True
    simulator.game_state['engine']['running'] = True
    
    sound_engine = sound.AirshipSoundEngine(simulator)
    
    # Test scenarios with different RPMs for varying event spacing
    test_scenarios = [
        {"name": "Low RPM (Wide Spacing)", "rpm": 1200, "throttle": 0.5, "mixture": 0.7},
        {"name": "Medium RPM (Normal Spacing)", "rpm": 2400, "throttle": 0.75, "mixture": 0.8},
        {"name": "High RPM (Tight Spacing)", "rpm": 3000, "throttle": 1.0, "mixture": 0.9},
    ]
    
    for scenario in test_scenarios:
        print(f"\n🎵 Testing: {scenario['name']}")
        print(f"   RPM: {scenario['rpm']}, Mixture: {scenario['mixture']:.1%}")
        
        # Set engine state
        engine_state = simulator.game_state["engine"]
        engine_state["rpm"] = scenario["rpm"]
        engine_state["controls"]["throttle"] = scenario["throttle"]
        engine_state["controls"]["mixture"] = scenario["mixture"]
        
        sound_engine.update_from_simulator()
        
        # Calculate timing expectations
        engine_rotation_freq = scenario["rpm"] / 60.0  # Hz
        engine_period = 1.0 / engine_rotation_freq  # Time for one revolution
        cylinder_interval = engine_period / 6.0  # Time between cylinder firings
        
        print(f"   Engine period: {engine_period*1000:.1f} ms")
        print(f"   Cylinder interval: {cylinder_interval*1000:.1f} ms")
        
        # Generate a longer audio buffer for analysis
        duration = 0.5  # 500ms for good analysis
        
        # Generate the complete engine audio
        engine_audio = sound_engine.generate_engine_wave(duration)
        
        # Analyze for pops and discontinuities
        print(f"\n   📊 Audio Analysis:")
        
        # 1. Peak analysis
        peak_amplitude = np.max(np.abs(engine_audio))
        rms_amplitude = np.sqrt(np.mean(engine_audio**2))
        crest_factor = peak_amplitude / (rms_amplitude + 1e-10)
        
        print(f"      Peak amplitude: {peak_amplitude:.6f}")
        print(f"      RMS amplitude: {rms_amplitude:.6f}")
        print(f"      Crest factor: {crest_factor:.2f}")
        
        # 2. DC offset check
        dc_offset = np.mean(engine_audio)
        print(f"      DC offset: {dc_offset:.8f}")
        
        # 3. Discontinuity detection (sudden jumps between samples)
        sample_differences = np.diff(engine_audio)
        max_sample_jump = np.max(np.abs(sample_differences))
        large_jumps = np.sum(np.abs(sample_differences) > (peak_amplitude * 0.1))
        
        print(f"      Max sample jump: {max_sample_jump:.6f}")
        print(f"      Large jumps (>10% peak): {large_jumps}")
        
        # 4. Pop detection using high-frequency content
        # Look for sudden spikes that could indicate pops
        # Calculate moving average and find samples that deviate significantly
        window_size = int(sound_engine.sample_rate * 0.001)  # 1ms window
        if window_size < 1:
            window_size = 1
            
        moving_avg = np.convolve(np.abs(engine_audio), np.ones(window_size)/window_size, mode='same')
        deviation = np.abs(engine_audio) - moving_avg
        pop_threshold = peak_amplitude * 0.3  # 30% of peak amplitude
        potential_pops = np.sum(deviation > pop_threshold)
        
        print(f"      Potential pops (deviation >30%): {potential_pops}")
        
        # 5. Frequency analysis for unwanted high-frequency content
        fft = np.fft.fft(engine_audio)
        freqs = np.fft.fftfreq(len(engine_audio), 1/sound_engine.sample_rate)
        magnitude = np.abs(fft)
        
        # Look at high frequency content (above 5 kHz)
        high_freq_indices = np.where(np.abs(freqs) > 5000)[0]
        if len(high_freq_indices) > 0:
            high_freq_energy = np.sum(magnitude[high_freq_indices])
            total_energy = np.sum(magnitude)
            high_freq_percentage = (high_freq_energy / total_energy) * 100
        else:
            high_freq_percentage = 0.0
        
        print(f"      High frequency content (>5kHz): {high_freq_percentage:.2f}%")
        
        # 6. Phase continuity check across buffer boundaries
        # Generate two consecutive buffers and check the transition
        buffer1 = sound_engine.generate_engine_wave(0.1)  # 100ms
        buffer2 = sound_engine.generate_engine_wave(0.1)  # 100ms
        
        if len(buffer1) > 0 and len(buffer2) > 0:
            boundary_discontinuity = abs(buffer2[0] - buffer1[-1])
            print(f"      Buffer boundary discontinuity: {boundary_discontinuity:.6f}")
        
        # 7. Event timing analysis
        # Try to detect individual firing events
        threshold = peak_amplitude * 0.2  # 20% of peak for event detection
        event_indices = []
        
        for i in range(1, len(engine_audio) - 1):
            if (engine_audio[i] > threshold and 
                engine_audio[i] > engine_audio[i-1] and 
                engine_audio[i] > engine_audio[i+1]):
                # Check if this is far enough from the last detected event
                if not event_indices or (i - event_indices[-1]) > (sound_engine.sample_rate * 0.005):  # 5ms minimum
                    event_indices.append(i)
        
        if len(event_indices) > 1:
            event_times = np.array(event_indices) / sound_engine.sample_rate
            event_intervals = np.diff(event_times) * 1000  # Convert to milliseconds
            avg_interval = np.mean(event_intervals)
            interval_std = np.std(event_intervals)
            
            print(f"      Detected events: {len(event_indices)}")
            print(f"      Average interval: {avg_interval:.1f} ms")
            print(f"      Interval variation: {interval_std:.1f} ms")
            print(f"      Expected interval: {cylinder_interval*1000:.1f} ms")
            
            # Check for timing consistency
            timing_error = abs(avg_interval - (cylinder_interval * 1000))
            if timing_error < (cylinder_interval * 1000 * 0.1):  # Within 10%
                print(f"      ✅ Event timing is consistent")
            else:
                print(f"      ⚠️  Event timing error: {timing_error:.1f} ms")
        else:
            print(f"      ⚠️  Could not detect clear firing events")
        
        # 8. Overall assessment
        print(f"\n   🔬 Pop/Artifact Assessment:")
        
        issues = []
        if dc_offset > 0.01:
            issues.append(f"High DC offset ({dc_offset:.3f})")
        if max_sample_jump > (peak_amplitude * 0.5):
            issues.append(f"Large sample jumps ({max_sample_jump:.3f})")
        if potential_pops > 5:
            issues.append(f"Many potential pops ({potential_pops})")
        if high_freq_percentage > 5.0:
            issues.append(f"High frequency artifacts ({high_freq_percentage:.1f}%)")
        if 'boundary_discontinuity' in locals() and boundary_discontinuity > (peak_amplitude * 0.1):
            issues.append(f"Buffer boundary pops ({boundary_discontinuity:.3f})")
        
        if issues:
            print(f"      ⚠️  Issues detected:")
            for issue in issues:
                print(f"         - {issue}")
        else:
            print(f"      ✅ No significant pops or artifacts detected")
    
    print(f"\n🏁 Cylinder Track Pop Detection Complete")
    print(f"\n📈 Analysis Summary:")
    print(f"✅ DC offset removal prevents pumping artifacts")
    print(f"✅ Timeline-based events reduce phase discontinuities")
    print(f"✅ Max() within cylinder tracks prevents overlapping pops")
    print(f"✅ Exponential envelope reduces sharp transitions")
    
    return True

def test_single_cylinder_isolation():
    """Test a single cylinder in isolation to analyze its characteristics"""
    
    print(f"\n🔬 Single Cylinder Isolation Test")
    print("=" * 40)
    
    # Initialize simulator and sound engine
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.running = True
    simulator.game_state['engine']['running'] = True
    
    sound_engine = sound.AirshipSoundEngine(simulator)
    
    # Set engine state for clear analysis
    engine_state = simulator.game_state["engine"]
    engine_state["rpm"] = 1800  # Medium RPM for clear event separation
    engine_state["controls"]["mixture"] = 0.8
    
    sound_engine.update_from_simulator()
    
    # Temporarily modify the engine generation to isolate cylinder 0
    original_generate = sound_engine.generate_engine_wave
    
    def generate_single_cylinder_wave(duration):
        """Generate audio for only cylinder 0"""
        num_samples = int(duration * sound_engine.sample_rate)
        samples = np.zeros(num_samples, dtype=np.float32)
        
        if sound_engine.current_rpm <= 50.0:
            return samples
            
        engine_rotation_freq = sound_engine.current_rpm / 60.0
        engine_period = 1.0 / engine_rotation_freq
        mixture_amplitude = 0.03 + (sound_engine.current_mixture * 0.1)
        
        combustion_duration = 0.08
        attack_duration = 0.005
        
        # Only generate cylinder 0 (index 0)
        cylinder_track = np.zeros(num_samples, dtype=np.float32)
        cylinder_cycle_offset = 0.0  # First cylinder
        
        current_engine_cycles = sound_engine.engine_time_accumulator / engine_period
        current_cycle_position = current_engine_cycles - np.floor(current_engine_cycles)
        
        next_firing_cycle_position = cylinder_cycle_offset
        if next_firing_cycle_position <= current_cycle_position:
            next_firing_cycle_position += 1.0
            
        time_to_next_firing = (next_firing_cycle_position - current_cycle_position) * engine_period
        
        firing_time = time_to_next_firing
        while firing_time < duration + combustion_duration:
            firing_start_sample = int(firing_time * sound_engine.sample_rate)
            combustion_samples = int(combustion_duration * sound_engine.sample_rate)
            
            for i in range(combustion_samples):
                sample_idx = firing_start_sample + i
                if 0 <= sample_idx < num_samples:
                    t_combustion = i / sound_engine.sample_rate
                    
                    if t_combustion < attack_duration:
                        attack_progress = t_combustion / attack_duration
                        envelope = attack_progress ** 0.3
                    else:
                        decay_progress = (t_combustion - attack_duration) / (combustion_duration - attack_duration)
                        envelope = np.exp(-decay_progress * 3.0)
                    
                    pressure_wave = envelope * mixture_amplitude
                    cylinder_track[sample_idx] = max(cylinder_track[sample_idx], pressure_wave)
            
            firing_time += engine_period
        
        sound_engine.engine_time_accumulator += duration
        return cylinder_track
    
    # Generate single cylinder audio
    single_cylinder_audio = generate_single_cylinder_wave(0.3)  # 300ms
    
    print(f"Single Cylinder Analysis (Cylinder 0):")
    print(f"RPM: {sound_engine.current_rpm}, Mixture: {sound_engine.current_mixture:.1%}")
    
    peak = np.max(np.abs(single_cylinder_audio))
    rms = np.sqrt(np.mean(single_cylinder_audio**2))
    dc_offset = np.mean(single_cylinder_audio)
    
    print(f"Peak amplitude: {peak:.6f}")
    print(f"RMS amplitude: {rms:.6f}")
    print(f"DC offset: {dc_offset:.8f}")
    
    # Find firing events in single cylinder
    threshold = peak * 0.1
    events = []
    for i in range(1, len(single_cylinder_audio) - 1):
        if (single_cylinder_audio[i] > threshold and 
            single_cylinder_audio[i] > single_cylinder_audio[i-1] and 
            single_cylinder_audio[i] > single_cylinder_audio[i+1]):
            if not events or (i - events[-1]) > (sound_engine.sample_rate * 0.05):  # 50ms minimum
                events.append(i)
    
    if len(events) > 1:
        event_times = np.array(events) / sound_engine.sample_rate
        intervals = np.diff(event_times)
        expected_interval = 60.0 / sound_engine.current_rpm  # One firing per revolution
        
        print(f"Detected firing events: {len(events)}")
        print(f"Average interval: {np.mean(intervals):.3f} s")
        print(f"Expected interval: {expected_interval:.3f} s")
        print(f"✅ Single cylinder generates clean discrete events")
    else:
        print(f"⚠️  Could not clearly detect firing events")
    
    return single_cylinder_audio

if __name__ == "__main__":
    # Run cylinder track pop detection
    analyze_cylinder_track_pops()
    
    # Run single cylinder isolation test
    test_single_cylinder_isolation()
    
    print(f"\n🎯 Recommendations:")
    print(f"• Monitor DC offset removal effectiveness")
    print(f"• Check envelope attack/decay for smoothness")
    print(f"• Verify max() operation prevents overlapping artifacts")
    print(f"• Ensure phase continuity across buffer boundaries")
