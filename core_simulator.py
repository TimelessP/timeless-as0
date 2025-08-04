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
            "fuel": {
                "totalCapacity": 550.0,
                "currentLevel": 425.0,
                "flowRate": 12.8,  # Current consumption GPH
                "pumpMode": "auto",  # manual, auto, backup
                "pumps": {
                    "primary": {"enabled": True, "pressure": 22.0},
                    "backup": {"enabled": False, "pressure": 0.0}
                },
                "tanks": {
                    "forward": {
                        "level": 140.0,
                        "capacity": 180.0,
                        "selected": True
                    },
                    "center": {
                        "level": 145.0,
                        "capacity": 190.0,
                        "selected": True
                    },
                    "aft": {
                        "level": 140.0,
                        "capacity": 180.0,
                        "selected": True
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
        self._update_engine(sim_dt)
        self._update_navigation(sim_dt)
        self._update_fuel_system(sim_dt)
        self._update_electrical_system(sim_dt)
        self._update_environment(sim_dt)
        self._update_systems_monitoring(sim_dt)
        
    def _update_engine(self, dt: float):
        """Update engine simulation"""
        engine = self.game_state["engine"]
        
        if not engine["running"]:
            # Engine is off - RPM decays
            engine["rpm"] = max(0, engine["rpm"] - 500 * dt)
            engine["manifoldPressure"] = 14.7  # Atmospheric pressure
            engine["fuelFlow"] = 0.0
            return
            
        # Engine is running - simulate performance
        controls = engine["controls"]
        
        # Calculate target RPM based on throttle and prop settings
        max_rpm = 2800.0
        target_rpm = controls["throttle"] * max_rpm * controls["propeller"]
        
        # RPM response (gradual change)
        rpm_diff = target_rpm - engine["rpm"]
        engine["rpm"] += rpm_diff * 2.0 * dt  # 2 second time constant
        
        # Manifold pressure correlates with throttle
        engine["manifoldPressure"] = 14.7 + (controls["throttle"] * 15.0)
        
        # Fuel flow based on throttle and mixture
        base_flow = controls["throttle"] * 18.0  # Max ~18 GPH
        mixture_efficiency = 0.7 + (controls["mixture"] * 0.3)  # 70-100% efficiency
        engine["fuelFlow"] = base_flow * mixture_efficiency
        
        # Temperature simulation (simplified)
        ambient_temp = self.game_state["environment"]["weather"]["temperature"]
        load_factor = controls["throttle"]
        
        target_oil_temp = ambient_temp + 100 + (load_factor * 80)  # °F
        target_cht = ambient_temp + 180 + (load_factor * 140)     # °F
        target_egt = 800 + (load_factor * 650)                   # °F
        
        # Gradual temperature changes
        temp_rate = 10.0 * dt  # 10 degrees per second max change
        engine["oilTemperature"] += self._approach_value(
            engine["oilTemperature"], target_oil_temp, temp_rate
        )
        engine["cylinderHeadTemp"] += self._approach_value(
            engine["cylinderHeadTemp"], target_cht, temp_rate
        )
        engine["exhaustGasTemp"] += self._approach_value(
            engine["exhaustGasTemp"], target_egt, temp_rate * 2
        )
        
        # Oil pressure correlates with RPM
        engine["oilPressure"] = 20 + (engine["rpm"] / 2800.0) * 55
        
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
        
        # Thrust from engine (simplified)
        if engine["running"]:
            thrust_factor = engine["controls"]["throttle"]
            base_airspeed = 85.0
            target_airspeed = base_airspeed * (0.3 + thrust_factor * 0.7)
        else:
            target_airspeed = motion["indicatedAirspeed"] * 0.95  # Gradual decrease
            
        # Airspeed changes
        airspeed_diff = target_airspeed - motion["indicatedAirspeed"]
        motion["indicatedAirspeed"] += airspeed_diff * 1.0 * dt
        
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
            if not hasattr(autopilot, "lastRudderAdjust"):
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
        """Update fuel consumption and management"""
        fuel = self.game_state["fuel"]
        engine = self.game_state["engine"]
        
        if engine["running"] and engine["fuelFlow"] > 0:
            # Consume fuel
            fuel_consumed = engine["fuelFlow"] * dt / 3600.0  # Convert GPH to gallons per second
            
            # Consume from selected tanks proportionally
            selected_tanks = [name for name, tank in fuel["tanks"].items() if tank["selected"]]
            if selected_tanks:
                fuel_per_tank = fuel_consumed / len(selected_tanks)
                for tank_name in selected_tanks:
                    tank = fuel["tanks"][tank_name]
                    tank["level"] = max(0, tank["level"] - fuel_per_tank)
                    
            # Update total fuel level
            fuel["currentLevel"] = sum(tank["level"] for tank in fuel["tanks"].values())
            
        # Update fuel pressure based on pumps and tank levels
        if fuel["pumpMode"] == "auto":
            fuel["pumps"]["primary"]["enabled"] = fuel["currentLevel"] > 10.0
        elif fuel["pumpMode"] == "manual":
            # Manual mode - pump states controlled by user
            pass
            
        # Calculate fuel pressure
        if fuel["pumps"]["primary"]["enabled"]:
            fuel["pumps"]["primary"]["pressure"] = 22.0
        else:
            fuel["pumps"]["primary"]["pressure"] *= 0.95  # Decay without pump
            
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
            self.game_state["navigation"]["mode"] = mode
            
    def toggle_battery(self, battery: str = "A"):
        """Toggle battery switch"""
        battery_key = f"batteryBus{battery}"
        if battery_key in self.game_state["electrical"]:
            battery_obj = self.game_state["electrical"][battery_key]
            battery_obj["switch"] = not battery_obj["switch"]
            
    def toggle_fuel_pump_mode(self):
        """Toggle fuel pump mode"""
        fuel = self.game_state["fuel"]
        current_mode = fuel["pumpMode"]
        modes = ["manual", "auto", "backup"]
        current_index = modes.index(current_mode) if current_mode in modes else 0
        fuel["pumpMode"] = modes[(current_index + 1) % len(modes)]
        
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
        autopilot = self.game_state["navigation"]["autopilot"]
        autopilot["engaged"] = not autopilot["engaged"]
        # If disengaging, turn off all modes
        if not autopilot["engaged"]:
            for mode in ["headingHold", "altitudeHold", "airspeedHold", "verticalSpeedHold"]:
                autopilot[mode] = False


# Global simulator instance
_simulator = None

def get_simulator() -> CoreSimulator:
    """Get the global simulator instance"""
    global _simulator
    if _simulator is None:
        _simulator = CoreSimulator()
    return _simulator
