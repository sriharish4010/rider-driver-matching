#!/usr/bin/env python3
"""
Quick verification script to check backend installation
Run this to verify all files are present and properly configured
"""

import os
import sys

def check_file(filepath, description):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}")
    return exists

def main():
    print("\n" + "="*70)
    print("  PySpark Backend Installation Verification")
    print("="*70 + "\n")
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check core files
    print("Core Backend Files:")
    print("-" * 70)
    checks = []
    checks.append(check_file(os.path.join(backend_dir, "app.py"), "Flask API Server"))
    checks.append(check_file(os.path.join(backend_dir, "spark_matcher.py"), "PySpark Matching Engine"))
    checks.append(check_file(os.path.join(backend_dir, "requirements.txt"), "Python Dependencies"))
    checks.append(check_file(os.path.join(backend_dir, "config.ini"), "Configuration File"))
    
    print("\nStartup Scripts:")
    print("-" * 70)
    checks.append(check_file(os.path.join(backend_dir, "start.bat"), "Windows Startup Script"))
    checks.append(check_file(os.path.join(backend_dir, "start.sh"), "Unix/Linux Startup Script"))
    
    print("\nTest Files:")
    print("-" * 70)
    checks.append(check_file(os.path.join(backend_dir, "test_matcher.py"), "PySpark Matcher Tests"))
    checks.append(check_file(os.path.join(backend_dir, "test_api.py"), "API Integration Tests"))
    checks.append(check_file(os.path.join(backend_dir, "sample_api_data.json"), "Sample API Data"))
    
    print("\nDocumentation:")
    print("-" * 70)
    checks.append(check_file(os.path.join(backend_dir, "README.md"), "Backend Documentation"))
    checks.append(check_file(os.path.join(backend_dir, "QUICKSTART.md"), "Quick Start Guide"))
    checks.append(check_file(os.path.join(backend_dir, ".gitignore"), "Git Ignore File"))
    
    print("\nData Files (Parent Directory):")
    print("-" * 70)
    parent_dir = os.path.dirname(backend_dir)
    checks.append(check_file(os.path.join(parent_dir, "drivers.json"), "Sample Drivers Data"))
    checks.append(check_file(os.path.join(parent_dir, "riders.json"), "Sample Riders Data"))
    
    # Check Python
    print("\nPython Environment:")
    print("-" * 70)
    print(f"✅ Python Version: {sys.version.split()[0]}")
    
    # Check if virtual environment exists
    venv_path = os.path.join(backend_dir, "venv")
    if os.path.exists(venv_path):
        print(f"✅ Virtual Environment: Found at {venv_path}")
    else:
        print(f"⚠️  Virtual Environment: Not created yet (run start script)")
    
    # Summary
    print("\n" + "="*70)
    total = len(checks)
    passed = sum(checks)
    
    if passed == total:
        print(f"✅ SUCCESS: All {total} files verified!")
        print("\nNext Steps:")
        print("  1. Run startup script:")
        print("     Windows:   .\\start.bat")
        print("     Unix:      ./start.sh")
        print("  2. Test the backend:")
        print("     python test_matcher.py")
        print("  3. Start the API server:")
        print("     python app.py")
    else:
        print(f"⚠️  WARNING: {total - passed} file(s) missing!")
        print("Some files may not be installed correctly.")
    
    print("="*70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
