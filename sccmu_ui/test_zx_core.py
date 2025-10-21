#!/usr/bin/env python3
"""
Unit tests for ZX-graph core data structures.

Tests Theory.md compliance:
- Axiom 1: Configuration space (ZX-diagrams)
- Valid graph construction
- Phase normalization (Qπ compliance)
"""

import pytest
import numpy as np
from .zx_core import (
    NodeLabel, ZXGraph, create_seed_graph, 
    normalize_phase, add_phases, graphs_equal, PHI
)


class TestNodeLabel:
    """Test NodeLabel dataclass (Theory.md Definition 1.1.1)"""
    
    def test_valid_z_spider(self):
        """Z-spider with Qπ/8 phase"""
        label = NodeLabel('Z', 3, 8, 0)
        assert label.kind == 'Z'
        assert label.phase_radians == 3*np.pi/8
    
    def test_valid_x_spider(self):
        """X-spider with Qπ/4 phase"""
        label = NodeLabel('X', 1, 4, 1)
        assert label.kind == 'X'
        assert label.phase_radians == np.pi/4
    
    def test_invalid_kind(self):
        """Invalid spider type should raise"""
        with pytest.raises(AssertionError):
            NodeLabel('Y', 0, 1, 0)
    
    def test_non_power_of_2_denominator(self):
        """Non-power-of-2 denominator violates Qπ compliance"""
        with pytest.raises(AssertionError):
            NodeLabel('Z', 1, 3, 0)  # 3 is not power of 2
    
    def test_power_of_2_validation(self):
        """Verify power-of-2 check"""
        assert NodeLabel.is_power_of_2(1)
        assert NodeLabel.is_power_of_2(2)
        assert NodeLabel.is_power_of_2(4)
        assert NodeLabel.is_power_of_2(8)
        assert NodeLabel.is_power_of_2(16)
        assert not NodeLabel.is_power_of_2(3)
        assert not NodeLabel.is_power_of_2(6)
        assert not NodeLabel.is_power_of_2(10)


class TestZXGraph:
    """Test ZXGraph structure (Theory.md Definition 1.1.1)"""
    
    def test_seed_graph(self):
        """Seed graph: single Z-spider at phase=0"""
        G = create_seed_graph()
        
        assert len(G.nodes) == 1
        assert len(G.edges) == 0
        assert 0 in G.labels
        assert G.labels[0].kind == 'Z'
        assert G.labels[0].phase_numer == 0
        assert G.labels[0].phase_denom == 1
        
        G.validate()
    
    def test_two_node_graph(self):
        """Two connected Z-spiders"""
        G = ZXGraph(
            nodes=[0, 1],
            edges=[(0, 1)],
            labels={
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 1, 2, 1)
            }
        )
        
        G.validate()
        assert len(G.nodes) == 2
        assert len(G.edges) == 1
    
    def test_self_loop_rejected(self):
        """Self-loops not permitted in ZX-calculus"""
        G = ZXGraph(
            nodes=[0],
            edges=[(0, 0)],  # Self-loop
            labels={0: NodeLabel('Z', 0, 1, 0)}
        )
        
        with pytest.raises(AssertionError, match="Self-loop"):
            G.validate()
    
    def test_missing_label(self):
        """All nodes must have labels"""
        G = ZXGraph(
            nodes=[0, 1],
            edges=[(0, 1)],
            labels={0: NodeLabel('Z', 0, 1, 0)}  # Missing label for node 1
        )
        
        with pytest.raises(AssertionError, match="has no label"):
            G.validate()
    
    def test_invalid_edge(self):
        """Edges must reference valid nodes"""
        G = ZXGraph(
            nodes=[0],
            edges=[(0, 1)],  # Node 1 doesn't exist
            labels={0: NodeLabel('Z', 0, 1, 0)}
        )
        
        with pytest.raises(AssertionError, match="unknown node"):
            G.validate()


class TestPhaseArithmetic:
    """Test phase operations (Theory.md ZX-calculus rules)"""
    
    def test_normalize_phase(self):
        """Phase normalization to [0, 2π)"""
        # 3π/2 normalized
        n, d = normalize_phase(3, 2)
        assert n == 3
        assert d == 2
        
        # 5π/2 = π/2 (mod 2π)
        n, d = normalize_phase(5, 2)
        assert n == 1
        assert d == 2
        
        # Reduce by GCD
        n, d = normalize_phase(2, 4)
        assert n == 1
        assert d == 2
    
    def test_add_phases(self):
        """Spider fusion: Z_α · Z_β = Z_{α+β}"""
        # π/4 + π/4 = π/2
        n, d = add_phases(1, 4, 1, 4)
        assert n == 1
        assert d == 2
        
        # π/8 + 3π/8 = π/2
        n, d = add_phases(1, 8, 3, 8)
        assert n == 1
        assert d == 2
        
        # Result must be power of 2
        n, d = add_phases(1, 2, 1, 4)
        assert NodeLabel.is_power_of_2(d)


class TestGraphEquality:
    """Test graph comparison for diagram space"""
    
    def test_identical_graphs(self):
        """Identical graphs are equal"""
        G1 = create_seed_graph()
        G2 = create_seed_graph()
        assert graphs_equal(G1, G2)
    
    def test_different_node_count(self):
        """Different node counts → not equal"""
        G1 = create_seed_graph()
        G2 = ZXGraph(
            nodes=[0, 1],
            edges=[(0, 1)],
            labels={
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 0, 1, 1)
            }
        )
        assert not graphs_equal(G1, G2)
    
    def test_different_phases(self):
        """Different phases → not equal"""
        G1 = create_seed_graph()  # phase = 0
        G2 = ZXGraph(
            nodes=[0],
            edges=[],
            labels={0: NodeLabel('Z', 1, 4, 0)}  # phase = π/4
        )
        assert not graphs_equal(G1, G2)


class TestTheoryCompliance:
    """Verify compliance with Theory.md axioms"""
    
    def test_axiom_4_phi_value(self):
        """Axiom 4: Λ² = Λ + 1 → Λ = φ"""
        # Verify φ satisfies equation
        assert abs(PHI**2 - PHI - 1) < 1e-10
        
        # Verify φ = (1+√5)/2
        expected = (1 + np.sqrt(5)) / 2
        assert abs(PHI - expected) < 1e-10
    
    def test_configuration_space_axiom_1(self):
        """Axiom 1: Σ = ZX-diagrams"""
        # Create various diagrams
        diagrams = [
            create_seed_graph(),
            ZXGraph([0, 1], [(0, 1)], {
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('X', 1, 2, 1)
            }),
        ]
        
        # All should validate
        for D in diagrams:
            D.validate()
    
    def test_qpi_compliance(self):
        """All phases must have power-of-2 denominators"""
        valid_denoms = [1, 2, 4, 8, 16, 32, 64]
        
        for denom in valid_denoms:
            label = NodeLabel('Z', 0, denom, 0)
            assert label.phase_denom == denom
        
        invalid_denoms = [3, 5, 6, 7, 9, 10]
        
        for denom in invalid_denoms:
            with pytest.raises(AssertionError):
                NodeLabel('Z', 0, denom, 0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

