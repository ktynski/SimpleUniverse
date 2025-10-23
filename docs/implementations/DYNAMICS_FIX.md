# Dynamics Fix: Correct Force Signs

**Issue:** Not seeing continued evolution/emergent complexity

**Root Cause:** Sign errors in force terms

---

## Theory Requirements

From Theory.md:
```
δℱ/δρ = -2(𝒞ρ) + (1/β)(log ρ + 1)
```

For particle dynamics:
```
∇δℱ/δρ = -2∇(𝒞ρ) + (1/β)∇(log ρ)
```

Where β = 2πφ ≈ 10.166

---

## Force Interpretation

**Key insight:** We want particles to MOVE toward coherence peaks.

If coherence is HIGH at location (x,y,z), we want force pointing TOWARD that location.

But ∇(𝒞ρ) points in direction of INCREASING coherence (away from peak).

So to attract toward peaks, we need: **F ∝ -∇(𝒞ρ)**

This is what theory says: `-2∇(𝒞ρ)` is correct!

---

## Entropy Term

The term `+(1/β)∇(log ρ)` with β = 2πφ:
- Acts to spread particles out (entropy maximization)
- Opposes over-concentration
- Coefficient is 1/β ≈ 0.098 (small compared to coherence)

**Proper sign:** `+NU * grad_log_rho` where NU = 1/(2πφ)

---

## Corrected Dynamics

```javascript
// Force = ∇δℱ/δρ = -2∇(𝒞ρ) + (1/β)∇(log ρ)
const ax = -NU * this.vx - 2.0 * grad_C_x + NU * grad_log_rho_x + 0.3 * curl_force_x + noise_x;
```

Where:
- `-2.0 * grad_C_x`: Attract toward coherence peaks ✓
- `+NU * grad_log_rho_x`: Entropy term (spreading) ✓  
- `0.3 * curl_force_x`: Vorticity ✓
- `-NU * this.vx`: Friction ✓

---

## Why This Should Work Better

**Before:** Wrong signs → particles pushed away from coherence  
**After:** Correct signs → particles attracted to coherence  

**Result:** Should see continued evolution as coherence peaks develop further structure!

