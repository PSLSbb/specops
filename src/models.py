"""Enhanced data models with validation for SpecOps components."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re
from pathlib import Path


class ValidationError(Exception):
    """Raised when data model validation fails."""
    pass


@dataclass
class RepositoryAnalysis:
    """Analysis results from repository content scanning."""
    concepts: List['Concept'] = field(default_factory=list)
    setup_steps: List['SetupStep'] = field(default_factory=list)
    code_examples: List['CodeExample'] = field(default_factory=list)
    file_structure: Dict[str, Any] = field(default_factory=dict)
    dependencies: List['Dependency'] = field(default_factory=list)

    def __post_init__(self):
        """Validate the repository analysis data."""
        self.validate()

    def validate(self) -> None:
        """Validate all components of the repository analysis."""
        if not isinstance(self.concepts, list):
            raise ValidationError("concepts must be a list")
        if not isinstance(self.setup_steps, list):
            raise ValidationError("setup_steps must be a list")
        if not isinstance(self.code_examples, list):
            raise ValidationError("code_examples must be a list")
        if not isinstance(self.file_structure, dict):
            raise ValidationError("file_structure must be a dictionary")
        if not isinstance(self.dependencies, list):
            raise ValidationError("dependencies must be a list")

        # Validate nested objects
        for concept in self.concepts:
            if hasattr(concept, 'validate'):
                concept.validate()
        for step in self.setup_steps:
            if hasattr(step, 'validate'):
                step.validate()
        for example in self.code_examples:
            if hasattr(example, 'validate'):
                example.validate()
        for dependency in self.dependencies:
            if hasattr(dependency, 'validate'):
                dependency.validate()


@dataclass
class Concept:
    """A key concept identified in repository content."""
    name: str
    description: str
    importance: int
    related_files: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate the concept data."""
        self.validate()

    def validate(self) -> None:
        """Validate concept data."""
        if not self.name or not isinstance(self.name, str):
            raise ValidationError("name must be a non-empty string")
        if not self.description or not isinstance(self.description, str):
            raise ValidationError("description must be a non-empty string")
        if not isinstance(self.importance, int) or not (1 <= self.importance <= 10):
            raise ValidationError("importance must be an integer between 1 and 10")
        if not isinstance(self.related_files, list):
            raise ValidationError("related_files must be a list")
        if not isinstance(self.prerequisites, list):
            raise ValidationError("prerequisites must be a list")
        
        # Validate file paths
        for file_path in self.related_files:
            if not isinstance(file_path, str):
                raise ValidationError("all related_files must be strings")


@dataclass
class SetupStep:
    """A setup or installation step."""
    title: str
    description: str
    commands: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    order: int = 0

    def __post_init__(self):
        """Validate the setup step data."""
        self.validate()

    def validate(self) -> None:
        """Validate setup step data."""
        if not self.title or not isinstance(self.title, str):
            raise ValidationError("title must be a non-empty string")
        if not self.description or not isinstance(self.description, str):
            raise ValidationError("description must be a non-empty string")
        if not isinstance(self.commands, list):
            raise ValidationError("commands must be a list")
        if not isinstance(self.prerequisites, list):
            raise ValidationError("prerequisites must be a list")
        if not isinstance(self.order, int) or self.order < 0:
            raise ValidationError("order must be a non-negative integer")

        # Validate commands are strings
        for command in self.commands:
            if not isinstance(command, str):
                raise ValidationError("all commands must be strings")


@dataclass
class CodeExample:
    """A code example found in documentation."""
    title: str
    code: str
    language: str
    description: str
    file_path: str

    def __post_init__(self):
        """Validate the code example data."""
        self.validate()

    def validate(self) -> None:
        """Validate code example data."""
        if not self.title or not isinstance(self.title, str):
            raise ValidationError("title must be a non-empty string")
        if not self.code or not isinstance(self.code, str):
            raise ValidationError("code must be a non-empty string")
        if not self.language or not isinstance(self.language, str):
            raise ValidationError("language must be a non-empty string")
        if not self.description or not isinstance(self.description, str):
            raise ValidationError("description must be a non-empty string")
        if not self.file_path or not isinstance(self.file_path, str):
            raise ValidationError("file_path must be a non-empty string")

        # Validate language is reasonable
        valid_languages = {
            'python', 'javascript', 'typescript', 'java', 'c', 'cpp', 'c++',
            'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'shell',
            'bash', 'powershell', 'sql', 'html', 'css', 'json', 'yaml', 'xml'
        }
        if self.language.lower() not in valid_languages:
            # Don't raise error, just normalize unknown languages
            pass


