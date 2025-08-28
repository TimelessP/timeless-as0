"""
Dynamically compute optimum altitudes for tailwind assist in all directions using Airship Zero wind model.
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
    # Linear sweep: 0ft=0°, 6000ft=360°
    t = (alt - 1000) / (6000 - 1000)
    return (t * 360.0) % 360.0

def wind_speed_1000_6000(alt):
    t = (alt - 1000) / (6000 - 1000)
    return 10 + (18 - 10) * t

def angle_diff(a, b):
    # Smallest difference between two angles in degrees
    d = (a - b + 180) % 360 - 180
    return abs(d)

headings = [
    ("N", 0), ("NE", 45), ("E", 90), ("SE", 135),
    ("S", 180), ("SW", 225), ("W", 270), ("NW", 315)
]

print(f"| Travelling | Heading | Best Altitude (ft) | Wind FROM | Wind Speed (kt) | Angle Offset | Note |")
print(f"|------------|---------|-------------------|-----------|-----------------|--------------|------|")

for name, heading in headings:
    # 1000-6000ft: can always get perfect tailwind
    # Find altitude for wind FROM = heading+180
    tail_from = (heading + 180) % 360
    t = tail_from / 360.0
    alt_1000_6000 = 1000 + t * (6000 - 1000)
    speed_1000_6000 = wind_speed_1000_6000(alt_1000_6000)
    print(f"| {name:<10} | {heading:>7} | {alt_1000_6000:>17.0f} | {tail_from:>9.0f} | {speed_1000_6000:>15.1f} | {0:>12} | 1000-6000ft, perfect tailwind |")
    # Also check other bands for stronger (but not perfectly aligned) tailwind
    for band in [wind_bands[0], wind_bands[2], wind_bands[3]]:
        min_a, max_a, base_dir, base_speed, *_ = band
        if base_dir == 'sweep':
            continue
        offset = angle_diff(base_dir, tail_from)
        note = ""
        if offset < 45:
            note = "Strong tailwind"
        elif offset < 90:
            note = "Cross/tailwind"
        else:
            note = "Mostly crosswind"
        print(f"| {name:<10} | {heading:>7} | {min_a:>5}-{max_a:<7} | {base_dir:>9.0f} | {base_speed:>15.1f} | {offset:>12.1f} | {note}        |")
