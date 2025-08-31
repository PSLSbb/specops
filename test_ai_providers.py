#!/usr/bin/env python3
"""Test script for AI providers."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ai_providers():
    """Test different AI providers."""
    print("🧪 Testing AI Providers")
    print("=" * 40)
    
    try:
        from src.ai.providers import get_available_providers, get_provider
        
        # Get all available providers
        providers = get_available_providers()
        print(f"📋 Available providers: {len(providers)}")
        
        for name, info in providers.items():
            print(f"\n🔧 {info['name']}:")
            print(f"   Available: {'✅' if info['available'] else '❌'}")
            print(f"   Models: {len(info['models'])} available")
            print(f"   Description: {info['description']}")
            
            # Test mock provider
            if name == 'mock' or not info['available']:
                continue
                
            try:
                provider = get_provider(name)
                print(f"   Status: {'✅ Ready' if provider.is_available() else '❌ Not configured'}")
            except Exception as e:
                print(f"   Status: ❌ Error - {e}")
        
        # Test mock provider
        print(f"\n🎭 Testing Mock Provider:")
        mock_provider = get_provider("mock")
        response = mock_provider.generate("Generate a simple task", "You are a helpful assistant")
        print(f"   Response length: {len(response.content)} characters")
        print(f"   Provider: {response.provider}")
        print(f"   Model: {response.model}")
        print("   ✅ Mock provider working")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_engine():
    """Test AI processing engine with different providers."""
    print(f"\n🤖 Testing AI Processing Engine")
    print("=" * 40)
    
    try:
        from src.ai.processing_engine import AIProcessingEngine
        
        # Test with mock provider
        engine = AIProcessingEngine(provider="mock", model="mock-model")
        info = engine.get_provider_info()
        print(f"✅ Engine initialized with {info['provider']} provider")
        print(f"   Model: {info['model']}")
        print(f"   Available: {info['available']}")
        
        # Test switching providers
        print(f"\n🔄 Testing provider switching:")
        
        # Try switching to different providers
        providers_to_test = ["openai", "anthropic", "google", "groq"]
        
        for provider_name in providers_to_test:
            success = engine.switch_provider(provider_name)
            current_info = engine.get_provider_info()
            status = "✅" if success and current_info['available'] else "❌"
            print(f"   {provider_name}: {status} ({'configured' if current_info['available'] else 'not configured'})")
        
        # Switch back to mock for testing
        engine.switch_provider("mock")
        
        # Test content generation
        print(f"\n📝 Testing content generation:")
        from src.models import RepositoryAnalysis, Concept
        
        # Create a simple analysis
        analysis = RepositoryAnalysis(
            concepts=[Concept(name="Test Concept", description="A test concept", importance=5)]
        )
        
        # Test task generation
        tasks = engine.generate_task_suggestions(analysis)
        print(f"   Task suggestions: ✅ Generated {len(tasks)} tasks")
        
        # Test FAQ generation  
        faqs = engine.create_faq_pairs(analysis)
        print(f"   FAQ pairs: ✅ Generated {len(faqs)} FAQ pairs")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all AI provider tests."""
    print("SpecOps AI Provider Test Suite")
    print("=" * 50)
    
    success = True
    
    # Test providers
    if not test_ai_providers():
        success = False
    
    # Test AI engine
    if not test_ai_engine():
        success = False
    
    if success:
        print(f"\n🎉 All AI provider tests passed!")
        print(f"\n💡 To use real AI providers:")
        print(f"   export OPENAI_API_KEY='your-key-here'")
        print(f"   export ANTHROPIC_API_KEY='your-key-here'")
        print(f"   export GOOGLE_AI_API_KEY='your-key-here'")
        print(f"   # etc...")
        return 0
    else:
        print(f"\n💥 Some tests failed. Check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())