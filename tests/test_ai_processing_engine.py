"""Tests for AI Processing Engine with mocked AI responses."""

import json
import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from src.ai.processing_engine import AIProcessingEngine, AIProcessingError
from src.models import (
    RepositoryAnalysis, Concept, SetupStep, CodeExample, Dependency,
    TaskSuggestion, FAQPair, QuickStartGuide, FeatureAnalysis, StyleConfig
)


class TestAIProcessingEngine:
    """Test cases for AIProcessingEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create AI processing engine for testing."""
        style_config = StyleConfig()
        style_config.code_style_content = "# Test Code Style\n- Follow PEP 8"
        style_config.onboarding_style_content = "# Test Onboarding Style\n- Be helpful"
        return AIProcessingEngine(
            model="test-model",
            temperature=0.5,
            max_retries=2,
            style_config=style_config
        )
    
    @pytest.fixture
    def sample_analysis(self):
        """Create sample repository analysis for testing."""
        return RepositoryAnalysis(
            concepts=[
                Concept(
                    name="Hello World",
                    description="Simple greeting function",
                    importance=8,
                    related_files=["features/hello_world.py"],
                    prerequisites=[]
                ),
                Concept(
                    name="Testing",
                    description="Unit testing patterns",
                    importance=9,
                    related_files=["tests/test_hello_world.py"],
                    prerequisites=["Hello World"]
                )
            ],
            setup_steps=[
                SetupStep(
                    title="Install Python",
                    description="Install Python 3.8 or higher",
                    commands=["python --version"],
                    prerequisites=[],
                    order=1
                ),
                SetupStep(
                    title="Install Dependencies",
                    description="Install required packages",
                    commands=["pip install -r requirements.txt"],
                    prerequisites=["Install Python"],
                    order=2
                )
            ],
            code_examples=[
                CodeExample(
                    title="Basic Usage",
                    code="print(hello_world())",
                    language="python",
                    description="Simple function call",
                    file_path="examples/basic.py"
                )
            ],
            file_structure={"src": {}, "tests": {}, "features": {}},
            dependencies=[
                Dependency(name="pytest", version="7.0.0", type="dev"),
                Dependency(name="requests", version="2.28.0", type="runtime")
            ]
        )  
  
    def test_initialization(self):
        """Test engine initialization with default parameters."""
        engine = AIProcessingEngine()
        assert engine.model == "gpt-3.5-turbo"
        assert engine.temperature == 0.7
        assert engine.max_retries == 3
        assert engine.retry_delay == 1.0
        assert isinstance(engine.style_config, StyleConfig)
    
    def test_initialization_with_custom_params(self):
        """Test engine initialization with custom parameters."""
        style_config = StyleConfig()
        engine = AIProcessingEngine(
            model="gpt-4",
            temperature=0.3,
            max_retries=5,
            retry_delay=2.0,
            style_config=style_config
        )
        assert engine.model == "gpt-4"
        assert engine.temperature == 0.3
        assert engine.max_retries == 5
        assert engine.retry_delay == 2.0
        assert engine.style_config == style_config
    
    def test_get_style_context(self, engine):
        """Test style context generation."""
        context = engine._get_style_context()
        assert "Code Style Guidelines" in context
        assert "Onboarding Style Guidelines" in context
        assert "Follow PEP 8" in context
        assert "Be helpful" in context
    
    def test_mock_ai_response_task_suggestions(self, engine):
        """Test mock AI response for task suggestions."""
        response = engine._mock_ai_response(
            "Generate task suggestions",
            response_format="json"
        )
        data = json.loads(response)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "title" in data[0]
        assert "description" in data[0]
        assert "acceptance_criteria" in data[0]
    
    def test_mock_ai_response_faq_pairs(self, engine):
        """Test mock AI response for FAQ pairs."""
        response = engine._mock_ai_response(
            "Generate FAQ pairs",
            response_format="json"
        )
        data = json.loads(response)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "question" in data[0]
        assert "answer" in data[0]
        assert data[0]["question"].endswith("?")
    
    def test_mock_ai_response_quick_start(self, engine):
        """Test mock AI response for Quick Start guide."""
        response = engine._mock_ai_response(
            "Generate quick start guide",
            response_format="json"
        )
        data = json.loads(response)
        assert isinstance(data, dict)
        assert "prerequisites" in data
        assert "setup_steps" in data
        assert "basic_usage" in data
        assert "next_steps" in data
    
    def test_mock_ai_response_feature_analysis(self, engine):
        """Test mock AI response for feature analysis."""
        response = engine._mock_ai_response(
            "Analyze feature analysis code",
            response_format="json"
        )
        data = json.loads(response)
        assert isinstance(data, dict)
        assert "functions" in data
        assert "classes" in data
        assert "tests" in data
        assert "complexity" in data 
   
    def test_generate_task_suggestions_success(self, engine, sample_analysis):
        """Test successful task suggestion generation."""
        tasks = engine.generate_task_suggestions(sample_analysis)
        
        assert isinstance(tasks, list)
        assert len(tasks) >= 1
        
        for task in tasks:
            assert isinstance(task, TaskSuggestion)
            assert task.title
            assert task.description
            assert isinstance(task.acceptance_criteria, list)
            assert isinstance(task.prerequisites, list)
            assert task.estimated_time > 0
            assert task.difficulty in ["easy", "medium", "hard", "expert"]
    
    def test_generate_task_suggestions_empty_analysis(self, engine):
        """Test task generation with empty analysis."""
        empty_analysis = RepositoryAnalysis()
        tasks = engine.generate_task_suggestions(empty_analysis)
        
        assert isinstance(tasks, list)
        # Should still generate some basic tasks even with empty analysis
    
    @patch('src.ai.processing_engine.AIProcessingEngine._make_ai_request')
    def test_generate_task_suggestions_ai_error(self, mock_request, engine, sample_analysis):
        """Test task generation with AI request failure."""
        mock_request.side_effect = AIProcessingError("AI request failed")
        
        with pytest.raises(AIProcessingError, match="AI request failed"):
            engine.generate_task_suggestions(sample_analysis)
    
    @patch('src.ai.processing_engine.AIProcessingEngine._make_ai_request')
    def test_generate_task_suggestions_invalid_json(self, mock_request, engine, sample_analysis):
        """Test task generation with invalid JSON response."""
        mock_request.return_value = "invalid json"
        
        with pytest.raises(AIProcessingError, match="Failed to parse task suggestions"):
            engine.generate_task_suggestions(sample_analysis)
    
    def test_create_faq_pairs_success(self, engine, sample_analysis):
        """Test successful FAQ pair generation."""
        faqs = engine.create_faq_pairs(sample_analysis)
        
        assert isinstance(faqs, list)
        assert len(faqs) >= 1
        
        for faq in faqs:
            assert isinstance(faq, FAQPair)
            assert faq.question
            assert faq.question.endswith("?")
            assert faq.answer
            assert faq.category in ["setup", "usage", "development", "troubleshooting", "general"]
            assert isinstance(faq.source_files, list)
            assert 0.0 <= faq.confidence <= 1.0
    
    def test_create_faq_pairs_empty_analysis(self, engine):
        """Test FAQ generation with empty analysis."""
        empty_analysis = RepositoryAnalysis()
        faqs = engine.create_faq_pairs(empty_analysis)
        
        assert isinstance(faqs, list)
        # Should still generate some basic FAQs
    
    @patch('src.ai.processing_engine.AIProcessingEngine._make_ai_request')
    def test_create_faq_pairs_ai_error(self, mock_request, engine, sample_analysis):
        """Test FAQ generation with AI request failure."""
        mock_request.side_effect = AIProcessingError("AI request failed")
        
        with pytest.raises(AIProcessingError, match="AI request failed"):
            engine.create_faq_pairs(sample_analysis)
    
    def test_extract_quick_start_steps_success(self, engine, sample_analysis):
        """Test successful Quick Start guide generation."""
        guide = engine.extract_quick_start_steps(sample_analysis)
        
        assert isinstance(guide, QuickStartGuide)
        assert isinstance(guide.prerequisites, list)
        assert isinstance(guide.setup_steps, list)
        assert isinstance(guide.basic_usage, list)
        assert isinstance(guide.next_steps, list)
        
        # Should have some content
        assert not guide.is_empty()
    
    def test_extract_quick_start_steps_empty_analysis(self, engine):
        """Test Quick Start generation with empty analysis."""
        empty_analysis = RepositoryAnalysis()
        guide = engine.extract_quick_start_steps(empty_analysis)
        
        assert isinstance(guide, QuickStartGuide)
        # Should still generate some basic guide content    

    @patch('builtins.open', new_callable=mock_open, read_data='def hello_world():\n    """Simple greeting."""\n    return "Hello, World!"')
    def test_analyze_feature_code_success(self, mock_file, engine):
        """Test successful feature code analysis."""
        # Mock test file content
        test_content = 'def test_hello_world():\n    assert hello_world() == "Hello, World!"'
        mock_file.side_effect = [
            mock_open(read_data='def hello_world():\n    """Simple greeting."""\n    return "Hello, World!"').return_value,
            mock_open(read_data=test_content).return_value
        ]
        
        analysis = engine.analyze_feature_code("features/hello_world.py")
        
        assert isinstance(analysis, FeatureAnalysis)
        assert analysis.feature_path == "features/hello_world.py"
        assert isinstance(analysis.functions, list)
        assert isinstance(analysis.classes, list)
        assert isinstance(analysis.tests, list)
        assert isinstance(analysis.documentation, str)
        assert analysis.complexity in ["low", "medium", "high", "very_high"]
    
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_analyze_feature_code_file_not_found(self, mock_file, engine):
        """Test feature analysis with missing file."""
        with pytest.raises(AIProcessingError, match="Could not read feature file"):
            engine.analyze_feature_code("nonexistent/file.py")
    
    @patch('builtins.open', new_callable=mock_open, read_data='def hello_world():\n    return "Hello!"')
    def test_analyze_feature_code_no_test_file(self, mock_file, engine):
        """Test feature analysis when test file doesn't exist."""
        # First call succeeds (feature file), second call fails (test file)
        mock_file.side_effect = [
            mock_open(read_data='def hello_world():\n    return "Hello!"').return_value,
            FileNotFoundError("Test file not found")
        ]
        
        analysis = engine.analyze_feature_code("features/hello_world.py")
        
        assert isinstance(analysis, FeatureAnalysis)
        assert analysis.feature_path == "features/hello_world.py"
        # Should still work without test file
    
    @patch('src.ai.processing_engine.AIProcessingEngine._make_ai_request')
    @patch('builtins.open', new_callable=mock_open, read_data='def hello():\n    pass')
    def test_analyze_feature_code_ai_error(self, mock_file, mock_request, engine):
        """Test feature analysis with AI request failure."""
        mock_request.side_effect = AIProcessingError("AI analysis failed")
        
        with pytest.raises(AIProcessingError, match="AI analysis failed"):
            engine.analyze_feature_code("features/test.py")
    
    @patch('src.ai.processing_engine.AIProcessingEngine._make_ai_request')
    @patch('builtins.open', new_callable=mock_open, read_data='def hello():\n    pass')
    def test_analyze_feature_code_invalid_json(self, mock_file, mock_request, engine):
        """Test feature analysis with invalid JSON response."""
        mock_request.return_value = "invalid json response"
        
        with pytest.raises(AIProcessingError, match="Failed to parse feature analysis"):
            engine.analyze_feature_code("features/test.py")
    
    def test_get_model_info(self, engine):
        """Test model information retrieval."""
        info = engine.get_model_info()
        
        assert isinstance(info, dict)
        assert "model" in info
        assert "temperature" in info
        assert "max_retries" in info
        assert "retry_delay" in info
        assert "style_config_loaded" in info
        
        assert info["model"] == "test-model"
        assert info["temperature"] == 0.5
        assert info["max_retries"] == 2
        assert isinstance(info["style_config_loaded"], bool)
    
    def test_update_style_config(self, engine):
        """Test style configuration update."""
        new_style_config = StyleConfig()
        new_style_config.code_style_content = "# New Style\n- Use black formatter"
        
        engine.update_style_config(new_style_config)
        
        assert engine.style_config == new_style_config
        assert "New Style" in engine._get_style_context()
    
    @patch('src.ai.processing_engine.time.sleep')
    def test_make_ai_request_retry_logic(self, mock_sleep, engine):
        """Test AI request retry logic with exponential backoff."""
        # Mock the _mock_ai_response to fail twice then succeed
        original_mock = engine._mock_ai_response
        call_count = 0
        
        def failing_mock(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Temporary failure")
            return original_mock(*args, **kwargs)
        
        engine._mock_ai_response = failing_mock
        
        response = engine._make_ai_request("test prompt")
        
        assert response is not None
        assert call_count == 3  # Failed twice, succeeded on third attempt
        assert mock_sleep.call_count == 2  # Should have slept twice
        
        # Check exponential backoff
        sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]
        assert sleep_calls[0] == 1.0  # First retry delay
        assert sleep_calls[1] == 2.0  # Second retry delay (exponential backoff)
    
    @patch('src.ai.processing_engine.time.sleep')
    def test_make_ai_request_max_retries_exceeded(self, mock_sleep, engine):
        """Test AI request failure after max retries."""
        # Mock to always fail
        def always_fail(*args, **kwargs):
            raise Exception("Persistent failure")
        
        engine._mock_ai_response = always_fail
        
        with pytest.raises(AIProcessingError, match="AI request failed after 2 attempts"):
            engine._make_ai_request("test prompt")
        
        assert mock_sleep.call_count == 1  # Should have slept once (max_retries - 1)