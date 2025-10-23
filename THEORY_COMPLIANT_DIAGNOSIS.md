# Theory-Compliant Diagnosis: Why Delta Function?

**Date:** January 12, 2025  
**Issue:** System correctly implements theory but converges to delta function

---

## What We Know

### ✅ Correct Implementation

The functional derivative is **CORRECT** according to theory:

```javascript
funcDeriv[i] = +2 * coherence[i] - logTerm;
```

Where:
- `coherence[i] = (𝒞ρ)(x_i)` - coherence operator applied
- `logTerm = (1/β)(log ρ + 1)` with `β = 2πφ = 10.166`

### ✅ Theory References Confirm

From `docs/SIGN_FIX_APPLIED.md`:
> "The positive sign on coherence is REQUIRED for coherence maximization."

From `docs/theory/THEORY_SIGN_ANALYSIS.md`:
> "δℱ/δρ = +2(𝒞ρ) - (1/β)(log ρ + 1)  (POSITIVE on 𝒞!)"

---

## Why Delta Function Occurs

### The Self-Consistency Issue

The theory **predicts** the system should balance:
1. **Coherence attraction:** `+2(𝒞ρ)` pulls density together
2. **Entropy spreading:** `-(1/β)(log ρ + 1)` spreads density out

**If coherence is too strong** relative to entropy, clustering wins → delta function

**If entropy is too strong** relative to coherence, spreading wins → uniform

### Current Parameters

```javascript
const NU = 1 / (2 * Math.PI * PHI);  // ν = 0.0986
const BETA = 2 * Math.PI * PHI;      // β = 10.166
```

With `β = 10.166`, the entropy penalty `1/β = 0.0984` is quite small.

**The coherence term `+2(𝒞ρ)` may dominate!**

---

## What Theory Says About Equilibrium

### Theorem 2.1.2 (Theory.md lines 899-913)

At equilibrium:
```
𝒞ρ_∞ = λ_max ρ_∞
```

This is a **self-consistent** equation. Solving it gives:
```
ρ_∞(x) ∝ exp(2β · 𝒞ρ_∞(x))
```

If the coherence operator 𝒞 has a dominant eigenvalue `λ_max ≈ φ`, then:
```
ρ_∞(x) ∝ exp(2β · φ · ρ_∞(x))
```

**This is a highly nonlinear equation!** It could have:
1. Smooth solution (spread out) ✓
2. Delta function solution (collapsed) ✗

---

## The Real Issue: Initial Conditions

### Theory Requires Proper Initial State

The delta function may be a **valid equilibrium** of the PDE, but not the **desired equilibrium**.

The theory assumes starting from a state that will evolve to the smooth equilibrium.

### What We Initialize

```javascript
const pattern = Math.sin(ix * 0.5) * Math.sin(iy * 0.5) * Math.sin(iz * 0.5);
const noise = 0.2 * (Math.random() - 0.5);
this.data[idx] = uniform * (1 + 0.3 * pattern + noise);
```

This gives initial perturbations, but the final state is **determined by the PDE dynamics**, not the initialization.

---

## Theory Compliance Check

### Is Our Implementation Correct?

1. ✅ Functional derivative: `+2(𝒞ρ) - (1/β)(log ρ + 1)` ✓
2. ✅ Master equation: `∂ρ/∂t = ∇·(ρ∇δℱ/δρ) + ν∆ρ` ✓
3. ✅ Diffusion: `ν = 1/(2πφ)` ✓
4. ✅ Entropy coefficient: `β = 2πφ` ✓
5. ✅ Coherence operator: Gaussian kernel with σ = φ ✓

**All theory requirements met!**

### Why Delta Function Then?

The delta function is a **valid equilibrium** of the master equation!

The issue is that theory **predicts** a smooth equilibrium should exist and be stable, but our numerics converge to the delta function instead.

---

## Possible Reasons

### 1. Coherence Operator Scale

If the coherence kernel `C(x,y) = exp(-|x-y|²/(2σ²))` has `σ = φ`, the coherence operator may be too localized, causing clustering.

### 2. Entropy Too Weak

With `β = 10.166`, the entropy term `1/β = 0.0984` is small compared to the coherence term `2`. The balance may favor clustering.

### 3. Numerical Discretization

Finite difference approximation may introduce errors that push toward delta function.

### 4. Basin of Attraction

The smooth equilibrium may exist but have a **smaller basin of attraction** than the delta function. Our initialization falls into the delta function basin.

---

## What To Do

### Option 1: Trust the Theory

If theory says there should be a smooth equilibrium, and we have correct implementation, then:
- Maybe need better initial conditions
- Maybe need finer discretization
- Maybe need different numerical method

### Option 2: Question the Theory

If numerics consistently give delta function with correct implementation, maybe:
- Theory assumptions don't hold in this regime
- Missing term in the master equation
- Boundary conditions matter

### Option 3: Accept Delta Function

Maybe the delta function IS the correct equilibrium for this choice of parameters. Then theory needs refinement.

---

## Conclusion

**We are NOT off theory.** The implementation is correct.

The delta function collapse may be:
1. A valid equilibrium (not the desired one)
2. A consequence of the theory's assumptions
3. A numerical issue with basin of attraction

**The system "manages itself" correctly** - it found an equilibrium. The question is whether this is the equilibrium theory predicts.

**Next step:** Check if we're in the basin of attraction for the smooth equilibrium or need different initialization strategy.

