# Riding the Winds: Designing a Realistic and Playable Wind System for Airship Zero

*By the Airship Zero Dev Team*

---

## Introduction

Simulating wind in a retro airship game is a deceptively complex challenge. We wanted wind to be more than a random number: it should be a navigational challenge, a source of skill, and a reflection of real atmospheric physics—yet it must remain fun and fair for players. This document is a technical deep-dive into the evolution of our wind system, the problems we encountered, and the pragmatic, math-driven solution we ultimately implemented.

---

## Early Attempts: The "Random Breeze" Problem

Our first wind model was simple:

```python
weather["windDirection"] += (math.sin(self.total_sim_time * 0.01) * 0.1)
weather["windDirection"] = weather["windDirection"] % 360
```

This produced a gently shifting wind, but it was:
- **Unrealistic**: No altitude dependence, no structure.
- **Uninteresting**: No skill—wind was just noise.
- **Unfair**: Sudden changes could make navigation feel arbitrary.

---

## Real-World Inspiration: Atmospheric Bands

We studied real meteorology:
- **Surface winds**: Variable, terrain-influenced, often SSW to WSW in temperate zones.
- **Mid-levels (1,000–6,000 ft)**: More consistent, stronger, often W to NW.
- **Jetstream (6,000–12,000+ ft)**: Fast, directional, highly variable.

We wanted to capture:
- **Altitude dependence**: Wind changes as you climb.
- **Smooth transitions**: No sharp jumps.
- **Skill**: Players can exploit or avoid winds by choosing their altitude.

---

## The Final Model: Altitude-Dependent, Smooth, and Navigable

### Wind Bands

We defined wind bands as tuples:

```python
(min_alt, max_alt, base_dir, base_speed, dir_var, speed_var)
```

Example:

```python
wind_bands = [
    (0, 1000, 220, 6, 20, 2),      # Low: SSW, gentle
    (1000, 3000, 250, 10, 25, 4),  # Mid: WSW, moderate
    (3000, 6000, 280, 18, 30, 6),  # High: W, strong
    (6000, 12000, 310, 30, 40, 10),# Jetstream: NW, fast
    (12000, 99999, 340, 40, 30, 8) # Stratosphere: NNW, very fast
]
```

### Interpolation

For any altitude, we interpolate between the two enclosing bands:

```python
t = (altitude - min_a) / (max_a - min_a)
base_dir = lerp(band_lo[2], band_hi[2], t)
base_speed = lerp(band_lo[3], band_hi[3], t)
dir_var = lerp(band_lo[4], band_hi[4], t)
speed_var = lerp(band_lo[5], band_hi[5], t)
```

Where `lerp(a, b, t) = a + (b - a) * t`.

### Smooth Transitions

Every 10–30 seconds, we pick a new target wind (direction and speed) within the allowed variance:

```python
ws["target_dir"] = base_dir + random.uniform(-dir_var, dir_var)
ws["target_speed"] = max(0.0, base_speed + random.uniform(-speed_var, speed_var))
```

We then smoothly approach these targets:

```python
def smooth_angle(a, b, rate):
    diff = ((b - a + 180) % 360) - 180
    if abs(diff) < rate:
        return b
    return (a + rate * (1 if diff > 0 else -1)) % 360

ws["dir"] = smooth_angle(ws["dir"], ws["target_dir"], dt * 2.5)  # 2.5 deg/sec
ws["speed"] += max(-1.5 * dt, min(1.5 * dt, ws["target_speed"] - ws["speed"]))
```

This ensures wind changes are gradual, never jarring.

### Example: Wind at 4,000 ft

- **Bands**: (3,000–6,000 ft) and (6,000–12,000 ft)
- **t**: (4,000 - 3,000) / (12,000 - 3,000) ≈ 0.11
- **Base direction**: lerp(280, 310, 0.11) ≈ 283.3°
- **Base speed**: lerp(18, 30, 0.11) ≈ 19.3 knots
- **Variance**: dir_var ≈ 33.3°, speed_var ≈ 7.3 knots

So, at 4,000 ft, wind is generally from the west-northwest at ~19 knots, but can vary ±33° and ±7 knots over time.

---

## Why Not More Realism?

We considered:
- **Perlin/simplex noise fields**: Too complex for our scale, hard to make skillful.
- **Full 3D wind simulation**: Overkill, not fun.
- **Random walk**: Not altitude-dependent, not skillful.

Our solution is a compromise: *realistic enough to feel right, simple enough to be learnable and fun*.

---

## Gameplay Impact

- **Navigation skill**: Players can climb or descend to exploit tailwinds or avoid headwinds.
- **Predictability**: Wind changes are smooth, so players can plan.
- **Challenge**: Jetstream altitudes are fast but turbulent—risky for precise navigation.

---

## Full Implementation (Excerpt)

```python
def _update_wind_field(self, dt: float):
    # ...
    # See core_simulator.py for full code
```

---

## Conclusion

Wind in Airship Zero is not just a number—it's a system, a challenge, and a story. We hope you enjoy riding the winds as much as we enjoyed building them.
