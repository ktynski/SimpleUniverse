#!/usr/bin/env python3
"""
Eigenspace Decomposition of Coherence Operator

Implements eigendecomposition of 𝒞 to reveal three-generation structure.

Theory.md Theorem 5.2.2 (lines 1737-1784):
    𝒞_F³ = 2𝒞_F + I
    → Three eigenvalues: λ₁ = φ, λ₂ = φω, λ₃ = φω²
    → Each eigenspace = one generation

Test with: python3 -m pytest sccmu_ui/test_eigenspace.py
"""

import numpy as np
from typing import List, Dict, Tuple
from .zx_core import ZXGraph, PHI
from .coherence import compute_coherence_matrix


def compute_eigendecomposition(C_matrix: np.ndarray) -> Dict:
    """
    Compute eigendecomposition of coherence operator.
    
    Theory.md: 𝒞 is symmetric, positive, compact
    → Has real eigenvalues and orthogonal eigenvectors
    
    Args:
        C_matrix: n×n coherence matrix
    
    Returns:
        Dictionary with:
        - eigenvalues: Sorted eigenvalues (descending)
        - eigenvectors: Corresponding eigenvectors (columns)
        - phi_indices: Indices of φ-related eigenvalues
        - generation_structure: Three-generation identification
    """
    # Eigendecomposition
    eigenvalues, eigenvectors = np.linalg.eigh(C_matrix)
    
    # Sort descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Identify φ-related eigenvalues
    phi_indices = identify_phi_eigenvalues(eigenvalues)
    
    # Identify three-generation structure
    generation_structure = identify_generations(eigenvalues, phi_indices)
    
    return {
        'eigenvalues': eigenvalues,
        'eigenvectors': eigenvectors,
        'phi_indices': phi_indices,
        'generation_structure': generation_structure,
        'num_eigenvalues': len(eigenvalues),
        'spectral_gap': float(eigenvalues[0] - eigenvalues[1]) if len(eigenvalues) > 1 else 0.0,
        'condition_number': float(eigenvalues[0] / eigenvalues[-1]) if eigenvalues[-1] > 0 else float('inf')
    }


def identify_phi_eigenvalues(eigenvalues: np.ndarray, tolerance: float = 0.1) -> List[int]:
    """
    Identify which eigenvalues are φ-related.
    
    Theory.md: Eigenvalues should be powers/multiples of φ
    
    Args:
        eigenvalues: Array of eigenvalues
        tolerance: Relative tolerance for matching
    
    Returns:
        List of indices for φ-related eigenvalues
    """
    phi_indices = []
    
    # φ powers to check: φ^k for k in [-2, 3]
    phi_powers = [PHI**k for k in range(-2, 4)]
    
    # Also check multiples: n*φ for small n
    phi_multiples = [n * PHI for n in range(1, 6)]
    phi_multiples += [n / PHI for n in range(1, 4)]
    
    targets = phi_powers + phi_multiples
    
    for i, lam in enumerate(eigenvalues):
        for target in targets:
            relative_error = abs(lam - target) / (target + 1e-10)
            if relative_error < tolerance:
                phi_indices.append(i)
                break
    
    return phi_indices


def identify_generations(eigenvalues: np.ndarray, phi_indices: List[int]) -> Dict:
    """
    Identify three-generation structure from eigenvalues.
    
    Theory.md Theorem 5.2.2:
    𝒞_F³ = 2𝒞_F + I
    → λ³ = 2λ + 1
    → Three roots: λ₁ = φ, λ₂ = φω, λ₃ = φω²
    
    where ω = exp(2πi/3) (cube root of unity)
    
    Args:
        eigenvalues: All eigenvalues
        phi_indices: Indices of φ-related eigenvalues
    
    Returns:
        Dictionary describing generation structure
    """
    # Cubic equation: λ³ - 2λ - 1 = 0
    # Roots: φ, φω, φω² where ω = exp(2πi/3)
    
    # Real parts of roots
    omega = np.exp(2j * np.pi / 3)
    lambda_1 = PHI  # φ
    lambda_2 = PHI * omega  # φω
    lambda_3 = PHI * omega**2  # φω²
    
    expected_real = [
        float(lambda_1.real),
        float(lambda_2.real),
        float(lambda_3.real)
    ]
    
    # Find closest matches in eigenvalues
    generations = []
    for i, expected in enumerate(expected_real):
        # Find closest eigenvalue
        if len(eigenvalues) > 0:
            errors = [abs(lam - expected) for lam in eigenvalues]
            best_idx = int(np.argmin(errors))
            best_error = errors[best_idx]
            
            generations.append({
                'generation': i + 1,
                'expected_eigenvalue': expected,
                'actual_eigenvalue': float(eigenvalues[best_idx]) if best_idx < len(eigenvalues) else None,
                'eigenvalue_index': best_idx,
                'error': float(best_error),
                'relative_error': float(best_error / (abs(expected) + 1e-10))
            })
    
    # Check if we have three distinct generations
    has_three_generations = len(set(g['eigenvalue_index'] for g in generations)) >= 3
    
    # Check cubic equation: λ³ = 2λ + 1
    cubic_check = []
    for lam in eigenvalues[:min(5, len(eigenvalues))]:  # Check top 5
        residual = abs(lam**3 - 2*lam - 1)
        cubic_check.append({
            'eigenvalue': float(lam),
            'cubic_residual': float(residual),
            'satisfies_cubic': residual < 0.1
        })
    
    return {
        'generations': generations,
        'has_three_generations': has_three_generations,
        'num_phi_eigenvalues': len(phi_indices),
        'cubic_equation_check': cubic_check,
        'theory_compliant': has_three_generations and len(phi_indices) >= 1
    }


