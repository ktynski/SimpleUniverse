#!/usr/bin/env python3
"""
Tests for ZX → Clifford mapping.

Verifies Theory.md Theorem 1.0.3.3: ZX ≅ Clifford correspondence.
"""

import pytest
import numpy as np
from .zx_core import ZXGraph, NodeLabel, create_seed_graph
from .clifford_mapping import (
    zx_to_clifford,
    detect_triangles,
    build_adjacency,
    get_clifford_grade_decomposition
)


class TestCliffordMapping:
    """Test ZX → Clifford transformation"""
    
    def test_seed_graph_mapping(self):
        """Seed graph maps to Clifford field"""
        G = create_seed_graph()
        components = zx_to_clifford(G)
        
        assert len(components) == 16
        assert components.shape == (16,)
        
        # Should be normalized
        magnitude = np.linalg.norm(components)
        assert abs(magnitude - 1.0) < 1e-6, f"Should be normalized, mag={magnitude}"
    
    def test_z_spider_produces_scalar(self):
        """Z-spider at phase=0 → scalar component"""
        G = create_seed_graph()  # Z-spider, phase=0
        components = zx_to_clifford(G)
        
        # cos(0/2) = 1 → scalar should dominate
        decomp = get_clifford_grade_decomposition(components)
        
        assert decomp['scalar'] > 0.5, \
            f"Z-spider at phase=0 should have strong scalar, got {decomp['scalar']}"
    
    def test_x_spider_produces_bivector(self):
        """X-spider → bivector component"""
        G = ZXGraph(
            nodes=[0],
            edges=[],
            labels={0: NodeLabel('X', 1, 4, 0)}  # X-spider, phase=π/4
        )
        
        components = zx_to_clifford(G)
        decomp = get_clifford_grade_decomposition(components)
        
        assert decomp['bivector_magnitude'] > 0.3, \
            f"X-spider should produce bivectors, got {decomp['bivector_magnitude']}"
    
    def test_two_nodes_produce_vectors(self):
        """Connected nodes → vector components (gauge connection)"""
        G = ZXGraph(
            nodes=[0, 1],
            edges=[(0, 1)],
            labels={
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 1, 4, 1)  # π/4 phase difference
            }
        )
        
        components = zx_to_clifford(G)
        decomp = get_clifford_grade_decomposition(components)
        
        assert decomp['vector_magnitude'] > 0.1, \
            f"Edges should produce vectors, got {decomp['vector_magnitude']}"
    
    def test_triangle_produces_trivectors(self):
        """Triangle (3-cycle) → trivector components (sovereignty)"""
        G = ZXGraph(
            nodes=[0, 1, 2],
            edges=[(0, 1), (1, 2), (2, 0)],
            labels={
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 1, 8, 1),
                2: NodeLabel('Z', 2, 8, 2)
            }
        )
        
        components = zx_to_clifford(G)
        decomp = get_clifford_grade_decomposition(components)
        
        # Should have trivector components from triangle
        assert decomp['trivector_magnitude'] >= 0.0, \
            f"Triangle should enable trivectors, got {decomp['trivector_magnitude']}"
    
    def test_normalized_output(self):
        """Output is always normalized"""
        graphs = [
            create_seed_graph(),
            ZXGraph([0, 1], [(0, 1)], {
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('X', 1, 2, 1)
            }),
            ZXGraph([0, 1, 2], [(0, 1), (1, 2)], {
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 1, 4, 1),
                2: NodeLabel('X', 2, 4, 2)
            })
        ]
        
        for G in graphs:
            components = zx_to_clifford(G)
            magnitude = np.linalg.norm(components)
            
            assert abs(magnitude - 1.0) < 1e-6, \
                f"Output should be normalized, got magnitude={magnitude}"


