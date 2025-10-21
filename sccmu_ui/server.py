#!/usr/bin/env python3
"""
SCCMU Backend Server

Serves Clifford field data from ZX-evolution engine to frontend (WebGL removed).

Run with: python3 sccmu_ui/server.py
Then open: http://localhost:8001/
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import threading
import time
import numpy as np
import os

from sccmu_ui.evolution_engine import ZXEvolutionEngine
from sccmu_ui.clifford_mapping import zx_to_clifford

app = Flask(__name__, static_folder='.')
CORS(app)

# Global engine instance
engine = ZXEvolutionEngine(ensemble_size=20)
current_state = {
    'clifford_components': np.zeros(16).tolist(),
    'num_nodes': 1,
    'num_edges': 0,
    'free_energy': 0.0,
    'mode_probability': 1.0,
    'time': 0.0,
    'convergence': {
        'converged': False,
        'lambda_max': 0.0,
        'residual': 1.0
    }
}

evolution_running = True


def evolution_thread():
    """Background thread evolving ZX-diagrams via master equation"""
    global current_state
    
    dt = 0.016  # 60 fps
    step_count = 0
    
    print("🌌 Evolution thread started")
    print(f"   Ensemble size: {engine.ensemble_size}")
    print(f"   Timestep: {dt}")
    
    while evolution_running:
        try:
            # Evolve one step
            state = engine.evolve_step(dt)
            
            # Map mode to Clifford
            clifford = zx_to_clifford(state['mode_graph'])
            
            # Get full state
            full_state = engine.get_state()
            
            # Update global state (ensure JSON serializable)
            current_state['clifford_components'] = clifford.tolist()
            current_state['num_nodes'] = int(full_state['num_nodes'])
            current_state['num_edges'] = int(full_state['num_edges'])
            current_state['free_energy'] = float(full_state['free_energy'])
            current_state['mode_probability'] = float(full_state['mode_probability'])
            current_state['time'] = float(full_state['time'])
            
            # Convergence dict - convert all numpy types to Python types
            conv = full_state['convergence']
            current_state['convergence'] = {
                'converged': bool(conv['converged']),
                'lambda_max': float(conv.get('lambda_max', 0.0)),
                'residual': float(conv.get('residual', 1.0)),
                'is_fixed_point': bool(conv.get('is_fixed_point', False)),
                'free_energy_stable': bool(conv.get('free_energy_stable', False))
            }
            
            step_count += 1
            
            # Log every 10 seconds
            if step_count % 600 == 0:
                print(f"t={full_state['time']:.1f}s: " +
                      f"nodes={full_state['num_nodes']}, " +
                      f"F={full_state['free_energy']:.4f}, " +
                      f"λ={full_state['convergence']['lambda_max']:.4f}")
            
            time.sleep(dt)
            
        except Exception as e:
            print(f"❌ Evolution error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(1.0)


@app.route('/')
def index():
    """Serve main HTML page"""
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)


@app.route('/state')
def get_state():
    """Return current Clifford field state"""
    return jsonify(current_state)


@app.route('/reset', methods=['POST'])
def reset():
    """Reset engine to seed graph"""
    global engine, current_state
    
    engine = ZXEvolutionEngine(ensemble_size=20)
    
    clifford = zx_to_clifford(engine.mode_graph)
    current_state['clifford_components'] = clifford.tolist()
    current_state['num_nodes'] = 1
    current_state['num_edges'] = 0
    current_state['time'] = 0.0
    
    return jsonify({'status': 'reset', 'message': 'Engine reset to seed graph'})


@app.route('/info')
def get_info():
    """Return theory information"""
    from sccmu_ui.zx_core import PHI
    from sccmu_ui.free_energy import BETA
    
    return jsonify({
        'theory': 'SCCMU (Self-Consistent Coherence-Maximizing Universe)',
        'version': '9.1',
        'config_space': 'ZX-diagrams (Definition 1.1.3)',
        'evolution': 'Master equation ∂ρ/∂t = ∇·(ρ∇δℱ/δρ) + ν∆ρ',
        'fixed_point': '𝒞ρ_∞ = λ_max ρ_∞',
        'phi': float(PHI),
        'beta': float(BETA),
        'nu': float(engine.nu)
    })


if __name__ == '__main__':
    # Start evolution thread
    thread = threading.Thread(target=evolution_thread, daemon=True)
    thread.start()
    
    print("=" * 60)
    print("🌌 SCCMU Backend Server")
    print("=" * 60)
    print("")
    print("Theory.md Implementation:")
    print("  ✅ Axiom 1: ZX-diagram configuration space")
    print("  ✅ Axiom 2: Coherence structure C([D₁], [D₂])")
    print("  ✅ Axiom 3: Free energy ℱ[ρ] = ℒ[ρ] - S[ρ]/β")
    print("  ✅ Axiom 4: φ-scaling")
    print("  ✅ Definition 2.1.3: Master equation")
    print("  ✅ Theorem 2.1.2: Fixed point convergence")
    print("  ✅ Theorem 1.0.3.3: ZX ≅ Clifford")
    print("")
    print(f"Server running at: http://localhost:8001")
    print(f"API endpoints:")
    print(f"  GET  /state  - Current Clifford field")
    print(f"  POST /reset  - Reset to seed")
    print(f"  GET  /info   - Theory information")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=8001, threaded=True, debug=False)
    except KeyboardInterrupt:
        evolution_running = False
        print("\n🛑 Server stopped")

