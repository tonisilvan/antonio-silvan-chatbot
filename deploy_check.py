#!/usr/bin/env python3
"""
Pre-deployment check script for Railway deployment
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"  [OK] {description}")
        return True
    else:
        print(f"  [MISSING] {description}")
        return False

def check_directory_structure():
    """Check required directory structure"""
    print("\n=== Directory Structure Check ===")
    
    checks = [
        ("app.py", "Main FastAPI application"),
        ("start_server.py", "Server startup script"),
        ("requirements.txt", "Python dependencies"),
        ("railway.json", "Railway configuration"),
        ("nixpacks.toml", "Nixpacks build configuration"),
        ("Procfile", "Process configuration"),
        ("data/", "Data directory"),
        ("data/summary.txt", "Summary data file"),
        (".env.example", "Environment variables example"),
        ("README.md", "Documentation"),
        ("RAILWAY_DEPLOYMENT.md", "Deployment guide"),
    ]
    
    all_good = True
    for file_path, description in checks:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_requirements():
    """Check requirements.txt content"""
    print("\n=== Requirements Check ===")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().strip().split("\n")
        
        required_packages = ["fastapi", "uvicorn", "openai", "python-dotenv", "pydantic"]
        found_packages = [req.split("==")[0] for req in requirements if req.strip()]
        
        for package in required_packages:
            if package in found_packages:
                print(f"  [OK] {package} in requirements")
            else:
                print(f"  [MISSING] {package} not in requirements")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Could not read requirements.txt: {e}")
        return False

def check_app_imports():
    """Check if the main app can be imported"""
    print("\n=== Import Check ===")
    
    try:
        # Mock environment variables
        os.environ['OPENAI_API_KEY'] = 'test-key'
        os.environ['GOOGLE_API_KEY'] = 'test-key'
        
        from app import app, linkedin_data, summary_data, name
        print(f"  [OK] App imports successfully")
        print(f"  [OK] Name: {name}")
        print(f"  [OK] Summary data loaded: {bool(summary_data)}")
        print(f"  [OK] LinkedIn data loaded: {bool(linkedin_data)}")
        return True
    except Exception as e:
        print(f"  [ERROR] Import failed: {e}")
        return False

def check_railway_config():
    """Check Railway configuration files"""
    print("\n=== Railway Configuration Check ===")
    
    try:
        import json
        
        # Check railway.json
        with open("railway.json", "r") as f:
            config = json.load(f)
        
        required_keys = ["build", "deploy"]
        for key in required_keys:
            if key in config:
                print(f"  [OK] {key} in railway.json")
            else:
                print(f"  [MISSING] {key} in railway.json")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Railway config check failed: {e}")
        return False

def main():
    """Run all checks"""
    print("=== Railway Deployment Pre-Check ===")
    print("This script verifies that everything is ready for Railway deployment.\n")
    
    checks = [
        check_directory_structure,
        check_requirements,
        check_app_imports,
        check_railway_config,
    ]
    
    all_passed = True
    for check_func in checks:
        if not check_func():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("  [SUCCESS] All checks passed! Ready for Railway deployment.")
        print("\nNext steps:")
        print("1. Push your code to Git")
        print("2. Create a new Railway project")
        print("3. Configure environment variables")
        print("4. Deploy!")
    else:
        print("  [WARNING] Some checks failed. Please fix issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
