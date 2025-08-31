#!/usr/bin/env python3
"""Fresh import test."""

import sys
import os

# Clear all modules related to task_generator
modules_to_clear = [k for k in sys.modules.keys() if 'task_generator' in k]
for module in modules_to_clear:
    del sys.modules[module]

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Import fresh
from src.generators.task_generator import TaskGenerator

print(f"TaskGenerator: {TaskGenerator}")
print(f"Methods: {[m for m in dir(TaskGenerator) if not m.startswith('_')]}")

# Try to create instance
try:
    generator = TaskGenerator(style_config=None)
    print("✓ Successfully created TaskGenerator with style_config")
    print(f"Generator has logger: {hasattr(generator, 'logger')}")
    print(f"Generator has style_config: {hasattr(generator, 'style_config')}")
except Exception as e:
    print(f"✗ Failed to create TaskGenerator: {e}")
    import traceback
    traceback.print_exc()