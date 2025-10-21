#!/usr/bin/env python3
"""
Grace-Weighted Dimensional Projection Calculator

This module implements computational methods for deriving the C factors
that bridge φ-structure to physical measurements.

Theory: Q = C · φⁿ where:
- φⁿ is the mathematical structure (derived)
- C is the grace-weighted projection constant (to be determined)
- Q is the observed physical quantity
"""

import numpy as np
from scipy.optimize import minimize, differential_evolution
from typing import Dict, Tuple, Optional, List
import yaml

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio


class GraceProjectionCalculator:
    """Calculate and derive Grace-Weighted Projection Constants"""
    
    def __init__(self):
        """Initialize calculator with known physics constants"""
        self.phi = PHI
        self.pi = np.pi
        
        # Known observations (for calibration)
        self.observations = {
            'muon_electron_mass': 206.768,
            'tau_muon_mass': 16.817,
            'fine_structure_inv': 137.036,
            'proton_electron_mass': 1836.152,
            'strong_coupling': 0.118,
            'dark_energy_ratio': 1e-52,  # In Planck units
        }
        
        # Known φ-structures (derived from theory)
        self.phi_structures = {
            'muon_electron_mass': 11,  # φ^11
            'tau_muon_mass': 6,         # φ^6
            'fine_structure_inv': -11,  # α^{-1} ∝ (4π^3)/φ^{11}
            'proton_electron_mass': -2, # m_p/m_e ∝ (32π^5/3) · φ^{-2}
            'strong_coupling': 2,        # φ^2
            'dark_energy_ratio': -250,  # φ^(-250)
        }

        # Structural prefactors K(quantity) multiplying φ^n (drawn from Theory.md)
        # These are not ad-hoc fits; they encode known structural factors so that residual C is smaller and theory-consistent.
        self.structure_prefactors = {
            'muon_electron_mass': lambda phi: 1.0,
            'tau_muon_mass': lambda phi: 1.0,
            'fine_structure_inv': lambda phi: 4 * (self.pi ** 3),  # α^{-1} = 4π^3 / φ^{11}
            'proton_electron_mass': lambda phi: (32 * (self.pi ** 5)) / 3.0,  # 32π^5/(3 φ^2)
            'strong_coupling': lambda phi: 1.0,
            'dark_energy_ratio': lambda phi: 1.0,
        }

        # Human-readable expressions for reporting
        self.structure_prefactor_expr = {
            'muon_electron_mass': '1',
            'tau_muon_mass': '1',
            'fine_structure_inv': '4π^3',
            'proton_electron_mass': '32π^5/3',
            'strong_coupling': '1',
            'dark_energy_ratio': '1',
        }
        
        # Calculated C factors
        self.c_factors = {}

    def structure_value(self, quantity: str) -> float:
        """
        Compute the structural prediction K(quantity) * φ^{n(quantity)}.
        """
        if quantity not in self.phi_structures:
            raise ValueError(f"Unknown φ-structure for: {quantity}")
        n = self.phi_structures[quantity]
        K = self.structure_prefactors.get(quantity, lambda phi: 1.0)(self.phi)
        return K * (self.phi ** n)
        
    def calculate_c_factor(self, quantity: str) -> float:
        """
        Calculate C factor for a given quantity
        
        C = Q_observed / φⁿ
        
        Args:
            quantity: Name of physical quantity
            
        Returns:
            Grace-weighted projection constant C
        """
        if quantity not in self.observations:
            raise ValueError(f"Unknown quantity: {quantity}")
        
        q_obs = self.observations[quantity]
        phi_struct = self.structure_value(quantity)
        
        c = q_obs / phi_struct if phi_struct != 0 else np.inf
        self.c_factors[quantity] = c
        
        return c
    
    def analyze_c_patterns(self) -> Dict:
        """
        Analyze patterns in C factors to find underlying structure
        
        Returns:
            Analysis results including potential φ-relationships
        """
        # Calculate all C factors
        for quantity in self.observations:
            self.calculate_c_factor(quantity)
        
        analysis = {
            'c_factors': self.c_factors,
            'c_as_phi_powers': {},
            'patterns': []
        }
        
        # Check if C factors are themselves φ-powers
        for quantity, c in self.c_factors.items():
            if c > 0:
                # Find closest φ-power
                log_c = np.log(c) / np.log(self.phi)
                nearest_int = round(log_c)
                error = abs(log_c - nearest_int)
                
                analysis['c_as_phi_powers'][quantity] = {
                    'c_value': c,
                    'log_phi': log_c,
                    'nearest_power': nearest_int,
                    'error': error,
                    'is_phi_power': error < 0.1  # Within 10% of integer power
                }
        
        # Look for patterns
        phi_powers = [v['nearest_power'] for v in analysis['c_as_phi_powers'].values() 
                     if v['is_phi_power']]
        
        if phi_powers:
            analysis['patterns'].append(f"C factors cluster near φ^n for n in {set(phi_powers)}")
        
        # Check for simple multiplicative factors
        for q1 in self.c_factors:
            for q2 in self.c_factors:
                if q1 != q2:
                    ratio = self.c_factors[q1] / self.c_factors[q2]
                    if abs(ratio - self.phi) < 0.1:
                        analysis['patterns'].append(f"C({q1})/C({q2}) ≈ φ")
                    elif abs(ratio - 1/self.phi) < 0.1:
                        analysis['patterns'].append(f"C({q1})/C({q2}) ≈ 1/φ")
        
        return analysis
    
    def derive_c_from_rg_flow(self, quantity: str, energy_scale: float = 91.2) -> float:
        """
        Attempt to derive C factor from renormalization group flow
        
        Args:
            quantity: Physical quantity name
            energy_scale: Energy scale in GeV (default: M_Z)
            
        Returns:
            Estimated C factor from RG considerations
        """
        # Simplified RG flow model
        # C(μ) = C₀ · (μ/μ₀)^γ where γ is anomalous dimension
        
        if quantity == 'muon_electron_mass':
            # Lepton masses run very slowly
            gamma = 0.004  # Approximate anomalous dimension
            mu_0 = 0.511e-3  # Electron mass scale in GeV
            mu = 0.106  # Muon mass scale in GeV
            c_0 = 1.0  # Boundary condition
            
            c_rg = c_0 * (mu / mu_0) ** gamma
            return c_rg
            
        elif quantity == 'fine_structure_inv':
            # QED running
            # α(μ) = α(0) / (1 - (α(0)/3π) ln(μ²/m_e²))
            alpha_0 = 1/137.036
            m_e = 0.511e-3  # GeV
            
            # At scale μ
            ln_factor = np.log((energy_scale / m_e) ** 2)
            alpha_mu = alpha_0 / (1 - (alpha_0 / (3 * np.pi)) * ln_factor)
            
            # Extract C factor
            c_rg = (1/alpha_mu) / (self.phi ** 11)
            return c_rg
        
        else:
            # Default: no RG correction
            return 1.0
    
    def derive_c_from_symmetry_breaking(self, quantity: str) -> float:
        """
        Derive C factor from symmetry breaking considerations
        
        Args:
            quantity: Physical quantity name
            
        Returns:
            Estimated C factor from symmetry breaking
        """
        if quantity == 'muon_electron_mass':
            # Electroweak symmetry breaking scale
            v_higgs = 246  # GeV
            m_e = 0.511e-3  # GeV
            m_mu = 0.106  # GeV
            
            # Yukawa coupling ratio
            y_ratio = m_mu / m_e
            
            # Expected from φ-structure
            phi_ratio = self.phi ** 11
            
            # C factor from symmetry breaking
            c_sb = y_ratio / phi_ratio
            return c_sb
            
        elif quantity == 'proton_electron_mass':
            # QCD confinement scale
            lambda_qcd = 0.217  # GeV
            m_p = 0.938  # GeV
            m_e = 0.511e-3  # GeV
            
            # Strong coupling at confinement
            alpha_s = 0.118
            
            # Dimensional analysis
            c_sb = (m_p / lambda_qcd) * (lambda_qcd / m_e) / self.phi
            return c_sb
        
        else:
            return 1.0
    
    def optimize_c_factors(self, constraints: Optional[Dict] = None) -> Dict:
        """
        Optimize C factors to minimize total error while respecting constraints
        
        Args:
            constraints: Optional constraints on C factors
            
        Returns:
            Optimized C factors and analysis
        """
        def objective(c_values):
            """Minimize total relative error"""
            total_error = 0
            for i, quantity in enumerate(self.observations):
                n = self.phi_structures[quantity]
                predicted = c_values[i] * (self.phi ** n)
                observed = self.observations[quantity]
                
                # Relative error
                if observed != 0:
                    error = ((predicted - observed) / observed) ** 2
                    total_error += error
            
        # Add regularization to prefer C factors that are φ-powers
            for c in c_values:
                if c > 0:
                    log_c = np.log(c) / np.log(self.phi)
                    distance_from_int = abs(log_c - round(log_c))
                    total_error += 0.1 * distance_from_int  # Regularization weight
            
            return total_error
        
        # Initial guess: current C factors
        x0 = [self.calculate_c_factor(q) for q in self.observations]
        
        # Bounds: C factors should be positive and reasonable
        bounds = [(1e-10, 1e10) for _ in self.observations]
        
        # Optimize
        result = differential_evolution(objective, bounds, seed=42, maxiter=1000)
        
        # Extract optimized C factors
        optimized = {}
        for i, quantity in enumerate(self.observations):
            optimized[quantity] = result.x[i]
        
        # Analyze optimization results
        analysis = {
            'optimized_c': optimized,
            'total_error': result.fun,
            'success': result.success,
            'predictions': {}
        }
        
        # Calculate predictions with optimized C
        for quantity in self.observations:
            base = self.structure_value(quantity)
            c_opt = optimized[quantity]
            predicted = c_opt * base
            observed = self.observations[quantity]
            
            analysis['predictions'][quantity] = {
                'observed': observed,
                'predicted': predicted,
                'error_percent': abs(predicted - observed) / observed * 100 if observed != 0 else 0
            }
        
        return analysis

    def explain_c_with_small_factors(self, c_value: float, max_power: int = 5) -> Dict:
        """
        Express C approximately as a product of small integer powers of
        {φ, 2π, π, 3}. Search exponents in [-max_power, max_power].
        Returns the best tuple and relative error.
        """
        bases = [self.phi, 2 * self.pi, self.pi, 3.0]
        names = ['φ', '2π', 'π', '3']
        best = {'exponents': [0,0,0,0], 'approx': 1.0, 'rel_error': float('inf')}
        if c_value <= 0:
            return best
        for a in range(-max_power, max_power+1):
            for b in range(-max_power, max_power+1):
                for c in range(-max_power, max_power+1):
                    for d in range(-max_power, max_power+1):
                        approx = (bases[0]**a) * (bases[1]**b) * (bases[2]**c) * (bases[3]**d)
                        if approx == 0:
                            continue
                        rel_error = abs(approx - c_value) / c_value
                        if rel_error < best['rel_error']:
                            best = {'exponents': [a,b,c,d], 'approx': approx, 'rel_error': rel_error}
        best['expression'] = " × ".join([
            f"{names[i]}^{best['exponents'][i]}" for i in range(4) if best['exponents'][i] != 0
        ]) or '1'
        return best
    
    def generate_yaml_report(self) -> str:
        """
        Generate YAML report of all C factor analyses
        
        Returns:
            YAML formatted string
        """
        # Calculate all C factors
        for quantity in self.observations:
            self.calculate_c_factor(quantity)
        
        # Perform analyses
        pattern_analysis = self.analyze_c_patterns()
        optimization = self.optimize_c_factors()
        
        report = {
            'grace_projection_analysis': {
                'timestamp': str(np.datetime64('now')),
                'golden_ratio': float(self.phi),
                'quantities': {}
            }
        }
        
        for quantity in self.observations:
            phi_n = float(self.phi ** self.phi_structures[quantity])
            struct_pref = float(self.structure_prefactors.get(quantity, lambda phi: 1.0)(self.phi))
            struct_value = float(self.structure_value(quantity))
            c_emp = float(self.c_factors[quantity])
            c_expl = self.explain_c_with_small_factors(c_emp)
            report['grace_projection_analysis']['quantities'][quantity] = {
                'observed': float(self.observations[quantity]),
                'phi_exponent': int(self.phi_structures[quantity]),
                'phi_only': phi_n,
                'structure_prefactor_expr': self.structure_prefactor_expr.get(quantity, '1'),
                'structure_prefactor_value': struct_pref,
                'structure_value': struct_value,
                'c_factor_empirical': c_emp,
                'c_factor_rg': float(self.derive_c_from_rg_flow(quantity)),
                'c_factor_symmetry': float(self.derive_c_from_symmetry_breaking(quantity)),
                'c_factor_optimized': float(optimization['optimized_c'][quantity]),
                'prediction_error': float(optimization['predictions'][quantity]['error_percent']),
                'c_factor_small_factorization': {
                    'expression': c_expl['expression'],
                    'approx_value': float(c_expl['approx']),
                    'relative_error': float(c_expl['rel_error'])
                }
            }
        
        # Add pattern analysis
        report['grace_projection_analysis']['patterns'] = pattern_analysis['patterns']
        
        # Add C as φ-powers analysis
        report['grace_projection_analysis']['c_as_phi_powers'] = {}
        for q, analysis in pattern_analysis['c_as_phi_powers'].items():
            report['grace_projection_analysis']['c_as_phi_powers'][q] = {
                'nearest_phi_power': int(analysis['nearest_power']),
                'is_phi_power': bool(analysis['is_phi_power'])
            }
        
        return yaml.dump(report, default_flow_style=False, sort_keys=False)
    
    def find_universal_c_formula(self) -> Optional[str]:
        """
        Attempt to find a universal formula for C factors
        
        Returns:
            Formula string if pattern found, None otherwise
        """
        # Hypothesis: C factors depend on dimension and scale
        # C = φ^a × (2π)^b × dimension^c
        
        # Try to fit: log(C) = a*log(φ) + b*log(2π) + c*log(d)
        
        c_values = []
        features = []
        
        for quantity in self.observations:
            c = self.calculate_c_factor(quantity)
            if c > 0:
                c_values.append(np.log(c))
                
                # Feature vector [log(φ), log(2π), log(dimension)]
                dimension = 4  # Spacetime dimension
                if 'mass' in quantity:
                    dimension = 1  # Mass dimension
                elif 'coupling' in quantity:
                    dimension = 0  # Dimensionless
                
                features.append([
                    np.log(self.phi),
                    np.log(2 * np.pi),
                    np.log(dimension) if dimension > 0 else 0
                ])
        
        if len(c_values) >= 3:
            # Least squares fit
            X = np.array(features)
            y = np.array(c_values)
            
            # Solve X @ coeffs = y
            coeffs, residual, rank, s = np.linalg.lstsq(X, y, rcond=None)
            
            a, b, c = coeffs
            
            # Check if coefficients are close to integers
            a_int = round(a)
            b_int = round(b)
            c_int = round(c)
            
            if abs(a - a_int) < 0.2 and abs(b - b_int) < 0.2:
                formula_parts = []
                if a_int != 0:
                    formula_parts.append(f"φ^{a_int}")
                if b_int != 0:
                    formula_parts.append(f"(2π)^{b_int}")
                if c_int != 0:
                    formula_parts.append(f"d^{c_int}")
                
                if formula_parts:
                    return " × ".join(formula_parts)
        
        return None


