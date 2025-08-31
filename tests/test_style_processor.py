"""Tests for style processing and compliance system."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src.utils.style_processor import (
    StyleProcessor,
    StyleViolation,
    StyleValidationResult
)
from src.models import StyleConfig


class TestStyleViolation:
    """Test StyleViolation data class."""
    
    def test_style_violation_creation(self):
        """Test basic StyleViolation creation."""
        violation = StyleViolation(
            rule="test_rule",
            description="Test violation",
            line_number=10,
            severity="error",
            suggestion="Fix this"
        )
        
        assert violation.rule == "test_rule"
        assert violation.description == "Test violation"
        assert violation.line_number == 10
        assert violation.severity == "error"
        assert violation.suggestion == "Fix this"
    
    def test_style_violation_defaults(self):
        """Test StyleViolation with default values."""
        violation = StyleViolation(
            rule="test_rule",
            description="Test violation"
        )
        
        assert violation.line_number is None
        assert violation.severity == "warning"
        assert violation.suggestion is None


class TestStyleValidationResult:
    """Test StyleValidationResult data class."""
    
    def test_validation_result_creation(self):
        """Test StyleValidationResult creation."""
        violations = [
            StyleViolation("rule1", "Description 1"),
            StyleViolation("rule2", "Description 2")
        ]
        
        result = StyleValidationResult(
            is_compliant=False,
            violations=violations,
            corrected_content="Fixed content"
        )
        
        assert result.is_compliant is False
        assert len(result.violations) == 2
        assert result.corrected_content == "Fixed content"
    
    def test_validation_result_defaults(self):
        """Test StyleValidationResult with defaults."""
        result = StyleValidationResult(
            is_compliant=True,
            violations=[]
        )
        
        assert result.is_compliant is True
        assert result.violations == []
        assert result.corrected_content is None


class TestStyleProcessor:
    """Test StyleProcessor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock style config
        self.mock_config = StyleConfig()
        self.mock_config.code_style_content = """# Code Style
- Python 3.10+
- Use snake_case for functions and variables
- Use PascalCase for classes
- Docstrings required for all functions and classes
- Limit line length to 88 characters (black standard)
- Apply black and isort formatting for consistency"""
        
        self.mock_config.structure_style_content = """# Project Structure
- src/        : core implementation modules
- features/   : feature stubs created to trigger hooks
- tests/      : pytest unit tests
- docs/       : documentation, demo GIFs/screenshots
- .kiro/      : Kiro steering, specs, and hooks"""
        
        self.mock_config.onboarding_style_content = """# Onboarding Tone
- Use friendly, concise language
- Tasks are actionable and numbered
- Include examples where relevant
- Highlight important points in bold
- Keep instructions easy to follow for new contributors"""
        
        self.processor = StyleProcessor(self.mock_config)
    
    def test_style_processor_initialization(self):
        """Test StyleProcessor initialization."""
        processor = StyleProcessor()
        
        assert isinstance(processor.style_config, StyleConfig)
        assert processor._code_rules_cache is None
        assert processor._structure_rules_cache is None
        assert processor._onboarding_rules_cache is None
    
    def test_style_processor_with_config(self):
        """Test StyleProcessor initialization with custom config."""
        config = StyleConfig()
        processor = StyleProcessor(config)
        
        assert processor.style_config is config
    
    def test_load_steering_guidelines(self):
        """Test loading steering guidelines."""
        with patch.object(self.processor.style_config, 'load_content') as mock_load:
            self.processor.load_steering_guidelines()
            
            mock_load.assert_called_once()
            # Caches should be cleared
            assert self.processor._code_rules_cache is None
            assert self.processor._structure_rules_cache is None
            assert self.processor._onboarding_rules_cache is None
    
    def test_get_code_style_rules(self):
        """Test getting code style rules."""
        rules = self.processor.get_code_style_rules()
        
        expected_rules = [
            "Python 3.10+",
            "Use snake_case for functions and variables",
            "Use PascalCase for classes",
            "Docstrings required for all functions and classes",
            "Limit line length to 88 characters (black standard)",
            "Apply black and isort formatting for consistency"
        ]
        
        assert rules == expected_rules
        # Should cache the result
        assert self.processor._code_rules_cache == expected_rules
    
    def test_get_structure_rules(self):
        """Test getting structure rules."""
        rules = self.processor.get_structure_rules()
        
        expected_rules = [
            "src/        : core implementation modules",
            "features/   : feature stubs created to trigger hooks",
            "tests/      : pytest unit tests",
            "docs/       : documentation, demo GIFs/screenshots",
            ".kiro/      : Kiro steering, specs, and hooks"
        ]
        
        assert rules == expected_rules
        assert self.processor._structure_rules_cache == expected_rules
    
    def test_get_onboarding_rules(self):
        """Test getting onboarding style rules."""
        rules = self.processor.get_onboarding_rules()
        
        expected_rules = [
            "Use friendly, concise language",
            "Tasks are actionable and numbered",
            "Include examples where relevant",
            "Highlight important points in bold",
            "Keep instructions easy to follow for new contributors"
        ]
        
        assert rules == expected_rules
        assert self.processor._onboarding_rules_cache == expected_rules


