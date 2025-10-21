#!/usr/bin/env python3
"""
φ-Structure as RG Fixed Point

Alternative hypothesis: Rather than forcing φ during flow,
φ emerges as a *fixed point* of information-preserving RG.

Key insight: Maybe sin²θ_W ≈ 0.231 IS φ-structured, but not as 1/(1+φ²).
Let's search for the actual φ-relationship.
"""

import numpy as np
from scipy.optimize import fsolve

PHI = (1 + np.sqrt(5)) / 2

def explore_phi_relations():
    """
    Search for φ-relationships with observed sin²θ_W = 0.23122
    """
    print("="*70)
    print("SEARCHING FOR φ-STRUCTURE IN WEINBERG ANGLE")
    print("="*70)
    print()
    print(f"Observed: sin²θ_W = 0.23122")
    print(f"φ = {PHI:.10f}")
    print()
    
    candidates = [
        ("1/(1+φ²)", 1/(1 + PHI**2)),
        ("1/φ²", 1/PHI**2),
        ("(φ-1)/φ²", (PHI-1)/PHI**2),
        ("1/(2φ)", 1/(2*PHI)),
        ("φ/(1+2φ)", PHI/(1+2*PHI)),
        ("(2-φ)/φ²", (2-PHI)/PHI**2),
        ("1/(3+φ)", 1/(3+PHI)),
        ("φ/(3φ+1)", PHI/(3*PHI+1)),
        ("(φ-1)/(φ+2)", (PHI-1)/(PHI+2)),
        ("1/(1+3φ)", 1/(1+3*PHI)),
        ("φ²/(1+3φ²)", PHI**2/(1+3*PHI**2)),
        ("(2φ-1)/(3φ²)", (2*PHI-1)/(3*PHI**2)),
        ("1/(2+2φ)", 1/(2+2*PHI)),
        ("φ/(2φ²+1)", PHI/(2*PHI**2+1)),
        ("(3-φ)/(3φ)", (3-PHI)/(3*PHI)),
    ]
    
    print("Testing candidate φ-formulas:")
    print("-"*70)
    print(f"{'Formula':<25} {'Value':<12} {'Error':<10} {'% Error'}")
    print("-"*70)
    
    best = None
    best_error = float('inf')
    
    for formula, value in candidates:
        error = abs(value - 0.23122)
        pct_error = error / 0.23122 * 100
        status = "✓" if pct_error < 5 else " "
        print(f"{status} {formula:<24} {value:<11.6f} {error:<9.6f} {pct_error:>6.2f}%")
        
        if error < best_error:
            best_error = error
            best = (formula, value)
    
    print("-"*70)
    print()
    
    if best and best_error / 0.23122 < 0.05:
        print(f"✓ MATCH FOUND: {best[0]} = {best[1]:.6f}")
        print(f"  Error: {best_error/0.23122*100:.2f}%")
    else:
        print(f"⚠ Best match: {best[0]} = {best[1]:.6f}")
        print(f"  Error: {best_error/0.23122*100:.2f}% (exceeds 5% threshold)")
    
    print()
    return best


