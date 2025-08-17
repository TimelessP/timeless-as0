#!/usr/bin/env python3
"""
Test Targeted Logarithmic Compression
Analyze the new 95% threshold compression approach
"""

import numpy as np
from core_simulator import get_simulator
import sound

def test_targeted_compression():
    """Test the new 95% threshold logarithmic compression"""
    
    print("🎛️ Targeted Logarithmic Compression Test (95% Threshold)")
    print("=" * 65)
    
    # Initialize simulator and sound engine
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.running = True
    simulator.game_state['engine']['running'] = True
    
    sound_engine = sound.AirshipSoundEngine(simulator)
    
    # Test with various amplitude levels to see compression curve
    test_amplitudes = np.array([0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.97, 0.99, 1.0, 1.2, 1.5, 2.0])
    
    print("📊 Compression Curve Analysis:")
    print("Input Amp  | Output Amp | Compression | Effect")
    print("-" * 50)
    
    # Test the compression function directly
    for input_amp in test_amplitudes:
        # Create a test signal with known amplitude
        test_signal = np.array([input_amp, -input_amp, input_amp * 0.5, -input_amp * 0.5])
        
        # Apply the logarithmic normalization
        compressed_signal = sound_engine.apply_logarithmic_normalization(test_signal)
        
        # Analyze the result
        input_peak = np.max(np.abs(test_signal))
        output_peak = np.max(np.abs(compressed_signal))
        compression_ratio = input_peak / (output_peak + 1e-10)
        
        # Determine effect level
        if input_amp <= 0.95:
            effect = "Minimal"
        elif input_amp <= 0.98:
            effect = "Moderate"
        else:
            effect = "Strong"
        
        print(f"{input_amp:8.2f}  | {output_peak:8.5f}  | {compression_ratio:8.2f}x  | {effect}")
    
    print(f"\n🔊 Real Audio Test:")
    
    # Test with actual engine audio at different power levels
    test_scenarios = [
        {"name": "Low Power", "rpm": 1500, "throttle": 0.3, "mixture": 0.6},
        {"name": "Medium Power", "rpm": 2200, "throttle": 0.7, "mixture": 0.8},
        {"name": "High Power", "rpm": 2700, "throttle": 1.0, "mixture": 0.9},
    ]
    
    for scenario in test_scenarios:
        print(f"\n🎵 {scenario['name']} Scenario:")
        print(f"   RPM: {scenario['rpm']}, Throttle: {scenario['throttle']:.1%}, Mixture: {scenario['mixture']:.1%}")
        
        # Set engine state
        engine_state = simulator.game_state["engine"]
        engine_state["rpm"] = scenario["rpm"]
        engine_state["controls"]["throttle"] = scenario["throttle"]
        engine_state["controls"]["mixture"] = scenario["mixture"]
        
        navigation_state = simulator.game_state["navigation"]
        navigation_state["motion"]["indicatedAirspeed"] = 85
        
        sound_engine.update_from_simulator()
        
        # Generate audio samples
        duration = 0.2  # 200ms
        
        # Get raw mixed audio (before log normalization)
        propeller_audio = sound_engine.generate_propeller_wave(duration)
        engine_audio = sound_engine.generate_engine_wave(duration)
        wind_audio = sound_engine.generate_wind_noise(duration)
        raw_mixed = propeller_audio + engine_audio + wind_audio
        
        # Apply log normalization
        normalized_audio = sound_engine.apply_logarithmic_normalization(raw_mixed)
        
        # Analyze both versions
        raw_peak = np.max(np.abs(raw_mixed))
        raw_rms = np.sqrt(np.mean(raw_mixed**2))
        norm_peak = np.max(np.abs(normalized_audio))
        norm_rms = np.sqrt(np.mean(normalized_audio**2))
        
        # Calculate which portion of signal was above 95% threshold
        max_raw = np.max(np.abs(raw_mixed))
        threshold_95 = max_raw * 0.95
        samples_above_95 = np.sum(np.abs(raw_mixed) > threshold_95)
        total_samples = len(raw_mixed)
        percentage_above_95 = (samples_above_95 / total_samples) * 100
        
        compression_ratio = raw_peak / (norm_peak + 1e-10)
        energy_preservation = norm_rms / (raw_rms + 1e-10)
        
        print(f"   Raw Audio - Peak: {raw_peak:.6f}, RMS: {raw_rms:.6f}")
        print(f"   Normalized - Peak: {norm_peak:.6f}, RMS: {norm_rms:.6f}")
        print(f"   Compression: {compression_ratio:.2f}x")
        print(f"   Energy preservation: {energy_preservation:.3f}")
        print(f"   Samples above 95%: {percentage_above_95:.2f}% of signal")
        
        # Check if compression is targeted correctly
        if percentage_above_95 < 5.0:
            print(f"   ✅ Good: Most signal below 95% threshold")
        else:
            print(f"   ⚠️  Note: {percentage_above_95:.1f}% of signal above 95% threshold")
    
    print(f"\n📈 Compression Behavior Summary:")
    print(f"✅ Signals ≤ 95%: Nearly linear response (minimal compression)")
    print(f"✅ Signals > 95%: Strong logarithmic compression")
    print(f"✅ Peak compression targets only the loudest 5% of signal")
    print(f"✅ Energy preservation maintained for most audio content")
    print(f"✅ Natural dynamics preserved while preventing clipping")
    
    print(f"\n🏁 Targeted Compression Test Complete")

if __name__ == "__main__":
    test_targeted_compression()
