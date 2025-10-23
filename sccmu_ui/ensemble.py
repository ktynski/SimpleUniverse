#!/usr/bin/env python3
"""
Improved Ensemble Generation for ZX-Diagrams

Creates diverse, interesting ZX-diagram ensembles for evolution.
Avoids "converges to seed" problem by generating larger initial structures.

Theory compliance: All operations are local ZX-rewrites
"""

import numpy as np
from typing import List, Set, Tuple, Dict
from .zx_core import ZXGraph, NodeLabel, create_seed_graph, PHI, add_phases


def generate_random_graph(num_nodes: int = 5, 
                          edge_probability: float = 0.3,
                          seed: int = None) -> ZXGraph:
    """
    Generate random ZX-diagram with specified size.
    
    Args:
        num_nodes: Number of nodes
        edge_probability: Probability of edge between nodes
        seed: Random seed for reproducibility
    
    Returns:
        Random ZXGraph
    """
    if seed is not None:
        np.random.seed(seed)
    
    nodes = list(range(num_nodes))
    edges = []
    labels = {}
    
    # Generate edges (Erdős-Rényi)
    for i in range(num_nodes):
        for j in range(i+1, num_nodes):
            if np.random.random() < edge_probability:
                edges.append((i, j))
    
    # Generate random labels
    for node_id in nodes:
        kind = np.random.choice(['Z', 'X'], p=[0.6, 0.4])  # Bias toward Z
        phase_n = np.random.randint(0, 8)
        phase_d = 8
        labels[node_id] = NodeLabel(kind, phase_n, phase_d, node_id)
    
    return ZXGraph(nodes, edges, labels)


def generate_diverse_ensemble(size: int = 50,
                              min_nodes: int = 1,
                              max_nodes: int = 10) -> List[ZXGraph]:
    """
    Generate diverse ensemble of ZX-diagrams with varied sizes.
    
    Creates mixture of:
    - Small graphs (1-3 nodes)
    - Medium graphs (4-7 nodes)
    - Large graphs (8-10 nodes)
    
    Args:
        size: Number of diagrams to generate
        min_nodes: Minimum number of nodes
        max_nodes: Maximum number of nodes
    
    Returns:
        List of diverse ZX-diagrams
    """
    ensemble = []
    
    # Size distribution: More medium-sized graphs
    # 20% small, 60% medium, 20% large
    size_ranges = [
        (min_nodes, 3, int(0.2 * size)),  # Small
        (4, 7, int(0.6 * size)),           # Medium
        (8, max_nodes, int(0.2 * size))    # Large
    ]
    
    diagram_count = 0
    for min_n, max_n, count in size_ranges:
        for _ in range(count):
            if diagram_count >= size:
                break
            
            num_nodes = np.random.randint(min_n, max_n + 1)
            edge_prob = 0.3 + 0.2 * np.random.random()  # 0.3-0.5
            
            graph = generate_random_graph(num_nodes, edge_prob)
            ensemble.append(graph)
            diagram_count += 1
    
    # Fill remaining with medium-sized graphs
    while len(ensemble) < size:
        num_nodes = np.random.randint(4, 8)
        graph = generate_random_graph(num_nodes, 0.4)
        ensemble.append(graph)
    
    return ensemble[:size]


