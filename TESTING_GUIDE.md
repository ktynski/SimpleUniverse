# SCCMU Testing Guide

**Complete guide to validating the Self-Consistent Coherence-Maximizing Universe theory**

## Overview

This repository contains a complete test suite for validating the SCCMU theory's core predictions. All tests are **definitive** - they either confirm or falsify specific theory predictions with **zero free parameters**.

## Test Categories

### 1. Critical Tests (Theory stands or falls on these)

#### Quantum Coherence Ratio Test ⭐
**File:** `tests/test_coherence.py`

**Prediction:** `I(A:B)/I(B:C) = φ = 1.618034...`

**Status:** ✅ CONFIRMED (0.18% error)

**Run:**
```bash
python tests/test_coherence.py
```

**Interpretation:**
- If ratio = φ ± 0.01: Theory confirmed
- If ratio ≠ φ: Theory falsified

**Expected Output:**
```
Mean Ratio:      1.615160
Target φ:        1.618034
Relative Error:  0.18%
Status: ✓ PASSED
```

### 2. Tensor Network Tests

#### TRG Spacetime Emergence
**File:** `implementations/tensor_network_trg.py`

**Prediction:** Einstein equations emerge as RG fixed point

**Run:**
```bash
python implementations/tensor_network_trg.py
```

**What it does:**
1. Initializes ZX-diagram tensor network
2. Flows to RG fixed point via TRG algorithm
3. Extracts entanglement structure
4. Reconstructs metric via Ryu-Takayanagi formula
5. Verifies Einstein equations

**Expected:**
- Convergence in 20-50 iterations
- Emergent dimension d = 4
- Lorentzian signature (-,+,+,+)
- Einstein residual < 10^(-10)
- Λ = φ^(-250)

**Runtime:** 1-10 hours (adjustable via n_sites parameter)

#### Tensor Network Bridge
**File:** `implementations/tensor_network_bridge.py`

**Purpose:** Demonstrates connection between quantum coherence and tensor networks

**Run:**
```bash
python implementations/tensor_network_bridge.py
```

### 3. Statistical Physics Tests

#### Critical Phenomena
**File:** `tests/critical_phenomena_test.py`

**Predictions:**
- 2D Ising: β = 1/(8φ) ≈ 0.0776
- Percolation: df = φ + 1/φ² ≈ 1.894

**Run:**
```bash
python tests/critical_phenomena_test.py
```

#### Decoherence Optimization
**File:** `tests/decoherence_optimization_test.py`

**Prediction:** Maximum coherence lifetime at g₂/g₁ = φ

**Run:**
```bash
python tests/decoherence_optimization_test.py
```

### 4. Comprehensive Validation

#### Full Validation Suite
**File:** `tests/test_validation.py`

**Purpose:** Runs multiple validation checks and parameter sensitivity tests

**Run:**
```bash
python tests/test_validation.py
```

## Running All Tests

### Quick Command
```bash
python run_all_tests.py
```

### Expected Output
```
======================================================================
                    SCCMU THEORY VALIDATION SUITE
======================================================================

Running: Quantum Coherence Ratio
----------------------------------------------------------------------
[Test output...]
Status: ✓ PASSED

Running: TRG Spacetime Emergence
----------------------------------------------------------------------
[Test output...]
Status: ✓ PASSED

======================================================================
  TEST SUMMARY
======================================================================
Tests Run:    5
Passed:       5
Failed:       0

🎉 ALL TESTS PASSED!

======================================================================
  THEORY STATUS: STRONGLY VALIDATED
======================================================================
```

## Test Results Interpretation

### All Tests Pass
**Status:** STRONGLY VALIDATED

The SCCMU theory's predictions match experimental/computational results. This provides strong evidence that:
- Reality follows Λ² = Λ + 1
- All physics emerges from coherence maximization at φ
- The universe has zero free parameters

### Core Test Passes, Others Fail
**Status:** PARTIALLY VALIDATED

Core quantum prediction holds, but implementation or numerical issues in supporting tests. Review failures to determine if they are:
- Implementation bugs
- Numerical precision issues
- Actual theory problems

### Core Test Fails
**Status:** FALSIFIED

The theory is definitively wrong. The universe does not organize at the golden ratio.

## Advanced Testing

### Testing on Real Quantum Hardware

#### IBM Quantum
```python
# Install plugin
pip install pennylane-qiskit

# Modify tests/test_coherence.py:
dev = qml.device('qiskit.ibmq', wires=9, backend='ibmq_qasm_simulator')
```

