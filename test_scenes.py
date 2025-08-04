#!/usr/bin/env python3
"""
Quick test script to verify all scenes can be imported and instantiated
"""

import sys
import traceback

def test_scene_imports():
    """Test that all scenes can be imported without errors"""
    try:
        print("Testing scene imports...")
        
        # Test bridge scene
        from scene_bridge import BridgeScene
        print("✓ Bridge scene import successful")
        
        # Test engine room scene
        from scene_engine_room import EngineRoomScene
        print("✓ Engine room scene import successful")
        
        # Test navigation scene
        from scene_navigation import NavigationScene
        print("✓ Navigation scene import successful")
        
        # Test fuel scene
        from scene_fuel import FuelScene
        print("✓ Fuel scene import successful")
        
        # Test cargo scene
        from scene_cargo import CargoScene
        print("✓ Cargo scene import successful")
        
        # Test communications scene
        from scene_communications import CommunicationsScene
        print("✓ Communications scene import successful")
        
        # Test camera scene
        from scene_camera import CameraScene
        print("✓ Camera scene import successful")
        
        # Test crew scene
        from scene_crew import CrewScene
        print("✓ Crew scene import successful")
        
        # Test missions scene
        from scene_missions import MissionsScene
        print("✓ Missions scene import successful")
        
        print("\nAll scene imports successful! 🎉")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_scene_instantiation():
    """Test that all scenes can be created"""
    try:
        print("\nTesting scene instantiation...")
        
        # Mock simulator for testing
        class MockSimulator:
            def get_state(self):
                return {
                    "navigation": {"motion": {"pitch": 0, "roll": 0}},
                    "engine": {"running": True},
                    "engines": {"fuel": {"tanks": [], "balance": {}}}
                }
        
        mock_sim = MockSimulator()
        
        # Test creating each scene
        from scene_bridge import BridgeScene
        bridge = BridgeScene(mock_sim)
        print("✓ Bridge scene creation successful")
        
        from scene_engine_room import EngineRoomScene
        engine_room = EngineRoomScene(mock_sim)
        print("✓ Engine room scene creation successful")
        
        from scene_navigation import NavigationScene
        navigation = NavigationScene(mock_sim)
        print("✓ Navigation scene creation successful")
        
        from scene_fuel import FuelScene
        fuel = FuelScene(mock_sim)
        print("✓ Fuel scene creation successful")
        
        from scene_cargo import CargoScene
        cargo = CargoScene(mock_sim)
        print("✓ Cargo scene creation successful")
        
        from scene_communications import CommunicationsScene
        comms = CommunicationsScene(mock_sim)
        print("✓ Communications scene creation successful")
        
        from scene_camera import CameraScene
        camera = CameraScene(mock_sim)
        print("✓ Camera scene creation successful")
        
        from scene_crew import CrewScene
        crew = CrewScene(mock_sim)
        print("✓ Crew scene creation successful")
        
        from scene_missions import MissionsScene
        missions = MissionsScene(mock_sim)
        print("✓ Missions scene creation successful")
        
        print("\nAll scene instantiation successful! 🎉")
        return True
        
    except Exception as e:
        print(f"❌ Instantiation error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = True
    success &= test_scene_imports()
    success &= test_scene_instantiation()
    
    if success:
        print("\n🎯 All tests passed! The scenes are ready for use.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the errors above.")
        sys.exit(1)
