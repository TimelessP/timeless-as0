#!/usr/bin/env python3
"""
Audio Track Reference Guide
Quick reference for all available audio tracks and testing modes
"""

def print_track_reference():
    print("🎵 Audio Track Reference Guide")
    print("=" * 50)
    
    print("\n📊 AVAILABLE AUDIO TRACKS:")
    print("-" * 30)
    
    print("🚁 PROPELLER TRACKS:")
    print("   propeller_blade1      - First blade pressure wave")
    print("   propeller_blade2      - Second blade pressure wave (180° offset)")
    print("   propeller_harmonics   - Blade tip harmonic effects")
    
    print("\n🔥 ENGINE COMBUSTION TRACKS:")
    print("   engine_cylinder0      - Cylinder 0 discrete combustion events")
    print("   engine_cylinder1      - Cylinder 1 discrete combustion events")
    print("   engine_cylinder2      - Cylinder 2 discrete combustion events")
    print("   engine_cylinder3      - Cylinder 3 discrete combustion events")
    print("   engine_cylinder4      - Cylinder 4 discrete combustion events")
    print("   engine_cylinder5      - Cylinder 5 discrete combustion events")
    
    print("\n🔊 ENGINE RUMBLE TRACKS:")
    print("   engine_rumble_fundamental  - Engine block vibration (fundamental)")
    print("   engine_rumble_harmonic     - Engine block vibration (1.5× harmonic)")
    
    print("\n💨 WIND NOISE TRACKS:")
    print("   wind_low_freq         - Low frequency hull vibration (20-50 Hz)")
    print("   wind_low_harmonic1    - Low frequency harmonic 1 (1.33×)")
    print("   wind_low_harmonic2    - Low frequency harmonic 2 (1.77×)")
    print("   wind_mid_freq         - Mid frequency turbulence (200-600 Hz)")
    print("   wind_mid_harmonic1    - Mid frequency harmonic 1 (1.41×)")
    print("   wind_mid_harmonic2    - Mid frequency harmonic 2 (2.13×)")
    print("   wind_high_freq        - High frequency rigging noise (1-3 kHz)")
    print("   wind_gusting          - Gusting modulation effect")
    
    print("\n🎛️  TRACK GROUPS:")
    print("-" * 20)
    print("   propeller            - All propeller tracks")
    print("   engine_cylinders     - All cylinder combustion tracks")
    print("   engine_rumble        - All engine rumble tracks")
    print("   wind                 - All wind noise tracks")
    
    print("\n🧪 TESTING MODES:")
    print("-" * 20)
    print("   python test_audio_tracks.py                 - Quick artifact test")
    print("   python test_audio_tracks.py interactive     - Interactive control")
    print("   python test_audio_tracks.py groups          - Test track groups")
    print("   python test_audio_tracks.py cylinders       - Test each cylinder")
    print("   python test_audio_tracks.py propeller       - Test propeller parts")
    print("   python test_audio_tracks.py wind            - Test wind components")
    print("   python test_audio_tracks.py all             - Test all tracks")
    
    print("\n🔍 ARTIFACT DETECTION PRIORITY:")
    print("-" * 35)
    print("   HIGH RISK:   engine_cylinder* tracks (discrete events)")
    print("   MEDIUM RISK: engine_rumble_* tracks (continuous tones)")
    print("   LOW RISK:    propeller_* tracks (continuous, tested clean)")
    print("   LOW RISK:    wind_* tracks (continuous, tested clean)")
    
    print("\n💡 USAGE EXAMPLES:")
    print("-" * 20)
    print("   # Test only cylinder 0")
    print("   python test_audio_tracks.py interactive")
    print("   > solo engine_cylinder0")
    print("   > play 5")
    print()
    print("   # Test all cylinders except cylinder 3")
    print("   python test_audio_tracks.py interactive")
    print("   > group engine_cylinders")
    print("   > disable engine_cylinder3")
    print("   > play 5")
    print()
    print("   # Test with reduced volume")
    print("   # (Note: Volume control requires code modification)")
    print("   sound_engine.set_track_volume('engine_cylinder0', 0.5)")

if __name__ == "__main__":
    print_track_reference()