def project_onto_eigenspace(rho: np.ndarray, 
                            eigenvectors: np.ndarray, 
                            eigenspace_indices: List[int]) -> np.ndarray:
    """
    Project ρ onto specified eigenspace.
    
    For generation i, this gives the "generation-i" component of ρ.
    
    Args:
        rho: Probability distribution
        eigenvectors: Eigenvector matrix (columns)
        eigenspace_indices: Which eigenspaces to project onto
    
    Returns:
        Projected distribution ρ_projected
    """
    # Project onto subspace spanned by selected eigenvectors
    V = eigenvectors[:, eigenspace_indices]  # Selected eigenvectors
    
    # Projection: ρ_proj = V(V^T ρ)
    coefficients = V.T @ rho
    rho_projected = V @ coefficients
    
    # Normalize
    if np.sum(rho_projected) > 0:
        rho_projected /= np.sum(rho_projected)
    
    return rho_projected


def analyze_generation_content(diagrams: List[ZXGraph], 
                               rho: np.ndarray,
                               eigendecomp: Dict) -> Dict:
    """
    Analyze how much of ρ is in each generation.
    
    Decomposes ρ = Σᵢ cᵢ ψᵢ where ψᵢ are eigenvectors.
    Groups by generation based on eigenvalue structure.
    
    Args:
        diagrams: ZX-diagrams
        rho: Probability distribution
        eigendecomp: Eigendecomposition from compute_eigendecomposition()
    
    Returns:
        Dictionary with generation weights
    """
    eigenvectors = eigendecomp['eigenvectors']
    generation_struct = eigendecomp['generation_structure']
    
    # Compute coefficients: ρ = Σᵢ cᵢ ψᵢ
    coefficients = eigenvectors.T @ rho
    
    # Group by generation
    generation_weights = []
    
    for gen_info in generation_struct['generations']:
        gen_idx = gen_info['eigenvalue_index']
        if gen_idx < len(coefficients):
            weight = abs(coefficients[gen_idx])
            generation_weights.append({
                'generation': gen_info['generation'],
                'weight': float(weight),
                'eigenvalue': gen_info['actual_eigenvalue'],
                'percentage': float(weight / np.sum(np.abs(coefficients)) * 100) if np.sum(np.abs(coefficients)) > 0 else 0.0
            })
    
    return {
        'generation_weights': generation_weights,
        'total_weight': float(np.sum([g['weight'] for g in generation_weights])),
        'dominant_generation': max(generation_weights, key=lambda g: g['weight'])['generation'] if generation_weights else None
    }


def compute_spectral_gap(eigenvalues: np.ndarray) -> Dict:
    """
    Compute spectral gap γ = λ_max - λ₂.
    
    Theory.md Theorem 2.1.2: Convergence rate is e^(-γt)
    
    Args:
        eigenvalues: Sorted eigenvalues (descending)
    
    Returns:
        Dictionary with gap analysis
    """
    if len(eigenvalues) < 2:
        return {
            'spectral_gap': 0.0,
            'convergence_rate': 0.0,
            'timescale': float('inf')
        }
    
    lambda_max = eigenvalues[0]
    lambda_2 = eigenvalues[1]
    
    gap = lambda_max - lambda_2
    
    # Convergence timescale: τ = 1/γ
    timescale = 1.0 / gap if gap > 0 else float('inf')
    
    return {
        'lambda_max': float(lambda_max),
        'lambda_2': float(lambda_2),
        'spectral_gap': float(gap),
        'convergence_rate': float(gap),  # γ
        'timescale': float(timescale),  # τ = 1/γ
        'relative_gap': float(gap / lambda_max) if lambda_max > 0 else 0.0
    }


