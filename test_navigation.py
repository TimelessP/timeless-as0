#!/usr/bin/env python3
"""
Test the circular navigation system to ensure all scenes link correctly
"""

def test_circular_navigation():
    """Test that all scenes have the correct circular navigation setup"""
    
    # Expected circular order
    scene_order = [
        "scene_bridge",
        "scene_engine_room", 
        "scene_navigation",
        "scene_fuel",
        "scene_cargo",
        "scene_communications",
        "scene_camera",
        "scene_crew",
        "scene_missions"
    ]
    
    # Import all scenes
    from scene_bridge import BridgeScene
    from scene_engine_room import EngineRoomScene
    from scene_navigation import NavigationScene
    from scene_fuel import FuelScene
    from scene_cargo import CargoScene
    from scene_communications import CommunicationsScene
    from scene_camera import CameraScene
    from scene_crew import CrewScene
    from scene_missions import MissionsScene
    
    # Mock simulator
    class MockSimulator:
        def get_state(self):
            return {
                "navigation": {"motion": {"pitch": 0, "roll": 0}},
                "engine": {"running": True},
                "engines": {"fuel": {"tanks": [], "balance": {}}}
            }
    
    mock_sim = MockSimulator()
    
    # Create scene instances
    scenes = {
        "scene_bridge": BridgeScene(mock_sim),
        "scene_engine_room": EngineRoomScene(mock_sim),
        "scene_navigation": NavigationScene(mock_sim),
        "scene_fuel": FuelScene(mock_sim),
        "scene_cargo": CargoScene(mock_sim),
        "scene_communications": CommunicationsScene(mock_sim),
        "scene_camera": CameraScene(mock_sim),
        "scene_crew": CrewScene(mock_sim),
        "scene_missions": MissionsScene(mock_sim)
    }
    
    print("Testing circular navigation links...")
    
    all_correct = True
    
    for i, current_scene_name in enumerate(scene_order):
        scene = scenes[current_scene_name]
        
        # Calculate expected prev and next
        prev_index = (i - 1) % len(scene_order)
        next_index = (i + 1) % len(scene_order)
        expected_prev = scene_order[prev_index]
        expected_next = scene_order[next_index]
        
        # Get actual prev and next
        actual_prev = scene._get_prev_scene()
        actual_next = scene._get_next_scene()
        
        # Check if they match
        prev_correct = actual_prev == expected_prev
        next_correct = actual_next == expected_next
        
        status_prev = "✓" if prev_correct else "❌"
        status_next = "✓" if next_correct else "❌"
        
        print(f"{current_scene_name}:")
        print(f"  {status_prev} prev: {actual_prev} (expected: {expected_prev})")
        print(f"  {status_next} next: {actual_next} (expected: {expected_next})")
        
        if not (prev_correct and next_correct):
            all_correct = False
    
    if all_correct:
        print("\n🎯 All navigation links are correct! 🎉")
        return True
    else:
        print("\n💥 Some navigation links are incorrect.")
        return False

def test_navigation_buttons():
    """Test that all scenes have the standardized navigation buttons"""
    
    # Import all scenes
    from scene_bridge import BridgeScene
    from scene_engine_room import EngineRoomScene
    from scene_navigation import NavigationScene
    from scene_fuel import FuelScene
    from scene_cargo import CargoScene
    from scene_communications import CommunicationsScene
    from scene_camera import CameraScene
    from scene_crew import CrewScene
    from scene_missions import MissionsScene
    
    # Mock simulator
    class MockSimulator:
        def get_state(self):
            return {
                "navigation": {"motion": {"pitch": 0, "roll": 0}},
                "engine": {"running": True},
                "engines": {"fuel": {"tanks": [], "balance": {}}}
            }
    
    mock_sim = MockSimulator()
    
    scenes = [
        ("Bridge", BridgeScene(mock_sim)),
        ("Engine Room", EngineRoomScene(mock_sim)),
        ("Navigation", NavigationScene(mock_sim)),
        ("Fuel", FuelScene(mock_sim)),
        ("Cargo", CargoScene(mock_sim)),
        ("Communications", CommunicationsScene(mock_sim)),
        ("Camera", CameraScene(mock_sim)),
        ("Crew", CrewScene(mock_sim)),
        ("Missions", MissionsScene(mock_sim))
    ]
    
    print("\nTesting navigation button standardization...")
    
    all_correct = True
    
    for scene_name, scene in scenes:
        # Find prev_scene and next_scene buttons
        prev_button = None
        next_button = None
        
        for widget in scene.widgets:
            if widget["id"] == "prev_scene":
                prev_button = widget
            elif widget["id"] == "next_scene":
                next_button = widget
        
        # Check if buttons exist
        if prev_button is None:
            print(f"❌ {scene_name}: Missing prev_scene button")
            all_correct = False
            continue
            
        if next_button is None:
            print(f"❌ {scene_name}: Missing next_scene button")
            all_correct = False
            continue
        
        # Check button properties
        prev_correct = (
            prev_button["position"] == [8, 290] and
            prev_button["size"] == [60, 24] and
            prev_button["text"] == "< ["
        )
        
        next_correct = (
            next_button["position"] == [252, 290] and
            next_button["size"] == [60, 24] and
            next_button["text"] == "] >"
        )
        
        if prev_correct and next_correct:
            print(f"✓ {scene_name}: Navigation buttons correct")
        else:
            print(f"❌ {scene_name}: Navigation buttons incorrect")
            if not prev_correct:
                print(f"    prev_scene: pos={prev_button['position']}, size={prev_button['size']}, text='{prev_button['text']}'")
            if not next_correct:
                print(f"    next_scene: pos={next_button['position']}, size={next_button['size']}, text='{next_button['text']}'")
            all_correct = False
    
    if all_correct:
        print("\n🎯 All navigation buttons are standardized! 🎉")
        return True
    else:
        print("\n💥 Some navigation buttons need fixing.")
        return False

if __name__ == "__main__":
    import sys
    
    success = True
    success &= test_circular_navigation()
    success &= test_navigation_buttons()
    
    if success:
        print("\n🚁 Navigation system is perfect! Ready for flight! ✈️")
        sys.exit(0)
    else:
        print("\n🔧 Navigation system needs adjustments.")
        sys.exit(1)
