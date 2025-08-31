"""Utility functions for style validation and compliance checking."""

from typing import List, Dict, Any, Optional
from pathlib import Path

from .style_processor import StyleProcessor, StyleValidationResult
from ..models import StyleConfig


def validate_file_style(file_path: str, style_config: Optional[StyleConfig] = None) -> StyleValidationResult:
    """Validate a single file against all applicable style guidelines.
    
    Args:
        file_path: Path to the file to validate
        style_config: Optional custom style configuration
        
    Returns:
        StyleValidationResult with compliance status and violations
    """
    processor = StyleProcessor(style_config)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (FileNotFoundError, IOError) as e:
        # Return a result indicating file access error
        from .style_processor import StyleViolation
        return StyleValidationResult(
            is_compliant=False,
            violations=[StyleViolation(
                rule="file_access",
                description=f"Could not read file: {e}",
                severity="error",
                suggestion="Check file path and permissions"
            )]
        )
    
    # Determine content type based on file extension
    path = Path(file_path)
    if path.suffix == '.py':
        content_type = 'python'
    elif path.suffix in ['.md', '.markdown']:
        content_type = 'markdown'
    else:
        content_type = 'text'
    
    return processor.validate_all_styles(content, content_type, file_path)


def validate_directory_style(
    directory_path: str, 
    file_patterns: Optional[List[str]] = None,
    style_config: Optional[StyleConfig] = None
) -> Dict[str, StyleValidationResult]:
    """Validate all files in a directory against style guidelines.
    
    Args:
        directory_path: Path to directory to validate
        file_patterns: Optional list of file patterns to include (e.g., ['*.py', '*.md'])
        style_config: Optional custom style configuration
        
    Returns:
        Dictionary mapping file paths to validation results
    """
    results = {}
    directory = Path(directory_path)
    
    if not directory.exists() or not directory.is_dir():
        return results
    
    # Default patterns if none provided
    if file_patterns is None:
        file_patterns = ['*.py', '*.md', '*.markdown']
    
    # Find all matching files
    files_to_validate = []
    for pattern in file_patterns:
        files_to_validate.extend(directory.rglob(pattern))
    
    # Validate each file
    for file_path in files_to_validate:
        if file_path.is_file():
            result = validate_file_style(str(file_path), style_config)
            results[str(file_path)] = result
    
    return results


def generate_style_report(
    validation_results: Dict[str, StyleValidationResult],
    include_compliant: bool = False
) -> str:
    """Generate a comprehensive style validation report.
    
    Args:
        validation_results: Dictionary of file paths to validation results
        include_compliant: Whether to include compliant files in the report
        
    Returns:
        Formatted report string
    """
    processor = StyleProcessor()
    
    report_lines = [
        "📋 Style Validation Report",
        "=" * 50,
        ""
    ]
    
    # Summary statistics
    total_files = len(validation_results)
    compliant_files = sum(1 for result in validation_results.values() if result.is_compliant)
    non_compliant_files = total_files - compliant_files
    total_violations = sum(len(result.violations) for result in validation_results.values())
    
    report_lines.extend([
        f"📊 Summary:",
        f"  • Total files checked: {total_files}",
        f"  • Compliant files: {compliant_files}",
        f"  • Non-compliant files: {non_compliant_files}",
        f"  • Total violations: {total_violations}",
        ""
    ])
    
    # Group violations by severity
    all_violations = []
    for file_path, result in validation_results.items():
        for violation in result.violations:
            all_violations.append((file_path, violation))
    
    errors = [(f, v) for f, v in all_violations if v.severity == 'error']
    warnings = [(f, v) for f, v in all_violations if v.severity == 'warning']
    info = [(f, v) for f, v in all_violations if v.severity == 'info']
    
    # Report by severity
    for severity, items, emoji in [
        ('Errors', errors, '❌'),
        ('Warnings', warnings, '⚠️'),
        ('Info', info, 'ℹ️')
    ]:
        if items:
            report_lines.append(f"{emoji} {severity} ({len(items)}):")
            for file_path, violation in items:
                line_info = f" (line {violation.line_number})" if violation.line_number else ""
                report_lines.append(f"  📁 {file_path}{line_info}")
                report_lines.append(f"     • {violation.rule}: {violation.description}")
                if violation.suggestion:
                    report_lines.append(f"     💡 {violation.suggestion}")
            report_lines.append("")
    
    # List compliant files if requested
    if include_compliant:
        compliant_files_list = [
            file_path for file_path, result in validation_results.items() 
            if result.is_compliant and not result.violations
        ]
        if compliant_files_list:
            report_lines.extend([
                "✅ Fully Compliant Files:",
                *[f"  📁 {file_path}" for file_path in compliant_files_list],
                ""
            ])
    
    # Recommendations
    if non_compliant_files > 0:
        report_lines.extend([
            "🔧 Recommendations:",
            "  • Fix error-level violations first (they prevent compliance)",
            "  • Address warnings to improve code quality",
            "  • Consider info-level suggestions for best practices",
            "  • Use automatic style corrections where available",
            ""
        ])
    else:
        report_lines.extend([
            "🎉 All files are compliant with style guidelines!",
            ""
        ])
    
    return "\n".join(report_lines)


