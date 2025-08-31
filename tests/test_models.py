"""Unit tests for SpecOps data models."""

import pytest
from src.models import (
    RepositoryAnalysis, Concept, SetupStep, CodeExample, Dependency,
    TaskSuggestion, FAQPair, QuickStartGuide, FeatureAnalysis,
    StyleConfig, HookConfig, AppConfig, ValidationError
)


class TestConcept:
    """Test cases for Concept data model."""

    def test_valid_concept_creation(self):
        """Test creating a valid concept."""
        concept = Concept(
            name="Authentication",
            description="User authentication system",
            importance=8,
            related_files=["auth.py", "login.py"],
            prerequisites=["database", "encryption"]
        )
        assert concept.name == "Authentication"
        assert concept.importance == 8
        assert len(concept.related_files) == 2

    def test_concept_validation_empty_name(self):
        """Test concept validation with empty name."""
        with pytest.raises(ValidationError, match="name must be a non-empty string"):
            Concept(
                name="",
                description="Valid description",
                importance=5
            )

    def test_concept_validation_invalid_importance(self):
        """Test concept validation with invalid importance."""
        with pytest.raises(ValidationError, match="importance must be an integer between 1 and 10"):
            Concept(
                name="Valid Name",
                description="Valid description",
                importance=15
            )

    def test_concept_validation_invalid_related_files(self):
        """Test concept validation with invalid related files."""
        with pytest.raises(ValidationError, match="all related_files must be strings"):
            Concept(
                name="Valid Name",
                description="Valid description",
                importance=5,
                related_files=["valid.py", 123]
            )


class TestSetupStep:
    """Test cases for SetupStep data model."""

    def test_valid_setup_step_creation(self):
        """Test creating a valid setup step."""
        step = SetupStep(
            title="Install Dependencies",
            description="Install required Python packages",
            commands=["pip install -r requirements.txt"],
            prerequisites=["Python 3.8+"],
            order=1
        )
        assert step.title == "Install Dependencies"
        assert step.order == 1
        assert len(step.commands) == 1

    def test_setup_step_validation_empty_title(self):
        """Test setup step validation with empty title."""
        with pytest.raises(ValidationError, match="title must be a non-empty string"):
            SetupStep(
                title="",
                description="Valid description"
            )

    def test_setup_step_validation_negative_order(self):
        """Test setup step validation with negative order."""
        with pytest.raises(ValidationError, match="order must be a non-negative integer"):
            SetupStep(
                title="Valid Title",
                description="Valid description",
                order=-1
            )


class TestCodeExample:
    """Test cases for CodeExample data model."""

    def test_valid_code_example_creation(self):
        """Test creating a valid code example."""
        example = CodeExample(
            title="Hello World Function",
            code="def hello_world():\n    return 'Hello, World!'",
            language="python",
            description="Simple greeting function",
            file_path="examples/hello.py"
        )
        assert example.title == "Hello World Function"
        assert example.language == "python"
        assert "Hello, World!" in example.code

    def test_code_example_validation_empty_code(self):
        """Test code example validation with empty code."""
        with pytest.raises(ValidationError, match="code must be a non-empty string"):
            CodeExample(
                title="Valid Title",
                code="",
                language="python",
                description="Valid description",
                file_path="valid/path.py"
            )


class TestDependency:
    """Test cases for Dependency data model."""

    def test_valid_dependency_creation(self):
        """Test creating a valid dependency."""
        dep = Dependency(
            name="requests",
            version="2.28.0",
            type="runtime",
            description="HTTP library for Python"
        )
        assert dep.name == "requests"
        assert dep.version == "2.28.0"
        assert dep.type == "runtime"

    def test_dependency_validation_invalid_type(self):
        """Test dependency validation with invalid type."""
        with pytest.raises(ValidationError, match="type must be one of"):
            Dependency(
                name="valid-package",
                type="invalid_type"
            )

    def test_dependency_validation_invalid_version_format(self):
        """Test dependency validation with invalid version format."""
        with pytest.raises(ValidationError, match="version format is invalid"):
            Dependency(
                name="valid-package",
                version="invalid version format!"
            )