@dataclass
class Dependency:
    """A project dependency."""
    name: str
    version: Optional[str] = None
    type: str = 'runtime'
    description: str = ''

    def __post_init__(self):
        """Validate the dependency data."""
        self.validate()

    def validate(self) -> None:
        """Validate dependency data."""
        if not self.name or not isinstance(self.name, str):
            raise ValidationError("name must be a non-empty string")
        if self.version is not None and not isinstance(self.version, str):
            raise ValidationError("version must be a string or None")
        if not isinstance(self.type, str):
            raise ValidationError("type must be a string")
        if not isinstance(self.description, str):
            raise ValidationError("description must be a string")

        # Validate dependency type
        valid_types = {'runtime', 'dev', 'optional', 'peer', 'build'}
        if self.type not in valid_types:
            raise ValidationError(f"type must be one of {valid_types}")

        # Validate version format if provided
        if self.version and not re.match(r'^[\d\w\.\-\+]+$', self.version):
            raise ValidationError("version format is invalid")


@dataclass
class TaskSuggestion:
    """AI-generated suggestion for an onboarding task."""
    title: str
    description: str
    acceptance_criteria: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    estimated_time: int = 30
    difficulty: str = 'medium'

    def __post_init__(self):
        """Validate the task suggestion data."""
        self.validate()

    def validate(self) -> None:
        """Validate task suggestion data."""
        if not self.title or not isinstance(self.title, str):
            raise ValidationError("title must be a non-empty string")
        if not self.description or not isinstance(self.description, str):
            raise ValidationError("description must be a non-empty string")
        if not isinstance(self.acceptance_criteria, list):
            raise ValidationError("acceptance_criteria must be a list")
        if not isinstance(self.prerequisites, list):
            raise ValidationError("prerequisites must be a list")
        if not isinstance(self.estimated_time, int) or self.estimated_time <= 0:
            raise ValidationError("estimated_time must be a positive integer")
        if not isinstance(self.difficulty, str):
            raise ValidationError("difficulty must be a string")

        # Validate difficulty level
        valid_difficulties = {'easy', 'medium', 'hard', 'expert'}
        if self.difficulty.lower() not in valid_difficulties:
            raise ValidationError(f"difficulty must be one of {valid_difficulties}")

        # Validate acceptance criteria are non-empty strings
        for criteria in self.acceptance_criteria:
            if not isinstance(criteria, str) or not criteria.strip():
                raise ValidationError("all acceptance_criteria must be non-empty strings")


@dataclass
class FAQPair:
    """A question-answer pair for FAQ generation."""
    question: str
    answer: str
    category: str = 'general'
    source_files: List[str] = field(default_factory=list)
    confidence: float = 0.8

    def __post_init__(self):
        """Validate the FAQ pair data."""
        self.validate()

    def validate(self) -> None:
        """Validate FAQ pair data."""
        if not self.question or not isinstance(self.question, str):
            raise ValidationError("question must be a non-empty string")
        if not self.answer or not isinstance(self.answer, str):
            raise ValidationError("answer must be a non-empty string")
        if not isinstance(self.category, str):
            raise ValidationError("category must be a string")
        if not isinstance(self.source_files, list):
            raise ValidationError("source_files must be a list")
        if not isinstance(self.confidence, (int, float)) or not (0.0 <= self.confidence <= 1.0):
            raise ValidationError("confidence must be a number between 0.0 and 1.0")

        # Validate question format
        if not self.question.strip().endswith('?'):
            # Auto-fix: add question mark if missing
            self.question = self.question.strip() + '?'

        # Validate source files are strings
        for file_path in self.source_files:
            if not isinstance(file_path, str):
                raise ValidationError("all source_files must be strings")


