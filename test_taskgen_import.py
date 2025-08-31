#!/usr/bin/env python3
"""Test which TaskGenerator is being imported."""

from src.generators.task_generator import TaskGenerator
import inspect

print(f"TaskGenerator class: {TaskGenerator}")
print(f"TaskGenerator file: {inspect.getfile(TaskGenerator)}")
print(f"TaskGenerator __init__ signature: {inspect.signature(TaskGenerator.__init__)}")

# Try to create an instance
try:
    generator = TaskGenerator()
    print("✓ TaskGenerator() works (no parameters)")
except Exception as e:
    print(f"✗ TaskGenerator() failed: {e}")

try:
    generator = TaskGenerator(style_config=None)
    print("✓ TaskGenerator(style_config=None) works")
except Exception as e:
    print(f"✗ TaskGenerator(style_config=None) failed: {e}")