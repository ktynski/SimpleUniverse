#!/usr/bin/env python3
"""
Systematic Search for Exact α^(-1) Formula

Goal: Find φ-formula matching α^(-1) = 127.955 to <0.1% error

Method: Exhaustive search over:
- Simple φ-combinations
- Rational coefficients with π
- Products and ratios
- No guessing—systematic enumeration
"""

import numpy as np
from itertools import product

PHI = (1 + np.sqrt(5)) / 2
ALPHA_INV_OBSERVED = 127.955

def search_simple_formulas():
    """
    Search: a × π^m × φ^n
    """
    print("="*70)
    print("SYSTEMATIC SEARCH: a × π^m × φ^n")
    print("="*70)
    print()
    
    target = ALPHA_INV_OBSERVED
    best_matches = []
    
    print(f"Target: α^(-1) = {target:.6f}")
    print()
    print(f"{'Formula':<30} {'Value':<15} {'Error %':<10}")
    print("-"*70)
    
    # Search over reasonable ranges
    for a in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 32]:
        for m in range(0, 5):
            for n in range(-3, 4):
                value = a * (np.pi**m) * (PHI**n)
                error = abs(value - target) / target * 100
                
                if error < 1.0:
                    formula = f"{a}π^{m}φ^{n}" if m > 0 else f"{a}φ^{n}"
                    best_matches.append((formula, value, error))
                    print(f"{formula:<30} {value:<15.6f} {error:<10.6f}")
    
    print()
    
    if best_matches:
        best = min(best_matches, key=lambda x: x[2])
        print(f"✅ BEST MATCH: {best[0]} = {best[1]:.6f} (error: {best[2]:.4f}%)")
    else:
        print("No matches within 1% found in simple search")
    
    print()
    return best_matches


def search_rational_combinations():
    """
    Search: (a + b×φ^n) / (c + d×φ^m) × π^k
    """
    print("="*70)
    print("SYSTEMATIC SEARCH: Rational φ-Combinations × π^k")
    print("="*70)
    print()
    
    target = ALPHA_INV_OBSERVED
    best_matches = []
    
    print("Searching (a + b×φ^n)/(c + d×φ^m) × π^k...")
    print()
    
    for a in range(-5, 6):
        for b in range(-5, 6):
            for c in range(1, 6):
                for d in range(-5, 6):
                    for n in [-2, -1, 0, 1, 2]:
                        for m in [-2, -1, 0, 1, 2]:
                            for k in range(0, 4):
                                try:
                                    numerator = a + b * (PHI**n)
                                    denominator = c + d * (PHI**m)
                                    
                                    if abs(denominator) < 0.01:
                                        continue
                                    
                                    value = (numerator / denominator) * (np.pi**k)
                                    
                                    if value < 0 or value > 200:
                                        continue
                                    
                                    error = abs(value - target) / target * 100
                                    
                                    if error < 0.1:  # <0.1% error
                                        formula = f"({a:+d}{b:+d}φ^{n})/({c:+d}{d:+d}φ^{m})×π^{k}"
                                        best_matches.append((formula, value, error))
                                except:
                                    pass
    
    # Sort by error
    best_matches.sort(key=lambda x: x[2])
    
    print(f"Found {len(best_matches)} matches with <0.1% error:")
    print()
    
    if best_matches:
        print(f"{'Formula':<50} {'Value':<15} {'Error %':<10}")
        print("-"*75)
        for formula, value, error in best_matches[:10]:  # Top 10
            print(f"{formula:<50} {value:<15.8f} {error:<10.6f}")
    else:
        print("No matches with <0.1% error found")
    
    print()
    return best_matches


