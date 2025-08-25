# Riding the Winds: Airship Zero Wind System (Technical)

## Overview

The wind system in Airship Zero is designed to provide a skill-based, physically plausible, and highly readable wind environment for airship navigation. This document details the technical implementation of the wind model as of August 2025, including the new continuous 360° wind direction sweep between 1000ft and 6000ft.

---

## Altitude-Dependent Wind Model

The wind field is a function of altitude, time, and random variance. The model is designed to:
- Encourage skillful altitude selection for optimal travel.
- Provide smooth, predictable transitions with some randomness.
- Allow for a full 360° sweep of wind direction in the key navigation band (1000ft–6000ft).

### Wind Bands

The wind model is divided into altitude bands:

| Altitude Band      | Wind Direction         | Speed (kt) | Direction Variance | Speed Variance |
|--------------------|-----------------------|------------|--------------------|---------------|
| 0–1000 ft          | 220° (SSW)            | 6          | ±20°               | ±2            |
| 1000–6000 ft       | **0–360° sweep**      | 10–18      | ±25°→±30°          | ±4→±6         |
| 6000–12000 ft      | 310° (NW)             | 30         | ±40°               | ±10           |
| 12000+ ft          | 340° (NNW)            | 40         | ±30°               | ±8            |

#### Special Band: 1000–6000 ft (360° Sweep)
- **Wind direction** increases linearly from 0° to 360° as you climb from 1000ft to 6000ft.
- At 1000ft: wind is from 0° (North).
- At 3500ft: wind is from 180° (South).
- At 6000ft: wind is from 360° (wraps to North).
- This creates a full directional cycle, rewarding pilots who find the best altitude for their desired heading.
- Wind speed and variance are interpolated between 10kt/±25°/±4 (at 1000ft) and 18kt/±30°/±6 (at 6000ft).

### Interpolation and Smoothness
- For altitudes outside 1000–6000ft, the model interpolates between adjacent bands for direction, speed, and variance.
- Within 1000–6000ft, direction is a pure linear sweep; speed/variance are interpolated.
- Wind direction and speed are subject to slow, smooth random changes (targeted every 10–30s, with gradual transitions).

---

## Mathematical Formulation

### Wind Direction (1000–6000ft)

Let `alt` be the altitude in feet:

```
if 1000 <= alt < 6000:
    t = (alt - 1000) / 5000
    wind_dir = (t * 360) % 360
    wind_speed = lerp(10, 18, t)
    dir_var = lerp(25, 30, t)
    speed_var = lerp(4, 6, t)
```

- `lerp(a, b, t)` is linear interpolation.
- For other bands, direction/speed/variance are interpolated between band endpoints.

### Randomness and Smoothing
- Every 10–30 seconds, a new target wind direction and speed are chosen within the allowed variance.
- The actual wind transitions smoothly toward the target (direction: max 2.5°/sec, speed: max 1.5kt/sec).

---

## Gameplay Implications

- **Navigation Skill**: Pilots can optimize ground speed by selecting the altitude where the wind best matches their desired course.
- **Dynamic Planning**: The 360° sweep means every heading has an optimal altitude between 1000ft and 6000ft.
- **Realism**: The model mimics real-world atmospheric layers and jetstreams, while remaining readable and learnable.

---

## Example Table: Wind Direction by Altitude (1000–6000ft)

| Altitude (ft) | Wind Dir (°) |
|--------------|--------------|
| 1000         | 0            |
| 2000         | 72           |
| 3000         | 144          |
| 4000         | 216          |
| 5000         | 288          |
| 6000         | 360 (0)      |

---

## Code Reference (core_simulator.py)

```python
if 1000 <= altitude < 6000:
    t = (altitude - 1000) / (6000 - 1000)
    base_dir = (t * 360.0) % 360.0
    base_speed = lerp(10, 18, t)
    dir_var = lerp(25, 30, t)
    speed_var = lerp(4, 6, t)
else:
    # Use banded model for other altitudes
    ...
```

---

## Revision History
- **2025-08-25**: Wind model updated to use a continuous 360° sweep between 1000ft and 6000ft.
- Previous versions used fixed directions per band or simple interpolation.

---

*This document is in-game technical lore and a reference for advanced pilots and modders.*
