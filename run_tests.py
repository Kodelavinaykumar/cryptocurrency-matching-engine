#!/usr/bin/env python3
"""
GoQuant Matching Engine - Test Runner
This script provides easy testing of the matching engine.
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_unit_tests():
    """Run unit tests."""
    print("Running unit tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/test_matching_engine.py", "-v"
        ], check=True, capture_output=True, text=True)
        print("✓ Unit tests passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Unit tests failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def run_benchmark_tests():
    """Run benchmark tests."""
    print("Running benchmark tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/benchmark/", "-v", "--benchmark-only"
        ], check=True, capture_output=True, text=True)
        print("✓ Benchmark tests passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Benchmark tests failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def run_all_tests():
    """Run all tests."""
    print("Running all tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "-v"
        ], check=True, capture_output=True, text=True)
        print("✓ All tests passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Some tests failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def run_coverage_tests():
    """Run tests with coverage."""
    print("Running tests with coverage...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "--cov=src", "--cov-report=html", "--cov-report=term"
        ], check=True, capture_output=True, text=True)
        print("✓ Coverage tests passed")
        print("Coverage report generated in htmlcov/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Coverage tests failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="GoQuant Matching Engine Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark tests only")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("✗ Please run this script from the GoQuant project directory")
        return 1
    
    success = True
    
    if args.unit:
        success &= run_unit_tests()
    elif args.benchmark:
        success &= run_benchmark_tests()
    elif args.coverage:
        success &= run_coverage_tests()
    elif args.all:
        success &= run_all_tests()
    else:
        # Default: run all tests
        success &= run_all_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
