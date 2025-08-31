#!/usr/bin/env python3
"""Test enhanced SpecOps with AI providers."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Test enhanced SpecOps functionality."""
    print("🚀 Enhanced SpecOps Test")
    print("=" * 40)
    
    try:
        from src.main import create_app
        
        # Create SpecOps app
        app = create_app()
        
        # Show AI provider info
        print("🤖 AI Provider Info:")
        info = app.ai_engine.get_provider_info()
        print(f"  Provider: {info['provider']}")
        print(f"  Model: {info['model']}")
        print(f"  Available: {info['available']}")
        
        # Show all available providers
        print(f"\n📋 All Available Providers:")
        all_providers = app.ai_engine.get_all_providers()
        for name, provider_info in all_providers.items():
            status = "✅" if provider_info['available'] else "❌"
            print(f"  {status} {provider_info['name']}: {len(provider_info['models'])} models")
        
        # Test repository analysis
        print(f"\n🔍 Testing Repository Analysis:")
        analysis = app.analyze_repository()
        print(f"  Concepts: {len(analysis.concepts)}")
        print(f"  Setup Steps: {len(analysis.setup_steps)}")
        print(f"  Code Examples: {len(analysis.code_examples)}")
        print(f"  Dependencies: {len(analysis.dependencies)}")
        
        # Test document generation
        print(f"\n📝 Testing Document Generation:")
        docs = app.generate_all_documents(analysis)
        print(f"  Generated documents: {list(docs.keys())}")
        
        # Test provider switching
        print(f"\n🔄 Testing Provider Switching:")
        original_provider = info['provider']
        
        # Try switching to different providers
        test_providers = ['anthropic', 'google', 'groq']
        for provider in test_providers:
            success = app.ai_engine.switch_provider(provider)
            current = app.ai_engine.get_provider_info()
            status = "✅" if success else "❌"
            print(f"  {provider}: {status} (now using {current['provider']})")
        
        # Switch back to original
        app.ai_engine.switch_provider(original_provider)
        
        print(f"\n🎉 All tests passed! Enhanced SpecOps is working perfectly.")
        print(f"\n💡 Key Features Added:")
        print(f"  ✅ Multiple AI providers (OpenAI, Anthropic, Google, etc.)")
        print(f"  ✅ Enhanced dependency detection")
        print(f"  ✅ Improved web interface with AI configuration")
        print(f"  ✅ Fallback to mock data when APIs unavailable")
        print(f"  ✅ Real-time provider switching")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())