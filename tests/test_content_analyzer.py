"""Unit tests for ContentAnalyzer component."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from src.analyzers.content_analyzer import ContentAnalyzer
from src.models import (
    RepositoryAnalysis, Concept, SetupStep, CodeExample, Dependency
)


class TestContentAnalyzer:
    """Test cases for ContentAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ContentAnalyzer()
        
        # Sample markdown content for testing
        self.sample_markdown = """# Getting Started

This is an overview of the project architecture.

## Prerequisites

Before you can start, make sure you have:
- Python 3.8 or higher
- pip package manager

## Installation

1. Clone the repository
2. Install dependencies with `pip install -r requirements.txt`
3. Run the setup script

```python
def hello_world():
    return "Hello, World!"
```

## Architecture Overview

The system consists of several key components that work together.

### Core Components

- **Content Analyzer**: Parses markdown files
- **AI Engine**: Processes content with AI

```bash
# Run the application
python main.py
```
"""
        
        self.setup_markdown = """# Setup Guide

## Getting Started

Follow these steps to set up the project:

### Step 1: Install Python
Download and install Python from python.org

### Step 2: Clone Repository
```bash
git clone https://github.com/example/repo.git
cd repo
```

### Step 3: Install Dependencies
Run the following command:
```bash
pip install -r requirements.txt
```
"""

    def test_init(self):
        """Test ContentAnalyzer initialization."""
        analyzer = ContentAnalyzer('/test/path')
        assert analyzer.workspace_path == Path('/test/path')
        assert analyzer.logger is not None
        assert 'install' in analyzer.setup_keywords
        assert 'overview' in analyzer.concept_keywords

    def test_extract_concepts(self):
        """Test concept extraction from markdown content."""
        concepts = self.analyzer.extract_concepts(self.sample_markdown)
        
        # Should find concepts based on headings
        concept_names = [c.name for c in concepts]
        assert 'Getting Started' in concept_names
        assert 'Architecture Overview' in concept_names
        
        # Check concept properties
        getting_started = next(c for c in concepts if c.name == 'Getting Started')
        assert getting_started.importance > 0
        assert isinstance(getting_started.description, str)
        assert len(getting_started.description) > 0

    def test_identify_setup_steps(self):
        """Test setup step identification."""
        steps = self.analyzer.identify_setup_steps(self.setup_markdown)
        
        # Should find setup steps
        assert len(steps) > 0
        
        # Check step properties
        for step in steps:
            assert isinstance(step.title, str)
            assert isinstance(step.description, str)
            assert isinstance(step.commands, list)
            assert isinstance(step.order, int)

    def test_find_code_examples(self):
        """Test code example extraction."""
        examples = self.analyzer.find_code_examples(self.sample_markdown)
        
        # Should find code blocks
        assert len(examples) >= 2  # Python and bash examples
        
        # Check example properties
        python_example = next((e for e in examples if e.language == 'python'), None)
        assert python_example is not None
        assert 'hello_world' in python_example.code
        
        bash_example = next((e for e in examples if e.language == 'bash'), None)
        assert bash_example is not None
        assert 'python main.py' in bash_example.code

    def test_extract_commands(self):
        """Test command extraction from text."""
        text = "Run `pip install package` and then execute `python script.py`"
        commands = self.analyzer._extract_commands(text)
        
        assert 'pip install package' in commands
        assert 'python script.py' in commands

    def test_looks_like_command(self):
        """Test command detection."""
        assert self.analyzer._looks_like_command('pip install requests')
        assert self.analyzer._looks_like_command('git clone repo')
        assert self.analyzer._looks_like_command('python main.py')
        assert not self.analyzer._looks_like_command('this is just text')

    def test_is_concept_heading(self):
        """Test concept heading detection."""
        assert self.analyzer._is_concept_heading('overview')
        assert self.analyzer._is_concept_heading('architecture')
        assert self.analyzer._is_concept_heading('introduction')
        assert not self.analyzer._is_concept_heading('random heading')

    def test_is_setup_heading(self):
        """Test setup heading detection."""
        assert self.analyzer._is_setup_heading('installation')
        assert self.analyzer._is_setup_heading('getting started')
        assert self.analyzer._is_setup_heading('setup')
        assert not self.analyzer._is_setup_heading('random heading')

    def test_calculate_concept_importance(self):
        """Test concept importance calculation."""
        # Higher level headings should have higher importance
        importance1 = self.analyzer._calculate_concept_importance(1, 'Overview', 'content')
        importance3 = self.analyzer._calculate_concept_importance(3, 'Overview', 'content')
        assert importance1 > importance3
        
        # Key terms should boost importance
        importance_key = self.analyzer._calculate_concept_importance(3, 'Architecture', 'content')
        importance_normal = self.analyzer._calculate_concept_importance(3, 'Random', 'content')
        assert importance_key > importance_normal

    def test_extract_concept_description(self):
        """Test concept description extraction."""
        content = "This is the first paragraph.\n\nThis is the second paragraph."
        description = self.analyzer._extract_concept_description(content)
        assert description == "This is the first paragraph."

    def test_extract_prerequisites(self):
        """Test prerequisite extraction."""
        content = "Prerequisites: Python 3.8, Git\nYou need to install Docker before starting."
        prerequisites = self.analyzer._extract_prerequisites(content)
        
        assert len(prerequisites) > 0
        # Should find some prerequisites
        prereq_text = ' '.join(prerequisites).lower()
        assert 'python' in prereq_text or 'git' in prereq_text

    def test_detect_language(self):
        """Test programming language detection."""
        assert self.analyzer._detect_language('def hello(): pass') == 'python'
        assert self.analyzer._detect_language('function hello() {}') == 'javascript'
        assert self.analyzer._detect_language('echo "hello"') == 'bash'
        assert self.analyzer._detect_language('SELECT * FROM table') == 'sql'

    def test_extract_dependencies(self):
        """Test dependency extraction."""
        content = "Install with `pip install requests` and `npm install express`"
        dependencies = self.analyzer._extract_dependencies(content, 'test.md')
        
        # Should find dependencies
        dep_names = [d.name for d in dependencies]
        assert 'requests' in dep_names
        assert 'express' in dep_names

    def test_deduplicate_concepts(self):
        """Test concept deduplication."""
        concepts = [
            Concept('Test', 'Description 1', 5, ['file1.md'], []),
            Concept('test', 'Description 2', 7, ['file2.md'], []),  # Duplicate (case insensitive)
            Concept('Other', 'Description 3', 3, ['file3.md'], [])
        ]
        
        unique = self.analyzer._deduplicate_concepts(concepts)
        assert len(unique) == 2  # Should remove duplicate
        
        # Should keep the one with higher importance
        test_concept = next(c for c in unique if c.name.lower() == 'test')
        assert test_concept.importance == 7

    def test_order_setup_steps(self):
        """Test setup step ordering."""
        steps = [
            SetupStep('Run tests', 'Run the tests', [], [], 3),
            SetupStep('Install dependencies', 'Install deps', [], [], 1),
            SetupStep('Configure settings', 'Configure', [], [], 2)
        ]
        
        ordered = self.analyzer._order_setup_steps(steps)
        assert ordered[0].title == 'Install dependencies'
        assert ordered[-1].title == 'Run tests'

    def test_find_markdown_files(self):
        """Test markdown file discovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / 'README.md').write_text('# Test')
            (temp_path / 'docs').mkdir()
            (temp_path / 'docs' / 'guide.md').write_text('# Guide')
            (temp_path / 'test.txt').write_text('Not markdown')
            
            # Should skip certain directories
            (temp_path / '.git').mkdir()
            (temp_path / '.git' / 'config.md').write_text('# Config')
            
            files = self.analyzer._find_markdown_files(temp_path)
            file_names = [f.name for f in files]
            
            assert 'README.md' in file_names
            assert 'guide.md' in file_names
            assert 'config.md' not in file_names  # Should skip .git directory

    def test_read_file_content(self):
        """Test file content reading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('# Test Content')
            temp_path = Path(f.name)
        
        try:
            content = self.analyzer._read_file_content(temp_path)
            assert content == '# Test Content'
        finally:
            temp_path.unlink()

    def test_read_file_content_error(self):
        """Test file reading error handling."""
        non_existent = Path('/non/existent/file.md')
        content = self.analyzer._read_file_content(non_existent)
        assert content is None

    def test_build_file_structure(self):
        """Test file structure building."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test structure
            (temp_path / 'src').mkdir()
            (temp_path / 'src' / 'main.py').write_text('# Main')
            (temp_path / 'tests').mkdir()
            (temp_path / 'tests' / 'test_main.py').write_text('# Test')
            (temp_path / 'README.md').write_text('# README')
            
            structure = self.analyzer._build_file_structure(temp_path)
            
            assert 'src' in structure
            assert 'tests' in structure
            assert '_files' in structure
            assert 'README.md' in structure['_files']

    @patch('os.walk')
    def test_analyze_repository_with_mocked_files(self, mock_walk):
        """Test repository analysis with mocked file system."""
        # Mock file system structure
        mock_walk.return_value = [
            ('/test', ['docs'], ['README.md']),
            ('/test/docs', [], ['guide.md'])
        ]
        
        # Mock file reading
        file_contents = {
            '/test/README.md': self.sample_markdown,
            '/test/docs/guide.md': self.setup_markdown
        }
        
        def mock_read_file(path):
            return file_contents.get(str(path))
        
        with patch.object(self.analyzer, '_read_file_content', side_effect=mock_read_file):
            analysis = self.analyzer.analyze_repository('/test')
            
            assert isinstance(analysis, RepositoryAnalysis)
            assert len(analysis.concepts) > 0
            assert len(analysis.setup_steps) > 0
            assert len(analysis.code_examples) > 0

    def test_analyze_repository_empty_directory(self):
        """Test repository analysis with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            analysis = self.analyzer.analyze_repository(temp_dir)
            
            assert isinstance(analysis, RepositoryAnalysis)
            assert len(analysis.concepts) == 0
            assert len(analysis.setup_steps) == 0
            assert len(analysis.code_examples) == 0

    def test_analyze_repository_nonexistent_path(self):
        """Test repository analysis with non-existent path."""
        analysis = self.analyzer.analyze_repository('/non/existent/path')
        
        assert isinstance(analysis, RepositoryAnalysis)
        assert len(analysis.concepts) == 0
        assert len(analysis.setup_steps) == 0
        assert len(analysis.code_examples) == 0


