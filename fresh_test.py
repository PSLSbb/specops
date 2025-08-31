#!/usr/bin/env python3
"""Fresh test without any imports."""

import subprocess
import sys

# Test by running a completely fresh Python process
code = '''
import sys
sys.path.insert(0, "src")
from generators.task_generator import TaskGenerator
tg = TaskGenerator()
print("Methods:", [m for m in dir(tg) if not m.startswith("_")])
print("Has format_tasks_markdown:", hasattr(tg, "format_tasks_markdown"))
if hasattr(tg, "format_tasks_markdown"):
    result = tg.format_tasks_markdown([])
    print("Method works:", len(result) > 0)
'''

result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
print("Return code:", result.returncode)