class TestTaskSuggestion:
    """Test cases for TaskSuggestion data model."""

    def test_valid_task_suggestion_creation(self):
        """Test creating a valid task suggestion."""
        task = TaskSuggestion(
            title="Set up development environment",
            description="Configure local development environment",
            acceptance_criteria=["Python 3.8+ installed", "Dependencies installed"],
            prerequisites=["Git installed"],
            estimated_time=30,
            difficulty="medium"
        )
        assert task.title == "Set up development environment"
        assert task.estimated_time == 30
        assert len(task.acceptance_criteria) == 2

    def test_task_suggestion_validation_invalid_difficulty(self):
        """Test task suggestion validation with invalid difficulty."""
        with pytest.raises(ValidationError, match="difficulty must be one of"):
            TaskSuggestion(
                title="Valid Title",
                description="Valid description",
                difficulty="impossible"
            )

    def test_task_suggestion_validation_negative_time(self):
        """Test task suggestion validation with negative estimated time."""
        with pytest.raises(ValidationError, match="estimated_time must be a positive integer"):
            TaskSuggestion(
                title="Valid Title",
                description="Valid description",
                estimated_time=-10
            )

    def test_task_suggestion_validation_empty_acceptance_criteria(self):
        """Test task suggestion validation with empty acceptance criteria."""
        with pytest.raises(ValidationError, match="all acceptance_criteria must be non-empty strings"):
            TaskSuggestion(
                title="Valid Title",
                description="Valid description",
                acceptance_criteria=["Valid criteria", ""]
            )


class TestFAQPair:
    """Test cases for FAQPair data model."""

    def test_valid_faq_pair_creation(self):
        """Test creating a valid FAQ pair."""
        faq = FAQPair(
            question="How do I install the package?",
            answer="Run pip install specops",
            category="installation",
            source_files=["README.md"],
            confidence=0.9
        )
        assert faq.question == "How do I install the package?"
        assert faq.confidence == 0.9
        assert faq.category == "installation"

    def test_faq_pair_auto_fix_question_mark(self):
        """Test FAQ pair auto-fixes missing question mark."""
        faq = FAQPair(
            question="How do I install the package",
            answer="Run pip install specops"
        )
        assert faq.question == "How do I install the package?"

    def test_faq_pair_validation_invalid_confidence(self):
        """Test FAQ pair validation with invalid confidence."""
        with pytest.raises(ValidationError, match="confidence must be a number between 0.0 and 1.0"):
            FAQPair(
                question="Valid question?",
                answer="Valid answer",
                confidence=1.5
            )

    def test_faq_pair_validation_empty_answer(self):
        """Test FAQ pair validation with empty answer."""
        with pytest.raises(ValidationError, match="answer must be a non-empty string"):
            FAQPair(
                question="Valid question?",
                answer=""
            )


class TestQuickStartGuide:
    """Test cases for QuickStartGuide data model."""

    def test_valid_quick_start_guide_creation(self):
        """Test creating a valid quick start guide."""
        guide = QuickStartGuide(
            prerequisites=["Python 3.8+", "Git"],
            setup_steps=["Clone repository", "Install dependencies"],
            basic_usage=["Run python main.py", "Check output"],
            next_steps=["Read documentation", "Try examples"]
        )
        assert len(guide.prerequisites) == 2
        assert len(guide.setup_steps) == 2
        assert not guide.is_empty()

    def test_quick_start_guide_empty_check(self):
        """Test quick start guide empty check."""
        empty_guide = QuickStartGuide()
        assert empty_guide.is_empty()

        non_empty_guide = QuickStartGuide(prerequisites=["Python"])
        assert not non_empty_guide.is_empty()

    def test_quick_start_guide_validation_empty_steps(self):
        """Test quick start guide validation with empty steps."""
        with pytest.raises(ValidationError, match="all setup_steps must be non-empty strings"):
            QuickStartGuide(
                setup_steps=["Valid step", ""]
            )


class TestFeatureAnalysis:
    """Test cases for FeatureAnalysis data model."""

    def test_valid_feature_analysis_creation(self):
        """Test creating a valid feature analysis."""
        analysis = FeatureAnalysis(
            feature_path="features/auth.py",
            functions=["login", "logout", "authenticate"],
            classes=["User", "AuthManager"],
            tests=["test_login", "test_logout"],
            documentation="Authentication module documentation",
            complexity="medium"
        )
        assert analysis.feature_path == "features/auth.py"
        assert len(analysis.functions) == 3
        assert len(analysis.classes) == 2

    def test_feature_analysis_validation_invalid_complexity(self):
        """Test feature analysis validation with invalid complexity."""
        with pytest.raises(ValidationError, match="complexity must be one of"):
            FeatureAnalysis(
                feature_path="valid/path.py",
                complexity="impossible"
            )

    def test_feature_analysis_validation_empty_path(self):
        """Test feature analysis validation with empty path."""
        with pytest.raises(ValidationError, match="feature_path must be a non-empty string"):
            FeatureAnalysis(feature_path="")


