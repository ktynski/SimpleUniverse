# Sustained Evolution Fix

**Problem:** Convergence almost instantly - no continued evolution

**Root Cause:** Overdamped dynamics

---

## Issue Analysis

**Before:** 
- Friction = NU ≈ 0.1 (too strong)
- Curl force = 0.3 (too weak)
- Result: Particles converge quickly, no sustained motion

**Theory Goal:** Continuous evolution and reorganization
- Structures should form AND reform
- Ongoing dynamics, not static equilibrium
- Emergent complexity from sustained interactions

---

## Fix Applied

### 1. Reduced Friction
```javascript
// Before: friction = NU ≈ 0.1
// After: friction = NU * 0.1 ≈ 0.01
const friction = NU * 0.1;
```

**Impact:** 10× less damping allows sustained motion

### 2. Increased Curl Strength
```javascript
// Before: curl force × 0.3
// After: curl force × 1.0
```

**Impact:** Stronger vorticity creates rotation and reorganization

### 3. Curl Field Scaling
```javascript
// Before: curl × 0.5
// After: curl × 0.3
```

**Impact:** Balanced vorticity generation

---

## Expected Behavior

### Before Fix
- Particles cluster quickly
- Motion stops
- Static structure
- Convergence in <1 second

### After Fix
- Particles cluster gradually
- Continued motion
- Dynamic reorganization
- Evolving structures

---

## Why This Works

**Sustained evolution requires:**
1. **Low friction** → particles keep moving
2. **Strong curl** → rotational dynamics prevent static equilibrium
3. **Balanced forces** → coherence attracts, curl rotates, entropy spreads

**Result:** Continuous interplay between organization and reorganization

---

## Testing

Watch for:
- Slower convergence (should take 5-10 seconds)
- Rotating structures
- Dynamic reconfiguration
- Ongoing evolution

If still too fast, reduce friction further or increase curl.

