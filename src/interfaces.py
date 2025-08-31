"""Core interfaces and abstract base classes for SpecOps components."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RepositoryAnalysis:
    """Analysis results from repository content scanning."""
    concepts: List['Concept']
    setup_steps: List['SetupStep']
    code_examples: List['CodeExample']
    file_structure: Dict[str, Any]
    dependencies: List['Dependency']


@dataclass
class Concept:
    """A key concept identified in repository content."""
    name: str
    description: str
    importance: int
    related_files: List[str]
    prerequisites: List[str]


@dataclass
class SetupStep:
    """A setup or installation step."""
    title: str
    description: str
    commands: List[str]
    prerequisites: List[str]
    order: int


@dataclass
class CodeExample:
    """A code example found in documentation."""
    title: str
    code: str
    language: str
    description: str
    file_path: str


@dataclass
class Dependency:
    """A project dependency."""
    name: str
    version: Optional[str]
    type: str  # 'runtime', 'dev', 'optional'
    description: str


@dataclass
class TaskSuggestion:
    """AI-generated suggestion for an onboarding task."""
    title: str
    description: str
    acceptance_criteria: List[str]
    prerequisites: List[str]
    estimated_time: int
    difficulty: str


@dataclass
class FAQPair:
    """A question-answer pair for FAQ generation."""
    question: str
    answer: str
    category: str
    source_files: List[str]
    confidence: float


@dataclass
class QuickStartGuide:
    """Structure for Quick Start guide content."""
    prerequisites: List[str]
    setup_steps: List[str]
    basic_usage: List[str]
    next_steps: List[str]


@dataclass
class FeatureAnalysis:
    """Analysis results from a specific feature."""
    feature_path: str
    functions: List[str]
    classes: List[str]
    tests: List[str]
    documentation: str
    complexity: str


class ContentAnalyzerInterface(ABC):
    """Interface for content analysis components."""
    
    @abstractmethod
    def analyze_repository(self, repo_path: str) -> RepositoryAnalysis:
        """Analyze repository content and extract structured information."""
        pass
    
    @abstractmethod
    def extract_concepts(self, markdown_content: str) -> List[Concept]:
        """Extract key concepts from markdown content."""
        pass
    
    @abstractmethod
    def identify_setup_steps(self, content: str) -> List[SetupStep]:
        """Identify setup and installation steps."""
        pass
    
    @abstractmethod
    def find_code_examples(self, content: str) -> List[CodeExample]:
        """Find and extract code examples."""
        pass


class AIProcessingEngineInterface(ABC):
    """Interface for AI processing components."""
    
    @abstractmethod
    def generate_task_suggestions(
        self, analysis: RepositoryAnalysis
    ) -> List[TaskSuggestion]:
        """Generate task suggestions from repository analysis."""
        pass
    
    @abstractmethod
    def create_faq_pairs(self, analysis: RepositoryAnalysis) -> List[FAQPair]:
        """Create FAQ question-answer pairs."""
        pass
    
    @abstractmethod
    def extract_quick_start_steps(
        self, analysis: RepositoryAnalysis
    ) -> QuickStartGuide:
        """Extract Quick Start guide information."""
        pass
    
    @abstractmethod
    def analyze_feature_code(self, feature_path: str) -> FeatureAnalysis:
        """Analyze a specific feature's code."""
        pass


class TaskGeneratorInterface(ABC):
    """Interface for task generation components."""
    
    @abstractmethod
    def generate_onboarding_tasks(
        self, suggestions: List[TaskSuggestion]
    ) -> 'TaskDocument':
        """Generate structured onboarding tasks."""
        pass
    
    @abstractmethod
    def append_feature_tasks(
        self, feature_analysis: FeatureAnalysis, existing_tasks: 'TaskDocument'
    ) -> 'TaskDocument':
        """Append tasks for a new feature to existing task document."""
        pass
    
    @abstractmethod
    def format_tasks_markdown(self, tasks: 'TaskDocument') -> str:
        """Format task document as markdown."""
        pass


class FAQGeneratorInterface(ABC):
    """Interface for FAQ generation components."""
    
    @abstractmethod
    def generate_faqs(self, faq_pairs: List[FAQPair]) -> str:
        """Generate FAQ document content."""
        pass
    
    @abstractmethod
    def merge_with_existing(self, new_content: str, existing_path: str) -> str:
        """Merge new FAQ content with existing file."""
        pass


class QuickStartGeneratorInterface(ABC):
    """Interface for Quick Start generation components."""
    
    @abstractmethod
    def generate_quick_start(self, guide: QuickStartGuide) -> str:
        """Generate Quick Start section content."""
        pass
    
    @abstractmethod
    def update_readme_section(
        self, readme_path: str, quick_start_content: str
    ) -> None:
        """Update README file with Quick Start content."""
        pass


class HookManagerInterface(ABC):
    """Interface for hook management components."""
    
    @abstractmethod
    def register_feature_created_hook(self) -> None:
        """Register the feature-created hook."""
        pass
    
    @abstractmethod
    def register_readme_save_hook(self) -> None:
        """Register the README-save hook."""
        pass
    
    @abstractmethod
    def handle_feature_created(self, feature_path: str) -> None:
        """Handle feature creation event."""
        pass
    
    @abstractmethod
    def handle_readme_saved(self, readme_path: str) -> None:
        """Handle README save event."""
        pass