#!/usr/bin/env python3
"""Fix sample repositories to use UTF-8 encoding for all text files."""

import re
from pathlib import Path

def fix_write_text_calls():
    """Add UTF-8 encoding to all write_text calls in sample repositories."""
    file_path = Path("tests/fixtures/sample_repositories.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Pattern to match write_text calls without encoding parameter
    pattern = r'\.write_text\(([^)]+)\)(?!\s*,\s*encoding=)'
    
    def replacement(match):
        args = match.group(1)
        # If it's a simple string, add encoding
        if not ', encoding=' in args:
            return f'.write_text({args}, encoding=\'utf-8\')'
        return match.group(0)
    
    # Replace all write_text calls
    fixed_content = re.sub(pattern, replacement, content)
    
    # Write back with UTF-8 encoding
    file_path.write_text(fixed_content, encoding='utf-8')
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_write_text_calls()