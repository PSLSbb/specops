"""Minimal task generation component for testing."""

import logging
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class MinimalTask:
    """Minimal task representation."""
    title: str
    number: Optional[int] = None


@dataclass
class MinimalTaskDocument:
    """Minimal task document."""
    tasks: List[MinimalTask] = field(default_factory=list)


class MinimalTaskGenerator:
    """Minimal task generator."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_task(self, title: str) -> MinimalTask:
        """Create a minimal task."""
        return MinimalTask(title=title)
    
    def create_document(self) -> MinimalTaskDocument:
        """Create a minimal document."""
        return MinimalTaskDocument()


# Test if this works
if __name__ == "__main__":
    generator = MinimalTaskGenerator()
    task = generator.create_task("Test Task")
    doc = generator.create_document()
    doc.tasks.append(task)
    print(f"Created task: {task.title}")
    print(f"Document has {len(doc.tasks)} tasks")