def search_products_with_integers():
    """
    Search: (integer from theory) × π^m × φ^n
    
    Theory integers: 7, 11, 3, 6, 250
    """
    print("="*70)
    print("SYSTEMATIC SEARCH: Theory Integers × π^m × φ^n")
    print("="*70)
    print()
    
    target = ALPHA_INV_OBSERVED
    theory_integers = [3, 6, 7, 11, 12, 24, 248, 250]
    
    best_matches = []
    
    print(f"Using theory-derived integers: {theory_integers}")
    print()
    print(f"{'Formula':<35} {'Value':<15} {'Error %':<10}")
    print("-"*70)
    
    for integer in theory_integers:
        for m in range(0, 4):
            for n in range(-3, 3):
                value = integer * (np.pi**m) * (PHI**n)
                error = abs(value - target) / target * 100
                
                if error < 0.5:
                    formula = f"{integer}π^{m}φ^{n}" if m > 0 else f"{integer}φ^{n}"
                    best_matches.append((formula, value, error))
                    print(f"{formula:<35} {value:<15.6f} {error:<10.6f}")
    
    print()
    
    if best_matches:
        best = min(best_matches, key=lambda x: x[2])
        print(f"✅ BEST: {best[0]} = {best[1]:.8f} (error: {best[2]:.6f}%)")
    
    print()
    return best_matches


def verify_best_formula(formula_str, value):
    """
    Verify a candidate formula rigorously
    """
    print("="*70)
    print(f"RIGOROUS VERIFICATION: {formula_str}")
    print("="*70)
    print()
    
    target = ALPHA_INV_OBSERVED
    error = abs(value - target) / target * 100
    
    print(f"Formula: α^(-1) = {formula_str}")
    print(f"Computed: {value:.10f}")
    print(f"Observed: {target:.10f}")
    print(f"Deviation: {abs(value - target):.10f}")
    print(f"Error: {error:.8f}%")
    print()
    
    if error < 0.01:
        print("✅ EXCELLENT: <0.01% error (Tier-1 precision)")
        tier = 1
    elif error < 0.1:
        print("✅ VERY GOOD: <0.1% error (High Tier-1)")
        tier = 1
    elif error < 0.5:
        print("✅ GOOD: <0.5% error (Tier-1)")
        tier = 1
    elif error < 1.0:
        print("⚠️ ACCEPTABLE: <1% error (Borderline Tier-1)")
        tier = 1.5
    else:
        print("❌ TOO LARGE: >1% error (Not Tier-1)")
        tier = 2
    
    print()
    return tier


def main():
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   EXHAUSTIVE SEARCH: EXACT α^(-1) FORMULA FROM φ            ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Search 1: Simple formulas
    simple = search_simple_formulas()
    
    # Search 2: Theory integers
    theory_int = search_products_with_integers()
    
    # Search 3: Rational combinations
    rational = search_rational_combinations()
    
    # Find absolute best
    all_matches = simple + theory_int + rational
    
    if all_matches:
        all_matches.sort(key=lambda x: x[2])
        
        print("="*70)
        print("TOP 5 BEST MATCHES")
        print("="*70)
        print()
        print(f"{'Rank':<6} {'Formula':<45} {'Value':<15} {'Error %':<10}")
        print("-"*76)
        
        for i, (formula, value, error) in enumerate(all_matches[:5], 1):
            print(f"{i:<6} {formula:<45} {value:<15.8f} {error:<10.6f}")
        
        print()
        
        # Verify the best
        best_formula, best_value, best_error = all_matches[0]
        tier = verify_best_formula(best_formula, best_value)
        
        print("="*70)
        print("CONCLUSION")
        print("="*70)
        print()
        
        if tier == 1 and best_error < 0.1:
            print(f"✅ EXACT FORMULA FOUND: α^(-1) = {best_formula}")
            print(f"   Error: {best_error:.6f}% (Tier-1 precision)")
            print()
            print("This should replace the previous formula in Theory.md")
        elif tier == 1:
            print(f"✅ GOOD FORMULA: α^(-1) = {best_formula}")
            print(f"   Error: {best_error:.4f}% (Tier-1, but not perfect)")
        else:
            print(f"⚠️ Best match: {best_formula} has {best_error:.2f}% error")
            print("   No Tier-1 formula found")
    else:
        print("❌ NO MATCHES FOUND")
        print("   α may not have simple φ-structure")
    
    print()
    
    return all_matches


if __name__ == '__main__':
    matches = main()
    exit(0 if matches else 1)

