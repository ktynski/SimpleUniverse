#!/usr/bin/env python3
"""
ZX-Diagram to Clifford Field Mapping

Implements Theory.md Theorem 1.0.3.3 (line 592-625):
    ZX ≅ Clifford correspondence

Maps ZX-diagrams → 16-component Clifford Cl(1,3) multivector.

Based on FIRM's phi_zx_to_clifford() implementation, 
adapted for our theory.

Test with: python3 -m pytest sccmu_ui/test_clifford_mapping.py
"""

import numpy as np
from typing import Dict, List, Tuple
from .zx_core import ZXGraph, PHI


def zx_to_clifford(graph: ZXGraph) -> np.ndarray:
    """
    Map ZX-diagram to 16-component Clifford multivector.
    
    Theory.md Theorem 1.0.3.3: ZX ≅ Clifford correspondence
    
    Mapping:
    - Z-spider rotations ↔ Clifford rotors exp(-½αB₁₂)
    - X-spiders ↔ Rotors in orthogonal bivector plane
    - Edge phase deltas → Gauge connection (vectors)
    - Cycles → Sovereignty structure (trivectors)
    
    Returns:
        components[16]: Clifford algebra components
            [0]: Scalar (grade-0)
            [1-4]: Vectors e₀,e₁,e₂,e₃ (grade-1)
            [5-10]: Bivectors e₀₁,e₀₂,e₀₃,e₁₂,e₁₃,e₂₃ (grade-2)
            [11-14]: Trivectors e₀₁₂,e₀₁₃,e₀₂₃,e₁₂₃ (grade-3)
            [15]: Pseudoscalar e₀₁₂₃ (grade-4)
    """
    graph.validate()
    
    components = np.zeros(16)
    
    if not graph.nodes:
        return components
    
    # Build adjacency for connectivity analysis
    adjacency = build_adjacency(graph)
    
    # === GRADE-0 & GRADE-2: Z/X-spiders → Rotors ===
    # Theory.md Theorem 1.0.3.3:
    # Z(α) ↔ exp(-½α e₁e₂) = cos(α/2) - sin(α/2) e₁e₂
    
    for node_id, label in graph.labels.items():
        phase = label.phase_radians
        degree = len(adjacency.get(node_id, []))
        weight = np.sqrt(1 + degree)  # Connectivity weight
        
        if label.kind == 'Z':
            # Z-spider → scalar rotor
            components[0] += weight * np.cos(phase / 2)      # Scalar
            components[5] += weight * np.sin(phase / 2)      # e₀₁ bivector
        
        elif label.kind == 'X':
            # X-spider → phase bivector (orthogonal plane)
            components[8] += weight * np.cos(phase)          # e₁₂ bivector
            components[9] += weight * np.sin(phase)          # e₁₃ bivector
    
    # === GRADE-1: Edge phase deltas → Vectors (gauge connection) ===
    # Theory: Connection from rotor phase deltas
    
    for u, v in graph.edges:
        label_u = graph.labels.get(u)
        label_v = graph.labels.get(v)
        
        if label_u and label_v:
            phase_u = label_u.phase_radians
            phase_v = label_v.phase_radians
            phase_delta = phase_v - phase_u
            
            # Connection strength
            deg_u = len(adjacency.get(u, []))
            deg_v = len(adjacency.get(v, []))
            connection_weight = np.sqrt((deg_u + deg_v) / 2) / max(len(graph.edges), 1)
            
            # Vector components from gauge connection
            components[1] += connection_weight * np.cos(phase_delta)
            components[2] += connection_weight * np.sin(phase_delta)
            components[3] += connection_weight * np.cos(2 * phase_delta)
            components[4] += connection_weight * np.sin(2 * phase_delta)
    
    # === GRADE-2: Mixed Z-X edges → Additional bivectors ===
    
    for u, v in graph.edges:
        label_u = graph.labels.get(u)
        label_v = graph.labels.get(v)
        
        if label_u and label_v and label_u.kind != label_v.kind:
            # Mixed edge (Z-X or X-Z)
            phase_u = label_u.phase_radians
            phase_v = label_v.phase_radians
            edge_weight = 1.0 / np.sqrt(max(len(graph.edges), 1))
            
            components[6] += edge_weight * np.sin(phase_u - phase_v)  # e₀₂
            components[7] += edge_weight * np.cos(phase_u + phase_v)  # e₀₃
            components[10] += edge_weight * np.sin(phase_u + phase_v) # e₂₃
    
    # === GRADE-3: Sovereign triads → Trivectors ===
    # Theory: Self-referential structure Ψ ≅ Hom(Ψ,Ψ)
    
    triads = detect_triangles(graph, adjacency)
    
    if triads:
        sovereignty_index = compute_sovereignty_from_triads(triads, graph)
        trivector_strength = sovereignty_index * np.sqrt(len(triads)) / max(len(graph.nodes), 1)
        
        for triad in triads:
            a, b, c = triad
            phase_a = graph.labels[a].phase_radians
            phase_b = graph.labels[b].phase_radians
            phase_c = graph.labels[c].phase_radians
            
            # Orientation from phase relationships
            orientation = (phase_a + phase_b + phase_c) / 3
            
            components[11] += trivector_strength * np.sin(orientation)
            components[12] += trivector_strength * np.cos(orientation)
            components[13] += trivector_strength * np.sin(2*orientation)
            components[14] += trivector_strength * np.cos(2*orientation)
    
    # === GRADE-4: Graph chirality → Pseudoscalar ===
    
    chirality = compute_graph_chirality(graph, adjacency)
    components[15] = chirality * 0.5
    
    # Normalize to unit magnitude
    magnitude = np.linalg.norm(components)
    if magnitude > 0:
        components /= magnitude
    
    return components


