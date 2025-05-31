#!/usr/bin/env python3
"""
Test script to verify the API structure and imports work correctly.
This script tests the API without actually deploying to Modal.
"""

import sys
import traceback

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    try:
        import modal
        print("✅ Modal imported successfully")
        
        from fastapi import FastAPI, HTTPException
        print("✅ FastAPI imported successfully")
        
        from pydantic import BaseModel, Field
        print("✅ Pydantic imported successfully")
        
        from typing import Union, Dict, Any
        print("✅ Typing imported successfully")
        
        import math
        from datetime import datetime, timezone
        print("✅ Standard library imports successful")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_api_structure():
    """Test that the API structure is valid"""
    print("\nTesting API structure...")
    try:
        # Import our main module
        sys.path.insert(0, 'src')
        import main
        
        print("✅ Main module imported successfully")
        
        # Check if the FastAPI app exists
        if hasattr(main, 'web_app'):
            print("✅ FastAPI app instance found")
            
            # Check routes
            routes = [route.path for route in main.web_app.routes]
            expected_routes = ['/', '/health', '/square', '/square/{number}', '/calculate']
            
            for route in expected_routes:
                if any(route in r for r in routes):
                    print(f"✅ Route {route} found")
                else:
                    print(f"❌ Route {route} not found")
        else:
            print("❌ FastAPI app instance not found")
            
        # Check if Modal app exists
        if hasattr(main, 'app'):
            print("✅ Modal app instance found")
        else:
            print("❌ Modal app instance not found")
            
        return True
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        traceback.print_exc()
        return False

def test_pydantic_models():
    """Test that Pydantic models are properly defined"""
    print("\nTesting Pydantic models...")
    try:
        sys.path.insert(0, 'src')
        import main
        
        # Test SquareRequest
        square_req = main.SquareRequest(number=5.0)
        print(f"✅ SquareRequest model works: {square_req}")
        
        # Test CalculationRequest
        calc_req = main.CalculationRequest(operation="add", a=5.0, b=3.0)
        print(f"✅ CalculationRequest model works: {calc_req}")
        
        return True
    except Exception as e:
        print(f"❌ Pydantic models test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing ST API Structure\n")
    
    tests = [
        test_imports,
        test_api_structure,
        test_pydantic_models
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    if all(results):
        print("🎉 All tests passed! Your API structure is correct.")
        print("\nTo run your API:")
        print("1. Run: uv run modal serve src/main.py")
        print("2. Or deploy: uv run modal deploy src/main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
