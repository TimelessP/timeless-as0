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
        self.engine_phase = 0.0       # Separate phase for engine firing cycles
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
        Generate propeller sound wave based on current RPM and pitch.
        
        Propeller sound is not a pure sine wave - it has harmonics from blade tip vortices
        and pressure pulses. We'll model this as a fundamental frequency with harmonics.
        """
        num_samples = int(duration * self.sample_rate)
        samples = np.zeros(num_samples, dtype=np.float32)
        
        if self.current_rpm <= 50.0:  # Effectively silent below 50 RPM
            return samples
            
        # Calculate propeller frequency (assuming 2-blade prop)
        # Each blade passage creates a pressure pulse
        prop_blades = 2
        prop_frequency = (self.current_rpm / 60.0) * prop_blades  # Hz
        
        # Propeller pitch affects amplitude - higher pitch = more air displacement
        pitch_amplitude = 0.2 + (self.current_pitch * 0.6)  # 0.2 to 0.8 base amplitude
        
        dt = 1.0 / self.sample_rate
        
        # Pre-calculate angular frequency for efficiency
        omega_fundamental = 2 * math.pi * prop_frequency
        omega_harmonic2 = omega_fundamental * 2
        omega_harmonic3 = omega_fundamental * 3
        
        for i in range(num_samples):
            # Calculate phase for this exact sample, continuing from accumulator
            phase_fundamental = self.phase_accumulator + omega_fundamental * (i * dt)
            phase_harmonic2 = self.phase_harmonic2 + omega_harmonic2 * (i * dt)
            phase_harmonic3 = self.phase_harmonic3 + omega_harmonic3 * (i * dt)
            
            # Fundamental frequency (main propeller whoosh)
            fundamental = math.sin(phase_fundamental)
            
            # Add harmonics for realism (reduced amplitudes to minimize boundary artifacts)
            harmonic2 = 0.2 * math.sin(phase_harmonic2)  # Reduced from 0.3 to 0.2
            harmonic3 = 0.1 * math.sin(phase_harmonic3)  # Reduced from 0.15 to 0.1
            
            # Combine with pitch-dependent amplitude
            propeller_wave = (fundamental + harmonic2 + harmonic3) * pitch_amplitude
            
            samples[i] = propeller_wave
        
        # Update all phase accumulators for continuous playback across buffers
        self.phase_accumulator += omega_fundamental * duration
        self.phase_accumulator = self.phase_accumulator % (2 * math.pi)
        
        self.phase_harmonic2 += omega_harmonic2 * duration
        self.phase_harmonic2 = self.phase_harmonic2 % (2 * math.pi)
        
        self.phase_harmonic3 += omega_harmonic3 * duration
        self.phase_harmonic3 = self.phase_harmonic3 % (2 * math.pi)
        
        return samples
        
    def generate_engine_wave(self, duration: float) -> np.ndarray:
        """
        Generate engine firing sound for 6-cylinder radial engine.
        
        Each cylinder fires at a different time, creating sharp pulses with intervals.
        The frequency is 6 times RPM (6 firings per engine revolution).
        """
        num_samples = int(duration * self.sample_rate)
        samples = np.zeros(num_samples, dtype=np.float32)
        
        if self.current_rpm <= 50.0:  # Effectively silent below 50 RPM
            return samples
            
        # Engine firing frequency (6 cylinders, each fires once per revolution)
        firing_frequency = (self.current_rpm / 60.0) * self.engine_cylinders  # Hz
        
        # Mixture affects amplitude - richer mixture = more power per firing
        mixture_amplitude = 0.1 + (self.current_mixture * 0.3)  # 0.1 to 0.4 amplitude
        
        dt = 1.0 / self.sample_rate
        
        for i in range(num_samples):
            t = i * dt
            
            # Calculate continuous firing phase (avoid modulo during buffer generation)
            firing_phase_continuous = self.engine_phase + firing_frequency * t
            firing_phase = firing_phase_continuous % 1.0
            
            # Generate firing pulses with smooth envelope to prevent clicking
            if firing_phase < 0.1:  # Sharp attack (10% of cycle)
                # Smooth attack curve to prevent discontinuities
                attack_factor = firing_phase / 0.1
                firing_amplitude = attack_factor * (2.0 - attack_factor)  # Parabolic curve
            else:  # Exponential decay (90% of cycle)
                decay_factor = (firing_phase - 0.1) / 0.9
                firing_amplitude = math.exp(-decay_factor * 5.0)  # Gentler decay
            
            # Apply mixture-dependent amplitude
            engine_wave = firing_amplitude * mixture_amplitude
            
            # Add low-frequency rumble with continuous phase tracking
            rumble_frequency = self.current_rpm / 60.0
            rumble_phase = self.rumble_phase + 2 * math.pi * rumble_frequency * t
            rumble = 0.1 * math.sin(rumble_phase)
            
            samples[i] = engine_wave + rumble
        
        # Update both engine phases for continuous playback
        self.engine_phase += firing_frequency * duration
        self.engine_phase = self.engine_phase % 1.0
        
        self.rumble_phase += 2 * math.pi * (self.current_rpm / 60.0) * duration
        self.rumble_phase = self.rumble_phase % (2 * math.pi)
        
        return samples
        
    def generate_wind_noise(self, duration: float) -> np.ndarray:
        """
        Generate realistic wind noise based on airspeed.
        
        Wind noise is generated using multiple frequency bands with turbulent
        modulation to simulate air flowing over the airship hull and rigging.
        """
        num_samples = int(duration * self.sample_rate)
        
        if self.current_airspeed <= 1.0:
            return np.zeros(num_samples, dtype=np.float32)
        
        # Airspeed affects both amplitude and frequency content
        speed_factor = min(self.current_airspeed / 100.0, 1.0)  # Normalize to 0-1
        wind_amplitude = speed_factor * 0.30  # Wind amplitude based on speed (doubled for better audibility)
        
        dt = 1.0 / self.sample_rate
        wind_samples = np.zeros(num_samples, dtype=np.float32)
        
        # Generate multi-band wind noise using phase-continuous sine waves
        # This avoids discontinuities from random noise while still sounding natural
        
        # Low frequency rumble (hull vibration from air pressure)
        low_freq = 20.0 + speed_factor * 30.0  # 20-50 Hz
        low_noise = np.zeros(num_samples, dtype=np.float32)
        
        # Mid frequency hiss (air turbulence) - multiple frequencies for texture
        mid_freq = 200.0 + speed_factor * 400.0  # 200-600 Hz
        mid_noise = np.zeros(num_samples, dtype=np.float32)
        
        # High frequency whistle (rigging and sharp edges)
        high_freq = 1000.0 + speed_factor * 2000.0  # 1-3 kHz
        high_noise = np.zeros(num_samples, dtype=np.float32)
        
        # Add multiple phases for each band to create noise-like texture
        dt = 1.0 / self.sample_rate
        for i in range(num_samples):
            t = i * dt
            
            # Low frequency: multiple harmonics for complexity
            low_phase = self.noise_phase + 2 * math.pi * low_freq * t
            low_noise[i] = (0.3 * math.sin(low_phase) + 
                           0.2 * math.sin(low_phase * 1.33) +
                           0.1 * math.sin(low_phase * 1.77))
            
            # Mid frequency: rapid modulation for turbulence effect (with subtle variance)
            mid_phase = self.noise_phase + 2 * math.pi * mid_freq * t
            mid_modulation = 1.0 + 0.5 * math.sin(2 * math.pi * 7.0 * t)
            # Add subtle phase variance for more natural turbulence
            mid_variance = 0.05 * math.sin(2 * math.pi * 13.0 * t + 0.7)
            mid_noise[i] = (0.4 * math.sin(mid_phase + mid_variance) * mid_modulation + 
                           0.2 * math.sin(mid_phase * 1.41) +
                           0.1 * math.sin(mid_phase * 2.13))
            
            # High frequency: fast modulation for rigging effects (reduced amplitude, added variance)
            high_phase = self.noise_phase + 2 * math.pi * high_freq * t
            high_modulation = 1.0 + 0.8 * math.sin(2 * math.pi * 17.0 * t)
            # Add subtle phase variance to reduce whistly character
            variance = 0.1 * math.sin(2 * math.pi * 41.0 * t + 1.5)
            high_noise[i] = 0.1 * math.sin(high_phase + variance) * high_modulation  # Halved from 0.2 to 0.1
        
        # Apply filtering to each frequency band and combine
        for i in range(num_samples):
            t = i * dt
            
            # Low frequency component (filtered random walk)
            if i > 0:
                low_noise[i] = low_noise[i-1] * 0.95 + low_noise[i] * 0.05
            
            # Mid frequency component with slight modulation
            mid_modulation = 1.0 + 0.2 * math.sin(2 * math.pi * 5.0 * t)  # 5 Hz modulation
            mid_filtered = mid_noise[i] * mid_modulation
            
            # High frequency component with rapid modulation (turbulence)
            high_modulation = 1.0 + 0.3 * math.sin(2 * math.pi * 23.0 * t)  # 23 Hz turbulence
            high_filtered = high_noise[i] * high_modulation
            
            # Combine frequency bands with speed-dependent mixing
            wind_samples[i] = (
                low_noise[i] * 0.4 +           # Always present
                mid_filtered * 0.4 * speed_factor +  # Increases with speed
                high_filtered * 0.2 * (speed_factor ** 2)  # Prominent at high speeds
            )
        
        # Apply overall wind amplitude
        wind_samples = wind_samples * wind_amplitude
        
        # Add gusting effect (slow amplitude modulation)
        gust_frequency = 0.3  # 0.3 Hz gusting
        for i in range(num_samples):
            t = i * dt
            gust_factor = 1.0 + 0.3 * math.sin(2 * math.pi * gust_frequency * t + self.noise_phase)
            wind_samples[i] *= gust_factor
        
        # Update noise phase for continuous gusting
        self.noise_phase += 2 * math.pi * gust_frequency * duration
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
            "engine_firing_freq": (self.current_rpm / 60.0) * 6 if self.current_rpm > 0 else 0
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
