#!/usr/bin/env python3
"""Fix dependency types in dependency_analyzer.py"""

import re

# Read the file
with open('src/analyzers/dependency_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all language-specific types with valid types
replacements = {
    "type='python'": "type='runtime'",
    "type='javascript'": "type='runtime'", 
    "type='ruby'": "type='runtime'",
    "type='rust'": "type='runtime'",
    "type='go'": "type='runtime'",
    "type='php'": "type='runtime'"
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Write back
with open('src/analyzers/dependency_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed dependency types!")