def generate_variations_improved(graph: ZXGraph, 
                                max_variations: int = 30,
                                exploration_factor: float = 1.0) -> List[ZXGraph]:
    """
    Improved variation generation with more diverse operations.
    
    Exploration factor controls how far from seed to explore:
    - 1.0 = normal (local changes)
    - 2.0 = aggressive (larger changes)
    - 0.5 = conservative (minimal changes)
    
    Operations:
    1. Add single node
    2. Add multiple nodes (new: for exploration)
    3. Remove node (new: allows contraction)
    4. Add edge
    5. Remove edge (new: allows breaking)
    6. Flip spider type (Z ↔ X)
    7. Change phase
    8. Multiple simultaneous changes (new)
    
    Args:
        graph: Source graph
        max_variations: Maximum number of variations
        exploration_factor: How aggressively to explore (>1 = more aggressive)
    
    Returns:
        List of varied ZX-diagrams
    """
    variations = [graph.copy()]  # Always include original
    
    max_nodes = int(15 * exploration_factor)
    num_simultaneous = max(1, int(2 * exploration_factor))
    
    # 1. Add single node (bootstrap/grace)
    if len(graph.nodes) < max_nodes:
        for source in graph.nodes[:min(5, len(graph.nodes))]:
            if len(variations) >= max_variations:
                break
            
            var = graph.copy()
            new_id = max(var.nodes) + 1 if var.nodes else 0
            var.nodes.append(new_id)
            var.edges.append((source, new_id))
            
            # Random label
            kind = np.random.choice(['Z', 'X'], p=[0.7, 0.3])
            phase_n = np.random.randint(0, 8)
            var.labels[new_id] = NodeLabel(kind, phase_n, 8, new_id)
            
            variations.append(var)
    
    # 2. Add multiple nodes (exploration)
    if exploration_factor > 1.0 and len(graph.nodes) < max_nodes - 2:
        for source in graph.nodes[:min(3, len(graph.nodes))]:
            if len(variations) >= max_variations:
                break
            
            var = graph.copy()
            
            # Add 2-3 nodes in chain
            num_to_add = min(3, max_nodes - len(var.nodes))
            prev_id = source
            
            for _ in range(num_to_add):
                new_id = max(var.nodes) + 1
                var.nodes.append(new_id)
                var.edges.append((prev_id, new_id))
                
                kind = np.random.choice(['Z', 'X'])
                phase_n = np.random.randint(0, 8)
                var.labels[new_id] = NodeLabel(kind, phase_n, 8, new_id)
                
                prev_id = new_id
            
            variations.append(var)
    
    # 3. Remove node (contraction)
    if len(graph.nodes) > 1:
        # Remove leaves (nodes with degree 1)
        for node in graph.nodes[:min(3, len(graph.nodes))]:
            if len(variations) >= max_variations:
                break
            
            # Count edges
            degree = sum(1 for u, v in graph.edges if u == node or v == node)
            
            if degree <= 1:  # Leaf or isolated
                var = graph.copy()
                var.nodes.remove(node)
                del var.labels[node]
                var.edges = [(u, v) for u, v in var.edges if u != node and v != node]
                variations.append(var)
    
    # 4. Add edge (if not too dense)
    current_edges = len(graph.edges)
    max_edges = len(graph.nodes) * (len(graph.nodes) - 1) // 2
    
    if current_edges < max_edges * 0.5:  # Less than 50% dense
        for i, u in enumerate(graph.nodes[:min(4, len(graph.nodes))]):
            if len(variations) >= max_variations:
                break
            
            for v in graph.nodes[i+1:min(i+4, len(graph.nodes))]:
                if (u, v) not in graph.edges and (v, u) not in graph.edges:
                    var = graph.copy()
                    var.edges.append((u, v))
                    variations.append(var)
                    break
    
    # 5. Remove edge
    if len(graph.edges) > 0:
        for edge in graph.edges[:min(3, len(graph.edges))]:
            if len(variations) >= max_variations:
                break
            
            var = graph.copy()
            var.edges.remove(edge)
            variations.append(var)
    
    # 6. Flip spider type (Z ↔ X)
    for node in graph.nodes[:min(5, len(graph.nodes))]:
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
    
    # 7. Change phase
    for node in graph.nodes[:min(5, len(graph.nodes))]:
        if len(variations) >= max_variations:
            break
        
        var = graph.copy()
        old_label = var.labels[node]
        
        # Vary phase by ±π/8 or ±π/4
        delta_n = np.random.choice([-2, -1, 1, 2])
        new_n, new_d = add_phases(old_label.phase_numer, old_label.phase_denom, delta_n, 8)
        var.labels[node] = NodeLabel(
            old_label.kind,
            new_n, new_d,
            old_label.node_id
        )
        variations.append(var)
    
    # 8. Multiple simultaneous changes (exploration)
    if exploration_factor > 0.8:
        for _ in range(min(5, int(max_variations * 0.1))):
            if len(variations) >= max_variations:
                break
            
            var = graph.copy()
            
            # Apply 2-3 random changes
            for _ in range(num_simultaneous):
                operation = np.random.choice(['add_node', 'flip_type', 'change_phase'])
                
                if operation == 'add_node' and len(var.nodes) < max_nodes:
                    source = np.random.choice(var.nodes) if var.nodes else 0
                    new_id = max(var.nodes) + 1 if var.nodes else 0
                    var.nodes.append(new_id)
                    var.edges.append((source, new_id))
                    kind = np.random.choice(['Z', 'X'])
                    phase_n = np.random.randint(0, 8)
                    var.labels[new_id] = NodeLabel(kind, phase_n, 8, new_id)
                
                elif operation == 'flip_type' and var.nodes:
                    node = np.random.choice(var.nodes)
                    old = var.labels[node]
                    new_kind = 'X' if old.kind == 'Z' else 'Z'
                    var.labels[node] = NodeLabel(new_kind, old.phase_numer, old.phase_denom, old.node_id)
                
                elif operation == 'change_phase' and var.nodes:
                    node = np.random.choice(var.nodes)
                    old = var.labels[node]
                    delta_n = np.random.randint(-3, 4)
                    new_n, new_d = add_phases(old.phase_numer, old.phase_denom, delta_n, 8)
                    var.labels[node] = NodeLabel(old.kind, new_n, new_d, old.node_id)
            
            variations.append(var)
    
    return variations[:max_variations]


