"""
Test latitude/longitude wrapping and pole reflection for heightmap lookup.
"""
from heightmap import HeightMap

def wrap_lat_lon(lat, lon):
    # Implements the same logic as in core_simulator.py
    while lat > 90.0 or lat < -90.0:
        if lat > 90.0:
            lat = 180.0 - lat
            lon += 180.0
        elif lat < -90.0:
            lat = -180.0 - lat
            lon += 180.0
    lon = ((lon + 180.0) % 360.0) - 180.0
    return lat, lon

if __name__ == "__main__":
    hm = HeightMap()
    # Test cases: crossing poles and wrapping longitude
    test_coords = [
        (95, 0),      # North pole crossing
        (100, 10),    # Far north
        (-95, 0),     # South pole crossing
        (-100, -10),  # Far south
        (45, 200),    # Longitude wrap
        (45, -200),   # Negative longitude wrap
        (90, 180),    # At north pole, edge longitude
        (-90, -180),  # At south pole, edge longitude
        (90.0001, 0), # Just above north pole
        (-90.0001, 0),# Just below south pole
        (89.9999, 0), # Just below north pole
        (-89.9999, 0),# Just above south pole
    ]
    for lat, lon in test_coords:
        wlat, wlon = wrap_lat_lon(lat, lon)
        try:
            h = hm.height_at(wlat, wlon)
            print(f"Input: ({lat}, {lon}) -> Wrapped: ({wlat:.4f}, {wlon:.4f}) -> Height: {h:.2f} m")
        except Exception as e:
            print(f"Input: ({lat}, {lon}) -> Wrapped: ({wlat:.4f}, {wlon:.4f}) -> ERROR: {e}")
