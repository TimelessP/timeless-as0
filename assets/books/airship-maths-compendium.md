# The Airship Zero Mathematical Compendium

*A Complete Guide to the Mathematical Foundations of Airship Flight Simulation*

---

## Preface

This compendium documents the mathematical formulas, algorithms, and calculations that power every aspect of the Airship Zero simulation. From the fundamental physics of flight to the complex trigonometry of navigation, every computation that brings our virtual airship to life is catalogued here for the mathematically curious captain.

Whether you seek to understand the exponential decay of atmospheric pressure with altitude, the spherical trigonometry that plots our course across the globe, or the harmonic analysis that generates our engine's distinctive sound, you will find the mathematical truth behind the simulation within these pages.

---

## Chapter 1: Atmospheric Physics

### 1.1 Altitude Density Factor

**Purpose**: Models how air density decreases exponentially with altitude, affecting engine performance, thrust, and indicated vs. true airspeed.

**Formula**:
```
altitude_density_factor = e^(-altitude / 29000.0)
```

**Variables**:
- `altitude`: Height above sea level in feet
- `29000.0`: Scale height constant (feet) - approximately where density drops to 50%

**Example**: At 10,000 feet:
```
altitude_density_factor = e^(-10000 / 29000) = e^(-0.345) ≈ 0.708
```
This means air density is approximately 71% of sea level density.

**Applications**:
- Engine manifold pressure calculation
- Propeller thrust reduction
- True airspeed conversion from indicated airspeed

### 1.2 Atmospheric Pressure with Altitude

**Purpose**: Calculates atmospheric pressure at different altitudes using the barometric formula.

**Formula**:
```
atmospheric_pressure = 29.92 * e^(-altitude / 29000.0)
```

**Variables**:
- `29.92`: Standard sea level atmospheric pressure (inches of mercury)
- `altitude`: Height above sea level in feet

**Example**: At 5,000 feet:
```
atmospheric_pressure = 29.92 * e^(-5000 / 29000) = 29.92 * 0.842 ≈ 25.2 inHg
```

### 1.3 True Airspeed to Indicated Airspeed Conversion

**Purpose**: Converts between indicated airspeed (what instruments show) and true airspeed (actual speed through air mass).

**Formula**:
```
TAS = IAS / √(density_ratio)
TAS = IAS / √(altitude_density_factor)
```

**Variables**:
- `TAS`: True airspeed
- `IAS`: Indicated airspeed
- `density_ratio`: Ratio of current air density to sea level density

**Example**: At 15,000 feet with IAS = 85 knots:
```
density_factor = e^(-15000 / 29000) ≈ 0.596
TAS = 85 / √(0.596) = 85 / 0.772 ≈ 110 knots
```

---

## Chapter 2: Engine Performance Mathematics

### 2.1 RPM Factor Calculation

**Purpose**: Determines engine performance based on current RPM relative to maximum.

**Formula**:
```
rpm_factor = current_rpm / 2800.0
```

**Variables**:
- `current_rpm`: Current engine revolutions per minute
- `2800.0`: Maximum engine RPM

**Example**: At 2100 RPM:
```
rpm_factor = 2100 / 2800 = 0.75
```
Engine is operating at 75% of maximum RPM.

### 2.2 Fuel Pressure Degradation

**Purpose**: Models fuel pressure drop when fuel levels are critically low.

**Formula**:
```
pressure_factor = total_fuel / 20.0  (when total_fuel < 20.0)
final_pressure = base_pressure * pressure_factor
```

**Variables**:
- `total_fuel`: Combined fuel from all feeding tanks
- `20.0`: Critical fuel threshold (gallons)
- `base_pressure`: Normal fuel pressure (22.0 PSI)

**Example**: With 8 gallons remaining:
```
pressure_factor = 8.0 / 20.0 = 0.4
final_pressure = 22.0 * 0.4 = 8.8 PSI
```

### 2.3 Oil Pressure Correlation

**Purpose**: Calculates oil pressure based on engine RPM and health.

**Formula**:
```
base_oil_pressure = 20 + (rpm / 2800.0) * 55
final_oil_pressure = base_oil_pressure * health_factor
```

**Variables**:
- `20`: Minimum oil pressure at idle (PSI)
- `55`: Additional pressure range from idle to redline
- `health_factor`: Engine health multiplier (0.5-1.0)