class TestCodeStyleValidation:
    """Test code style validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StyleProcessor()
    
    def test_validate_code_style_compliant(self):
        """Test validation of compliant code."""
        code = '''def hello_world(name: str = "World") -> str:
    """Simple greeting function for demonstration."""
    return f"Hello, {name}!"


class GreetingService:
    """Service for handling greetings."""
    
    def greet(self, name: str) -> str:
        """Generate a greeting message."""
        return hello_world(name)
'''
        
        result = self.processor.validate_code_style(code)
        
        assert result.is_compliant is True
        assert len(result.violations) == 0
        assert result.corrected_content is None
    
    def test_validate_code_style_line_length_violation(self):
        """Test validation of code with line length violations."""
        code = 'def very_long_function_name_that_exceeds_the_maximum_line_length_limit_of_eighty_eight_characters():'
        
        result = self.processor.validate_code_style(code)
        
        assert result.is_compliant is True  # Line length is warning, not error
        # Should have both line length and docstring violations
        line_length_violations = [v for v in result.violations if v.rule == "line_length"]
        assert len(line_length_violations) == 1
        assert line_length_violations[0].severity == "warning"
        assert line_length_violations[0].line_number == 1
    
    def test_validate_code_style_snake_case_violation(self):
        """Test validation of code with snake_case violations."""
        code = '''def HelloWorld():
    pass

CamelCaseVariable = "test"
'''
        
        result = self.processor.validate_code_style(code)
        
        assert result.is_compliant is False  # snake_case violations are errors
        violations = [v for v in result.violations if v.rule == "snake_case"]
        assert len(violations) == 2
        assert all(v.severity == "error" for v in violations)
    
    def test_validate_code_style_pascal_case_violation(self):
        """Test validation of code with PascalCase violations."""
        code = '''class myClass:
    pass

class another_class:
    pass
'''
        
        result = self.processor.validate_code_style(code)
        
        assert result.is_compliant is False  # PascalCase violations are errors
        violations = [v for v in result.violations if v.rule == "pascal_case"]
        assert len(violations) == 2
        assert all(v.severity == "error" for v in violations)
    
    def test_validate_code_style_missing_docstring(self):
        """Test validation of code with missing docstrings."""
        code = '''def hello_world():
    return "Hello, World!"

class TestClass:
    def method(self):
        pass
'''
        
        result = self.processor.validate_code_style(code)
        
        assert result.is_compliant is True  # Missing docstrings are warnings
        violations = [v for v in result.violations if v.rule == "docstring_required"]
        assert len(violations) == 3  # function, class, and method
        assert all(v.severity == "warning" for v in violations)
    
    def test_validate_code_style_with_docstrings(self):
        """Test validation of code with proper docstrings."""
        code = '''def hello_world():
    """Return a greeting message."""
    return "Hello, World!"

class TestClass:
    """A test class."""
    
    def method(self):
        """A test method."""
        pass
'''
        
        result = self.processor.validate_code_style(code)
        
        # Should not have docstring violations
        docstring_violations = [v for v in result.violations if v.rule == "docstring_required"]
        assert len(docstring_violations) == 0


class TestStructureValidation:
    """Test structure validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StyleProcessor()
    
    def test_validate_structure_compliant_src_file(self):
        """Test validation of properly placed src file."""
        result = self.processor.validate_structure_compliance("src/utils/helper.py")
        
        assert result.is_compliant is True
        # May have warning about __init__.py but should be compliant
        error_violations = [v for v in result.violations if v.severity == "error"]
        assert len(error_violations) == 0
    
    def test_validate_structure_compliant_test_file(self):
        """Test validation of properly placed test file."""
        result = self.processor.validate_structure_compliance("tests/test_helper.py")
        
        assert result.is_compliant is True
        # Should not have test structure violations since it's in tests/
        test_violations = [v for v in result.violations if v.rule == "test_structure"]
        assert len(test_violations) == 0
    
    def test_validate_structure_compliant_feature_file(self):
        """Test validation of properly placed feature file."""
        result = self.processor.validate_structure_compliance("features/hello_world.py")
        
        assert result.is_compliant is True
        assert len(result.violations) == 0
    
    def test_validate_structure_misplaced_src_file(self):
        """Test validation of misplaced src file."""
        result = self.processor.validate_structure_compliance("utils/helper.py")
        
        # Should have violation for src structure
        src_violations = [v for v in result.violations if v.rule == "src_structure"]
        assert len(src_violations) == 1
        assert src_violations[0].severity == "error"
    
    def test_validate_structure_misplaced_test_file(self):
        """Test validation of misplaced test file."""
        result = self.processor.validate_structure_compliance("src/test_helper.py")
        
        # Should have violation for test structure
        test_violations = [v for v in result.violations if v.rule == "test_structure"]
        assert len(test_violations) == 1
        assert test_violations[0].severity == "error"
    
    def test_validate_structure_misplaced_feature_file(self):
        """Test validation of misplaced feature file."""
        result = self.processor.validate_structure_compliance("src/feature_hello.py")
        
        # Should have violation for feature structure
        feature_violations = [v for v in result.violations if v.rule == "feature_structure"]
        assert len(feature_violations) == 1
        assert feature_violations[0].severity == "warning"
    
    def test_validate_structure_missing_init_file(self):
        """Test validation of missing __init__.py files."""
        # This test is more conceptual since we can't easily mock file system
        result = self.processor.validate_structure_compliance("src/new_module/helper.py")
        
        # Should have violation for missing __init__.py
        init_violations = [v for v in result.violations if v.rule == "init_file_required"]
        assert len(init_violations) == 1
        assert init_violations[0].severity == "warning"
    
    def test_validate_structure_non_python_file(self):
        """Test validation of non-Python files."""
        result = self.processor.validate_structure_compliance("README.md")
        
        assert result.is_compliant is True
        assert len(result.violations) == 0


