#!/usr/bin/env python3
"""
Audio Track Isolation Test
Test individual audio tracks to identify artifact sources
"""

import pygame
import time
import sys
from core_simulator import get_simulator
import sound

def test_individual_track(sound_engine, track_name, duration=3.0):
    """Test a single audio track in isolation"""
    print(f"🎵 Testing: {track_name}")
    
    # Disable all tracks, then enable only the target track
    sound_engine.disable_all_tracks()
    sound_engine.set_track_enabled(track_name, True)
    
    # Run the audio for specified duration
    start_time = time.time()
    end_time = start_time + duration
    
    print(f"   Playing {track_name} for {duration:.1f} seconds...")
    
    while time.time() < end_time:
        sound_engine.update_audio()
        time.sleep(0.05)  # 50ms update interval
    
    print(f"   ✅ {track_name} complete\n")

def test_track_group(sound_engine, group_name, duration=3.0):
    """Test a group of related audio tracks"""
    print(f"🎵 Testing Group: {group_name}")
    
    # Disable all tracks, then enable the target group
    sound_engine.disable_all_tracks()
    sound_engine.set_track_group_enabled(group_name, True)
    
    # List which tracks are enabled
    enabled_tracks = []
    for track, controls in sound_engine.get_track_info().items():
        if controls["enabled"]:
            enabled_tracks.append(track)
    
    print(f"   Enabled tracks: {', '.join(enabled_tracks)}")
    
    # Run the audio for specified duration
    start_time = time.time()
    end_time = start_time + duration
    
    print(f"   Playing {group_name} group for {duration:.1f} seconds...")
    
    while time.time() < end_time:
        sound_engine.update_audio()
        time.sleep(0.05)  # 50ms update interval
    
    print(f"   ✅ {group_name} group complete\n")

