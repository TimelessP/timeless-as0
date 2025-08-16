#!/usr/bin/env python3
"""
Test script for wind noise amplitude
Testing the doubled wind amplitude
"""

import pygame
import numpy as np
import time
from core_simulator import get_simulator
from sound import AirshipSoundEngine

def main():
    print("🌬️ Testing Doubled Wind Noise Amplitude")
    print("=" * 50)
    
    # Initialize pygame (required for audio)
    pygame.init()
    
    # Create simulator and sound engine
    simulator = get_simulator()
    simulator.start_new_game()
    sound_engine = AirshipSoundEngine(simulator)
    
    # Test wind noise at different airspeeds
    test_scenarios = [
        {
            "name": "Engine OFF, Low speed (10 kts)",
            "engine_running": False,
            "airspeed": 10.0,
            "expected": "Should hear light wind noise"
        },
        {
            "name": "Engine OFF, Medium speed (35 kts)",
            "engine_running": False,
            "airspeed": 35.0,
            "expected": "Should hear moderate wind noise"
        },
        {
            "name": "Engine OFF, High speed (65 kts)",
            "engine_running": False,
            "airspeed": 65.0,
            "expected": "Should hear strong wind noise"
        },
        {
            "name": "Engine OFF, Very high speed (100 kts)",
            "engine_running": False,
            "airspeed": 100.0,
            "expected": "Should hear maximum wind noise"
        }
    ]
    
    print("Testing wind noise amplitude at different airspeeds...")
    print("Listen for clear, audible wind sounds at each speed\n")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🌬️ Test {i}/4: {scenario['name']}")
        print(f"   Expected: {scenario['expected']}")
        
        # Set up simulator state - engine OFF for pure wind testing
        simulator.set_engine_control("throttle", 0.0)
        current_state = simulator.get_state()
        if current_state["engine"]["running"]:
            simulator.toggle_engine()
        
        # Set airspeed for testing
        state = simulator.get_state()
        state["navigation"]["motion"]["indicatedAirspeed"] = scenario["airspeed"]
        state["navigation"]["motion"]["groundSpeed"] = scenario["airspeed"]
        state["engine"]["rpm"] = 0.0  # Ensure engine is silent
        
        print(f"   Airspeed: {scenario['airspeed']:.1f} kts, Engine: OFF")
        
        # Generate and analyze audio for this scenario
        test_buffer = sound_engine.generate_audio_buffer(0.5)  # 0.5 second test buffer
        
        # Analyze the audio content
        max_amplitude = np.max(np.abs(test_buffer))
        rms_amplitude = np.sqrt(np.mean(test_buffer**2))
        
        print(f"   Audio analysis: Max amplitude: {max_amplitude:.4f}, RMS: {rms_amplitude:.4f}")
        
        if max_amplitude < 0.001:
            print("   🔇 Result: Complete silence (unexpected!)")
        elif max_amplitude < 0.01:
            print("   🔉 Result: Very quiet wind noise")
        elif max_amplitude < 0.05:
            print("   🔊 Result: Audible wind noise")
        else:
            print("   🔊 Result: Strong wind noise")
        
        # Play the audio for user evaluation
        try:
            # Update audio in real-time for user listening
            duration = 3.0  # 3 seconds per test
            elapsed = 0.0
            while elapsed < duration:
                sound_engine.update_audio()
                time.sleep(0.05)  # 50ms updates
                elapsed += 0.05
                
        except KeyboardInterrupt:
            print("\n⏹️  Test interrupted by user")
            break
        
        print("   ✅ Test complete\n")
    
    print("🏁 Wind noise amplitude tests completed!")
    print("\nWind Noise Enhancement:")
    print("• Wind amplitude doubled from 0.15 to 0.30")
    print("• Should be clearly audible when engine is off")
    print("• Scales with airspeed (10 kts = quiet, 100 kts = loud)")
    print("• Multi-band frequency generation for realistic wind sound")
    
    pygame.quit()

if __name__ == "__main__":
    main()
