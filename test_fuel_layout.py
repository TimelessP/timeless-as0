#!/usr/bin/env python3
"""
Test script for fuel scene layout optimization
Demonstrates systematic overlap detection and resolution
"""

def test_fuel_layout():
    """Test the fuel scene layout system"""
    print("🧪 Testing Fuel Scene Layout System")
    print("=" * 50)
    
    try:
        from scene_fuel import FuelScene
        from core_simulator import get_simulator
        
        # Create scene instance
        simulator = get_simulator()
        scene = FuelScene(simulator)
        
        print("✅ Fuel scene initialized successfully")
        
        # Test overlap detection
        overlaps = scene.check_layout_overlaps()
        if overlaps:
            print("❌ Layout overlaps detected:")
            for overlap in overlaps:
                print(f"   - {overlap}")
            return False
        else:
            print("✅ No layout overlaps detected")
        
        # Test bounds calculation
        bounds = scene.get_layout_bounds()
        print(f"✅ Layout bounds: {bounds['width']}x{bounds['height']} pixels")
        
        # Verify all widgets fit within 320x320 screen
        if bounds['max_x'] <= 320 and bounds['max_y'] <= 320:
            print("✅ All widgets fit within 320x320 screen")
        else:
            print(f"❌ Layout exceeds screen bounds: {bounds['max_x']}x{bounds['max_y']}")
            return False
            
        # Test zone organization
        zones = {
            "Feed controls": [name for name in scene.layout.keys() if 'feed' in name],
            "Fuel tanks": [name for name in scene.layout.keys() if 'tank' in name], 
            "Control sliders": [name for name in scene.layout.keys() if any(s in name for s in ['transfer', 'dump'])],
            "Navigation": [name for name in scene.layout.keys() if 'nav' in name]
        }
        
        print("\n📋 Layout Zone Organization:")
        for zone_name, widgets in zones.items():
            print(f"   {zone_name}: {len(widgets)} widgets - {', '.join(widgets)}")
        
        # Verify fixed elements haven't moved
        nav_prev = scene.layout["nav_prev"]
        nav_next = scene.layout["nav_next"]
        if (nav_prev["position"] == [8, 290] and nav_prev["size"] == [60, 24] and
            nav_next["position"] == [252, 290] and nav_next["size"] == [60, 24]):
            print("✅ Navigation buttons remain fixed as requested")
        else:
            print("❌ Navigation buttons were moved (should be fixed)")
            return False
            
        print("\n🎯 Layout Optimization Summary:")
        print("   - Systematic position calculation (no guessing!)")
        print("   - Zero widget overlaps")
        print("   - Proper zone organization")
        print("   - Fixed navigation elements preserved")
        print("   - Centralized layout configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_fuel_layout()
    if success:
        print("\n🎉 All layout tests passed!")
        exit(0)
    else:
        print("\n💥 Layout tests failed!")
        exit(1)