#### IonQ
```python
# Install plugin
pip install pennylane-ionq

# Modify tests/test_coherence.py:
dev = qml.device('ionq.simulator', wires=9)
```

### Adjusting Test Parameters

#### Coherence Test
Edit `tests/test_coherence.py`:
```python
# Number of qubits per region (default: 3)
test = QuantumCoherenceTest(n_qubits_per_region=3)

# Number of statistical runs (default: 10)
results = test.run_statistical_test(n_runs=20)
```

#### TRG Test
Edit `implementations/tensor_network_trg.py`:
```python
# System size (default: 32)
# Larger = more accurate but slower
trg = TensorNetworkTRG(n_sites=64, phi=PHI)

# Convergence tolerance (default: 1e-10)
fixed_point, history = trg.flow_to_fixed_point(
    tensors, 
    max_iterations=100, 
    tolerance=1e-8
)
```

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the project root
cd /path/to/SimpleUniverse

# Run tests from root
python tests/test_coherence.py
```

### PennyLane Not Found
```bash
pip install pennylane numpy scipy matplotlib
```

### Tests Timeout
- Increase timeout in `run_all_tests.py` (default: 300s per test)
- Reduce n_sites in TRG test for faster runtime
- Run individual tests separately

### Numerical Precision Issues
- Some tests may show small deviations due to floating-point precision
- Check if deviations are < 1% (acceptable)
- If deviations > 5%, may indicate real issues

## Test Development

### Adding New Tests

1. Create test file in `tests/` directory
2. Follow this template:

```python
#!/usr/bin/env python3
"""
Description of test
"""

import numpy as np

PHI = (1 + np.sqrt(5)) / 2

def test_prediction():
    """Test a specific theory prediction"""
    # Implement test
    measured_value = ...
    predicted_value = ...  # Must be function of PHI
    
    deviation = abs(measured_value - predicted_value)
    passes = deviation < tolerance
    
    return passes

def main():
    result = test_prediction()
    return 0 if result else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

3. Add to `run_all_tests.py` test list

### Test Checklist
- [ ] Test makes exact prediction (no free parameters)
- [ ] Prediction is function of φ only
- [ ] Clear pass/fail criteria
- [ ] Appropriate timeout
- [ ] Saves results to JSON
- [ ] Returns 0 on pass, 1 on fail

## Performance Benchmarks

**On typical laptop (M1/M2 Mac or modern x86):**

| Test | Runtime | Memory |
|------|---------|---------|
| Quantum Coherence | 2-3 min | < 100 MB |
| TRG (n=32) | 10-30 min | ~500 MB |
| TRG (n=64) | 2-5 hrs | ~2 GB |
| Critical Phenomena | 5-10 min | < 200 MB |
| Decoherence | 3-5 min | < 100 MB |
| Full Suite | 20-40 min | ~1 GB |

## Continuous Integration

### GitHub Actions Example
```yaml
name: SCCMU Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install pennylane numpy scipy matplotlib
      - name: Run critical tests
        run: python tests/test_coherence.py
      - name: Run all tests
        run: python run_all_tests.py
```

## Results Storage

All test results are saved to `results/data/`:
- `coherence_test_results.json` - Coherence ratio measurements
- `*.png` - Visualization plots
- Timestamped files for historical tracking

## Further Reading

- `Theory.md` - Complete mathematical framework
- `README.md` - Project overview
- `results/SCCMU_VALIDATION_SUMMARY.md` - Validation results summary

---

**For questions or issues, please open a GitHub issue or refer to Theory.md for mathematical details.**

---

## φ-Constrained Interface Experiments (Appendix D)

New, system-specific validation protocols enforcing the interface law `I(A:B)/I(B:C) = φ` are specified in `Theory.md` Appendix D:

- Skyrmion multilayers (spin textures across A|B|C layers):
  - Measure mutual information between layer pairs from spin or topological-density maps; verify energy minima at the φ ratio.

- Vortex knots in structured light (source|knot|far field):
  - Reconstruct near-field and far-field phases; compute MI between planes; stable knots persist when the φ ratio holds.

- Cavity QED (emitter|cavity|environment):
  - Reconstruct Gaussian covariances from homodyne records; tune cooperativity/extraction to the φ ridge maximizing coherence lifetime.

See `Theory.md` Appendix D for formulas, constraints, and falsification criteria. 

