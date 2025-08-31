"""Task generation component for creating structured onboarding tasks."""

from __future__ import annotations

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field

from src.models import TaskSuggestion, FeatureAnalysis


@dataclass
class Task:
    """Represents a single task with optional subtasks."""
    title: str
    description: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    requirements_refs: List[str] = field(default_factory=list)
    estimated_time: int = 30
    difficulty: str = "medium"
    number: Optional[int] = None
    parent_number: Optional[int] = None
    subtasks: List = field(default_factory=list)
    completed: bool = False


class TaskGenerator:
    """Generates structured onboarding tasks from AI suggestions."""
    
    def __init__(self, style_config: Optional[Any] = None):
        """Initialize the task generator.
        
        Args:
            style_config: Style configuration for task formatting
        """
        self.style_config = style_config
        self.logger = logging.getLogger(__name__)
    
    def generate_onboarding_tasks(self, suggestions: List[TaskSuggestion]) -> List[Task]:
        """Generate structured onboarding tasks from AI suggestions."""
        tasks = []
        for suggestion in suggestions:
            task = Task(
                title=suggestion.title,
                description=suggestion.description,
                acceptance_criteria=suggestion.acceptance_criteria.copy(),
                prerequisites=suggestion.prerequisites.copy(),
                estimated_time=suggestion.estimated_time,
                difficulty=suggestion.difficulty
            )
            tasks.append(task)
        return tasks
