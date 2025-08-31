#!/usr/bin/env python3
"""Simple test of task generator classes without inheritance."""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
import logging

# Import models directly
from src.models import TaskSuggestion, FeatureAnalysis

@dataclass
class SimpleTask:
    """Simple task class for testing."""
    title: str
    description: str = ""
    number: Optional[int] = None

@dataclass  
class SimpleTaskDocument:
    """Simple task document for testing."""
    tasks: List[SimpleTask] = field(default_factory=list)
    next_task_number: int = 1

class SimpleTaskGenerator:
    """Simple task generator for testing."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_onboarding_tasks(self, suggestions: List[TaskSuggestion]) -> SimpleTaskDocument:
        """Generate simple tasks."""
        doc = SimpleTaskDocument()
        for suggestion in suggestions:
            task = SimpleTask(title=suggestion.title, description=suggestion.description)
            doc.tasks.append(task)
        return doc

# Test the classes
if __name__ == "__main__":
    print("Testing simple classes...")
    
    # Create test suggestion
    suggestion = TaskSuggestion(
        title="Test Task",
        description="A test task",
        acceptance_criteria=["Test criterion"],
        prerequisites=[],
        estimated_time=30,
        difficulty="easy"
    )
    
    # Create generator and test
    generator = SimpleTaskGenerator()
    doc = generator.generate_onboarding_tasks([suggestion])
    
    print(f"Generated {len(doc.tasks)} tasks")
    print(f"First task: {doc.tasks[0].title}")
    print("✓ Simple classes work correctly")