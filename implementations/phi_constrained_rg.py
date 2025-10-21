#!/usr/bin/env python3
"""
φ-Constrained Renormalization Group Theory

Core Insight: If φ is a fundamental information invariant, RG flow must preserve
the mutual information ratio I(A:B)/I(B:C) = φ across all energy scales.

This constrains the allowed form of β-functions.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, minimize
from scipy.integrate import odeint

PHI = (1 + np.sqrt(5)) / 2

class PhiConstrainedRG:
    """
    Implements RG flow with the constraint that coherence ratios remain at φ
    
    Key hypothesis: Standard β-functions are φ-blind projections.
    True β-functions must satisfy:
        d/d(log μ) [I(A:B)/I(B:C)] = 0
    """
    
    def __init__(self):
        self.phi = PHI
        
    def standard_beta_functions(self, alpha, b_coeffs):
        """
        Standard 1-loop β-function: β_i = b_i α_i² / (2π)
        
        This is the φ-blind version used in conventional QFT
        """
        return np.array([b * a**2 / (2 * np.pi) for a, b in zip(alpha, b_coeffs)])
    
    def phi_constraint_correction(self, alpha, b_coeffs):
        """
        Compute the correction term needed to preserve φ-structure
        
        Hypothesis: True β = β_standard + β_phi_correction
        where β_phi_correction ensures MI ratios stay at φ
        """
        # If couplings encode tripartite information structure, then
        # α_1, α_2, α_3 might correspond to I(A:B), I(B:C), I(A:C)
        
        # Constraint: α_1/α_2 should flow toward φ
        current_ratio = alpha[0] / alpha[1] if len(alpha) > 1 else 1.0
        ratio_error = current_ratio - self.phi
        
        # Correction proportional to deviation from φ
        # This is a phenomenological ansatz; the true form needs derivation
        correction_strength = 0.1  # Tunable parameter (should be derived)
        
        corrections = np.zeros_like(alpha)
        if len(alpha) > 1:
            # Drive α_1/α_2 toward φ
            corrections[0] = correction_strength * ratio_error * alpha[0]
            corrections[1] = -correction_strength * ratio_error * alpha[1]
        
        return corrections
    
    def phi_constrained_beta(self, alpha, b_coeffs, use_constraint=True):
        """
        Full β-function with φ-constraint
        """
        beta_standard = self.standard_beta_functions(alpha, b_coeffs)
        
        if use_constraint:
            beta_correction = self.phi_constraint_correction(alpha, b_coeffs)
            return beta_standard + beta_correction
        else:
            return beta_standard
    
    def rg_flow_equations(self, alpha, log_mu, b_coeffs, use_constraint=True):
        """
        RG flow: dα/d(log μ) = β(α)
        """
        beta = self.phi_constrained_beta(alpha, b_coeffs, use_constraint)
        return beta
    
    def evolve(self, alpha_initial, log_mu_initial, log_mu_final, 
               b_coeffs, use_constraint=True, num_steps=1000):
        """
        Evolve couplings from μ_initial to μ_final
        """
        log_mu_range = np.linspace(log_mu_initial, log_mu_final, num_steps)
        
        solution = odeint(
            self.rg_flow_equations,
            alpha_initial,
            log_mu_range,
            args=(b_coeffs, use_constraint)
        )
        
        return log_mu_range, solution


def test_weinberg_with_phi_constraint():
    """
    Test: Does φ-constrained RG reproduce Weinberg angle?
    """
    print("="*70)
    print("WEINBERG ANGLE: φ-CONSTRAINED RG TEST")
    print("="*70)
    print()
    
    # SM beta coefficients (SU(5) normalized)
    B1 = 41 / 10
    B2 = -19 / 6
    b_coeffs = [B1, B2]
    
    # Energy scales
    M_Z = 91.1876  # GeV
    mu_gut = 2e16   # GeV
    
    log_mu_gut = np.log(mu_gut)
    log_mu_z = np.log(M_Z)
    
    # Initial conditions at GUT scale with φ boundary
    # Set α_1/α_2 = 1/φ² at GUT scale
    alpha_gut_total = 1/25.0  # Approximate unified coupling
    
    # Split according to φ
    # α_1 / α_2 = 1/φ²
    # α_1 + α_2 = alpha_gut_total
    # Solving: α_1 = alpha_gut_total / (1 + φ²), α_2 = alpha_gut_total * φ² / (1 + φ²)
    
    alpha1_gut = alpha_gut_total / (1 + PHI**2)
    alpha2_gut = alpha_gut_total - alpha1_gut
    
    print(f"Boundary condition at μ_GUT = {mu_gut:.2e} GeV:")
    print(f"  α₁(μ_GUT) = {alpha1_gut:.6f}")
    print(f"  α₂(μ_GUT) = {alpha2_gut:.6f}")
    print(f"  α₁/α₂ = {alpha1_gut/alpha2_gut:.6f} (target: {1/PHI**2:.6f})")
    print(f"  g'/g = {np.sqrt(alpha1_gut/alpha2_gut):.6f} (target: {1/PHI:.6f})")
    print()
    
    # Evolve with standard RG
    rg = PhiConstrainedRG()
    
    print("Standard RG (φ-blind):")
    print("-" * 40)
    log_mu_std, alpha_std = rg.evolve(
        [alpha1_gut, alpha2_gut],
        log_mu_gut,
        log_mu_z,
        b_coeffs,
        use_constraint=False
    )
    
    alpha1_z_std = alpha_std[-1, 0]
    alpha2_z_std = alpha_std[-1, 1]
    sin2w_std = alpha1_z_std / (alpha1_z_std + alpha2_z_std)
    
    print(f"  α₁(M_Z) = {alpha1_z_std:.6f}")
    print(f"  α₂(M_Z) = {alpha2_z_std:.6f}")
    print(f"  sin²θ_W(M_Z) = {sin2w_std:.5f}")
    print(f"  Target: 0.23122")
    print(f"  Error: {abs(sin2w_std - 0.23122)/0.23122 * 100:.1f}%")
    print()
    
    # Evolve with φ-constrained RG
    print("φ-Constrained RG:")
    print("-" * 40)
    log_mu_phi, alpha_phi = rg.evolve(
        [alpha1_gut, alpha2_gut],
        log_mu_gut,
        log_mu_z,
        b_coeffs,
        use_constraint=True
    )
    
    alpha1_z_phi = alpha_phi[-1, 0]
    alpha2_z_phi = alpha_phi[-1, 1]
    sin2w_phi = alpha1_z_phi / (alpha1_z_phi + alpha2_z_phi)
    
    print(f"  α₁(M_Z) = {alpha1_z_phi:.6f}")
    print(f"  α₂(M_Z) = {alpha2_z_phi:.6f}")
    print(f"  sin²θ_W(M_Z) = {sin2w_phi:.5f}")
    print(f"  Target: 0.23122")
    print(f"  Error: {abs(sin2w_phi - 0.23122)/0.23122 * 100:.1f}%")
    print()
    
    # Plot comparison
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 6))
    
    # Plot 1: Coupling evolution
    mu_range_std = np.exp(log_mu_std)
    mu_range_phi = np.exp(log_mu_phi)
    
    ax1.loglog(mu_range_std, alpha_std[:, 0], 'b-', label='α₁ (standard)', linewidth=2)
    ax1.loglog(mu_range_std, alpha_std[:, 1], 'r-', label='α₂ (standard)', linewidth=2)
    ax1.loglog(mu_range_phi, alpha_phi[:, 0], 'b--', label='α₁ (φ-constrained)', linewidth=2)
    ax1.loglog(mu_range_phi, alpha_phi[:, 1], 'r--', label='α₂ (φ-constrained)', linewidth=2)
    ax1.set_xlabel('μ (GeV)', fontsize=12)
    ax1.set_ylabel('α_i', fontsize=12)
    ax1.set_title('Coupling Evolution', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3, which='both')
    
    # Plot 2: Ratio evolution
    ratio_std = alpha_std[:, 0] / alpha_std[:, 1]
    ratio_phi = alpha_phi[:, 0] / alpha_phi[:, 1]
    
    ax2.semilogx(mu_range_std, ratio_std, 'b-', label='Standard RG', linewidth=2)
    ax2.semilogx(mu_range_phi, ratio_phi, 'r-', label='φ-Constrained RG', linewidth=2)
    ax2.axhline(1/PHI**2, color='g', linestyle='--', linewidth=2, label=f'1/φ² = {1/PHI**2:.3f}')
    ax2.set_xlabel('μ (GeV)', fontsize=12)
    ax2.set_ylabel('α₁/α₂', fontsize=12)
    ax2.set_title('Coupling Ratio Evolution', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: sin²θ_W evolution
    sin2w_evolution_std = alpha_std[:, 0] / (alpha_std[:, 0] + alpha_std[:, 1])
    sin2w_evolution_phi = alpha_phi[:, 0] / (alpha_phi[:, 0] + alpha_phi[:, 1])
    
    ax3.semilogx(mu_range_std, sin2w_evolution_std, 'b-', label='Standard RG', linewidth=2)
    ax3.semilogx(mu_range_phi, sin2w_evolution_phi, 'r-', label='φ-Constrained RG', linewidth=2)
    ax3.axhline(0.23122, color='g', linestyle='--', linewidth=2, label='Observed (0.23122)')
    ax3.fill_between([M_Z, mu_gut], 0.23022, 0.23222, alpha=0.2, color='g')
    ax3.set_xlabel('μ (GeV)', fontsize=12)
    ax3.set_ylabel('sin²θ_W(μ)', fontsize=12)
    ax3.set_title('Weinberg Angle Running', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout(pad=2.0)
    plt.savefig('results/data/phi_constrained_rg_weinberg.png', dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Plot saved: phi_constrained_rg_weinberg.png")
    print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    improvement = abs(sin2w_std - 0.23122) - abs(sin2w_phi - 0.23122)
    print(f"Standard RG error: {abs(sin2w_std - 0.23122)/0.23122 * 100:.2f}%")
    print(f"φ-Constrained RG error: {abs(sin2w_phi - 0.23122)/0.23122 * 100:.2f}%")
    print(f"Improvement: {improvement/0.23122 * 100:.2f} percentage points")
    print()
    
    if abs(sin2w_phi - 0.23122) < 0.01:
        print("✓ φ-Constrained RG SIGNIFICANTLY IMPROVES agreement")
    elif improvement > 0:
        print("⚠ φ-Constrained RG shows improvement but needs refinement")
    else:
        print("✗ φ-Constrained RG does not improve prediction")
    
    return {
        'standard': sin2w_std,
        'phi_constrained': sin2w_phi,
        'target': 0.23122,
        'improvement': improvement
    }


if __name__ == '__main__':
    results = test_weinberg_with_phi_constraint()