**Example**: At 2100 RPM with healthy engine:
```
base_oil_pressure = 20 + (2100 / 2800) * 55 = 20 + 41.25 = 61.25 PSI
```

### 2.4 Manifold Pressure Calculation

**Purpose**: Determines intake manifold pressure based on throttle, altitude, and fuel availability.

**Formula**:
```
atmospheric_pressure = 29.92 * e^(-altitude / 29000.0)
base_manifold = atmospheric_pressure + (throttle * 15.0)
manifold_pressure = base_manifold * fuel_factor * mixture_factor
```

**Variables**:
- `throttle`: Throttle setting (0.0 to 1.0)
- `15.0`: Maximum boost above atmospheric (inches Hg)
- `fuel_factor`: Fuel availability multiplier
- `mixture_factor`: Mixture efficiency multiplier

**Example**: At sea level, full throttle, optimal conditions:
```
atmospheric_pressure = 29.92 inHg
base_manifold = 29.92 + (1.0 * 15.0) = 44.92 inHg
manifold_pressure = 44.92 * 1.0 * 1.0 = 44.92 inHg
```

---

## Chapter 3: Propeller Physics and Thrust Calculations

### 3.1 Propeller Efficiency with Pitch Optimization

**Purpose**: Calculates propeller efficiency based on pitch setting relative to optimal pitch for current conditions.

**Optimal Pitch Formula**:
```
optimal_pitch_for_speed = 0.3 + (airspeed / 100.0) * 0.4
optimal_pitch_for_altitude = optimal_pitch_for_speed * (0.9 + density_factor * 0.1)
```

**Efficiency Calculation**:
```
pitch_deviation = |propeller_pitch - optimal_pitch_for_altitude|

if pitch_deviation ≤ 0.1:
    pitch_efficiency = 1.0
elif pitch_deviation ≤ 0.3:
    pitch_efficiency = 1.0 - (pitch_deviation - 0.1) * 1.5
else:
    pitch_efficiency = 0.7 - (pitch_deviation - 0.3) * 0.5

pitch_efficiency = max(0.4, pitch_efficiency)
```

**Example**: At 60 knots airspeed, 10,000 feet, pitch setting 0.5:
```
optimal_pitch_for_speed = 0.3 + (60 / 100) * 0.4 = 0.54
density_factor = e^(-10000 / 29000) ≈ 0.708
optimal_pitch_for_altitude = 0.54 * (0.9 + 0.708 * 0.1) = 0.54 * 0.971 ≈ 0.524
pitch_deviation = |0.5 - 0.524| = 0.024
pitch_efficiency = 1.0 (within 0.1 tolerance)
```

### 3.2 Thrust Factor Calculation

**Purpose**: Determines total thrust output combining all engine and propeller factors.

**Formula**:
```
base_thrust = throttle * rpm_factor * prop_efficiency * altitude_factor
fuel_flow_efficiency = min(1.0, actual_flow / expected_flow)
thrust_factor = base_thrust * fuel_flow_efficiency
```

**Variables**:
- `throttle`: Throttle setting (0.0 to 1.0)
- `rpm_factor`: Engine RPM efficiency
- `prop_efficiency`: Propeller efficiency factor
- `altitude_factor`: Air density at current altitude
- `fuel_flow_efficiency`: Fuel delivery adequacy

### 3.3 Target Airspeed from Thrust

**Purpose**: Converts thrust factor into achievable airspeed.

**Formula**:
```
sea_level_airspeed = 85.0  # knots
altitude_airspeed_factor = 0.7 + altitude_density_factor * 0.3
base_airspeed = sea_level_airspeed * altitude_airspeed_factor
min_airspeed = 15.0  # stall speed
target_airspeed = min_airspeed + (base_airspeed - min_airspeed) * thrust_factor
```

**Example**: At 8,000 feet with 80% thrust:
```
altitude_density_factor = e^(-8000 / 29000) ≈ 0.762
altitude_airspeed_factor = 0.7 + 0.762 * 0.3 = 0.929
base_airspeed = 85.0 * 0.929 = 78.9 knots
target_airspeed = 15.0 + (78.9 - 15.0) * 0.8 = 15.0 + 51.1 = 66.1 knots
```

---

## Chapter 4: Wind and Motion Dynamics

