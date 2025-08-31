"""Test version of task generator without model imports."""

import logging
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class TestTask:
    """Test task class."""
    title: str
    number: Optional[int] = None


@dataclass
class TestTaskDocument:
    """Test task document class."""
    tasks: List[TestTask] = field(default_factory=list)


class TestTaskGenerator:
    """Test task generator class."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_task(self, title: str) -> TestTask:
        """Create a test task."""
        return TestTask(title=title)


# Test if this can be imported
if __name__ == "__main__":
    generator = TestTaskGenerator()
    task = generator.create_task("Test")
    print(f"Created task: {task.title}")