"""Debug version of task generator."""

print("Starting imports...")

import logging
from typing import List, Optional
from dataclasses import dataclass, field

print("Basic imports done...")

from src.models import TaskSuggestion, FeatureAnalysis

print("Model imports done...")


@dataclass
class DebugTask:
    """Debug task class."""
    title: str
    number: Optional[int] = None

print("DebugTask class defined...")


@dataclass
class DebugTaskDocument:
    """Debug task document class."""
    tasks: List[DebugTask] = field(default_factory=list)

print("DebugTaskDocument class defined...")


class DebugTaskGenerator:
    """Debug task generator class."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_task(self, title: str) -> DebugTask:
        """Create a debug task."""
        return DebugTask(title=title)

print("DebugTaskGenerator class defined...")

print("All classes defined successfully!")


# Test if this can be imported
if __name__ == "__main__":
    generator = DebugTaskGenerator()
    task = generator.create_task("Test")
    print(f"Created task: {task.title}")