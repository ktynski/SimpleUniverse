#!/usr/bin/env python3
"""
ZX-Graph Core Data Structures

Implements Theory.md Definition 1.1.1-1.1.3:
- ZX-diagrams with nodes, edges, labels
- Validation ensuring theory compliance
- No free parameters, all from φ

Test with: python3 -m pytest sccmu_ui/test_zx_core.py
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Set
import numpy as np

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio from Λ² = Λ + 1


@dataclass(frozen=True)
class NodeLabel:
    """
    ZX spider label (Theory.md Definition 1.1.1).
    
    kind: 'Z' or 'X' spider type
    phase_numer: Numerator of phase (in units of π)
    phase_denom: Denominator (must be power of 2 for Qπ compliance)
    node_id: Unique identifier
    """
    kind: str  # 'Z' or 'X'
    phase_numer: int
    phase_denom: int
    node_id: int
    
    def __post_init__(self):
        """Validate on construction"""
        assert self.kind in ['Z', 'X'], f"kind must be 'Z' or 'X', got {self.kind}"
        assert self.phase_denom > 0, "phase_denom must be positive"
        assert self.is_power_of_2(self.phase_denom), f"phase_denom must be power of 2, got {self.phase_denom}"
    
    @staticmethod
    def is_power_of_2(n):
        """Check if n is power of 2"""
        return n > 0 and (n & (n - 1)) == 0
    
    @property
    def phase_radians(self):
        """Phase in radians"""
        return np.pi * self.phase_numer / self.phase_denom


@dataclass
class ZXGraph:
    """
    ZX-diagram (Theory.md Definition 1.1.1).
    
    nodes: List of node IDs
    edges: List of (source, target) pairs
    labels: Dict mapping node_id → NodeLabel
    """
    nodes: List[int]
    edges: List[Tuple[int, int]]
    labels: Dict[int, NodeLabel]
    
    def validate(self):
        """
        Validate ZX-diagram is well-formed.
        
        Theory requirements:
        - No self-loops
        - All edges reference valid nodes
        - All nodes have labels
        - All phase denominators are powers of 2 (Qπ compliance)
        """
        node_set = set(self.nodes)
        
        # Check edges
        for u, v in self.edges:
            assert u != v, f"Self-loop not permitted: {u} -> {u}"
            assert u in node_set, f"Edge references unknown node: {u}"
            assert v in node_set, f"Edge references unknown node: {v}"
        
        # Check labels
        for node_id in self.nodes:
            assert node_id in self.labels, f"Node {node_id} has no label"
        
        # NodeLabel validates itself in __post_init__
        
        return True
    
    def copy(self):
        """Deep copy of graph"""
        import copy
        return ZXGraph(
            nodes=copy.copy(self.nodes),
            edges=copy.copy(self.edges),
            labels=copy.deepcopy(self.labels)
        )


def create_seed_graph() -> ZXGraph:
    """
    Create seed graph for ex nihilo bootstrap.
    
    Theory.md: Ex nihilo emergence from apparent void.
    Start with single Z-spider at phase = 0.
    
    Returns:
        Seed graph with 1 node, 0 edges
    """
    return ZXGraph(
        nodes=[0],
        edges=[],
        labels={0: NodeLabel('Z', 0, 1, 0)}
    )


def normalize_phase(phase_numer: int, phase_denom: int) -> Tuple[int, int]:
    """
    Normalize phase to reduced form.
    
    Phase = (phase_numer / phase_denom) * π
    Normalize to [0, 2π) range with gcd reduction.
    """
    from math import gcd
    
    # Reduce to [0, 2*denom) range
    mod = 2 * phase_denom
    numer_mod = phase_numer % mod
    
    # Reduce by GCD
    g = gcd(abs(numer_mod), phase_denom)
    if g > 0:
        numer_reduced = numer_mod // g
        denom_reduced = phase_denom // g
    else:
        numer_reduced = numer_mod
        denom_reduced = phase_denom
    
    return numer_reduced, denom_reduced


def add_phases(phase1_n: int, phase1_d: int, 
               phase2_n: int, phase2_d: int) -> Tuple[int, int]:
    """
    Add two Qπ phases.
    
    Theory requirement: Result must have power-of-2 denominator.
    """
    # Find common denominator (LCM for powers of 2 is max)
    common_denom = max(phase1_d, phase2_d)
    
    # Convert to common denominator
    numer1 = phase1_n * (common_denom // phase1_d)
    numer2 = phase2_n * (common_denom // phase2_d)
    
    # Add
    result_numer = numer1 + numer2
    result_denom = common_denom
    
    # Normalize
    return normalize_phase(result_numer, result_denom)


# Graph equality and hashing for diagram space
def graphs_equal(G1: ZXGraph, G2: ZXGraph) -> bool:
    """
    Check if two graphs are equal (not just isomorphic).
    
    For diagram space enumeration.
    """
    if len(G1.nodes) != len(G2.nodes):
        return False
    if len(G1.edges) != len(G2.edges):
        return False
    
    # Check node labels
    for node in G1.nodes:
        if node not in G2.nodes:
            return False
        label1 = G1.labels.get(node)
        label2 = G2.labels.get(node)
        if label1 != label2:
            return False
    
    # Check edges (order independent)
    edges1 = set(G1.edges)
    edges2 = set(G2.edges)
    return edges1 == edges2

