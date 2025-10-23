#!/bin/bash
set -e
echo "Running all Python tests..."
python3 run_all_tests.py
echo "Running JS tests (if any)..."
node test_dissonance_evolution.js
echo "All tests passed."
