#!/usr/bin/env python3
"""
Test script for the refactored API structure
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health check endpoint."""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working: {data}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return False

def test_chat_endpoint():
    """Test the chat endpoint."""
    print("\n💬 Testing chat endpoint...")
    try:
        payload = {
            "input": "What tables are available in the database?",
            "config": {}
        }
        response = requests.post(
            "http://localhost:8000/chat/invoke",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat request successful: {data}")
            return True
        else:
            print(f"❌ Chat request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Refactored API Structure")
    print("=" * 40)
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        test_health_endpoint,
        test_root_endpoint,
        test_chat_endpoint,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactored API structure working correctly!")
    else:
        print("⚠️ Some tests failed. Check the server logs for details.")
    
    print("\n💡 To test manually:")
    print("   - Health: http://localhost:8000/health")
    print("   - Root: http://localhost:8000/")
    print("   - Chat: http://localhost:8000/chat/invoke")
    print("   - Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
