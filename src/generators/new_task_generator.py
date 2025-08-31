"""New task generation component."""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a single task."""
    title: str


class TaskGenerator:
    """Generates tasks."""
    
    def create_task(self, title: str) -> Task:
        """Create a task."""
        return Task(title=title)


if __name__ == "__main__":
    print("Classes defined successfully!")
    task = Task(title="Test")
    generator = TaskGenerator()
    print(f"Task: {task.title}")
    print(f"Generator: {generator}")