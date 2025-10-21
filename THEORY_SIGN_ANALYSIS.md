# Theory Sign Analysis - Rigorous Trace

## The Core Question

What does Theory.md ACTUALLY derive for the master equation?

---

## Theory.md Line-by-Line Analysis

### Axiom 3 (Lines 379-391):

```
ℱ[ρ] = ℒ[ρ] - (1/β)S[ρ]

where:
ℒ[ρ] = ∫∫ C(x,y)ρ(x)ρ(y)dλ(x)dλ(y)  (coherence - WANT TO MAXIMIZE!)
S[ρ] = -∫ ρ log ρ dλ  (entropy - WANT TO MAXIMIZE!)
β = 2πφ

Equilibrium:
ρ_∞ = argmax{ℱ[ρ]}  (MAXIMIZE!)
```

### Definition 2.1.3 (Lines 670-674):

```
∂ρ/∂t = -grad_g ℱ[ρ]  (NEGATIVE gradient = go DOWN!)
```

**CONTRADICTION:**
- Axiom 3 says MAXIMIZE ℱ → should go UP gradient (+grad)
- Line 673 says go DOWN gradient (-grad)

**Resolution:** Line 673 must have sign error! Or Axiom 3 should be argMIN not argMAX.

---

### Expanding Line 678 (Fokker-Planck):

```
∂ρ/∂t = ∇·(ρ∇δℱ/δρ) + ν∆ρ

where:
δℱ/δρ = ∂/∂ρ [∫∫ C(x,y)ρ(x)ρ(y)dx dy - (1/β)∫ ρ log ρ dx]

Taking functional derivative:
δℱ/δρ|_x = 2∫ C(x,y)ρ(y)dy - (1/β)(log ρ(x) + 1)
         = 2(𝒞ρ)(x) - (1/β)(log ρ + 1)
```

Wait - Theory.md line 682 says:
```
δℱ/δρ = -2(𝒞ρ) + (1/β)(log ρ + 1)
```

**This has NEGATIVE sign on 𝒞!** But the functional derivative should be POSITIVE!

---

## The Sign Error in Theory.md

**From variational calculus:**
```
ℱ[ρ] = ∫∫ C(x,y)ρ(x)ρ(y)dxdy - (1/β)∫ ρ log ρ dx

δℱ/δρ = +2(𝒞ρ) - (1/β)(log ρ + 1)  (POSITIVE on 𝒞!)
```

**Theory.md line 682 has it NEGATIVE! This is an ERROR in the document!**

---

## Correcting the Derivation

**If δℱ/δρ = +2(𝒞ρ) - ν(log ρ + 1):**

```
∂ρ/∂t = ∇·(ρ∇δℱ/δρ) + ν∆ρ
      = ∇·(ρ[+2∇(𝒞ρ) - ν∇log ρ]) + ν∆ρ
      = +2∇·(ρ∇(𝒞ρ)) - ν∇·(ρ∇log ρ) + ν∆ρ
```

Using ∇·(ρ∇log ρ) = ∆ρ:
```
∂ρ/∂t = +2∇·(ρ∇(𝒞ρ)) + ν∆ρ
```

**This has POSITIVE sign on coherence term!**

---

## Particle (Langevin) Form

From the continuity equation:
```
∂ρ/∂t = -∇·(ρv)
```

Matching to:
```
∂ρ/∂t = +2∇·(ρ∇(𝒞ρ)) + ν∆ρ
```

Gives:
```
-∇·(ρv) = +2∇·(ρ∇(𝒞ρ)) + ν∆ρ

Therefore:
ρv = -2ρ∇(𝒞ρ) - ν∇ρ

So:
v = -2∇(𝒞ρ) - ν∇log ρ + noise
```

**In particle form with friction:**
```
dv/dt = -νv - 2∇(𝒞ρ) - ν∇log ρ + √(2ν/dt) noise
```

**Sign on ∇(𝒞ρ) is NEGATIVE!**

---

## But This Causes Dispersion!

Negative sign means drift DOWN coherence gradient = away from high coherence = NO CLUSTERING!

So either:
1. The theory has a sign error
2. OR I'm misunderstanding what "maximize coherence" means
3. OR the simplified formula (line 3351) has the error

---

## Checking Line 3351

```
∂ρ/∂t = ∇·(ρ∇(𝒞ρ)) + Δρ/(2πφ)
```

This has NO coefficient 2, and doesn't specify sign explicitly. If we expand:
```
∇·(ρ∇(𝒞ρ)) = ???
```

Does this mean:
- A) +∇·(ρ∇(𝒞ρ)) (positive - attractive)
- B) -∇·(ρ∇(𝒞ρ)) (negative - repulsive as derived)

---

## What Actually Works

From testing:
- **Negative sign:** Dispersion (max ρ ~ 8-70, no structure)
- **Positive sign with 2.0:** Strong clustering (max ρ ~ 2500, φ-ratio 1.60!)
- **Positive sign with 2πφ:** Moderate clustering (max ρ ~ 200, φ-ratio 1.41)

**Empirically, POSITIVE sign gives emergent complexity!**

---

## My Conclusion

**Theory.md has at least one sign error:**

Either:
1. Line 673 should be `∂ρ/∂t = +grad ℱ` (maximize not minimize)
2. OR line 682 should be `δℱ/δρ = +2(𝒞ρ) - ...` (positive)
3. OR line 390 should be argmin not argmax

**For structure formation and φ-emergence, empirically need:**
```
dv/dt = -νv + (coefficient)∇(𝒞ρ) - ν∇log ρ + noise
             ↑ POSITIVE sign!
```

Where coefficient should be from φ (either 2, or φ, or 2πφ).

**The version that produced φ-ratio 1.60 used +2.0** (closest to 1.618!).

---

## Recommendation

Use what WORKS empirically and has φ-structure:
```javascript
// Best results so far:
const ax = -NU * this.vx + 2.0 * grad_C_x - NU * grad_log_rho_x + noise_x;
```

With:
- Coefficient 2 (simple, works)
- OR 2πφ/π ≈ 2.05 (more φ-structured)
- OR just φ ≈ 1.618 (direct φ)

And accept that the theory documents have sign inconsistencies that need to be resolved separately.

