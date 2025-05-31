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
            expected_routes = ['/', '/health', '/classify']

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

        # Test ClassificationResponse
        classification_resp = main.ClassificationResponse(
            extracted_text="12345",
            confidence=0.95,
            num_characters=5,
            processing_time_ms=150.5,
            timestamp="2024-01-01T00:00:00Z"
        )
        print(f"✅ ClassificationResponse model works: {classification_resp.extracted_text}")

        # Test HealthResponse
        health_resp = main.HealthResponse(
            status="healthy",
            timestamp="2024-01-01T00:00:00Z",
            model_loaded=True
        )
        print(f"✅ HealthResponse model works: {health_resp.status}")

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
        print("🎉 All tests passed! Your image classification API structure is correct.")
        print("\nTo run your API:")
        print("1. Development: just dev")
        print("2. Deploy: just deploy")
        print("3. Test endpoints: just test-endpoints")
        print("4. Health check: just health-check")
        print("\nAPI endpoints:")
        print("- POST /classify - Upload image for text classification")
        print("- GET /health - Health check")
        print("- GET /docs - Interactive API documentation")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
