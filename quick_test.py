#!/usr/bin/env python3
"""Quick test script to verify SpecOps is working."""

import sys
from pathlib import Path

# Add project root to Python path so we can import src as a package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_functionality():
    """Test basic SpecOps functionality."""
    print("🧪 Testing SpecOps Basic Functionality")
    print("=" * 40)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from src.main import create_app, SpecOpsApp
        from src.analyzers.content_analyzer import ContentAnalyzer
        from src.config import SpecOpsConfig
        print("✅ Core imports successful")
        
        # Test app creation
        print("🚀 Testing app creation...")
        app = create_app()
        print("✅ App created successfully")
        
        # Test content analyzer
        print("🔍 Testing content analyzer...")
        analyzer = ContentAnalyzer()
        print("✅ Content analyzer created")
        
        # Test configuration
        print("⚙️  Testing configuration...")
        config = SpecOpsConfig.load_default()
        print("✅ Configuration loaded")
        
        # Test status
        print("📊 Testing app status...")
        status = app.get_status()
        print(f"✅ Status retrieved: {len(status)} components")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hello_world():
    """Test the hello world feature."""
    print("\n👋 Testing Hello World Feature")
    print("=" * 30)
    
    try:
        from features.hello_world import hello_world
        result = hello_world()
        print(f"✅ Hello World result: {result}")
        return True
    except Exception as e:
        print(f"❌ Hello World test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("SpecOps Quick Test Suite")
    print("=" * 50)
    
    success = True
    
    # Run basic functionality test
    if not test_basic_functionality():
        success = False
    
    # Run hello world test
    if not test_hello_world():
        success = False
    
    if success:
        print("\n🎊 All tests passed! SpecOps is ready to use.")
        print("\nNext steps:")
        print("1. Run: python run_specops.py --help")
        print("2. Try: python run_specops.py analyze")
        print("3. Or: python examples/analyze_online_repo.py")
        return 0
    else:
        print("\n💥 Some tests failed. Check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())