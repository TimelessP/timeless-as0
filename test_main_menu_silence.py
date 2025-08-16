#!/usr/bin/env python3
"""
Test script for initial main menu sound behavior
Testing that no sounds play when first starting the application
"""

import pygame
import numpy as np
import time
from core_simulator import get_simulator
from sound import AirshipSoundEngine

def main():
    print("🔇 Testing Initial Main Menu Silence")
    print("=" * 50)
    
    # Initialize pygame (required for audio)
    pygame.init()
    
    # Create simulator in initial state (no game started)
    simulator = get_simulator()
    # DO NOT call start_new_game() - simulate fresh app startup
    
    print(f"Simulator initial state:")
    print(f"  simulator.running = {simulator.running}")
    
    game_state = simulator.get_state()
    print(f"  gameInfo.paused = {game_state.get('gameInfo', {}).get('paused', 'MISSING')}")
    print(f"  engine.running = {game_state.get('engine', {}).get('running', 'MISSING')}")
    print(f"  airspeed = {game_state.get('navigation', {}).get('motion', {}).get('indicatedAirspeed', 'MISSING')}")
    
    # Initialize sound engine
    sound_engine = AirshipSoundEngine(simulator)
    
    print("\n🎵 Testing initial main menu audio generation...")
    
    # Generate audio buffer to check what sounds are produced in initial state
    test_buffer = sound_engine.generate_audio_buffer(1.0)  # 1 second test buffer
    
    # Analyze the audio content
    max_amplitude = np.max(np.abs(test_buffer))
    rms_amplitude = np.sqrt(np.mean(test_buffer**2))
    
    print(f"Initial state audio analysis:")
    print(f"  Max amplitude: {max_amplitude:.6f}")
    print(f"  RMS amplitude: {rms_amplitude:.6f}")
    
    if max_amplitude < 0.00001:
        print("  ✅ Result: Complete silence (CORRECT)")
        result_correct = True
    else:
        print("  ❌ Result: Audio detected (INCORRECT - should be silent)")
        result_correct = False
    
    print("\n🎮 Now testing after starting a new game...")
    
    # Start a new game
    simulator.start_new_game()
    print(f"After start_new_game():")
    print(f"  simulator.running = {simulator.running}")
    
    game_state = simulator.get_state()
    print(f"  gameInfo.paused = {game_state.get('gameInfo', {}).get('paused', 'MISSING')}")
    print(f"  engine.running = {game_state.get('engine', {}).get('running', 'MISSING')}")
    print(f"  airspeed = {game_state.get('navigation', {}).get('motion', {}).get('indicatedAirspeed', 'MISSING')}")
    
    # Generate audio after game started
    test_buffer_game = sound_engine.generate_audio_buffer(1.0)
    max_amplitude_game = np.max(np.abs(test_buffer_game))
    rms_amplitude_game = np.sqrt(np.mean(test_buffer_game**2))
    
    print(f"Game running audio analysis:")
    print(f"  Max amplitude: {max_amplitude_game:.6f}")
    print(f"  RMS amplitude: {rms_amplitude_game:.6f}")
    
    if max_amplitude_game > 0.01:
        print("  ✅ Result: Audio playing (CORRECT)")
        game_result_correct = True
    else:
        print("  ❌ Result: No audio (INCORRECT - should have engine/wind sounds)")
        game_result_correct = False
    
    print("\n🔇 Testing pause simulation...")
    
    # Pause the simulation (like returning to main menu)
    simulator.pause_simulation()
    print(f"After pause_simulation():")
    print(f"  simulator.running = {simulator.running}")
    
    game_state = simulator.get_state()
    print(f"  gameInfo.paused = {game_state.get('gameInfo', {}).get('paused', 'MISSING')}")
    
    # Generate audio after pause
    test_buffer_paused = sound_engine.generate_audio_buffer(1.0)
    max_amplitude_paused = np.max(np.abs(test_buffer_paused))
    rms_amplitude_paused = np.sqrt(np.mean(test_buffer_paused**2))
    
    print(f"Paused state audio analysis:")
    print(f"  Max amplitude: {max_amplitude_paused:.6f}")
    print(f"  RMS amplitude: {rms_amplitude_paused:.6f}")
    
    if max_amplitude_paused < 0.00001:
        print("  ✅ Result: Complete silence (CORRECT)")
        pause_result_correct = True
    else:
        print("  ❌ Result: Audio detected (INCORRECT - should be silent when paused)")
        pause_result_correct = False
    
    print("\n🏁 Main Menu Sound Test Results:")
    print(f"  Initial main menu silence: {'✅ PASS' if result_correct else '❌ FAIL'}")
    print(f"  Game running audio: {'✅ PASS' if game_result_correct else '❌ FAIL'}")
    print(f"  Paused state silence: {'✅ PASS' if pause_result_correct else '❌ FAIL'}")
    
    if result_correct and game_result_correct and pause_result_correct:
        print("\n🎉 All tests PASSED! Main menu sound behavior is correct.")
    else:
        print("\n⚠️  Some tests FAILED. Check the logic above.")
    
    pygame.quit()

if __name__ == "__main__":
    main()