class TestOnboardingStyleValidation:
    """Test onboarding style validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StyleProcessor()
    
    def test_validate_onboarding_style_compliant(self):
        """Test validation of compliant onboarding content."""
        content = '''# Getting Started

Welcome to our project! Here are the **important** steps to get started:

1. Clone the repository
2. Install dependencies
3. Run the tests

Please follow these instructions carefully.
'''
        
        result = self.processor.validate_onboarding_style(content)
        
        assert result.is_compliant is True
        assert len(result.violations) == 0
    
    def test_validate_onboarding_style_assumptive_language(self):
        """Test validation of content with assumptive language."""
        content = '''# Getting Started

Obviously, you need to install Python first. 
Clearly, this is the most important step.
Simply run the command below.
Just follow these steps.
'''
        
        result = self.processor.validate_onboarding_style(content)
        
        # Should be compliant since violations are warnings, not errors
        assert result.is_compliant is True
        violations = [v for v in result.violations if v.rule == "friendly_language"]
        assert len(violations) == 4  # obviously, clearly, simply, just
        assert all(v.severity == "warning" for v in violations)
    
    def test_validate_onboarding_style_tasks_numbered(self):
        """Test validation of task numbering."""
        content = '''# Tasks

- [ ] 1. Create the database
- [ ] 2. Set up authentication
- [ ] Install dependencies
- [ ] Run tests
'''
        
        result = self.processor.validate_onboarding_style(content, "tasks")
        
        # Should have violations for unnumbered tasks
        violations = [v for v in result.violations if v.rule == "numbered_tasks"]
        assert len(violations) == 2  # Two unnumbered tasks
        assert all(v.severity == "info" for v in violations)
    
    def test_validate_onboarding_style_actionable_tasks(self):
        """Test validation of actionable task language."""
        content = '''# Tasks

- [ ] 1. Create the database
- [ ] 2. authentication setup
- [ ] 3. Install dependencies
- [ ] 4. testing phase
'''
        
        result = self.processor.validate_onboarding_style(content, "tasks")
        
        # Should have violations for non-actionable tasks
        violations = [v for v in result.violations if v.rule == "actionable_tasks"]
        assert len(violations) == 2  # "authentication setup" and "testing phase"
        assert all(v.severity == "info" for v in violations)
    
    def test_validate_onboarding_style_highlight_important(self):
        """Test validation of important point highlighting."""
        content = '''# Instructions

This is important information that should be highlighted.
Note: This is also important.
Warning: Be careful with this step.
'''
        
        result = self.processor.validate_onboarding_style(content)
        
        # Should suggest highlighting important points
        violations = [v for v in result.violations if v.rule == "highlight_important"]
        assert len(violations) == 3
        assert all(v.severity == "info" for v in violations)
        
        # Should provide corrected content
        assert result.corrected_content is not None
        assert "**important**" in result.corrected_content
        assert "**Note**" in result.corrected_content
        assert "**Warning**" in result.corrected_content
    
    def test_validate_onboarding_style_already_highlighted(self):
        """Test validation of already highlighted content."""
        content = '''# Instructions

This is **important** information.
**Note**: This is also important.
**Warning**: Be careful with this step.
'''
        
        result = self.processor.validate_onboarding_style(content)
        
        # Should not have highlighting violations
        violations = [v for v in result.violations if v.rule == "highlight_important"]
        assert len(violations) == 0


class TestStyleCorrections:
    """Test automatic style corrections."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StyleProcessor()
    
    def test_apply_style_corrections_python(self):
        """Test applying corrections to Python code."""
        code = '''def HelloWorld():
    return "Hello, World!"
'''
        
        corrected = self.processor.apply_style_corrections(code, "python")
        
        # Should return corrected content (though actual corrections depend on validation)
        assert isinstance(corrected, str)
    
    def test_apply_style_corrections_markdown(self):
        """Test applying corrections to markdown content."""
        content = '''# Getting Started

This is important information.
Note: Follow these steps.
'''
        
        corrected = self.processor.apply_style_corrections(content, "markdown")
        
        # Should highlight important points
        assert "**important**" in corrected
        assert "**Note**" in corrected
    
    def test_apply_style_corrections_tasks(self):
        """Test applying corrections to task content."""
        content = '''# Tasks

- [ ] Create database
- [ ] authentication setup
'''
        
        corrected = self.processor.apply_style_corrections(content, "tasks")
        
        # Should return corrected content
        assert isinstance(corrected, str)
    
    def test_apply_style_corrections_no_changes(self):
        """Test applying corrections when no changes needed."""
        content = '''# Getting Started

This is **important** information.
**Note**: Follow these steps.
'''
        
        corrected = self.processor.apply_style_corrections(content, "markdown")
        
        # Should return original content if no corrections needed
        assert corrected == content