class TestRepositoryAnalysis:
    """Test cases for RepositoryAnalysis data model."""

    def test_valid_repository_analysis_creation(self):
        """Test creating a valid repository analysis."""
        concept = Concept(
            name="Test Concept",
            description="Test description",
            importance=5
        )
        step = SetupStep(
            title="Test Step",
            description="Test step description"
        )
        
        analysis = RepositoryAnalysis(
            concepts=[concept],
            setup_steps=[step],
            code_examples=[],
            file_structure={"src": {"main.py": "file"}},
            dependencies=[]
        )
        assert len(analysis.concepts) == 1
        assert len(analysis.setup_steps) == 1
        assert isinstance(analysis.file_structure, dict)

    def test_repository_analysis_validation_invalid_types(self):
        """Test repository analysis validation with invalid types."""
        with pytest.raises(ValidationError, match="concepts must be a list"):
            RepositoryAnalysis(concepts="not a list")

    def test_repository_analysis_nested_validation(self):
        """Test repository analysis validates nested objects."""
        invalid_concept = Concept.__new__(Concept)  # Create without validation
        invalid_concept.name = ""  # Invalid name
        invalid_concept.description = "Valid"
        invalid_concept.importance = 5
        invalid_concept.related_files = []
        invalid_concept.prerequisites = []
        
        with pytest.raises(ValidationError):
            RepositoryAnalysis(concepts=[invalid_concept])


class TestStyleConfig:
    """Test cases for StyleConfig data model."""

    def test_valid_style_config_creation(self):
        """Test creating a valid style configuration."""
        config = StyleConfig(
            code_style_path='.kiro/steering/code-style.md',
            structure_style_path='.kiro/steering/structure.md',
            onboarding_style_path='.kiro/steering/onboarding-style.md'
        )
        assert config.code_style_path == '.kiro/steering/code-style.md'
        assert config.code_style_content == ''

    def test_style_config_load_content_file_not_found(self):
        """Test style config handles missing files gracefully."""
        config = StyleConfig(
            code_style_path='nonexistent/path.md',
            structure_style_path='nonexistent/path2.md',
            onboarding_style_path='nonexistent/path3.md'
        )
        config.load_content()
        assert "Default Code Style" in config.code_style_content
        assert "Default Structure" in config.structure_style_content
        assert "Default Onboarding Style" in config.onboarding_style_content

    def test_style_config_get_rules(self):
        """Test extracting rules from style content."""
        config = StyleConfig()
        config.code_style_content = "# Code Style\n- Rule 1\n- Rule 2\nNot a rule"
        rules = config.get_code_style_rules()
        assert len(rules) == 2
        assert "Rule 1" in rules
        assert "Rule 2" in rules

    def test_style_config_validation_invalid_path_type(self):
        """Test style config validation with invalid path type."""
        with pytest.raises(ValidationError, match="code_style_path must be a string"):
            StyleConfig(code_style_path=123)


class TestHookConfig:
    """Test cases for HookConfig data model."""

    def test_valid_hook_config_creation(self):
        """Test creating a valid hook configuration."""
        config = HookConfig(
            feature_created_enabled=True,
            readme_save_enabled=False,
            auto_update_interval=60,
            hook_timeout=45,
            max_retries=5,
            log_level='DEBUG'
        )
        assert config.feature_created_enabled is True
        assert config.readme_save_enabled is False
        assert config.auto_update_interval == 60

    def test_hook_config_is_hook_enabled(self):
        """Test hook enabled checking."""
        config = HookConfig(
            feature_created_enabled=True,
            readme_save_enabled=False
        )
        assert config.is_hook_enabled('feature_created') is True
        assert config.is_hook_enabled('readme_save') is False
        assert config.is_hook_enabled('unknown_hook') is False

    def test_hook_config_get_retry_config(self):
        """Test getting retry configuration."""
        config = HookConfig(max_retries=3, hook_timeout=30)
        retry_config = config.get_retry_config()
        assert retry_config['max_retries'] == 3
        assert retry_config['timeout'] == 30

    def test_hook_config_validation_invalid_log_level(self):
        """Test hook config validation with invalid log level."""
        with pytest.raises(ValidationError, match="log_level must be one of"):
            HookConfig(log_level='INVALID')

    def test_hook_config_validation_negative_interval(self):
        """Test hook config validation with negative interval."""
        with pytest.raises(ValidationError, match="auto_update_interval must be a non-negative integer"):
            HookConfig(auto_update_interval=-1)

    def test_hook_config_validation_invalid_timeout(self):
        """Test hook config validation with invalid timeout."""
        with pytest.raises(ValidationError, match="hook_timeout must be a positive integer"):
            HookConfig(hook_timeout=0)