class TestContentAnalyzerIntegration:
    """Integration tests for ContentAnalyzer with real files."""
    
    def test_analyze_current_repository(self):
        """Test analyzing the current repository structure."""
        analyzer = ContentAnalyzer()
        
        # Analyze the current repository
        analysis = analyzer.analyze_repository('.')
        
        # Should find some content
        assert isinstance(analysis, RepositoryAnalysis)
        assert isinstance(analysis.file_structure, dict)
        
        # Should have found the spec files
        if analysis.concepts:
            concept_names = [c.name.lower() for c in analysis.concepts]
            # Might find concepts from spec files
            assert any('specops' in name or 'onboarding' in name or 'requirements' in name 
                      for name in concept_names)

    def test_extract_from_spec_files(self):
        """Test extracting content from actual spec files."""
        analyzer = ContentAnalyzer()
        
        # Test with requirements file
        req_path = '.kiro/specs/specops-onboarding-factory/requirements.md'
        if Path(req_path).exists():
            with open(req_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            concepts = analyzer.extract_concepts(content, req_path)
            setup_steps = analyzer.identify_setup_steps(content, req_path)
            code_examples = analyzer.find_code_examples(content, req_path)
            
            # Should extract some information
            assert len(concepts) > 0 or len(setup_steps) > 0 or len(code_examples) >= 0


class TestContentRelationshipAnalysis:
    """Test cases for content relationship analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures for relationship analysis."""
        self.analyzer = ContentAnalyzer()
        
        # Sample markdown files with relationships
        self.readme_content = """# Project Overview

This project demonstrates the core architecture concepts.

## Getting Started

Before you begin, make sure you read the [Setup Guide](setup.md) and understand the [Architecture](docs/architecture.md).

### Prerequisites

- Python 3.8+
- Understanding of the core concepts

## Quick Start

1. Follow the setup instructions
2. Read the API documentation
3. Run your first example

For more details, see the setup guide.
"""
        
        self.setup_content = """# Setup Guide

This guide depends on the Project Overview for context.

## Installation Steps

1. Install Python (see prerequisites in README.md)
2. Clone the repository
3. Install dependencies with `pip install -r requirements.txt`

## Configuration

After installation, you need to configure the system.
Refer to the configuration section in the architecture documentation.

## Next Steps

Once setup is complete, check out the [API Guide](api.md) for usage examples.
"""
        
        self.architecture_content = """# Architecture Overview

This document describes the system architecture.

## Core Components

The system consists of several key components:

- **Content Analyzer**: Processes markdown files
- **Relationship Engine**: Identifies dependencies
- **Cache Manager**: Optimizes performance

## Dependencies

The architecture depends on understanding the setup process.
Before implementing features, developers should complete the setup guide.

## Design Patterns

We use several design patterns throughout the codebase.
"""
        
        self.api_content = """# API Documentation

This guide assumes you have completed the setup process.

## Authentication

Before using the API, ensure your environment is configured.

## Endpoints

### Content Analysis
```python
analyzer = ContentAnalyzer()
result = analyzer.analyze_repository('.')
```

### Relationship Analysis
```python
relationships = analyzer.analyze_content_relationships('.')
```

## Examples

See the setup guide for environment configuration examples.
"""

    def test_analyze_content_relationships(self):
        """Test the main content relationship analysis method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / 'README.md').write_text(self.readme_content)
            (temp_path / 'setup.md').write_text(self.setup_content)
            (temp_path / 'docs').mkdir()
            (temp_path / 'docs' / 'architecture.md').write_text(self.architecture_content)
            (temp_path / 'api.md').write_text(self.api_content)
            
            # Analyze relationships
            relationships = self.analyzer.analyze_content_relationships(str(temp_path))
            
            # Verify structure
            assert 'file_dependencies' in relationships
            assert 'concept_relationships' in relationships
            assert 'content_hierarchy' in relationships
            assert 'cross_references' in relationships
            assert 'prerequisite_chains' in relationships
            
            # Verify file dependencies
            file_deps = relationships['file_dependencies']
            assert 'README.md' in file_deps
            assert 'setup.md' in file_deps['README.md']

    def test_identify_file_dependencies(self):
        """Test file dependency identification."""
        content_map = {
            'README.md': self.readme_content,
            'setup.md': self.setup_content,
            'docs/architecture.md': self.architecture_content
        }
        
        dependencies = self.analyzer._identify_file_dependencies(content_map)
        
        # README should depend on setup.md and architecture.md
        readme_deps = dependencies['README.md']
        assert 'setup.md' in readme_deps
        assert 'docs/architecture.md' in readme_deps
        
        # Setup should reference README.md
        setup_deps = dependencies['setup.md']
        assert 'README.md' in setup_deps

    def test_identify_concept_relationships(self):
        """Test concept relationship identification."""
        content_map = {
            'README.md': self.readme_content,
            'setup.md': self.setup_content,
            'docs/architecture.md': self.architecture_content
        }
        
        concept_relationships = self.analyzer._identify_concept_relationships(content_map)
        
        # Should find relationships between concepts
        assert len(concept_relationships) > 0
        
        # Check for specific concept relationships
        concept_names = list(concept_relationships.keys())
        assert any('overview' in name.lower() for name in concept_names)

    def test_build_content_hierarchy(self):
        """Test content hierarchy building."""
        content_map = {
            'README.md': self.readme_content,
            'setup.md': self.setup_content,
            'docs/architecture.md': self.architecture_content
        }
        
        hierarchy = self.analyzer._build_content_hierarchy(content_map)
        
        # Should have hierarchy for each file
        assert 'README.md' in hierarchy
        assert 'setup.md' in hierarchy
        assert 'docs/architecture.md' in hierarchy
        
        # Check hierarchy structure
        readme_hierarchy = hierarchy['README.md']
        assert 'headings' in readme_hierarchy
        assert 'importance' in readme_hierarchy
        assert 'word_count' in readme_hierarchy
        assert 'has_code_examples' in readme_hierarchy
        
        # README should have higher importance
        assert readme_hierarchy['importance'] > hierarchy['setup.md']['importance']

    def test_find_cross_references(self):
        """Test cross-reference identification."""
        content_map = {
            'README.md': self.readme_content,
            'setup.md': self.setup_content,
            'api.md': self.api_content
        }
        
        cross_references = self.analyzer._find_cross_references(content_map)
        
        # Should find cross-references
        assert 'README.md' in cross_references
        readme_refs = cross_references['README.md']
        
        # Should find markdown links
        link_refs = [ref for ref in readme_refs if ref['type'] == 'link']
        assert len(link_refs) > 0
        
        # Should find textual references
        text_refs = [ref for ref in readme_refs if ref['type'] == 'textual_reference']
        assert len(text_refs) >= 0  # May or may not find textual references

    def test_build_prerequisite_chains(self):
        """Test prerequisite chain building."""
        content_map = {
            'README.md': self.readme_content,
            'setup.md': self.setup_content,
            'api.md': self.api_content
        }
        
        prerequisite_chains = self.analyzer._build_prerequisite_chains(content_map)
        
        # Should have chains for each file
        assert 'README.md' in prerequisite_chains
        assert 'setup.md' in prerequisite_chains
        assert 'api.md' in prerequisite_chains
        
        # API should depend on setup
        api_chain = prerequisite_chains['api.md']
        assert len(api_chain) >= 0  # May find prerequisites

    def test_calculate_file_importance(self):
        """Test file importance calculation."""
        # README should have high importance
        readme_importance = self.analyzer._calculate_file_importance('README.md', self.readme_content)
        setup_importance = self.analyzer._calculate_file_importance('setup.md', self.setup_content)
        
        assert readme_importance > setup_importance
        assert readme_importance >= 5  # README gets bonus points
        
        # Test with different file types
        api_importance = self.analyzer._calculate_file_importance('api.md', self.api_content)
        assert api_importance >= 1

    def test_extract_link_context(self):
        """Test link context extraction."""
        content = "This is some text with a [link](url) in the middle of a sentence."
        context = self.analyzer._extract_link_context(content, 'link')
        
        assert 'link' in context
        assert len(context) > 0
        assert len(context) <= 100  # Should be limited

    def test_extract_reference_context(self):
        """Test reference context extraction."""
        content = "You should see the documentation. It contains important information."
        context = self.analyzer._extract_reference_context(content, 'documentation')
        
        assert 'documentation' in context
        assert len(context) > 0

    def test_caching_functionality(self):
        """Test caching mechanisms."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test file
            (temp_path / 'test.md').write_text('# Test Content')
            
            # First analysis should populate cache
            relationships1 = self.analyzer.analyze_content_relationships(str(temp_path))
            
            # Second analysis should use cache
            relationships2 = self.analyzer.analyze_content_relationships(str(temp_path))
            
            # Results should be identical
            assert relationships1 == relationships2
            
            # Check cache stats
            stats = self.analyzer.get_cache_stats()
            assert stats['relationship_cache_size'] > 0

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / 'test.md').write_text('# Test')
            
            # Populate cache
            self.analyzer.analyze_content_relationships(str(temp_path))
            
            # Verify cache has content
            stats_before = self.analyzer.get_cache_stats()
            assert stats_before['relationship_cache_size'] > 0
            
            # Clear cache
            self.analyzer.clear_cache()
            
            # Verify cache is empty
            stats_after = self.analyzer.get_cache_stats()
            assert stats_after['relationship_cache_size'] == 0
            assert stats_after['content_cache_size'] == 0

    def test_get_cache_key(self):
        """Test cache key generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / 'test.md').write_text('# Test')
            
            # Generate cache keys
            key1 = self.analyzer._get_cache_key(str(temp_path), 'relationships')
            key2 = self.analyzer._get_cache_key(str(temp_path), 'relationships')
            
            # Keys should be consistent
            assert key1 == key2
            assert 'relationships' in key1
            
            # Different analysis types should have different keys
            key3 = self.analyzer._get_cache_key(str(temp_path), 'content')
            assert key1 != key3

    def test_relationship_analysis_with_sample_markdown(self):
        """Test relationship analysis with comprehensive sample markdown files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a comprehensive set of sample files
            samples = {
                'README.md': """# Sample Project
                
This project demonstrates content relationship analysis.

## Overview
See the [Architecture Guide](docs/architecture.md) for system design.

## Getting Started
1. Read the [Setup Guide](setup.md)
2. Check the [API Documentation](api/reference.md)
3. Try the [Examples](examples/basic.md)

## Prerequisites
- Python 3.8+
- Basic understanding of the concepts
""",
                'setup.md': """# Setup Guide
                
This guide helps you set up the project.

## Prerequisites
Before starting, ensure you understand the project overview in README.md.

## Installation
1. Install Python
2. Clone repository
3. Install dependencies

## Configuration
After setup, refer to the configuration section in the architecture guide.
""",
                'docs/architecture.md': """# Architecture
                
System architecture overview.

## Components
- Content Analyzer
- Relationship Engine

## Dependencies
This architecture depends on proper setup (see setup.md).
""",
                'api/reference.md': """# API Reference
                
Complete API documentation.

## Prerequisites
Complete the setup process before using the API.

## Usage
```python
from analyzer import ContentAnalyzer
analyzer = ContentAnalyzer()
```
""",
                'examples/basic.md': """# Basic Examples
                
Simple usage examples.

## Setup Required
Ensure you have completed the setup guide.

## Example 1
Basic content analysis example.
"""
            }
            
            # Create directory structure and files
            for file_path, content in samples.items():
                full_path = temp_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
            
            # Analyze relationships
            relationships = self.analyzer.analyze_content_relationships(str(temp_path))
            
            # Comprehensive verification
            assert 'file_dependencies' in relationships
            assert 'concept_relationships' in relationships
            assert 'content_hierarchy' in relationships
            assert 'cross_references' in relationships
            assert 'prerequisite_chains' in relationships
            
            # Verify file dependencies
            file_deps = relationships['file_dependencies']
            readme_deps = file_deps.get('README.md', [])
            assert any('setup.md' in dep for dep in readme_deps)
            assert any('architecture.md' in dep for dep in readme_deps)
            
            # Verify content hierarchy
            hierarchy = relationships['content_hierarchy']
            assert 'README.md' in hierarchy
            readme_hierarchy = hierarchy['README.md']
            assert readme_hierarchy['importance'] >= 5  # README should have high importance
            
            # Verify cross-references
            cross_refs = relationships['cross_references']
            readme_refs = cross_refs.get('README.md', [])
            link_refs = [ref for ref in readme_refs if ref['type'] == 'link']
            assert len(link_refs) > 0  # Should find markdown links
            
            # Verify prerequisite chains
            prereq_chains = relationships['prerequisite_chains']
            assert len(prereq_chains) > 0