#!/usr/bin/env python3
"""Simple runner script for SpecOps."""

import sys
import os
from pathlib import Path

# Add project root to Python path so we can import src as a package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set PYTHONPATH environment variable as well
os.environ['PYTHONPATH'] = str(project_root) + os.pathsep + os.environ.get('PYTHONPATH', '')

# Import and run CLI
from src.cli import main

if __name__ == '__main__':
    sys.exit(main())