### 4.1 Wind Component Calculation

**Purpose**: Determines headwind/tailwind component affecting ground speed.

**Formula**:
```
wind_component = wind_speed * cos(aircraft_heading - wind_direction)
ground_speed = true_airspeed + wind_component
```

**Variables**:
- `wind_speed`: Wind velocity in knots
- `aircraft_heading`: Aircraft heading in degrees
- `wind_direction`: Wind direction in degrees
- Angles converted to radians: `radians = degrees * π / 180`

**Example**: Aircraft heading 090°, wind from 070° at 20 knots:
```
heading_difference = 90 - 70 = 20°
wind_component = 20 * cos(20°) = 20 * 0.940 = 18.8 knots (tailwind)
```

### 4.2 Position Updates from Ground Track

**Purpose**: Updates latitude and longitude based on ground speed and heading.

**Formula**:
```
degrees_per_second = ground_speed / 3600.0 / 60.0
heading_rad = radians(heading)
lat_change = degrees_per_second * cos(heading_rad) * dt
lon_change = degrees_per_second * sin(heading_rad) * dt / cos(radians(latitude))
```

**Variables**:
- `ground_speed`: Speed over ground in knots
- `3600.0`: Seconds per hour
- `60.0`: Nautical miles per degree (approximate)
- `dt`: Time step in seconds
- Longitude change adjusted for latitude convergence

**Example**: Flying north at 60 knots for 1 minute at 45°N:
```
degrees_per_second = 60 / 3600 / 60 = 0.000278
lat_change = 0.000278 * cos(0°) * 60 = 0.0167° ≈ 1 nautical mile north
lon_change = 0.000278 * sin(0°) * 60 / cos(45°) = 0° (no eastward movement)
```

---

## Chapter 5: Great Circle Navigation

### 5.1 Haversine Distance Formula

**Purpose**: Calculates the shortest distance between two points on Earth's surface.

**Formula**:
```
a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
c = 2 * atan2(√a, √(1-a))
distance = R * c
```

**Variables**:
- `lat1, lon1`: Starting coordinates in radians
- `lat2, lon2`: Ending coordinates in radians
- `Δlat = lat2 - lat1`, `Δlon = lon2 - lon1`
- `R`: Earth's radius (3440.065 nautical miles)

**Example**: Distance from 40°N 74°W to 51°N 0°W:
```
lat1 = 40° = 0.698 rad, lon1 = -74° = -1.291 rad
lat2 = 51° = 0.890 rad, lon2 = 0° = 0 rad
Δlat = 0.192 rad, Δlon = 1.291 rad

a = sin²(0.096) + cos(0.698) * cos(0.890) * sin²(0.646)
a = 0.009 + 0.766 * 0.629 * 0.392 = 0.197
c = 2 * atan2(√0.197, √0.803) = 2 * atan2(0.444, 0.896) = 0.896
distance = 3440.065 * 0.896 ≈ 3082 nautical miles
```

### 5.2 Forward Azimuth (Bearing) Calculation

**Purpose**: Determines the initial compass bearing from one point toward another.

**Formula**:
```
y = sin(Δlon) * cos(lat2)
x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(Δlon)
bearing = atan2(y, x)
```

**Variables**:
- All coordinates in radians
- Result in radians, convert to degrees and normalize to 0-360°

**Example**: Bearing from 40°N 74°W to 51°N 0°W:
```
y = sin(1.291) * cos(0.890) = 0.964 * 0.629 = 0.607
x = cos(0.698) * sin(0.890) - sin(0.698) * cos(0.890) * cos(1.291)
x = 0.766 * 0.775 - 0.643 * 0.629 * 0.269 = 0.594 - 0.109 = 0.485
bearing = atan2(0.607, 0.485) = 0.896 rad = 51.3°
```

### 5.3 Destination Point from Distance and Bearing

**Purpose**: Calculates the endpoint given a starting point, bearing, and distance.

**Formula**:
```
lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(bearing))
Δlon = atan2(sin(bearing) * sin(d/R) * cos(lat1), cos(d/R) - sin(lat1) * sin(lat2))
lon2 = lon1 + Δlon
```

**Variables**:
- `d`: Distance in nautical miles
- `R`: Earth's radius (3440.065 nautical miles)
- `d/R`: Angular distance in radians