def verify_phi_cubic(eigenvalue: float, tolerance: float = 0.01) -> bool:
    """
    Verify if eigenvalue satisfies φ³ = 2φ + 1.
    
    Theory.md: Generation eigenvalues satisfy this cubic equation.
    
    Args:
        eigenvalue: Eigenvalue to check
        tolerance: Absolute tolerance
    
    Returns:
        True if eigenvalue satisfies cubic equation
    """
    residual = abs(eigenvalue**3 - 2*eigenvalue - 1)
    return residual < tolerance


def get_generation_summary(diagrams: List[ZXGraph], rho: np.ndarray) -> Dict:
    """
    Complete generation analysis for given state.
    
    Computes eigendecomposition, identifies generations,
    analyzes content, and checks theory compliance.
    
    Args:
        diagrams: List of ZX-diagrams
        rho: Probability distribution
    
    Returns:
        Complete generation analysis dictionary
    """
    # Compute coherence matrix
    from .coherence import compute_coherence_matrix
    C_matrix = compute_coherence_matrix(diagrams)
    
    # Eigendecomposition
    eigendecomp = compute_eigendecomposition(C_matrix)
    
    # Generation analysis
    generation_analysis = analyze_generation_content(diagrams, rho, eigendecomp)
    
    # Spectral gap
    spectral_gap = compute_spectral_gap(eigendecomp['eigenvalues'])
    
    return {
        'eigendecomposition': eigendecomp,
        'generation_analysis': generation_analysis,
        'spectral_gap': spectral_gap,
        'theory_compliant': eigendecomp['generation_structure']['theory_compliant']
    }


if __name__ == "__main__":
    # Demo eigenspace decomposition
    print("=" * 80)
    print("SCCMU Eigenspace Decomposition - Three Generations")
    print("=" * 80)
    
    # Create test coherence matrix
    n = 10
    np.random.seed(42)
    
    # Construct matrix with three dominant eigenvalues near φ, φω, φω²
    omega = np.exp(2j * np.pi / 3)
    target_eigenvalues = [PHI, abs(PHI * omega), abs(PHI * omega**2)]
    
    # Random orthogonal matrix
    Q, _ = np.linalg.qr(np.random.randn(n, n))
    
    # Diagonal with target eigenvalues + noise
    D = np.diag([target_eigenvalues[i % 3] + 0.1 * np.random.randn() for i in range(n)])
    
    # Construct C = Q D Q^T
    C_test = Q @ D @ Q.T
    C_test = (C_test + C_test.T) / 2  # Ensure symmetric
    C_test = np.maximum(C_test, 0)  # Ensure positive
    
    # Analyze
    eigendecomp = compute_eigendecomposition(C_test)
    
    print("\nEigenvalue Spectrum:")
    print("-" * 80)
    for i, lam in enumerate(eigendecomp['eigenvalues'][:5]):
        phi_related = "📐 φ-related" if i in eigendecomp['phi_indices'] else ""
        print(f"  λ_{i+1} = {lam:8.4f}  {phi_related}")
    
    print(f"\nSpectral Gap: γ = {eigendecomp['spectral_gap']:.4f}")
    print(f"Condition Number: κ = {eigendecomp['condition_number']:.2e}")
    
    print("\nThree-Generation Structure:")
    print("-" * 80)
    gen_struct = eigendecomp['generation_structure']
    
    for gen in gen_struct['generations']:
        status = "✅" if gen['relative_error'] < 0.1 else "⚠️"
        print(f"{status} Generation {gen['generation']}:")
        print(f"   Expected: λ = {gen['expected_eigenvalue']:.4f}")
        print(f"   Actual:   λ = {gen['actual_eigenvalue']:.4f}")
        print(f"   Error:    {gen['relative_error']*100:.1f}%")
    
    print(f"\nTheory Compliant: {'✅ YES' if gen_struct['theory_compliant'] else '❌ NO'}")
    print(f"Has Three Generations: {'✅ YES' if gen_struct['has_three_generations'] else '❌ NO'}")
    
    print("\nCubic Equation Check (λ³ = 2λ + 1):")
    print("-" * 80)
    for check in gen_struct['cubic_equation_check'][:3]:
        status = "✅" if check['satisfies_cubic'] else "❌"
        print(f"{status} λ = {check['eigenvalue']:.4f}, residual = {check['cubic_residual']:.4e}")

