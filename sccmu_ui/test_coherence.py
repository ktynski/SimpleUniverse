#!/usr/bin/env python3
"""
Tests for coherence between ZX-diagrams.

Verifies Theory.md Axiom 2 compliance.
"""

import pytest
import numpy as np
from .zx_core import ZXGraph, NodeLabel, create_seed_graph, PHI
from .coherence import (
    coherence_between_diagrams,
    compute_structural_overlap,
    compute_edit_distance,
    compute_coherence_matrix,
    verify_coherence_properties
)


class TestCoherenceBetweenDiagrams:
    """Test C([D₁], [D₂]) function"""
    
    def test_self_coherence(self):
        """Axiom 2: C([D], [D]) = 1"""
        G = create_seed_graph()
        C = coherence_between_diagrams(G, G)
        
        assert abs(C - 1.0) < 1e-6, f"Self-coherence should be 1.0, got {C}"
    
    def test_symmetry(self):
        """Axiom 2: C([D₁], [D₂]) = C([D₂], [D₁])"""
        G1 = create_seed_graph()
        G2 = ZXGraph(
            nodes=[0, 1],
            edges=[(0, 1)],
            labels={
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 1, 2, 1)
            }
        )
        
        C_12 = coherence_between_diagrams(G1, G2)
        C_21 = coherence_between_diagrams(G2, G1)
        
        assert abs(C_12 - C_21) < 1e-6, f"Coherence not symmetric: {C_12} vs {C_21}"
    
    def test_bounded(self):
        """Axiom 2: C ∈ [0, 1]"""
        G1 = create_seed_graph()
        G2 = ZXGraph(
            nodes=[0, 1, 2],
            edges=[(0, 1), (1, 2)],
            labels={
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('X', 1, 4, 1),
                2: NodeLabel('Z', 3, 4, 2)
            }
        )
        
        C = coherence_between_diagrams(G1, G2)
        
        assert 0 <= C <= 1, f"Coherence out of bounds: {C}"
    
    def test_similar_graphs_high_coherence(self):
        """Similar graphs should have high coherence"""
        G1 = ZXGraph(
            nodes=[0, 1],
            edges=[(0, 1)],
            labels={
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 1, 8, 1)
            }
        )
        
        G2 = ZXGraph(
            nodes=[0, 1],
            edges=[(0, 1)],
            labels={
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 2, 8, 1)  # Slightly different phase
            }
        )
        
        C = coherence_between_diagrams(G1, G2)
        
        assert C > 0.5, f"Similar graphs should have high coherence, got {C}"
    
    def test_dissimilar_graphs_low_coherence(self):
        """Very different graphs should have low coherence"""
        G1 = create_seed_graph()  # 1 node
        
        G2 = ZXGraph(
            nodes=list(range(10)),
            edges=[(i, i+1) for i in range(9)],
            labels={i: NodeLabel('Z', i % 8, 8, i) for i in range(10)}
        )  # 10 nodes
        
        C = coherence_between_diagrams(G1, G2)
        
        assert C < 0.3, f"Dissimilar graphs should have low coherence, got {C}"


class TestEditDistance:
    """Test edit distance metric"""
    
    def test_same_graph_zero_distance(self):
        """Distance to self = 0"""
        G = create_seed_graph()
        d = compute_edit_distance(G, G)
        
        assert d == 0.0
    
    def test_one_node_difference(self):
        """Adding one node increases distance"""
        G1 = create_seed_graph()
        G2 = ZXGraph(
            nodes=[0, 1],
            edges=[(0, 1)],
            labels={
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 0, 1, 1)
            }
        )
        
        d = compute_edit_distance(G1, G2)
        
        assert d >= 1.0, f"One node addition should increase distance, got {d}"