def build_adjacency(graph: ZXGraph) -> Dict[int, List[int]]:
    """Build adjacency list from edge list"""
    adjacency = {node: [] for node in graph.nodes}
    
    for u, v in graph.edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    
    return adjacency


def detect_triangles(graph: ZXGraph, adjacency: Dict[int, List[int]]) -> List[Tuple[int, int, int]]:
    """
    Find all triangles (3-cycles) in graph.
    
    Triangles represent sovereign triads (Theory: Ψ ≅ Hom(Ψ,Ψ)).
    """
    triangles = []
    nodes = list(graph.nodes)
    
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            for k in range(j+1, len(nodes)):
                a, b, c = nodes[i], nodes[j], nodes[k]
                
                # Check if forms triangle
                has_ab = b in adjacency.get(a, [])
                has_bc = c in adjacency.get(b, [])
                has_ca = a in adjacency.get(c, [])
                
                if has_ab and has_bc and has_ca:
                    triangles.append((a, b, c))
    
    return triangles


def compute_sovereignty_from_triads(triads: List[Tuple[int, int, int]], 
                                   graph: ZXGraph) -> float:
    """
    Compute sovereignty index from triangle coherence.
    
    Measures self-referential structure strength.
    """
    if not triads:
        return 0.0
    
    total_coherence = 0.0
    
    for a, b, c in triads:
        # Phase coherence within triad
        phase_a = graph.labels[a].phase_radians
        phase_b = graph.labels[b].phase_radians
        phase_c = graph.labels[c].phase_radians
        
        # Measure phase alignment
        phases = [phase_a, phase_b, phase_c]
        phase_var = np.var(phases)
        
        # High alignment → high sovereignty
        coherence = np.exp(-phase_var)
        total_coherence += coherence
    
    avg_coherence = total_coherence / len(triads)
    
    return avg_coherence


def compute_graph_chirality(graph: ZXGraph, adjacency: Dict[int, List[int]]) -> float:
    """
    Compute global chirality from Z/X imbalance and phase distribution.
    
    Maps to pseudoscalar (grade-4) Clifford component.
    """
    labels = list(graph.labels.values())
    
    if not labels:
        return 0.0
    
    # Z vs X imbalance
    z_count = sum(1 for l in labels if l.kind == 'Z')
    x_count = sum(1 for l in labels if l.kind == 'X')
    
    total = z_count + x_count
    if total == 0:
        return 0.0
    
    imbalance = (z_count - x_count) / total
    
    # Phase variance contributes to chirality
    phases = [l.phase_radians for l in labels]
    phase_var = np.var(phases) if len(phases) > 1 else 0.0
    
    chirality = imbalance * np.sqrt(phase_var) * 0.1
    
    return chirality


def get_clifford_grade_decomposition(components: np.ndarray) -> dict:
    """
    Decompose Clifford multivector by grade.
    
    Useful for analysis and visualization.
    """
    return {
        'scalar': float(components[0]),
        'vectors': components[1:5],
        'bivectors': components[5:11],
        'trivectors': components[11:15],
        'pseudoscalar': float(components[15]),
        'vector_magnitude': float(np.linalg.norm(components[1:5])),
        'bivector_magnitude': float(np.linalg.norm(components[5:11])),
        'trivector_magnitude': float(np.linalg.norm(components[11:15])),
        'total_magnitude': float(np.linalg.norm(components))
    }

