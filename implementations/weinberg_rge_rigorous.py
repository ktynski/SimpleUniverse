#!/usr/bin/env python3
"""
Rigorous Weinberg Angle RGE Test
Boundary: g'/g = 1/φ at μ_GUT
Evolution: 1-loop SM RGEs (MS-bar)
Target: sin²θ_W(M_Z) ≈ 0.231
"""

import numpy as np
import matplotlib.pyplot as plt

PHI = (1 + np.sqrt(5)) / 2

# One-loop beta coefficients (SU(5)-normalized U(1)_Y)
B1 = 41 / 10
B2 = -19 / 6

# Physical inputs
M_Z = 91.1876  # GeV
ALPHA_EM_MZ = 1 / 127.95  # QED at M_Z

def alpha_inv_run(alpha_inv_mu0, b, mu, mu0):
    """One-loop RG evolution of α^(-1)"""
    return alpha_inv_mu0 - (b / (2 * np.pi)) * np.log(mu / mu0)

def sin2_theta_w(alpha1_inv, alpha2_inv):
    """Compute sin²θ_W from gauge couplings"""
    a1 = 1.0 / alpha1_inv
    a2 = 1.0 / alpha2_inv
    g1_sq = 4 * np.pi * a1
    g2_sq = 4 * np.pi * a2
    return g1_sq / (g1_sq + g2_sq)

def test_weinberg_boundary(mu_gut_range, verbose=True):
    """
    Test g'/g = 1/φ boundary condition at various μ_GUT
    
    Returns: dict with μ_GUT values where sin²θ_W(M_Z) ≈ 0.231
    """
    results = []
    
    for mu_gut in mu_gut_range:
        # Boundary condition: g'/g = 1/φ at μ_GUT
        # With g'^2 = 4πα₁, g^2 = 4πα₂
        # (g'/g)^2 = α₁/α₂ = 1/φ^2
        
        # Need α₁(μ_GUT) + α₂(μ_GUT) = some total; split by ratio
        # Use α_EM(M_Z) as reference, evolve backwards to get plausible GUT values
        
        # Backwards evolution to guess reasonable GUT couplings
        # Start with α₁(M_Z) ≈ 0.0102, α₂(M_Z) ≈ 0.0337 (approximate SM values)
        alpha1_inv_mz = 98.0
        alpha2_inv_mz = 29.7
        
        # Evolve to μ_GUT
        alpha1_inv_gut = alpha_inv_run(alpha1_inv_mz, B1, mu_gut, M_Z)
        alpha2_inv_gut = alpha_inv_run(alpha2_inv_mz, B2, mu_gut, M_Z)
        
        # Check ratio at GUT scale
        alpha1_gut = 1 / alpha1_inv_gut
        alpha2_gut = 1 / alpha2_inv_gut
        ratio_gut = np.sqrt(alpha1_gut / alpha2_gut)
        
        # Apply φ boundary condition: rescale to enforce g'/g = 1/φ
        target_ratio = 1 / PHI
        scale_factor = target_ratio / ratio_gut
        
        # Rescale α₁ to match boundary
        alpha1_gut_corrected = alpha1_gut * scale_factor**2
        alpha1_inv_gut_corrected = 1 / alpha1_gut_corrected
        
        # Now evolve both back down to M_Z
        alpha1_inv_mz_new = alpha_inv_run(alpha1_inv_gut_corrected, B1, M_Z, mu_gut)
        alpha2_inv_mz_new = alpha_inv_run(alpha2_inv_gut, B2, M_Z, mu_gut)
        
        # Compute sin²θ_W at M_Z
        sin2w_mz = sin2_theta_w(alpha1_inv_mz_new, alpha2_inv_mz_new)
        
        results.append({
            'mu_gut': mu_gut,
            'sin2w_mz': sin2w_mz,
            'alpha1_inv_gut': alpha1_inv_gut_corrected,
            'alpha2_inv_gut': 1/alpha2_gut,
            'ratio_gut': target_ratio,
            'deviation': abs(sin2w_mz - 0.231)
        })
        
        if verbose and abs(sin2w_mz - 0.231) < 0.005:
            print(f"μ_GUT = {mu_gut:.2e} GeV:")
            print(f"  sin²θ_W(M_Z) = {sin2w_mz:.4f} (target: 0.231)")
            print(f"  g'/g at GUT = {target_ratio:.4f} (= 1/φ = {1/PHI:.4f})")
            print(f"  deviation = {abs(sin2w_mz - 0.231):.5f}")
            print()
    
    return results

def main():
    print("="*70)
    print("RIGOROUS WEINBERG ANGLE RGE TEST")
    print("="*70)
    print(f"\nBoundary condition: g'/g = 1/φ = {1/PHI:.6f} at μ_GUT")
    print(f"Target: sin²θ_W(M_Z) = 0.231 (observed: 0.23122)")
    print(f"Method: 1-loop SM RGEs with b₁={B1}, b₂={B2}")
    print("\n" + "-"*70 + "\n")
    
    # Scan GUT scales
    mu_gut_range = np.logspace(15, 17, 50)  # 10^15 to 10^17 GeV
    
    results = test_weinberg_boundary(mu_gut_range, verbose=True)
    
    # Find best match
    best = min(results, key=lambda r: r['deviation'])
    
    print("\n" + "="*70)
    print("BEST MATCH:")
    print("="*70)
    print(f"μ_GUT = {best['mu_gut']:.3e} GeV")
    print(f"sin²θ_W(M_Z) = {best['sin2w_mz']:.5f}")
    print(f"Observed value = 0.23122")
    print(f"Deviation = {best['deviation']:.5f}")
    print(f"Percent error = {best['deviation']/0.231 * 100:.2f}%")
    
    if best['deviation'] < 0.001:
        print("\n✓ CONFIRMED: φ boundary reproduces Weinberg angle within ±0.001")
    elif best['deviation'] < 0.005:
        print("\n⚠ PARTIAL: φ boundary matches within ±0.005 (1-loop uncertainty)")
    else:
        print("\n✗ FAILED: Cannot reproduce sin²θ_W(M_Z) from φ boundary")
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    mu_guts = [r['mu_gut'] for r in results]
    sin2ws = [r['sin2w_mz'] for r in results]
    
    ax1.semilogx(mu_guts, sin2ws, 'b-', linewidth=2, label='From φ boundary')
    ax1.axhline(0.231, color='r', linestyle='--', label='Target (0.231)')
    ax1.fill_between(mu_guts, 0.230, 0.232, alpha=0.2, color='r', label='±0.001 band')
    ax1.set_xlabel('μ_GUT (GeV)', fontsize=12)
    ax1.set_ylabel('sin²θ_W(M_Z)', fontsize=12)
    ax1.set_title('Weinberg Angle from φ Boundary + RGE', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    deviations = [r['deviation'] for r in results]
    ax2.loglog(mu_guts, deviations, 'g-', linewidth=2)
    ax2.axhline(0.001, color='r', linestyle='--', label='±0.001 target')
    ax2.set_xlabel('μ_GUT (GeV)', fontsize=12)
    ax2.set_ylabel('|sin²θ_W - 0.231|', fontsize=12)
    ax2.set_title('Deviation from Target', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, which='both')
    ax2.legend()
    
    plt.tight_layout(pad=2.0)
    plt.savefig('results/data/weinberg_rge_test.png', dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nPlot saved: weinberg_rge_test.png")
    
    return results, best

if __name__ == '__main__':
    results, best = main()

