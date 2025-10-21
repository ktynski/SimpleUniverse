#!/usr/bin/env python3
"""
Master Equation Evolution Engine

Implements Theory.md Definition 2.1.3 (line 883-897):
    ∂ρ/∂t = -grad_g ℱ[ρ]

Hybrid approach for computational tractability:
- Evolve ρ over small ensemble of diagrams near mode
- Track mode diagram for visualization
- Verify mode maximizes ℱ

Test with: python3 -m pytest sccmu_ui/test_evolution.py
"""

import numpy as np
from typing import List, Tuple
import copy
from .zx_core import ZXGraph, NodeLabel, create_seed_graph, PHI, add_phases
from .coherence import compute_coherence_matrix, coherence_between_diagrams
from .free_energy import (
    compute_free_energy, compute_functional_derivative,
    verify_fixed_point, BETA
)


class ZXEvolutionEngine:
    """
    Evolve probability distribution over ZX-diagram space.
    
    Theory.md master equation (Definition 2.1.3):
    ∂ρ/∂t = ∇·(ρ∇δℱ/δρ) + ν∆ρ
    
    where δℱ/δρ = -2(𝒞ρ) + (1/β)(log ρ + 1)
    
    Hybrid implementation:
    - Full statistical mechanics on small ensemble
    - Mode diagram for visualization
    - Verify equilibrium conditions
    """
    
    def __init__(self, ensemble_size=20):
        # Start with seed diagram
        self.mode_graph = create_seed_graph()
        
        # Small ensemble around mode
        self.ensemble = [self.mode_graph.copy()]
        self.ensemble_rho = np.array([1.0])
        
        # Precomputed coherence matrix
        self.C_matrix = None
        
        # Evolution tracking
        self.time = 0.0
        self.free_energy_history = []
        self.coherence_history = []
        self.mode_probability_history = []
        
        # Parameters
        self.nu = 1.0 / (2*np.pi*PHI)  # Diffusion coefficient
        self.ensemble_size = ensemble_size
    
    def generate_variations(self, graph: ZXGraph, max_variations: int = 20) -> List[ZXGraph]:
        """
        Generate nearby diagrams via single local operations.
        
        Operations:
        1. Add node (bootstrap/grace)
        2. Add edge
        3. Change spider type (Z ↔ X)
        4. Change phase
        """
        variations = [graph.copy()]
        
        # 1. Add node variations (if not too large)
        if len(graph.nodes) < 15 and len(variations) < max_variations:
            for source in graph.nodes[:min(3, len(graph.nodes))]:
                var = graph.copy()
                new_id = max(var.nodes) + 1 if var.nodes else 0
                var.nodes.append(new_id)
                var.edges.append((source, new_id))
                
                # Add random label
                kind = np.random.choice(['Z', 'X'])
                phase_n = np.random.randint(0, 8)
                var.labels[new_id] = NodeLabel(kind, phase_n, 8, new_id)
                
                variations.append(var)
        
        # 2. Spider type flip (Z ↔ X)
        for node in graph.nodes[:min(3, len(graph.nodes))]:
            if len(variations) >= max_variations:
                break
            
            var = graph.copy()
            old_label = var.labels[node]
            new_kind = 'X' if old_label.kind == 'Z' else 'Z'
            var.labels[node] = NodeLabel(
                new_kind, 
                old_label.phase_numer,
                old_label.phase_denom,
                old_label.node_id
            )
            variations.append(var)
        
        # 3. Phase variations
        for node in graph.nodes[:min(2, len(graph.nodes))]:
            if len(variations) >= max_variations:
                break
            
            var = graph.copy()
            old_label = var.labels[node]
            
            # Increment phase by π/8
            new_n, new_d = add_phases(old_label.phase_numer, old_label.phase_denom, 1, 8)
            var.labels[node] = NodeLabel(
                old_label.kind,
                new_n, new_d,
                old_label.node_id
            )
            variations.append(var)
        
        return variations[:max_variations]
    
    def evolve_step(self, dt: float) -> dict:
        """
        Single master equation evolution step.
        
        Theory.md Definition 2.1.3:
        ∂ρ/∂t = ∇·(ρ∇δℱ/δρ) + ν∆ρ
        
        Returns:
            State dictionary with mode, F, convergence info
        """
        # 1. Generate ensemble around current mode
        self.ensemble = self.generate_variations(self.mode_graph, self.ensemble_size)
        n = len(self.ensemble)
        
        # 2. Initialize/update ρ distribution
        if len(self.ensemble_rho) != n:
            # Uniform initialization over new ensemble
            self.ensemble_rho = np.ones(n) / n
        
        # 3. Compute coherence matrix
        self.C_matrix = compute_coherence_matrix(self.ensemble)
        
        # 4. Compute functional derivative
        delta_F = compute_functional_derivative(self.ensemble, self.ensemble_rho, self.C_matrix)
        
        # 5. Master equation evolution (simplified gradient descent)
        # ∂ρ/∂t ∝ -δℱ/δρ (gradient ascent on ℱ)
        # Keep probability normalized
        drho_dt = -delta_F + np.mean(delta_F)  # Subtract mean to preserve normalization
        
        # Update with timestep
        self.ensemble_rho += drho_dt * dt
        
        # Project to probability simplex
        self.ensemble_rho = np.maximum(self.ensemble_rho, 0)
        self.ensemble_rho /= np.sum(self.ensemble_rho)
        
        # 6. Find mode (most probable diagram)
        mode_idx = np.argmax(self.ensemble_rho)
        self.mode_graph = self.ensemble[mode_idx].copy()
        mode_prob = self.ensemble_rho[mode_idx]
        
        # 7. Compute observables
        F = compute_free_energy(self.ensemble, self.ensemble_rho)
        
        # Mode coherence (for visualization)
        mode_coherence = coherence_between_diagrams(self.mode_graph, self.mode_graph)
        
        # 8. Track history
        self.free_energy_history.append(F)
        self.coherence_history.append(mode_coherence)
        self.mode_probability_history.append(mode_prob)
        self.time += dt
        
        # 9. Check convergence
        convergence = self.check_convergence()
        
        return {
            'mode_graph': self.mode_graph,
            'mode_probability': mode_prob,
            'free_energy': F,
            'mode_coherence': mode_coherence,
            'num_diagrams': n,
            'time': self.time,
            'convergence': convergence
        }
    
    def check_convergence(self) -> dict:
        """
        Check if system has reached equilibrium.
        
        Theory.md Theorem 2.1.2:
        1. δℱ/δρ = constant (equilibrium condition)
        2. 𝒞ρ_∞ = λ_max ρ_∞ (fixed point condition)
        """
        if len(self.ensemble_rho) == 0:
            return {'converged': False}
        
        # Check free energy convergence (ℱ no longer increasing)
        if len(self.free_energy_history) > 10:
            recent_F = self.free_energy_history[-10:]
            F_change = max(recent_F) - min(recent_F)
            F_converged = F_change < 1e-4
        else:
            F_converged = False
        
        # Check fixed point condition
        fixed_point = verify_fixed_point(self.ensemble, self.ensemble_rho, self.C_matrix)
        
        # Overall convergence
        converged = F_converged and fixed_point['is_fixed_point']
        
        return {
            'converged': converged,
            'free_energy_stable': F_converged,
            'is_fixed_point': fixed_point['is_fixed_point'],
            'lambda_max': fixed_point['lambda_max'],
            'residual': fixed_point['normalized_residual'],
            'is_phi_eigenvalue': fixed_point['is_phi_eigenvalue']
        }
    
    def get_state(self) -> dict:
        """
        Get current state for visualization.
        
        Returns mode diagram and statistics.
        """
        return {
            'mode_graph': self.mode_graph,
            'num_nodes': len(self.mode_graph.nodes),
            'num_edges': len(self.mode_graph.edges),
            'mode_probability': float(np.max(self.ensemble_rho)) if len(self.ensemble_rho) > 0 else 0.0,
            'free_energy': float(self.free_energy_history[-1]) if self.free_energy_history else 0.0,
            'time': float(self.time),
            'convergence': self.check_convergence()
        }