class TestComprehensiveValidation:
    """Test comprehensive validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StyleProcessor()
    
    def test_validate_all_styles_python_file(self):
        """Test comprehensive validation of Python file."""
        code = '''def HelloWorld():
    return "Hello, World!"

class myClass:
    def method(self):
        pass
'''
        
        result = self.processor.validate_all_styles(
            code, 
            "python", 
            "wrong_location/test.py"
        )
        
        assert result.is_compliant is False
        
        # Should have violations from multiple categories
        rule_types = {v.rule for v in result.violations}
        assert "snake_case" in rule_types  # Code style
        assert "pascal_case" in rule_types  # Code style
        # Structure violations depend on the specific path logic
    
    def test_validate_all_styles_markdown_file(self):
        """Test comprehensive validation of markdown file."""
        content = '''# Getting Started

Obviously, you need to install Python.
This is important information.
'''
        
        result = self.processor.validate_all_styles(content, "markdown")
        
        # Should be compliant since violations are warnings/info, not errors
        assert result.is_compliant is True
        
        # Should have onboarding style violations
        rule_types = {v.rule for v in result.violations}
        assert "friendly_language" in rule_types
        assert "highlight_important" in rule_types
    
    def test_validate_all_styles_compliant_content(self):
        """Test comprehensive validation of compliant content."""
        content = '''# Getting Started

Welcome to our project! Here are the **important** steps:

1. Clone the repository
2. Install dependencies
3. Run the tests
'''
        
        result = self.processor.validate_all_styles(content, "markdown")
        
        assert result.is_compliant is True
        assert len(result.violations) == 0
        assert result.corrected_content is None


class TestStyleSummaryAndReporting:
    """Test style summary and reporting functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StyleProcessor()
    
    def test_get_style_summary(self):
        """Test getting style summary."""
        summary = self.processor.get_style_summary()
        
        assert "code_style_rules" in summary
        assert "structure_rules" in summary
        assert "onboarding_rules" in summary
        assert "config_paths" in summary
        
        assert isinstance(summary["code_style_rules"], list)
        assert isinstance(summary["structure_rules"], list)
        assert isinstance(summary["onboarding_rules"], list)
        assert isinstance(summary["config_paths"], dict)
    
    def test_format_violations_report_no_violations(self):
        """Test formatting report with no violations."""
        violations = []
        
        report = self.processor.format_violations_report(violations)
        
        assert "✅ No style violations found." in report
    
    def test_format_violations_report_with_violations(self):
        """Test formatting report with violations."""
        violations = [
            StyleViolation("rule1", "Error description", 10, "error", "Fix this"),
            StyleViolation("rule2", "Warning description", 20, "warning", "Consider this"),
            StyleViolation("rule3", "Info description", 30, "info", "Note this")
        ]
        
        report = self.processor.format_violations_report(violations)
        
        assert "📋 Style Validation Report" in report
        assert "Errors (1):" in report
        assert "Warnings (1):" in report
        assert "Info (1):" in report
        assert "rule1: Error description (line 10)" in report
        assert "💡 Fix this" in report
        assert "rule2: Warning description (line 20)" in report
        assert "💡 Consider this" in report
    
    def test_format_violations_report_grouped_by_severity(self):
        """Test that violations are properly grouped by severity."""
        violations = [
            StyleViolation("rule1", "Error 1", severity="error"),
            StyleViolation("rule2", "Error 2", severity="error"),
            StyleViolation("rule3", "Warning 1", severity="warning"),
            StyleViolation("rule4", "Info 1", severity="info"),
            StyleViolation("rule5", "Info 2", severity="info"),
        ]
        
        report = self.processor.format_violations_report(violations)
        
        assert "Errors (2):" in report
        assert "Warnings (1):" in report
        assert "Info (2):" in report


