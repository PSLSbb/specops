"""FAQ Generator component for SpecOps onboarding factory."""

from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import re
from dataclasses import dataclass, field

from ..models import FAQPair, StyleConfig, ValidationError
from ..interfaces import FAQGeneratorInterface


@dataclass
class FAQDocument:
    """Represents a structured FAQ document."""
    categories: Dict[str, List[FAQPair]] = field(default_factory=dict)
    title: str = "Frequently Asked Questions"
    introduction: str = ""
    
    def add_faq_pair(self, faq_pair: FAQPair) -> None:
        """Add an FAQ pair to the appropriate category."""
        if faq_pair.category not in self.categories:
            self.categories[faq_pair.category] = []
        self.categories[faq_pair.category].append(faq_pair)
    
    def get_all_questions(self) -> Set[str]:
        """Get all questions in the document for duplicate detection."""
        questions = set()
        for category_faqs in self.categories.values():
            for faq in category_faqs:
                questions.add(faq.question.lower().strip())
        return questions
    
    def merge_with_pairs(self, new_pairs: List[FAQPair]) -> None:
        """Merge new FAQ pairs, avoiding duplicates."""
        existing_questions = self.get_all_questions()
        
        for pair in new_pairs:
            # Check for duplicates (case-insensitive)
            if pair.question.lower().strip() not in existing_questions:
                self.add_faq_pair(pair)
                existing_questions.add(pair.question.lower().strip())


