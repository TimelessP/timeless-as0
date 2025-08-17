"""
Sound Module for Airship Zero
Real-time procedural audio generation for propeller and engine sounds
"""
import pygame
import numpy as np
import math
import time
from typing import Dict, Any, Optional
from core_simulator import get_simulator

class AirshipSoundEngine:
    """
    Real-time procedural audio engine for airship sounds.
    Generates propeller, engine, and wind audio based on simulator state.
    """
    
    def __init__(self, simulator, sample_rate: int = 22050, buffer_size: int = 512):
        """
        Initialize the sound engine.
        
        Args:
            simulator: Reference to core_simulator instance for real-time data
            sample_rate: Audio sample rate in Hz (22050 for good quality/performance balance)
            buffer_size: Audio buffer size in samples (smaller = lower latency, higher CPU)
        """
        self.simulator = simulator
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        
        # Initialize pygame mixer for audio output
        pygame.mixer.pre_init(
            frequency=sample_rate,
            size=-16,  # 16-bit signed
            channels=2,  # Stereo
            buffer=buffer_size
        )
        pygame.mixer.init()
        
        # Audio generation state
        self.phase_accumulator = 0.0  # For continuous phase across buffers  
        self.phase_harmonic2 = 0.0    # Phase for 2nd harmonic
        self.phase_harmonic3 = 0.0    # Phase for 3rd harmonic
        self.propeller_blade1_phase = 0.0  # Phase for first propeller blade
        self.propeller_blade2_phase = math.pi  # Second blade offset by 180° (π radians)
        
        # Individual cylinder phases for 6-cylinder radial engine
        # Each cylinder fires once per engine revolution, evenly spaced
        # Track absolute time positions for each cylinder's next firing
        self.cylinder_next_firing_times = []
        for i in range(6):
            # Each cylinder starts at its phase offset in the engine cycle
            cylinder_time_offset = i / 6.0  # 0/6, 1/6, 2/6, etc. of engine cycle
            self.cylinder_next_firing_times.append(cylinder_time_offset)
        
        self.engine_time_accumulator = 0.0  # Track absolute engine time
        
        self.rumble_phase = 0.0       # Phase for engine rumble
        self.noise_phase = 0.0        # Phase for wind noise generation
        self.last_update_time = time.time()
        
        # Audio parameters (will be updated from simulator)
        self.current_rpm = 0.0
        self.current_pitch = 0.0
        self.current_mixture = 0.0
        self.current_airspeed = 0.0
        self.is_hull_filter = True
        self.volume = 0.5  # Master volume (0.0 to 1.0)
        self.is_engine_running = True  # Engine state
        self.is_simulation_paused = False  # Simulation pause state
        
        # Individual audio track controls for testing and debugging
        self.track_controls = {
            # Propeller tracks
            "propeller_blade1": {"enabled": True, "volume": 1.0},
            "propeller_blade2": {"enabled": True, "volume": 1.0},
            "propeller_harmonics": {"enabled": True, "volume": 1.0},
            
            # Engine combustion tracks (individual cylinders)
            "engine_cylinder0": {"enabled": True, "volume": 1.0},
            "engine_cylinder1": {"enabled": True, "volume": 1.0},
            "engine_cylinder2": {"enabled": True, "volume": 1.0},
            "engine_cylinder3": {"enabled": True, "volume": 1.0},
            "engine_cylinder4": {"enabled": True, "volume": 1.0},
            "engine_cylinder5": {"enabled": True, "volume": 1.0},
            
            # Engine rumble tracks
            "engine_rumble_fundamental": {"enabled": True, "volume": 1.0},
            "engine_rumble_harmonic": {"enabled": True, "volume": 1.0},
            
            # Wind noise tracks
            "wind_low_freq": {"enabled": True, "volume": 1.0},
            "wind_low_harmonic1": {"enabled": True, "volume": 1.0},
            "wind_low_harmonic2": {"enabled": True, "volume": 1.0},
            "wind_mid_freq": {"enabled": True, "volume": 1.0},
            "wind_mid_harmonic1": {"enabled": True, "volume": 1.0},
            "wind_mid_harmonic2": {"enabled": True, "volume": 1.0},
            "wind_high_freq": {"enabled": True, "volume": 1.0},
            "wind_gusting": {"enabled": True, "volume": 1.0},
        }
        
        # Engine configuration
        self.engine_cylinders = 6  # 6-cylinder radial engine
        
        # Sound channel for continuous playback
        self.sound_channel = None
        
        print(f"🔊 AirshipSoundEngine initialized:")
        print(f"   Sample rate: {sample_rate} Hz")
        print(f"   Buffer size: {buffer_size} samples")
        print(f"   Buffer duration: {buffer_size/sample_rate*1000:.1f} ms")
        
    def update_from_simulator(self):
        """Update audio parameters from current simulator state"""
        if not self.simulator:
            return
            
        state = self.simulator.get_state()
        engine = state.get("engine", {})
        navigation = state.get("navigation", {})
        motion = navigation.get("motion", {})
        controls = engine.get("controls", {})
        game_info = state.get("gameInfo", {})
        settings = state.get("settings", {})
        
        # Check simulation and engine state
        self.is_simulation_paused = game_info.get("paused", False) or not self.simulator.running
        self.is_engine_running = engine.get("running", False) and self.simulator.running
        self.volume = settings.get("soundVolume", 0.5)  # Default to 50% if not set
        
        # Always read airspeed (needed for wind noise regardless of engine state)
        self.current_airspeed = motion.get("indicatedAirspeed", 0.0)
        
        # Extract engine-relevant parameters only if engine is running
        if self.is_engine_running:
            self.current_rpm = engine.get("rpm", 0.0)
            self.current_pitch = controls.get("propeller", 0.0)  # 0.0 to 1.0
            self.current_mixture = controls.get("mixture", 0.0)  # 0.0 to 1.0
        else:
            # Engine off - no engine sound parameters
            self.current_rpm = 0.0
            self.current_pitch = 0.0
            self.current_mixture = 0.0
        
        # Debug: Print updated values
        # print(f"Audio update: RPM={self.current_rpm:.0f}, Pitch={self.current_pitch:.2f}, Mix={self.current_mixture:.2f}, Speed={self.current_airspeed:.1f}")
        
    def generate_propeller_wave(self, duration: float) -> np.ndarray:
        """
        Generate propeller sound wave based on two-blade propeller physics.
        
        COMPLETELY REWRITTEN FOR ARTIFACT ELIMINATION:
        - Pure sinusoidal basis to eliminate all sharp transitions
        - Smooth amplitude modulation for blade character
        - No rectification or clipping operations
        - Optimized for clean, artifact-free audio
        """
        num_samples = int(duration * self.sample_rate)
        samples = np.zeros(num_samples, dtype=np.float32)
        
        if self.current_rpm <= 50.0:  # Effectively silent below 50 RPM
            return samples
            
        # Calculate propeller rotation frequency
        prop_frequency = self.current_rpm / 60.0  # Hz (one full rotation)
        
        # Propeller pitch affects amplitude - higher pitch = more air displacement
        pitch_amplitude = 0.15 + (self.current_pitch * 0.35)  # 0.15 to 0.5 amplitude (reduced for cleaner sound)
        
        dt = 1.0 / self.sample_rate
        omega = 2 * math.pi * prop_frequency
        
        # Generate completely smooth propeller sound using pure sinusoidal components
        for i in range(num_samples):
            t = i * dt
            
            # Calculate continuous phases for each blade
            blade1_phase = self.propeller_blade1_phase + omega * t
            blade2_phase = self.propeller_blade2_phase + omega * t
            
            total_sample = 0.0
            
            # Blade 1 - smooth sinusoidal with gentle amplitude modulation
            if self.track_controls["propeller_blade1"]["enabled"]:
                # Pure sine wave with smooth amplitude envelope
                blade1_base = math.sin(blade1_phase)
                # Gentle amplitude modulation to create blade character (no sharp edges)
                blade1_envelope = 0.5 + 0.5 * math.sin(blade1_phase * 2)  # Creates 2 pulses per rotation
                blade1_smooth = blade1_base * blade1_envelope * 0.4  # Reduced amplitude
                
                total_sample += blade1_smooth * self.track_controls["propeller_blade1"]["volume"]
            
            # Blade 2 - similar processing but phase-shifted
            if self.track_controls["propeller_blade2"]["enabled"]:
                blade2_base = math.sin(blade2_phase)
                blade2_envelope = 0.5 + 0.5 * math.sin(blade2_phase * 2)
                blade2_smooth = blade2_base * blade2_envelope * 0.4
                
                total_sample += blade2_smooth * self.track_controls["propeller_blade2"]["volume"]
            
            # Harmonics - very gentle harmonic content
            if self.track_controls["propeller_harmonics"]["enabled"]:
                # Pure harmonic frequencies without any clipping or rectification
                harmonic1 = 0.05 * math.sin(blade1_phase * 3)  # 3rd harmonic
                harmonic2 = 0.03 * math.sin(blade2_phase * 3)
                harmonic3 = 0.02 * math.sin((blade1_phase + blade2_phase) * 1.5)  # Beat frequency
                
                total_sample += (harmonic1 + harmonic2 + harmonic3) * self.track_controls["propeller_harmonics"]["volume"]
            
            # Apply pitch amplitude scaling
            samples[i] = total_sample * pitch_amplitude
        
        # Apply very gentle crossfade at buffer boundaries
        fade_samples = min(16, num_samples // 8)  # Shorter fade: 16 samples (~0.7ms)
        
        if fade_samples > 0:
            # Gentle fade in
            fade_in = np.sin(np.linspace(0, math.pi/2, fade_samples)) ** 2  # Smooth sine-squared fade
            samples[:fade_samples] *= fade_in
            
            # Gentle fade out
            fade_out = np.cos(np.linspace(0, math.pi/2, fade_samples)) ** 2  # Smooth cosine-squared fade
            samples[-fade_samples:] *= fade_out
        
        # Update phase accumulators for continuous playback
        self.propeller_blade1_phase += omega * duration
        self.propeller_blade1_phase = self.propeller_blade1_phase % (2 * math.pi)
        
        self.propeller_blade2_phase += omega * duration
        self.propeller_blade2_phase = self.propeller_blade2_phase % (2 * math.pi)
        
        # Final DC offset removal (should be minimal with pure sine waves)
        dc_offset = np.mean(samples)
        samples = samples - dc_offset
        
        return samples
        
    def generate_engine_wave(self, duration: float) -> np.ndarray:
        """
        Generate engine firing sound for 6-cylinder radial engine.
        
        Each cylinder fires once per engine revolution, creating discrete combustion 
        pressure waves that are placed in a timeline. These are not continuous tones
        but discrete events with fast attack and slower decay phases.
        """
        num_samples = int(duration * self.sample_rate)
        samples = np.zeros(num_samples, dtype=np.float32)
        
        if self.current_rpm <= 50.0:  # Effectively silent below 50 RPM
            return samples
            
        # Engine rotation frequency - each cylinder fires once per rotation
        engine_rotation_freq = self.current_rpm / 60.0  # Hz
        engine_period = 1.0 / engine_rotation_freq  # Time for one complete revolution
        
        # Mixture affects amplitude - richer mixture = more power per firing
        mixture_amplitude = 0.03 + (self.current_mixture * 0.1)  # 0.03 to 0.13 amplitude (reduced by ~1/3)
        
        # Combustion pressure wave characteristics (independent of RPM)
        combustion_duration = 0.08  # 80ms combustion event duration
        attack_duration = 0.005     # 5ms fast attack phase
        decay_duration = combustion_duration - attack_duration  # 75ms decay phase
        
        dt = 1.0 / self.sample_rate
        
        # Generate separate audio tracks for each cylinder
        cylinder_tracks = []
        for cylinder_idx in range(6):
            cylinder_track = np.zeros(num_samples, dtype=np.float32)
            
            # Check if this cylinder is enabled
            cylinder_track_name = f"engine_cylinder{cylinder_idx}"
            if not self.track_controls[cylinder_track_name]["enabled"]:
                cylinder_tracks.append(cylinder_track)
                continue
            
            cylinder_volume = self.track_controls[cylinder_track_name]["volume"]
            
            # Calculate when this cylinder should fire within the current buffer
            # Each cylinder fires at a different offset within the engine cycle
            cylinder_cycle_offset = cylinder_idx / 6.0  # 0.0, 0.167, 0.333, 0.5, 0.667, 0.833
            
            # Find the next firing time for this cylinder
            current_engine_cycles = self.engine_time_accumulator / engine_period
            current_cycle_position = current_engine_cycles - math.floor(current_engine_cycles)
            
            # Calculate when this cylinder should fire next
            next_firing_cycle_position = cylinder_cycle_offset
            if next_firing_cycle_position <= current_cycle_position:
                next_firing_cycle_position += 1.0  # Next engine cycle
                
            time_to_next_firing = (next_firing_cycle_position - current_cycle_position) * engine_period
            
            # Generate all firing events for this cylinder within the buffer
            firing_time = time_to_next_firing
            while firing_time < duration + combustion_duration:
                firing_start_sample = int(firing_time * self.sample_rate)
                combustion_samples = int(combustion_duration * self.sample_rate)
                attack_samples = int(attack_duration * self.sample_rate)
                
                # Generate smooth combustion pressure wave for this firing event
                # ARTIFACT ELIMINATION: Use smooth envelope curves without sharp transitions
                for i in range(combustion_samples):
                    sample_idx = firing_start_sample + i
                    if 0 <= sample_idx < num_samples:
                        t_combustion = i / self.sample_rate  # Time within combustion event
                        
                        if t_combustion < attack_duration:
                            # Smooth attack phase using sine-based curve instead of sharp exponential
                            attack_progress = t_combustion / attack_duration
                            # Use sine curve for smooth attack without sharp derivatives
                            envelope = math.sin(attack_progress * math.pi / 2) ** 1.2  # Gentle S-curve
                        else:
                            # Smooth decay phase with gentler exponential curve
                            decay_progress = (t_combustion - attack_duration) / decay_duration
                            # Use smoother exponential decay with cosine taper
                            exponential_decay = math.exp(-decay_progress * 2.5)  # Gentler than 3.0
                            cosine_taper = math.cos(decay_progress * math.pi / 2) ** 0.8  # Smooth taper
                            envelope = exponential_decay * cosine_taper
                        
                        # Apply gentle end taper instead of hard cutoff
                        # Smooth the last 20% of the combustion event to prevent sharp edges
                        end_taper_threshold = 0.8  # Start taper at 80% through event
                        event_progress = t_combustion / combustion_duration
                        if event_progress > end_taper_threshold:
                            taper_progress = (event_progress - end_taper_threshold) / (1.0 - end_taper_threshold)
                            # Smooth cosine taper to zero
                            end_taper = math.cos(taper_progress * math.pi / 2) ** 2
                            envelope *= end_taper
                        
                        # Create pressure wave with realistic combustion character
                        pressure_wave = envelope * mixture_amplitude
                        
                        # Apply smooth polarity variation instead of hard switching
                        # Use continuous phase-based polarity for smooth DC balance
                        polarity_phase = (cylinder_idx * 0.7 + firing_time * 0.3) * math.pi
                        polarity_factor = math.sin(polarity_phase)  # Smooth bipolar variation
                        pressure_wave *= polarity_factor
                        
                        # Add cylinder-specific character with smooth modulation
                        cylinder_phase = self.engine_time_accumulator * 2.1 + cylinder_idx * 1.3
                        cylinder_variation = 1.0 + 0.05 * math.sin(cylinder_phase)  # Reduced variation
                        pressure_wave *= cylinder_variation
                        
                        # Apply cylinder volume control
                        pressure_wave *= cylinder_volume
                        
                        # Use additive synthesis with smooth blending
                        cylinder_track[sample_idx] += pressure_wave
                
                # Next firing event for this cylinder (one engine cycle later)
                firing_time += engine_period
            
            # Apply gentle smoothing filter to each cylinder track to eliminate any remaining artifacts
            if len(cylinder_track) > 1 and np.max(np.abs(cylinder_track)) > 1e-6:
                # Light low-pass filtering to smooth sharp transitions
                alpha = 0.06  # Gentle filtering coefficient
                filtered_track = np.zeros_like(cylinder_track)
                filtered_track[0] = cylinder_track[0]
                
                for i in range(1, len(cylinder_track)):
                    filtered_track[i] = filtered_track[i-1] * alpha + cylinder_track[i] * (1.0 - alpha)
                
                cylinder_track = filtered_track
            
            cylinder_tracks.append(cylinder_track)
        
        # Combine all cylinder tracks (linear addition is natural here since each track
        # already handles its own overlaps with max())
        combined_engine_wave = np.zeros(num_samples, dtype=np.float32)
        for track in cylinder_tracks:
            combined_engine_wave += track
        
        # Add low-frequency rumble (engine block vibration) with polarity variation
        rumble_fundamental = np.zeros(num_samples, dtype=np.float32)
        rumble_harmonic = np.zeros(num_samples, dtype=np.float32)
        
        for i in range(num_samples):
            t = i * dt
            rumble_phase = 2 * math.pi * engine_rotation_freq * (self.engine_time_accumulator + t)
            
            # Fundamental rumble frequency
            if self.track_controls["engine_rumble_fundamental"]["enabled"]:
                fundamental = 0.15 * math.sin(rumble_phase)
                rumble_fundamental[i] = fundamental * self.track_controls["engine_rumble_fundamental"]["volume"]
            
            # Harmonic rumble frequency
            if self.track_controls["engine_rumble_harmonic"]["enabled"]:
                harmonic = 0.08 * math.sin(rumble_phase * 1.5)
                rumble_harmonic[i] = harmonic * self.track_controls["engine_rumble_harmonic"]["volume"]
        
        # Add rumble components to the combined wave
        combined_engine_wave += rumble_fundamental + rumble_harmonic
        
        # Apply enhanced crossfade at buffer boundaries to eliminate discontinuities
        fade_samples = min(32, num_samples // 6)  # 32 samples (~1.5ms) or 1/6 buffer
        
        if fade_samples > 0:
            # Smooth sine-squared fade in at start (only if not the first buffer)
            if self.engine_time_accumulator > 0:
                fade_in = np.sin(np.linspace(0, math.pi/2, fade_samples)) ** 2
                combined_engine_wave[:fade_samples] *= fade_in
            
            # Smooth cosine-squared fade out at end
            fade_out = np.cos(np.linspace(0, math.pi/2, fade_samples)) ** 2
            combined_engine_wave[-fade_samples:] *= fade_out
        
        # Update engine time accumulator for continuous playback
        self.engine_time_accumulator += duration
        
        # Copy to output samples
        samples = combined_engine_wave
        
        # Remove DC offset to prevent pumping artifacts
        dc_offset = np.mean(samples)
        samples = samples - dc_offset
        
        return samples
        
    def generate_wind_noise(self, duration: float) -> np.ndarray:
        """
        Generate realistic wind noise based on airspeed.
        
        REWRITTEN FOR REALISTIC TURBULENCE:
        Wind noise comes from many small turbulence sources on the hull - each creates
        a soft pressure pulse at different frequencies and phases. The result is a 
        chaotic but smooth combination of many overlapping sine waves that construct
        and destruct naturally, creating broadband noise without sharp artifacts.
        """
        num_samples = int(duration * self.sample_rate)
        
        if self.current_airspeed <= 1.0:
            return np.zeros(num_samples, dtype=np.float32)
        
        # Airspeed affects both amplitude and frequency content
        speed_factor = min(self.current_airspeed / 100.0, 1.0)  # Normalize to 0-1
        wind_amplitude = speed_factor * 0.20  # Reduced amplitude for more realistic level
        
        dt = 1.0 / self.sample_rate
        
        # Create multiple turbulence generators - many small sources of varying frequencies
        # Each represents turbulence from different hull features (rigging, edges, surfaces)
        
        # Low frequency rumble: Large-scale hull vibration and pressure waves
        low_freq_base = 15.0 + speed_factor * 25.0  # 15-40 Hz base
        low_turbulence = np.zeros(num_samples, dtype=np.float32)
        low_harmonic1 = np.zeros(num_samples, dtype=np.float32)
        low_harmonic2 = np.zeros(num_samples, dtype=np.float32)
        
        # Mid frequency hiss: Medium-scale turbulence from hull details
        mid_freq_base = 80.0 + speed_factor * 120.0  # 80-200 Hz base
        mid_turbulence = np.zeros(num_samples, dtype=np.float32)
        mid_harmonic1 = np.zeros(num_samples, dtype=np.float32)
        mid_harmonic2 = np.zeros(num_samples, dtype=np.float32)
        
        # High frequency content: Small-scale turbulence (reduced frequency range)
        high_freq_base = 200.0 + speed_factor * 300.0  # 200-500 Hz (much lower than before)
        high_turbulence = np.zeros(num_samples, dtype=np.float32)
        
        # Generate chaotic turbulence using multiple interfering sine waves
        for i in range(num_samples):
            t = i * dt
            
            # === LOW FREQUENCY TURBULENCE ===
            if self.track_controls["wind_low_freq"]["enabled"]:
                # Create 5 interfering low-frequency sources with slightly different frequencies
                low_sum = 0.0
                for osc in range(5):
                    freq_offset = low_freq_base * (1.0 + osc * 0.07)  # 7% frequency spread
                    phase_offset = self.noise_phase + osc * 1.3  # Different phase for each oscillator
                    low_sum += math.sin(2 * math.pi * freq_offset * t + phase_offset)
                
                # Average and apply slow envelope modulation for natural variation
                envelope = 1.0 + 0.3 * math.sin(2 * math.pi * 0.4 * t + self.noise_phase)
                low_turbulence[i] = (low_sum / 5.0) * envelope * 0.15 * self.track_controls["wind_low_freq"]["volume"]
            
            if self.track_controls["wind_low_harmonic1"]["enabled"]:
                # Low harmonic with 3 interfering sources
                low_harm1_sum = 0.0
                for osc in range(3):
                    freq = low_freq_base * 1.6 * (1.0 + osc * 0.05)
                    phase = self.noise_phase * 1.7 + osc * 0.9
                    low_harm1_sum += math.sin(2 * math.pi * freq * t + phase)
                
                low_harmonic1[i] = (low_harm1_sum / 3.0) * 0.08 * self.track_controls["wind_low_harmonic1"]["volume"]
                
            if self.track_controls["wind_low_harmonic2"]["enabled"]:
                # Second low harmonic with 3 interfering sources  
                low_harm2_sum = 0.0
                for osc in range(3):
                    freq = low_freq_base * 2.3 * (1.0 + osc * 0.04)
                    phase = self.noise_phase * 2.1 + osc * 1.1
                    low_harm2_sum += math.sin(2 * math.pi * freq * t + phase)
                
                low_harmonic2[i] = (low_harm2_sum / 3.0) * 0.05 * self.track_controls["wind_low_harmonic2"]["volume"]
            
            # === MID FREQUENCY TURBULENCE ===
            if self.track_controls["wind_mid_freq"]["enabled"]:
                # Create 8 interfering mid-frequency sources (more complexity)
                mid_sum = 0.0
                for osc in range(8):
                    freq_offset = mid_freq_base * (1.0 + osc * 0.12)  # 12% frequency spread
                    phase_offset = self.noise_phase * 1.4 + osc * 0.7
                    # Add slow amplitude modulation to each oscillator
                    amp_mod = 1.0 + 0.2 * math.sin(2 * math.pi * (0.3 + osc * 0.1) * t + phase_offset)
                    mid_sum += math.sin(2 * math.pi * freq_offset * t + phase_offset) * amp_mod
                
                mid_turbulence[i] = (mid_sum / 8.0) * 0.12 * speed_factor * self.track_controls["wind_mid_freq"]["volume"]
            
            if self.track_controls["wind_mid_harmonic1"]["enabled"]:
                # Mid harmonic 1 with 4 interfering sources
                mid_harm1_sum = 0.0
                for osc in range(4):
                    freq = mid_freq_base * 1.8 * (1.0 + osc * 0.08)
                    phase = self.noise_phase * 1.9 + osc * 0.6
                    mid_harm1_sum += math.sin(2 * math.pi * freq * t + phase)
                
                mid_harmonic1[i] = (mid_harm1_sum / 4.0) * 0.08 * speed_factor * self.track_controls["wind_mid_harmonic1"]["volume"]
                
            if self.track_controls["wind_mid_harmonic2"]["enabled"]:
                # Mid harmonic 2 with 4 interfering sources
                mid_harm2_sum = 0.0
                for osc in range(4):
                    freq = mid_freq_base * 2.7 * (1.0 + osc * 0.06)
                    phase = self.noise_phase * 2.3 + osc * 0.8
                    mid_harm2_sum += math.sin(2 * math.pi * freq * t + phase)
                
                mid_harmonic2[i] = (mid_harm2_sum / 4.0) * 0.06 * speed_factor * self.track_controls["wind_mid_harmonic2"]["volume"]
            
            # === HIGH FREQUENCY TURBULENCE ===
            if self.track_controls["wind_high_freq"]["enabled"]:
                # Create 12 interfering high-frequency sources (maximum complexity)
                high_sum = 0.0
                for osc in range(12):
                    freq_offset = high_freq_base * (1.0 + osc * 0.15)  # 15% frequency spread  
                    phase_offset = self.noise_phase * 2.1 + osc * 0.5
                    # Each source has its own envelope modulation
                    env_freq = 0.8 + osc * 0.3  # Different envelope rates
                    envelope = 1.0 + 0.4 * math.sin(2 * math.pi * env_freq * t + phase_offset)
                    high_sum += math.sin(2 * math.pi * freq_offset * t + phase_offset) * envelope
                
                # High frequencies prominent only at higher airspeeds
                high_factor = speed_factor ** 1.5  # More nonlinear response
                high_turbulence[i] = (high_sum / 12.0) * 0.06 * high_factor * self.track_controls["wind_high_freq"]["volume"]
        
        # Combine all turbulence components
        wind_samples = np.zeros(num_samples, dtype=np.float32)
        for i in range(num_samples):
            wind_samples[i] = (
                low_turbulence[i] +      # Always present
                low_harmonic1[i] +
                low_harmonic2[i] +
                mid_turbulence[i] +      # Increases with speed
                mid_harmonic1[i] +
                mid_harmonic2[i] +
                high_turbulence[i]       # Prominent at high speeds
            )
        
        # Apply overall wind amplitude
        wind_samples = wind_samples * wind_amplitude
        
        # Add slow gusting effect (amplitude modulation of the entire mix)
        if self.track_controls["wind_gusting"]["enabled"]:
            gust_frequency = 0.25  # 0.25 Hz gusting (4-second period)
            gust_volume = self.track_controls["wind_gusting"]["volume"]
            for i in range(num_samples):
                t = i * dt
                # Use multiple overlapping gust frequencies for natural variation
                gust1 = math.sin(2 * math.pi * gust_frequency * t + self.noise_phase)
                gust2 = 0.6 * math.sin(2 * math.pi * gust_frequency * 1.3 * t + self.noise_phase * 1.7)
                gust3 = 0.4 * math.sin(2 * math.pi * gust_frequency * 0.7 * t + self.noise_phase * 2.1)
                combined_gust = (gust1 + gust2 + gust3) / 3.0
                gust_factor = 1.0 + 0.25 * combined_gust * gust_volume
                wind_samples[i] *= gust_factor
        
        # Update noise phase for continuous evolution
        self.noise_phase += 2 * math.pi * 0.13 * duration  # Slow phase evolution
        self.noise_phase = self.noise_phase % (2 * math.pi)
        
        return wind_samples
        
    def apply_hull_filter(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply hull filtering effect - low-pass filter to simulate sound dampening.
        
        The airship hull dampens higher frequencies more than lower frequencies.
        """
        if not self.is_hull_filter:
            return audio
            
        # Simple single-pole low-pass filter
        # Cutoff frequency around 2000 Hz (dampens prop blade slap but keeps engine rumble)
        cutoff_freq = 2000.0
        RC = 1.0 / (2 * math.pi * cutoff_freq)
        dt = 1.0 / self.sample_rate
        alpha = dt / (RC + dt)
        
        filtered = np.zeros_like(audio)
        y_prev = 0.0
        
        for i in range(len(audio)):
            y_prev = y_prev + alpha * (audio[i] - y_prev)
            filtered[i] = y_prev
            
        return filtered
        
    def apply_logarithmic_normalization(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply logarithmic normalization ("HDR" audio processing).
        
        This preserves energy and detail at lower amplitudes while preventing
        clipping at higher amplitudes, similar to HDR in visual processing.
        Uses a logarithmic curve that primarily affects signals above 95% amplitude.
        """
        # Find the maximum absolute amplitude in the signal
        max_amplitude = np.max(np.abs(audio))
        
        # If signal is too quiet, skip normalization to avoid noise amplification
        if max_amplitude < 1e-6:
            return audio
        
        # Threshold where logarithmic compression starts to have significant effect
        compression_threshold = 0.95  # 95% of max amplitude
        
        # Apply sign-preserving logarithmic compression
        normalized_audio = np.zeros_like(audio)
        
        for i in range(len(audio)):
            # Normalize to 0-1 range (preserving sign)
            normalized_sample = audio[i] / max_amplitude
            abs_normalized = abs(normalized_sample)
            
            if abs_normalized <= compression_threshold:
                # Below threshold: minimal compression (nearly linear)
                # Use a very gentle curve that's almost 1:1
                compressed_abs = abs_normalized * (1.0 + 0.05 * abs_normalized)  # Very slight boost
            else:
                # Above threshold: strong logarithmic compression
                # Map the range [compression_threshold, 1.0] to [compression_threshold, target_max]
                excess = abs_normalized - compression_threshold
                excess_range = 1.0 - compression_threshold  # 0.05 for 95% threshold
                
                # Apply logarithmic compression to the excess
                # Use log(1 + x) curve scaled to compress the top 5% significantly
                compression_factor = 8.0  # Higher = more aggressive compression of peaks
                compressed_excess = (np.log(1 + excess * compression_factor) / 
                                   np.log(1 + excess_range * compression_factor)) * excess_range * 0.6
                
                compressed_abs = compression_threshold + compressed_excess
            
            # Restore original sign and scale back to appropriate amplitude range
            if normalized_sample >= 0:
                compressed_sample = compressed_abs
            else:
                compressed_sample = -compressed_abs
                
            normalized_audio[i] = compressed_sample * 0.8 * max_amplitude  # Leave headroom for subsequent processing
        
        return normalized_audio
        
    def apply_soft_limiter(self, audio: np.ndarray, threshold: float = 0.85) -> np.ndarray:
        """
        Apply soft limiting to prevent harsh clipping artifacts.
        Uses tanh-based soft clipping for musical distortion characteristics.
        """
        # Soft limiting using tanh function
        # This provides gentle compression above the threshold
        limited = np.tanh(audio / threshold) * threshold
        return limited
        
    def generate_audio_buffer(self, duration: float) -> np.ndarray:
        """
        Generate a complete audio buffer mixing all sound sources.
        
        Args:
            duration: Duration of audio buffer in seconds
            
        Returns:
            Mixed stereo audio buffer as numpy array
        """
        # NOTE: update_from_simulator() should be called by the main game loop,
        # not here, to maintain phase continuity between consecutive buffers
        
        num_samples = int(duration * self.sample_rate)
        
        # If simulation is paused or volume is off, return complete silence
        if self.is_simulation_paused or self.volume <= 0.0:
            stereo_audio = np.zeros((num_samples, 2), dtype=np.float32)
            return stereo_audio
        
        # Generate individual sound components based on engine and motion state
        if self.is_engine_running:
            propeller_audio = self.generate_propeller_wave(duration)
            engine_audio = self.generate_engine_wave(duration)
        else:
            # Engine is off - no propeller or engine sounds
            propeller_audio = np.zeros(num_samples, dtype=np.float32)
            engine_audio = np.zeros(num_samples, dtype=np.float32)
        
        # Wind noise is always generated based on airspeed (independent of engine state)
        wind_audio = self.generate_wind_noise(duration)
        
        # Mix the audio sources
        mixed_audio = propeller_audio + engine_audio + wind_audio
        
        # Apply logarithmic normalization ("HDR" audio) to preserve energy at low amplitudes
        # while preventing clipping at high amplitudes
        mixed_audio = self.apply_logarithmic_normalization(mixed_audio)
        
        # Apply hull filtering if enabled
        if self.is_hull_filter:
            mixed_audio = self.apply_hull_filter(mixed_audio)
        
        # Apply volume control before normalization to preserve phase relationships
        mixed_audio = mixed_audio * self.volume
        
        # Apply soft limiting instead of hard normalization to prevent harsh artifacts
        mixed_audio = self.apply_soft_limiter(mixed_audio, threshold=0.80)
        
        # Convert to stereo (duplicate mono signal)
        stereo_audio = np.zeros((num_samples, 2), dtype=np.float32)
        stereo_audio[:, 0] = mixed_audio  # Left channel
        stereo_audio[:, 1] = mixed_audio  # Right channel
        
        return stereo_audio
        
    def update_audio(self):
        """
        Update audio output - call this regularly from the main game loop.
        
        This method checks if the audio buffer needs refilling and generates
        new audio data when needed. Should be called at least every 50ms
        to prevent audio underruns.
        """
        # Update sound engine parameters from simulator state
        # This is done once per game loop, not per buffer, to maintain phase continuity
        self.update_from_simulator()
        
        current_time = time.time()
        dt = current_time - self.last_update_time
        
        # Generate new audio buffer if needed
        # Buffer duration should be longer than update interval to prevent gaps
        buffer_duration = self.buffer_size / self.sample_rate
        
        if dt >= buffer_duration * 0.5:  # Refill when half empty
            audio_buffer = self.generate_audio_buffer(buffer_duration)
            
            # Convert to pygame-compatible format (16-bit signed integer)
            audio_int16 = (audio_buffer * 32767).astype(np.int16)
            
            # Create pygame sound and play
            try:
                sound = pygame.sndarray.make_sound(audio_int16)
                if self.sound_channel is None or not self.sound_channel.get_busy():
                    self.sound_channel = sound.play()
                else:
                    # Queue the next buffer
                    self.sound_channel.queue(sound)
            except Exception as e:
                print(f"Audio playback error: {e}")
            
            self.last_update_time = current_time
            
    def set_hull_filter(self, enabled: bool):
        """Enable or disable hull filtering effect"""
        self.is_hull_filter = enabled
        
    def set_track_enabled(self, track_name: str, enabled: bool):
        """Enable or disable a specific audio track"""
        if track_name in self.track_controls:
            self.track_controls[track_name]["enabled"] = enabled
        else:
            print(f"Warning: Unknown track '{track_name}'")
            
    def set_track_volume(self, track_name: str, volume: float):
        """Set volume for a specific audio track (0.0 to 1.0)"""
        if track_name in self.track_controls:
            self.track_controls[track_name]["volume"] = max(0.0, min(1.0, volume))
        else:
            print(f"Warning: Unknown track '{track_name}'")
            
    def disable_all_tracks(self):
        """Disable all audio tracks"""
        for track in self.track_controls:
            self.track_controls[track]["enabled"] = False
            
    def enable_all_tracks(self):
        """Enable all audio tracks"""
        for track in self.track_controls:
            self.track_controls[track]["enabled"] = True
            
    def set_track_group_enabled(self, group: str, enabled: bool):
        """Enable/disable groups of tracks"""
        if group == "propeller":
            tracks = ["propeller_blade1", "propeller_blade2", "propeller_harmonics"]
        elif group == "engine_cylinders":
            tracks = [f"engine_cylinder{i}" for i in range(6)]
        elif group == "engine_rumble":
            tracks = ["engine_rumble_fundamental", "engine_rumble_harmonic"]
        elif group == "wind":
            tracks = ["wind_low_freq", "wind_low_harmonic1", "wind_low_harmonic2",
                     "wind_mid_freq", "wind_mid_harmonic1", "wind_mid_harmonic2",
                     "wind_high_freq", "wind_gusting"]
        else:
            print(f"Warning: Unknown track group '{group}'")
            return
            
        for track in tracks:
            self.set_track_enabled(track, enabled)
            
    def get_track_list(self):
        """Get list of all available audio tracks"""
        return list(self.track_controls.keys())
        
    def get_track_info(self):
        """Get current status of all audio tracks"""
        return self.track_controls.copy()
        
    def get_audio_info(self) -> Dict[str, Any]:
        """Get current audio engine status for debugging"""
        # Ensure we have the latest parameters
        self.update_from_simulator()
        
        return {
            "sample_rate": self.sample_rate,
            "buffer_size": self.buffer_size,
            "current_rpm": self.current_rpm,
            "current_pitch": self.current_pitch,
            "current_mixture": self.current_mixture,
            "current_airspeed": self.current_airspeed,
            "hull_filter": self.is_hull_filter,
            "volume": self.volume,
            "engine_running": self.is_engine_running,
            "simulation_paused": self.is_simulation_paused,
            "propeller_freq": (self.current_rpm / 60.0) * 2 if self.current_rpm > 0 else 0,
            "engine_firing_freq": (self.current_rpm / 60.0) if self.current_rpm > 0 else 0  # Each cylinder fires once per rotation
        }


def main():
    """
    Test the AirshipSoundEngine with various engine parameters.
    
    PYGAME INTEGRATION NOTES:
    ========================
    To integrate this sound engine into the main pygame loop:
    
    1. Initialize the sound engine once during game startup:
       sound_engine = AirshipSoundEngine(simulator)
    
    2. Call sound_engine.update_audio() in your main game loop:
       - Place this call after simulator.update(dt)
       - Call it every frame or at least every 50ms
       - No need for separate threading - pygame.mixer handles audio buffering
    
    3. Optional: Add hull filter toggle in settings:
       sound_engine.set_hull_filter(settings.get("hull_filter", True))
    
    4. The sound engine automatically reads from the simulator state,
       so no manual parameter updates are needed.
    
    Example integration in main.py:
    ```python
    # In AirshipApp.__init__():
    self.sound_engine = AirshipSoundEngine(self.simulator)
    
    # In main game loop (after self.update(dt)):
    self.sound_engine.update_audio()
    ```
    
    The sound engine is designed to be lightweight and avoid threading
    by using pygame's built-in audio queuing system.
    """
    
    print("🎵 Testing Airship Sound Engine")
    print("=" * 50)
    
    # Initialize pygame (required for audio)
    pygame.init()
    
    # Create a test simulator with various engine states
    simulator = get_simulator()
    simulator.start_new_game()
    
    # Initialize sound engine
    sound_engine = AirshipSoundEngine(simulator)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Engine Startup",
            "rpm": 1000,
            "throttle": 0.3,
            "mixture": 0.7,
            "propeller": 0.4,
            "airspeed": 0,
            "duration": 3.0
        },
        {
            "name": "Cruise Flight",
            "rpm": 2400,
            "throttle": 0.75,
            "mixture": 0.85,
            "propeller": 0.8,
            "airspeed": 85,
            "duration": 4.0
        },
        {
            "name": "High Power Climb",
            "rpm": 2700,
            "throttle": 1.0,
            "mixture": 0.9,
            "propeller": 0.6,
            "airspeed": 65,
            "duration": 3.0
        },
        {
            "name": "High Speed Descent",
            "rpm": 2200,
            "throttle": 0.4,
            "mixture": 0.7,
            "propeller": 1.0,
            "airspeed": 120,
            "duration": 3.0
        }
    ]
    
    print("Testing audio generation with different engine states...")
    print("Press Ctrl+C to stop\n")
    
    try:
        for scenario in test_scenarios:
            print(f"🔊 {scenario['name']}:")
            print(f"   RPM: {scenario['rpm']}")
            print(f"   Throttle: {scenario['throttle']:.1%}")
            print(f"   Mixture: {scenario['mixture']:.1%}")
            print(f"   Prop Pitch: {scenario['propeller']:.1%}")
            print(f"   Airspeed: {scenario['airspeed']} knots")
            
            # Set simulator state
            engine_state = simulator.game_state["engine"]
            engine_state["rpm"] = scenario["rpm"]
            engine_state["controls"]["throttle"] = scenario["throttle"]
            engine_state["controls"]["mixture"] = scenario["mixture"]
            engine_state["controls"]["propeller"] = scenario["propeller"]
            
            navigation_state = simulator.game_state["navigation"]
            navigation_state["motion"]["indicatedAirspeed"] = scenario["airspeed"]
            
            # Test audio info
            audio_info = sound_engine.get_audio_info()
            print(f"   Propeller freq: {audio_info['propeller_freq']:.1f} Hz")
            print(f"   Engine firing freq: {audio_info['engine_firing_freq']:.1f} Hz")
            
            # Run audio for specified duration
            start_time = time.time()
            end_time = start_time + scenario["duration"]
            
            print(f"   Playing for {scenario['duration']:.1f} seconds...")
            
            while time.time() < end_time:
                sound_engine.update_audio()
                time.sleep(0.05)  # 50ms update interval
            
            print("   ✅ Complete\n")
            time.sleep(0.5)  # Brief pause between scenarios
        
        # Test hull filter toggle
        print("🔧 Testing hull filter...")
        print("   Without hull filter (direct engine sound):")
        sound_engine.set_hull_filter(False)
        
        # Set moderate engine state
        engine_state["rpm"] = 2400
        engine_state["controls"]["throttle"] = 0.75
        navigation_state["motion"]["indicatedAirspeed"] = 85
        
        start_time = time.time()
        while time.time() < start_time + 2.0:
            sound_engine.update_audio()
            time.sleep(0.05)
        
        print("   With hull filter (dampened highs):")
        sound_engine.set_hull_filter(True)
        
        start_time = time.time()
        while time.time() < start_time + 2.0:
            sound_engine.update_audio()
            time.sleep(0.05)
        
        print("   ✅ Hull filter test complete")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    finally:
        pygame.mixer.quit()
        pygame.quit()
        print("\n🏁 Sound engine test complete")


if __name__ == "__main__":
    main()
