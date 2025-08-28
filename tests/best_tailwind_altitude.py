"""
Find the single best altitude for maximum tailwind assist for each cardinal/intercardinal direction.
"""
import math

# Wind bands as in _update_wind_field
wind_bands = [
    (0, 1000, 220, 6, 20, 2),      # Low: SSW, gentle, variable
    (1000, 6000, 'sweep', None, None, None),  # 1000-6000ft: direction sweeps 0-360°
    (6000, 12000, 310, 30, 40, 10), # Jetstream: NW, fast, highly variable
    (12000, 99999, 340, 40, 30, 8) # Stratosphere: NNW, very fast, less variable
]

def wind_dir_1000_6000(alt):
    t = (alt - 1000) / (6000 - 1000)
    return (t * 360.0) % 360.0

def wind_speed_1000_6000(alt):
    t = (alt - 1000) / (6000 - 1000)
    return 10 + (18 - 10) * t

def angle_diff(a, b):
    d = (a - b + 180) % 360 - 180
    return abs(d)

headings = [
    ("N", 0), ("NE", 45), ("E", 90), ("SE", 135),
    ("S", 180), ("SW", 225), ("W", 270), ("NW", 315)
]

results = {}

for name, heading in headings:
    tail_from = (heading + 180) % 360
    # 1000-6000ft: perfect tailwind, but speed 10-18kt
    alt_1000_6000 = 1000 + (tail_from / 360.0) * (6000 - 1000)
    speed_1000_6000 = wind_speed_1000_6000(alt_1000_6000)
    best = {'altitude': alt_1000_6000, 'speed': speed_1000_6000, 'offset': 0, 'band': '1000-6000'}
    # Only consider bands with midpoint under 7000 ft
    for band in [wind_bands[0], wind_bands[2]]:
        min_a, max_a, base_dir, base_speed, *_ = band
        if base_dir == 'sweep':
            continue
        mid_alt = (min_a + max_a) / 2
        if mid_alt > 7000:
            continue
        offset = angle_diff(base_dir, tail_from)
        if offset <= 45 and base_speed > best['speed']:
            best = {'altitude': mid_alt, 'speed': base_speed, 'offset': offset, 'band': f'{min_a}-{max_a}'}
    results[name] = best

print(f"| Travelling | Best Altitude (ft) | Wind Speed (kt) |")
print(f"|------------|-------------------|-----------------|")
for name in headings:
    h = name[0]
    r = results[h]
    print(f"| {h:<10} | {r['altitude']:>17.0f} | {r['speed']:>15.1f} |")