class TestAppConfig:
    """Test cases for AppConfig data model."""

    def test_valid_app_config_creation(self):
        """Test creating a valid application configuration."""
        style_config = StyleConfig()
        hook_config = HookConfig()
        config = AppConfig(
            style_config=style_config,
            hook_config=hook_config,
            workspace_path='/path/to/workspace',
            ai_model='gpt-4',
            ai_temperature=0.5,
            debug_mode=True
        )
        assert config.workspace_path == '/path/to/workspace'
        assert config.ai_model == 'gpt-4'
        assert config.debug_mode is True

    def test_app_config_from_dict(self):
        """Test creating AppConfig from dictionary."""
        config_dict = {
            'style': {
                'code_style_path': 'custom/code.md'
            },
            'hooks': {
                'feature_created_enabled': False,
                'log_level': 'ERROR'
            },
            'workspace_path': '/custom/path',
            'ai_model': 'gpt-4',
            'ai_temperature': 0.3,
            'debug_mode': True
        }
        config = AppConfig.from_dict(config_dict)
        assert config.workspace_path == '/custom/path'
        assert config.ai_model == 'gpt-4'
        assert config.style_config.code_style_path == 'custom/code.md'
        assert config.hook_config.feature_created_enabled is False
        assert config.hook_config.log_level == 'ERROR'

    def test_app_config_to_dict(self):
        """Test converting AppConfig to dictionary."""
        config = AppConfig(
            workspace_path='/test/path',
            ai_model='gpt-3.5-turbo',
            debug_mode=True
        )
        config_dict = config.to_dict()
        assert config_dict['workspace_path'] == '/test/path'
        assert config_dict['ai_model'] == 'gpt-3.5-turbo'
        assert config_dict['debug_mode'] is True
        assert 'style' in config_dict
        assert 'hooks' in config_dict

    def test_app_config_validation_invalid_temperature(self):
        """Test app config validation with invalid AI temperature."""
        with pytest.raises(ValidationError, match="ai_temperature must be a number between 0.0 and 2.0"):
            AppConfig(ai_temperature=3.0)

    def test_app_config_validation_invalid_workspace_path(self):
        """Test app config validation with invalid workspace path."""
        with pytest.raises(ValidationError, match="workspace_path must be a string"):
            AppConfig(workspace_path=123)

    def test_app_config_nested_validation(self):
        """Test app config validates nested configurations."""
        invalid_hook_config = HookConfig.__new__(HookConfig)
        invalid_hook_config.feature_created_enabled = "not a boolean"
        invalid_hook_config.readme_save_enabled = True
        invalid_hook_config.auto_update_interval = 0
        invalid_hook_config.hook_timeout = 30
        invalid_hook_config.max_retries = 3
        invalid_hook_config.log_level = 'INFO'
        
        with pytest.raises(ValidationError):
            AppConfig(hook_config=invalid_hook_config)


class TestValidationErrorHandling:
    """Test cases for validation error handling."""

    def test_validation_error_inheritance(self):
        """Test that ValidationError is properly inherited."""
        error = ValidationError("Test error message")
        assert isinstance(error, Exception)
        assert str(error) == "Test error message"

    def test_multiple_validation_errors(self):
        """Test handling multiple validation scenarios."""
        # Test that first validation error is raised
        with pytest.raises(ValidationError) as exc_info:
            Concept(
                name="",  # This will fail first
                description="",  # This would also fail
                importance=15  # This would also fail
            )
        assert "name must be a non-empty string" in str(exc_info.value)