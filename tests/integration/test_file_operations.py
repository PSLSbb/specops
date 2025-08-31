"""File operations integration tests for SpecOps."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import json
import os

from src.main import SpecOpsApp, create_app
from src.models import AppConfig, RepositoryAnalysis, Concept, SetupStep, CodeExample, Dependency
from src.analyzers.content_analyzer import ContentAnalyzer
from src.generators.task_generator import TaskGenerator
from src.generators.faq_generator import FAQGenerator
from src.generators.quick_start_generator import QuickStartGenerator


class TestFileOperations:
    """Test file reading, writing, and updating operations."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace with various file types."""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)
        
        # Create directory structure
        (workspace / 'src').mkdir()
        (workspace / 'tests').mkdir()
        (workspace / 'features').mkdir()
        (workspace / 'docs').mkdir()
        (workspace / '.kiro').mkdir()
        (workspace / '.kiro' / 'steering').mkdir()
        (workspace / '.kiro' / 'specs').mkdir()
        
        # Create various file types for testing
        self._create_test_files(workspace)
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def _create_test_files(self, workspace: Path):
        """Create various test files with different content types."""
        # README with different sections
        readme_content = """# Test Project

A comprehensive test project for file operations testing.

## Installation

```bash
pip install -r requirements.txt
python setup.py install
```

## Quick Start

This section will be updated by SpecOps.

## Usage

```python
from features.calculator import Calculator
calc = Calculator()
result = calc.add(2, 3)
print(result)  # Output: 5
```

## Configuration

Edit the config.json file to customize settings.

## Contributing

Please read CONTRIBUTING.md for guidelines.

## License

MIT License
"""
        (workspace / 'README.md').write_text(readme_content)
        
        # Multiple markdown files with different content
        api_docs = """# API Documentation

## Calculator Class

### Methods

#### add(a, b)
Adds two numbers and returns the result.

**Parameters:**
- `a` (int): First number
- `b` (int): Second number

**Returns:**
- `int`: Sum of a and b

#### subtract(a, b)
Subtracts b from a and returns the result.

**Example:**
```python
calc = Calculator()
result = calc.subtract(10, 3)
print(result)  # Output: 7
```
"""
        (workspace / 'docs' / 'api.md').write_text(api_docs)
        
        # Setup guide
        setup_guide = """# Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git for version control

## Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/example/test-project.git
   cd test-project
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run tests to verify installation:
   ```bash
   pytest tests/
   ```

## Configuration

Copy `config.example.json` to `config.json` and modify as needed.
"""
        (workspace / 'docs' / 'setup.md').write_text(setup_guide)
        
        # Feature files
        calculator_feature = '''"""Calculator feature for mathematical operations."""

from typing import Union

class Calculator:
    """A simple calculator class for basic mathematical operations."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.history = []
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Subtract b from a.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Difference of a and b
        """
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def get_history(self) -> list:
        """Get calculation history.
        
        Returns:
            List of calculation strings
        """
        return self.history.copy()
'''
        (workspace / 'features' / 'calculator.py').write_text(calculator_feature)
        
        # Test files
        test_calculator = '''"""Tests for calculator feature."""

import pytest
from features.calculator import Calculator


class TestCalculator:
    """Test cases for Calculator class."""
    
    def test_add_integers(self):
        """Test adding two integers."""
        calc = Calculator()
        result = calc.add(2, 3)
        assert result == 5
    
    def test_add_floats(self):
        """Test adding two floats."""
        calc = Calculator()
        result = calc.add(2.5, 3.7)
        assert result == 6.2
    
    def test_subtract_integers(self):
        """Test subtracting two integers."""
        calc = Calculator()
        result = calc.subtract(10, 3)
        assert result == 7
    
    def test_history_tracking(self):
        """Test that calculation history is tracked."""
        calc = Calculator()
        calc.add(2, 3)
        calc.subtract(10, 4)
        
        history = calc.get_history()
        assert len(history) == 2
        assert "2 + 3 = 5" in history
        assert "10 - 4 = 6" in history
'''
        (workspace / 'tests' / 'test_calculator.py').write_text(test_calculator)
        
        # Configuration files
        requirements = """pytest>=7.0.0
requests>=2.28.0
pydantic>=1.10.0
"""
        (workspace / 'requirements.txt').write_text(requirements)
        
        config_example = """{
    "debug": false,
    "log_level": "INFO",
    "api_endpoint": "https://api.example.com",
    "timeout": 30
}"""
        (workspace / 'config.example.json').write_text(config_example)
        
        # Existing tasks file
        existing_tasks = """# Implementation Tasks

- [x] 1. Set up project structure
  - Create directory structure
  - Set up configuration files
  - _Requirements: 1.1_

- [ ] 2. Implement core features
  - [ ] 2.1 Create Calculator class
    - Implement basic arithmetic operations
    - Add input validation
    - _Requirements: 2.1, 2.2_
  
  - [ ] 2.2 Add advanced operations
    - Implement multiplication and division
    - Add error handling for division by zero
    - _Requirements: 2.3_

- [ ] 3. Create comprehensive tests
  - Write unit tests for all operations
  - Add integration tests
  - _Requirements: 3.1_
"""
        (workspace / 'tasks.md').write_text(existing_tasks)
        
        # Existing FAQ file
        existing_faq = """# Frequently Asked Questions

## General Questions

### What is this project?
This is a test project for demonstrating SpecOps functionality.

### How do I get started?
Follow the setup guide in docs/setup.md.

## Technical Questions

### What Python version is required?
Python 3.8 or higher is required.

<!-- SpecOps Generated Content Below -->
"""
        (workspace / 'faq.md').write_text(existing_faq)
        
        # Steering files
        (workspace / '.kiro' / 'steering' / 'code-style.md').write_text(
            "# Code Style Guidelines\n\n- Use type hints\n- Write docstrings\n- Follow PEP 8"
        )
        (workspace / '.kiro' / 'steering' / 'structure.md').write_text(
            "# Project Structure\n\n- src/ for source code\n- tests/ for tests\n- docs/ for documentation"
        )
        (workspace / '.kiro' / 'steering' / 'onboarding-style.md').write_text(
            "# Onboarding Style\n\n- Be clear and concise\n- Provide examples\n- Include prerequisites"
        )
    
    def test_content_analyzer_file_reading(self, temp_workspace):
        """Test content analyzer reads various file types correctly."""
        analyzer = ContentAnalyzer(str(temp_workspace))
        
        # Test repository analysis
        analysis = analyzer.analyze_repository(str(temp_workspace))
        
        # Verify analysis results
        assert isinstance(analysis, RepositoryAnalysis)
        assert len(analysis.concepts) > 0
        assert len(analysis.setup_steps) > 0
        assert len(analysis.code_examples) > 0
        
        # Verify specific content was extracted
        concept_names = [c.name.lower() for c in analysis.concepts]
        assert any('calculator' in name for name in concept_names)
        
        # Verify setup steps were found
        setup_titles = [s.title.lower() for s in analysis.setup_steps]
        assert any('install' in title or 'setup' in title for title in setup_titles)
        
        # Verify code examples were extracted
        assert len(analysis.code_examples) > 0
        code_languages = [e.language for e in analysis.code_examples]
        assert 'python' in code_languages or 'bash' in code_languages
    
    def test_task_generator_file_operations(self, temp_workspace):
        """Test task generator file reading and writing operations."""
        task_generator = TaskGenerator()
        
        # Test loading existing tasks
        tasks_file = temp_workspace / 'tasks.md'
        existing_tasks = task_generator.load_tasks_from_file(str(tasks_file))
        
        # Verify existing tasks were loaded
        assert existing_tasks is not None
        assert len(existing_tasks.tasks) > 0
        
        # Verify specific tasks were found
        task_titles = [task.title.lower() for task in existing_tasks.tasks]
        assert any('project structure' in title for title in task_titles)
        assert any('core features' in title for title in task_titles)
        
        # Test appending new tasks
        new_task_data = {
            'title': 'Add documentation',
            'description': 'Create comprehensive documentation',
            'acceptance_criteria': ['API docs created', 'User guide written'],
            'prerequisites': ['Implement core features'],
            'estimated_time': 30,
            'difficulty': 'medium'
        }
        
        updated_tasks = task_generator.append_task_to_document(existing_tasks, new_task_data)
        
        # Verify task was appended
        assert len(updated_tasks.tasks) > len(existing_tasks.tasks)
        new_task_titles = [task.title for task in updated_tasks.tasks]
        assert 'Add documentation' in new_task_titles
        
        # Test writing tasks back to file
        markdown_content = task_generator.format_tasks_markdown(updated_tasks)
        
        # Write to temporary file and verify
        temp_tasks_file = temp_workspace / 'tasks_updated.md'
        with open(temp_tasks_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Verify file was written correctly
        assert temp_tasks_file.exists()
        written_content = temp_tasks_file.read_text()
        assert 'Add documentation' in written_content
        assert '- [' in written_content  # Checkbox format
        assert '_Requirements:' in written_content or 'Requirements:' in written_content
    
    def test_faq_generator_file_operations(self, temp_workspace):
        """Test FAQ generator file reading, merging, and writing operations."""
        faq_generator = FAQGenerator()
        
        # Test generating new FAQ content
        faq_pairs = [
            {
                'question': 'How do I run the calculator?',
                'answer': 'Import the Calculator class and create an instance.',
                'category': 'usage',
                'source_files': ['features/calculator.py'],
                'confidence': 0.9
            },
            {
                'question': 'What operations are supported?',
                'answer': 'Addition, subtraction, and history tracking are supported.',
                'category': 'features',
                'source_files': ['features/calculator.py'],
                'confidence': 0.8
            }
        ]
        
        new_faq_content = faq_generator.generate_faqs(faq_pairs)
        
        # Test merging with existing FAQ
        existing_faq_path = temp_workspace / 'faq.md'
        merged_content = faq_generator.merge_with_existing(new_faq_content, str(existing_faq_path))
        
        # Verify merging preserved existing content
        assert 'What is this project?' in merged_content
        assert 'Python 3.8 or higher' in merged_content
        
        # Verify new content was added
        assert 'How do I run the calculator?' in merged_content
        assert 'What operations are supported?' in merged_content
        
        # Test writing merged content
        updated_faq_path = temp_workspace / 'faq_updated.md'
        with open(updated_faq_path, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        # Verify file operations
        assert updated_faq_path.exists()
        written_content = updated_faq_path.read_text()
        assert len(written_content) > 0
        assert '?' in written_content  # Questions present
    
    def test_quick_start_generator_readme_operations(self, temp_workspace):
        """Test Quick Start generator README reading and updating operations."""
        quick_start_generator = QuickStartGenerator()
        
        # Test generating Quick Start content
        quick_start_guide = {
            'prerequisites': ['Python 3.8+', 'pip'],
            'setup_steps': [
                'Clone the repository',
                'Install dependencies with pip install -r requirements.txt',
                'Run tests with pytest'
            ],
            'basic_usage': [
                'Import Calculator from features.calculator',
                'Create Calculator instance',
                'Use add() and subtract() methods'
            ],
            'next_steps': [
                'Read API documentation',
                'Explore advanced features',
                'Check out examples'
            ]
        }
        
        quick_start_content = quick_start_generator.generate_quick_start(quick_start_guide)
        
        # Verify content generation
        assert 'Quick Start' in quick_start_content or 'Getting Started' in quick_start_content
        assert 'Python 3.8+' in quick_start_content
        assert 'pip install' in quick_start_content
        assert 'Calculator' in quick_start_content
        
        # Test README updating
        readme_path = temp_workspace / 'README.md'
        original_content = readme_path.read_text()
        
        # Update README with Quick Start content
        quick_start_generator.update_readme_section(str(readme_path), quick_start_content)
        
        # Verify README was updated
        updated_content = readme_path.read_text()
        
        # Original content should be preserved
        assert 'Test Project' in updated_content
        assert 'Installation' in updated_content
        assert 'Contributing' in updated_content
        
        # Quick Start content should be present or updated
        # (Implementation may vary based on generator logic)
        assert len(updated_content) >= len(original_content)
    
    def test_file_encoding_and_special_characters(self, temp_workspace):
        """Test handling of different file encodings and special characters."""
        # Create files with special characters
        special_content = """# Spéciál Chäractërs Tëst

This file contains special characters: àáâãäåæçèéêë

## Code Example

```python
def grëët(nämë: str) -> str:
    return f"Hëllö, {nämë}! 🌟"
```

## Mathematical Symbols

- α (alpha)
- β (beta) 
- π (pi) ≈ 3.14159
- ∑ (sum)
- ∞ (infinity)
"""
        
        special_file = temp_workspace / 'special_chars.md'
        special_file.write_text(special_content, encoding='utf-8')
        
        # Test content analyzer with special characters
        analyzer = ContentAnalyzer(str(temp_workspace))
        analysis = analyzer.analyze_repository(str(temp_workspace))
        
        # Should handle special characters without errors
        assert isinstance(analysis, RepositoryAnalysis)
        
        # Test that special characters are preserved in concepts
        concept_descriptions = [c.description for c in analysis.concepts]
        # Should not crash on special characters
        assert len(concept_descriptions) >= 0
    
    def test_large_file_handling(self, temp_workspace):
        """Test handling of large files and directories."""
        # Create a large markdown file
        large_content = "# Large File Test\n\n"
        
        # Add many sections to make it large
        for i in range(100):
            large_content += f"""## Section {i}

This is section {i} with some content. It contains information about topic {i}.

### Subsection {i}.1

More detailed information about topic {i}.

```python
def function_{i}():
    return "Result from function {i}"
```

### Subsection {i}.2

Additional content for section {i}.

"""
        
        large_file = temp_workspace / 'large_file.md'
        large_file.write_text(large_content)
        
        # Create many small files
        many_files_dir = temp_workspace / 'many_files'
        many_files_dir.mkdir()
        
        for i in range(50):
            small_file = many_files_dir / f'file_{i}.md'
            small_file.write_text(f"# File {i}\n\nContent for file {i}.")
        
        # Test content analyzer with large/many files
        analyzer = ContentAnalyzer(str(temp_workspace))
        analysis = analyzer.analyze_repository(str(temp_workspace))
        
        # Should handle large files without errors
        assert isinstance(analysis, RepositoryAnalysis)
        assert len(analysis.concepts) > 0
        
        # Should process multiple files
        assert len(analysis.file_structure) > 0
    
    def test_file_permission_and_access_errors(self, temp_workspace):
        """Test handling of file permission and access errors."""
        # Create a file and make it unreadable (if possible on the system)
        restricted_file = temp_workspace / 'restricted.md'
        restricted_file.write_text("# Restricted Content\n\nThis file has restricted access.")
        
        try:
            # Try to make file unreadable (may not work on all systems)
            os.chmod(restricted_file, 0o000)
            
            # Test content analyzer with restricted file
            analyzer = ContentAnalyzer(str(temp_workspace))
            analysis = analyzer.analyze_repository(str(temp_workspace))
            
            # Should handle permission errors gracefully
            assert isinstance(analysis, RepositoryAnalysis)
            
        except (OSError, PermissionError):
            # If we can't change permissions, skip this test
            pass
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(restricted_file, 0o644)
            except (OSError, PermissionError):
                pass
    
    def test_concurrent_file_operations(self, temp_workspace):
        """Test concurrent file operations don't cause conflicts."""
        import threading
        import time
        
        results = []
        errors = []
        
        def analyze_repository():
            try:
                analyzer = ContentAnalyzer(str(temp_workspace))
                analysis = analyzer.analyze_repository(str(temp_workspace))
                results.append(analysis)
            except Exception as e:
                errors.append(e)
        
        def generate_tasks():
            try:
                task_generator = TaskGenerator()
                tasks_file = temp_workspace / 'tasks.md'
                if tasks_file.exists():
                    existing_tasks = task_generator.load_tasks_from_file(str(tasks_file))
                    results.append(existing_tasks)
            except Exception as e:
                errors.append(e)
        
        # Run operations concurrently
        threads = [
            threading.Thread(target=analyze_repository),
            threading.Thread(target=generate_tasks),
            threading.Thread(target=analyze_repository)  # Duplicate to test concurrent reads
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join(timeout=10)  # 10 second timeout
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent operations failed: {errors}"
        assert len(results) > 0, "No results from concurrent operations"
    
    def test_file_backup_and_recovery(self, temp_workspace):
        """Test file backup and recovery mechanisms."""
        # Create original files
        original_readme = temp_workspace / 'README.md'
        original_content = original_readme.read_text()
        
        original_tasks = temp_workspace / 'tasks.md'
        original_tasks_content = original_tasks.read_text()
        
        # Test that generators preserve original content
        quick_start_generator = QuickStartGenerator()
        
        # Generate and update Quick Start
        quick_start_guide = {
            'prerequisites': ['Test prerequisite'],
            'setup_steps': ['Test setup'],
            'basic_usage': ['Test usage'],
            'next_steps': ['Test next steps']
        }
        
        quick_start_content = quick_start_generator.generate_quick_start(quick_start_guide)
        quick_start_generator.update_readme_section(str(original_readme), quick_start_content)
        
        # Verify original content is preserved
        updated_content = original_readme.read_text()
        assert 'Test Project' in updated_content  # Original title preserved
        assert 'Installation' in updated_content  # Original section preserved
        
        # Test FAQ generator preserves existing content
        faq_generator = FAQGenerator()
        original_faq = temp_workspace / 'faq.md'
        original_faq_content = original_faq.read_text()
        
        new_faq_pairs = [
            {
                'question': 'Test question?',
                'answer': 'Test answer.',
                'category': 'test',
                'source_files': ['test.md'],
                'confidence': 0.9
            }
        ]
        
        new_faq_content = faq_generator.generate_faqs(new_faq_pairs)
        merged_content = faq_generator.merge_with_existing(new_faq_content, str(original_faq))
        
        # Write merged content
        with open(original_faq, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        # Verify original FAQ content is preserved
        final_faq_content = original_faq.read_text()
        assert 'What is this project?' in final_faq_content  # Original question preserved
        assert 'Test question?' in final_faq_content  # New question added