class FAQGenerator(FAQGeneratorInterface):
    """Generates and manages FAQ documentation."""
    
    def __init__(self, style_config: Optional[StyleConfig] = None):
        """Initialize FAQ generator with optional style configuration."""
        self.style_config = style_config or StyleConfig()
        self._category_order = [
            'getting-started',
            'setup',
            'usage',
            'development',
            'troubleshooting',
            'general'
        ]
    
    def generate_faqs(self, faq_pairs: List[FAQPair]) -> str:
        """Generate FAQ document content from FAQ pairs."""
        if not faq_pairs:
            return self._generate_empty_faq()
        
        # Create FAQ document and organize pairs
        faq_doc = FAQDocument()
        for pair in faq_pairs:
            faq_doc.add_faq_pair(pair)
        
        # Apply style processing
        self._apply_style_guidelines(faq_doc)
        
        # Format as markdown
        return self._format_faq_markdown(faq_doc)
    
    def merge_with_existing(self, new_content: str, existing_path: str) -> str:
        """Merge new FAQ content with existing file while preserving manual additions."""
        try:
            # Parse existing FAQ content
            existing_doc = self._parse_existing_faq(existing_path)
            
            # Parse new content to extract FAQ pairs
            new_pairs = self._extract_faq_pairs_from_content(new_content)
            
            # Merge new pairs with existing document
            existing_doc.merge_with_pairs(new_pairs)
            
            # Apply style processing
            self._apply_style_guidelines(existing_doc)
            
            # Format merged document
            return self._format_faq_markdown(existing_doc)
            
        except FileNotFoundError:
            # If existing file doesn't exist, return new content
            return new_content
        except Exception as e:
            # If parsing fails, preserve existing content and append new
            return self._safe_merge_fallback(new_content, existing_path)
    
    def categorize_faq_pairs(self, faq_pairs: List[FAQPair]) -> List[FAQPair]:
        """Categorize FAQ pairs based on content analysis."""
        categorized_pairs = []
        
        for pair in faq_pairs:
            # Auto-categorize if category is 'general' or empty
            if pair.category in ['general', '']:
                pair.category = self._determine_category(pair.question, pair.answer)
            
            categorized_pairs.append(pair)
        
        return categorized_pairs
    
    def _generate_empty_faq(self) -> str:
        """Generate an empty FAQ template."""
        return """# Frequently Asked Questions

## Getting Started

*No questions yet. FAQ content will be automatically generated based on repository analysis.*

## Setup

*Setup-related questions will appear here.*

## Usage

*Usage-related questions will appear here.*

## Development

*Development-related questions will appear here.*

## Troubleshooting

*Troubleshooting questions will appear here.*

---

*This FAQ is automatically generated and updated. Manual additions are preserved during updates.*
"""
    
    def _apply_style_guidelines(self, faq_doc: FAQDocument) -> None:
        """Apply style guidelines from steering configuration."""
        # Load style rules if not already loaded
        if not self.style_config.onboarding_style_content:
            self.style_config.load_content()
        
        # Apply consistent tone and formatting
        for category_faqs in faq_doc.categories.values():
            for faq in category_faqs:
                faq.question = self._format_question(faq.question)
                faq.answer = self._format_answer(faq.answer)
    
    def _format_question(self, question: str) -> str:
        """Format question according to style guidelines."""
        # Clean up whitespace and normalize
        question = ' '.join(question.strip().split())
        
        if not question:
            return question
        
        # Ensure question ends with question mark
        if not question.endswith('?'):
            question += '?'
        
        # Apply friendly, concise language style
        question = self._apply_friendly_tone(question)
        
        # Capitalize first letter and proper nouns
        question = self._capitalize_properly(question)
        
        return question
    
    def _format_answer(self, answer: str) -> str:
        """Format answer according to style guidelines."""
        # Clean up whitespace and normalize line breaks
        answer = self._normalize_answer_text(answer)
        
        if not answer:
            return answer
        
        # Ensure answer ends with proper punctuation
        if not answer.endswith(('.', '!', '?')):
            answer += '.'
        
        # Capitalize first letter
        answer = answer[0].upper() + answer[1:]
        
        # Apply friendly, concise language style
        answer = self._apply_friendly_tone(answer)
        
        # Format code blocks and examples
        answer = self._format_code_examples(answer)
        
        # Highlight important points
        answer = self._highlight_important_points(answer)
        
        return answer
    
    def _apply_friendly_tone(self, text: str) -> str:
        """Apply friendly, concise language style from steering guidelines."""
        # Replace formal language with friendly alternatives
        friendly_replacements = {
            'utilize': 'use',
            'commence': 'start',
            'terminate': 'stop',
            'implement': 'add',
            'execute': 'run',
            'initialize': 'set up',
            'configure': 'set up',
            'subsequently': 'then',
            'prior to': 'before',
            'in order to': 'to',
            'it is necessary to': 'you need to',
            'it is recommended': 'we recommend',
            'please note that': 'note that',
        }
        
        for formal, friendly in friendly_replacements.items():
            # Use word boundaries to avoid partial word replacements
            pattern = r'\b' + re.escape(formal) + r'\b'
            text = re.sub(pattern, friendly, text, flags=re.IGNORECASE)
        
        return text
    
    def _capitalize_properly(self, text: str) -> str:
        """Properly capitalize text including 'I' and first letters."""
        if not text:
            return text
        
        # Split into words and capitalize appropriately
        words = text.split()
        capitalized_words = []
        
        for i, word in enumerate(words):
            if i == 0:
                # Always capitalize first word
                capitalized_words.append(word.capitalize())
            elif word.lower() == 'i':
                # Always capitalize 'I'
                capitalized_words.append('I')
            else:
                # Keep other words as they are (already processed by friendly tone)
                capitalized_words.append(word)
        
        return ' '.join(capitalized_words)
    
    def _normalize_answer_text(self, answer: str) -> str:
        """Normalize answer text formatting."""
        # Remove excessive whitespace
        answer = re.sub(r'\s+', ' ', answer.strip())
        
        # Normalize line breaks for better readability
        answer = re.sub(r'\n\s*\n\s*\n+', '\n\n', answer)
        
        # Clean up bullet points and lists
        answer = re.sub(r'\n\s*[-*]\s+', '\n- ', answer)
        answer = re.sub(r'\n\s*\d+\.\s+', lambda m: f'\n{m.group().strip()} ', answer)
        
        return answer.strip()
    
    def _format_code_examples(self, text: str) -> str:
        """Format code examples and commands in text."""
        # Format inline code (backticks)
        text = re.sub(r'`([^`]+)`', r'`\1`', text)
        
        # Format file paths and commands
        text = re.sub(r'\b([a-zA-Z0-9_-]+\.[a-zA-Z]{2,4})\b', r'`\1`', text)
        text = re.sub(r'\b(npm|pip|git|python|node)\s+([a-zA-Z0-9_-]+)', r'`\1 \2`', text)
        
        return text
    
    def _highlight_important_points(self, text: str) -> str:
        """Highlight important points in bold according to steering guidelines."""
        # Highlight important keywords and phrases
        important_patterns = [
            (r'\b(important|note|warning|caution|remember)\b:?\s*', r'**\1:**'),
            (r'\b(required|mandatory|must|essential)\b', r'**\1**'),
            (r'\b(first|before|after|then)\b(?=\s+you)', r'**\1**'),
        ]
        
        for pattern, replacement in important_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _format_faq_markdown(self, faq_doc: FAQDocument) -> str:
        """Format FAQ document as structured markdown."""
        lines = []
        
        # Add title with proper spacing
        lines.extend([f"# {faq_doc.title}", ""])
        
        # Add introduction if present
        if faq_doc.introduction:
            lines.extend([faq_doc.introduction, ""])
        
        # Add table of contents for better navigation
        if len(faq_doc.categories) > 1:
            lines.extend(self._generate_table_of_contents(faq_doc))
        
        # Sort categories by predefined order
        sorted_categories = self._sort_categories(list(faq_doc.categories.keys()))
        
        for i, category in enumerate(sorted_categories):
            if category not in faq_doc.categories:
                continue
                
            faqs = faq_doc.categories[category]
            if not faqs:
                continue
            
            # Add category header with proper spacing
            category_title = self._format_category_title(category)
            lines.extend([f"## {category_title}", ""])
            
            # Add category description if available
            category_desc = self._get_category_description(category)
            if category_desc:
                lines.extend([category_desc, ""])
            
            # Add FAQ pairs with consistent formatting
            for j, faq in enumerate(faqs):
                lines.append(f"### {faq.question}")
                lines.append("")
                
                # Format multi-line answers properly
                formatted_answer = self._format_multiline_answer(faq.answer)
                lines.append(formatted_answer)
                lines.append("")
                
                # Add source reference if available
                if hasattr(faq, 'source_files') and faq.source_files:
                    source_ref = self._format_source_reference(faq.source_files)
                    lines.extend([source_ref, ""])
        
        # Add footer with proper spacing
        lines.extend([
            "---",
            "",
            "*This FAQ is automatically generated and updated based on repository analysis.*",
            "*Manual additions and edits are preserved during updates.*"
        ])
        
        return "\n".join(lines)
    
    def _generate_table_of_contents(self, faq_doc: FAQDocument) -> List[str]:
        """Generate table of contents for FAQ document."""
        toc_lines = ["## Table of Contents", ""]
        
        sorted_categories = self._sort_categories(list(faq_doc.categories.keys()))
        
        for category in sorted_categories:
            if category in faq_doc.categories and faq_doc.categories[category]:
                category_title = self._format_category_title(category)
                anchor = category.lower().replace(' ', '-')
                toc_lines.append(f"- [{category_title}](#{anchor})")
        
        toc_lines.extend(["", ""])
        return toc_lines
    
    def _get_category_description(self, category: str) -> str:
        """Get description for FAQ category."""
        descriptions = {
            'getting-started': 'Questions about initial setup and first steps.',
            'setup': 'Installation, configuration, and environment setup questions.',
            'usage': 'How to use features and common usage patterns.',
            'development': 'Development workflow, contributing, and building.',
            'troubleshooting': 'Common issues and their solutions.',
            'general': 'General questions about the project.'
        }
        return descriptions.get(category, '')
    
    def _format_multiline_answer(self, answer: str) -> str:
        """Format multi-line answers with proper indentation and structure."""
        if not answer:
            return answer
        
        # Split into paragraphs
        paragraphs = answer.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Handle code blocks
            if paragraph.startswith('```') or paragraph.startswith('    '):
                formatted_paragraphs.append(paragraph)
            # Handle lists
            elif any(paragraph.startswith(prefix) for prefix in ['- ', '* ', '1. ', '2. ']):
                formatted_paragraphs.append(paragraph)
            # Handle regular paragraphs
            else:
                # Ensure proper line wrapping for readability
                formatted_paragraphs.append(paragraph)
        
        return '\n\n'.join(formatted_paragraphs)
    
    def _format_source_reference(self, source_files: List[str]) -> str:
        """Format source file references."""
        if not source_files:
            return ""
        
        if len(source_files) == 1:
            return f"*Source: {source_files[0]}*"
        else:
            files_str = ", ".join(source_files[:3])  # Limit to first 3 files
            if len(source_files) > 3:
                files_str += f" and {len(source_files) - 3} more"
            return f"*Sources: {files_str}*"
    
    def _parse_existing_faq(self, existing_path: str) -> FAQDocument:
        """Parse existing FAQ file into FAQDocument structure."""
        faq_doc = FAQDocument()
        
        try:
            with open(existing_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            return faq_doc
        
        lines = content.split('\n')
        current_category = 'general'
        current_question = None
        current_answer_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines and separators
            if not line_stripped or line_stripped.startswith('---'):
                continue
            
            # Check for main title
            if line_stripped.startswith('# '):
                faq_doc.title = line_stripped[2:].strip()
                continue
            
            # Check for category headers
            if line_stripped.startswith('## '):
                # Save previous question if exists
                if current_question and current_answer_lines:
                    answer = '\n'.join(current_answer_lines).strip()
                    if answer and not answer.startswith('*') and 'automatically generated' not in answer.lower():
                        faq_pair = FAQPair(
                            question=current_question,
                            answer=answer,
                            category=current_category
                        )
                        faq_doc.add_faq_pair(faq_pair)
                
                # Reset for new category
                current_category = self._normalize_category_name(line_stripped[3:].strip())
                current_question = None
                current_answer_lines = []
                continue
            
            # Check for question headers
            if line_stripped.startswith('### '):
                # Save previous question if exists
                if current_question and current_answer_lines:
                    answer = '\n'.join(current_answer_lines).strip()
                    if answer and not answer.startswith('*') and 'automatically generated' not in answer.lower():
                        faq_pair = FAQPair(
                            question=current_question,
                            answer=answer,
                            category=current_category
                        )
                        faq_doc.add_faq_pair(faq_pair)
                
                # Start new question
                current_question = line_stripped[4:].strip()
                current_answer_lines = []
                continue
            
            # Skip placeholder text
            if line_stripped.startswith('*') and ('appear here' in line_stripped.lower() or 
                                                   'automatically generated' in line_stripped.lower() or
                                                   'no questions yet' in line_stripped.lower()):
                continue
            
            # Collect answer lines
            if current_question:
                current_answer_lines.append(line)
        
        # Save final question if exists
        if current_question and current_answer_lines:
            answer = '\n'.join(current_answer_lines).strip()
            if answer and not answer.startswith('*') and 'automatically generated' not in answer.lower():
                faq_pair = FAQPair(
                    question=current_question,
                    answer=answer,
                    category=current_category
                )
                faq_doc.add_faq_pair(faq_pair)
        
        return faq_doc
    
    def _extract_faq_pairs_from_content(self, content: str) -> List[FAQPair]:
        """Extract FAQ pairs from markdown content."""
        faq_pairs = []
        lines = content.split('\n')
        current_category = 'general'
        current_question = None
        current_answer_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines and separators
            if not line_stripped or line_stripped.startswith('---'):
                continue
            
            # Check for category headers
            if line_stripped.startswith('## '):
                # Save previous question if exists
                if current_question and current_answer_lines:
                    answer = '\n'.join(current_answer_lines).strip()
                    if answer and not answer.startswith('*'):
                        faq_pairs.append(FAQPair(
                            question=current_question,
                            answer=answer,
                            category=current_category
                        ))
                
                # Reset for new category
                current_category = self._normalize_category_name(line_stripped[3:].strip())
                current_question = None
                current_answer_lines = []
                continue
            
            # Check for question headers
            if line_stripped.startswith('### '):
                # Save previous question if exists
                if current_question and current_answer_lines:
                    answer = '\n'.join(current_answer_lines).strip()
                    if answer and not answer.startswith('*'):
                        faq_pairs.append(FAQPair(
                            question=current_question,
                            answer=answer,
                            category=current_category
                        ))
                
                # Start new question
                current_question = line_stripped[4:].strip()
                current_answer_lines = []
                continue
            
            # Skip placeholder text
            if line_stripped.startswith('*'):
                continue
            
            # Collect answer lines
            if current_question:
                current_answer_lines.append(line)
        
        # Save final question if exists
        if current_question and current_answer_lines:
            answer = '\n'.join(current_answer_lines).strip()
            if answer and not answer.startswith('*'):
                faq_pairs.append(FAQPair(
                    question=current_question,
                    answer=answer,
                    category=current_category
                ))
        
        return faq_pairs
    
    def _safe_merge_fallback(self, new_content: str, existing_path: str) -> str:
        """Fallback merge strategy when parsing fails."""
        try:
            with open(existing_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Simple append strategy
            return existing_content + "\n\n---\n\n## New Content\n\n" + new_content
        except FileNotFoundError:
            return new_content
        except Exception:
            return new_content
    
    def _determine_category(self, question: str, answer: str) -> str:
        """Determine appropriate category for an FAQ pair."""
        text = (question + " " + answer).lower()
        
        # Category keywords mapping
        category_keywords = {
            'getting-started': ['start', 'begin', 'first', 'new', 'intro', 'overview'],
            'setup': ['install', 'setup', 'configure', 'requirement', 'dependency', 'environment'],
            'usage': ['how to', 'use', 'run', 'execute', 'command', 'example'],
            'development': ['develop', 'code', 'contribute', 'build', 'test', 'debug'],
            'troubleshooting': ['error', 'problem', 'issue', 'fix', 'troubleshoot', 'fail', 'wrong']
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, or 'general' if no matches
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return 'general'
    
    def _sort_categories(self, categories: List[str]) -> List[str]:
        """Sort categories according to predefined order."""
        sorted_cats = []
        
        # Add categories in predefined order
        for cat in self._category_order:
            if cat in categories:
                sorted_cats.append(cat)
        
        # Add any remaining categories
        for cat in categories:
            if cat not in sorted_cats:
                sorted_cats.append(cat)
        
        return sorted_cats
    
    def _format_category_title(self, category: str) -> str:
        """Format category name for display."""
        # Convert kebab-case to title case
        return category.replace('-', ' ').title()
    
    def _normalize_category_name(self, category_title: str) -> str:
        """Normalize category title to internal category name."""
        # Convert to lowercase and replace spaces with hyphens
        normalized = category_title.lower().replace(' ', '-')
        
        # Map common variations
        category_mapping = {
            'getting-started': 'getting-started',
            'get-started': 'getting-started',
            'start': 'getting-started',
            'setup': 'setup',
            'installation': 'setup',
            'install': 'setup',
            'usage': 'usage',
            'use': 'usage',
            'how-to': 'usage',
            'development': 'development',
            'dev': 'development',
            'develop': 'development',
            'troubleshooting': 'troubleshooting',
            'troubleshoot': 'troubleshooting',
            'problems': 'troubleshooting',
            'issues': 'troubleshooting'
        }
        
        return category_mapping.get(normalized, normalized)
    
    def validate_formatting_quality(self, content: str) -> Dict[str, Any]:
        """Validate the quality of formatted FAQ content."""
        validation_results = {
            'is_valid': True,
            'issues': [],
            'suggestions': [],
            'metrics': {}
        }
        
        lines = content.split('\n')
        
        # Check basic structure
        has_title = any(line.startswith('# ') for line in lines)
        has_categories = any(line.startswith('## ') for line in lines)
        has_questions = any(line.startswith('### ') for line in lines)
        
        if not has_title:
            validation_results['issues'].append('Missing main title (# heading)')
            validation_results['is_valid'] = False
        
        if not has_categories:
            validation_results['issues'].append('Missing category sections (## headings)')
            validation_results['is_valid'] = False
        
        if not has_questions:
            validation_results['issues'].append('Missing FAQ questions (### headings)')
            validation_results['is_valid'] = False
        
        # Check formatting consistency
        question_count = sum(1 for line in lines if line.startswith('### '))
        category_count = sum(1 for line in lines if line.startswith('## ') and not line.startswith('## Table'))
        
        # Check for proper question formatting
        questions = [line[4:].strip() for line in lines if line.startswith('### ')]
        questions_without_marks = [q for q in questions if not q.endswith('?')]
        
        if questions_without_marks:
            validation_results['issues'].append(f'{len(questions_without_marks)} questions missing question marks')
            validation_results['suggestions'].append('Ensure all questions end with question marks')
        
        # Check for empty sections
        empty_sections = 0
        current_section = None
        section_has_content = False
        
        for line in lines:
            if line.startswith('## '):
                if current_section and not section_has_content:
                    empty_sections += 1
                current_section = line
                section_has_content = False
            elif line.startswith('### ') or (line.strip() and not line.startswith('#')):
                section_has_content = True
        
        if empty_sections > 0:
            validation_results['suggestions'].append(f'{empty_sections} empty sections could be removed or populated')
        
        # Calculate metrics
        validation_results['metrics'] = {
            'question_count': question_count,
            'category_count': category_count,
            'average_questions_per_category': question_count / max(category_count, 1),
            'total_lines': len(lines),
            'content_lines': len([line for line in lines if line.strip() and not line.startswith('#')])
        }
        
        return validation_results