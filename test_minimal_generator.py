#!/usr/bin/env python3
"""Minimal test of task generator."""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Task:
    """Simple task."""
    title: str
    description: str = ""
    number: Optional[int] = None

class SimpleTaskGenerator:
    """Simple task generator."""
    
    def format_tasks_markdown(self, tasks: List[Task]) -> str:
        """Format tasks as markdown."""
        if not tasks:
            return "# No tasks\n"
        
        lines = ["# Tasks", ""]
        for task in tasks:
            lines.append(f"## {task.title}")
            if task.description:
                lines.append(task.description)
            lines.append("")
        
        return "\n".join(lines)

# Test it
if __name__ == "__main__":
    gen = SimpleTaskGenerator()
    print("Has method:", hasattr(gen, 'format_tasks_markdown'))
    
    sample_task = Task(title="Test Task", description="Test description")
    result = gen.format_tasks_markdown([sample_task])
    print("Result length:", len(result))
    print("Result:")
    print(result)