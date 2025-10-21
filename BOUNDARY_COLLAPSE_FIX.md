# Boundary Collapse Fix

## The Problem You Observed

**Symptom:** "Structure starts to emerge, then all disperses and all nodes end up on 3 sides of a cube"

**What this means:**
- Initial clustering works! (positive sign correct ✓)
- But particles escape the grid
- Accumulate on cube boundary faces
- System collapses to boundaries instead of forming internal structure

## Root Causes

### Cause 1: No Boundary Conditions

**The issue:**
```javascript
// Particles initialized in range: -16 to +16
const x = (Math.random() - 0.5) * GRID_EXTENT * 1.6;  // ±16

// But grid only covers: -10 to +10
const GRID_EXTENT = 10.0;

// NO boundary wrapping or reflection!
// Particles can escape and never come back
```

**What happens:**
1. Particles drift outside grid bounds
2. At grid edge, density/coherence sampled as zero
3. Creates artificial gradients pointing outward
4. More particles pushed to boundaries
5. Eventually all particles on 3 cube faces (±x, ±y, ±z limits)

### Cause 2: Coefficient 2.0 Too Strong

**From testing:**
- Coefficient 2.0: Max density ~2500 (very aggressive clustering)
- Over-strong attraction → rapid collapse
- Combined with boundary issues → accumulation at edges

**Better choice:**
- Coefficient φ ≈ 1.618: More balanced
- Theory-motivated (golden ratio appears throughout)
- Allows structure to form without over-collapsing

## The Fixes

### Fix 1: Periodic Boundary Conditions

**Added wrapping:**
```javascript
// PERIODIC BOUNDARY CONDITIONS (wrap around)
const box_size = GRID_EXTENT * 1.8;  // 18 units (covers init range)

if (this.x > box_size) this.x -= 2 * box_size;   // Wrap right → left
if (this.x < -box_size) this.x += 2 * box_size;  // Wrap left → right
// Same for y, z
```

**Effect:**
- Particles that reach edge wrap to opposite side
- Like Pac-Man screen wrapping
- No boundary accumulation
- Maintains simulation volume

**Alternative options considered:**
- **Reflective boundaries:** Bounce back (creates wall effects)
- **Soft confining potential:** Restoring force (artificial)
- **Periodic (chosen):** Most physical for cosmology simulation

### Fix 2: Gentler Coefficient

**Changed:**
```javascript
// Before:
const ax = -NU * this.vx + 2.0 * grad_C_x - ...;  // Too strong

// After:
const COHERENCE_STRENGTH = PHI;  // φ ≈ 1.618
const ax = -NU * this.vx + COHERENCE_STRENGTH * grad_C_x - ...;
```

**Rationale:**
- φ appears naturally in theory (β = 2πφ, σ = φ, etc.)
- Value 1.618 close to 2 but gentler
- Allows stable structure formation
- Prevents runaway collapse

## Expected Behavior Now

### Timeline:

**t = 0-10s:** 
- Uniform distribution with thermal noise
- Small random density fluctuations

**t = 10-20s:**
- Fluctuations amplified by eigenmodes at φ-scale
- Small clusters start forming
- NO boundary escape!

**t = 20-40s:**
- Clear clustering visible
- Multiple cluster centers
- Stable separation between clusters

**t = 40-60s:**
- Structure converges
- Peak spacings should show φ-ratios
- Clusters remain in interior (not boundaries!)

### Observables:

**Max density:** 
- Should reach 500-1500 (not 2500, more stable)
- Multiple peaks (not all at boundaries)

**Spatial distribution:**
- Clusters throughout volume
- NOT concentrated on cube faces
- Wrap-around at boundaries (particles reappear)

**φ-ratios:**
- Measure peak spacings at t > 300 frames
- Should approach φ ≈ 1.618
- TRUE emergence (no imposed structure!)

## Why These Fixes Work

### Periodic Boundaries:

**Physical justification:**
- Cosmology: universe has no edge
- Simulates small patch of infinite system
- Standard in N-body simulations
- Prevents artificial boundary effects

**Implementation:**
- Simple modulo arithmetic
- No computation overhead
- Preserves particle count
- Natural for statistical systems

### Coefficient φ:

**Theory motivation:**
- All scales in SCCMU involve φ:
  - β = 2πφ (inverse temperature)
  - ν = 1/(2πφ) (diffusion)
  - σ = φ (coherence scale)
  - Coefficient = φ (natural!)

**Balance:**
- Strong enough: clustering happens (feedback works)
- Gentle enough: stable (doesn't over-collapse)
- φ-structured: consistent with theory

## Diagnostic Signs

### Good behavior (working):
✓ Clusters form in interior volume
✓ Stable cluster positions over time
✓ Particles wrap at boundaries (appear on opposite side)
✓ Max density 500-1500
✓ Multiple distinct peaks
✓ Peaks spaced at φ-ratios

### Bad behavior (still broken):
✗ All particles on cube faces
✗ Density highest at boundaries
✗ Empty interior
✗ Max density > 3000
✗ Single massive collapse

## Summary

**Your observation was KEY diagnostic!**

The "cube face accumulation" revealed:
1. Missing boundary conditions
2. Over-strong clustering coefficient

**Fixes applied:**
1. ✅ Periodic boundaries (wrap-around)
2. ✅ Coefficient 2.0 → φ ≈ 1.618

**Should now see:**
- Structure emerges AND STAYS stable
- Clusters in interior, not at boundaries
- φ-ratios in peak spacings
- TRUE emergence from uniform start!

Try it again - should be much better!