class TestCoherenceMatrix:
    """Test coherence matrix computation"""
    
    def test_small_diagram_set(self):
        """Coherence matrix for small set of diagrams"""
        diagrams = [
            create_seed_graph(),
            ZXGraph([0, 1], [(0, 1)], {
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 0, 1, 1)
            }),
            ZXGraph([0], [], {0: NodeLabel('X', 1, 4, 0)})
        ]
        
        C_matrix = compute_coherence_matrix(diagrams)
        
        assert C_matrix.shape == (3, 3)
        
        # Verify properties
        props = verify_coherence_properties(C_matrix)
        
        assert props['symmetric'], f"Matrix not symmetric: error = {props['symmetry_error']}"
        assert props['self_coherent'], f"Diagonal not 1: error = {props['self_coherence_error']}"
        assert props['bounded'], f"Values out of bounds: [{props['min_value']}, {props['max_value']}]"
        assert props['all_valid'], "Coherence matrix violates Axiom 2"
    
    def test_diagonal_is_one(self):
        """Self-coherence = 1 (Axiom 2)"""
        diagrams = [
            create_seed_graph(),
            ZXGraph([0, 1], [(0, 1)], {
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('X', 1, 2, 1)
            })
        ]
        
        C_matrix = compute_coherence_matrix(diagrams)
        diagonal = np.diag(C_matrix)
        
        for i, d in enumerate(diagonal):
            assert abs(d - 1.0) < 1e-6, f"C[{i},{i}] = {d}, should be 1.0"


class TestTheoryAxiom2:
    """Verify Axiom 2 properties"""
    
    def test_axiom_2_symmetry(self):
        """C(x,y) = C(y,x) for all x,y ∈ Σ"""
        G1 = create_seed_graph()
        G2 = ZXGraph([0, 1], [(0, 1)], {
            0: NodeLabel('Z', 0, 1, 0),
            1: NodeLabel('Z', 1, 4, 1)
        })
        G3 = ZXGraph([0], [], {0: NodeLabel('X', 0, 1, 0)})
        
        diagrams = [G1, G2, G3]
        
        for i, Di in enumerate(diagrams):
            for j, Dj in enumerate(diagrams):
                C_ij = coherence_between_diagrams(Di, Dj)
                C_ji = coherence_between_diagrams(Dj, Di)
                
                assert abs(C_ij - C_ji) < 1e-6, \
                    f"Symmetry violated: C[{i},{j}]={C_ij} != C[{j},{i}]={C_ji}"
    
    def test_axiom_2_self_coherence(self):
        """C(x,x) = 1 for all x ∈ Σ"""
        diagrams = [
            create_seed_graph(),
            ZXGraph([0, 1], [(0, 1)], {
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('X', 1, 2, 1)
            }),
            ZXGraph([0, 1, 2], [(0, 1), (1, 2), (2, 0)], {
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 1, 4, 1),
                2: NodeLabel('Z', 2, 4, 2)
            })
        ]
        
        for D in diagrams:
            C = coherence_between_diagrams(D, D)
            assert abs(C - 1.0) < 1e-6, f"Self-coherence = {C}, should be 1.0"
    
    def test_axiom_2_bounded(self):
        """C: Σ × Σ → [0, 1]"""
        # Generate random diagrams
        np.random.seed(42)
        
        diagrams = []
        for _ in range(5):
            n_nodes = np.random.randint(1, 5)
            nodes = list(range(n_nodes))
            
            # Random edges
            edges = []
            for i in range(n_nodes):
                for j in range(i+1, n_nodes):
                    if np.random.random() < 0.3:
                        edges.append((i, j))
            
            # Random labels
            labels = {}
            for i in nodes:
                kind = np.random.choice(['Z', 'X'])
                phase_n = np.random.randint(0, 8)
                labels[i] = NodeLabel(kind, phase_n, 8, i)
            
            diagrams.append(ZXGraph(nodes, edges, labels))
        
        # Check all pairs
        for Di in diagrams:
            for Dj in diagrams:
                C = coherence_between_diagrams(Di, Dj)
                assert 0 <= C <= 1, f"Coherence out of bounds: {C}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

