"""
Core Simulator for Airship Zero
Centralized game state management and physics simulation
"""
import json
import time
import math
from typing import Dict, Any, Optional, Tuple


class CoreSimulator:
    """
    Centralized simulator core that manages all game state and physics.
    All scenes reference this single source of truth.
    """
    
    def __init__(self):
        self.game_state = self._create_initial_game_state()
        self.last_update_time = time.time()
        self.total_sim_time = 0.0
        self.running = False
        
    def _create_initial_game_state(self) -> Dict[str, Any]:
        """Create the initial game state with all systems"""
        return {
            "gameInfo": {
                "version": "1.0.0",
                "created": time.time(),
                "lastSaved": time.time(),
                "totalFlightTime": 0.0,
                "sessionTime": 0.0,
                "paused": False
            },
            "navigation": {
                "position": {
                    "latitude": 40.7128,  # NYC area
                    "longitude": -74.0060,
                    "altitude": 1250.0,
                    "heading": 45.0,
                    "track": 45.0
                },
                "motion": {
                    "indicatedAirspeed": 85.0,
                    "trueAirspeed": 88.2,
                    "groundSpeed": 82.5,
                    "verticalSpeed": 0.0,
                    "pitch": 0.0,
                    "roll": 0.0,
                    "yaw": 0.0,
                    "rateOfTurn": 0.0  # degrees per second
                },
                "controls": {
                    "rudder": 0.0,  # -30 to +30 degrees
                    "elevator": 0.0,  # -20 to +20 degrees  
                    "ailerons": 0.0   # -25 to +25 degrees
                },
                "targets": {
                    "altitude": 1250.0,
                    "heading": 45.0,
                    "airspeed": 85.0
                },
                "mode": "manual",  # manual, heading_hold, altitude_hold, route_follow
                "autopilot": {
                    "engaged": False,
                    "headingHold": False,
                    "altitudeHold": False,
                    "airspeedHold": False,
                    "verticalSpeedHold": False,
                    "targetRudder": 0.0,  # Autopilot's target rudder position
                    "headingError": 0.0,  # Current heading error for autopilot
                    "turnRate": 0.0       # Autopilot's target turn rate
                },
                "route": {
                    "active": False,
                    "waypoints": [],
                    "currentWaypoint": 0,
                    "crossTrackError": 0.0
                }
            },
            "engine": {
                "running": True,
                "rpm": 2650.0,
                "targetRpm": 2650.0,
                "manifoldPressure": 24.5,
                "fuelFlow": 12.8,
                "oilPressure": 65.0,
                "oilTemperature": 185.0,
                "cylinderHeadTemp": 320.0,
                "exhaustGasTemp": 1450.0,
                "fuelPressure": 22.0,
                "controls": {
                    "throttle": 0.75,
                    "mixture": 0.85,
                    "propeller": 0.80
                },
                "propellerFeathered": False,
                "emergencyShutdown": False,
                "startupSequence": False
            },
            "electrical": {
                "batteryBusA": {
                    "switch": True,
                    "voltage": 12.6,
                    "current": 8.5,
                    "capacity": 24.0,  # Amp-hours
                    "remaining": 20.5
                },
                "batteryBusB": {
                    "switch": True,
                    "voltage": 12.5,
                    "current": 6.2,
                    "capacity": 24.0,
                    "remaining": 21.8
                },
                "alternator": {
                    "online": True,
                    "voltage": 14.2,
                    "current": 15.0,
                    "maxOutput": 60.0
                },
                "loads": {
                    "instruments": 3.2,
                    "navigation": 2.8,
                    "lighting": 4.5,
                    "radio": 1.8
                }
            },
            # Reworked fuel system: two tanks (forward & aft), each with transfer and dump pumps
            "fuel": {
                "totalCapacity": 360.0,  # 180 + 180
                "currentLevel": 280.0,
                "flowRate": 12.8,  # Current engine consumption GPH (informational)
                "engineFeedCut": False,  # True if no tank is feeding
                "tanks": {
                    "forward": {
                        "level": 140.0,
                        "capacity": 180.0,
                        "feed": True,          # Feeding engine
                        "transferRate": 0.0,   # 0..1 user slider -> transfers OUT to aft
                        "dumpRate": 0.0        # 0..1 user slider -> dumps overboard
                    },
                    "aft": {
                        "level": 140.0,
                        "capacity": 180.0,
                        "feed": True,          # Feeding engine
                        "transferRate": 0.0,   # OUT to forward
                        "dumpRate": 0.0
                    }
                }
            },
            "environment": {
                "weather": {
                    "temperature": 15.0,  # Celsius
                    "pressure": 29.92,    # inHg
                    "humidity": 65.0,     # %
                    "visibility": 10.0,   # statute miles
                    "windSpeed": 8.0,     # knots
                    "windDirection": 270.0  # degrees
                },
                "time": {
                    "utc": time.time(),
                    "local": time.time(),
                    "timezone": "UTC",
                    "daylight": True
                }
            },
            "systems": {
                "warnings": [],
                "alerts": [],
                "failures": []
            }
        }
    
    def start_new_game(self):
        """Initialize a new game session"""
        self.game_state = self._create_initial_game_state()
        self.running = True
        self.last_update_time = time.time()
        self.total_sim_time = 0.0
        
    def pause_simulation(self):
        """Pause the simulation"""
        self.game_state["gameInfo"]["paused"] = True
        
    def resume_simulation(self):
        """Resume the simulation"""
        self.game_state["gameInfo"]["paused"] = False
        self.last_update_time = time.time()
        
    def save_game(self, filename: str = "saved_game.json") -> bool:
        """Save current game state to file"""
        try:
            # Update save timestamp
            self.game_state["gameInfo"]["lastSaved"] = time.time()
            
            with open(filename, 'w') as f:
                json.dump(self.game_state, f, indent=2)
            print(f"✅ Game saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to save game: {e}")
            return False
            
    def load_game(self, filename: str = "saved_game.json") -> bool:
        """Load game state from file"""
        try:
            with open(filename, 'r') as f:
                loaded_state = json.load(f)
            
            # Validate the loaded state has required structure
            if "gameInfo" in loaded_state and "navigation" in loaded_state:
                # Migration: if old multi-tank layout present, collapse to forward/aft
                if "fuel" in loaded_state and "tanks" in loaded_state["fuel"]:
                    fuel_block = loaded_state["fuel"]
                    tanks = fuel_block.get("tanks", {})
                    if not ("forward" in tanks and "aft" in tanks and "feed" in tanks.get("forward", {})):
                        # Build new structure using forward & aft from available
                        forward_level = 0.0
                        aft_level = 0.0
                        if "forward" in tanks:
                            forward_level = tanks["forward"].get("level", 0.0)
                        elif "center" in tanks:
                            forward_level = tanks["center"].get("level", 0.0)
                        if "aft" in tanks:
                            aft_level = tanks["aft"].get("level", 0.0)
                        fuel_block["tanks"] = {
                            "forward": {
                                "level": forward_level,
                                "capacity": 180.0,
                                "feed": True,
                                "transferRate": 0.0,
                                "dumpRate": 0.0
                            },
                            "aft": {
                                "level": aft_level,
                                "capacity": 180.0,
                                "feed": True,
                                "transferRate": 0.0,
                                "dumpRate": 0.0
                            }
                        }
                        fuel_block["totalCapacity"] = 360.0
                        fuel_block["currentLevel"] = forward_level + aft_level
                        fuel_block.pop("pumpMode", None)
                        fuel_block.pop("pumps", None)
                self.game_state = loaded_state
                self.running = True
                self.last_update_time = time.time()
                print(f"✅ Game loaded from {filename}")
                return True
            else:
                print(f"❌ Invalid save file format: {filename}")
                return False
                
        except FileNotFoundError:
            print(f"❌ Save file not found: {filename}")
            return False
        except Exception as e:
            print(f"❌ Failed to load game: {e}")
            return False
            
    def has_saved_game(self, filename: str = "saved_game.json") -> bool:
        """Check if a saved game file exists"""
        import os
        return os.path.exists(filename)
        
    def update(self, real_dt: float):
        """
        Update the simulation state
        real_dt: real-world time delta in seconds
        """
        if self.game_state["gameInfo"]["paused"] or not self.running:
            return
            
        # Simulation time step (could be scaled for faster/slower simulation)
        sim_dt = real_dt
        self.total_sim_time += sim_dt
        
        # Update game time
        self.game_state["gameInfo"]["sessionTime"] += sim_dt
        self.game_state["gameInfo"]["totalFlightTime"] += sim_dt
        
        # Update all systems
        self._update_fuel_system(sim_dt)
        self._update_engine(sim_dt)
        self._update_navigation(sim_dt)
        self._update_fuel_system(sim_dt)
        self._update_electrical_system(sim_dt)
        self._update_environment(sim_dt)
        self._update_systems_monitoring(sim_dt)
        
    def _update_engine(self, dt: float):
        """Update engine simulation"""
        engine = self.game_state["engine"]
        fuel = self.game_state["fuel"]
        
        if not engine["running"]:
            # Engine is off - RPM decays
            engine["rpm"] = max(0, engine["rpm"] - 500 * dt)
            engine["manifoldPressure"] = 14.7  # Atmospheric pressure
            engine["fuelFlow"] = 0.0
            engine["fuelPressure"] = 0.0
            return
            
        # Check fuel availability and pressure
        fuel_available = not fuel.get("engineFeedCut", False)
        total_fuel = fuel.get("currentLevel", 0.0)
        
        # Calculate fuel pressure based on fuel availability and tank levels
        if fuel_available and total_fuel > 0.1:
            # Normal fuel pressure when tanks are feeding
            base_fuel_pressure = 22.0
            # Reduce pressure if fuel is very low
            if total_fuel < 20.0:
                pressure_factor = total_fuel / 20.0  # Gradual pressure drop
                engine["fuelPressure"] = base_fuel_pressure * pressure_factor
            else:
                engine["fuelPressure"] = base_fuel_pressure
        else:
            # No fuel pressure when tanks not feeding or empty
            engine["fuelPressure"] = max(0.0, engine["fuelPressure"] - 50.0 * dt)
        
        # Engine is running - simulate performance based on fuel availability
        controls = engine["controls"]
        navigation = self.game_state["navigation"]
        altitude = navigation["position"]["altitude"]
        
        # Calculate mixture effectiveness based on altitude and mixture setting
        # Optimal mixture changes with altitude (leaner needed at higher altitudes)
        optimal_mixture_for_altitude = 0.85 - (altitude / 10000.0) * 0.15  # 0.85 at sea level, 0.70 at 10k ft
        optimal_mixture_for_altitude = max(0.50, min(0.95, optimal_mixture_for_altitude))
        
        # Calculate mixture power factor (bell curve around optimal)
        mixture_deviation = abs(controls["mixture"] - optimal_mixture_for_altitude)
        if mixture_deviation <= 0.05:  # Within 5% of optimal
            mixture_power_factor = 1.0
        elif mixture_deviation <= 0.15:  # Within 15% of optimal
            mixture_power_factor = 1.0 - (mixture_deviation - 0.05) * 2.0  # Linear falloff
        else:  # More than 15% off optimal
            mixture_power_factor = 0.8 - (mixture_deviation - 0.15) * 1.5  # Steeper falloff
        mixture_power_factor = max(0.3, mixture_power_factor)  # Minimum 30% power
        

        # Calculate target RPM based on throttle, mixture, and fuel availability
        max_rpm = 2800.0
        # Prop pitch acts as a load: low pitch = low load, high pitch = high load
        # At low pitch, engine can reach max RPM; at high pitch, RPM may drop if engine can't overcome load
        # We'll model load as: load_factor = 0.5 + prop_pitch * 0.5 (0.5 at flat, 1.0 at max pitch)
        prop_pitch = controls["propeller"]
        load_factor = 0.5 + prop_pitch * 0.5
        # Engine can reach max RPM at low load, but at high load, only a fraction
        base_target_rpm = controls["throttle"] * max_rpm * mixture_power_factor
        achievable_rpm = base_target_rpm / load_factor

        # Reduce achievable RPM if fuel pressure is low or fuel is cut
        fuel_factor = 1.0
        if engine["fuelPressure"] < 10.0:
            fuel_factor = engine["fuelPressure"] / 10.0  # Severe power loss below 10 PSI
        elif not fuel_available:
            fuel_factor = 0.0  # Complete power loss when fuel cut

        target_rpm = achievable_rpm * fuel_factor

        # RPM response (gradual change, faster decay when fuel-starved)
        rpm_diff = target_rpm - engine["rpm"]
        if fuel_factor < 1.0:
            # Faster RPM decay when fuel-starved
            rpm_rate = 5.0 if rpm_diff < 0 else 2.0
        else:
            # Slightly slower response at high load
            rpm_rate = 2.0 / load_factor
        engine["rpm"] += rpm_diff * rpm_rate * dt
        engine["rpm"] = max(0.0, engine["rpm"])  # Ensure non-negative RPM

        # Automatically shut down engine if RPM drops to zero
        if engine["rpm"] <= 0.0:
            engine["running"] = False
        
        # Manifold pressure correlates with throttle, altitude, and fuel availability
        # Atmospheric pressure decreases with altitude
        atmospheric_pressure = 29.92 * math.exp(-altitude / 29000.0)  # Rough altitude correction
        base_manifold = atmospheric_pressure + (controls["throttle"] * 15.0)
        engine["manifoldPressure"] = base_manifold * fuel_factor * mixture_power_factor
        
        # Fuel flow based on throttle, mixture, and actual engine performance
        if fuel_available and engine["fuelPressure"] > 5.0:
            # Base fuel flow scales with throttle and actual RPM
            base_flow = controls["throttle"] * 18.0  # Max ~18 GPH at full throttle
            
            # Mixture affects fuel flow directly - higher mixture = more fuel
            mixture_flow_factor = 0.6 + (controls["mixture"] * 0.8)  # 60-140% flow based on mixture
            
            # Reduce flow if fuel pressure is low
            pressure_factor = min(1.0, engine["fuelPressure"] / 22.0)
            
            # Also factor in actual RPM vs target (engine under stress uses more fuel)
            rpm_factor = engine["rpm"] / max(1.0, target_rpm) if target_rpm > 0 else 0.0
            
            engine["fuelFlow"] = base_flow * mixture_flow_factor * pressure_factor * rpm_factor
        else:
            # No fuel flow when fuel cut or very low pressure
            engine["fuelFlow"] = max(0.0, engine["fuelFlow"] - 25.0 * dt)
        
        # Temperature simulation (affected by fuel availability, engine load, and mixture)
        ambient_temp = self.game_state["environment"]["weather"]["temperature"]
        load_factor = controls["throttle"] * fuel_factor
        
        # Mixture significantly affects exhaust gas temperature
        # Lean mixture (low mixture setting) runs much hotter
        mixture_temp_factor = 2.0 - controls["mixture"]  # Lean = hot, Rich = cooler
        
        # Temperatures drop when engine is fuel-starved or not running properly
        if fuel_factor < 0.5 or engine["rpm"] < 1000:
            # Engine cooling down due to fuel starvation or low RPM
            target_oil_temp = ambient_temp + 50 + (load_factor * 40)
            target_cht = ambient_temp + 100 + (load_factor * 80)
            target_egt = 400 + (load_factor * 400)
        else:
            # Normal operating temperatures with mixture effects
            target_oil_temp = ambient_temp + 100 + (load_factor * 80)  # °F
            target_cht = ambient_temp + 180 + (load_factor * 140)     # °F
            # EGT strongly affected by mixture - lean mixtures run much hotter
            base_egt = 800 + (load_factor * 650)
            target_egt = base_egt * mixture_temp_factor
            target_egt = min(1800, target_egt)  # Cap at realistic maximum
        
        # Gradual temperature changes (faster cooling when fuel-starved)
        temp_rate = 15.0 * dt if fuel_factor < 0.5 else 10.0 * dt
        engine["oilTemperature"] += self._approach_value(
            engine["oilTemperature"], target_oil_temp, temp_rate
        )
        engine["cylinderHeadTemp"] += self._approach_value(
            engine["cylinderHeadTemp"], target_cht, temp_rate
        )
        engine["exhaustGasTemp"] += self._approach_value(
            engine["exhaustGasTemp"], target_egt, temp_rate * 2
        )
        
        # Oil pressure correlates with RPM and engine health
        base_oil_pressure = 20 + (engine["rpm"] / 2800.0) * 55
        # Reduce oil pressure if engine is struggling
        if fuel_factor < 0.8:
            oil_pressure_factor = 0.5 + (fuel_factor * 0.5)  # 50-100% oil pressure
            engine["oilPressure"] = base_oil_pressure * oil_pressure_factor
        else:
            engine["oilPressure"] = base_oil_pressure
        
    def _update_navigation(self, dt: float):
        """Update navigation and flight dynamics"""
        nav = self.game_state["navigation"]
        engine = self.game_state["engine"]
        env = self.game_state["environment"]["weather"]
        
        # Simple flight dynamics
        position = nav["position"]
        motion = nav["motion"]
        controls = nav["controls"]
        
        # Rudder physics - convert rudder angle to rate of turn
        rudder_angle = controls["rudder"]  # -30 to +30 degrees
        airspeed_factor = motion["indicatedAirspeed"] / 85.0  # Normalize to typical cruise speed
        
        # Rate of turn based on rudder (simplified aerodynamics)
        max_turn_rate = 3.0  # degrees per second at full rudder, cruise speed
        motion["rateOfTurn"] = (rudder_angle / 30.0) * max_turn_rate * airspeed_factor
        
        # Apply rate of turn to heading
        position["heading"] += motion["rateOfTurn"] * dt
        position["heading"] = position["heading"] % 360
        
        # Realistic thrust calculation based on actual engine performance
        if engine["running"]:
            # Calculate thrust based on actual engine RPM and propeller efficiency
            max_rpm = 2800.0
            current_rpm = engine["rpm"]
            rpm_factor = current_rpm / max_rpm
            # Propeller efficiency curve (peak around 75% RPM)
            if rpm_factor < 0.2:
                prop_efficiency = rpm_factor * 2.0  # Poor efficiency at very low RPM
            elif rpm_factor < 0.75:
                prop_efficiency = 0.4 + (rpm_factor - 0.2) * 1.1  # Rising efficiency
            else:
                prop_efficiency = 1.0 - (rpm_factor - 0.75) * 0.4  # Declining past peak
            # Base thrust from throttle setting and RPM
            throttle_setting = engine["controls"]["throttle"]
            base_thrust = throttle_setting * rpm_factor * prop_efficiency
            # Further reduce thrust if fuel flow is insufficient
            expected_fuel_flow = throttle_setting * 18.0 * 0.85  # Expected flow at mixture
            actual_fuel_flow = engine["fuelFlow"]
            fuel_flow_factor = min(1.0, actual_fuel_flow / max(0.1, expected_fuel_flow))
            # Final thrust factor combining all effects
            thrust_factor = base_thrust * fuel_flow_factor
            # Calculate target airspeed based on thrust
            base_airspeed = 85.0  # Cruise airspeed at full power
            min_airspeed = 15.0   # Minimum flying speed (stall region)
            target_airspeed = min_airspeed + (base_airspeed - min_airspeed) * thrust_factor
            
        else:
            # Engine off - aircraft becomes a glider with significant drag
            # Apply continuous deceleration due to drag until the aircraft stops
            current_speed = motion["indicatedAirspeed"]
            if current_speed > 0.5:  # Above minimum threshold
                # Exponential decay with a lower bound that allows reaching zero
                target_airspeed = max(0.0, current_speed * 0.92 - 0.1)  # Subtract constant to reach zero
            else:
                # Below threshold - stop completely
                target_airspeed = 0.0
            
        # Airspeed changes with realistic acceleration/deceleration rates
        airspeed_diff = target_airspeed - motion["indicatedAirspeed"]
        
        # Different response rates for acceleration vs deceleration
        if airspeed_diff > 0:
            # Acceleration - slower, depends on available thrust
            accel_rate = 0.8 * dt if engine["running"] else 0.1 * dt
        else:
            # Deceleration - faster due to drag
            decel_rate = 1.5 * dt
            accel_rate = decel_rate
            
        motion["indicatedAirspeed"] += airspeed_diff * accel_rate
        motion["indicatedAirspeed"] = max(0.0, motion["indicatedAirspeed"])  # Prevent negative airspeed
        
        # True airspeed (simplified - just add a bit for altitude/temp)
        motion["trueAirspeed"] = motion["indicatedAirspeed"] * 1.02
        
        # Ground speed affected by wind
        wind_component = env["windSpeed"] * math.cos(
            math.radians(position["heading"] - env["windDirection"])
        )
        motion["groundSpeed"] = motion["trueAirspeed"] + wind_component
        
        # Position updates based on ground speed and heading
        if motion["groundSpeed"] > 0:
            # Convert knots to degrees per second (very approximate)
            degrees_per_second = motion["groundSpeed"] / 3600.0 / 60.0
            
            heading_rad = math.radians(position["heading"])
            lat_change = degrees_per_second * math.cos(heading_rad) * dt
            lon_change = degrees_per_second * math.sin(heading_rad) * dt / math.cos(math.radians(position["latitude"]))
            
            position["latitude"] += lat_change
            position["longitude"] += lon_change
            
        # Autopilot handling
        if nav["autopilot"]["engaged"]:
            self._update_autopilot(dt)
            
    def _update_autopilot(self, dt: float):
        """Update autopilot systems"""
        nav = self.game_state["navigation"]
        autopilot = nav["autopilot"]
        position = nav["position"]
        targets = nav["targets"]
        controls = nav["controls"]
        motion = nav["motion"]
        
        # Heading hold with discrete rudder control (like manual input)
        if autopilot["headingHold"]:
            heading_error = targets["heading"] - position["heading"]
            # Normalize to -180 to +180
            while heading_error > 180:
                heading_error -= 360
            while heading_error < -180:
                heading_error += 360
                
            autopilot["headingError"] = heading_error
            
            # Discrete rudder adjustments based on heading error
            abs_error = abs(heading_error)
            current_rudder = controls["rudder"]
            
            # Determine target rudder adjustment based on error magnitude
            if abs_error > 20:
                # Large error: aggressive correction
                target_rudder_step = 2.0 if heading_error > 0 else -2.0
            elif abs_error > 10:
                # Medium error: moderate correction
                target_rudder_step = 2.0 if heading_error > 0 else -2.0
            elif abs_error > 2:
                # Small error: gentle correction
                target_rudder_step = 2.0 if heading_error > 0 else -2.0
            else:
                # Very close to target: center the rudder
                if abs(current_rudder) >= 2.0:
                    target_rudder_step = -2.0 if current_rudder > 0 else 2.0
                else:
                    target_rudder_step = -current_rudder  # Final centering step
            
            # Apply discrete rudder adjustment at autopilot rate (slower than manual)
            # Autopilot makes adjustments every 0.5 seconds instead of instantly
            if "lastRudderAdjust" not in autopilot:
                autopilot["lastRudderAdjust"] = 0.0
                
            autopilot["lastRudderAdjust"] += dt
            
            if autopilot["lastRudderAdjust"] >= 0.5:  # Adjust every 0.5 seconds
                # Apply the discrete step
                new_rudder = current_rudder + target_rudder_step
                controls["rudder"] = max(-30.0, min(30.0, new_rudder))
                autopilot["lastRudderAdjust"] = 0.0
                
                # Store autopilot debug info
                autopilot["targetRudderStep"] = target_rudder_step
                autopilot["turnRate"] = target_rudder_step / 2.0  # Approximate turn rate
                
        # Altitude hold
        if autopilot["altitudeHold"]:
            altitude_error = targets["altitude"] - position["altitude"]
            climb_rate = altitude_error * 0.1  # feet per second
            climb_rate = max(-500, min(500, climb_rate))  # Limit climb rate
            position["altitude"] += climb_rate * dt
            motion["verticalSpeed"] = climb_rate * 60  # Convert to fpm
            
    def _update_fuel_system(self, dt: float):
        """Update two-tank fuel system: feed, transfer, dump, and effect on attitude/speed"""
        fuel = self.game_state["fuel"]
        engine = self.game_state["engine"]
        nav_motion = self.game_state["navigation"]["motion"]

        forward = fuel["tanks"]["forward"]
        aft = fuel["tanks"]["aft"]

        # Engine consumption only if at least one tank feeding
        feed_tanks = [t for t in (forward, aft) if t["feed"] and t["level"] > 0.01]
        fuel["engineFeedCut"] = len(feed_tanks) == 0
        if engine["running"] and not fuel["engineFeedCut"]:
            per_tank = (engine["fuelFlow"] * dt / 3600.0) / len(feed_tanks)
            for tank in feed_tanks:
                tank["level"] = max(0.0, tank["level"] - per_tank)
        elif engine["running"] and fuel["engineFeedCut"]:
            # Starved engine: rapidly lose RPM & fuelFlow
            engine["rpm"] = max(0.0, engine["rpm"] - 800.0 * dt)
            engine["fuelFlow"] = max(0.0, engine["fuelFlow"] - 30.0 * dt)

        # Transfer pumps: rate scale (transferRate 0..1) * maxTransferGPH
        # Max rate empties 180g tank in 60 seconds: 180g / (60s / 3600s/h) = 10,800 GPH
        max_transfer_gph = 10800.0  # High flow rate for rapid tank-to-tank transfers
        # Forward -> Aft
        if forward["transferRate"] > 0 and forward["level"] > 0.01 and aft["level"] < aft["capacity"] - 0.01:
            gal = min(forward["level"], (forward["transferRate"] * max_transfer_gph) * dt / 3600.0)
            # Don't overfill aft
            gal = min(gal, aft["capacity"] - aft["level"])
            forward["level"] -= gal
            aft["level"] += gal
        # Aft -> Forward
        if aft["transferRate"] > 0 and aft["level"] > 0.01 and forward["level"] < forward["capacity"] - 0.01:
            gal = min(aft["level"], (aft["transferRate"] * max_transfer_gph) * dt / 3600.0)
            gal = min(gal, forward["capacity"] - forward["level"])
            aft["level"] -= gal
            forward["level"] += gal

        # Dump pumps: remove fuel overboard (same 60-second emptying rate)
        max_dump_gph = 10800.0  # Match transfer rate for consistent emptying time
        if forward["dumpRate"] > 0 and forward["level"] > 0.01:
            dump = min(forward["level"], (forward["dumpRate"] * max_dump_gph) * dt / 3600.0)
            forward["level"] -= dump
        if aft["dumpRate"] > 0 and aft["level"] > 0.01:
            dump = min(aft["level"], (aft["dumpRate"] * max_dump_gph) * dt / 3600.0)
            aft["level"] -= dump

        # Clamp levels
        forward["level"] = max(0.0, min(forward["capacity"], forward["level"]))
        aft["level"] = max(0.0, min(aft["capacity"], aft["level"]))

        # Update aggregate fuel value
        fuel["currentLevel"] = forward["level"] + aft["level"]

        # Balance & attitude effects: pitch based on difference
        # Difference ratio (-1..+1) (aft heavy positive -> nose up) we want forward heavy nose down maybe.
        diff = aft["level"] - forward["level"]  # +ve means aft heavier
        max_diff = forward["capacity"]  # scale reference
        imbalance_ratio = max(-1.0, min(1.0, diff / max_diff))
        # Max +/-10 deg pitch
        target_pitch = imbalance_ratio * 10.0
        # Smooth pitch change
        current_pitch = nav_motion.get("pitch", 0.0)
        pitch_diff = target_pitch - current_pitch
        nav_motion["pitch"] = current_pitch + pitch_diff * min(1.0, 2.0 * dt)

        # Aerodynamic drag penalty for imbalance: reduce indicated airspeed
        base_speed = nav_motion.get("indicatedAirspeed", 0.0)
        penalty_factor = 1.0 - (abs(imbalance_ratio) * 0.15)  # up to 15% loss
        nav_motion["indicatedAirspeed"] = base_speed * penalty_factor
        # True airspeed recalculated next nav update; we tweak here only indicated
            
    def _update_electrical_system(self, dt: float):
        """Update electrical system simulation"""
        electrical = self.game_state["electrical"]
        engine = self.game_state["engine"]
        
        # Calculate total electrical load
        total_load = sum(electrical["loads"].values())
        
        # Alternator output when engine running
        if engine["running"] and engine["rpm"] > 1000:
            alternator = electrical["alternator"]
            alternator["online"] = True
            # Output varies with RPM
            rpm_factor = min(1.0, engine["rpm"] / 2000.0)
            alternator["current"] = min(alternator["maxOutput"], total_load * 1.2) * rpm_factor
            alternator["voltage"] = 14.2 if rpm_factor > 0.8 else 12.8
        else:
            electrical["alternator"]["online"] = False
            electrical["alternator"]["current"] = 0.0
            electrical["alternator"]["voltage"] = 0.0
            
        # Battery discharge/charge
        net_current = electrical["alternator"]["current"] - total_load
        
        for battery_name in ["batteryBusA", "batteryBusB"]:
            battery = electrical[battery_name]
            if battery["switch"]:
                if net_current > 0:
                    # Charging
                    charge_rate = min(net_current / 2, 10.0)  # Max 10A charge rate
                    battery["remaining"] = min(battery["capacity"], 
                                             battery["remaining"] + charge_rate * dt / 3600.0)
                    battery["voltage"] = 12.6 if battery["remaining"] > battery["capacity"] * 0.8 else 12.3
                else:
                    # Discharging
                    discharge_rate = abs(net_current) / 2  # Split load between batteries
                    battery["remaining"] = max(0, battery["remaining"] - discharge_rate * dt / 3600.0)
                    
                    # Voltage drops as battery depletes
                    charge_percent = battery["remaining"] / battery["capacity"]
                    if charge_percent > 0.5:
                        battery["voltage"] = 12.6
                    elif charge_percent > 0.2:
                        battery["voltage"] = 12.3
                    else:
                        battery["voltage"] = 11.8
                        
                battery["current"] = discharge_rate if net_current < 0 else 0
                
    def _update_environment(self, dt: float):
        """Update environmental conditions"""
        env = self.game_state["environment"]
        
        # Update time
        env["time"]["utc"] += dt
        env["time"]["local"] = env["time"]["utc"]  # Simplified
        
        # Simple weather changes (very gradual)
        weather = env["weather"]
        
        # Wind can shift slightly
        weather["windDirection"] += (math.sin(self.total_sim_time * 0.01) * 0.1)
        weather["windDirection"] = weather["windDirection"] % 360
        
    def _update_systems_monitoring(self, dt: float):
        """Monitor systems and generate warnings/alerts"""
        systems = self.game_state["systems"]
        engine = self.game_state["engine"]
        fuel = self.game_state["fuel"]
        electrical = self.game_state["electrical"]
        
        # Clear old warnings
        systems["warnings"] = []
        systems["alerts"] = []
        
        # Engine warnings
        if engine["running"]:
            if engine["oilPressure"] < 25:
                systems["warnings"].append("LOW OIL PRESSURE")
            if engine["oilTemperature"] > 240:
                systems["warnings"].append("HIGH OIL TEMPERATURE")
            if engine["cylinderHeadTemp"] > 400:
                systems["warnings"].append("HIGH CYLINDER HEAD TEMP")
                
        # Fuel warnings
        if fuel["currentLevel"] < 50:
            systems["warnings"].append("LOW FUEL")
        if fuel["currentLevel"] < 20:
            systems["alerts"].append("CRITICAL FUEL")
            
        # Electrical warnings
        for battery_name in ["batteryBusA", "batteryBusB"]:
            battery = electrical[battery_name]
            if battery["switch"] and battery["remaining"] < 5:
                systems["warnings"].append(f"LOW BATTERY {battery_name[-1]}")
                
    def _approach_value(self, current: float, target: float, rate: float) -> float:
        """Helper to gradually approach a target value"""
        diff = target - current
        if abs(diff) <= rate:
            return diff
        return rate if diff > 0 else -rate
        
    def get_state(self) -> Dict[str, Any]:
        """Get the current game state (read-only access)"""
        return self.game_state.copy()
        
    def set_engine_control(self, control: str, value: float):
        """Set engine control position"""
        if control in ["throttle", "mixture", "propeller"]:
            self.game_state["engine"]["controls"][control] = max(0.0, min(1.0, value))
            
    def toggle_engine(self):
        """Toggle engine on/off"""
        engine = self.game_state["engine"]
        if engine["running"]:
            engine["running"] = False
        else:
            engine["running"] = True
            engine["emergencyShutdown"] = False
            
    def set_autopilot_target(self, parameter: str, value: float):
        """Set autopilot target values"""
        targets = self.game_state["navigation"]["targets"]
        if parameter in targets:
            targets[parameter] = value
            
    def toggle_autopilot_mode(self, mode: str):
        """Toggle autopilot modes"""
        autopilot = self.game_state["navigation"]["autopilot"]
        if mode in autopilot:
            autopilot[mode] = not autopilot[mode]
            autopilot["engaged"] = any(autopilot[key] for key in ["headingHold", "altitudeHold", "airspeedHold"])
            
    def set_nav_mode(self, mode: str):
        """Set navigation mode"""
        if mode in ["manual", "heading_hold", "altitude_hold", "route_follow"]:
            nav = self.game_state["navigation"]
            nav["mode"] = mode
            
            # Navigation mode just sets the mode - autopilot engagement is separate
            # The pilot must manually engage the autopilot using the AP button
            
    def toggle_battery(self, battery: str = "A"):
        """Toggle battery switch"""
        battery_key = f"batteryBus{battery}"
        if battery_key in self.game_state["electrical"]:
            battery_obj = self.game_state["electrical"][battery_key]
            battery_obj["switch"] = not battery_obj["switch"]
            
    def toggle_fuel_pump_mode(self):
        """Toggle fuel pump mode"""
        # Legacy - no-op after refactor
        pass

    # --- New Fuel Control Interface ---
    def set_tank_feed(self, tank: str, feed: bool):
        if tank in self.game_state["fuel"]["tanks"]:
            self.game_state["fuel"]["tanks"][tank]["feed"] = bool(feed)

    def set_transfer_rate(self, tank: str, rate: float):
        if tank in self.game_state["fuel"]["tanks"]:
            self.game_state["fuel"]["tanks"][tank]["transferRate"] = max(0.0, min(1.0, rate))

    def set_dump_rate(self, tank: str, rate: float):
        if tank in self.game_state["fuel"]["tanks"]:
            self.game_state["fuel"]["tanks"][tank]["dumpRate"] = max(0.0, min(1.0, rate))
        
    def adjust_rudder(self, degrees: float):
        """Adjust rudder position by the specified degrees (manual control)"""
        nav = self.game_state["navigation"]
        controls = nav["controls"]
        
        # Only allow manual rudder in manual mode
        if nav.get("mode", "manual") == "manual":
            # Adjust rudder by the specified amount
            new_rudder = controls["rudder"] + degrees
            
            # Clamp to realistic limits (-30 to +30 degrees)
            controls["rudder"] = max(-30.0, min(30.0, new_rudder))
        
    def apply_rudder_input(self, input_strength: float):
        """Apply continuous rudder input (for autopilot use)"""
        nav = self.game_state["navigation"]
        
        # Set rudder directly (used by autopilot)
        max_rudder = 30.0  # Maximum rudder deflection in degrees
        target_rudder = input_strength * max_rudder
        
        # Apply rudder input with some smoothing
        current_rudder = nav["controls"]["rudder"]
        rudder_rate = 60.0  # degrees per second rudder movement rate
        
        # Move rudder towards target
        if abs(target_rudder - current_rudder) > 0.1:
            if target_rudder > current_rudder:
                nav["controls"]["rudder"] = min(target_rudder, current_rudder + rudder_rate * 0.1)
            else:
                nav["controls"]["rudder"] = max(target_rudder, current_rudder - rudder_rate * 0.1)
        else:
            nav["controls"]["rudder"] = target_rudder
                
    def toggle_main_autopilot(self):
        """Toggle main autopilot engagement"""
        nav = self.game_state["navigation"]
        autopilot = nav["autopilot"]
        current_mode = nav.get("mode", "manual")
        
        if autopilot["engaged"]:
            # Disengage autopilot - turn off all modes
            autopilot["engaged"] = False
            autopilot["headingHold"] = False
            autopilot["altitudeHold"] = False
        else:
            # Engage autopilot based on current navigation mode
            autopilot["engaged"] = True
            
            if current_mode == "heading_hold":
                autopilot["headingHold"] = True
                autopilot["altitudeHold"] = False
                # Set current heading as target if not already set
                if nav["targets"]["heading"] == 0:  # Default value
                    nav["targets"]["heading"] = nav["position"]["heading"]
            elif current_mode == "altitude_hold":
                autopilot["headingHold"] = False
                autopilot["altitudeHold"] = True
                # Set current altitude as target if not already set
                if nav["targets"]["altitude"] == 0:  # Default value
                    nav["targets"]["altitude"] = nav["position"]["altitude"]
            elif current_mode == "route_follow":
                autopilot["headingHold"] = True
                autopilot["altitudeHold"] = True
            else:
                # Manual mode - autopilot disengaged
                autopilot["engaged"] = False


# Global simulator instance
_simulator = None

def get_simulator() -> CoreSimulator:
    """Get the global simulator instance"""
    global _simulator
    if _simulator is None:
        _simulator = CoreSimulator()
    return _simulator
