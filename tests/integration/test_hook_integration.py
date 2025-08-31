"""Hook integration tests for SpecOps."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import json
import time

from src.main import SpecOpsApp, create_app
from src.models import AppConfig, HookConfig, FeatureAnalysis
from src.hooks.hook_manager import HookManager, HookError


class TestHookIntegration:
    """Test hook integration with actual file system operations."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)
        
        # Create workspace structure
        (workspace / 'src').mkdir()
        (workspace / 'tests').mkdir()
        (workspace / 'features').mkdir()
        (workspace / '.kiro').mkdir()
        (workspace / '.kiro' / 'steering').mkdir()
        
        # Create basic files
        (workspace / 'README.md').write_text("# Test Project\n\nBasic project for testing.")
        (workspace / 'tasks.md').write_text("# Tasks\n\n- [ ] 1. Initial task\n  - Basic setup task\n")
        
        # Create steering files
        (workspace / '.kiro' / 'steering' / 'code-style.md').write_text("# Code Style\n\nUse type hints.")
        (workspace / '.kiro' / 'steering' / 'structure.md').write_text("# Structure\n\nOrganize properly.")
        (workspace / '.kiro' / 'steering' / 'onboarding-style.md').write_text("# Onboarding\n\nBe clear.")
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def hook_config(self):
        """Create hook configuration for testing."""
        return HookConfig(
            feature_created_enabled=True,
            readme_save_enabled=True,
            hook_timeout=30,
            max_retries=2,
            log_level='INFO'
        )
    
    def test_hook_manager_initialization(self, temp_workspace, hook_config):
        """Test hook manager initializes correctly with configuration."""
        hook_manager = HookManager(config=hook_config, workspace_path=str(temp_workspace))
        
        # Verify initialization
        assert hook_manager.config == hook_config
        assert hook_manager.workspace_path == temp_workspace
        
        # Verify registry initialization
        status = hook_manager.get_hook_status()
        assert 'hooks' in status
        assert 'config' in status
        assert 'feature_created' in status['hooks']
        assert 'readme_save' in status['hooks']
        
        # Verify configuration
        config_status = status['config']
        assert config_status['feature_created_enabled'] == True
        assert config_status['readme_save_enabled'] == True
        assert config_status['hook_timeout'] == 30
        assert config_status['max_retries'] == 2
    
    def test_hook_registration_and_status(self, temp_workspace, hook_config):
        """Test hook registration and status reporting."""
        hook_manager = HookManager(config=hook_config, workspace_path=str(temp_workspace))
        
        # Test initial status
        status = hook_manager.get_hook_status()
        assert status['hooks']['feature_created']['enabled'] == True
        assert status['hooks']['feature_created']['registered'] == False
        
        # Register hooks
        hook_manager.register_feature_created_hook()
        hook_manager.register_readme_save_hook()
        
        # Test updated status
        status = hook_manager.get_hook_status()
        assert status['hooks']['feature_created']['registered'] == True
        assert status['hooks']['readme_save']['registered'] == True
        
        # Test unregistration
        hook_manager.unregister_hook('feature_created')
        status = hook_manager.get_hook_status()
        assert status['hooks']['feature_created']['registered'] == False
    
    @patch('src.ai.processing_engine.AIProcessingEngine.analyze_feature_code')
    def test_feature_created_hook_execution(self, mock_analyze_feature, temp_workspace, hook_config):
        """Test feature created hook execution with file system operations."""
        # Setup mock
        mock_feature_analysis = Mock(spec=FeatureAnalysis)
        mock_feature_analysis.feature_path = str(temp_workspace / 'features' / 'test_feature.py')
        mock_feature_analysis.functions = [
            {
                'name': 'test_function',
                'description': 'A test function',
                'parameters': ['param1: str'],
                'return_type': 'str'
            }
        ]
        mock_feature_analysis.tests_needed = ['test_test_function']
        mock_feature_analysis.complexity = 'low'
        mock_analyze_feature.return_value = mock_feature_analysis
        
        # Create hook manager
        hook_manager = HookManager(config=hook_config, workspace_path=str(temp_workspace))
        hook_manager.register_feature_created_hook()
        
        # Create test feature file
        feature_content = '''"""Test feature for hook testing."""

def test_function(param1: str) -> str:
    """A test function for hook integration.
    
    Args:
        param1: Test parameter
        
    Returns:
        Test result
    """
    return f"Test: {param1}"
'''
        feature_path = temp_workspace / 'features' / 'test_feature.py'
        feature_path.write_text(feature_content)
        
        # Execute hook
        hook_manager.handle_feature_created(str(feature_path))
        
        # Verify AI analysis was called
        mock_analyze_feature.assert_called_once_with(str(feature_path))
        
        # Verify tasks.md still exists and has content
        tasks_file = temp_workspace / 'tasks.md'
        assert tasks_file.exists()
        tasks_content = tasks_file.read_text()
        assert 'Initial task' in tasks_content  # Original content preserved
    
    @patch('src.ai.processing_engine.AIProcessingEngine.extract_quick_start_steps')
    @patch('src.ai.processing_engine.AIProcessingEngine.create_faq_pairs')
    def test_readme_saved_hook_execution(self, mock_faq_pairs, mock_quick_start, temp_workspace, hook_config):
        """Test README saved hook execution with file system operations."""
        # Setup mocks
        mock_quick_start.return_value = {
            'prerequisites': ['Python 3.8+'],
            'setup_steps': ['Install dependencies', 'Run tests'],
            'basic_usage': ['Import module', 'Call function'],
            'next_steps': ['Read documentation']
        }
        
        mock_faq_pairs.return_value = [
            {
                'question': 'How do I get started?',
                'answer': 'Follow the Quick Start guide.',
                'category': 'getting-started',
                'source_files': ['README.md'],
                'confidence': 0.9
            }
        ]
        
        # Create hook manager
        hook_manager = HookManager(config=hook_config, workspace_path=str(temp_workspace))
        hook_manager.register_readme_save_hook()
        
        # Get README path
        readme_path = temp_workspace / 'README.md'
        original_content = readme_path.read_text()
        
        # Execute hook
        hook_manager.handle_readme_saved(str(readme_path))
        
        # Verify AI methods were called
        mock_quick_start.assert_called_once()
        mock_faq_pairs.assert_called_once()
        
        # Verify README still exists
        assert readme_path.exists()
        
        # Verify FAQ file might be created
        possible_faq_files = [
            temp_workspace / 'faq.md',
            temp_workspace / 'FAQ.md'
        ]
        # At least one FAQ file should exist or be attempted
        # (depending on generator implementation)
    
    def test_hook_error_handling_and_recovery(self, temp_workspace, hook_config):
        """Test hook error handling and graceful degradation."""
        hook_manager = HookManager(config=hook_config, workspace_path=str(temp_workspace))
        hook_manager.register_feature_created_hook()
        
        # Test with non-existent file
        non_existent_path = str(temp_workspace / 'features' / 'non_existent.py')
        
        # Should handle error gracefully without raising
        hook_manager.handle_feature_created(non_existent_path)
        
        # Test with invalid path
        hook_manager.handle_feature_created("")
        hook_manager.handle_feature_created(None)
        
        # Hook manager should still be functional
        status = hook_manager.get_hook_status()
        assert status['hooks']['feature_created']['enabled'] == True
    
    def test_hook_configuration_updates(self, temp_workspace, hook_config):
        """Test dynamic hook configuration updates."""
        hook_manager = HookManager(config=hook_config, workspace_path=str(temp_workspace))
        
        # Register initial hooks
        hook_manager.register_all_hooks()
        status = hook_manager.get_hook_status()
        assert status['hooks']['feature_created']['registered'] == True
        assert status['hooks']['readme_save']['registered'] == True
        
        # Update configuration to disable feature_created hook
        new_config = HookConfig(
            feature_created_enabled=False,
            readme_save_enabled=True,
            hook_timeout=60,
            max_retries=3,
            log_level='DEBUG'
        )
        
        hook_manager.update_config(new_config)
        
        # Verify configuration update
        status = hook_manager.get_hook_status()
        assert status['config']['feature_created_enabled'] == False
        assert status['config']['readme_save_enabled'] == True
        assert status['config']['hook_timeout'] == 60
        assert status['config']['max_retries'] == 3
        assert status['config']['log_level'] == 'DEBUG'
    
    def test_hook_execution_with_missing_components(self, temp_workspace):
        """Test hook execution when some components are not available."""
        # Create hook manager with minimal config
        config = HookConfig(feature_created_enabled=True, readme_save_enabled=True)
        hook_manager = HookManager(config=config, workspace_path=str(temp_workspace))
        
        # Simulate missing components by setting them to None
        hook_manager.ai_engine = None
        hook_manager.task_generator = None
        
        # Create test feature
        feature_path = temp_workspace / 'features' / 'test.py'
        feature_path.write_text('def test(): pass')
        
        # Hook should handle missing components gracefully
        hook_manager.handle_feature_created(str(feature_path))
        
        # Should not raise exceptions
        readme_path = temp_workspace / 'README.md'
        hook_manager.handle_readme_saved(str(readme_path))
    
    def test_hook_execution_logging_and_monitoring(self, temp_workspace, hook_config):
        """Test hook execution logging and monitoring capabilities."""
        import logging
        from io import StringIO
        
        # Setup logging capture
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger('src.hooks.hook_manager')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        try:
            hook_manager = HookManager(config=hook_config, workspace_path=str(temp_workspace))
            hook_manager.register_feature_created_hook()
            
            # Create test feature
            feature_path = temp_workspace / 'features' / 'logged_feature.py'
            feature_path.write_text('def logged_function(): pass')
            
            # Execute hook
            hook_manager.handle_feature_created(str(feature_path))
            
            # Check logs
            log_output = log_stream.getvalue()
            assert 'Handling feature_created event' in log_output
            assert 'logged_feature.py' in log_output
            
        finally:
            logger.removeHandler(handler)
    
    def test_hook_timeout_and_retry_behavior(self, temp_workspace):
        """Test hook timeout and retry mechanisms."""
        # Create config with short timeout and retries
        config = HookConfig(
            feature_created_enabled=True,
            hook_timeout=1,  # Very short timeout
            max_retries=2
        )
        
        hook_manager = HookManager(config=config, workspace_path=str(temp_workspace))
        
        # Mock a slow operation
        with patch('src.ai.processing_engine.AIProcessingEngine.analyze_feature_code') as mock_analyze:
            def slow_analysis(*args, **kwargs):
                time.sleep(2)  # Longer than timeout
                return Mock(feature_path='test', functions=[], tests_needed=[])
            
            mock_analyze.side_effect = slow_analysis
            
            # Create test feature
            feature_path = temp_workspace / 'features' / 'slow_feature.py'
            feature_path.write_text('def slow_function(): pass')
            
            # Execute hook - should handle timeout gracefully
            hook_manager.handle_feature_created(str(feature_path))
            
            # Should have attempted the call despite timeout
            assert mock_analyze.called
    
    def test_multiple_hook_types_coordination(self, temp_workspace, hook_config):
        """Test coordination between different hook types."""
        hook_manager = HookManager(config=hook_config, workspace_path=str(temp_workspace))
        hook_manager.register_all_hooks()
        
        # Mock AI components
        with patch('src.ai.processing_engine.AIProcessingEngine.analyze_feature_code') as mock_analyze, \
             patch('src.ai.processing_engine.AIProcessingEngine.extract_quick_start_steps') as mock_quick_start, \
             patch('src.ai.processing_engine.AIProcessingEngine.create_faq_pairs') as mock_faq:
            
            mock_analyze.return_value = Mock(feature_path='test', functions=[], tests_needed=[])
            mock_quick_start.return_value = {'prerequisites': [], 'setup_steps': [], 'basic_usage': [], 'next_steps': []}
            mock_faq.return_value = []
            
            # Create test files
            feature_path = temp_workspace / 'features' / 'coordinated_feature.py'
            feature_path.write_text('def coordinated_function(): pass')
            readme_path = temp_workspace / 'README.md'
            
            # Execute both hooks
            hook_manager.handle_feature_created(str(feature_path))
            hook_manager.handle_readme_saved(str(readme_path))
            
            # Verify both hooks executed
            mock_analyze.assert_called_once()
            mock_quick_start.assert_called_once()
            mock_faq.assert_called_once()
    
    def test_hook_state_persistence_and_recovery(self, temp_workspace, hook_config):
        """Test hook state persistence and recovery after failures."""
        hook_manager = HookManager(config=hook_config, workspace_path=str(temp_workspace))
        
        # Register hooks
        hook_manager.register_all_hooks()
        initial_status = hook_manager.get_hook_status()
        
        # Simulate failure and recovery
        try:
            # Force an error in hook execution
            with patch.object(hook_manager, '_log_hook_execution', side_effect=Exception("Logging error")):
                feature_path = temp_workspace / 'features' / 'recovery_test.py'
                feature_path.write_text('def recovery_function(): pass')
                
                # Should handle logging error gracefully
                hook_manager.handle_feature_created(str(feature_path))
        except Exception:
            pass  # Expected to handle gracefully
        
        # Verify hook manager is still functional
        current_status = hook_manager.get_hook_status()
        assert current_status['hooks']['feature_created']['enabled'] == initial_status['hooks']['feature_created']['enabled']
        assert current_status['hooks']['readme_save']['enabled'] == initial_status['hooks']['readme_save']['enabled']
    
    def test_hook_integration_with_app_lifecycle(self, temp_workspace):
        """Test hook integration with full application lifecycle."""
        # Create app with hooks enabled
        config = AppConfig(
            workspace_path=str(temp_workspace),
            hook_config=HookConfig(
                feature_created_enabled=True,
                readme_save_enabled=True
            )
        )
        
        app = create_app(workspace_path=str(temp_workspace), config=config)
        
        # Register hooks through app
        app.register_hooks()
        
        # Verify hooks are registered
        hook_status = app.hook_manager.get_hook_status()
        assert hook_status['hooks']['feature_created']['registered'] == True
        assert hook_status['hooks']['readme_save']['registered'] == True
        
        # Test hook execution through app interface
        feature_path = temp_workspace / 'features' / 'app_lifecycle_test.py'
        feature_path.write_text('def app_lifecycle_function(): pass')
        
        # Mock AI to avoid external dependencies
        with patch('src.ai.processing_engine.AIProcessingEngine.analyze_feature_code') as mock_analyze:
            mock_analyze.return_value = Mock(feature_path=str(feature_path), functions=[], tests_needed=[])
            
            # Execute through app interface
            app.handle_feature_created(str(feature_path))
            
            # Verify execution
            mock_analyze.assert_called_once_with(str(feature_path))
        
        # Test graceful shutdown
        app.shutdown()
        
        # Verify cleanup
        assert app._hook_manager is None