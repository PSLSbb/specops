"""Unit tests for configuration loader."""

import json
import os
import tempfile
from pathlib import Path
import pytest
from src.config_loader import ConfigLoader
from src.models import AppConfig, StyleConfig, HookConfig


class TestConfigLoader:
    """Test cases for ConfigLoader."""

    def test_init(self):
        """Test ConfigLoader initialization."""
        loader = ConfigLoader('/test/path')
        assert loader.workspace_path == Path('/test/path')

    def test_load_from_steering_missing_files(self):
        """Test loading from steering files when files don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = ConfigLoader(temp_dir)
            config = loader.load_from_steering()
            
            assert isinstance(config, AppConfig)
            assert isinstance(config.style_config, StyleConfig)
            assert isinstance(config.hook_config, HookConfig)
            assert config.workspace_path == temp_dir

    def test_load_from_steering_with_files(self):
        """Test loading from steering files when files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create steering directory and files
            steering_dir = Path(temp_dir) / '.kiro' / 'steering'
            steering_dir.mkdir(parents=True)
            
            # Create test steering files
            (steering_dir / 'code-style.md').write_text(
                "# Code Style\n- Use Python 3.8+\n- Follow PEP 8"
            )
            (steering_dir / 'stucture.md').write_text(
                "# Structure\n- src/ for code\n- tests/ for tests"
            )
            (steering_dir / 'onboarding-style.md').write_text(
                "# Onboarding\n- Be friendly\n- Use examples"
            )
            
            loader = ConfigLoader(temp_dir)
            config = loader.load_from_steering()
            
            assert "Use Python 3.8+" in config.style_config.code_style_content
            assert "src/ for code" in config.style_config.structure_style_content
            assert "Be friendly" in config.style_config.onboarding_style_content

    def test_load_from_json_valid_file(self):
        """Test loading configuration from valid JSON file."""
        config_data = {
            'workspace_path': '/test/workspace',
            'ai_model': 'gpt-4',
            'ai_temperature': 0.5,
            'debug_mode': True,
            'hooks': {
                'feature_created_enabled': False,
                'log_level': 'DEBUG'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader()
            config = loader.load_from_json(config_path)
            
            assert config.workspace_path == '/test/workspace'
            assert config.ai_model == 'gpt-4'
            assert config.ai_temperature == 0.5
            assert config.debug_mode is True
            assert config.hook_config.feature_created_enabled is False
            assert config.hook_config.log_level == 'DEBUG'
        finally:
            os.unlink(config_path)

    def test_load_from_json_file_not_found(self):
        """Test loading from non-existent JSON file."""
        loader = ConfigLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_from_json('nonexistent.json')

    def test_load_from_json_invalid_json(self):
        """Test loading from invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('invalid json content')
            config_path = f.name
        
        try:
            loader = ConfigLoader()
            with pytest.raises(ValueError, match="Invalid JSON"):
                loader.load_from_json(config_path)
        finally:
            os.unlink(config_path)

    def test_save_to_json(self):
        """Test saving configuration to JSON file."""
        config = AppConfig(
            workspace_path='/test/path',
            ai_model='gpt-4',
            debug_mode=True
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.json'
            loader = ConfigLoader()
            loader.save_to_json(config, str(config_path))
            
            assert config_path.exists()
            
            # Verify content
            with open(config_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data['workspace_path'] == '/test/path'
            assert saved_data['ai_model'] == 'gpt-4'
            assert saved_data['debug_mode'] is True

    def test_load_from_env_empty(self):
        """Test loading from environment variables when none are set."""
        loader = ConfigLoader()
        env_config = loader.load_from_env()
        assert env_config == {}

    def test_load_from_env_with_values(self):
        """Test loading from environment variables with values set."""
        env_vars = {
            'SPECOPS_AI_MODEL': 'gpt-4',
            'SPECOPS_AI_TEMPERATURE': '0.3',
            'SPECOPS_DEBUG': 'true',
            'SPECOPS_FEATURE_HOOK_ENABLED': 'false',
            'SPECOPS_README_HOOK_ENABLED': 'yes',
            'SPECOPS_HOOK_TIMEOUT': '45',
            'SPECOPS_LOG_LEVEL': 'error'
        }
        
        # Set environment variables
        for key, value in env_vars.items():
            os.environ[key] = value
        
        try:
            loader = ConfigLoader()
            env_config = loader.load_from_env()
            
            assert env_config['ai_model'] == 'gpt-4'
            assert env_config['ai_temperature'] == 0.3
            assert env_config['debug_mode'] is True
            assert env_config['hooks']['feature_created_enabled'] is False
            assert env_config['hooks']['readme_save_enabled'] is True
            assert env_config['hooks']['hook_timeout'] == 45
            assert env_config['hooks']['log_level'] == 'ERROR'
        finally:
            # Clean up environment variables
            for key in env_vars:
                os.environ.pop(key, None)

    def test_load_from_env_invalid_values(self):
        """Test loading from environment variables with invalid values."""
        env_vars = {
            'SPECOPS_AI_TEMPERATURE': 'invalid_float',
            'SPECOPS_HOOK_TIMEOUT': 'invalid_int'
        }
        
        # Set environment variables
        for key, value in env_vars.items():
            os.environ[key] = value
        
        try:
            loader = ConfigLoader()
            env_config = loader.load_from_env()
            
            # Invalid values should be ignored
            assert 'ai_temperature' not in env_config
            assert 'hooks' not in env_config or 'hook_timeout' not in env_config.get('hooks', {})
        finally:
            # Clean up environment variables
            for key in env_vars:
                os.environ.pop(key, None)

    def test_merge_configs(self):
        """Test merging two configurations."""
        # Create base config with specific values
        base_config = AppConfig(
            workspace_path='/base/path',
            ai_model='gpt-3.5-turbo',
            debug_mode=False
        )
        base_config.hook_config.feature_created_enabled = True
        base_config.hook_config.log_level = 'INFO'
        
        # Create override config from dict (only specifying values to override)
        override_dict = {
            'ai_model': 'gpt-4',
            'debug_mode': True,
            'hooks': {
                'log_level': 'DEBUG'
            }
        }
        
        # Test the deep merge directly
        loader = ConfigLoader()
        base_dict = base_config.to_dict()
        merged_dict = loader._deep_merge_dicts(base_dict, override_dict)
        merged_config = AppConfig.from_dict(merged_dict)
        
        # Base values should be preserved where not overridden
        assert merged_config.workspace_path == '/base/path'
        assert merged_config.hook_config.feature_created_enabled is True
        
        # Override values should take precedence
        assert merged_config.ai_model == 'gpt-4'
        assert merged_config.debug_mode is True
        assert merged_config.hook_config.log_level == 'DEBUG'

    def test_deep_merge_dicts(self):
        """Test deep merging of dictionaries."""
        base = {
            'a': 1,
            'b': {
                'c': 2,
                'd': 3
            },
            'e': 4
        }
        
        override = {
            'b': {
                'd': 5,
                'f': 6
            },
            'g': 7
        }
        
        loader = ConfigLoader()
        result = loader._deep_merge_dicts(base, override)
        
        assert result['a'] == 1  # Preserved from base
        assert result['b']['c'] == 2  # Preserved from base
        assert result['b']['d'] == 5  # Overridden
        assert result['b']['f'] == 6  # Added from override
        assert result['e'] == 4  # Preserved from base
        assert result['g'] == 7  # Added from override

    def test_get_default_config_path(self):
        """Test getting default configuration path."""
        loader = ConfigLoader('/test/workspace')
        path = loader.get_default_config_path()
        expected_path = str(Path('/test/workspace') / '.kiro' / 'specops-config.json')
        assert path == expected_path

    def test_ensure_config_exists_creates_file(self):
        """Test that ensure_config_exists creates a file when it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = ConfigLoader(temp_dir)
            config_path = loader.ensure_config_exists()
            
            assert Path(config_path).exists()
            
            # Verify it's valid JSON
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            assert 'workspace_path' in config_data

    def test_ensure_config_exists_preserves_existing(self):
        """Test that ensure_config_exists preserves existing files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'existing-config.json'
            original_content = {'test': 'value'}
            
            with open(config_path, 'w') as f:
                json.dump(original_content, f)
            
            loader = ConfigLoader(temp_dir)
            result_path = loader.ensure_config_exists(str(config_path))
            
            assert result_path == str(config_path)
            
            # Verify original content is preserved
            with open(config_path, 'r') as f:
                content = json.load(f)
            assert content == original_content

    def test_load_config_integration(self):
        """Test the complete load_config method with multiple sources."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create steering files
            steering_dir = Path(temp_dir) / '.kiro' / 'steering'
            steering_dir.mkdir(parents=True)
            (steering_dir / 'code-style.md').write_text("# Code Style\n- Rule 1")
            (steering_dir / 'stucture.md').write_text("# Structure\n- Rule 2")
            (steering_dir / 'onboarding-style.md').write_text("# Onboarding\n- Rule 3")
            
            # Create JSON config
            json_config = {
                'ai_model': 'gpt-4',
                'hooks': {
                    'log_level': 'DEBUG'
                }
            }
            config_path = Path(temp_dir) / 'config.json'
            with open(config_path, 'w') as f:
                json.dump(json_config, f)
            
            loader = ConfigLoader(temp_dir)
            
            # Test just steering + JSON (no environment variables)
            base_config = loader.load_from_steering()
            json_config_obj = loader.load_from_json(str(config_path))
            merged_config = loader._merge_configs(base_config, json_config_obj)
            merged_config.style_config.load_content()
            
            # Should have steering content
            assert "Rule 1" in merged_config.style_config.code_style_content
            
            # Should have JSON overrides
            assert merged_config.ai_model == 'gpt-4'
            assert merged_config.hook_config.log_level == 'DEBUG'