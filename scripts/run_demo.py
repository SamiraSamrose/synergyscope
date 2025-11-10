# File: scripts/run_demo.py
# Purpose: Demo runner with sample data initialization

#!/usr/bin/env python3
"""
SynergyScope Demo Runner
Starts the application in demo mode with sample data
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the demo application"""
    print("=" * 60)
    print("SynergyScope - Interactive Demo Mode")
    print("=" * 60)
    print()
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Virtual environment not found. Creating...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("Virtual environment created.")
        print()
    
    # Activate virtual environment
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"
    
    # Install dependencies if needed
    print("Checking dependencies...")
    subprocess.run([str(python_path), "-m", "pip", "install", "-q", "-r", "backend/requirements.txt"])
    print("Dependencies OK")
    print()
    
    # Set demo mode environment variable
    os.environ["DEMO_MODE"] = "true"
    os.environ["DEBUG"] = "true"
    
    # Start the application
    print("Starting SynergyScope Demo Server...")
    print("=" * 60)
    print()
    print("Access the demo at: http://localhost:8000/demo.html")
    print("Main dashboard at: http://localhost:8000/")
    print("API docs at: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        subprocess.run([
            str(python_path), "-m", "uvicorn",
            "backend.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\nShutting down demo server...")
        print("Thank you for using SynergyScope!")

if __name__ == "__main__":
    main()
