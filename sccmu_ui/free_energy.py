#!/usr/bin/env python3
"""
Free Energy Functional for ZX-Diagrams

Implements Theory.md Axiom 3 (line 380-393):
    ℱ[ρ] = ℒ[ρ] - (1/β)S[ρ]

where:
    ℒ[ρ] = ∫∫ C(x,y)ρ(x)ρ(y)dλ(x)dλ(y)  (coherence functional)
    S[ρ] = -∫ ρ log ρ dλ                  (entropy)
    β = 2πφ                                (inverse temperature)

Test with: python3 -m pytest sccmu_ui/test_free_energy.py
"""

import numpy as np
from typing import List
from .zx_core import ZXGraph, PHI
from .coherence import coherence_between_diagrams


BETA = 2 * np.pi * PHI  # Inverse temperature from theory


def compute_coherence_functional(diagrams: List[ZXGraph], rho: np.ndarray) -> float:
    """
    Compute coherence functional ℒ[ρ].
    
    Theory.md Axiom 3 (line 386):
    ℒ[ρ] = ∫∫ C(x,y)ρ(x)ρ(y)dλ(x)dλ(y)
    
    Discrete form:
    ℒ = Σᵢⱼ C([Dᵢ], [Dⱼ]) ρ([Dᵢ]) ρ([Dⱼ])
    
    Args:
        diagrams: List of ZX-diagrams
        rho: Probability distribution over diagrams (sums to 1)
    
    Returns:
        Coherence functional value ℒ[ρ] ∈ [0, 1]
    """
    assert len(diagrams) == len(rho), "Diagrams and rho must have same length"
    assert abs(np.sum(rho) - 1.0) < 1e-6, f"ρ must sum to 1, got {np.sum(rho)}"
    
    n = len(diagrams)
    L = 0.0
    
    for i in range(n):
        for j in range(n):
            # C([Dᵢ], [Dⱼ])
            C_ij = coherence_between_diagrams(diagrams[i], diagrams[j])
            
            # ρ([Dᵢ]) ρ([Dⱼ])
            rho_i = rho[i]
            rho_j = rho[j]
            
            # Accumulate
            L += C_ij * rho_i * rho_j
    
    return float(L)


def compute_entropy(rho: np.ndarray) -> float:
    """
    Compute Shannon entropy S[ρ].
    
    Theory.md Axiom 3 (line 387):
    S[ρ] = -∫ ρ log ρ dλ
    
    Discrete form:
    S = -Σᵢ ρ([Dᵢ]) log ρ([Dᵢ])
    
    Args:
        rho: Probability distribution (sums to 1)
    
    Returns:
        Entropy S[ρ] ≥ 0
    """
    assert abs(np.sum(rho) - 1.0) < 1e-6, f"ρ must sum to 1, got {np.sum(rho)}"
    
    # Avoid log(0) by adding small epsilon
    rho_safe = np.maximum(rho, 1e-10)
    
    entropy = -np.sum(rho * np.log(rho_safe))
    
    return float(entropy)


def compute_free_energy(diagrams: List[ZXGraph], rho: np.ndarray, beta: float = None) -> float:
    """
    Compute free energy functional ℱ[ρ].
    
    Theory.md Axiom 3 (line 381-388):
    ℱ[ρ] = ℒ[ρ] - (1/β)S[ρ]
    
    where β = 2πφ (inverse temperature)
    
    Args:
        diagrams: List of ZX-diagrams
        rho: Probability distribution over diagrams
        beta: Inverse temperature (defaults to 2πφ from theory)
    
    Returns:
        Free energy ℱ[ρ]
        
    At equilibrium: ρ_∞ = argmax{ℱ[ρ]}
    """
    if beta is None:
        beta = BETA
    
    # Coherence term (attractive)
    L = compute_coherence_functional(diagrams, rho)
    
    # Entropy term (spreading)
    S = compute_entropy(rho)
    
    # Free energy
    F = L - S / beta
    
    return float(F)