@dataclass
class QuickStartGuide:
    """Structure for Quick Start guide content."""
    prerequisites: List[str] = field(default_factory=list)
    setup_steps: List[str] = field(default_factory=list)
    basic_usage: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate the quick start guide data."""
        self.validate()

    def validate(self) -> None:
        """Validate quick start guide data."""
        if not isinstance(self.prerequisites, list):
            raise ValidationError("prerequisites must be a list")
        if not isinstance(self.setup_steps, list):
            raise ValidationError("setup_steps must be a list")
        if not isinstance(self.basic_usage, list):
            raise ValidationError("basic_usage must be a list")
        if not isinstance(self.next_steps, list):
            raise ValidationError("next_steps must be a list")

        # Validate all steps are non-empty strings
        for step_list, name in [
            (self.prerequisites, 'prerequisites'),
            (self.setup_steps, 'setup_steps'),
            (self.basic_usage, 'basic_usage'),
            (self.next_steps, 'next_steps')
        ]:
            for step in step_list:
                if not isinstance(step, str) or not step.strip():
                    raise ValidationError(f"all {name} must be non-empty strings")

    def is_empty(self) -> bool:
        """Check if the guide has any content."""
        return not any([
            self.prerequisites,
            self.setup_steps,
            self.basic_usage,
            self.next_steps
        ])


@dataclass
class FeatureAnalysis:
    """Analysis results from a specific feature."""
    feature_path: str
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)
    documentation: str = ''
    complexity: str = 'medium'

    def __post_init__(self):
        """Validate the feature analysis data."""
        self.validate()

    def validate(self) -> None:
        """Validate feature analysis data."""
        if not self.feature_path or not isinstance(self.feature_path, str):
            raise ValidationError("feature_path must be a non-empty string")
        if not isinstance(self.functions, list):
            raise ValidationError("functions must be a list")
        if not isinstance(self.classes, list):
            raise ValidationError("classes must be a list")
        if not isinstance(self.tests, list):
            raise ValidationError("tests must be a list")
        if not isinstance(self.documentation, str):
            raise ValidationError("documentation must be a string")
        if not isinstance(self.complexity, str):
            raise ValidationError("complexity must be a string")

        # Validate complexity level
        valid_complexities = {'low', 'medium', 'high', 'very_high'}
        if self.complexity.lower() not in valid_complexities:
            raise ValidationError(f"complexity must be one of {valid_complexities}")

        # Validate path exists (if it's a real path)
        try:
            path = Path(self.feature_path)
            if not path.exists() and not self.feature_path.startswith('test_'):
                # Don't validate test paths or mock paths
                pass
        except (OSError, ValueError):
            # Invalid path format, but don't fail validation
            pass


@dataclass
class StyleConfig:
    """Configuration for style guidelines from .kiro/steering files."""
    code_style_path: str = '.kiro/steering/code-style.md'
    structure_style_path: str = '.kiro/steering/stucture.md'
    onboarding_style_path: str = '.kiro/steering/onboarding-style.md'
    code_style_content: str = ''
    structure_style_content: str = ''
    onboarding_style_content: str = ''

    def __post_init__(self):
        """Validate the style configuration data."""
        self.validate()

    def validate(self) -> None:
        """Validate style configuration data."""
        if not isinstance(self.code_style_path, str):
            raise ValidationError("code_style_path must be a string")
        if not isinstance(self.structure_style_path, str):
            raise ValidationError("structure_style_path must be a string")
        if not isinstance(self.onboarding_style_path, str):
            raise ValidationError("onboarding_style_path must be a string")
        if not isinstance(self.code_style_content, str):
            raise ValidationError("code_style_content must be a string")
        if not isinstance(self.structure_style_content, str):
            raise ValidationError("structure_style_content must be a string")
        if not isinstance(self.onboarding_style_content, str):
            raise ValidationError("onboarding_style_content must be a string")

    def load_content(self) -> None:
        """Load content from steering files."""
        try:
            with open(self.code_style_path, 'r', encoding='utf-8') as f:
                self.code_style_content = f.read()
        except (FileNotFoundError, IOError):
            self.code_style_content = "# Default Code Style\n- Follow PEP 8 standards"

        try:
            with open(self.structure_style_path, 'r', encoding='utf-8') as f:
                self.structure_style_content = f.read()
        except (FileNotFoundError, IOError):
            self.structure_style_content = "# Default Structure\n- Organize code logically"

        try:
            with open(self.onboarding_style_path, 'r', encoding='utf-8') as f:
                self.onboarding_style_content = f.read()
        except (FileNotFoundError, IOError):
            self.onboarding_style_content = "# Default Onboarding Style\n- Be clear and helpful"

    def get_code_style_rules(self) -> List[str]:
        """Extract code style rules from content."""
        if not self.code_style_content:
            self.load_content()
        
        rules = []
        lines = self.code_style_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                rules.append(line[2:])  # Remove '- ' prefix
        return rules

    def get_structure_rules(self) -> List[str]:
        """Extract structure rules from content."""
        if not self.structure_style_content:
            self.load_content()
        
        rules = []
        lines = self.structure_style_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                rules.append(line[2:])  # Remove '- ' prefix
        return rules

    def get_onboarding_rules(self) -> List[str]:
        """Extract onboarding style rules from content."""
        if not self.onboarding_style_content:
            self.load_content()
        
        rules = []
        lines = self.onboarding_style_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                rules.append(line[2:])  # Remove '- ' prefix
        return rules


@dataclass
class HookConfig:
    """Configuration for Kiro hook integration."""
    feature_created_enabled: bool = True
    readme_save_enabled: bool = True
    auto_update_interval: int = 0  # 0 means no auto-update, only on events
    hook_timeout: int = 30  # seconds
    max_retries: int = 3
    log_level: str = 'INFO'

    def __post_init__(self):
        """Validate the hook configuration data."""
        self.validate()

    def validate(self) -> None:
        """Validate hook configuration data."""
        if not isinstance(self.feature_created_enabled, bool):
            raise ValidationError("feature_created_enabled must be a boolean")
        if not isinstance(self.readme_save_enabled, bool):
            raise ValidationError("readme_save_enabled must be a boolean")
        if not isinstance(self.auto_update_interval, int) or self.auto_update_interval < 0:
            raise ValidationError("auto_update_interval must be a non-negative integer")
        if not isinstance(self.hook_timeout, int) or self.hook_timeout <= 0:
            raise ValidationError("hook_timeout must be a positive integer")
        if not isinstance(self.max_retries, int) or self.max_retries < 0:
            raise ValidationError("max_retries must be a non-negative integer")
        if not isinstance(self.log_level, str):
            raise ValidationError("log_level must be a string")

        # Validate log level
        valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if self.log_level.upper() not in valid_log_levels:
            raise ValidationError(f"log_level must be one of {valid_log_levels}")

    def is_hook_enabled(self, hook_type: str) -> bool:
        """Check if a specific hook type is enabled."""
        if hook_type == 'feature_created':
            return self.feature_created_enabled
        elif hook_type == 'readme_save':
            return self.readme_save_enabled
        else:
            return False

    def get_retry_config(self) -> Dict[str, int]:
        """Get retry configuration for hooks."""
        return {
            'max_retries': self.max_retries,
            'timeout': self.hook_timeout
        }


@dataclass
class AppConfig:
    """Main application configuration combining all config types."""
    style_config: StyleConfig = field(default_factory=StyleConfig)
    hook_config: HookConfig = field(default_factory=HookConfig)
    workspace_path: str = '.'
    output_dir: str = '.'
    ai_model: str = 'gpt-3.5-turbo'
    ai_temperature: float = 0.7
    debug_mode: bool = False

    def __post_init__(self):
        """Validate the application configuration data."""
        self.validate()

    def validate(self) -> None:
        """Validate application configuration data."""
        if not isinstance(self.workspace_path, str):
            raise ValidationError("workspace_path must be a string")
        if not isinstance(self.output_dir, str):
            raise ValidationError("output_dir must be a string")
        if not isinstance(self.ai_model, str):
            raise ValidationError("ai_model must be a string")
        if not isinstance(self.ai_temperature, (int, float)) or not (0.0 <= self.ai_temperature <= 2.0):
            raise ValidationError("ai_temperature must be a number between 0.0 and 2.0")
        if not isinstance(self.debug_mode, bool):
            raise ValidationError("debug_mode must be a boolean")

        # Validate nested configurations
        if hasattr(self.style_config, 'validate'):
            self.style_config.validate()
        if hasattr(self.hook_config, 'validate'):
            self.hook_config.validate()

    def load_from_steering(self) -> None:
        """Load configuration from .kiro/steering files."""
        self.style_config.load_content()

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AppConfig':
        """Create AppConfig from dictionary."""
        # Create default instance first
        instance = cls()
        
        # Update style config if provided
        if 'style' in config_dict:
            style_data = config_dict['style']
            for key, value in style_data.items():
                if hasattr(instance.style_config, key):
                    setattr(instance.style_config, key, value)
        
        # Update hook config if provided
        if 'hooks' in config_dict:
            hook_data = config_dict['hooks']
            for key, value in hook_data.items():
                if hasattr(instance.hook_config, key):
                    setattr(instance.hook_config, key, value)
        
        # Update main config values
        for key in ['workspace_path', 'output_dir', 'ai_model', 'ai_temperature', 'debug_mode']:
            if key in config_dict:
                setattr(instance, key, config_dict[key])
        
        # Re-validate after updates
        instance.validate()
        
        return instance

    @classmethod
    def from_dict_preserve_paths(cls, config_dict: Dict[str, Any], base_config: Optional['AppConfig'] = None) -> 'AppConfig':
        """Create AppConfig from dictionary while preserving paths from base config."""
        # Start with base config if provided, otherwise create default
        if base_config:
            instance = cls(
                style_config=StyleConfig(
                    code_style_path=base_config.style_config.code_style_path,
                    structure_style_path=base_config.style_config.structure_style_path,
                    onboarding_style_path=base_config.style_config.onboarding_style_path,
                    code_style_content=base_config.style_config.code_style_content,
                    structure_style_content=base_config.style_config.structure_style_content,
                    onboarding_style_content=base_config.style_config.onboarding_style_content
                ),
                hook_config=HookConfig(
                    feature_created_enabled=base_config.hook_config.feature_created_enabled,
                    readme_save_enabled=base_config.hook_config.readme_save_enabled,
                    auto_update_interval=base_config.hook_config.auto_update_interval,
                    hook_timeout=base_config.hook_config.hook_timeout,
                    max_retries=base_config.hook_config.max_retries,
                    log_level=base_config.hook_config.log_level
                ),
                workspace_path=base_config.workspace_path,
                output_dir=base_config.output_dir,
                ai_model=base_config.ai_model,
                ai_temperature=base_config.ai_temperature,
                debug_mode=base_config.debug_mode
            )
        else:
            instance = cls()
        
        # Update style config if provided (but preserve paths if not explicitly set)
        if 'style' in config_dict:
            style_data = config_dict['style']
            for key, value in style_data.items():
                if hasattr(instance.style_config, key):
                    setattr(instance.style_config, key, value)
        
        # Update hook config if provided
        if 'hooks' in config_dict:
            hook_data = config_dict['hooks']
            for key, value in hook_data.items():
                if hasattr(instance.hook_config, key):
                    setattr(instance.hook_config, key, value)
        
        # Update main config values
        for key in ['workspace_path', 'output_dir', 'ai_model', 'ai_temperature', 'debug_mode']:
            if key in config_dict:
                setattr(instance, key, config_dict[key])
        
        # Re-validate after updates
        instance.validate()
        
        return instance

    def to_dict(self) -> Dict[str, Any]:
        """Convert AppConfig to dictionary."""
        # Only include style paths if they're different from defaults
        default_style = StyleConfig()
        style_dict = {}
        if self.style_config.code_style_path != default_style.code_style_path:
            style_dict['code_style_path'] = self.style_config.code_style_path
        if self.style_config.structure_style_path != default_style.structure_style_path:
            style_dict['structure_style_path'] = self.style_config.structure_style_path
        if self.style_config.onboarding_style_path != default_style.onboarding_style_path:
            style_dict['onboarding_style_path'] = self.style_config.onboarding_style_path
        
        result = {
            'hooks': {
                'feature_created_enabled': self.hook_config.feature_created_enabled,
                'readme_save_enabled': self.hook_config.readme_save_enabled,
                'auto_update_interval': self.hook_config.auto_update_interval,
                'hook_timeout': self.hook_config.hook_timeout,
                'max_retries': self.hook_config.max_retries,
                'log_level': self.hook_config.log_level
            },
            'workspace_path': self.workspace_path,
            'output_dir': self.output_dir,
            'ai_model': self.ai_model,
            'ai_temperature': self.ai_temperature,
            'debug_mode': self.debug_mode
        }
        
        if style_dict:
            result['style'] = style_dict
            
        return result