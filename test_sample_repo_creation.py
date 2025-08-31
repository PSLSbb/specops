#!/usr/bin/env python3
"""Test sample repository creation."""

from tests.fixtures.sample_repositories import get_sample_repositories

def test_repo_creation():
    """Test that all sample repositories can be created without errors."""
    repositories = get_sample_repositories()
    
    for repo_name, repo in repositories.items():
        print(f"Testing {repo_name}...")
        try:
            with repo:
                workspace = repo.create()
                print(f"  ✓ Created at {workspace}")
                
                # Check that key files exist
                readme = workspace / 'README.md'
                if readme.exists():
                    print(f"  ✓ README.md exists")
                else:
                    print(f"  ✗ README.md missing")
                
                kiro_dir = workspace / '.kiro' / 'steering'
                if kiro_dir.exists():
                    print(f"  ✓ .kiro/steering directory exists")
                else:
                    print(f"  ✗ .kiro/steering directory missing")
                    
        except Exception as e:
            print(f"  ✗ Error creating {repo_name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_repo_creation()