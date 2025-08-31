#!/usr/bin/env python3
"""Debug TaskGenerator import issue."""

import sys
import importlib

# Force reload the module
if 'src.generators.task_generator' in sys.modules:
    del sys.modules['src.generators.task_generator']

# Import the module
from src.generators import task_generator
importlib.reload(task_generator)

# Check the class
TaskGenerator = task_generator.TaskGenerator
print(f"TaskGenerator: {TaskGenerator}")
print(f"TaskGenerator methods: {[m for m in dir(TaskGenerator) if not m.startswith('_')]}")

# Check if __init__ exists
if hasattr(TaskGenerator, '__init__'):
    print(f"__init__ method exists: {TaskGenerator.__init__}")
    import inspect
    try:
        sig = inspect.signature(TaskGenerator.__init__)
        print(f"__init__ signature: {sig}")
    except Exception as e:
        print(f"Error getting signature: {e}")

# Try to create instance
try:
    instance = TaskGenerator(style_config=None)
    print("✓ Successfully created TaskGenerator with style_config")
except Exception as e:
    print(f"✗ Failed to create TaskGenerator: {e}")
    
# Check the source
try:
    source = inspect.getsource(TaskGenerator.__init__)
    print(f"__init__ source:\n{source}")
except Exception as e:
    print(f"Error getting source: {e}")