"""Configuration loading utilities for SpecOps."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from src.models import AppConfig, StyleConfig, HookConfig


class ConfigLoader:
    """Utility class for loading configuration from various sources."""

    def __init__(self, workspace_path: str = '.'):
        """Initialize the config loader with workspace path."""
        self.workspace_path = Path(workspace_path)

    def load_from_steering(self) -> AppConfig:
        """Load configuration from .kiro/steering files."""
        steering_path = self.workspace_path / '.kiro' / 'steering'
        
        style_config = StyleConfig(
            code_style_path=str(steering_path / 'code-style.md'),
            structure_style_path=str(steering_path / 'stucture.md'),
            onboarding_style_path=str(steering_path / 'onboarding-style.md')
        )
        
        # Load content from files
        style_config.load_content()
        
        # Create default hook config
        hook_config = HookConfig()
        
        return AppConfig(
            style_config=style_config,
            hook_config=hook_config,
            workspace_path=str(self.workspace_path)
        )

    def load_from_json(self, config_path: str) -> AppConfig:
        """Load configuration from JSON file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return AppConfig.from_dict(config_data)
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading configuration: {e}")

    def save_to_json(self, config: AppConfig, config_path: str) -> None:
        """Save configuration to JSON file."""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Error saving configuration: {e}")

    def load_from_env(self) -> Dict[str, Any]:
        """Load configuration overrides from environment variables."""
        env_config = {}
        
        # AI configuration
        if 'SPECOPS_AI_MODEL' in os.environ:
            env_config['ai_model'] = os.environ['SPECOPS_AI_MODEL']
        
        if 'SPECOPS_AI_TEMPERATURE' in os.environ:
            try:
                env_config['ai_temperature'] = float(os.environ['SPECOPS_AI_TEMPERATURE'])
            except ValueError:
                pass  # Ignore invalid values
        
        # Debug mode
        if 'SPECOPS_DEBUG' in os.environ:
            env_config['debug_mode'] = os.environ['SPECOPS_DEBUG'].lower() in ('true', '1', 'yes')
        
        # Hook configuration
        hook_config = {}
        if 'SPECOPS_FEATURE_HOOK_ENABLED' in os.environ:
            hook_config['feature_created_enabled'] = os.environ['SPECOPS_FEATURE_HOOK_ENABLED'].lower() in ('true', '1', 'yes')
        
        if 'SPECOPS_README_HOOK_ENABLED' in os.environ:
            hook_config['readme_save_enabled'] = os.environ['SPECOPS_README_HOOK_ENABLED'].lower() in ('true', '1', 'yes')
        
        if 'SPECOPS_HOOK_TIMEOUT' in os.environ:
            try:
                hook_config['hook_timeout'] = int(os.environ['SPECOPS_HOOK_TIMEOUT'])
            except ValueError:
                pass
        
        if 'SPECOPS_LOG_LEVEL' in os.environ:
            hook_config['log_level'] = os.environ['SPECOPS_LOG_LEVEL'].upper()
        
        if hook_config:
            env_config['hooks'] = hook_config
        
        return env_config

    def load_config(self, config_path: Optional[str] = None) -> AppConfig:
        """Load configuration from multiple sources with precedence."""
        # Start with steering files as base
        config = self.load_from_steering()
        
        # Override with JSON config if provided
        if config_path and Path(config_path).exists():
            try:
                json_config = self.load_from_json(config_path)
                # Merge configurations (JSON takes precedence)
                config = self._merge_configs(config, json_config)
                # Ensure steering content is still loaded with correct paths
                config.style_config.load_content()
            except Exception as e:
                print(f"Warning: Could not load JSON config: {e}")
        
        # Apply environment variable overrides
        env_overrides = self.load_from_env()
        if env_overrides:
            env_config = AppConfig.from_dict(env_overrides)
            config = self._merge_configs(config, env_config)
        
        return config

    def _merge_configs(self, base_config: AppConfig, override_config: AppConfig) -> AppConfig:
        """Merge two configurations with override taking precedence."""
        # Convert to dicts for easier merging
        base_dict = base_config.to_dict()
        override_dict = override_config.to_dict()
        
        # Merge dictionaries
        merged_dict = self._deep_merge_dicts(base_dict, override_dict)
        
        return AppConfig.from_dict_preserve_paths(merged_dict, base_config)

    def _deep_merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result

    def get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        return str(self.workspace_path / '.kiro' / 'specops-config.json')

    def ensure_config_exists(self, config_path: Optional[str] = None) -> str:
        """Ensure a configuration file exists, creating default if needed."""
        if config_path is None:
            config_path = self.get_default_config_path()
        
        config_file = Path(config_path)
        
        if not config_file.exists():
            # Create default configuration
            default_config = self.load_from_steering()
            self.save_to_json(default_config, config_path)
        
        return config_path