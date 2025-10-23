#!/usr/bin/env python3
"""
Test runner script for GoQuant Matching Engine.
"""

import subprocess
import sys
import os

def run_unit_tests():
    """Run unit tests."""
    print("Running unit tests...")
    return subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_matching_engine.py", 
        "-v", "--tb=short"
    ]).returncode == 0

def run_benchmarks():
    """Run performance benchmarks."""
    print("Running performance benchmarks...")
    return subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/benchmark/test_performance.py", 
        "-v", "--benchmark-only", "--tb=short"
    ]).returncode == 0

def run_all_tests():
    """Run all tests."""
    print("Running all tests...")
    return subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", "--tb=short"
    ]).returncode == 0

def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "unit":
            success = run_unit_tests()
        elif test_type == "benchmark":
            success = run_benchmarks()
        elif test_type == "all":
            success = run_all_tests()
        else:
            print("Usage: python run_tests.py [unit|benchmark|all]")
            return 1
    else:
        success = run_all_tests()
    
    if success:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