class TestStyleProcessorIntegration:
    """Test StyleProcessor integration scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StyleProcessor()
    
    def test_end_to_end_python_validation(self):
        """Test end-to-end Python code validation and correction."""
        code = '''def HelloWorld(name):
    return f"Hello, {name}!"

class myService:
    def greet(self, name):
        return HelloWorld(name)
'''
        
        # Validate
        result = self.processor.validate_all_styles(code, "python", "src/service.py")
        
        # Should have violations
        assert result.is_compliant is False
        assert len(result.violations) > 0
        
        # Apply corrections
        corrected = self.processor.apply_style_corrections(code, "python", "src/service.py")
        
        # Should return corrected content
        assert isinstance(corrected, str)
    
    def test_end_to_end_markdown_validation(self):
        """Test end-to-end markdown validation and correction."""
        content = '''# Setup Guide

Obviously, you need Python installed.
This is important: make sure you have the right version.

- [ ] Install Python
- [ ] setup virtual environment
- [ ] dependency installation
'''
        
        # Validate
        result = self.processor.validate_all_styles(content, "tasks")
        
        # Should be compliant since violations are warnings/info, not errors
        assert result.is_compliant is True
        assert len(result.violations) > 0
        
        # Apply corrections
        corrected = self.processor.apply_style_corrections(content, "tasks")
        
        # Should return corrected content
        assert isinstance(corrected, str)
        assert "**important**" in corrected
    
    def test_style_processor_with_custom_config(self):
        """Test StyleProcessor with custom configuration."""
        # Create custom config
        custom_config = StyleConfig()
        custom_config.code_style_content = "# Custom Code Style\n- Use tabs for indentation"
        custom_config.onboarding_style_content = "# Custom Onboarding\n- Be very formal"
        
        processor = StyleProcessor(custom_config)
        
        # Should use custom rules
        code_rules = processor.get_code_style_rules()
        onboarding_rules = processor.get_onboarding_rules()
        
        assert "Use tabs for indentation" in code_rules
        assert "Be very formal" in onboarding_rules
    
    @patch('builtins.open', new_callable=mock_open, read_data="# Mock Style\n- Mock rule")
    def test_style_processor_file_loading(self, mock_file):
        """Test StyleProcessor loading from actual files."""
        config = StyleConfig()
        processor = StyleProcessor(config)
        
        # Load guidelines (should read from mocked files)
        processor.load_steering_guidelines()
        
        # Should have loaded content
        rules = processor.get_code_style_rules()
        assert "Mock rule" in rules


if __name__ == "__main__":
    pytest.main([__file__])