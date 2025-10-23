#!/usr/bin/env python3
"""
GoQuant Matching Engine Startup Script
This script provides easy startup and testing of the matching engine.
"""

import asyncio
import subprocess
import sys
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        import websockets  # noqa: F401
        import pydantic  # noqa: F401
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False

def start_server():
    """Start the matching engine server."""
    print("Starting GoQuant Matching Engine...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to start server: {e}")
        return False
    return True

def test_server():
    """Test if the server is running and responding."""
    print("Testing server connection...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Server is running and healthy")
            return True
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to server: {e}")
        return False

def run_tests():
    """Run the test suite."""
    print("Running tests...")
    try:
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], check=True)
        print("✓ All tests passed")
        return True
    except subprocess.CalledProcessError:
        print("✗ Some tests failed")
        return False

def run_benchmarks():
    """Run performance benchmarks."""
    print("Running performance benchmarks...")
    try:
        subprocess.run([sys.executable, "-m", "pytest", "tests/benchmark/", "-v", "--benchmark-only"], check=True)
        print("✓ Benchmarks completed")
        return True
    except subprocess.CalledProcessError:
        print("✗ Benchmarks failed")
        return False

def run_demo():
    """Run the demonstration client."""
    print("Running demonstration client...")
    try:
        subprocess.run([sys.executable, "test_client.py"], check=True)
        print("✓ Demonstration completed")
        return True
    except subprocess.CalledProcessError:
        print("✗ Demonstration failed")
        return False

def main():
    """Main startup function."""
    print("=" * 60)
    print("GoQuant Matching Engine - Startup Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("✗ Please run this script from the GoQuant project directory")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        print("\nInstalling missing dependencies...")
        if not install_dependencies():
            return 1
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            return 0 if run_tests() else 1
        elif command == "benchmark":
            return 0 if run_benchmarks() else 1
        elif command == "demo":
            return 0 if run_demo() else 1
        elif command == "server":
            return 0 if start_server() else 1
        else:
            print(f"Unknown command: {command}")
            print("Available commands: test, benchmark, demo, server")
            return 1
    
    # Interactive mode
    while True:
        print("\n" + "=" * 40)
        print("GoQuant Matching Engine - Main Menu")
        print("=" * 40)
        print("1. Start Server")
        print("2. Run Tests")
        print("3. Run Benchmarks")
        print("4. Run Demo")
        print("5. Test Server Connection")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            start_server()
        elif choice == "2":
            run_tests()
        elif choice == "3":
            run_benchmarks()
        elif choice == "4":
            run_demo()
        elif choice == "5":
            test_server()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    sys.exit(main())
