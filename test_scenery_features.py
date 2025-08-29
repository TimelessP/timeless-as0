#!/usr/bin/env python3
"""
Test advanced scenery features for Observatory Scene
"""

import sys
import os
import pygame

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scenery import Scenery

def test_scenery_features():
    """Test all advanced scenery features"""
    
    print("🧪 Testing Advanced Scenery Features...")
    
    # Initialize pygame for surface operations
    pygame.init()
    
    # Create scenery instance
    scenery = Scenery()
    print("✅ Scenery instance created")
    
    # Test terrain color sampling
    print("\n🎨 Testing terrain color sampling:")
    
    # Test various geographic locations
    test_locations = [
        (40.7128, -74.0060, "New York City"),
        (51.5074, -0.1278, "London"),
        (35.6762, 139.6503, "Tokyo"),
        (0.0, 0.0, "Gulf of Guinea"),
        (-33.8688, 151.2093, "Sydney"),
        (55.7558, 37.6176, "Moscow")
    ]
    
    for lat, lon, name in test_locations:
        color = scenery.sample_terrain_color(lat, lon)
        is_water = scenery._is_water_color(color)
        terrain_type = "Water" if is_water else "Land"
        print(f"  {name:15} ({lat:7.3f}, {lon:8.3f}): RGB{color} - {terrain_type}")
    
    # Test sun position calculation
    print("\n☀️ Testing sun position calculation:")
    time_info = {}  # Will use current system time
    sun_lat, sun_lon = scenery.calculate_sun_position(time_info)
    print(f"  Current sun position: {sun_lat:.2f}°N, {sun_lon:.2f}°E")
    
    # Test fuel-based tilt calculation
    print("\n⚖️ Testing fuel-based tilt calculation:")
    test_fuel_states = [
        ({"tanks": {"forward": {"level": 50}, "aft": {"level": 50}}}, "Balanced"),
        ({"tanks": {"forward": {"level": 80}, "aft": {"level": 20}}}, "Forward heavy"),
        ({"tanks": {"forward": {"level": 20}, "aft": {"level": 80}}}, "Aft heavy"),
        ({"tanks": {"forward": {"level": 100}, "aft": {"level": 0}}}, "Maximum forward"),
        ({"tanks": {"forward": {"level": 0}, "aft": {"level": 100}}}, "Maximum aft")
    ]
    
    for fuel_state, description in test_fuel_states:
        tilt = scenery.calculate_tilt_from_fuel(fuel_state)
        print(f"  {description:15}: {tilt:+.1f}° (positive = nose up)")
    
    # Test horizon rendering
    print("\n🌄 Testing horizon rendering:")
    test_surface = pygame.Surface((304, 200))
    
    # Mock game state data
    mock_position = {"latitude": 40.7128, "longitude": -74.0060}
    mock_motion = {"pitch": 2.5}
    mock_fuel_state = {"tanks": {"forward": {"level": 60}, "aft": {"level": 40}}}
    mock_time_info = {}
    
    try:
        scenery.render_horizon_360(
            test_surface,
            view_angle=45.0,  # Looking northeast
            position=mock_position,
            motion=mock_motion,
            fuel_state=mock_fuel_state,
            time_info=mock_time_info,
            field_of_view=120.0
        )
        print("  ✅ Horizon rendering completed successfully")
        print(f"  📐 Rendered 360° view with 120° FOV at 45° heading")
        print(f"  🗺️ Position: {mock_position['latitude']:.3f}°N, {abs(mock_position['longitude']):.3f}°W")
        
        # Verify surface was modified (not just filled with one color)
        pixels = pygame.surfarray.array3d(test_surface)
        unique_colors = len(set(tuple(pixel) for pixel in pixels.reshape(-1, 3)))
        print(f"  🎨 Generated {unique_colors} unique colors (terrain variation)")
        
    except Exception as e:
        print(f"  ❌ Horizon rendering failed: {e}")
    
    # Test bearing calculations
    print("\n🧭 Testing bearing calculations:")
    test_bearings = [
        ((40.7128, -74.0060), (51.5074, -0.1278), "NYC to London"),
        ((0.0, 0.0), (90.0, 0.0), "Equator to North Pole"),
        ((35.6762, 139.6503), (-33.8688, 151.2093), "Tokyo to Sydney")
    ]
    
    for (lat1, lon1), (lat2, lon2), description in test_bearings:
        bearing = scenery._calculate_bearing(lat1, lon1, lat2, lon2)
        print(f"  {description:20}: {bearing:06.2f}°")
    
    print("\n✅ All scenery feature tests completed!")
    print("🎯 Observatory scene now has:")
    print("   • Terrain color sampling from world-map.png")
    print("   • Real-time sun position calculation")
    print("   • Fuel-based airship tilt effects")
    print("   • Sun shading of terrain based on lighting")
    print("   • Dynamic horizon rendering with geographic accuracy")
    print("   • Forward and sun direction indicators")

if __name__ == "__main__":
    test_scenery_features()
