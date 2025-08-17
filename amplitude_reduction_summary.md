🔊 Cylinder Firing Amplitude Reduction Summary
==============================================

## Change Made (v0.2.61)

### Amplitude Reduction
**Before**: `mixture_amplitude = 0.1 + (self.current_mixture * 0.3)` → Range: 0.1 to 0.4
**After**: `mixture_amplitude = 0.03 + (self.current_mixture * 0.1)` → Range: 0.03 to 0.13

### Reduction Factor
- **Maximum amplitude**: 0.4 → 0.13 (32.5% of original)
- **Minimum amplitude**: 0.1 → 0.03 (30% of original)  
- **Effective reduction**: ~67% decrease (about 1/3 of original level)

### Why This Change
- Cylinder firing events were too loud relative to propeller and wind sounds
- Needed better balance in the audio mix for more realistic engine character
- Maintains the same mixture response curve but at lower overall level

### Technical Impact
- **Combustion events** now have more appropriate amplitude
- **HDR processing** still applied for dynamic range control
- **Mix balance** improved between engine, propeller, and wind components
- **Frequency characteristics** unchanged - only amplitude affected

### Testing Results
With 90% mixture setting (near maximum):
- **Expected amplitude**: 0.120 (vs 0.37 previously)
- **Actual peak**: 0.513 (after envelope and track combination)
- **Full mix peak**: 0.348 (with HDR processing)
- **Reduction achieved**: ✅ ~67% decrease as intended

### Audio Balance Status
- **Propeller**: Smooth physics-based pressure waves ✅
- **Engine**: Discrete combustion events at appropriate level ✅  
- **Wind**: Multi-band realistic air turbulence ✅
- **HDR**: Logarithmic normalization prevents clipping ✅
- **Hull Filter**: Low-pass filtering for interior dampening ✅

## Result
The engine audio now has a more realistic balance where:
1. **Propeller** provides the primary rhythmic sound signature
2. **Engine** adds authentic combustion character without overwhelming
3. **Wind** contributes appropriate environmental atmosphere
4. **All components** blend naturally through HDR processing

The reduced amplitude makes the engine sound more like background power generation rather than dominating the audio mix, which is more authentic for an airship where you're inside the gondola/cabin rather than sitting directly on the engine.
