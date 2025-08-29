#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from terrain_mesh import Camera3D, Vector3
import math

# Test aspect ratio calculation
viewport_w = 304
viewport_h = 200
aspect_ratio = viewport_w / viewport_h
print(f"Viewport: {viewport_w}x{viewport_h}, aspect ratio: {aspect_ratio:.3f}")

# Test camera at origin looking in different directions
camera = Camera3D(
    position=Vector3(0, 0, 0),
    target=Vector3(0, 0, 1),  # Looking in +Z direction
    up=Vector3(0, 1, 0)       # Y is up for camera
)

# Test points at different positions
test_points = [
    Vector3(0, 0, 1000),     # Straight ahead, far
    Vector3(100, 0, 1000),   # Right of center
    Vector3(-100, 0, 1000),  # Left of center
    Vector3(0, 100, 1000),   # Above center
    Vector3(0, -100, 1000),  # Below center
]

print(f"\nProjection tests:")
for i, point in enumerate(test_points):
    projected = camera.project_to_2d(point, viewport_w, viewport_h)
    print(f"  Point {i} {point} -> {projected}")

# Test with various FOV values
print(f"\nFOV tests for point Vector3(100, 0, 1000):")
test_point = Vector3(100, 0, 1000)
for fov in [30, 60, 90, 120]:
    projected = camera.project_to_2d(test_point, viewport_w, viewport_h, fov)
    print(f"  FOV {fov}° -> {projected}")