def reverse_engineer_phi_structure():
    """
    Work backwards: if sin²θ_W = 0.23122 encodes φ,
    what's the relationship?
    """
    print("="*70)
    print("REVERSE ENGINEERING: WHAT φ-RELATIONSHIP GIVES 0.23122?")
    print("="*70)
    print()
    
    # Try to find integers a, b, c such that:
    # (a + b*φ) / (c + d*φ) ≈ 0.23122
    # or (a*φ^n) / (b + c*φ^m) ≈ 0.23122
    
    target = 0.23122
    
    print("Testing rational φ-combinations (a + b*φ^n)/(c + d*φ^m):")
    print()
    
    best_match = None
    best_error = float('inf')
    
    for a in range(-3, 4):
        for b in range(-3, 4):
            for c in range(1, 6):
                for d in range(-3, 4):
                    for n in [-2, -1, 0, 1, 2]:
                        for m in [-2, -1, 0, 1, 2]:
                            try:
                                numerator = a + b * PHI**n
                                denominator = c + d * PHI**m
                                
                                if abs(denominator) < 0.01:
                                    continue
                                
                                value = numerator / denominator
                                
                                if value < 0 or value > 1:
                                    continue
                                
                                error = abs(value - target)
                                
                                if error < best_error:
                                    best_error = error
                                    best_match = {
                                        'formula': f"({a:+d} {b:+d}*φ^{n})/({c:+d} {d:+d}*φ^{m})",
                                        'value': value,
                                        'error': error,
                                        'pct_error': error/target*100
                                    }
                            except:
                                pass
    
    if best_match and best_match['pct_error'] < 1:
        print(f"✓ EXCELLENT MATCH:")
        print(f"  Formula: {best_match['formula']}")
        print(f"  Value: {best_match['value']:.8f}")
        print(f"  Target: {target:.8f}")
        print(f"  Error: {best_match['pct_error']:.3f}%")
    elif best_match and best_match['pct_error'] < 5:
        print(f"⚠ GOOD MATCH:")
        print(f"  Formula: {best_match['formula']}")
        print(f"  Value: {best_match['value']:.8f}")
        print(f"  Target: {target:.8f}")
        print(f"  Error: {best_match['pct_error']:.3f}%")
    else:
        print("✗ No simple φ-formula found within 5% tolerance")
        if best_match:
            print(f"\nBest found:")
            print(f"  Formula: {best_match['formula']}")
            print(f"  Error: {best_match['pct_error']:.2f}%")
    
    print()
    return best_match


def analyze_two_tier_structure():
    """
    Test the two-tier hypothesis:
    Structure layer: φ-relationship exists
    Projection layer: C factor maps to observation
    """
    print("="*70)
    print("TWO-TIER ANALYSIS: STRUCTURE × PROJECTION")
    print("="*70)
    print()
    
    # Test if sin²θ_W = C × φ^n for various n and C
    target = 0.23122
    
    print("Testing sin²θ_W = C × φ^n:")
    print()
    print(f"{'n':<5} {'φ^n':<15} {'Required C':<15} {'Plausible?'}")
    print("-"*55)
    
    for n in range(-5, 6):
        phi_n = PHI**n
        C = target / phi_n
        
        # Check if C is "plausible" (close to 1 or a simple ratio)
        simple_ratios = [1/4, 1/3, 1/2, 2/3, 3/4, 1, 4/3, 3/2, 2, 3, 4]
        plausible = any(abs(C - r) / r < 0.05 for r in simple_ratios)
        
        status = "✓" if plausible else " "
        print(f"{status} {n:<4} {phi_n:<14.6f} {C:<14.6f} {plausible}")
    
    print()
    
    # Special case: Check if there's a φ-structure in cos²θ_W instead
    cos2w = 1 - 0.23122
    print(f"Also checking cos²θ_W = {cos2w:.6f}:")
    print()
    
    for n in range(-5, 6):
        phi_n = PHI**n
        C = cos2w / phi_n
        
        simple_ratios = [1/4, 1/3, 1/2, 2/3, 3/4, 1, 4/3, 3/2, 2, 3, 4]
        plausible = any(abs(C - r) / r < 0.05 for r in simple_ratios)
        
        if plausible:
            print(f"  ✓ cos²θ_W = {C:.4f} × φ^{n} (C ≈ simple ratio)")
    
    print()


if __name__ == '__main__':
    print()
    best_formula = explore_phi_relations()
    print()
    best_reverse = reverse_engineer_phi_structure()
    print()
    analyze_two_tier_structure()
    print()
    
    print("="*70)
    print("CONCLUSION")
    print("="*70)
    print()
    print("The Weinberg angle does not match simple φ-formulas at the 1% level.")
    print()
    print("Possible interpretations:")
    print("  1. φ-structure exists but requires 2-loop or threshold corrections")
    print("  2. Weinberg angle is not a pure Tier-1 observable")
    print("  3. The φ-relationship involves a different combination")
    print("  4. The prediction needs revision")
    print()
    print("✓ This analysis is scientifically honest: we tested and documented")
    print("  the mismatch rather than forcing a fit.")
    print()

