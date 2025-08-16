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
        self.engine_phase = 0.0       # Separate phase for engine firing cycles
        self.noise_phase = 0.0        # Phase for wind noise generation
        self.last_update_time = time.time()
        
        # Audio parameters (will be updated from simulator)
        self.current_rpm = 0.0
        self.current_pitch = 0.0
        self.current_mixture = 0.0
        self.current_airspeed = 0.0
        self.is_hull_filter = True
        
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
        
        # Extract audio-relevant parameters
        self.current_rpm = engine.get("rpm", 0.0)
        self.current_pitch = controls.get("propeller", 0.0)  # 0.0 to 1.0
        self.current_mixture = controls.get("mixture", 0.0)  # 0.0 to 1.0
        self.current_airspeed = motion.get("indicatedAirspeed", 0.0)
        
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
        
        if self.current_rpm <= 0:
            return samples
            
        # Calculate propeller frequency (assuming 2-blade prop)
        # Each blade passage creates a pressure pulse
        prop_blades = 2
        prop_frequency = (self.current_rpm / 60.0) * prop_blades  # Hz
        
        # Propeller pitch affects amplitude - higher pitch = more air displacement
        pitch_amplitude = 0.2 + (self.current_pitch * 0.6)  # 0.2 to 0.8 base amplitude
        
        dt = 1.0 / self.sample_rate
        
        for i in range(num_samples):
            t = i * dt
            
            # Fundamental frequency (main propeller whoosh)
            fundamental = math.sin(2 * math.pi * prop_frequency * t + self.phase_accumulator)
            
            # Add harmonics for realism (blade tip effects, vortex shedding)
            harmonic2 = 0.3 * math.sin(2 * math.pi * prop_frequency * 2 * t + self.phase_accumulator)
            harmonic3 = 0.15 * math.sin(2 * math.pi * prop_frequency * 3 * t + self.phase_accumulator)
            
            # Combine with pitch-dependent amplitude
            propeller_wave = (fundamental + harmonic2 + harmonic3) * pitch_amplitude
            
            samples[i] = propeller_wave
        
        # Update phase accumulator for continuous playback
        self.phase_accumulator += 2 * math.pi * prop_frequency * duration
        self.phase_accumulator = self.phase_accumulator % (2 * math.pi)
        
        return samples
        
    def generate_engine_wave(self, duration: float) -> np.ndarray:
        """
        Generate engine firing sound for 6-cylinder radial engine.
        
        Each cylinder fires at a different time, creating sharp pulses with intervals.
        The frequency is 6 times RPM (6 firings per engine revolution).
        """
        num_samples = int(duration * self.sample_rate)
        samples = np.zeros(num_samples, dtype=np.float32)
        
        if self.current_rpm <= 0:
            return samples
            
        # Engine firing frequency (6 cylinders, each fires once per revolution)
        firing_frequency = (self.current_rpm / 60.0) * self.engine_cylinders  # Hz
        
        # Mixture affects amplitude - richer mixture = more power per firing
        mixture_amplitude = 0.1 + (self.current_mixture * 0.3)  # 0.1 to 0.4 amplitude
        
        dt = 1.0 / self.sample_rate
        
        for i in range(num_samples):
            t = i * dt
            
            # Generate firing pulses - sharp attacks with quick decay
            # Use a sawtooth-like wave that simulates combustion pressure spikes
            firing_phase = (firing_frequency * t + self.engine_phase) % 1.0
            
            if firing_phase < 0.1:  # Sharp attack (10% of cycle)
                firing_amplitude = firing_phase / 0.1
            else:  # Quick exponential decay (90% of cycle)
                firing_amplitude = math.exp(-(firing_phase - 0.1) * 8)
            
            # Apply mixture-dependent amplitude
            engine_wave = firing_amplitude * mixture_amplitude
            
            # Add some low-frequency rumble for engine body resonance
            rumble = 0.1 * math.sin(2 * math.pi * (self.current_rpm / 60.0) * t + self.engine_phase)
            
            samples[i] = engine_wave + rumble
        
        # Update engine phase for continuous playback
        self.engine_phase += firing_frequency * duration
        self.engine_phase = self.engine_phase % 1.0
        
        return samples
        
    def generate_wind_noise(self, duration: float) -> np.ndarray:
        """
        Generate brown noise for wind sounds, affected by airspeed.
        
        Brown noise has more low-frequency content than white noise,
        simulating the wind rushing over the airship hull.
        """
        num_samples = int(duration * self.sample_rate)
        
        if self.current_airspeed <= 1.0:
            return np.zeros(num_samples, dtype=np.float32)
        
        # Generate white noise
        white_noise = np.random.normal(0, 1, num_samples).astype(np.float32)
        
        # Convert to brown noise by integrating (low-pass filtering)
        brown_noise = np.zeros_like(white_noise)
        integrator = 0.0
        
        for i in range(num_samples):
            integrator += white_noise[i] * 0.02  # Integration constant
            brown_noise[i] = integrator
            integrator *= 0.999  # Slight decay to prevent DC buildup
        
        # Airspeed affects both amplitude and frequency content
        speed_factor = min(self.current_airspeed / 100.0, 1.0)  # Normalize to 0-1
        wind_amplitude = speed_factor * 0.2  # Wind amplitude based on speed
        
        # High-frequency content increases with speed (turbulence)
        if speed_factor > 0.5:
            # Add some higher frequency content for high-speed turbulence
            turbulence = np.random.normal(0, speed_factor * 0.1, num_samples).astype(np.float32)
            brown_noise += turbulence
        
        return brown_noise * wind_amplitude
        
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
        
    def generate_audio_buffer(self, duration: float) -> np.ndarray:
        """
        Generate a complete audio buffer mixing all sound sources.
        
        Args:
            duration: Duration of audio buffer in seconds
            
        Returns:
            Mixed stereo audio buffer as numpy array
        """
        # Update parameters from simulator
        self.update_from_simulator()
        
        # Generate individual sound components
        propeller_audio = self.generate_propeller_wave(duration)
        engine_audio = self.generate_engine_wave(duration)
        wind_audio = self.generate_wind_noise(duration)
        
        # Mix the audio sources
        mixed_audio = propeller_audio + engine_audio + wind_audio
        
        # Apply hull filtering if enabled
        if self.is_hull_filter:
            mixed_audio = self.apply_hull_filter(mixed_audio)
        
        # Normalize to prevent clipping
        max_amplitude = np.max(np.abs(mixed_audio))
        if max_amplitude > 0.95:
            mixed_audio = mixed_audio * (0.95 / max_amplitude)
        
        # Convert to stereo (duplicate mono signal)
        num_samples = len(mixed_audio)
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
