#!/usr/bin/env python3
"""Test script to debug import issues."""

try:
    print("Testing basic imports...")
    import logging
    from typing import List, Dict, Any, Optional, Tuple
    from pathlib import Path
    from dataclasses import dataclass
    print("Basic imports successful")
    
    print("Testing model imports...")
    from src.models import TaskSuggestion, FeatureAnalysis
    print("Model imports successful")
    
    print("Testing interface imports...")
    from src.interfaces import TaskGeneratorInterface
    print("Interface imports successful")
    
    print("Testing task generator module import...")
    import src.generators.task_generator as tg_module
    print(f"Module attributes: {[attr for attr in dir(tg_module) if not attr.startswith('_')]}")
    
    print("Testing direct class definitions...")
    
    @dataclass
    class TestTaskDocument:
        tasks: List['TestTask'] = None
        next_task_number: int = 1
        
        def __post_init__(self):
            if self.tasks is None:
                self.tasks = []
    
    print("TestTaskDocument created successfully")
    
    @dataclass
    class TestTask:
        title: str
        description: str = ""
        acceptance_criteria: List[str] = None
        prerequisites: List[str] = None
        requirements_refs: List[str] = None
        estimated_time: int = 30
        difficulty: str = "medium"
        number: Optional[int] = None
        parent_number: Optional[int] = None
        subtasks: List['TestTask'] = None
        completed: bool = False
        
        def __post_init__(self):
            if self.acceptance_criteria is None:
                self.acceptance_criteria = []
            if self.prerequisites is None:
                self.prerequisites = []
            if self.requirements_refs is None:
                self.requirements_refs = []
            if self.subtasks is None:
                self.subtasks = []
    
    print("TestTask created successfully")
    
    # Test creating instances
    task = TestTask(title="Test Task")
    doc = TestTaskDocument()
    print("Test instances created successfully")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()