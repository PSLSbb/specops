"""Tests for HookManager component."""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from src.hooks.hook_manager import HookManager, HookError
from src.models import HookConfig


class TestHookManager:
    """Test cases for HookManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = HookConfig(
            feature_created_enabled=True,
            readme_save_enabled=True,
            hook_timeout=30,
            max_retries=3,
            log_level='INFO'
        )
        self.hook_manager = HookManager(self.config)
    
    def test_init_with_default_config(self):
        """Test HookManager initialization with default configuration."""
        manager = HookManager()
        
        assert manager.config is not None
        assert isinstance(manager.config, HookConfig)
        assert manager.config.feature_created_enabled is True
        assert manager.config.readme_save_enabled is True
        assert len(manager._hook_registry) == 2
        assert 'feature_created' in manager._hook_registry
        assert 'readme_save' in manager._hook_registry
    
    def test_init_with_custom_config(self):
        """Test HookManager initialization with custom configuration."""
        custom_config = HookConfig(
            feature_created_enabled=False,
            readme_save_enabled=True,
            hook_timeout=60,
            max_retries=5,
            log_level='DEBUG'
        )
        manager = HookManager(custom_config)
        
        assert manager.config == custom_config
        assert manager._hook_registry['feature_created']['enabled'] is False
        assert manager._hook_registry['readme_save']['enabled'] is True
    
    def test_setup_logging(self):
        """Test logging configuration setup."""
        manager = HookManager(HookConfig(log_level='DEBUG'))
        
        assert manager.logger.level == logging.DEBUG
        assert len(manager.logger.handlers) > 0
    
    def test_initialize_registry(self):
        """Test hook registry initialization."""
        registry = self.hook_manager._hook_registry
        
        assert len(registry) == 2
        
        # Test feature_created hook registry
        feature_hook = registry['feature_created']
        assert feature_hook['enabled'] is True
        assert feature_hook['handler'] == 'handle_feature_created'
        assert feature_hook['timeout'] == 30
        assert feature_hook['max_retries'] == 3
        assert 'description' in feature_hook
        
        # Test readme_save hook registry
        readme_hook = registry['readme_save']
        assert readme_hook['enabled'] is True
        assert readme_hook['handler'] == 'handle_readme_saved'
        assert readme_hook['timeout'] == 30
        assert readme_hook['max_retries'] == 3
        assert 'description' in readme_hook
    
    def test_register_feature_created_hook_success(self):
        """Test successful feature_created hook registration."""
        self.hook_manager.register_feature_created_hook()
        
        assert 'feature_created' in self.hook_manager._handlers
        assert self.hook_manager._hook_registry['feature_created']['registered'] is True
        assert 'config' in self.hook_manager._hook_registry['feature_created']
    
    def test_register_feature_created_hook_disabled(self):
        """Test feature_created hook registration when disabled."""
        disabled_config = HookConfig(feature_created_enabled=False)
        manager = HookManager(disabled_config)
        
        manager.register_feature_created_hook()
        
        assert 'feature_created' not in manager._handlers
        assert manager._hook_registry['feature_created'].get('registered') is not True
    
    def test_register_readme_save_hook_success(self):
        """Test successful readme_save hook registration."""
        self.hook_manager.register_readme_save_hook()
        
        assert 'readme_save' in self.hook_manager._handlers
        assert self.hook_manager._hook_registry['readme_save']['registered'] is True
        assert 'config' in self.hook_manager._hook_registry['readme_save']
    
    def test_register_readme_save_hook_disabled(self):
        """Test readme_save hook registration when disabled."""
        disabled_config = HookConfig(readme_save_enabled=False)
        manager = HookManager(disabled_config)
        
        manager.register_readme_save_hook()
        
        assert 'readme_save' not in manager._handlers
        assert manager._hook_registry['readme_save'].get('registered') is not True
    
    def test_register_all_hooks(self):
        """Test registering all hooks at once."""
        self.hook_manager.register_all_hooks()
        
        assert 'feature_created' in self.hook_manager._handlers
        assert 'readme_save' in self.hook_manager._handlers
        assert self.hook_manager._hook_registry['feature_created']['registered'] is True
        assert self.hook_manager._hook_registry['readme_save']['registered'] is True
    
    @patch('src.hooks.hook_manager.AIProcessingEngine')
    @patch('src.hooks.hook_manager.TaskGenerator')
    def test_handle_feature_created_success(self, mock_task_gen, mock_ai_engine):
        """Test successful feature_created event handling."""
        # Mock the components
        mock_ai_instance = Mock()
        mock_task_instance = Mock()
        mock_ai_engine.return_value = mock_ai_instance
        mock_task_gen.return_value = mock_task_instance
        
        # Create a new hook manager to get mocked components
        hook_manager = HookManager(self.config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test_function(): pass')
            temp_path = f.name
        
        try:
            # Should not raise an exception
            hook_manager.handle_feature_created(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_handle_feature_created_invalid_path(self):
        """Test feature_created event handling with invalid path."""
        # Should not raise exception due to graceful degradation
        self.hook_manager.handle_feature_created("")
        self.hook_manager.handle_feature_created(None)
        self.hook_manager.handle_feature_created("/nonexistent/path.py")
    
    def test_handle_feature_created_disabled(self):
        """Test feature_created event handling when hook is disabled."""
        disabled_config = HookConfig(feature_created_enabled=False)
        manager = HookManager(disabled_config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test_function(): pass')
            temp_path = f.name
        
        try:
            # Should return early without processing
            manager.handle_feature_created(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch('src.hooks.hook_manager.ContentAnalyzer')
    @patch('src.hooks.hook_manager.AIProcessingEngine')
    @patch('src.hooks.hook_manager.FAQGenerator')
    @patch('src.hooks.hook_manager.QuickStartGenerator')
    def test_handle_readme_saved_success(self, mock_qs_gen, mock_faq_gen, mock_ai_engine, mock_content_analyzer):
        """Test successful readme_saved event handling."""
        # Mock the components
        mock_content_instance = Mock()
        mock_ai_instance = Mock()
        mock_faq_instance = Mock()
        mock_qs_instance = Mock()
        
        mock_content_analyzer.return_value = mock_content_instance
        mock_ai_engine.return_value = mock_ai_instance
        mock_faq_gen.return_value = mock_faq_instance
        mock_qs_gen.return_value = mock_qs_instance
        
        # Create a new hook manager to get mocked components
        hook_manager = HookManager(self.config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('# Test README\n\nThis is a test.')
            temp_path = f.name
        
        try:
            # Should not raise an exception
            hook_manager.handle_readme_saved(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_handle_readme_saved_invalid_path(self):
        """Test readme_saved event handling with invalid path."""
        # Should not raise exception due to graceful degradation
        self.hook_manager.handle_readme_saved("")
        self.hook_manager.handle_readme_saved(None)
        self.hook_manager.handle_readme_saved("/nonexistent/README.md")
    
    def test_handle_readme_saved_disabled(self):
        """Test readme_saved event handling when hook is disabled."""
        disabled_config = HookConfig(readme_save_enabled=False)
        manager = HookManager(disabled_config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('# Test README\n\nThis is a test.')
            temp_path = f.name
        
        try:
            # Should return early without processing
            manager.handle_readme_saved(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_log_hook_execution(self):
        """Test hook execution logging."""
        with patch.object(self.hook_manager.logger, 'info') as mock_info:
            self.hook_manager._log_hook_execution('feature_created', '/test/path.py', 'success')
            mock_info.assert_called_once()
        
        with patch.object(self.hook_manager.logger, 'error') as mock_error:
            self.hook_manager._log_hook_execution('readme_save', '/test/README.md', 'error', 'Test error')
            mock_error.assert_called_once()
    
    def test_get_hook_status(self):
        """Test getting hook status information."""
        status = self.hook_manager.get_hook_status()
        
        assert 'hooks' in status
        assert 'config' in status
        
        # Test hooks section
        hooks = status['hooks']
        assert 'feature_created' in hooks
        assert 'readme_save' in hooks
        
        feature_hook = hooks['feature_created']
        assert 'enabled' in feature_hook
        assert 'registered' in feature_hook
        assert 'handler' in feature_hook
        assert 'description' in feature_hook
        
        # Test config section
        config = status['config']
        assert config['feature_created_enabled'] is True
        assert config['readme_save_enabled'] is True
        assert config['hook_timeout'] == 30
        assert config['max_retries'] == 3
        assert config['log_level'] == 'INFO'
    
    def test_unregister_hook_success(self):
        """Test successful hook unregistration."""
        # First register the hook
        self.hook_manager.register_feature_created_hook()
        assert 'feature_created' in self.hook_manager._handlers
        
        # Then unregister it
        self.hook_manager.unregister_hook('feature_created')
        assert 'feature_created' not in self.hook_manager._handlers
        assert self.hook_manager._hook_registry['feature_created']['registered'] is False
    
    def test_unregister_hook_unknown_type(self):
        """Test unregistering unknown hook type."""
        # Should not raise exception, just log warning
        self.hook_manager.unregister_hook('unknown_hook')
    
    def test_unregister_all_hooks(self):
        """Test unregistering all hooks."""
        # First register hooks
        self.hook_manager.register_all_hooks()
        assert len(self.hook_manager._handlers) == 2
        
        # Then unregister all
        self.hook_manager.unregister_all_hooks()
        assert len(self.hook_manager._handlers) == 0
        assert self.hook_manager._hook_registry['feature_created']['registered'] is False
        assert self.hook_manager._hook_registry['readme_save']['registered'] is False
    
    def test_update_config(self):
        """Test updating hook configuration."""
        # Register hooks with initial config
        self.hook_manager.register_all_hooks()
        
        # Update config
        new_config = HookConfig(
            feature_created_enabled=False,
            readme_save_enabled=True,
            hook_timeout=60,
            max_retries=5,
            log_level='DEBUG'
        )
        
        self.hook_manager.update_config(new_config)
        
        assert self.hook_manager.config == new_config
        assert self.hook_manager._hook_registry['feature_created']['enabled'] is False
        assert self.hook_manager._hook_registry['readme_save']['enabled'] is True
        assert self.hook_manager.logger.level == logging.DEBUG
    
    def test_hook_error_exception(self):
        """Test HookError exception handling."""
        with pytest.raises(HookError):
            raise HookError("Test error message")
    
    @patch('src.hooks.hook_manager.Path')
    def test_handle_feature_created_with_path_mock(self, mock_path):
        """Test feature_created handling with mocked Path."""
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_file.name = 'test_feature.py'
        mock_path.return_value = mock_file
        
        # Should complete without error
        self.hook_manager.handle_feature_created('/test/feature.py')
        
        mock_path.assert_called_once_with('/test/feature.py')
        mock_file.exists.assert_called_once()
    
    @patch('src.hooks.hook_manager.Path')
    def test_handle_readme_saved_with_path_mock(self, mock_path):
        """Test readme_saved handling with mocked Path."""
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_file.name = 'README.md'
        mock_path.return_value = mock_file
        
        # Should complete without error
        self.hook_manager.handle_readme_saved('/test/README.md')
        
        mock_path.assert_called_once_with('/test/README.md')
        mock_file.exists.assert_called_once()


class TestHookManagerIntegration:
    """Integration tests for HookManager."""
    
    def test_full_hook_lifecycle(self):
        """Test complete hook registration and execution lifecycle."""
        config = HookConfig(
            feature_created_enabled=True,
            readme_save_enabled=True,
            hook_timeout=10,
            max_retries=1,
            log_level='INFO'
        )
        
        manager = HookManager(config)
        
        # Register hooks
        manager.register_all_hooks()
        
        # Check status
        status = manager.get_hook_status()
        assert status['hooks']['feature_created']['registered'] is True
        assert status['hooks']['readme_save']['registered'] is True
        
        # Create temporary files for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as feature_file:
            feature_file.write('def new_feature(): pass')
            feature_path = feature_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as readme_file:
            readme_file.write('# Updated README')
            readme_path = readme_file.name
        
        try:
            # Execute hooks
            manager.handle_feature_created(feature_path)
            manager.handle_readme_saved(readme_path)
            
            # Unregister hooks
            manager.unregister_all_hooks()
            
            # Verify unregistration
            final_status = manager.get_hook_status()
            assert final_status['hooks']['feature_created']['registered'] is False
            assert final_status['hooks']['readme_save']['registered'] is False
            
        finally:
            # Clean up temporary files
            os.unlink(feature_path)
            os.unlink(readme_path)
    
    def test_config_update_integration(self):
        """Test configuration updates with hook re-registration."""
        initial_config = HookConfig(
            feature_created_enabled=True,
            readme_save_enabled=False,
            log_level='INFO'
        )
        
        manager = HookManager(initial_config)
        manager.register_all_hooks()
        
        # Verify initial state
        assert 'feature_created' in manager._handlers
        assert 'readme_save' not in manager._handlers
        
        # Update configuration
        updated_config = HookConfig(
            feature_created_enabled=False,
            readme_save_enabled=True,
            log_level='DEBUG'
        )
        
        manager.update_config(updated_config)
        
        # Verify updated state
        assert manager.config == updated_config
        assert manager.logger.level == logging.DEBUG
    
    def test_find_tasks_file(self):
        """Test finding tasks.md file in workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            hook_manager = HookManager(workspace_path=str(temp_path))
            
            # Test when no tasks.md exists
            result = hook_manager._find_tasks_file()
            assert result is None
            
            # Create tasks.md in workspace root
            tasks_file = temp_path / 'tasks.md'
            tasks_file.write_text('# Tasks\n\n- [ ] Test task')
            
            result = hook_manager._find_tasks_file()
            assert result == tasks_file
    
    def test_find_or_create_faq_file(self):
        """Test finding or creating FAQ file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            hook_manager = HookManager(workspace_path=str(temp_path))
            
            # Test when no FAQ file exists - should return default location
            result = hook_manager._find_or_create_faq_file()
            assert result == temp_path / 'faq.md'
            
            # Create FAQ file and test finding it
            faq_file = temp_path / 'faq.md'
            faq_file.write_text('# FAQ\n\n## Question 1\nAnswer 1')
            
            result = hook_manager._find_or_create_faq_file()
            assert result == faq_file