def interactive_track_test(sound_engine):
    """Interactive mode for testing tracks"""
    print("🎛️  Interactive Track Testing Mode")
    print("=" * 50)
    print("Commands:")
    print("  list - Show all available tracks")
    print("  enable <track> - Enable a specific track")
    print("  disable <track> - Disable a specific track")
    print("  solo <track> - Play only the specified track")
    print("  group <group> - Play only the specified group")
    print("  all - Enable all tracks")
    print("  none - Disable all tracks")
    print("  play <seconds> - Play current configuration")
    print("  status - Show current track status")
    print("  quit - Exit interactive mode")
    print()
    
    while True:
        try:
            cmd = input("🎵 > ").strip().lower()
            
            if cmd == "quit" or cmd == "exit":
                break
            elif cmd == "list":
                tracks = sound_engine.get_track_list()
                print("Available tracks:")
                for track in tracks:
                    status = "✅" if sound_engine.track_controls[track]["enabled"] else "❌"
                    volume = sound_engine.track_controls[track]["volume"]
                    print(f"  {status} {track} (vol: {volume:.2f})")
            elif cmd == "all":
                sound_engine.enable_all_tracks()
                print("✅ All tracks enabled")
            elif cmd == "none":
                sound_engine.disable_all_tracks()
                print("❌ All tracks disabled")
            elif cmd == "status":
                enabled_tracks = []
                disabled_tracks = []
                for track, controls in sound_engine.get_track_info().items():
                    if controls["enabled"]:
                        enabled_tracks.append(f"{track} (vol: {controls['volume']:.2f})")
                    else:
                        disabled_tracks.append(track)
                
                print(f"✅ Enabled ({len(enabled_tracks)}): {', '.join(enabled_tracks) if enabled_tracks else 'None'}")
                print(f"❌ Disabled ({len(disabled_tracks)}): {', '.join(disabled_tracks) if disabled_tracks else 'None'}")
            elif cmd.startswith("enable "):
                track = cmd[7:]
                sound_engine.set_track_enabled(track, True)
                print(f"✅ Enabled {track}")
            elif cmd.startswith("disable "):
                track = cmd[8:]
                sound_engine.set_track_enabled(track, False)
                print(f"❌ Disabled {track}")
            elif cmd.startswith("solo "):
                track = cmd[5:]
                sound_engine.disable_all_tracks()
                sound_engine.set_track_enabled(track, True)
                print(f"🎵 Solo mode: {track}")
            elif cmd.startswith("group "):
                group = cmd[6:]
                sound_engine.disable_all_tracks()
                sound_engine.set_track_group_enabled(group, True)
                print(f"🎵 Group mode: {group}")
            elif cmd.startswith("play "):
                try:
                    duration = float(cmd[5:])
                    print(f"🎵 Playing current configuration for {duration:.1f} seconds...")
                    start_time = time.time()
                    end_time = start_time + duration
                    while time.time() < end_time:
                        sound_engine.update_audio()
                        time.sleep(0.05)
                    print("✅ Playback complete")
                except ValueError:
                    print("❌ Invalid duration. Use: play <seconds>")
            else:
                print("❌ Unknown command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            print("\n🛑 Interactive mode interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Test individual audio tracks to isolate artifact sources"""
    print("🔍 Audio Track Isolation Test")
    print("=" * 40)
    
    # Initialize pygame and sound engine
    pygame.init()
    
    # Create test simulator with engine running
    simulator = get_simulator()
    simulator.start_new_game()
    simulator.running = True
    simulator.game_state['engine']['running'] = True
    
    # Initialize sound engine
    sound_engine = sound.AirshipSoundEngine(simulator)
    
    # Set engine to cruise flight conditions
    engine_state = simulator.game_state["engine"]
    engine_state["rpm"] = 2400
    engine_state["controls"]["throttle"] = 0.75
    engine_state["controls"]["mixture"] = 0.85
    engine_state["controls"]["propeller"] = 0.8
    
    navigation_state = simulator.game_state["navigation"]
    navigation_state["motion"]["indicatedAirspeed"] = 85
    
    sound_engine.update_from_simulator()
    
    print(f"Test Configuration:")
    print(f"   RPM: {sound_engine.current_rpm}")
    print(f"   Mixture: {sound_engine.current_mixture:.2f}")
    print(f"   Pitch: {sound_engine.current_pitch:.2f}")
    print(f"   Airspeed: {sound_engine.current_airspeed:.1f} knots")
    print()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "interactive" or mode == "i":
            interactive_track_test(sound_engine)
            
        elif mode == "groups":
            print("🎵 Testing Track Groups")
            print("=" * 25)
            test_track_group(sound_engine, "propeller", 4.0)
            test_track_group(sound_engine, "engine_cylinders", 4.0)
            test_track_group(sound_engine, "engine_rumble", 4.0)
            test_track_group(sound_engine, "wind", 4.0)
            
        elif mode == "cylinders":
            print("🎵 Testing Individual Cylinders")
            print("=" * 35)
            for i in range(6):
                test_individual_track(sound_engine, f"engine_cylinder{i}", 3.0)
                
        elif mode == "propeller":
            print("🎵 Testing Propeller Components")
            print("=" * 35)
            test_individual_track(sound_engine, "propeller_blade1", 3.0)
            test_individual_track(sound_engine, "propeller_blade2", 3.0)
            test_individual_track(sound_engine, "propeller_harmonics", 3.0)
            
        elif mode == "wind":
            print("🎵 Testing Wind Components")
            print("=" * 30)
            test_individual_track(sound_engine, "wind_low_freq", 3.0)
            test_individual_track(sound_engine, "wind_mid_freq", 3.0)
            test_individual_track(sound_engine, "wind_high_freq", 3.0)
            
        elif mode == "all":
            print("🎵 Testing All Individual Tracks")
            print("=" * 35)
            for track in sound_engine.get_track_list():
                test_individual_track(sound_engine, track, 2.0)
                
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Available modes: interactive, groups, cylinders, propeller, wind, all")
            
    else:
        # Default: Test problematic tracks first
        print("🎵 Quick Artifact Detection Test")
        print("=" * 35)
        print("Testing most likely artifact sources...")
        print()
        
        # Test engine cylinders (most likely culprits)
        print("🔥 Engine Cylinders (High Risk)")
        test_individual_track(sound_engine, "engine_cylinder0", 3.0)
        test_individual_track(sound_engine, "engine_cylinder1", 3.0)
        
        # Test rumble components
        print("🔊 Engine Rumble")
        test_individual_track(sound_engine, "engine_rumble_fundamental", 3.0)
        test_individual_track(sound_engine, "engine_rumble_harmonic", 3.0)
        
        # Test all cylinders together
        print("🔥 All Cylinders Combined")
        test_track_group(sound_engine, "engine_cylinders", 4.0)
        
        print("🎯 Quick test complete!")
        print("\nFor more detailed testing, run:")
        print("  python test_audio_tracks.py interactive")
        print("  python test_audio_tracks.py groups")
        print("  python test_audio_tracks.py all")
    
    # Cleanup
    pygame.mixer.quit()
    pygame.quit()
    print("\n🏁 Audio track test complete")

if __name__ == "__main__":
    main()
