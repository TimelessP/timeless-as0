#!/usr/bin/env python3
"""
Test script for sound engine fixes:
1. Main menu pause/resume functionality
2. Improved wind noise generation
3. Phase continuity fixes for smoother audio
"""
import pygame
import time
from core_simulator import get_simulator
from sound import AirshipSoundEngine

def test_menu_pause_resume():
    """Test that main menu properly pauses and resumes sound"""
    print("🔇 Testing Main Menu Pause/Resume")
    print("=" * 40)
    
    pygame.init()
    
    # Create simulator and sound engine
    simulator = get_simulator()
    simulator.start_new_game()  # Start game
    sound_engine = AirshipSoundEngine(simulator)
    
    print("✅ Game started - should have sound")
    
    # Test initial state (game running)
    info = sound_engine.get_audio_info()
    buffer = sound_engine.generate_audio_buffer(0.1)
    has_sound = (buffer != 0).any()
    
    print(f"   Game running: {simulator.running}")
    print(f"   Engine running: {info['engine_running']}")
    print(f"   Simulation paused: {info['simulation_paused']}")
    print(f"   Has sound: {has_sound}")
    print(f"   Expected: Sound ON")
    
    # Simulate returning to main menu (pause)
    print("\n🔇 Simulating return to main menu...")
    simulator.pause_simulation()
    
    info = sound_engine.get_audio_info()
    buffer = sound_engine.generate_audio_buffer(0.1)
    has_sound = (buffer != 0).any()
    
    print(f"   Game running: {simulator.running}")
    print(f"   Engine running: {info['engine_running']}")
    print(f"   Simulation paused: {info['simulation_paused']}")
    print(f"   Has sound: {has_sound}")
    print(f"   Expected: Sound OFF (paused)")
    
    # Simulate resuming game
    print("\n🔊 Simulating resume game...")
    simulator.resume_simulation()
    
    info = sound_engine.get_audio_info()
    buffer = sound_engine.generate_audio_buffer(0.1)
    has_sound = (buffer != 0).any()
    
    print(f"   Game running: {simulator.running}")
    print(f"   Engine running: {info['engine_running']}")
    print(f"   Simulation paused: {info['simulation_paused']}")
    print(f"   Has sound: {has_sound}")
    print(f"   Expected: Sound ON (resumed)")
    
    pygame.quit()
    print("✅ Main menu pause/resume test complete\n")

def test_wind_noise():
    """Test the improved wind noise generation"""
    print("💨 Testing Improved Wind Noise")
    print("=" * 40)
    
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    sound_engine = AirshipSoundEngine(simulator)
    
    # Test at different airspeeds
    test_speeds = [0, 30, 60, 90, 120]  # knots
    
    for speed in test_speeds:
        print(f"\n   Testing at {speed} knots:")
        
        # Set airspeed in simulator
        simulator.game_state["navigation"]["motion"]["indicatedAirspeed"] = speed
        
        # Generate wind noise sample
        wind_samples = sound_engine.generate_wind_noise(0.1)  # 100ms sample
        has_wind = (wind_samples != 0).any()
        max_amplitude = max(abs(wind_samples)) if has_wind else 0.0
        
        print(f"     Wind present: {has_wind}")
        print(f"     Max amplitude: {max_amplitude:.4f}")
        
        if speed <= 1:
            print(f"     Expected: No wind (below threshold)")
        else:
            print(f"     Expected: Wind sound (multi-band turbulence)")
    
    pygame.quit()
    print("✅ Wind noise test complete\n")

def test_phase_continuity():
    """Test that audio phase continuity eliminates popping"""
    print("🎵 Testing Phase Continuity (Anti-Pop)")
    print("=" * 40)
    
    pygame.init()
    
    simulator = get_simulator()
    simulator.start_new_game()
    sound_engine = AirshipSoundEngine(simulator)
    
    # Set a specific RPM for consistent testing
    simulator.game_state["engine"]["rpm"] = 2400
    print(f"   Testing at 2400 RPM")
    
    # Generate multiple consecutive buffers
    num_buffers = 5
    buffer_duration = 0.02  # 20ms buffers (shorter for more frequent transitions)
    
    print(f"   Generating {num_buffers} consecutive {buffer_duration*1000:.0f}ms buffers...")
    
    all_samples = []
    for i in range(num_buffers):
        # Generate propeller wave
        prop_buffer = sound_engine.generate_propeller_wave(buffer_duration)
        
        # Generate engine wave  
        engine_buffer = sound_engine.generate_engine_wave(buffer_duration)
        
        # Check for discontinuities at buffer boundaries
        if i > 0:
            # Check if the start of this buffer is similar to end of previous buffer
            prev_end = all_samples[-1][-5:]  # Last 5 samples of previous buffer
            curr_start = prop_buffer[:5]     # First 5 samples of current buffer
            
            # Calculate maximum jump between buffers
            max_jump = max(abs(curr_start[0] - prev_end[-1]) for _ in range(1))
            
            print(f"     Buffer {i}: Max discontinuity = {max_jump:.6f}")
            
            # Large jumps indicate popping issues
            if max_jump > 0.1:
                print(f"     ⚠️  Potential pop detected (jump > 0.1)")
            else:
                print(f"     ✅ Smooth transition")
        
        all_samples.append(prop_buffer)
    
    # Test engine firing continuity
    print(f"\n   Testing engine firing phase continuity...")
    
    # Reset and test engine waves
    sound_engine.engine_phase = 0.0
    engine_samples = []
    
    for i in range(3):
        engine_buffer = sound_engine.generate_engine_wave(buffer_duration)
        engine_samples.append(engine_buffer)
        
        # Check phase tracking
        print(f"     Buffer {i+1}: Engine phase = {sound_engine.engine_phase:.4f}")
    
    pygame.quit()
    print("✅ Phase continuity test complete\n")

def main():
    """Run all audio improvement tests"""
    print("🎵 Testing Sound Engine Improvements")
    print("=" * 50)
    
    try:
        # Test 1: Main menu pause/resume
        test_menu_pause_resume()
        
        # Test 2: Improved wind noise
        test_wind_noise()
        
        # Test 3: Phase continuity
        test_phase_continuity()
        
        print("🏁 All sound improvement tests complete!")
        print("\nImprovements tested:")
        print("✅ Main menu pause/resume functionality")
        print("✅ Multi-band wind noise generation")
        print("✅ Phase continuity for smooth audio transitions")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
