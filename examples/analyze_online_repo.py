#!/usr/bin/env python3
"""Example: Analyze an online repository with SpecOps."""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import create_app
from src.analyzers.online_content_analyzer import OnlineContentAnalyzer


def main():
    """Demonstrate online repository analysis."""
    
    # Example repository URLs
    example_repos = [
        "https://github.com/microsoft/vscode",
        "https://github.com/python/cpython",
        "https://github.com/facebook/react",
        "https://github.com/tensorflow/tensorflow"
    ]
    
    print("SpecOps Online Repository Analysis Example")
    print("=" * 50)
    
    # Get repository URL from user or use example
    repo_url = input(f"Enter repository URL (or press Enter for example): ").strip()
    if not repo_url:
        repo_url = example_repos[0]
        print(f"Using example repository: {repo_url}")
    
    # Validate URL format
    if not repo_url.startswith(('http://', 'https://')):
        print(f"❌ Invalid URL format: {repo_url}")
        return 1
    
    # Check if URL is supported
    if not OnlineContentAnalyzer.is_supported_url(repo_url):
        print(f"❌ Unsupported repository URL: {repo_url}")
        return 1
    
    # Check dependencies
    missing_deps = OnlineContentAnalyzer.get_required_dependencies()
    if missing_deps:
        print("\n⚠️  Missing dependencies for online analysis:")
        for dep, install_cmd in missing_deps.items():
            print(f"   {dep}: {install_cmd}")
        
        proceed = input("\nProceed anyway? (y/N): ").strip().lower()
        if proceed != 'y':
            return 1
    
    try:
        print(f"\n🔍 Analyzing repository: {repo_url}")
        print("This may take a moment...")
        
        # Create SpecOps app
        app = create_app()
        
        # Analyze online repository
        analysis = app.analyze_repository(repo_url=repo_url)
        
        # Display results
        print("\n✅ Analysis Complete!")
        print(f"📊 Results:")
        print(f"   • {len(analysis.concepts)} concepts found")
        print(f"   • {len(analysis.setup_steps)} setup steps found")
        print(f"   • {len(analysis.code_examples)} code examples found")
        print(f"   • {len(analysis.dependencies)} dependencies found")
        
        # Show top concepts
        if analysis.concepts:
            print(f"\n🎯 Top Concepts:")
            for i, concept in enumerate(analysis.concepts[:5], 1):
                print(f"   {i}. {concept.name} (importance: {concept.importance})")
                if concept.description:
                    desc = concept.description[:100] + "..." if len(concept.description) > 100 else concept.description
                    print(f"      {desc}")
        
        # Show setup steps
        if analysis.setup_steps:
            print(f"\n🛠️  Setup Steps:")
            for i, step in enumerate(analysis.setup_steps[:3], 1):
                print(f"   {i}. {step.title}")
        
        # Show dependencies
        if analysis.dependencies:
            print(f"\n📦 Dependencies:")
            for dep in analysis.dependencies[:5]:
                version_info = f" ({dep.version})" if dep.version else ""
                print(f"   • {dep.name}{version_info}")
        
        # Offer to generate documents
        generate = input(f"\n📝 Generate onboarding documents? (y/N): ").strip().lower()
        if generate == 'y':
            print("🚀 Generating documents...")
            
            # Generate all documents
            generated_docs = app.generate_all_documents(analysis)
            
            print(f"✅ Generated {len(generated_docs)} documents:")
            for doc_type, path in generated_docs.items():
                print(f"   • {doc_type}: {path}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error analyzing repository: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())