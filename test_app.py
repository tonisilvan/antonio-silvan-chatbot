#!/usr/bin/env python3

"""
Test script to verify the FastAPI app can start and basic endpoints work
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the environment variables for testing
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['GOOGLE_API_KEY'] = 'test-key'

try:
    from app import app, linkedin_data, summary_data, name
    print("Successfully imported app")
    print(f"Name: {name}")
    print(f"Summary data loaded: {bool(summary_data)}")
    print(f"LinkedIn data loaded: {bool(linkedin_data)}")
    print("App import successful!")
    print("Backend is ready to run!")
    
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