def compute_functional_derivative(diagrams: List[ZXGraph], 
                                 rho: np.ndarray,
                                 C_matrix: np.ndarray = None,
                                 beta: float = None) -> np.ndarray:
    """
    Compute functional derivative δℱ/δρ.
    
    Theory.md Definition 2.1.3 (line 895):
    δℱ/δρ = -2(𝒞ρ) + (1/β)(log ρ + 1)
    
    Args:
        diagrams: List of ZX-diagrams
        rho: Probability distribution
        C_matrix: Precomputed coherence matrix (optional, for efficiency)
        beta: Inverse temperature (defaults to 2πφ from theory)
    
    Returns:
        Functional derivative δℱ/δρ[i] for each diagram i
    """
    if beta is None:
        beta = BETA
    
    n = len(diagrams)
    
    # Apply coherence operator: (𝒞ρ)[i] = Σⱼ C([Dᵢ], [Dⱼ]) ρ([Dⱼ])
    if C_matrix is None:
        C_rho = np.zeros(n)
        for i in range(n):
            for j in range(n):
                C_ij = coherence_between_diagrams(diagrams[i], diagrams[j])
                C_rho[i] += C_ij * rho[j]
    else:
        C_rho = C_matrix @ rho
    
    # Functional derivative
    rho_safe = np.maximum(rho, 1e-10)
    delta_F = -2 * C_rho + (1/beta) * (np.log(rho_safe) + 1)
    
    return delta_F


def verify_equilibrium(diagrams: List[ZXGraph], 
                      rho: np.ndarray,
                      C_matrix: np.ndarray = None) -> dict:
    """
    Verify equilibrium condition: δℱ/δρ = constant.
    
    Theory.md Theorem 2.1.2 (line 903-907):
    At equilibrium: δℱ/δρ|_{ρ=ρ_∞} = const
    
    Equivalently: 𝒞ρ_∞ = λ_max ρ_∞
    
    Returns:
        Dictionary with verification results
    """
    delta_F = compute_functional_derivative(diagrams, rho, C_matrix)
    
    # At equilibrium, δℱ/δρ should be constant (Lagrange multiplier)
    mean = np.mean(delta_F)
    std = np.std(delta_F)
    
    # Normalized standard deviation
    relative_std = std / (abs(mean) + 1e-10)
    
    is_equilibrium = relative_std < 0.01
    
    return {
        'is_equilibrium': is_equilibrium,
        'delta_F_mean': float(mean),
        'delta_F_std': float(std),
        'relative_std': float(relative_std),
        'max_deviation': float(np.max(np.abs(delta_F - mean)))
    }


def verify_fixed_point(diagrams: List[ZXGraph],
                      rho: np.ndarray,
                      C_matrix: np.ndarray = None) -> dict:
    """
    Verify fixed point condition: 𝒞ρ_∞ = λ_max ρ_∞.
    
    Theory.md Theorem 2.1.2 (line 907):
    𝒞ρ_∞ = λ_max ρ_∞
    
    Returns:
        Dictionary with eigenvalue verification
    """
    n = len(diagrams)
    
    # Apply coherence operator
    if C_matrix is None:
        C_rho = np.zeros(n)
        for i in range(n):
            for j in range(n):
                C_ij = coherence_between_diagrams(diagrams[i], diagrams[j])
                C_rho[i] += C_ij * rho[j]
    else:
        C_rho = C_matrix @ rho
    
    # At fixed point: 𝒞ρ = λ ρ for some λ
    # So λ[i] = (𝒞ρ)[i] / ρ[i] should be constant
    
    rho_safe = np.maximum(rho, 1e-10)
    lambda_ratios = C_rho / rho_safe
    
    lambda_max = np.mean(lambda_ratios)
    lambda_std = np.std(lambda_ratios)
    
    # Residual: ||𝒞ρ - λ_max ρ||
    residual = np.linalg.norm(C_rho - lambda_max * rho)
    normalized_residual = residual / (np.linalg.norm(C_rho) + 1e-10)
    
    is_fixed_point = (lambda_std < 0.01 and normalized_residual < 1e-4)
    
    # Check if λ_max is φ-related
    phi_powers = [PHI**k for k in range(-5, 6)]
    closest_phi_power = min(phi_powers, key=lambda p: abs(p - lambda_max))
    phi_power_error = abs(lambda_max - closest_phi_power) / (closest_phi_power + 1e-10)
    
    return {
        'is_fixed_point': is_fixed_point,
        'lambda_max': float(lambda_max),
        'lambda_std': float(lambda_std),
        'residual': float(residual),
        'normalized_residual': float(normalized_residual),
        'closest_phi_power': float(closest_phi_power),
        'phi_power_error': float(phi_power_error),
        'is_phi_eigenvalue': phi_power_error < 0.05
    }

