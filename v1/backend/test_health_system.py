"""
AI Base Project v1 - Simple Health Check Test
Tests the health check endpoints without requiring all dependencies
"""

import subprocess
import sys
import time
import json


def check_server_running():
    """Check if the FastAPI server is running."""
    try:
        import requests

        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def test_health_endpoints():
    """Test all health check endpoints."""
    try:
        import requests

        endpoints = [
            ("/api/v1/health", "Basic Health Check"),
            ("/api/v1/health/detailed", "Detailed Health Check"),
            ("/api/v1/health/database", "Database Health Check"),
            ("/api/v1/health/system", "System Health Check"),
            ("/api/v1/health/dependencies", "Dependencies Health Check"),
        ]

        print("🔍 Testing Health Check Endpoints")
        print("-" * 40)

        for endpoint, description in endpoints:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
                status = (
                    "✅ PASS"
                    if response.status_code == 200
                    else f"❌ FAIL ({response.status_code})"
                )
                print(f"{status} {description}")

                if response.status_code == 200:
                    data = response.json()
                    if "status" in data:
                        print(f"     Status: {data['status']}")
                    if "timestamp" in data:
                        print(f"     Time: {data['timestamp']}")
                else:
                    print(f"     Error: {response.text[:100]}")

            except Exception as e:
                print(f"❌ FAIL {description}")
                print(f"     Error: {str(e)}")

            print()

        return True

    except ImportError:
        print("❌ requests library not available for testing")
        print("Install with: pip install requests")
        return False


def test_basic_import():
    """Test if we can import our modules."""
    print("🔍 Testing Module Imports")
    print("-" * 40)

    modules = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("sqlalchemy", "Database ORM"),
        ("pydantic", "Data validation"),
        ("psutil", "System monitoring"),
        ("requests", "HTTP client for testing"),
    ]

    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - {description}")
        except ImportError:
            print(f"❌ {module_name} - {description} (not installed)")

    print()


def main():
    """Main test function."""
    print("=" * 60)
    print("   AI Base Project v1 - Health Check Test")
    print("=" * 60)
    print()

    # Test imports
    test_basic_import()

    # Check if server is running
    if check_server_running():
        print("✅ FastAPI server is running")
        print()

        # Test health endpoints
        test_health_endpoints()

    else:
        print("❌ FastAPI server is not running")
        print()
        print("To start the server:")
        print("   cd v1/backend")
        print("   python start_dev_server.py")
        print("   # or")
        print("   start_backend.bat")
        print()

    print("=" * 60)
    print("   Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
