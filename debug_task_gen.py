#!/usr/bin/env python3
"""Debug script for task generator import issues."""

import sys
import traceback

try:
    print("Step 1: Testing basic imports...")
    import logging
    from typing import List, Dict, Any, Optional, Tuple
    from pathlib import Path
    from dataclasses import dataclass, field
    print("✓ Basic imports successful")
    
    print("Step 2: Testing model imports...")
    from src.models import TaskSuggestion, FeatureAnalysis
    print("✓ Model imports successful")
    
    print("Step 3: Testing interface imports...")
    from src.interfaces import TaskGeneratorInterface
    print("✓ Interface imports successful")
    
    print("Step 4: Testing module import...")
    import src.generators.task_generator
    print("✓ Module import successful")
    
    print("Step 5: Checking module contents...")
    module_attrs = [attr for attr in dir(src.generators.task_generator) if not attr.startswith('_')]
    print(f"Module attributes: {module_attrs}")
    
    print("Step 6: Testing direct execution of module...")
    exec(open('src/generators/task_generator.py').read())
    print("✓ Direct execution successful")
    
    print("Step 7: Testing class definitions...")
    # Try to access the classes that should be defined
    if hasattr(src.generators.task_generator, 'Task'):
        print("✓ Task class found")
    else:
        print("✗ Task class not found")
        
    if hasattr(src.generators.task_generator, 'TaskDocument'):
        print("✓ TaskDocument class found")
    else:
        print("✗ TaskDocument class not found")
        
    if hasattr(src.generators.task_generator, 'TaskGenerator'):
        print("✓ TaskGenerator class found")
    else:
        print("✗ TaskGenerator class not found")

except Exception as e:
    print(f"Error at step: {e}")
    traceback.print_exc()