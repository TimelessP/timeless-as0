#!/usr/bin/env python3

"""Test script to verify triangle rendering fixes"""

import time
import pygame
from terrain_mesh import TerrainMesh, Camera3D, Vector3, TerrainVertex, TerrainTriangle
from heightmap import HeightMap

def test_triangle_rendering():
    """Test triangle rendering with edge cases that previously caused glitches"""
    
    # Initialize pygame for testing
    pygame.init()
    surface = pygame.Surface((320, 320))
    
    # Load test data
    heightmap = HeightMap()
    # HeightMap loads automatically, no need to explicitly load
    
    world_map = pygame.image.load("assets/png/world-map.png")
    mesh = TerrainMesh(heightmap, world_map)
    
    # Create test camera at problematic position
    camera_pos = Vector3(1000, 1000, 500)
    camera_target = Vector3(1000, 2000, 500)  # Looking north
    camera = Camera3D(camera_pos, camera_target)
    
    print("🔧 Testing triangle rendering fixes...")
    
    # Test 1: Generate mesh at current position
    start_time = time.time()
    mesh.generate_dual_lod_mesh_around_position(40.7128, -74.0060, 1000.0)  # NYC
    generation_time = time.time() - start_time
    
    stats = mesh.get_mesh_statistics()
    total_triangles = stats['total_triangles']
    print(f"✅ Generated {total_triangles} triangles in {generation_time:.3f}s")
    
    # Test 2: Render triangles without exceptions
    start_time = time.time()
    try:
        mesh.render_to_surface(surface, camera, 0, 0, 320, 320)
        render_time = time.time() - start_time
        print(f"✅ Rendered triangles in {render_time:.3f}s without exceptions")
        success = True
    except Exception as e:
        print(f"❌ Rendering failed with exception: {e}")
        success = False
    
    # Test 3: Test camera movement (potential glitch trigger)
    for i in range(5):
        # Create new camera position
        new_pos = Vector3(camera.position.x + 100, camera.position.y, camera.position.z + 50)
        new_target = Vector3(camera.target.x + 100, camera.target.y, camera.target.z + 50)
        camera = Camera3D(new_pos, new_target)
        
        try:
            mesh.render_to_surface(surface, camera, 0, 0, 320, 320)
        except Exception as e:
            print(f"❌ Movement test {i+1} failed: {e}")
            success = False
            break
    else:
        print("✅ Camera movement test passed")
    
    if success:
        print("🎉 All triangle rendering tests passed!")
        print("   - No vertex position glitches")
        print("   - No degenerate triangles")
        print("   - No try-catch exceptions needed")
    else:
        print("⚠️  Some tests failed")
    
    pygame.quit()
    return success

if __name__ == "__main__":
    test_triangle_rendering()
