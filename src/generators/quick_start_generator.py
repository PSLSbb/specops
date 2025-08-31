"""Quick Start Generator component for SpecOps onboarding factory."""

import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field

from ..models import QuickStartGuide, StyleConfig, ValidationError
from ..interfaces import QuickStartGeneratorInterface


@dataclass
class ReadmeSection:
    """Represents a section in a README file."""
    title: str
    content: str
    start_line: int
    end_line: int
    level: int  # Header level (1-6)


class QuickStartGenerator(QuickStartGeneratorInterface):
    """Generates and manages Quick Start sections in README files."""
    
    def __init__(self, style_config: Optional[StyleConfig] = None):
        """Initialize Quick Start generator with optional style configuration."""
        self.style_config = style_config or StyleConfig()
        self._quick_start_titles = [
            'quick start',
            'quickstart', 
            'getting started',
            'get started',
            'quick setup',
            'setup',
            'installation'
        ]
    
    def generate_quick_start(self, guide: QuickStartGuide) -> str:
        """Generate Quick Start content from guide data."""
        if guide.is_empty():
            return self._generate_empty_quick_start()
        
        # Apply style processing
        self._apply_style_guidelines(guide)
        
        # Format as markdown
        return self._format_quick_start_markdown(guide)
    
    def update_readme_section(self, readme_path: str, quick_start_content: str) -> None:
        """Update README file with new Quick Start content while preserving other sections."""
        try:
            # Read existing README content
            readme_content = self._read_readme_file(readme_path)
            
            # Parse README sections
            sections = self._parse_readme_sections(readme_content)
            
            # Find or create Quick Start section
            quick_start_section = self._find_quick_start_section(sections)
            
            if quick_start_section:
                # Update existing section
                updated_content = self._replace_section_content(
                    readme_content, quick_start_section, quick_start_content
                )
            else:
                # Insert new Quick Start section
                updated_content = self._insert_quick_start_section(
                    readme_content, sections, quick_start_content
                )
            
            # Write updated content back to file
            self._write_readme_file(readme_path, updated_content)
            
        except Exception as e:
            raise ValidationError(f"Failed to update README section: {e}")
    
    def extract_essential_steps(self, content: str) -> List[str]:
        """Extract essential setup and usage steps from content."""
        steps = []
        
        # Look for numbered lists, bullet points, and step indicators
        step_patterns = [
            r'^\s*\d+\.\s+(.+)$',  # Numbered lists
            r'^\s*[-*]\s+(.+)$',   # Bullet points
            r'^\s*Step\s+\d+[:\s]+(.+)$',  # Step indicators
            r'^\s*First[,\s]+(.+)$',  # First, then patterns
            r'^\s*Then[,\s]+(.+)$',
            r'^\s*Next[,\s]+(.+)$',
            r'^\s*Finally[,\s]+(.+)$'
        ]
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in step_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    step_text = match.group(1).strip()
                    if step_text and len(step_text) > 10:  # Filter out very short steps
                        steps.append(step_text)
                    break
        
        # Remove duplicates while preserving order
        unique_steps = []
        seen = set()
        for step in steps:
            step_lower = step.lower()
            if step_lower not in seen:
                unique_steps.append(step)
                seen.add(step_lower)
        
        return unique_steps[:10]  # Limit to first 10 steps
    
    def extract_basic_usage_examples(self, content: str) -> List[str]:
        """Extract basic usage examples from content."""
        examples = []
        
        # Look for code blocks and command examples
        code_block_pattern = r'```[\w]*\n(.*?)\n```'
        inline_code_pattern = r'`([^`]+)`'
        
        # Extract code blocks
        code_blocks = re.findall(code_block_pattern, content, re.DOTALL)
        for block in code_blocks:
            block = block.strip()
            if block and len(block) < 200:  # Filter out very long blocks
                examples.append(f"```\n{block}\n```")
        
        # Extract inline code that looks like commands
        inline_codes = re.findall(inline_code_pattern, content)
        for code in inline_codes:
            code = code.strip()
            # Look for command-like patterns
            if any(keyword in code.lower() for keyword in ['start', 'install', 'python', 'npm', 'pip']):
                if len(code) < 100:  # Filter out very long commands
                    examples.append(f"`{code}`")
        
        # Remove duplicates while preserving order
        unique_examples = []
        seen = set()
        for example in examples:
            if example not in seen:
                unique_examples.append(example)
                seen.add(example)
        
        return unique_examples[:5]  # Limit to first 5 examples
    
    def identify_prerequisites(self, content: str) -> List[str]:
        """Identify prerequisites from content."""
        prerequisites = []
        
        # Look for prerequisite indicators
        prereq_patterns = [
            r'(?:prerequisite|requirement)[s]?[:\s]*\n?\s*[-*]?\s*(.+?)(?:\n|$)',
            r'(?:before|first)[,\s]+(?:you\s+)?(?:need|must|should)[,\s]+(.+?)(?:\n|$)',
            r'(?:install|setup)[,\s]+(.+?)(?:\n|$)',
            r'((?:python|node|npm|pip|git)\s+[\d\.]+[+]?)',  # Version requirements
        ]
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for bullet point prerequisites
            if line.startswith(('- ', '* ')) and any(keyword in line.lower() for keyword in ['python', 'node', 'git', 'requirement', 'need']):
                prereq = line[2:].strip()
                if len(prereq) > 3 and len(prereq) < 100:
                    prerequisites.append(prereq)
            
            # Check for other patterns
            for pattern in prereq_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, str):
                        prereq = match.strip().rstrip('.,;')
                        if prereq and len(prereq) > 3 and len(prereq) < 100:
                            prerequisites.append(prereq)
        
        # Remove duplicates while preserving order
        unique_prereqs = []
        seen = set()
        for prereq in prerequisites:
            prereq_lower = prereq.lower()
            if prereq_lower not in seen:
                unique_prereqs.append(prereq)
                seen.add(prereq_lower)
        
        return unique_prereqs[:5]  # Limit to first 5 prerequisites
    
    def _generate_empty_quick_start(self) -> str:
        """Generate an empty Quick Start template."""
        return """## Quick Start

### Prerequisites

*Prerequisites will be automatically identified from repository analysis.*

### Setup

*Setup steps will be automatically generated from repository content.*

### Basic Usage

*Usage examples will be automatically extracted from documentation.*

### Next Steps

*Next steps will be suggested based on project structure and documentation.*

---

*This Quick Start section is automatically generated and updated.*
"""
    
    def _apply_style_guidelines(self, guide: QuickStartGuide) -> None:
        """Apply style guidelines from steering configuration."""
        # Load style rules if not already loaded
        if not self.style_config.onboarding_style_content:
            self.style_config.load_content()
        
        # Apply consistent formatting to all sections
        guide.prerequisites = [self._format_step(step) for step in guide.prerequisites]
        guide.setup_steps = [self._format_step(step) for step in guide.setup_steps]
        guide.basic_usage = [self._format_step(step) for step in guide.basic_usage]
        guide.next_steps = [self._format_step(step) for step in guide.next_steps]
    
    def _format_step(self, step: str) -> str:
        """Format a single step according to style guidelines."""
        if not step:
            return step
        
        # Clean up whitespace
        step = ' '.join(step.strip().split())
        
        # Ensure proper capitalization
        if step and not step[0].isupper():
            step = step[0].upper() + step[1:]
        
        # Apply friendly tone
        step = self._apply_friendly_tone(step)
        
        # Format code examples
        step = self._format_inline_code(step)
        
        return step
    
    def _apply_friendly_tone(self, text: str) -> str:
        """Apply friendly, concise language style."""
        # Replace formal language with friendly alternatives
        friendly_replacements = {
            'execute': 'run',
            'utilize': 'use',
            'commence': 'start',
            'terminate': 'stop',
            'initialize': 'set up',
            'configure': 'set up',
            'it is necessary to': 'you need to',
            'it is recommended': 'we recommend',
            'please ensure': 'make sure',
            'in order to': 'to',
        }
        
        text_lower = text.lower()
        for formal, friendly in friendly_replacements.items():
            if formal in text_lower:
                text = re.sub(re.escape(formal), friendly, text, flags=re.IGNORECASE)
        
        return text
    
    def _format_inline_code(self, text: str) -> str:
        """Format inline code and commands in text."""
        # Don't format text that already has backticks
        if '`' in text:
            return text
            
        # Format file paths and commands that aren't already in backticks
        patterns = [
            (r'\b([a-zA-Z0-9_-]+\.[a-zA-Z]{2,4})\b', r'`\1`'),  # File extensions
            (r'\b(npm|pip|git|python|node)\s+([a-zA-Z0-9_.-]+)', r'`\1 \2`'),  # Commands
            (r'\b(cd|ls|mkdir|rm)\s+([^\s]+)', r'`\1 \2`'),  # Shell commands
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _format_quick_start_markdown(self, guide: QuickStartGuide) -> str:
        """Format Quick Start guide as structured markdown."""
        lines = ["## Quick Start", ""]
        
        # Add prerequisites section
        if guide.prerequisites:
            lines.extend(["### Prerequisites", ""])
            for prereq in guide.prerequisites:
                lines.append(f"- {prereq}")
            lines.append("")
        
        # Add setup steps section
        if guide.setup_steps:
            lines.extend(["### Setup", ""])
            for i, step in enumerate(guide.setup_steps, 1):
                lines.append(f"{i}. {step}")
            lines.append("")
        
        # Add basic usage section
        if guide.basic_usage:
            lines.extend(["### Basic Usage", ""])
            for usage in guide.basic_usage:
                if usage.startswith('```') or usage.startswith('`'):
                    lines.append(usage)
                else:
                    lines.append(f"- {usage}")
            lines.append("")
        
        # Add next steps section
        if guide.next_steps:
            lines.extend(["### Next Steps", ""])
            for step in guide.next_steps:
                lines.append(f"- {step}")
            lines.append("")
        
        # Add footer
        lines.extend([
            "---",
            "",
            "*This Quick Start section is automatically generated and updated.*"
        ])
        
        return "\n".join(lines)
    
    def _read_readme_file(self, readme_path: str) -> str:
        """Read README file content."""
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Create empty README if it doesn't exist
            return "# Project\n\n*Add project description here.*\n"
        except Exception as e:
            raise ValidationError(f"Failed to read README file: {e}")
    
    def _write_readme_file(self, readme_path: str, content: str) -> None:
        """Write content to README file."""
        try:
            # Ensure directory exists
            Path(readme_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise ValidationError(f"Failed to write README file: {e}")
    
    def _parse_readme_sections(self, content: str) -> List[ReadmeSection]:
        """Parse README content into sections."""
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for i, line in enumerate(lines):
            # Check for header lines
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            
            if header_match:
                # Save previous section if exists
                if current_section:
                    current_section.content = '\n'.join(current_content)
                    current_section.end_line = i - 1
                    sections.append(current_section)
                
                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = ReadmeSection(
                    title=title,
                    content="",
                    start_line=i,
                    end_line=i,
                    level=level
                )
                current_content = []
            else:
                # Add line to current section content
                if current_section:
                    current_content.append(line)
        
        # Save final section
        if current_section:
            current_section.content = '\n'.join(current_content)
            current_section.end_line = len(lines) - 1
            sections.append(current_section)
        
        return sections
    
    def _find_quick_start_section(self, sections: List[ReadmeSection]) -> Optional[ReadmeSection]:
        """Find existing Quick Start section in README."""
        for section in sections:
            section_title_lower = section.title.lower()
            for quick_start_title in self._quick_start_titles:
                if quick_start_title in section_title_lower:
                    return section
        return None
    
    def _replace_section_content(
        self, readme_content: str, section: ReadmeSection, new_content: str
    ) -> str:
        """Replace content of an existing section."""
        lines = readme_content.split('\n')
        
        # Find the end of the section (next header at same or higher level, or end of file)
        section_end = len(lines)
        for i in range(section.start_line + 1, len(lines)):
            line = lines[i].strip()
            header_match = re.match(r'^(#{1,6})\s+', line)
            if header_match:
                header_level = len(header_match.group(1))
                if header_level <= section.level:
                    section_end = i
                    break
        
        # Replace section content
        new_lines = (
            lines[:section.start_line] +
            new_content.split('\n') +
            lines[section_end:]
        )
        
        return '\n'.join(new_lines)
    
    def _insert_quick_start_section(
        self, readme_content: str, sections: List[ReadmeSection], quick_start_content: str
    ) -> str:
        """Insert new Quick Start section at appropriate location."""
        lines = readme_content.split('\n')
        
        # Find best insertion point (after title/description, before detailed sections)
        insertion_point = self._find_insertion_point(sections)
        
        if insertion_point is None:
            # Append at the end
            if readme_content.strip():
                return readme_content + '\n\n' + quick_start_content
            else:
                return quick_start_content
        
        # Insert at the determined point
        new_lines = (
            lines[:insertion_point] +
            [''] +  # Add blank line before
            quick_start_content.split('\n') +
            [''] +  # Add blank line after
            lines[insertion_point:]
        )
        
        return '\n'.join(new_lines)
    
    def _find_insertion_point(self, sections: List[ReadmeSection]) -> Optional[int]:
        """Find the best insertion point for Quick Start section."""
        if not sections:
            return None
        
        # Look for sections that should come after Quick Start
        later_sections = [
            'installation', 'usage', 'api', 'documentation', 'examples',
            'contributing', 'license', 'changelog', 'development'
        ]
        
        for section in sections:
            section_title_lower = section.title.lower()
            for later_section in later_sections:
                if later_section in section_title_lower:
                    return section.start_line
        
        # If no good insertion point found, insert after first section (usually title)
        if len(sections) > 1:
            return sections[1].start_line
        
        return None
    
    def validate_quick_start_quality(self, content: str) -> Dict[str, Any]:
        """Validate the quality of Quick Start content."""
        validation_results = {
            'is_valid': True,
            'issues': [],
            'suggestions': [],
            'metrics': {}
        }
        
        lines = content.split('\n')
        
        # Check basic structure
        has_title = any('quick start' in line.lower() for line in lines if line.startswith('#'))
        has_prerequisites = any('prerequisite' in line.lower() for line in lines)
        has_setup = any('setup' in line.lower() for line in lines)
        has_usage = any('usage' in line.lower() for line in lines)
        
        if not has_title:
            validation_results['issues'].append('Missing Quick Start title')
            validation_results['is_valid'] = False
        
        if not has_setup:
            validation_results['suggestions'].append('Consider adding setup instructions')
        
        if not has_usage:
            validation_results['suggestions'].append('Consider adding usage examples')
        
        # Check for code examples
        code_blocks = len(re.findall(r'```', content))
        inline_code = len(re.findall(r'`[^`]+`', content))
        
        if code_blocks == 0 and inline_code == 0:
            validation_results['suggestions'].append('Consider adding code examples')
        
        # Calculate metrics
        validation_results['metrics'] = {
            'total_lines': len(lines),
            'content_lines': len([line for line in lines if line.strip() and not line.startswith('#')]),
            'code_blocks': code_blocks // 2,  # Divide by 2 since ``` appears twice per block
            'inline_code_count': inline_code,
            'has_prerequisites': has_prerequisites,
            'has_setup': has_setup,
            'has_usage': has_usage
        }
        
        return validation_results