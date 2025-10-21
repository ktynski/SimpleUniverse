#!/usr/bin/env python3
"""
Regenerate All Figures with Standardized Styling

This script runs all figure generation scripts to create consistently
formatted figures for the SCCMU paper.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_script(script_path, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"Generating: {description}")
    print(f"Script: {script_path}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print("❌ FAILED")
            if result.stderr:
                print("Error:")
                print(result.stderr)
            if result.stdout:
                print("Output:")
                print(result.stdout)
                
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT - Script took too long to run")
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")

def main():
    """Main function to regenerate all figures"""
    print("🔄 REGENERATING ALL SCCMU PAPER FIGURES")
    print("="*60)
    
    # Change to implementations directory
    implementations_dir = Path("implementations")
    if not implementations_dir.exists():
        print("❌ implementations directory not found")
        return
    
    os.chdir(implementations_dir)
    
    # List of scripts to run with descriptions
    scripts = [
        ("alpha_rg_full_calculation.py", "Fine Structure Constant RG Evolution"),
        ("tfim_finite_size_analysis.py", "TFIM Finite-Size Scaling Analysis"),
        ("tfim_large_n_monte_carlo.py", "TFIM Large-N Monte Carlo Scaling"),
        ("weinberg_rge_rigorous.py", "Weinberg Angle RGE Evolution"),
        ("phi_constrained_rg.py", "Phi-Constrained RG Evolution"),
        ("ryu_takayanagi_explicit.py", "Ryu-Takayanagi Holographic Entanglement"),
    ]
    
    # Run each script
    for script_name, description in scripts:
        if Path(script_name).exists():
            run_script(script_name, description)
        else:
            print(f"⚠️  Script not found: {script_name}")
    
    print(f"\n{'='*60}")
    print("🎉 FIGURE REGENERATION COMPLETE")
    print("="*60)
    print("\nAll figures have been regenerated with standardized styling:")
    print("• Consistent sizing and spacing")
    print("• Professional typography")
    print("• High-resolution output (300 DPI)")
    print("• Proper alignment and formatting")
    print("\nFigures saved to: results/data/")

if __name__ == "__main__":
    main()
