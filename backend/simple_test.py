"""
Simple test script to verify basic functionality with minimal dependencies.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_python():
    """Test basic Python functionality."""
    print("Testing basic Python...")
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Python executable: {sys.executable}")
    return True

def test_fastapi_imports():
    """Test FastAPI imports."""
    print("\nTesting FastAPI imports...")
    
    try:
        import fastapi
        print(f"✅ FastAPI imported: version {fastapi.__version__}")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        from fastapi import FastAPI
        print(f"✅ FastAPI class imported")
    except Exception as e:
        print(f"❌ FastAPI class import failed: {e}")
        return False
    
    return True

def test_pydantic_imports():
    """Test Pydantic imports."""
    print("\nTesting Pydantic imports...")
    
    try:
        import pydantic
        print(f"✅ Pydantic imported: version {pydantic.__version__}")
    except Exception as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
        from pydantic import BaseModel
        print(f"✅ Pydantic BaseModel imported")
    except Exception as e:
        print(f"❌ Pydantic BaseModel import failed: {e}")
        return False
    
    return True

def test_uvicorn_imports():
    """Test Uvicorn imports."""
    print("\nTesting Uvicorn imports...")
    
    try:
        import uvicorn
        print(f"✅ Uvicorn imported: version {uvicorn.__version__}")
    except Exception as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    return True

def test_basic_app_creation():
    """Test basic FastAPI app creation."""
    print("\nTesting basic app creation...")
    
    try:
        from fastapi import FastAPI
        
        app = FastAPI(title="Test App")
        
        @app.get("/")
        async def root():
            return {"message": "Test working"}
        
        print(f"✅ Basic FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_environment_file():
    """Test environment file."""
    print("\nTesting environment file...")
    
    try:
        if os.path.exists('.env'):
            print(f"✅ .env file exists")
            
            with open('.env', 'r') as f:
                content = f.read()
                print(f"✅ .env file readable")
                
                if 'DEBUG' in content:
                    print(f"✅ DEBUG setting found")
                if 'ENVIRONMENT' in content:
                    print(f"✅ ENVIRONMENT setting found")
                if 'SECRET_KEY' in content:
                    print(f"✅ SECRET_KEY setting found")
                
                return True
        else:
            print(f"❌ .env file not found")
            return False
    except Exception as e:
        print(f"❌ Environment file test failed: {e}")
        return False

def test_project_structure():
    """Test project structure."""
    print("\nTesting project structure...")
    
    required_dirs = ['app', 'app/api', 'app/api/v1', 'app/core', 'app/models', 'app/services']
    required_files = ['test_server.py', 'pyproject.toml']
    
    all_exist = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")
            all_exist = False
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ File exists: {file}")
        else:
            print(f"❌ File missing: {file}")
            all_exist = False
    
    return all_exist

def test_imports():
    """Test basic imports from our app."""
    print("\nTesting app imports...")
    
    try:
        from app.core.config import settings
        print(f"✅ Config imported: {settings.PROJECT_NAME}")
        return True
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        # This is expected if dependencies are missing
        print("ℹ️  This is expected if full dependencies aren't installed")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Research Competitive Intelligence Platform")
    print("Basic Functionality Tests")
    print("=" * 60)
    
    tests = [
        ("Basic Python", test_basic_python),
        ("FastAPI Imports", test_fastapi_imports),
        ("Pydantic Imports", test_pydantic_imports),
        ("Uvicorn Imports", test_uvicorn_imports),
        ("Basic App Creation", test_basic_app_creation),
        ("Environment File", test_environment_file),
        ("Project Structure", test_project_structure),
        ("App Imports", test_imports),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed >= 6:  # At least 6 basic tests should pass
        print("\n🎉 Basic tests passed! Ready to run the server.")
        print("\nNext steps:")
        print("1. Install remaining dependencies: pip install pydantic-settings sqlalchemy aiohttp")
        print("2. Run the server: python test_server.py")
        print("3. Test endpoints: http://localhost:8000")
        return 0
    else:
        print("\n⚠️  Some basic tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())