"""Configuration models and loading utilities."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
import os


@dataclass
class StyleConfig:
    """Configuration for style and formatting guidelines."""
    code_style_path: str
    structure_style_path: str
    onboarding_style_path: str
    
    @classmethod
    def from_kiro_steering(cls, base_path: str = ".kiro/steering") -> 'StyleConfig':
        """Load style configuration from .kiro/steering directory."""
        return cls(
            code_style_path=os.path.join(base_path, "code-style.md"),
            structure_style_path=os.path.join(base_path, "stucture.md"),
            onboarding_style_path=os.path.join(base_path, "onboarding-style.md")
        )


@dataclass
class HookConfig:
    """Configuration for hook behavior."""
    feature_created_enabled: bool = True
    readme_save_enabled: bool = True
    auto_update_interval: int = 0  # 0 = immediate
    
    @classmethod
    def default(cls) -> 'HookConfig':
        """Create default hook configuration."""
        return cls()


@dataclass
class AIConfig:
    """Configuration for AI processing."""
    model_name: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30
    github_token: Optional[str] = None
    
    @classmethod
    def default(cls) -> 'AIConfig':
        """Create default AI configuration."""
        return cls()


@dataclass
class SpecOpsConfig:
    """Main configuration for SpecOps application."""
    style: StyleConfig
    hooks: HookConfig
    ai: AIConfig
    repo_path: str = "."
    output_dir: str = "."
    
    @classmethod
    def load_default(cls, repo_path: str = ".") -> 'SpecOpsConfig':
        """Load default configuration."""
        return cls(
            style=StyleConfig.from_kiro_steering(),
            hooks=HookConfig.default(),
            ai=AIConfig.default(),
            repo_path=repo_path,
            output_dir=repo_path
        )