def main():
    """Run Grace Projection analysis and generate report"""
    
    print("="*60)
    print("GRACE-WEIGHTED DIMENSIONAL PROJECTION ANALYSIS")
    print("="*60)
    
    calculator = GraceProjectionCalculator()
    
    # Calculate basic C factors
    print("\n1. EMPIRICAL C FACTORS")
    print("-"*40)
    for quantity in calculator.observations:
        c = calculator.calculate_c_factor(quantity)
        print(f"{quantity:20s}: C = {c:.6f}")
    
    # Analyze patterns
    print("\n2. PATTERN ANALYSIS")
    print("-"*40)
    analysis = calculator.analyze_c_patterns()
    for pattern in analysis['patterns']:
        print(f"  • {pattern}")
    
    # Check if C factors are φ-powers
    print("\n3. C FACTORS AS φ-POWERS")
    print("-"*40)
    for quantity, result in analysis['c_as_phi_powers'].items():
        if result['is_phi_power']:
            print(f"{quantity:20s}: C ≈ φ^{result['nearest_power']}")
        else:
            print(f"{quantity:20s}: C ≈ φ^{result['log_phi']:.2f} (not integer)")
    
    # Try to find universal formula
    print("\n4. UNIVERSAL C FORMULA SEARCH")
    print("-"*40)
    formula = calculator.find_universal_c_formula()
    if formula:
        print(f"Potential universal formula: C ∝ {formula}")
    else:
        print("No simple universal formula found")
    
    # Optimize C factors
    print("\n5. OPTIMIZED C FACTORS")
    print("-"*40)
    optimization = calculator.optimize_c_factors()
    for quantity, pred in optimization['predictions'].items():
        print(f"{quantity:20s}: Error = {pred['error_percent']:.2f}%")
    
    # Generate YAML report
    report = calculator.generate_yaml_report()
    
    # Save report
    with open('grace_projection_analysis.yaml', 'w') as f:
        f.write(report)
    
    print("\n" + "="*60)
    print("Report saved to grace_projection_analysis.yaml")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
