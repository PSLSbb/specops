"""Validation tests for sample repository testing infrastructure."""

import pytest
from pathlib import Path
from tests.fixtures.sample_repositories import get_sample_repositories


class TestSampleRepositoryValidation:
    """Validate that sample repository testing infrastructure works correctly."""
    
    def test_all_sample_repositories_can_be_created(self):
        """Test that all sample repositories can be created without errors."""
        repositories = get_sample_repositories()
        
        for repo_name, repo in repositories.items():
            with repo:
                workspace = repo.create()
                
                # Verify workspace exists
                assert workspace.exists(), f"Workspace not created for {repo_name}"
                
                # Verify README exists
                readme = workspace / 'README.md'
                assert readme.exists(), f"README.md missing in {repo_name}"
                
                # Verify .kiro/steering directory exists
                steering_dir = workspace / '.kiro' / 'steering'
                assert steering_dir.exists(), f".kiro/steering missing in {repo_name}"
                
                # Verify at least one steering file exists
                steering_files = list(steering_dir.glob('*.md'))
                assert len(steering_files) > 0, f"No steering files in {repo_name}"
    
    def test_sample_repositories_have_different_structures(self):
        """Test that different repository types have distinct structures."""
        repositories = get_sample_repositories()
        
        structures = {}
        for repo_name, repo in repositories.items():
            with repo:
                workspace = repo.create()
                
                # Get directory structure
                dirs = [p.name for p in workspace.iterdir() if p.is_dir()]
                structures[repo_name] = set(dirs)
        
        # Verify each repository type has some unique directories
        python_lib_dirs = structures['python_library']
        web_app_dirs = structures['web_application']
        microservice_dirs = structures['microservice']
        
        # Python library should have src, tests, docs, examples
        assert 'src' in python_lib_dirs
        assert 'tests' in python_lib_dirs
        assert 'docs' in python_lib_dirs
        assert 'examples' in python_lib_dirs
        
        # Web application should have src, tests, config, static, templates
        assert 'src' in web_app_dirs
        assert 'tests' in web_app_dirs
        assert 'config' in web_app_dirs
        
        # Microservice should have src, tests, docker, k8s
        assert 'src' in microservice_dirs
        assert 'tests' in microservice_dirs
        assert 'docker' in microservice_dirs
        assert 'k8s' in microservice_dirs
    
    def test_sample_repositories_have_appropriate_content(self):
        """Test that sample repositories contain appropriate content for their type."""
        repositories = get_sample_repositories()
        
        for repo_name, repo in repositories.items():
            with repo:
                workspace = repo.create()
                readme_content = (workspace / 'README.md').read_text(encoding='utf-8').lower()
                
                if repo_name == 'python_library':
                    assert 'library' in readme_content or 'package' in readme_content
                    assert 'pip install' in readme_content
                    
                elif repo_name == 'web_application':
                    assert 'api' in readme_content or 'web' in readme_content
                    assert 'fastapi' in readme_content or 'server' in readme_content
                    
                elif repo_name == 'microservice':
                    assert 'microservice' in readme_content or 'service' in readme_content
                    assert 'docker' in readme_content
    
    def test_sample_repositories_have_valid_steering_files(self):
        """Test that sample repositories have valid steering files."""
        repositories = get_sample_repositories()
        
        for repo_name, repo in repositories.items():
            with repo:
                workspace = repo.create()
                steering_dir = workspace / '.kiro' / 'steering'
                
                # Check for expected steering files
                code_style = steering_dir / 'code-style.md'
                if code_style.exists():
                    content = code_style.read_text(encoding='utf-8')
                    assert len(content.strip()) > 0, f"Empty code-style.md in {repo_name}"
                    assert 'style' in content.lower() or 'code' in content.lower()
    
    def test_sample_repositories_cleanup_properly(self):
        """Test that sample repositories clean up their temporary directories."""
        repositories = get_sample_repositories()
        
        workspaces = []
        for repo_name, repo in repositories.items():
            workspace = repo.create()
            workspaces.append(workspace)
            assert workspace.exists(), f"Workspace not created for {repo_name}"
            
            # Clean up
            repo.cleanup()
        
        # Verify all workspaces are cleaned up
        for workspace in workspaces:
            assert not workspace.exists(), f"Workspace not cleaned up: {workspace}"
    
    def test_sample_repositories_context_manager(self):
        """Test that sample repositories work correctly as context managers."""
        repositories = get_sample_repositories()
        
        workspaces = []
        for repo_name, repo in repositories.items():
            with repo as workspace:
                workspaces.append(workspace)
                assert workspace.exists(), f"Workspace not created for {repo_name}"
                
                # Verify basic structure
                assert (workspace / 'README.md').exists()
                assert (workspace / '.kiro').exists()
        
        # After context manager exits, workspaces should be cleaned up
        for workspace in workspaces:
            assert not workspace.exists(), f"Workspace not cleaned up: {workspace}"
    
    def test_sample_repositories_have_different_file_counts(self):
        """Test that different repository types have different numbers of files."""
        repositories = get_sample_repositories()
        
        file_counts = {}
        for repo_name, repo in repositories.items():
            with repo:
                workspace = repo.create()
                
                # Count all files recursively
                file_count = len(list(workspace.rglob('*')))
                file_counts[repo_name] = file_count
        
        # Each repository type should have a different number of files
        counts = list(file_counts.values())
        assert len(set(counts)) == len(counts), f"Repository types have same file counts: {file_counts}"
        
        # All should have a reasonable number of files
        for repo_name, count in file_counts.items():
            assert count > 10, f"{repo_name} has too few files: {count}"
            assert count < 100, f"{repo_name} has too many files: {count}"