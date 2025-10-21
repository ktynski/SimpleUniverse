#!/usr/bin/env python3
"""
Coherence Between ZX-Diagrams

Implements Theory.md Axiom 2 and Definition 1.1.4:
- C: Σ × Σ → [0,1] (coherence function)
- C([D₁], [D₂]) = structural overlap × exp(-distance/φ)

Test with: python3 -m pytest sccmu_ui/test_coherence.py
"""

import numpy as np
from typing import Dict
from .zx_core import ZXGraph, PHI


def coherence_between_diagrams(D1: ZXGraph, D2: ZXGraph) -> float:
    """
    Coherence between two ZX-diagrams.
    
    Theory.md Definition 1.1.4 (line 742-746):
    C([D₁], [D₂]) = |⟨D₁|D₂⟩_ZX|²/n · exp(-d([D₁],[D₂])/φ)
    
    Simplified implementation:
    C([D₁], [D₂]) = structural_overlap([D₁], [D₂]) × exp(-edit_distance/φ)
    
    Properties (Theory.md Axiom 2, line 373-378):
    - Symmetry: C([D₁], [D₂]) = C([D₂], [D₁])
    - Self-coherence: C([D], [D]) = 1
    - Bounded: C ∈ [0, 1]
    """
    # Validate inputs
    D1.validate()
    D2.validate()
    
    # 1. Structural overlap
    overlap = compute_structural_overlap(D1, D2)
    
    # 2. Edit distance
    dist = compute_edit_distance(D1, D2)
    
    # 3. φ-decay factor
    decay = np.exp(-dist / PHI)
    
    # 4. Combined coherence
    coherence = overlap * decay
    
    # Ensure bounds [0, 1]
    return float(np.clip(coherence, 0.0, 1.0))


def compute_structural_overlap(D1: ZXGraph, D2: ZXGraph) -> float:
    """
    Structural similarity between diagrams.
    
    Components:
    1. Node count similarity
    2. Edge structure similarity  
    3. Spider type distribution
    4. Phase distribution overlap
    
    Returns value in [0, 1] where 1 = identical structure.
    """
    # Node count similarity
    n1, n2 = len(D1.nodes), len(D2.nodes)
    if n1 == 0 and n2 == 0:
        node_sim = 1.0
    elif n1 == 0 or n2 == 0:
        node_sim = 0.0
    else:
        node_sim = min(n1, n2) / max(n1, n2)
    
    # Edge density similarity
    e1, e2 = len(D1.edges), len(D2.edges)
    max_edges = max(e1, e2, 1)
    edge_sim = 1.0 - abs(e1 - e2) / max_edges
    
    # Spider type distribution (Z vs X ratio)
    z1 = sum(1 for l in D1.labels.values() if l.kind == 'Z')
    x1 = sum(1 for l in D1.labels.values() if l.kind == 'X')
    z2 = sum(1 for l in D2.labels.values() if l.kind == 'Z')
    x2 = sum(1 for l in D2.labels.values() if l.kind == 'X')
    
    if n1 > 0 and n2 > 0:
        ratio1 = z1 / n1
        ratio2 = z2 / n2
        type_sim = 1.0 - abs(ratio1 - ratio2)
    else:
        type_sim = 1.0
    
    # Phase distribution overlap (histogram)
    if D1.labels and D2.labels:
        phases1 = [l.phase_radians for l in D1.labels.values()]
        phases2 = [l.phase_radians for l in D2.labels.values()]
        
        # Bin phases into 16 bins over [0, 2π)
        hist1, _ = np.histogram(phases1, bins=16, range=(0, 2*np.pi), density=True)
        hist2, _ = np.histogram(phases2, bins=16, range=(0, 2*np.pi), density=True)
        
        # Cosine similarity
        norm1 = np.linalg.norm(hist1)
        norm2 = np.linalg.norm(hist2)
        if norm1 > 0 and norm2 > 0:
            phase_overlap = np.dot(hist1, hist2) / (norm1 * norm2)
        else:
            phase_overlap = 0.0
    else:
        phase_overlap = 1.0 if (not D1.labels and not D2.labels) else 0.0
    
    # Geometric mean of all components
    overlap = (node_sim * edge_sim * type_sim * phase_overlap) ** 0.25
    
    return float(overlap)


def compute_edit_distance(D1: ZXGraph, D2: ZXGraph) -> float:
    """
    Minimal edit distance between diagrams.
    
    Approximate as: |nodes difference| + |edge difference|
    
    True edit distance would be minimal ZX rewrites to transform D1 → D2.
    This is NP-hard, so we use structural proxy.
    """
    node_diff = abs(len(D1.nodes) - len(D2.nodes))
    edge_diff = abs(len(D1.edges) - len(D2.edges))
    
    # Label differences (if same node count)
    if len(D1.nodes) == len(D2.nodes):
        label_diff = 0
        for node in D1.nodes:
            if node in D2.nodes:
                l1 = D1.labels.get(node)
                l2 = D2.labels.get(node)
                if l1 and l2:
                    if l1.kind != l2.kind:
                        label_diff += 1
                    if abs(l1.phase_radians - l2.phase_radians) > 0.1:
                        label_diff += 0.5
    else:
        label_diff = 0
    
    return float(node_diff + edge_diff + label_diff)


def compute_coherence_matrix(diagrams: list) -> np.ndarray:
    """
    Compute full coherence matrix C([Dᵢ], [Dⱼ]) for all pairs.
    
    Theory.md Axiom 2: Coherence structure on configuration space.
    
    Returns:
        C_matrix: n×n matrix where C[i,j] = coherence(diagrams[i], diagrams[j])
    """
    n = len(diagrams)
    C_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            C_matrix[i, j] = coherence_between_diagrams(diagrams[i], diagrams[j])
    
    return C_matrix


def verify_coherence_properties(C_matrix: np.ndarray, tolerance=1e-6) -> Dict[str, bool]:
    """
    Verify coherence matrix satisfies Axiom 2 properties.
    
    Theory.md Axiom 2 (line 373-378):
    - C(x,y) = C(y,x) (symmetry)
    - C(x,x) = 1 (self-coherence)
    - C ∈ [0,1] (bounded)
    """
    n = C_matrix.shape[0]
    
    # Check symmetry
    symmetry_error = np.max(np.abs(C_matrix - C_matrix.T))
    is_symmetric = symmetry_error < tolerance
    
    # Check self-coherence = 1
    diagonal = np.diag(C_matrix)
    self_coherence_error = np.max(np.abs(diagonal - 1.0))
    is_self_coherent = self_coherence_error < tolerance
    
    # Check bounds [0, 1]
    is_bounded = np.all(C_matrix >= -tolerance) and np.all(C_matrix <= 1.0 + tolerance)
    
    return {
        'symmetric': is_symmetric,
        'symmetry_error': float(symmetry_error),
        'self_coherent': is_self_coherent,
        'self_coherence_error': float(self_coherence_error),
        'bounded': is_bounded,
        'min_value': float(np.min(C_matrix)),
        'max_value': float(np.max(C_matrix)),
        'all_valid': is_symmetric and is_self_coherent and is_bounded
    }