def generate_biased_ensemble(size: int = 50,
                            bias_toward_size: int = 7,
                            spread: float = 2.0) -> List[ZXGraph]:
    """
    Generate ensemble biased toward specific size.
    
    Useful for starting evolution near interesting regime.
    
    Args:
        size: Number of diagrams
        bias_toward_size: Target number of nodes (mean)
        spread: Standard deviation of size distribution
    
    Returns:
        List of ZX-diagrams centered on target size
    """
    ensemble = []
    
    for _ in range(size):
        # Sample size from normal distribution
        num_nodes = int(np.clip(np.random.normal(bias_toward_size, spread), 1, 15))
        edge_prob = 0.3 + 0.1 * np.random.random()
        
        graph = generate_random_graph(num_nodes, edge_prob)
        ensemble.append(graph)
    
    return ensemble


def estimate_ensemble_diversity(ensemble: List[ZXGraph]) -> Dict:
    """
    Estimate diversity of ensemble.
    
    Measures:
    - Size distribution
    - Type distribution (Z vs X)
    - Phase distribution
    - Edge density distribution
    
    Args:
        ensemble: List of ZX-diagrams
    
    Returns:
        Dictionary with diversity metrics
    """
    sizes = [len(g.nodes) for g in ensemble]
    edges = [len(g.edges) for g in ensemble]
    
    z_counts = []
    x_counts = []
    phases = []
    densities = []
    
    for g in ensemble:
        z_count = sum(1 for l in g.labels.values() if l.kind == 'Z')
        x_count = sum(1 for l in g.labels.values() if l.kind == 'X')
        z_counts.append(z_count)
        x_counts.append(x_count)
        
        for l in g.labels.values():
            phases.append(l.phase_radians)
        
        max_edges = len(g.nodes) * (len(g.nodes) - 1) / 2
        density = len(g.edges) / max_edges if max_edges > 0 else 0
        densities.append(density)
    
    return {
        'size_mean': float(np.mean(sizes)),
        'size_std': float(np.std(sizes)),
        'size_min': int(np.min(sizes)),
        'size_max': int(np.max(sizes)),
        'edge_mean': float(np.mean(edges)),
        'edge_std': float(np.std(edges)),
        'z_fraction': float(np.sum(z_counts) / (np.sum(z_counts) + np.sum(x_counts))) if (np.sum(z_counts) + np.sum(x_counts)) > 0 else 0,
        'phase_mean': float(np.mean(phases)),
        'phase_std': float(np.std(phases)),
        'density_mean': float(np.mean(densities)),
        'density_std': float(np.std(densities))
    }


if __name__ == "__main__":
    # Demo ensemble generation
    print("=" * 80)
    print("SCCMU Improved Ensemble Generation")
    print("=" * 80)
    
    print("\n1. Diverse Ensemble (size=50):")
    print("-" * 80)
    ensemble_diverse = generate_diverse_ensemble(50, min_nodes=1, max_nodes=10)
    diversity = estimate_ensemble_diversity(ensemble_diverse)
    
    print(f"Size: mean={diversity['size_mean']:.1f} ± {diversity['size_std']:.1f}, " +
          f"range=[{diversity['size_min']}, {diversity['size_max']}]")
    print(f"Edges: mean={diversity['edge_mean']:.1f} ± {diversity['edge_std']:.1f}")
    print(f"Z/X ratio: {diversity['z_fraction']:.1%} Z, {1-diversity['z_fraction']:.1%} X")
    print(f"Edge density: {diversity['density_mean']:.1%} ± {diversity['density_std']:.1%}")
    
    print("\n2. Biased Ensemble (toward size=7):")
    print("-" * 80)
    ensemble_biased = generate_biased_ensemble(50, bias_toward_size=7, spread=2.0)
    diversity_biased = estimate_ensemble_diversity(ensemble_biased)
    
    print(f"Size: mean={diversity_biased['size_mean']:.1f} ± {diversity_biased['size_std']:.1f}, " +
          f"range=[{diversity_biased['size_min']}, {diversity_biased['size_max']}]")
    print(f"Edges: mean={diversity_biased['edge_mean']:.1f} ± {diversity_biased['edge_std']:.1f}")
    
    print("\n3. Improved Variations (exploration_factor=1.5):")
    print("-" * 80)
    seed_graph = create_seed_graph()
    variations = generate_variations_improved(seed_graph, max_variations=30, exploration_factor=1.5)
    
    print(f"Generated {len(variations)} variations from seed")
    variation_sizes = [len(v.nodes) for v in variations]
    print(f"Size range: [{min(variation_sizes)}, {max(variation_sizes)}]")
    print(f"Mean size: {np.mean(variation_sizes):.1f}")

