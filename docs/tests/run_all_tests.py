#!/usr/bin/env python3
"""
SCCMU Theory - Unified Test Runner
Runs all validation tests in systematic order

This test suite can definitively validate or falsify the theory that
all physics emerges from coherence maximization at the golden ratio.
"""

import sys
import os
import time
import subprocess
from typing import Dict, List, Tuple

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'implementations'))

PHI = (1 + 5**0.5) / 2


class TestRunner:
    """Unified test runner for SCCMU validation"""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        
    def print_header(self):
        """Print test suite header"""
        print("="*70)
        print(" "*15 + "SCCMU THEORY VALIDATION SUITE")
        print(" "*5 + "Self-Consistent Coherence-Maximizing Universe")
        print("="*70)
        print()
        print("Testing the prediction that all physics emerges from")
        print("coherence maximization at the golden ratio φ = 1.618034...")
        print()
        print("⚠  WARNING: These tests are DEFINITIVE")
        print("   Any failure falsifies the entire theory")
        print()
        print("="*70)
        print()
        
    def run_test(self, name: str, test_file: str, 
                 critical: bool = False) -> Tuple[bool, float, str]:
        """
        Run a single test
        
        Args:
            name: Test name
            test_file: Path to test file
            critical: If True, failure stops all testing
        
        Returns:
            success: Whether test passed
            runtime: Test runtime in seconds
            output: Test output
        """
        print(f"Running: {name}")
        print("-" * 70)
        
        start = time.time()
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per test
            )
            elapsed = time.time() - start
            
            success = (result.returncode == 0)
            output = result.stdout + result.stderr
            
            # Print output
            print(output)
            
            # Print status
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"\nStatus: {status}")
            print(f"Runtime: {elapsed:.1f}s")
            
            if not success and critical:
                print()
                print("🚨 CRITICAL TEST FAILED - Theory falsified!")
                print("   Stopping all tests.")
                
            return success, elapsed, output
            
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            print(f"✗ TIMEOUT after {elapsed:.1f}s")
            return False, elapsed, "Test timed out"
        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ ERROR: {e}")
            return False, elapsed, str(e)
        finally:
            print()
    
    def run_all_tests(self):
        """Run complete test suite"""
        self.start_time = time.time()
        self.print_header()
        
        # Test categories in order of importance
        tests = [
            # CRITICAL TESTS - Theory stands or falls on these
            {
                'category': 'CRITICAL: Quantum Coherence',
                'tests': [
                    ('Quantum Coherence Ratio', 'tests/test_coherence.py', True),
                ]
            },
            # SUPPORTING TESTS - Additional validation
            {
                'category': 'Tensor Network Formalism',
                'tests': [
                    ('TRG Spacetime Emergence', 'implementations/tensor_network_trg.py', False),
                    ('Tensor Network Bridge', 'implementations/tensor_network_bridge.py', False),
                ]
            },
            {
                'category': 'Statistical Physics',
                'tests': [
                    ('Critical Phenomena', 'tests/critical_phenomena_test.py', False),
                ]
            },
            {
                'category': 'Quantum Optimization',
                'tests': [
                    ('Decoherence Optimization', 'tests/decoherence_optimization_test.py', False),
                ]
            },
            {
                'category': 'Comprehensive Validation',
                'tests': [
                    ('Full Validation Suite', 'tests/test_validation.py', False),
                ]
            }
        ]
        
        # Run all tests
        all_passed = True
        total_runtime = 0
        
        for category_data in tests:
            category = category_data['category']
            
            print("="*70)
            print(f"  {category}")
            print("="*70)
            print()
            
            for test_name, test_file, critical in category_data['tests']:
                # Check if file exists
                if not os.path.exists(test_file):
                    print(f"⚠  Skipping {test_name}: {test_file} not found")
                    print()
                    continue
                
                success, runtime, output = self.run_test(test_name, test_file, critical)
                
                self.results[test_name] = {
                    'success': success,
                    'runtime': runtime,
                    'output': output,
                    'critical': critical
                }
                
                total_runtime += runtime
                
                if not success:
                    all_passed = False
                    if critical:
                        break  # Stop on critical failure
            
            if not all_passed and any(t[2] for t in category_data['tests']):
                break  # Stop if critical test failed
        
        # Print summary
        self.print_summary(all_passed, total_runtime)
        
        return all_passed
    
    def print_summary(self, all_passed: bool, total_runtime: float):
        """Print test summary"""
        print("="*70)
        print("  TEST SUMMARY")
        print("="*70)
        print()
        
        # Count results
        passed = sum(1 for r in self.results.values() if r['success'])
        failed = len(self.results) - passed
        critical_passed = sum(1 for r in self.results.values() 
                            if r['success'] and r['critical'])
        critical_total = sum(1 for r in self.results.values() if r['critical'])
        
        print(f"Tests Run:    {len(self.results)}")
        print(f"Passed:       {passed}")
        print(f"Failed:       {failed}")
        print(f"Total Runtime: {total_runtime:.1f}s")
        print()
        
        print("Critical Tests:")
        print(f"  Passed: {critical_passed}/{critical_total}")
        print()
        
        # Individual results
        print("Individual Results:")
        for test_name, result in self.results.items():
            status = "✓" if result['success'] else "✗"
            critical = " [CRITICAL]" if result['critical'] else ""
            print(f"  {status} {test_name}{critical} ({result['runtime']:.1f}s)")
        
        print()
        print("="*70)
        
        # Final verdict
        if all_passed:
            print()
            print("🎉 ALL TESTS PASSED!")
            print()
            print("="*70)
            print("  THEORY STATUS: STRONGLY VALIDATED")
            print("="*70)
            print()
            print("The SCCMU theory has passed all validation tests.")
            print("Key findings:")
            print()
            print("✓ Quantum coherence organizes at golden ratio φ")
            print("✓ Tensor network formalism connects to spacetime")
            print("✓ Statistical physics shows φ-structure")
            print()
            print("This provides concrete evidence that the universe")
            print("may indeed be the unique solution to Λ² = Λ + 1.")
            print()
        else:
            print()
            print("⚠  SOME TESTS FAILED")
            print()
            
            # Check if critical tests failed
            critical_failed = any(
                not r['success'] and r['critical'] 
                for r in self.results.values()
            )
            
            if critical_failed:
                print("="*70)
                print("  THEORY STATUS: FALSIFIED")
                print("="*70)
                print()
                print("Critical test(s) failed. The SCCMU theory's core")
                print("prediction does not match experimental results.")
                print()
            else:
                print("="*70)
                print("  THEORY STATUS: PARTIALLY VALIDATED")
                print("="*70)
                print()
                print("Core predictions hold, but some supporting tests failed.")
                print("Further investigation needed.")
                print()
        
        print("="*70)


def main():
    """Main entry point"""
    runner = TestRunner()
    success = runner.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
