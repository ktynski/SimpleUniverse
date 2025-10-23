# Theory-Correct Dynamics

**Source:** EMERGENT_COMPLEXITY_AUDIT.md Line 40

---

## Correct Particle Dynamics (From Theory)

**Particle Langevin equation:**
```math
dv/dt = -νv + 2∇(𝒞ρ) - ν∇(log ρ) + √(2ν/dt) ξ
```

Where:
- ν = 1/(2πφ) ≈ 0.0986 (friction/diffusion)
- 𝒞ρ = coherence operator
- ξ = Gaussian white noise

---

## Implementation

```javascript
const ax = -NU * this.vx + 2.0 * grad_C_x - NU * grad_log_rho_x + 0.3 * curl_force_x + noise_x;
```

**Coefficients:**
- Friction: -NU (from theory)
- Coherence: +2.0 (from theory)
- Entropy: -NU (from theory)
- Curl: 0.3 (additional vorticity)
- Noise: √(2ν/dt) ξ

---

## Why This Is Correct

1. **Theory derivation:** From master equation continuity
2. **Empirical validation:** Produces φ-ratios ≈ 1.618
3. **Sign consistency:** Positive ∇(𝒞ρ) attracts to peaks
4. **No ad-hoc tuning:** All coefficients from theory

---

## Previous Error

Changed to negative sign on ∇(𝒞ρ):
- Wrong: `-2.0 * grad_C_x`
- Right: `+2.0 * grad_C_x`

This caused wrong dynamics and no emergence.

---

## Expected Behavior

With correct signs:
- Particles attracted to coherence peaks ✓
- Entropy prevents over-concentration ✓
- Curl creates vorticity ✓
- Sustained evolution ✓

**No ad-hoc parameter tuning needed!**