**Example**: 100 NM northeast (045°) from 40°N 74°W:
```
d/R = 100 / 3440.065 = 0.029 rad
lat2 = asin(sin(0.698) * cos(0.029) + cos(0.698) * sin(0.029) * cos(0.785))
lat2 = asin(0.643 * 0.999 + 0.766 * 0.029 * 0.707) = asin(0.658) = 0.718 rad = 41.1°N

Δlon = atan2(sin(0.785) * 0.029 * 0.766, 0.999 - 0.643 * 0.660)
Δlon = atan2(0.016, 0.575) = 0.028 rad = 1.6°
lon2 = -74° + 1.6° = -72.4°W
```

### 5.4 Spherical Linear Interpolation (SLERP)

**Purpose**: Generates intermediate points along a great circle arc for route visualization.

**Formula**:
```
A = sin((1 - t) * angular_distance) / sin(angular_distance)
B = sin(t * angular_distance) / sin(angular_distance)

x = A * cos(lat1) * cos(lon1) + B * cos(lat2) * cos(lon2)
y = A * cos(lat1) * sin(lon1) + B * cos(lat2) * sin(lon2)
z = A * sin(lat1) + B * sin(lat2)

lat_intermediate = atan2(z, √(x² + y²))
lon_intermediate = atan2(y, x)
```

**Variables**:
- `t`: Interpolation parameter (0.0 to 1.0)
- `angular_distance`: Total angular distance between points

---

## Chapter 6: Cargo Physics and Center of Gravity

### 6.1 Weighted Center of Gravity Calculation

**Purpose**: Determines the cargo hold's center of gravity based on crate positions and weights.

**Formula**:
```
total_weight = Σ(weight_i)
weighted_x = Σ(x_i * weight_i)
weighted_y = Σ(y_i * weight_i)

center_of_gravity_x = weighted_x / total_weight
center_of_gravity_y = weighted_y / total_weight
```

**Variables**:
- `weight_i`: Weight of crate i
- `x_i, y_i`: Position coordinates of crate i
- Sum over all crates in cargo hold

**Example**: Three crates:
- Crate A: 10 lbs at (50, 100)
- Crate B: 15 lbs at (150, 100)  
- Crate C: 5 lbs at (100, 50)

```
total_weight = 10 + 15 + 5 = 30 lbs
weighted_x = (50 * 10) + (150 * 15) + (100 * 5) = 500 + 2250 + 500 = 3250
weighted_y = (100 * 10) + (100 * 15) + (50 * 5) = 1000 + 1500 + 250 = 2750

CG_x = 3250 / 30 = 108.3
CG_y = 2750 / 30 = 91.7
```

### 6.2 Euclidean Distance for Winch Proximity

**Purpose**: Calculates distance between winch hook and cargo attachment points.

**Formula**:
```
distance = √((x₂ - x₁)² + (y₂ - y₁)²)
```

**Variables**:
- `(x₁, y₁)`: Hook position
- `(x₂, y₂)`: Crate attachment point (center of top edge)

**Example**: Hook at (160, 75), crate center at (140, 90):
```
distance = √((140 - 160)² + (90 - 75)²) = √(400 + 225) = √625 = 25 pixels
```

---

## Chapter 7: Sound Synthesis and Harmonic Analysis

### 7.1 Propeller Blade Phase Calculation

**Purpose**: Generates realistic propeller audio using phase-shifted sine waves for each blade.

**Formula**:
```
prop_frequency = rpm / 60.0  # Hz
omega = 2π * prop_frequency
blade1_phase = phase_accumulator + omega * t
blade2_phase = blade1_phase + π  # 180° offset for 2-blade prop
```

**Variables**:
- `rpm`: Propeller revolutions per minute
- `t`: Time in seconds
- `π`: Pi (180° phase offset for second blade)

**Example**: At 2400 RPM:
```
prop_frequency = 2400 / 60 = 40 Hz
omega = 2π * 40 = 251.3 rad/s
```

### 7.2 Blade Envelope Modulation

**Purpose**: Creates realistic propeller sound with amplitude modulation representing blade passage.

**Formula**:
```
blade_base = sin(blade_phase)
blade_envelope = 0.5 + 0.5 * sin(blade_phase * 2)
blade_signal = blade_base * blade_envelope
```

