#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from terrain_mesh import TerrainMesh
from heightmap import HeightMap

# Test sun generation
heightmap = HeightMap()
world_map = None  # Not needed for sun generation
mesh = TerrainMesh(heightmap, world_map)

# Generate sun with test parameters
latitude = 51.5074  # London
longitude = -0.1278
altitude = 0.0  # Sea level
time_info = {
    'gameTime': 43200.0,  # Noon UTC
    'realTime': 1735459200.0  # Some timestamp
}

print(f"Testing sun generation at lat={latitude}, lon={longitude}, alt={altitude}")

mesh.generate_3d_sun(latitude, longitude, altitude, time_info)
print(f"Sun triangles generated: {len(mesh.sun_triangles)}")

if mesh.sun_triangles:
    # Look at first triangle
    triangle = mesh.sun_triangles[0]
    print(f"First triangle vertices:")
    vertices = [triangle.v1, triangle.v2, triangle.v3]
    for i, vertex in enumerate(vertices):
        pos = vertex.position
        print(f"  Vertex {i}: x={pos.x:.2f}, y={pos.y:.2f}, z={pos.z:.2f}")
    
    # Test projection
    from terrain_mesh import Camera3D, Vector3
    import math
    
    # Calculate camera direction to look at sun (azimuth 253.4°, elevation 23.8°)
    sun_azimuth = 253.4
    sun_elevation = 23.8
    
    # Convert to radians
    az_rad = math.radians(sun_azimuth)
    el_rad = math.radians(sun_elevation)
    
    # Calculate target point in the direction of the sun
    target_x = math.cos(el_rad) * math.sin(az_rad)
    target_y = math.cos(el_rad) * math.cos(az_rad)  
    target_z = math.sin(el_rad)
    
    # Create camera looking towards the sun
    camera = Camera3D(
        position=Vector3(0, 0, 0),
        target=Vector3(target_x, target_y, target_z),
        up=Vector3(0, 0, 1)  # Z is up
    )
    
    print(f"Camera target direction: ({target_x:.3f}, {target_y:.3f}, {target_z:.3f})")
    
    print(f"\nProjection test (viewport 304x200):")
    for i, vertex in enumerate(vertices):
        projected = camera.project_to_2d(vertex.position, 304, 200)
        print(f"  Vertex {i} -> {projected}")
else:
    print("ERROR: No sun triangles generated!")
