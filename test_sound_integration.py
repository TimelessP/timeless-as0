#!/usr/bin/env python3
"""
Test script for sound engine integration with main application
Tests pause states, engine states, and volume control
"""
import pygame
import time
from core_simulator import get_simulator
from sound import AirshipSoundEngine

def test_sound_integration():
    """Test the integrated sound engine with various game states"""
    print("🎵 Testing Sound Engine Integration")
    print("=" * 50)
    
    # Initialize pygame (required for audio)
    pygame.init()
    
    # Create simulator and sound engine
    simulator = get_simulator()
    simulator.start_new_game()
    sound_engine = AirshipSoundEngine(simulator)
    
    print("✅ Sound engine and simulator initialized")
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Normal Operation (Engine Running)",
            "setup": lambda: None,  # Default state has engine running
            "duration": 2.0,
            "expected_sound": True
        },
        {
            "name": "Simulation Paused",
            "setup": lambda: simulator.pause_simulation(),
            "teardown": lambda: simulator.resume_simulation(),
            "duration": 2.0,
            "expected_sound": False
        },
        {
            "name": "Engine Turned Off",
            "setup": lambda: simulator.game_state["engine"].update({"running": False}),
            "teardown": lambda: simulator.game_state["engine"].update({"running": True}),
            "duration": 2.0,
            "expected_sound": False
        },
        {
            "name": "Volume Set to Zero",
            "setup": lambda: simulator.game_state["settings"].update({"soundVolume": 0.0}),
            "teardown": lambda: simulator.game_state["settings"].update({"soundVolume": 0.5}),
            "duration": 2.0,
            "expected_sound": False
        },
        {
            "name": "Low Volume (25%)",
            "setup": lambda: simulator.game_state["settings"].update({"soundVolume": 0.25}),
            "teardown": lambda: simulator.game_state["settings"].update({"soundVolume": 0.5}),
            "duration": 2.0,
            "expected_sound": True
        },
        {
            "name": "High Volume (100%)",
            "setup": lambda: simulator.game_state["settings"].update({"soundVolume": 1.0}),
            "teardown": lambda: simulator.game_state["settings"].update({"soundVolume": 0.5}),
            "duration": 2.0,
            "expected_sound": True
        }
    ]
    
    try:
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🔊 Test {i}/{len(test_scenarios)}: {scenario['name']}")
            
            # Setup scenario
            if "setup" in scenario:
                scenario["setup"]()
            
            # Generate test audio buffer and get info
            audio_info = sound_engine.get_audio_info()
            buffer_duration = sound_engine.buffer_size / sound_engine.sample_rate
            test_buffer = sound_engine.generate_audio_buffer(buffer_duration)
            
            # Check if buffer has sound
            has_sound = (test_buffer != 0).any()
            
            print(f"   Engine Running: {audio_info['engine_running']}")
            print(f"   Simulation Paused: {audio_info['simulation_paused']}")
            print(f"   Volume: {audio_info['volume']:.1%}")
            print(f"   RPM: {audio_info['current_rpm']:.0f}")
            print(f"   Buffer has sound: {has_sound}")
            print(f"   Expected sound: {scenario['expected_sound']}")
            
            # Verify expectation
            if has_sound == scenario['expected_sound']:
                print(f"   ✅ PASS - Sound state matches expectation")
            else:
                print(f"   ❌ FAIL - Expected {scenario['expected_sound']}, got {has_sound}")
            
            # Run audio for test duration
            print(f"   Playing for {scenario['duration']:.1f} seconds...")
            start_time = time.time()
            end_time = start_time + scenario['duration']
            
            while time.time() < end_time:
                sound_engine.update_audio()
                time.sleep(0.05)  # 50ms update interval
            
            # Teardown scenario
            if "teardown" in scenario:
                scenario["teardown"]()
            
            print(f"   ✅ Test complete")
            
            if i < len(test_scenarios):
                time.sleep(0.5)  # Brief pause between tests
        
        print(f"\n🔧 Testing volume control from settings...")
        
        # Test that volume changes are picked up from game settings
        original_volume = simulator.game_state["settings"]["soundVolume"]
        test_volumes = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for vol in test_volumes:
            simulator.game_state["settings"]["soundVolume"] = vol
            audio_info = sound_engine.get_audio_info()
            print(f"   Settings volume: {vol:.2f} → Audio engine volume: {audio_info['volume']:.2f}")
            
            if abs(audio_info['volume'] - vol) < 0.01:
                print(f"     ✅ Volume sync correct")
            else:
                print(f"     ❌ Volume sync failed")
        
        # Restore original volume
        simulator.game_state["settings"]["soundVolume"] = original_volume
        
        print(f"\n🔧 Testing save/load with sound settings...")
        
        # Test that sound volume survives save/load cycle
        simulator.game_state["settings"]["soundVolume"] = 0.8
        save_success = simulator.save_game("test_sound_settings.json")
        print(f"   Save with volume 0.8: {'✅ Success' if save_success else '❌ Failed'}")
        
        if save_success:
            # Create new simulator and load
            test_simulator = get_simulator()
            load_success = test_simulator.load_game("test_sound_settings.json")
            print(f"   Load test: {'✅ Success' if load_success else '❌ Failed'}")
            
            if load_success:
                loaded_volume = test_simulator.game_state["settings"]["soundVolume"]
                print(f"   Loaded volume: {loaded_volume:.2f}")
                
                if abs(loaded_volume - 0.8) < 0.01:
                    print(f"   ✅ Volume setting persisted correctly")
                else:
                    print(f"   ❌ Volume setting not persisted correctly")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.mixer.quit()
        pygame.quit()
        print("\n🏁 Sound integration test complete")

if __name__ == "__main__":
    test_sound_integration()