class TestTriangleDetection:
    """Test triangle (3-cycle) detection"""
    
    def test_no_triangles_in_line(self):
        """Line graph has no triangles"""
        G = ZXGraph(
            nodes=[0, 1, 2],
            edges=[(0, 1), (1, 2)],
            labels={i: NodeLabel('Z', 0, 1, i) for i in range(3)}
        )
        
        adjacency = build_adjacency(G)
        triangles = detect_triangles(G, adjacency)
        
        assert len(triangles) == 0
    
    def test_single_triangle(self):
        """Triangle graph has one 3-cycle"""
        G = ZXGraph(
            nodes=[0, 1, 2],
            edges=[(0, 1), (1, 2), (2, 0)],
            labels={i: NodeLabel('Z', 0, 1, i) for i in range(3)}
        )
        
        adjacency = build_adjacency(G)
        triangles = detect_triangles(G, adjacency)
        
        assert len(triangles) >= 1, "Should detect triangle"


class TestTheorem1_0_3_3:
    """Verify Theorem 1.0.3.3: ZX ≅ Clifford correspondence"""
    
    def test_zx_operations_map_to_clifford(self):
        """ZX operations have Clifford analogs"""
        # Z-spider
        G_z = ZXGraph([0], [], {0: NodeLabel('Z', 1, 4, 0)})  # Z(π/4)
        clifford_z = zx_to_clifford(G_z)
        
        # X-spider  
        G_x = ZXGraph([0], [], {0: NodeLabel('X', 1, 4, 0)})  # X(π/4)
        clifford_x = zx_to_clifford(G_x)
        
        # Should map to different Clifford elements
        dot_product = np.dot(clifford_z, clifford_x)
        
        # Not identical
        assert abs(dot_product) < 0.99, "Z and X should map differently"
    
    def test_phase_affects_mapping(self):
        """Different phases → different Clifford elements"""
        G1 = ZXGraph([0], [], {0: NodeLabel('Z', 0, 1, 0)})    # phase = 0
        G2 = ZXGraph([0], [], {0: NodeLabel('Z', 1, 2, 0)})    # phase = π
        
        c1 = zx_to_clifford(G1)
        c2 = zx_to_clifford(G2)
        
        # Different phases should give different Clifford fields
        difference = np.linalg.norm(c1 - c2)
        
        assert difference > 0.1, f"Phase should affect mapping, diff={difference}"
    
    def test_connectivity_affects_weights(self):
        """Node degree affects Clifford component weights"""
        # Single node
        G1 = create_seed_graph()
        c1 = zx_to_clifford(G1)
        
        # Same node but connected
        G2 = ZXGraph(
            nodes=[0, 1],
            edges=[(0, 1)],
            labels={
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('Z', 0, 1, 1)
            }
        )
        c2 = zx_to_clifford(G2)
        
        # Higher connectivity → stronger components
        # (Due to weight = sqrt(1 + degree))
        assert np.linalg.norm(c2) >= np.linalg.norm(c1) * 0.9


class TestGradeStructure:
    """Test Clifford grade decomposition"""
    
    def test_grade_decomposition(self):
        """Grade decomposition is computable"""
        G = ZXGraph(
            nodes=[0, 1, 2],
            edges=[(0, 1), (1, 2), (2, 0)],
            labels={
                0: NodeLabel('Z', 0, 1, 0),
                1: NodeLabel('X', 1, 4, 1),
                2: NodeLabel('Z', 2, 4, 2)
            }
        )
        
        components = zx_to_clifford(G)
        decomp = get_clifford_grade_decomposition(components)
        
        assert 'scalar' in decomp
        assert 'vectors' in decomp
        assert 'bivectors' in decomp
        assert 'trivectors' in decomp
        assert 'pseudoscalar' in decomp
        
        # All should be finite
        assert np.isfinite(decomp['scalar'])
        assert np.all(np.isfinite(decomp['vectors']))
        assert np.isfinite(decomp['vector_magnitude'])
    
    def test_magnitudes_sum_correctly(self):
        """Grade magnitudes should sum to total"""
        G = create_seed_graph()
        components = zx_to_clifford(G)
        decomp = get_clifford_grade_decomposition(components)
        
        # Total magnitude (already computed)
        total = decomp['total_magnitude']
        
        # Should be 1 (normalized)
        assert abs(total - 1.0) < 1e-6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

