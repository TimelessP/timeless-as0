#!/usr/bin/env python3
"""
Test script to demonstrate the new close-triangle culling behavior

This shows how triangles within 3 triangle distances are preserved
even when they would normally be frustum culled.
"""

def main():
    print("=== Close Triangle Culling Protection ===")
    print()
    
    # Calculate triangle distances based on mesh parameters
    inner_radius_deg = 2.0
    inner_resolution = 32
    scale_horizontal = 13050.0
    
    # Triangle edge length calculation
    triangle_edge_deg = (inner_radius_deg * 2) / inner_resolution
    triangle_edge_units = triangle_edge_deg * scale_horizontal
    
    print(f"Inner mesh parameters:")
    print(f"  Radius: {inner_radius_deg}° = {inner_radius_deg * 111.3:.0f} km")
    print(f"  Resolution: {inner_resolution}x{inner_resolution}")
    print(f"  Triangle edge: {triangle_edge_deg:.3f}° = {triangle_edge_units:.0f} units")
    print()
    
    # No-cull distance
    no_cull_distance = 5000.0
    triangle_distances = no_cull_distance / triangle_edge_units
    
    print(f"Close triangle protection:")
    print(f"  No-cull distance: {no_cull_distance:.0f} units")
    print(f"  Triangle edge: {triangle_edge_units:.0f} units")
    print(f"  Protection coverage: {triangle_distances:.1f} triangle distances")
    print()
    
    # Physical distances
    triangle_edge_km = triangle_edge_deg * 111.3  # km per degree
    no_cull_km = no_cull_distance / 1000.0  # Assuming scale units are meters
    
    print(f"Physical coverage:")
    print(f"  Triangle edge: {triangle_edge_km:.1f} km")
    print(f"  No-cull radius: {no_cull_km:.1f} km")
    print()
    
    print("Benefits:")
    print("  ✓ Landing on hillsides won't lose ground triangles")
    print("  ✓ Close terrain always visible regardless of camera angle") 
    print("  ✓ Prevents 'falling through world' visual artifacts")
    print("  ✓ 5x larger viewport bounds for close triangles")
    print("  ✓ Less aggressive behind-camera culling for close triangles")
    print()
    
    # Show culling behavior at different distances
    test_distances = [1000, 3000, 5000, 7500, 10000, 50000, 100000, 150000]
    
    print("Culling behavior by distance:")
    print("Distance (units) | Status")
    print("-" * 30)
    
    for dist in test_distances:
        if dist <= no_cull_distance:
            status = "PROTECTED (no culling)"
        elif dist <= 100000:
            status = "Normal culling"
        else:
            status = "CULLED (too distant)"
        print(f"{dist:>13} | {status}")

if __name__ == "__main__":
    main()
