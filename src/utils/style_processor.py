"""Style processing and compliance system for SpecOps generated content."""

import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from ..models import StyleConfig, ValidationError


@dataclass
class StyleViolation:
    """Represents a style guideline violation."""
    rule: str
    description: str
    line_number: Optional[int] = None
    severity: str = 'warning'  # 'error', 'warning', 'info'
    suggestion: Optional[str] = None


@dataclass
class StyleValidationResult:
    """Results from style validation."""
    is_compliant: bool
    violations: List[StyleViolation]
    corrected_content: Optional[str] = None


class StyleProcessor:
    """Processes and validates content against steering guidelines."""
    
    def __init__(self, style_config: Optional[StyleConfig] = None):
        """Initialize the style processor with configuration."""
        self.style_config = style_config or StyleConfig()
        # Load content if not already loaded
        if not self.style_config.code_style_content:
            self.style_config.load_content()
        
        # Cache parsed rules for performance
        self._code_rules_cache: Optional[List[str]] = None
        self._structure_rules_cache: Optional[List[str]] = None
        self._onboarding_rules_cache: Optional[List[str]] = None
        
    def load_steering_guidelines(self) -> None:
        """Load and parse steering guidelines from .kiro/steering files."""
        self.style_config.load_content()
        # Clear caches to force re-parsing
        self._code_rules_cache = None
        self._structure_rules_cache = None
        self._onboarding_rules_cache = None
    
    def get_code_style_rules(self) -> List[str]:
        """Get parsed code style rules."""
        if self._code_rules_cache is None:
            self._code_rules_cache = self.style_config.get_code_style_rules()
        return self._code_rules_cache
    
    def get_structure_rules(self) -> List[str]:
        """Get parsed structure rules."""
        if self._structure_rules_cache is None:
            self._structure_rules_cache = self.style_config.get_structure_rules()
        return self._structure_rules_cache
    
    def get_onboarding_rules(self) -> List[str]:
        """Get parsed onboarding style rules."""
        if self._onboarding_rules_cache is None:
            self._onboarding_rules_cache = self.style_config.get_onboarding_rules()
        return self._onboarding_rules_cache
    
    def validate_code_style(self, content: str, file_path: str = '') -> StyleValidationResult:
        """Validate content against code style guidelines."""
        violations = []
        corrected_lines = []
        lines = content.split('\n')
        
        code_rules = self.get_code_style_rules()
        
        for line_num, line in enumerate(lines, 1):
            corrected_line = line
            
            # Check line length (88 characters for black standard)
            if len(line) > 88:
                violations.append(StyleViolation(
                    rule="line_length",
                    description=f"Line exceeds 88 characters ({len(line)} chars)",
                    line_number=line_num,
                    severity="warning",
                    suggestion="Break line into multiple lines"
                ))
            
            # Check for snake_case in function/variable names
            if re.search(r'def\s+[A-Z]', line) or re.search(r'^\s*[A-Z][a-zA-Z]*\s*=', line):
                violations.append(StyleViolation(
                    rule="snake_case",
                    description="Use snake_case for functions and variables",
                    line_number=line_num,
                    severity="error",
                    suggestion="Convert to snake_case naming"
                ))
            
            # Check for PascalCase in class names
            class_match = re.search(r'class\s+([a-z][a-zA-Z]*)', line)
            if class_match:
                violations.append(StyleViolation(
                    rule="pascal_case",
                    description="Use PascalCase for class names",
                    line_number=line_num,
                    severity="error",
                    suggestion=f"Rename to {class_match.group(1).title()}"
                ))
            
            # Check for missing docstrings
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                # Look ahead for docstring
                next_lines = lines[line_num:line_num+3] if line_num < len(lines) else []
                has_docstring = any('"""' in next_line or "'''" in next_line for next_line in next_lines)
                if not has_docstring:
                    violations.append(StyleViolation(
                        rule="docstring_required",
                        description="Docstring required for functions and classes",
                        line_number=line_num,
                        severity="warning",
                        suggestion="Add docstring describing the purpose"
                    ))
            
            corrected_lines.append(corrected_line)
        
        is_compliant = not any(v.severity == 'error' for v in violations)
        corrected_content = '\n'.join(corrected_lines) if violations else None
        
        return StyleValidationResult(
            is_compliant=is_compliant,
            violations=violations,
            corrected_content=corrected_content
        )
    
    def validate_structure_compliance(self, file_path: str) -> StyleValidationResult:
        """Validate file structure against structure guidelines."""
        violations = []
        path = Path(file_path)
        
        structure_rules = self.get_structure_rules()
        
        # Check if file is in correct directory structure
        if path.suffix == '.py':
            # Normalize path separators for cross-platform compatibility
            normalized_path = str(path).replace('\\', '/')
            
            # Check for misplaced src files (should be in src/ but aren't)
            if ('src/' not in normalized_path and 
                not normalized_path.startswith('tests/') and 
                not normalized_path.startswith('features/') and
                not path.name.startswith('test_') and
                not path.name.startswith('feature_')):
                violations.append(StyleViolation(
                    rule="src_structure",
                    description="Core implementation should be in src/ directory",
                    severity="error",
                    suggestion="Move file to src/ directory"
                ))
            
            # Check for misplaced test files
            if 'test_' in path.name and not normalized_path.startswith('tests/'):
                violations.append(StyleViolation(
                    rule="test_structure",
                    description="Test files should be in tests/ directory",
                    severity="error",
                    suggestion="Move test file to tests/ directory"
                ))
            
            # Check for misplaced feature files
            if path.name.startswith('feature_') and not normalized_path.startswith('features/'):
                violations.append(StyleViolation(
                    rule="feature_structure",
                    description="Feature files should be in features/ directory",
                    severity="warning",
                    suggestion="Move feature file to features/ directory"
                ))
        
        # Check for __init__.py files in Python packages (simplified check)
        if (path.suffix == '.py' and 
            '/' in str(path).replace('\\', '/') and 
            any(dir_name in str(path) for dir_name in ['src', 'tests', 'features'])):
            # This is a simplified check - in real implementation would check file system
            normalized_path = str(path).replace('\\', '/')
            parent_parts = normalized_path.split('/')[:-1]  # Remove filename
            if len(parent_parts) > 1:  # Has subdirectories
                # Check if it's a nested module (not just src/, tests/, features/)
                if parent_parts[-1] not in ['src', 'tests', 'features']:
                    violations.append(StyleViolation(
                        rule="init_file_required",
                        description="__init__.py file required for Python packages",
                        severity="warning",
                        suggestion=f"Create __init__.py in {'/'.join(parent_parts)}"
                    ))
        
        is_compliant = not any(v.severity == 'error' for v in violations)
        
        return StyleValidationResult(
            is_compliant=is_compliant,
            violations=violations
        )
    
    def validate_onboarding_style(self, content: str, content_type: str = 'markdown') -> StyleValidationResult:
        """Validate content against onboarding style guidelines."""
        violations = []
        corrected_lines = []
        lines = content.split('\n')
        
        onboarding_rules = self.get_onboarding_rules()
        
        for line_num, line in enumerate(lines, 1):
            corrected_line = line
            
            # Check for friendly, concise language
            if re.search(r'\b(obviously|clearly|simply|just|merely)\b', line.lower()):
                violations.append(StyleViolation(
                    rule="friendly_language",
                    description="Avoid assumptive language like 'obviously', 'clearly', 'simply'",
                    line_number=line_num,
                    severity="warning",
                    suggestion="Use more inclusive language"
                ))
            
            # Check for numbered tasks
            if content_type == 'tasks' and re.match(r'^\s*-\s*\[\s*\]\s*\d+\.', line):
                # Good: numbered task format
                pass
            elif content_type == 'tasks' and re.match(r'^\s*-\s*\[\s*\]', line) and not re.search(r'\d+\.', line):
                violations.append(StyleViolation(
                    rule="numbered_tasks",
                    description="Tasks should be numbered for clarity",
                    line_number=line_num,
                    severity="info",
                    suggestion="Add task numbering"
                ))
            
            # Check for actionable language
            if content_type == 'tasks' and line.strip().startswith('- [ ]'):
                task_text = re.sub(r'^\s*-\s*\[\s*\]\s*\d*\.?\s*', '', line).strip()
                if not re.match(r'^[A-Z][a-z]+\s+', task_text):  # Should start with action verb
                    violations.append(StyleViolation(
                        rule="actionable_tasks",
                        description="Tasks should start with action verbs",
                        line_number=line_num,
                        severity="info",
                        suggestion="Start with verbs like 'Create', 'Implement', 'Add', etc."
                    ))
            
            # Check for bold highlighting of important points
            if re.search(r'\b(important|note|warning|caution)\b', line.lower()) and '**' not in line:
                corrected_line = re.sub(
                    r'\b(important|note|warning|caution)\b',
                    r'**\1**',
                    line,
                    flags=re.IGNORECASE
                )
                violations.append(StyleViolation(
                    rule="highlight_important",
                    description="Important points should be highlighted in bold",
                    line_number=line_num,
                    severity="info",
                    suggestion="Use **bold** for important points"
                ))
            
            corrected_lines.append(corrected_line)
        
        # Only consider errors for compliance, not warnings or info
        is_compliant = not any(v.severity == 'error' for v in violations)
        corrected_content = '\n'.join(corrected_lines) if any(corrected_line != original_line for corrected_line, original_line in zip(corrected_lines, lines)) else None
        
        return StyleValidationResult(
            is_compliant=is_compliant,
            violations=violations,
            corrected_content=corrected_content
        )
    
    def apply_style_corrections(self, content: str, content_type: str = 'markdown', file_path: str = '') -> str:
        """Apply automatic style corrections to content."""
        corrected_content = content
        
        # Apply code style corrections
        if content_type == 'python':
            result = self.validate_code_style(content, file_path)
            if result.corrected_content:
                corrected_content = result.corrected_content
        
        # Apply onboarding style corrections
        if content_type in ['markdown', 'tasks', 'faq']:
            result = self.validate_onboarding_style(corrected_content, content_type)
            if result.corrected_content:
                corrected_content = result.corrected_content
        
        return corrected_content
    
    def validate_all_styles(self, content: str, content_type: str = 'markdown', file_path: str = '') -> StyleValidationResult:
        """Validate content against all applicable style guidelines."""
        all_violations = []
        final_content = content
        
        # Validate structure if file path provided
        if file_path:
            structure_result = self.validate_structure_compliance(file_path)
            all_violations.extend(structure_result.violations)
        
        # Validate code style for Python content
        if content_type == 'python':
            code_result = self.validate_code_style(content, file_path)
            all_violations.extend(code_result.violations)
            if code_result.corrected_content:
                final_content = code_result.corrected_content
        
        # Validate onboarding style for documentation content
        if content_type in ['markdown', 'tasks', 'faq']:
            onboarding_result = self.validate_onboarding_style(final_content, content_type)
            all_violations.extend(onboarding_result.violations)
            if onboarding_result.corrected_content:
                final_content = onboarding_result.corrected_content
        
        is_compliant = not any(v.severity == 'error' for v in all_violations)
        
        return StyleValidationResult(
            is_compliant=is_compliant,
            violations=all_violations,
            corrected_content=final_content if final_content != content else None
        )
    
    def get_style_summary(self) -> Dict[str, Any]:
        """Get a summary of loaded style guidelines."""
        return {
            'code_style_rules': self.get_code_style_rules(),
            'structure_rules': self.get_structure_rules(),
            'onboarding_rules': self.get_onboarding_rules(),
            'config_paths': {
                'code_style': self.style_config.code_style_path,
                'structure': self.style_config.structure_style_path,
                'onboarding': self.style_config.onboarding_style_path
            }
        }
    
    def format_violations_report(self, violations: List[StyleViolation]) -> str:
        """Format style violations into a readable report."""
        if not violations:
            return "✅ No style violations found."
        
        report_lines = ["📋 Style Validation Report", "=" * 30, ""]
        
        # Group by severity
        errors = [v for v in violations if v.severity == 'error']
        warnings = [v for v in violations if v.severity == 'warning']
        info = [v for v in violations if v.severity == 'info']
        
        for severity, items in [('Errors', errors), ('Warnings', warnings), ('Info', info)]:
            if items:
                report_lines.append(f"{severity} ({len(items)}):")
                for violation in items:
                    line_info = f" (line {violation.line_number})" if violation.line_number else ""
                    report_lines.append(f"  • {violation.rule}: {violation.description}{line_info}")
                    if violation.suggestion:
                        report_lines.append(f"    💡 {violation.suggestion}")
                report_lines.append("")
        
        return "\n".join(report_lines)