def apply_automatic_corrections(
    file_path: str,
    style_config: Optional[StyleConfig] = None,
    backup: bool = True
) -> bool:
    """Apply automatic style corrections to a file.
    
    Args:
        file_path: Path to the file to correct
        style_config: Optional custom style configuration
        backup: Whether to create a backup of the original file
        
    Returns:
        True if corrections were applied, False otherwise
    """
    processor = StyleProcessor(style_config)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except (FileNotFoundError, IOError):
        return False
    
    # Determine content type
    path = Path(file_path)
    if path.suffix == '.py':
        content_type = 'python'
    elif path.suffix in ['.md', '.markdown']:
        content_type = 'markdown'
    else:
        content_type = 'text'
    
    # Apply corrections
    corrected_content = processor.apply_style_corrections(
        original_content, 
        content_type, 
        file_path
    )
    
    # Check if any changes were made
    if corrected_content == original_content:
        return False
    
    # Create backup if requested
    if backup:
        backup_path = f"{file_path}.backup"
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
        except IOError:
            # If backup fails, don't proceed with corrections
            return False
    
    # Write corrected content
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(corrected_content)
        return True
    except IOError:
        # If writing fails and we made a backup, restore it
        if backup and Path(f"{file_path}.backup").exists():
            try:
                with open(f"{file_path}.backup", 'r', encoding='utf-8') as f:
                    original = f.read()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(original)
            except IOError:
                pass  # Best effort to restore
        return False


def get_style_guidelines_summary(style_config: Optional[StyleConfig] = None) -> str:
    """Get a formatted summary of all style guidelines.
    
    Args:
        style_config: Optional custom style configuration
        
    Returns:
        Formatted summary of style guidelines
    """
    processor = StyleProcessor(style_config)
    summary = processor.get_style_summary()
    
    lines = [
        "📋 Style Guidelines Summary",
        "=" * 40,
        ""
    ]
    
    # Code style rules
    if summary['code_style_rules']:
        lines.extend([
            "🐍 Code Style Rules:",
            *[f"  • {rule}" for rule in summary['code_style_rules']],
            ""
        ])
    
    # Structure rules
    if summary['structure_rules']:
        lines.extend([
            "📁 Project Structure Rules:",
            *[f"  • {rule}" for rule in summary['structure_rules']],
            ""
        ])
    
    # Onboarding rules
    if summary['onboarding_rules']:
        lines.extend([
            "📚 Onboarding Style Rules:",
            *[f"  • {rule}" for rule in summary['onboarding_rules']],
            ""
        ])
    
    # Configuration paths
    lines.extend([
        "⚙️ Configuration Files:",
        f"  • Code Style: {summary['config_paths']['code_style']}",
        f"  • Structure: {summary['config_paths']['structure']}",
        f"  • Onboarding: {summary['config_paths']['onboarding']}",
        ""
    ])
    
    return "\n".join(lines)