**Variables**:
- `blade_phase`: Current phase of blade rotation
- Envelope creates 2 pulses per rotation (once per blade passage)

### 7.3 Engine Cylinder Firing Sequence

**Purpose**: Models 6-cylinder radial engine with individual cylinder firing phases.

**Formula**:
```
firing_interval = 60.0 / (rpm * cylinders)  # seconds between firings
cylinder_phase_offset = (cylinder_number / 6.0) * 2π
next_firing_time = current_time + firing_interval
```

**Variables**:
- `cylinders = 6`: Number of engine cylinders
- `cylinder_number`: 0-5 for each cylinder
- Evenly spaced firing: 0°, 60°, 120°, 180°, 240°, 300°

**Example**: At 1800 RPM:
```
firing_interval = 60.0 / (1800 * 6) = 0.00556 seconds
Cylinder 0 fires at phase 0°
Cylinder 1 fires at phase 60° = π/3 radians
```

### 7.4 Wind Noise Harmonic Generation

**Purpose**: Creates realistic wind noise using multiple frequency components.

**Formula**:
```
base_frequency = 30 + airspeed * 2  # Hz
harmonic1_frequency = base_frequency * 1.618  # Golden ratio
harmonic2_frequency = base_frequency * 2.414  # √2 * √3

wind_signal = sin(2π * base_freq * t) + 
              0.6 * sin(2π * harmonic1_freq * t) +
              0.3 * sin(2π * harmonic2_freq * t)
```

**Variables**:
- `airspeed`: Aircraft indicated airspeed in knots
- `1.618`: Golden ratio for natural-sounding harmonics
- `2.414`: Irrational multiplier for complex harmonic content

---

## Chapter 8: Control System Mathematics

### 8.1 Autopilot Heading Control

**Purpose**: Calculates heading adjustments for autopilot course corrections.

**Formula**:
```
heading_error = target_heading - current_heading

# Normalize to [-180, 180] range
if heading_error > 180:
    heading_error -= 360
elif heading_error < -180:
    heading_error += 360

# Proportional control with limited rate
max_turn_rate = 2.0  # degrees per second
heading_adjustment = clamp(heading_error * 0.5, -max_turn_rate, max_turn_rate)
```

**Variables**:
- `target_heading`: Desired compass heading
- `current_heading`: Current compass heading
- `0.5`: Proportional gain factor
- `2.0`: Maximum turn rate limit

### 8.2 Altitude Hold Control

**Purpose**: Manages vertical speed for altitude hold autopilot mode.

**Formula**:
```
altitude_error = target_altitude - current_altitude
target_vertical_speed = clamp(altitude_error * 0.1, -500, 500)

vs_error = target_vertical_speed - current_vertical_speed
elevator_adjustment = vs_error * 0.02
```

**Variables**:
- Altitudes in feet
- Vertical speeds in feet per minute
- `0.1`: Altitude-to-vertical-speed gain
- `0.02`: Vertical speed control gain

### 8.3 Approach Value Function

**Purpose**: Smoothly transitions values toward targets with realistic response rates.

**Formula**:
```
def approach_value(current, target, rate):
    difference = target - current
    if abs(difference) < 0.001:
        return 0.0
    
    max_change = rate * dt
    if abs(difference) <= max_change:
        return difference
    else:
        return max_change * sign(difference)
```

**Variables**:
- `current`: Current value
- `target`: Target value
- `rate`: Maximum rate of change per second
- `dt`: Time step in seconds

---

## Chapter 9: Environmental and Weather Modeling

### 9.1 Sinusoidal Wind Variation

**Purpose**: Creates natural wind direction changes using trigonometric functions.

**Formula**:
```
wind_direction += sin(simulation_time * 0.01) * 0.1
```

**Variables**:
- `simulation_time`: Total elapsed simulation time
- `0.01`: Frequency scaling factor (very slow oscillation)
- `0.1`: Amplitude in degrees per time step

### 9.2 Temperature Lapse Rate

**Purpose**: Models temperature decrease with altitude using standard atmosphere.

**Formula**:
```
temperature_at_altitude = sea_level_temp + (altitude * lapse_rate)
lapse_rate = -0.00356  # °F per foot (standard atmosphere)
```

