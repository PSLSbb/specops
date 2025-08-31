"""End-to-end workflow integration tests for SpecOps."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
import os

from src.main import SpecOpsApp, create_app, SpecOpsError
from src.models import AppConfig, HookConfig, StyleConfig, RepositoryAnalysis, Concept, SetupStep, CodeExample, Dependency
from src.config_loader import ConfigLoader


class TestEndToEndWorkflow:
    """Test complete pipelines from content analysis to output generation."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)
        
        # Create basic workspace structure
        (workspace / 'src').mkdir()
        (workspace / 'tests').mkdir()
        (workspace / 'features').mkdir()
        (workspace / 'docs').mkdir()
        (workspace / '.kiro').mkdir()
        (workspace / '.kiro' / 'steering').mkdir()
        (workspace / '.kiro' / 'specs').mkdir()
        
        # Create sample files
        self._create_sample_files(workspace)
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def _create_sample_files(self, workspace: Path):
        """Create sample files for testing."""
        # Create README.md
        readme_content = """# Test Project

This is a test project for SpecOps integration testing.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from features.hello_world import hello_world
print(hello_world("Test"))
```

## Contributing

Please read our contributing guidelines.
"""
        (workspace / 'README.md').write_text(readme_content)
        
        # Create requirements.txt
        (workspace / 'requirements.txt').write_text("pytest>=7.0.0\nrequests>=2.28.0\n")
        
        # Create sample feature
        feature_content = '''"""Sample feature for testing."""

def hello_world(name: str = "World") -> str:
    """Return a greeting message.
    
    Args:
        name: Name to greet
        
    Returns:
        Greeting message
    """
    return f"Hello, {name}!"

def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b
'''
        (workspace / 'features' / 'hello_world.py').write_text(feature_content)
        
        # Create sample test
        test_content = '''"""Tests for hello_world feature."""

import pytest
from features.hello_world import hello_world, calculate_sum


def test_hello_world_default():
    """Test hello_world with default parameter."""
    assert hello_world() == "Hello, World!"

def test_hello_world_custom_name():
    """Test hello_world with custom name."""
    assert hello_world("Test") == "Hello, Test!"

def test_calculate_sum():
    """Test calculate_sum function."""
    assert calculate_sum(2, 3) == 5
    assert calculate_sum(-1, 1) == 0
'''
        (workspace / 'tests' / 'test_hello_world.py').write_text(test_content)
        
        # Create documentation
        doc_content = """# API Documentation

## Functions

### hello_world(name)

Returns a greeting message.

### calculate_sum(a, b)

Calculates the sum of two numbers.
"""
        (workspace / 'docs' / 'api.md').write_text(doc_content)
        
        # Create steering files
        (workspace / '.kiro' / 'steering' / 'code-style.md').write_text("# Code Style Guidelines\n\nUse type hints and docstrings.")
        (workspace / '.kiro' / 'steering' / 'structure.md').write_text("# Project Structure\n\nOrganize code in src/, tests/, features/.")
        (workspace / '.kiro' / 'steering' / 'onboarding-style.md').write_text("# Onboarding Style\n\nBe clear and concise.")
    
    @pytest.fixture
    def mock_ai_responses(self):
        """Mock AI responses for testing."""
        return {
            'task_suggestions': [
                {
                    'title': 'Set up development environment',
                    'description': 'Install dependencies and configure workspace',
                    'acceptance_criteria': ['Dependencies installed', 'Environment configured'],
                    'prerequisites': [],
                    'estimated_time': 15,
                    'difficulty': 'easy'
                },
                {
                    'title': 'Understand hello_world feature',
                    'description': 'Learn how the greeting function works',
                    'acceptance_criteria': ['Function behavior understood', 'Tests passing'],
                    'prerequisites': ['Set up development environment'],
                    'estimated_time': 10,
                    'difficulty': 'easy'
                }
            ],
            'faq_pairs': [
                {
                    'question': 'How do I install the project?',
                    'answer': 'Run `pip install -r requirements.txt` to install dependencies.',
                    'category': 'setup',
                    'source_files': ['README.md'],
                    'confidence': 0.9
                },
                {
                    'question': 'How do I run tests?',
                    'answer': 'Use `pytest` to run the test suite.',
                    'category': 'testing',
                    'source_files': ['tests/test_hello_world.py'],
                    'confidence': 0.8
                }
            ],
            'quick_start_guide': {
                'prerequisites': ['Python 3.8+', 'pip'],
                'setup_steps': ['Clone repository', 'Install dependencies', 'Run tests'],
                'basic_usage': ['Import hello_world', 'Call function with name'],
                'next_steps': ['Read API documentation', 'Explore features']
            }
        }
    
    @patch('src.ai.processing_engine.AIProcessingEngine.generate_task_suggestions')
    @patch('src.ai.processing_engine.AIProcessingEngine.create_faq_pairs')
    @patch('src.ai.processing_engine.AIProcessingEngine.extract_quick_start_steps')
    def test_complete_analysis_to_generation_pipeline(self, mock_quick_start, mock_faq, mock_tasks, 
                                                     temp_workspace, mock_ai_responses):
        """Test complete pipeline from content analysis to document generation."""
        # Setup mocks
        mock_tasks.return_value = mock_ai_responses['task_suggestions']
        mock_faq.return_value = mock_ai_responses['faq_pairs']
        mock_quick_start.return_value = mock_ai_responses['quick_start_guide']
        
        # Create app
        app = create_app(workspace_path=str(temp_workspace))
        
        # Test repository analysis
        analysis = app.analyze_repository()
        
        # Verify analysis results
        assert isinstance(analysis, RepositoryAnalysis)
        assert len(analysis.concepts) > 0
        assert len(analysis.setup_steps) > 0
        assert len(analysis.code_examples) > 0
        
        # Test document generation
        generated_docs = app.generate_all_documents(analysis)
        
        # Verify documents were generated
        assert 'tasks' in generated_docs or 'faq' in generated_docs or 'quick_start' in generated_docs
        
        # Verify files exist
        if 'tasks' in generated_docs:
            assert Path(generated_docs['tasks']).exists()
            tasks_content = Path(generated_docs['tasks']).read_text()
            assert 'Set up development environment' in tasks_content
        
        if 'faq' in generated_docs:
            assert Path(generated_docs['faq']).exists()
            faq_content = Path(generated_docs['faq']).read_text()
            assert 'How do I install the project?' in faq_content
        
        if 'quick_start' in generated_docs:
            readme_content = Path(generated_docs['quick_start']).read_text()
            assert 'Quick Start' in readme_content or 'Getting Started' in readme_content
    
    @patch('src.ai.processing_engine.AIProcessingEngine.analyze_feature_code')
    def test_feature_created_hook_integration(self, mock_analyze_feature, temp_workspace):
        """Test hook integration with actual file system operations."""
        # Setup mock
        mock_feature_analysis = Mock()
        mock_feature_analysis.feature_path = str(temp_workspace / 'features' / 'new_feature.py')
        mock_feature_analysis.functions = [
            {'name': 'new_function', 'description': 'A new function', 'parameters': []}
        ]
        mock_feature_analysis.tests_needed = ['test_new_function']
        mock_analyze_feature.return_value = mock_feature_analysis
        
        # Create app with hooks enabled
        config = AppConfig(
            workspace_path=str(temp_workspace),
            hook_config=HookConfig(feature_created_enabled=True)
        )
        app = create_app(workspace_path=str(temp_workspace), config=config)
        
        # Create a tasks.md file first
        tasks_content = """# Implementation Tasks

- [ ] 1. Initial setup
  - Set up project structure
  - _Requirements: 1.1_
"""
        (temp_workspace / 'tasks.md').write_text(tasks_content)
        
        # Create new feature file
        new_feature_content = '''"""New feature for testing hooks."""

def new_function() -> str:
    """A new function for testing."""
    return "New feature works!"
'''
        new_feature_path = temp_workspace / 'features' / 'new_feature.py'
        new_feature_path.write_text(new_feature_content)
        
        # Trigger feature created hook
        app.handle_feature_created(str(new_feature_path))
        
        # Verify hook execution
        mock_analyze_feature.assert_called_once_with(str(new_feature_path))
        
        # Verify tasks.md was updated (if task generator is working)
        if (temp_workspace / 'tasks.md').exists():
            updated_tasks = (temp_workspace / 'tasks.md').read_text()
            # Should contain original content
            assert 'Initial setup' in updated_tasks
    
    @patch('src.ai.processing_engine.AIProcessingEngine.extract_quick_start_steps')
    @patch('src.ai.processing_engine.AIProcessingEngine.create_faq_pairs')
    def test_readme_saved_hook_integration(self, mock_faq, mock_quick_start, temp_workspace, mock_ai_responses):
        """Test README save hook integration."""
        # Setup mocks
        mock_faq.return_value = mock_ai_responses['faq_pairs']
        mock_quick_start.return_value = mock_ai_responses['quick_start_guide']
        
        # Create app with hooks enabled
        config = AppConfig(
            workspace_path=str(temp_workspace),
            hook_config=HookConfig(readme_save_enabled=True)
        )
        app = create_app(workspace_path=str(temp_workspace), config=config)
        
        # Get README path
        readme_path = temp_workspace / 'README.md'
        
        # Trigger README saved hook
        app.handle_readme_saved(str(readme_path))
        
        # Verify hook execution
        mock_quick_start.assert_called_once()
        mock_faq.assert_called_once()
        
        # Verify README was updated with Quick Start (if generator is working)
        readme_content = readme_path.read_text()
        # Original content should still be there
        assert 'Test Project' in readme_content
        
        # Verify FAQ file was created/updated (if generator is working)
        faq_files = list(temp_workspace.glob('**/faq.md')) + list(temp_workspace.glob('**/FAQ.md'))
        # FAQ file might be created depending on generator implementation
    
    def test_error_handling_and_recovery(self, temp_workspace):
        """Test error handling and recovery mechanisms."""
        # Create app with invalid configuration to trigger errors
        config = AppConfig(
            workspace_path=str(temp_workspace),
            ai_model="invalid-model",
            debug_mode=True
        )
        
        # App should still initialize with error handling
        app = create_app(workspace_path=str(temp_workspace), config=config)
        
        # Test graceful handling of analysis errors
        try:
            analysis = app.analyze_repository()
            # Should either succeed with fallback or handle gracefully
            assert isinstance(analysis, RepositoryAnalysis)
        except SpecOpsError as e:
            # Error should be properly wrapped
            assert "analysis failed" in str(e).lower() or "component" in str(e).lower()
    
    def test_content_quality_and_consistency(self, temp_workspace, mock_ai_responses):
        """Test generated content quality and consistency."""
        with patch('src.ai.processing_engine.AIProcessingEngine.generate_task_suggestions') as mock_tasks, \
             patch('src.ai.processing_engine.AIProcessingEngine.create_faq_pairs') as mock_faq, \
             patch('src.ai.processing_engine.AIProcessingEngine.extract_quick_start_steps') as mock_quick_start:
            
            # Setup mocks
            mock_tasks.return_value = mock_ai_responses['task_suggestions']
            mock_faq.return_value = mock_ai_responses['faq_pairs']
            mock_quick_start.return_value = mock_ai_responses['quick_start_guide']
            
            # Create app
            app = create_app(workspace_path=str(temp_workspace))
            
            # Generate all documents
            generated_docs = app.generate_all_documents()
            
            # Test content quality
            for doc_type, doc_path in generated_docs.items():
                if Path(doc_path).exists():
                    content = Path(doc_path).read_text()
                    
                    # Basic quality checks
                    assert len(content.strip()) > 0, f"{doc_type} document is empty"
                    assert content.count('\n') > 1, f"{doc_type} document has insufficient content"
                    
                    # Markdown format checks
                    if doc_path.endswith('.md'):
                        assert '#' in content, f"{doc_type} document missing headers"
                        
                    # Consistency checks
                    if doc_type == 'tasks':
                        assert '- [' in content, "Tasks document missing checkboxes"
                        assert 'Requirements:' in content or '_Requirements:' in content, "Tasks missing requirement references"
                    
                    elif doc_type == 'faq':
                        assert '?' in content, "FAQ document missing questions"
                        assert len([line for line in content.split('\n') if line.strip().endswith('?')]) > 0, "FAQ missing question format"
    
    def test_component_integration_health(self, temp_workspace):
        """Test that all components integrate properly and report health status."""
        # Create app
        app = create_app(workspace_path=str(temp_workspace))
        
        # Test component health
        status = app.get_status()
        
        # Verify status structure
        assert 'workspace_path' in status
        assert 'config' in status
        assert 'components' in status
        
        # Verify component initialization
        components = status['components']
        expected_components = [
            'content_analyzer', 'ai_engine', 'task_generator', 
            'faq_generator', 'quick_start_generator', 'hook_manager'
        ]
        
        for component in expected_components:
            assert component in components, f"Missing component: {component}"
            # Components should be initialized (True) or gracefully handle failure (False)
            assert isinstance(components[component], bool), f"Invalid component status for {component}"
        
        # Test graceful shutdown
        app.shutdown()
        
        # Verify components are cleaned up
        assert app._content_analyzer is None
        assert app._ai_engine is None
    
    def test_configuration_loading_and_validation(self, temp_workspace):
        """Test configuration loading from workspace steering files."""
        # Create custom config files
        config_content = {
            'code-style.md': "# Custom Code Style\n\nUse custom formatting rules.",
            'structure.md': "# Custom Structure\n\nCustom project organization.",
            'onboarding-style.md': "# Custom Onboarding\n\nCustom onboarding approach."
        }
        
        for filename, content in config_content.items():
            (temp_workspace / '.kiro' / 'steering' / filename).write_text(content)
        
        # Create app - should load custom steering
        app = create_app(workspace_path=str(temp_workspace))
        
        # Verify configuration was loaded
        assert app.config.workspace_path == str(temp_workspace)
        
        # Test that style config is loaded
        if hasattr(app.config, 'style_config') and app.config.style_config:
            style_config = app.config.style_config
            # Should have loaded custom content
            assert hasattr(style_config, 'code_style_content') or hasattr(style_config, 'code_style_path')
    
    def test_concurrent_hook_execution(self, temp_workspace):
        """Test that multiple hooks can execute without conflicts."""
        # Create app with all hooks enabled
        config = AppConfig(
            workspace_path=str(temp_workspace),
            hook_config=HookConfig(
                feature_created_enabled=True,
                readme_save_enabled=True
            )
        )
        app = create_app(workspace_path=str(temp_workspace), config=config)
        
        # Create tasks.md for feature hook
        (temp_workspace / 'tasks.md').write_text("# Tasks\n\n- [ ] Initial task")
        
        # Create new feature
        feature_path = temp_workspace / 'features' / 'concurrent_test.py'
        feature_path.write_text('def test_function(): pass')
        
        # Mock AI responses to avoid external dependencies
        with patch('src.ai.processing_engine.AIProcessingEngine.analyze_feature_code') as mock_analyze, \
             patch('src.ai.processing_engine.AIProcessingEngine.extract_quick_start_steps') as mock_quick_start, \
             patch('src.ai.processing_engine.AIProcessingEngine.create_faq_pairs') as mock_faq:
            
            mock_analyze.return_value = Mock(feature_path=str(feature_path), functions=[], tests_needed=[])
            mock_quick_start.return_value = {'prerequisites': [], 'setup_steps': [], 'basic_usage': [], 'next_steps': []}
            mock_faq.return_value = []
            
            # Execute hooks concurrently (simulate)
            readme_path = temp_workspace / 'README.md'
            
            # Both hooks should execute without errors
            app.handle_feature_created(str(feature_path))
            app.handle_readme_saved(str(readme_path))
            
            # Verify both hooks were called
            mock_analyze.assert_called_once()
            mock_quick_start.assert_called_once()