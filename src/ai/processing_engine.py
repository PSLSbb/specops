"""AI Processing Engine for generating onboarding content."""

import json
import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from ..models import (
    RepositoryAnalysis, TaskSuggestion, FAQPair, QuickStartGuide,
    FeatureAnalysis, StyleConfig
)
from ..interfaces import AIProcessingEngineInterface


class AIProcessingError(Exception):
    """Raised when AI processing fails."""
    pass


class AIProcessingEngine(AIProcessingEngineInterface):
    """AI-powered content generation engine."""
    
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        style_config: Optional[StyleConfig] = None
    ):
        """Initialize the AI processing engine.
        
        Args:
            model: AI model to use for generation
            temperature: Temperature for AI generation (0.0-2.0)
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            style_config: Style configuration for content generation
        """
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.style_config = style_config or StyleConfig()
        self.logger = logging.getLogger(__name__)
        
        # Load style content if not already loaded
        if not self.style_config.code_style_content:
            self.style_config.load_content()
    
    def _make_ai_request(
        self,
        prompt: str,
        system_prompt: str = "",
        response_format: str = "text"
    ) -> str:
        """Make an AI request with retry logic.
        
        Args:
            prompt: The main prompt for the AI
            system_prompt: System prompt for context
            response_format: Expected response format ("text" or "json")
            
        Returns:
            AI response as string
            
        Raises:
            AIProcessingError: If all retry attempts fail
        """
        for attempt in range(self.max_retries):
            try:
                # Mock AI response for now - in real implementation this would call OpenAI API
                response = self._mock_ai_response(prompt, system_prompt, response_format)
                self.logger.debug(f"AI request successful on attempt {attempt + 1}")
                return response
                
            except Exception as e:
                self.logger.warning(f"AI request attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise AIProcessingError(f"AI request failed after {self.max_retries} attempts: {e}")
    
    def _mock_ai_response(
        self,
        prompt: str,
        system_prompt: str = "",
        response_format: str = "text"
    ) -> str:
        """Mock AI response for testing and development.
        
        This method simulates AI responses based on prompt content.
        In production, this would be replaced with actual AI API calls.
        """
        # Simulate processing delay
        time.sleep(0.1)
        
        if "task suggestions" in prompt.lower():
            if response_format == "json":
                return json.dumps([
                    {
                        "title": "Set up development environment",
                        "description": "Install required dependencies and configure the development environment",
                        "acceptance_criteria": [
                            "Python 3.8+ is installed",
                            "All dependencies from requirements.txt are installed",
                            "Tests can be run successfully"
                        ],
                        "prerequisites": [],
                        "estimated_time": 30,
                        "difficulty": "easy"
                    },
                    {
                        "title": "Understand project structure",
                        "description": "Explore the codebase and understand the main components",
                        "acceptance_criteria": [
                            "Can identify main modules and their purposes",
                            "Understands the data flow between components"
                        ],
                        "prerequisites": ["Set up development environment"],
                        "estimated_time": 45,
                        "difficulty": "medium"
                    }
                ])
            else:
                return "Generated task suggestions based on repository analysis"
        
        elif "faq pairs" in prompt.lower():
            if response_format == "json":
                return json.dumps([
                    {
                        "question": "How do I set up the development environment?",
                        "answer": "Install Python 3.8+, then run 'pip install -r requirements.txt' to install dependencies.",
                        "category": "setup",
                        "source_files": ["README.md"],
                        "confidence": 0.9
                    },
                    {
                        "question": "How do I run the tests?",
                        "answer": "Use 'python -m pytest' to run all tests, or 'python -m pytest tests/test_specific.py' for specific tests.",
                        "category": "testing",
                        "source_files": ["README.md", "tests/"],
                        "confidence": 0.8
                    }
                ])
            else:
                return "Generated FAQ pairs based on repository content"
        
        elif "quick start" in prompt.lower():
            if response_format == "json":
                return json.dumps({
                    "prerequisites": ["Python 3.8+", "Git"],
                    "setup_steps": [
                        "Clone the repository",
                        "Install dependencies with pip install -r requirements.txt",
                        "Run tests to verify setup"
                    ],
                    "basic_usage": [
                        "Import the main module",
                        "Create a basic configuration",
                        "Run the hello_world example"
                    ],
                    "next_steps": [
                        "Read the full documentation",
                        "Explore the examples directory",
                        "Try modifying the sample code"
                    ]
                })
            else:
                return "Generated Quick Start guide content"
        
        elif "feature analysis" in prompt.lower():
            if response_format == "json":
                return json.dumps({
                    "functions": ["hello_world", "main"],
                    "classes": [],
                    "tests": ["test_hello_world_default", "test_hello_world_custom_name"],
                    "documentation": "Simple greeting function for demonstration purposes",
                    "complexity": "low"
                })
            else:
                return "Analyzed feature code structure and complexity"
        
        else:
            return "Generated AI response based on the provided prompt"
    
    def _get_style_context(self) -> str:
        """Get style guidelines as context for AI generation."""
        context_parts = []
        
        if self.style_config.code_style_content:
            context_parts.append(f"Code Style Guidelines:\n{self.style_config.code_style_content}")
        
        if self.style_config.onboarding_style_content:
            context_parts.append(f"Onboarding Style Guidelines:\n{self.style_config.onboarding_style_content}")
        
        if self.style_config.structure_style_content:
            context_parts.append(f"Structure Guidelines:\n{self.style_config.structure_style_content}")
        
        return "\n\n".join(context_parts)
    
    def generate_task_suggestions(
        self, analysis: RepositoryAnalysis
    ) -> List[TaskSuggestion]:
        """Generate task suggestions from repository analysis.
        
        Args:
            analysis: Repository analysis results
            
        Returns:
            List of task suggestions
            
        Raises:
            AIProcessingError: If task generation fails
        """
        try:
            # Prepare context from analysis
            concepts_summary = "\n".join([
                f"- {concept.name}: {concept.description} (importance: {concept.importance})"
                for concept in analysis.concepts[:10]  # Limit to top 10 concepts
            ])
            
            setup_steps_summary = "\n".join([
                f"- {step.title}: {step.description}"
                for step in analysis.setup_steps[:5]  # Limit to top 5 steps
            ])
            
            # Create system prompt with style context
            system_prompt = f"""You are an expert at creating onboarding tasks for software projects.
Generate structured learning tasks that help new developers understand and contribute to the project.

{self._get_style_context()}

Focus on:
- Progressive difficulty from basic setup to advanced concepts
- Hands-on exercises that build practical skills
- Clear acceptance criteria for each task
- Realistic time estimates
"""
            
            # Create main prompt
            prompt = f"""Based on this repository analysis, generate onboarding task suggestions:

Key Concepts:
{concepts_summary}

Setup Steps:
{setup_steps_summary}

File Structure: {len(analysis.file_structure)} files analyzed
Dependencies: {len(analysis.dependencies)} dependencies found

Generate 5-8 task suggestions that would help a new developer learn this project effectively.
Return the response as a JSON array of task objects with these fields:
- title: Clear, actionable task title
- description: Detailed description of what to do
- acceptance_criteria: List of specific criteria to meet
- prerequisites: List of prerequisite task titles
- estimated_time: Time in minutes
- difficulty: "easy", "medium", "hard", or "expert"
"""
            
            # Make AI request
            response = self._make_ai_request(prompt, system_prompt, "json")
            
            # Parse response and create TaskSuggestion objects
            task_data = json.loads(response)
            tasks = []
            
            for task_dict in task_data:
                task = TaskSuggestion(
                    title=task_dict.get("title", ""),
                    description=task_dict.get("description", ""),
                    acceptance_criteria=task_dict.get("acceptance_criteria", []),
                    prerequisites=task_dict.get("prerequisites", []),
                    estimated_time=task_dict.get("estimated_time", 30),
                    difficulty=task_dict.get("difficulty", "medium")
                )
                tasks.append(task)
            
            self.logger.info(f"Generated {len(tasks)} task suggestions")
            return tasks
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise AIProcessingError(f"Failed to parse task suggestions: {e}")
        except Exception as e:
            raise AIProcessingError(f"Task generation failed: {e}")
    
    def create_faq_pairs(self, analysis: RepositoryAnalysis) -> List[FAQPair]:
        """Create FAQ question-answer pairs from repository analysis.
        
        Args:
            analysis: Repository analysis results
            
        Returns:
            List of FAQ pairs
            
        Raises:
            AIProcessingError: If FAQ generation fails
        """
        try:
            # Prepare context from analysis
            concepts_context = "\n".join([
                f"- {concept.name}: {concept.description}"
                for concept in analysis.concepts[:8]
            ])
            
            setup_context = "\n".join([
                f"- {step.title}: {step.description}"
                for step in analysis.setup_steps[:5]
            ])
            
            code_examples_context = "\n".join([
                f"- {example.title} ({example.language}): {example.description}"
                for example in analysis.code_examples[:3]
            ])
            
            # Create system prompt
            system_prompt = f"""You are an expert at creating helpful FAQ content for software projects.
Generate question-answer pairs that address common developer concerns and questions.

{self._get_style_context()}

Focus on:
- Questions that new developers commonly ask
- Clear, actionable answers
- Proper categorization of questions
- Confidence levels based on available information
"""
            
            # Create main prompt
            prompt = f"""Based on this repository analysis, generate FAQ question-answer pairs:

Key Concepts:
{concepts_context}

Setup Information:
{setup_context}

Code Examples:
{code_examples_context}

Dependencies: {[dep.name for dep in analysis.dependencies[:5]]}

Generate 6-10 FAQ pairs covering setup, usage, troubleshooting, and development questions.
Return as JSON array with these fields:
- question: Clear question (ending with ?)
- answer: Comprehensive answer
- category: "setup", "usage", "development", "troubleshooting", or "general"
- source_files: Array of relevant file paths
- confidence: Float between 0.0 and 1.0
"""
            
            # Make AI request
            response = self._make_ai_request(prompt, system_prompt, "json")
            
            # Parse response and create FAQPair objects
            faq_data = json.loads(response)
            faqs = []
            
            for faq_dict in faq_data:
                faq = FAQPair(
                    question=faq_dict.get("question", ""),
                    answer=faq_dict.get("answer", ""),
                    category=faq_dict.get("category", "general"),
                    source_files=faq_dict.get("source_files", []),
                    confidence=faq_dict.get("confidence", 0.8)
                )
                faqs.append(faq)
            
            self.logger.info(f"Generated {len(faqs)} FAQ pairs")
            return faqs
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise AIProcessingError(f"Failed to parse FAQ pairs: {e}")
        except Exception as e:
            raise AIProcessingError(f"FAQ generation failed: {e}")
    
    def extract_quick_start_steps(
        self, analysis: RepositoryAnalysis
    ) -> QuickStartGuide:
        """Extract Quick Start guide information from repository analysis.
        
        Args:
            analysis: Repository analysis results
            
        Returns:
            QuickStartGuide object
            
        Raises:
            AIProcessingError: If Quick Start generation fails
        """
        try:
            # Prepare context from analysis
            setup_context = "\n".join([
                f"{i+1}. {step.title}: {step.description}"
                for i, step in enumerate(analysis.setup_steps[:5])
            ])
            
            dependencies_context = ", ".join([
                f"{dep.name}" + (f" ({dep.version})" if dep.version else "")
                for dep in analysis.dependencies[:8]
            ])
            
            examples_context = "\n".join([
                f"- {example.title}: {example.description}"
                for example in analysis.code_examples[:3]
            ])
            
            # Create system prompt
            system_prompt = f"""You are an expert at creating concise Quick Start guides for software projects.
Generate essential setup and usage steps that get developers productive quickly.

{self._get_style_context()}

Focus on:
- Essential prerequisites only
- Minimal viable setup steps
- Basic usage that demonstrates core functionality
- Clear next steps for further learning
"""
            
            # Create main prompt
            prompt = f"""Based on this repository analysis, create a Quick Start guide:

Setup Steps Found:
{setup_context}

Dependencies: {dependencies_context}

Code Examples:
{examples_context}

Key Concepts: {len(analysis.concepts)} concepts identified
File Structure: {len(analysis.file_structure)} files

Generate a Quick Start guide with these sections:
- prerequisites: Essential requirements (tools, versions, etc.)
- setup_steps: Minimal steps to get running
- basic_usage: Simple examples to verify it works
- next_steps: Where to go for more advanced usage

Return as JSON object with arrays for each section.
"""
            
            # Make AI request
            response = self._make_ai_request(prompt, system_prompt, "json")
            
            # Parse response and create QuickStartGuide object
            guide_data = json.loads(response)
            
            guide = QuickStartGuide(
                prerequisites=guide_data.get("prerequisites", []),
                setup_steps=guide_data.get("setup_steps", []),
                basic_usage=guide_data.get("basic_usage", []),
                next_steps=guide_data.get("next_steps", [])
            )
            
            self.logger.info("Generated Quick Start guide")
            return guide
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise AIProcessingError(f"Failed to parse Quick Start guide: {e}")
        except Exception as e:
            raise AIProcessingError(f"Quick Start generation failed: {e}")   
 
    def analyze_feature_code(self, feature_path: str) -> FeatureAnalysis:
        """Analyze a specific feature's code structure and complexity.
        
        Args:
            feature_path: Path to the feature file
            
        Returns:
            FeatureAnalysis object
            
        Raises:
            AIProcessingError: If feature analysis fails
        """
        try:
            # Read the feature file
            try:
                with open(feature_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
            except (FileNotFoundError, IOError) as e:
                raise AIProcessingError(f"Could not read feature file {feature_path}: {e}")
            
            # Look for corresponding test file
            test_content = ""
            test_path = feature_path.replace('features/', 'tests/test_').replace('.py', '.py')
            try:
                with open(test_path, 'r', encoding='utf-8') as f:
                    test_content = f.read()
            except (FileNotFoundError, IOError):
                # Test file not found, continue without it
                pass
            
            # Create system prompt
            system_prompt = f"""You are an expert code analyzer. Analyze Python code to extract:
- Function names and signatures
- Class names and methods
- Test function names
- Documentation and docstrings
- Code complexity assessment

{self._get_style_context()}

Focus on:
- Identifying all public functions and classes
- Understanding test coverage patterns
- Assessing complexity for onboarding purposes
"""
            
            # Create main prompt
            prompt = f"""Analyze this Python feature code:

Feature File: {feature_path}
```python
{code_content[:2000]}  # Limit content to avoid token limits
```

Test File Content:
```python
{test_content[:1000] if test_content else "No test file found"}
```

Extract and return as JSON:
- functions: Array of function names found in the feature
- classes: Array of class names found in the feature
- tests: Array of test function names found in test file
- documentation: Summary of docstrings and comments
- complexity: "low", "medium", "high", or "very_high" based on code structure

Analyze the code structure, identify key components, and assess learning complexity.
"""
            
            # Make AI request
            response = self._make_ai_request(prompt, system_prompt, "json")
            
            # Parse response and create FeatureAnalysis object
            analysis_data = json.loads(response)
            
            analysis = FeatureAnalysis(
                feature_path=feature_path,
                functions=analysis_data.get("functions", []),
                classes=analysis_data.get("classes", []),
                tests=analysis_data.get("tests", []),
                documentation=analysis_data.get("documentation", ""),
                complexity=analysis_data.get("complexity", "medium")
            )
            
            self.logger.info(f"Analyzed feature {feature_path}: {len(analysis.functions)} functions, {len(analysis.classes)} classes")
            return analysis
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise AIProcessingError(f"Failed to parse feature analysis: {e}")
        except Exception as e:
            raise AIProcessingError(f"Feature analysis failed: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current AI model configuration.
        
        Returns:
            Dictionary with model configuration details
        """
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "style_config_loaded": bool(self.style_config.code_style_content)
        }
    
    def update_style_config(self, style_config: StyleConfig) -> None:
        """Update the style configuration.
        
        Args:
            style_config: New style configuration
        """
        self.style_config = style_config
        if not self.style_config.code_style_content:
            self.style_config.load_content()
        self.logger.info("Updated style configuration")