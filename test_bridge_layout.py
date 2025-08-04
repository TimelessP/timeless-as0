#!/usr/bin/env python3
"""
Visual layout test for the Bridge scene to verify no overlaps
"""

def test_bridge_layout():
    """Test the bridge scene layout for overlaps"""
    
    from scene_bridge import BridgeScene
    
    # Mock simulator
    class MockSimulator:
        def get_state(self):
            return {
                "navigation": {"motion": {"pitch": 0, "roll": 0}},
                "engine": {"running": True},
                "engines": {"fuel": {"tanks": [], "balance": {}}}
            }
    
    mock_sim = MockSimulator()
    bridge = BridgeScene(mock_sim)
    
    print("Bridge Scene Widget Layout:")
    print("=" * 50)
    print("Y Position | Widget ID              | Size        | Type")
    print("-" * 50)
    
    # Sort widgets by Y position for easy overlap detection
    widgets_by_y = sorted(bridge.widgets, key=lambda w: w["position"][1])
    
    for widget in widgets_by_y:
        x, y = widget["position"]
        w, h = widget["size"]
        widget_id = widget["id"]
        widget_type = widget["type"]
        
        print(f"{y:3d}-{y+h:3d}     | {widget_id:<20} | {w:3d}x{h:<3d}   | {widget_type}")
    
    print("\nChecking for overlaps...")
    
    overlaps = []
    for i, widget1 in enumerate(widgets_by_y):
        for widget2 in widgets_by_y[i+1:]:
            x1, y1 = widget1["position"]
            w1, h1 = widget1["size"]
            x2, y2 = widget2["position"]
            w2, h2 = widget2["size"]
            
            # Check if widgets overlap
            if (x1 < x2 + w2 and x1 + w1 > x2 and 
                y1 < y2 + h2 and y1 + h1 > y2):
                overlaps.append((widget1["id"], widget2["id"]))
    
    if overlaps:
        print("❌ Found overlaps:")
        for widget1, widget2 in overlaps:
            print(f"   {widget1} overlaps with {widget2}")
        return False
    else:
        print("✅ No overlaps detected!")
        return True

def test_spacing():
    """Test spacing between UI elements"""
    
    from scene_bridge import BridgeScene
    
    # Mock simulator
    class MockSimulator:
        def get_state(self):
            return {
                "navigation": {"motion": {"pitch": 0, "roll": 0}},
                "engine": {"running": True},
                "engines": {"fuel": {"tanks": [], "balance": {}}}
            }
    
    mock_sim = MockSimulator()
    bridge = BridgeScene(mock_sim)
    
    print("\nLayout Analysis:")
    print("=" * 30)
    
    # Find different widget groups
    header_space = 24  # Header height
    
    nav_displays = [w for w in bridge.widgets if w["id"] in ["altitude", "airspeed", "heading"]]
    engine_displays = [w for w in bridge.widgets if w["id"] in ["engine_rpm", "manifold_pressure", "fuel_flow"]]
    system_buttons = [w for w in bridge.widgets if w["id"] in ["battery_status", "fuel_pumps", "autopilot"]]
    nav_controls = [w for w in bridge.widgets if w["id"] in ["nav_mode", "altitude_set", "heading_set"]]
    scene_nav = [w for w in bridge.widgets if w["id"] in ["prev_scene", "next_scene"]]
    
    print(f"Header space: 0-{header_space}")
    if nav_displays:
        y_pos = nav_displays[0]["position"][1]
        print(f"Nav displays: {y_pos}-{y_pos+16} (gap from header: {y_pos - header_space}px)")
    
    if engine_displays:
        y_pos = engine_displays[0]["position"][1]
        print(f"Engine displays: {y_pos}-{y_pos+16}")
    
    if system_buttons:
        y_pos = system_buttons[0]["position"][1]
        height = system_buttons[0]["size"][1]
        print(f"System buttons: {y_pos}-{y_pos+height}")
    
    if nav_controls:
        y_pos = nav_controls[0]["position"][1]
        height = nav_controls[0]["size"][1]
        print(f"Nav controls: {y_pos}-{y_pos+height}")
    
    if scene_nav:
        y_pos = scene_nav[0]["position"][1]
        height = scene_nav[0]["size"][1]
        print(f"Scene nav: {y_pos}-{y_pos+height}")
    
    print(f"Artificial horizon area: ~200-280")
    
    return True

if __name__ == "__main__":
    import sys
    
    success = True
    success &= test_bridge_layout()
    success &= test_spacing()
    
    if success:
        print("\n🎯 Bridge layout is clean and organized! 🚁")
        sys.exit(0)
    else:
        print("\n🔧 Bridge layout needs adjustments.")
        sys.exit(1)
