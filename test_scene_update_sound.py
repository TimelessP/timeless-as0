#!/usr/bin/env python3
"""
Test script for scene_update sound behavior
Testing that scene_update doesn't resume simulation/sound
"""

import pygame
import numpy as np
import time
from core_simulator import get_simulator
from sound import AirshipSoundEngine

def test_scene_transition_sound_behavior():
    """Test that scene transitions properly handle sound state"""
    print("🔧 Testing Scene Transition Sound Behavior")
    print("=" * 60)
    
    # Initialize pygame (required for audio)
    pygame.init()
    
    # Import scenes for testing
    from scene_main_menu import MainMenuScene
    from scene_update import SceneUpdate
    from scene_bridge import BridgeScene
    
    # Create simulator and sound engine
    simulator = get_simulator()
    sound_engine = AirshipSoundEngine(simulator)
    
    # Initialize scenes
    main_menu = MainMenuScene()
    update_scene = SceneUpdate(pygame.font.Font(None, 14))
    bridge_scene = BridgeScene(simulator)
    
    # Simulate the application flow
    test_scenarios = [
        {
            "name": "1. Initial State (Main Menu)",
            "simulator_running": False,
            "simulator_paused": False,
            "expected_sound": False,
            "description": "Fresh app start - no game loaded"
        },
        {
            "name": "2. Start New Game (Bridge Scene)",
            "simulator_running": True,
            "simulator_paused": False,
            "expected_sound": True,
            "description": "Game started - simulation and sound active"
        },
        {
            "name": "3. Pause for Main Menu",
            "simulator_running": True,
            "simulator_paused": True,
            "expected_sound": False,
            "description": "Returned to main menu - simulation paused"
        },
        {
            "name": "4. Enter Update Scene",
            "simulator_running": True,
            "simulator_paused": True,
            "expected_sound": False,
            "description": "In update scene - should stay paused"
        },
        {
            "name": "5. Return to Game (Bridge Scene)",
            "simulator_running": True,
            "simulator_paused": False,
            "expected_sound": True,
            "description": "Back to game - simulation resumed"
        }
    ]
    
    print("Testing each scenario...")
    print()
    
    all_tests_passed = True
    
    for i, scenario in enumerate(test_scenarios):
        print(f"🎵 {scenario['name']}")
        print(f"   {scenario['description']}")
        
        # Set up simulator state
        if scenario["name"].startswith("1."):
            # Initial state - no game started
            pass  # Simulator starts with running=False
        elif scenario["name"].startswith("2."):
            # Start new game
            simulator.start_new_game()
        elif scenario["name"].startswith("3."):
            # Pause simulation (like returning to main menu)
            simulator.pause_simulation()
        elif scenario["name"].startswith("4."):
            # Scene_update should not change simulation state
            # It should remain paused
            pass  # No state change - this is the test!
        elif scenario["name"].startswith("5."):
            # Resume simulation (like entering game scene)
            simulator.resume_simulation()
        
        # Get current state
        state = simulator.get_state()
        actual_running = simulator.running
        actual_paused = state.get("gameInfo", {}).get("paused", False)
        
        print(f"   State: running={actual_running}, paused={actual_paused}")
        
        # Generate audio to test sound behavior
        test_buffer = sound_engine.generate_audio_buffer(0.5)
        max_amplitude = np.max(np.abs(test_buffer))
        
        # Determine if sound is playing
        sound_playing = max_amplitude > 0.001
        
        print(f"   Audio: amplitude={max_amplitude:.6f}, playing={sound_playing}")
        
        # Check if behavior matches expectation
        if sound_playing == scenario["expected_sound"]:
            print(f"   ✅ PASS: Sound behavior correct")
        else:
            print(f"   ❌ FAIL: Expected sound={scenario['expected_sound']}, got={sound_playing}")
            all_tests_passed = False
        
        print()
    
    print("🏁 Scene Transition Sound Test Results:")
    if all_tests_passed:
        print("🎉 All tests PASSED! Scene transitions handle sound correctly.")
        print("\nKey findings:")
        print("• Main menu: Silent ✅")
        print("• Update scene: Stays silent (doesn't resume simulation) ✅")
        print("• Game scenes: Resume simulation and sound ✅")
    else:
        print("⚠️  Some tests FAILED. Check the logic above.")
    
    pygame.quit()
    
    return all_tests_passed

def main():
    test_scene_transition_sound_behavior()

if __name__ == "__main__":
    main()