**Variables**:
- `sea_level_temp`: Temperature at sea level (°F)
- `altitude`: Height above sea level (feet)
- `-0.00356`: Standard atmospheric lapse rate

**Example**: At 10,000 feet with sea level temp 59°F:
```
temperature = 59 + (10000 * -0.00356) = 59 - 35.6 = 23.4°F
```

---

## Chapter 10: Geometric Projections and Coordinate Systems

### 10.1 Mercator Map Projection

**Purpose**: Converts latitude/longitude to pixel coordinates for map display.

**Formula**:
```
map_x = (longitude + 180) * (map_width / 360)
map_y = (90 - latitude) * (map_height / 180)
```

**Variables**:
- `longitude`: Longitude in degrees (-180 to +180)
- `latitude`: Latitude in degrees (-90 to +90)
- `map_width, map_height`: Map dimensions in pixels

**Example**: Position 40°N 74°W on 640×320 map:
```
map_x = (-74 + 180) * (640 / 360) = 106 * 1.778 = 188.4 pixels
map_y = (90 - 40) * (320 / 180) = 50 * 1.778 = 88.9 pixels
```

### 10.2 Screen to Logical Coordinate Conversion

**Purpose**: Converts screen mouse coordinates to logical game coordinates.

**Formula**:
```
scale_x = screen_width / 320.0
scale_y = screen_height / 320.0
logical_x = screen_x / scale_x
logical_y = screen_y / scale_y
```

**Variables**:
- `320.0`: Fixed logical resolution
- Screen dimensions vary with window size

**Example**: 800×600 window, mouse at (400, 300):
```
scale_x = 800 / 320 = 2.5
scale_y = 600 / 320 = 1.875
logical_x = 400 / 2.5 = 160
logical_y = 300 / 1.875 = 160
```

---

## Chapter 11: Digital Signal Processing

### 11.1 Phase Accumulator for Continuous Audio

**Purpose**: Maintains phase continuity across audio buffer boundaries.

**Formula**:
```
phase_increment = 2π * frequency / sample_rate
new_phase = (old_phase + phase_increment * samples) % (2π)
```

**Variables**:
- `frequency`: Signal frequency in Hz
- `sample_rate`: Audio sample rate (22050 Hz)
- `samples`: Number of samples in current buffer

### 11.2 Linear Interpolation for Smooth Transitions

**Purpose**: Smoothly blends between audio levels or control values.

**Formula**:
```
interpolated_value = start_value + (end_value - start_value) * fraction
fraction = current_step / total_steps
```

**Variables**:
- `fraction`: Interpolation parameter (0.0 to 1.0)
- Linear blend between start and end values

---

## Appendices

### Appendix A: Mathematical Constants Used

- **π (Pi)**: 3.14159... (circular motion, waves, harmonics)
- **e (Euler's number)**: 2.71828... (exponential decay, atmospheric models)
- **Golden Ratio φ**: 1.61803... (harmonic ratios in audio synthesis)
- **√2**: 1.41421... (geometric relationships)
- **Earth's Radius**: 3440.065 nautical miles (navigation calculations)
- **Standard Atmosphere Scale Height**: 29,000 feet (pressure/density models)

### Appendix B: Unit Conversions

- **Degrees to Radians**: `radians = degrees * π / 180`
- **Radians to Degrees**: `degrees = radians * 180 / π`
- **Knots to Degrees/Second**: `deg_per_sec = knots / 3600 / 60`
- **RPM to Hz**: `frequency = rpm / 60`
- **Feet to Meters**: `meters = feet * 0.3048`
- **Nautical Miles to Statute Miles**: `statute = nautical * 1.15078`

### Appendix C: Common Error Bounds and Tolerances

- **Angle Normalization**: Ensure angles stay within [0°, 360°) or [-180°, 180°)
- **Floating Point Comparison**: Use tolerance (e.g., `abs(a - b) < 0.001`)
- **Division by Zero Protection**: Check denominators before division
- **Square Root Domain**: Ensure arguments are non-negative
- **Trigonometric Function Domains**: Check for valid input ranges

---

*This compendium represents the mathematical heart of Airship Zero. Every formula herein has been tested through countless virtual flights, ensuring that the physics of our steam-powered world remain both authentic and engaging. May your calculations be accurate and your flights ever steady.*

**— The Engineering Department**  
**Airship Zero Development Team**
