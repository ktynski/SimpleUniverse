#!/usr/bin/env python3
"""
Complete Audit of All Formulas in Theory.md

Systematically verifies every numerical claim in the SCCMU theory.
Reports discrepancies honestly without fake fallbacks.
"""

import numpy as np
from typing import Tuple, Dict

PHI = (1 + np.sqrt(5)) / 2


class FormulaAuditor:
    """Systematic verification of Theory.md formulas"""
    
    def __init__(self):
        self.results = []
        self.critical_failures = 0
        self.moderate_issues = 0
        self.passes = 0
    
    def check_formula(self, name: str, formula_str: str, 
                     computed: float, claimed: float, observed: float,
                     tolerance_percent: float = 1.0, critical: bool = True) -> Dict:
        """
        Check a single formula
        
        Returns: dict with status and analysis
        """
        error_vs_claimed = abs(computed - claimed) / abs(claimed) * 100 if claimed != 0 else float('inf')
        error_vs_observed = abs(computed - observed) / abs(observed) * 100 if observed != 0 else float('inf')
        
        # Determine status
        if error_vs_claimed < tolerance_percent and error_vs_observed < tolerance_percent:
            status = '✅ PASS'
            self.passes += 1
        elif error_vs_claimed > 50:
            status = '🔴 CRITICAL' if critical else '🟡 MODERATE'
            if critical:
                self.critical_failures += 1
            else:
                self.moderate_issues += 1
        else:
            status = '🟡 MODERATE'
            self.moderate_issues += 1
        
        result = {
            'name': name,
            'formula': formula_str,
            'computed': computed,
            'claimed': claimed,
            'observed': observed,
            'error_vs_claimed_percent': error_vs_claimed,
            'error_vs_observed_percent': error_vs_observed,
            'status': status,
            'critical': critical
        }
        
        self.results.append(result)
        return result
    
    def print_result(self, result: Dict):
        """Print a single result"""
        print(f"\n{result['status']} {result['name']}")
        print(f"{'─' * 60}")
        print(f"Formula: {result['formula']}")
        print(f"  Computed:       {result['computed']:.6g}")
        print(f"  Claimed in doc: {result['claimed']:.6g}")
        print(f"  Observed:       {result['observed']:.6g}")
        print(f"  Error vs claim: {result['error_vs_claimed_percent']:.1f}%")
        print(f"  Error vs obs:   {result['error_vs_observed_percent']:.1f}%")
        
        if result['error_vs_claimed_percent'] > 10:
            factor = result['claimed'] / result['computed'] if result['computed'] != 0 else 0
            print(f"  ⚠ Missing factor: ~{factor:.2f}")
    
    def run_complete_audit(self):
        """Run audit of all formulas"""
        print("="*60)
        print("  COMPLETE THEORY.MD FORMULA AUDIT")
        print("="*60)
        
        # Test 1: Fine structure constant
        alpha_inv_computed = 4 * (np.pi**3) / (PHI**11)
        r = self.check_formula(
            "Fine Structure Constant",
            "α^(-1) = 4π³/φ^11",
            alpha_inv_computed,
            137.036,
            137.035999,
            tolerance_percent=1.0,
            critical=True
        )
        self.print_result(r)
        
        # Test 2: Lepton mass ratio μ/e
        mu_e_computed = PHI**7
        r = self.check_formula(
            "Lepton Mass Ratio m_μ/m_e",
            "φ^7",
            mu_e_computed,
            207.0,
            206.768,
            tolerance_percent=1.0,
            critical=True
        )
        self.print_result(r)
        
        # Test 3: Lepton mass ratio τ/μ
        tau_mu_computed = PHI**3
        r = self.check_formula(
            "Lepton Mass Ratio m_τ/m_μ",
            "φ^3",
            tau_mu_computed,
            16.8,
            16.817,
            tolerance_percent=1.0,
            critical=True
        )
        self.print_result(r)
        
        # Test 4: Weinberg angle
        cos2_theta_computed = PHI / (2 - PHI)
        r = self.check_formula(
            "Weinberg Angle (tree level)",
            "cos²θ_W = φ/(2-φ)",
            cos2_theta_computed,
            0.8097,
            0.7764,
            tolerance_percent=5.0,
            critical=True
        )
        self.print_result(r)
        
        # Test 5: Proton-electron mass ratio
        mp_me_computed = 32 * (np.pi**5) / (3 * PHI**2)
        r = self.check_formula(
            "Proton-Electron Mass Ratio",
            "32π^5/(3φ²)",
            mp_me_computed,
            1836.15,
            1836.152,
            tolerance_percent=1.0,
            critical=False
        )
        self.print_result(r)
        
        # Test 6: Dark energy
        rho_lambda_computed = PHI**(-250)
        rho_observed_planck = 1e-52  # Order of magnitude in Planck units
        r = self.check_formula(
            "Dark Energy Density",
            "φ^(-250)",
            rho_lambda_computed,
            1e-52,
            rho_observed_planck,
            tolerance_percent=50.0,  # Order of magnitude test
            critical=False
        )
        self.print_result(r)
        
        # Test 7: Strong coupling
        alpha_s_computed = (PHI**2) / (4 * np.pi)
        r = self.check_formula(
            "Strong Coupling α_s(m_Z)",
            "φ²/(4π)",
            alpha_s_computed,
            0.118,
            0.118,
            tolerance_percent=5.0,
            critical=False
        )
        self.print_result(r)
        
        # Test 8: Higgs mass (tree level)
        lambda_h = 1 / (PHI**3)
        v_higgs = 246  # GeV
        m_H_computed = np.sqrt(2 * lambda_h) * v_higgs
        r = self.check_formula(
            "Higgs Mass (tree level)",
            "√(2/φ³) × 246 GeV",
            m_H_computed,
            169,
            125,
            tolerance_percent=10.0,
            critical=False
        )
        self.print_result(r)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive summary"""
        print("\n" + "="*60)
        print("  AUDIT SUMMARY")
        print("="*60)
        print()
        print(f"Total formulas checked: {len(self.results)}")
        print(f"  ✅ Passes:            {self.passes}")
        print(f"  🟡 Moderate issues:   {self.moderate_issues}")
        print(f"  🔴 Critical failures: {self.critical_failures}")
        print()
        
        if self.critical_failures > 0:
            print(f"{'⚠'*30}")
            print(f"  {self.critical_failures} CRITICAL FORMULA ERRORS FOUND")
            print(f"{'⚠'*30}")
            print()
            print("Critical failures:")
            for r in self.results:
                if '🔴' in r['status']:
                    factor = r['claimed'] / r['computed'] if r['computed'] != 0 else 0
                    print(f"  • {r['name']}")
                    print(f"    Formula gives {r['computed']:.4g}, claims {r['claimed']:.4g}")
                    print(f"    Missing factor: ~{factor:.2f}")
            print()
        
        # Determine overall status
        print("="*60)
        if self.critical_failures == 0 and self.moderate_issues == 0:
            print("  STATUS: ✅ ALL FORMULAS CORRECT")
        elif self.critical_failures == 0:
            print("  STATUS: ⚠️  MINOR ISSUES ONLY")
        else:
            print("  STATUS: 🔴 MAJOR ISSUES - THEORY NEEDS REVISION")
        print("="*60)
        print()
        
        # Recommendations
        print("RECOMMENDATIONS:")
        print()
        if self.critical_failures > 0:
            print("1. 🔴 URGENT: Fix or caveat all critical formula errors")
            print("2. Distinguish 'derived exponents' from 'complete formulas'")
            print("3. Be honest about incomplete normalizations")
            print("4. Research missing factors systematically")
            print()
            print("The theory's STRUCTURE (φ-scaling) may be correct even if")
            print("exact FORMULAS need work. Don't oversell current status.")
        else:
            print("✓ Formulas are sound. Continue with testing and validation.")
        print()


def main():
    """Run complete formula audit"""
    auditor = FormulaAuditor()
    auditor.run_complete_audit()
    
    # Return error code if critical failures found
    return 1 if auditor.critical_failures > 0 else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

