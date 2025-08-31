"""Content analyzer for extracting structured information from repository content."""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import logging
import hashlib
import json
from functools import lru_cache

from ..models import RepositoryAnalysis, Concept, SetupStep, CodeExample, Dependency
from ..interfaces import ContentAnalyzerInterface


class ContentAnalyzer(ContentAnalyzerInterface):
    """Analyzes repository content to extract structured information."""
    
    def __init__(self, workspace_path: str = '.'):
        self.workspace_path = Path(workspace_path)
        self.logger = logging.getLogger(__name__)
        
        # Patterns for extracting different types of content
        self.code_block_pattern = re.compile(r'```(\w+)?\n(.*?)\n```', re.DOTALL | re.MULTILINE)
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.setup_keywords = {'install', 'setup', 'configuration', 'getting started', 'prerequisites', 'requirements', 'dependencies'}
        self.concept_keywords = {'overview', 'architecture', 'design', 'concepts', 'introduction', 'about', 'what is'}
        
        # Content relationship analysis patterns
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.reference_pattern = re.compile(r'(?:see|refer to|check|read|visit)\s+([^\s\n.]+)', re.IGNORECASE)
        self.dependency_keywords = {'depends on', 'requires', 'needs', 'prerequisite', 'before', 'after', 'following'}
        
        # Caching for performance
        self._content_cache = {}
        self._relationship_cache = {}
        
    def analyze_repository(self, repo_path: str) -> RepositoryAnalysis:
        """Analyze repository content and extract structured information."""
        repo_path = Path(repo_path)
        if not repo_path.exists():
            self.logger.warning(f"Repository path does not exist: {repo_path}")
            return RepositoryAnalysis()
        
        # Find all markdown files
        markdown_files = self._find_markdown_files(repo_path)
        
        # Extract information from all markdown files
        all_concepts, all_setup_steps, all_code_examples, all_dependencies = [], [], [], []
        
        for md_file in markdown_files:
            try:
                content = self._read_file_content(md_file)
                if content:
                    all_concepts.extend(self.extract_concepts(content, str(md_file)))
                    all_setup_steps.extend(self.identify_setup_steps(content, str(md_file)))
                    all_code_examples.extend(self.find_code_examples(content, str(md_file)))
                    all_dependencies.extend(self._extract_dependencies(content, str(md_file)))
            except Exception as e:
                self.logger.error(f"Error processing {md_file}: {e}")
                continue
        
        return RepositoryAnalysis(
            concepts=self._deduplicate_concepts(all_concepts),
            setup_steps=self._order_setup_steps(all_setup_steps),
            code_examples=all_code_examples,
            file_structure=self._build_file_structure(repo_path),
            dependencies=self._deduplicate_dependencies(all_dependencies)
        )
    
    def extract_concepts(self, markdown_content: str, file_path: str = '') -> List[Concept]:
        """Extract key concepts from markdown content."""
        concepts = []
        headings = self.heading_pattern.findall(markdown_content)
        content_sections = self.heading_pattern.split(markdown_content)
        
        for i, (level_markers, heading_text) in enumerate(headings):
            if self._is_concept_heading(heading_text.lower()):
                section_content = content_sections[i * 3 + 3] if i * 3 + 3 < len(content_sections) else ''
                concepts.append(Concept(
                    name=heading_text.strip(),
                    description=self._extract_concept_description(section_content),
                    importance=self._calculate_concept_importance(len(level_markers), heading_text, section_content),
                    related_files=[file_path] if file_path else [],
                    prerequisites=self._extract_prerequisites(section_content)
                ))
        return concepts
    
    def identify_setup_steps(self, content: str, file_path: str = '') -> List[SetupStep]:
        """Identify setup and installation steps."""
        setup_steps = []
        headings = self.heading_pattern.findall(content)
        content_sections = self.heading_pattern.split(content)
        
        for i, (level_markers, heading_text) in enumerate(headings):
            if self._is_setup_heading(heading_text.lower()):
                section_content = content_sections[i * 3 + 3] if i * 3 + 3 < len(content_sections) else ''
                setup_steps.extend(self._extract_setup_steps_from_section(heading_text, section_content, len(setup_steps)))
        return setup_steps
    
    def find_code_examples(self, content: str, file_path: str = '') -> List[CodeExample]:
        """Find and extract code examples."""
        code_examples = []
        matches = self.code_block_pattern.findall(content)
        
        for language, code in matches:
            if code.strip():
                title, description = self._extract_code_context(content, code)
                code_examples.append(CodeExample(
                    title=title,
                    code=code.strip(),
                    language=(language or self._detect_language(code)).lower(),
                    description=description,
                    file_path=file_path
                ))
        return code_examples  
  
    def _find_markdown_files(self, repo_path: Path) -> List[Path]:
        """Find all markdown files in the repository."""
        markdown_files = []
        md_extensions = {'.md', '.markdown', '.mdown', '.mkd'}
        skip_dirs = {'.git', '.kiro', '__pycache__', 'node_modules', '.pytest_cache'}
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for file in files:
                if any(file.lower().endswith(ext) for ext in md_extensions):
                    markdown_files.append(Path(root) / file)
        return markdown_files
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read content from a file safely."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (IOError, UnicodeDecodeError) as e:
            self.logger.warning(f"Could not read file {file_path}: {e}")
            return None
    
    def _extract_dependencies(self, content: str, file_path: str) -> List[Dependency]:
        """Extract dependencies from content."""
        dependencies = []
        patterns = [(r'pip install\s+([^\s\n]+)', 'runtime'), (r'npm install\s+([^\s\n]+)', 'runtime'), (r'yarn add\s+([^\s\n]+)', 'runtime'), (r'gem install\s+([^\s\n]+)', 'runtime'), (r'apt-get install\s+([^\s\n]+)', 'runtime'), (r'brew install\s+([^\s\n]+)', 'runtime')]
        
        for pattern, dep_type in patterns:
            for match in re.findall(pattern, content, re.IGNORECASE):
                dep_name = match.strip().split('==')[0].split('>=')[0].split('<=')[0]
                version = None
                if '==' in match:
                    version = match.split('==')[1].strip()
                elif '>=' in match:
                    version = '>=' + match.split('>=')[1].strip()
                elif '<=' in match:
                    version = '<=' + match.split('<=')[1].strip()
                
                dependencies.append(Dependency(name=dep_name, version=version, type=dep_type, description=f"Dependency found in {file_path}"))
        return dependencies
    
    def _build_file_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Build a representation of the repository file structure."""
        structure = {}
        try:
            skip_dirs = {'.git', '.kiro', '__pycache__', 'node_modules', '.pytest_cache'}
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                rel_path = Path(root).relative_to(repo_path)
                current = structure
                if str(rel_path) != '.':
                    for part in rel_path.parts:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                if files:
                    current['_files'] = files
        except Exception as e:
            self.logger.error(f"Error building file structure: {e}")
            structure = {'error': str(e)}
        return structure
    
    def _deduplicate_concepts(self, concepts: List[Concept]) -> List[Concept]:
        """Remove duplicate concepts and sort by importance."""
        unique_concepts = {}
        for concept in concepts:
            key = concept.name.lower().strip()
            if key not in unique_concepts:
                unique_concepts[key] = concept
            else:
                existing = unique_concepts[key]
                existing.related_files.extend(concept.related_files)
                existing.prerequisites.extend(concept.prerequisites)
                if len(concept.description) > len(existing.description):
                    existing.description = concept.description
                existing.importance = max(existing.importance, concept.importance)
        
        result = list(unique_concepts.values())
        for concept in result:
            concept.related_files = list(set(concept.related_files))
            concept.prerequisites = list(set(concept.prerequisites))
        return sorted(result, key=lambda c: c.importance, reverse=True)
    
    def analyze_content_relationships(self, repo_path: str) -> Dict[str, Any]:
        """Analyze relationships and dependencies between content files."""
        repo_path = Path(repo_path)
        cache_key = self._get_cache_key(str(repo_path), 'relationships')
        
        # Check cache first
        if cache_key in self._relationship_cache:
            self.logger.debug(f"Using cached relationship analysis for {repo_path}")
            return self._relationship_cache[cache_key]
        
        self.logger.info(f"Analyzing content relationships in {repo_path}")
        
        # Find all markdown files
        markdown_files = self._find_markdown_files(repo_path)
        
        # Build content map
        content_map = {}
        for md_file in markdown_files:
            content = self._read_file_content(md_file)
            if content:
                rel_path = str(md_file.relative_to(repo_path))
                content_map[rel_path] = content
        
        # Analyze relationships
        relationships = {
            'file_dependencies': self._identify_file_dependencies(content_map),
            'concept_relationships': self._identify_concept_relationships(content_map),
            'content_hierarchy': self._build_content_hierarchy(content_map),
            'cross_references': self._find_cross_references(content_map),
            'prerequisite_chains': self._build_prerequisite_chains(content_map)
        }
        
        # Cache results
        self._relationship_cache[cache_key] = relationships
        
        return relationships
    
    def _identify_file_dependencies(self, content_map: Dict[str, str]) -> Dict[str, List[str]]:
        """Identify which files depend on or reference other files."""
        dependencies = {}
        
        for file_path, content in content_map.items():
            file_deps = set()
            
            # Find explicit file references
            for other_file in content_map.keys():
                if other_file != file_path:
                    # Check for direct file name mentions
                    file_name = Path(other_file).name
                    if file_name.lower() in content.lower():
                        file_deps.add(other_file)
                    
                    # Check for path references
                    if other_file in content:
                        file_deps.add(other_file)
            
            # Find markdown links to other files
            links = self.link_pattern.findall(content)
            for link_text, link_url in links:
                # Check if link points to another markdown file
                if link_url.endswith('.md') or link_url.endswith('.markdown'):
                    # Normalize path
                    if not link_url.startswith('/'):
                        # Relative path - resolve relative to current file
                        current_dir = Path(file_path).parent
                        target_path = str((current_dir / link_url).as_posix())
                        if target_path in content_map:
                            file_deps.add(target_path)
                    else:
                        # Absolute path
                        if link_url.lstrip('/') in content_map:
                            file_deps.add(link_url.lstrip('/'))
            
            dependencies[file_path] = list(file_deps)
        
        return dependencies
    
    def _identify_concept_relationships(self, content_map: Dict[str, str]) -> Dict[str, Dict[str, List[str]]]:
        """Identify relationships between concepts across files."""
        concept_relationships = {}
        
        # Extract concepts from all files
        all_concepts = {}
        for file_path, content in content_map.items():
            concepts = self.extract_concepts(content, file_path)
            for concept in concepts:
                concept_key = concept.name.lower().strip()
                if concept_key not in all_concepts:
                    all_concepts[concept_key] = []
                all_concepts[concept_key].append((concept, file_path))
        
        # Find concept relationships
        for concept_key, concept_instances in all_concepts.items():
            relationships = {
                'mentions_in_other_files': [],
                'related_concepts': [],
                'prerequisite_for': [],
                'depends_on': []
            }
            
            concept_name = concept_instances[0][0].name
            
            # Find mentions of this concept in other files
            for file_path, content in content_map.items():
                # Skip files where this concept is defined
                concept_files = [inst[1] for inst in concept_instances]
                if file_path not in concept_files:
                    if concept_name.lower() in content.lower():
                        relationships['mentions_in_other_files'].append(file_path)
            
            # Find related concepts (concepts mentioned in same sections)
            for concept_instance, file_path in concept_instances:
                content = content_map[file_path]
                # Find other concepts mentioned near this one
                for other_key, other_instances in all_concepts.items():
                    if other_key != concept_key:
                        other_name = other_instances[0][0].name
                        if other_name.lower() in content.lower():
                            if other_name not in relationships['related_concepts']:
                                relationships['related_concepts'].append(other_name)
            
            # Find dependency relationships
            for concept_instance, file_path in concept_instances:
                content = content_map[file_path]
                for keyword in self.dependency_keywords:
                    if keyword in content.lower():
                        # Look for concepts mentioned after dependency keywords
                        pattern = rf'{keyword}\s+([^.!?\n]+)'
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            for other_key, other_instances in all_concepts.items():
                                if other_key != concept_key:
                                    other_name = other_instances[0][0].name
                                    if other_name.lower() in match.lower():
                                        relationships['depends_on'].append(other_name)
            
            concept_relationships[concept_name] = relationships
        
        return concept_relationships
    
    def _build_content_hierarchy(self, content_map: Dict[str, str]) -> Dict[str, Any]:
        """Build a hierarchy of content based on file structure and headings."""
        hierarchy = {}
        
        for file_path, content in content_map.items():
            # Parse heading structure
            headings = self.heading_pattern.findall(content)
            file_hierarchy = []
            
            for level_markers, heading_text in headings:
                level = len(level_markers)
                file_hierarchy.append({
                    'level': level,
                    'title': heading_text.strip(),
                    'is_concept': self._is_concept_heading(heading_text.lower()),
                    'is_setup': self._is_setup_heading(heading_text.lower())
                })
            
            # Determine file importance based on name and content
            importance = self._calculate_file_importance(file_path, content)
            
            hierarchy[file_path] = {
                'headings': file_hierarchy,
                'importance': importance,
                'word_count': len(content.split()),
                'has_code_examples': len(self.code_block_pattern.findall(content)) > 0
            }
        
        return hierarchy
    
    def _find_cross_references(self, content_map: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
        """Find cross-references between files."""
        cross_references = {}
        
        for file_path, content in content_map.items():
            references = []
            
            # Find markdown links
            links = self.link_pattern.findall(content)
            for link_text, link_url in links:
                references.append({
                    'type': 'link',
                    'text': link_text,
                    'target': link_url,
                    'context': self._extract_link_context(content, link_text)
                })
            
            # Find textual references
            ref_matches = self.reference_pattern.findall(content)
            for match in ref_matches:
                references.append({
                    'type': 'textual_reference',
                    'text': match,
                    'target': match,
                    'context': self._extract_reference_context(content, match)
                })
            
            cross_references[file_path] = references
        
        return cross_references
    
    def _build_prerequisite_chains(self, content_map: Dict[str, str]) -> Dict[str, List[str]]:
        """Build chains of prerequisites across content."""
        prerequisite_chains = {}
        
        for file_path, content in content_map.items():
            chain = []
            
            # Extract prerequisites from content
            prerequisites = self._extract_prerequisites(content)
            
            # Try to match prerequisites to other files or concepts
            for prereq in prerequisites:
                # Check if prerequisite matches another file
                for other_file in content_map.keys():
                    if other_file != file_path:
                        other_name = Path(other_file).stem.replace('_', ' ').replace('-', ' ')
                        if other_name.lower() in prereq.lower():
                            chain.append(other_file)
                            break
                
                # Check if prerequisite matches a concept
                for other_file, other_content in content_map.items():
                    if other_file != file_path:
                        concepts = self.extract_concepts(other_content, other_file)
                        for concept in concepts:
                            if concept.name.lower() in prereq.lower():
                                chain.append(f"concept:{concept.name}")
                                break
            
            prerequisite_chains[file_path] = chain
        
        return prerequisite_chains
    
    @lru_cache(maxsize=128)
    def _get_cache_key(self, path: str, analysis_type: str) -> str:
        """Generate a cache key for analysis results."""
        # Include file modification times in cache key for invalidation
        try:
            repo_path = Path(path)
            if repo_path.exists():
                md_files = self._find_markdown_files(repo_path)
                mod_times = []
                for md_file in md_files:
                    try:
                        mod_times.append(str(md_file.stat().st_mtime))
                    except (OSError, AttributeError):
                        mod_times.append('0')
                
                content_hash = hashlib.md5(''.join(mod_times).encode()).hexdigest()
                return f"{analysis_type}:{path}:{content_hash}"
        except Exception as e:
            self.logger.warning(f"Error generating cache key: {e}")
        
        return f"{analysis_type}:{path}:no_hash"
    
    def _calculate_file_importance(self, file_path: str, content: str) -> int:
        """Calculate the importance of a file based on various factors."""
        importance = 1
        
        # File name importance
        file_name = Path(file_path).name.lower()
        if 'readme' in file_name:
            importance += 5
        elif 'getting' in file_name and 'started' in file_name:
            importance += 4
        elif any(keyword in file_name for keyword in ['setup', 'install', 'guide']):
            importance += 3
        elif any(keyword in file_name for keyword in ['api', 'reference', 'docs']):
            importance += 2
        
        # Content importance
        if len(content) > 2000:
            importance += 2
        elif len(content) > 1000:
            importance += 1
        
        # Code examples boost importance
        if len(self.code_block_pattern.findall(content)) > 3:
            importance += 2
        elif len(self.code_block_pattern.findall(content)) > 0:
            importance += 1
        
        # Heading structure importance
        headings = self.heading_pattern.findall(content)
        if len(headings) > 5:
            importance += 1
        
        return min(importance, 10)  # Cap at 10
    
    def _extract_link_context(self, content: str, link_text: str) -> str:
        """Extract context around a link for better understanding."""
        link_index = content.find(link_text)
        if link_index == -1:
            return ""
        
        # Get surrounding text (50 chars before and after)
        start = max(0, link_index - 50)
        end = min(len(content), link_index + len(link_text) + 50)
        context = content[start:end].strip()
        
        # Clean up context
        context = re.sub(r'\s+', ' ', context)
        return context
    
    def _extract_reference_context(self, content: str, reference: str) -> str:
        """Extract context around a textual reference."""
        ref_index = content.find(reference)
        if ref_index == -1:
            return ""
        
        # Get the sentence containing the reference
        sentences = re.split(r'[.!?]+', content)
        for sentence in sentences:
            if reference in sentence:
                return sentence.strip()
        
        return ""
    
    def clear_cache(self) -> None:
        """Clear all cached analysis results."""
        self._content_cache.clear()
        self._relationship_cache.clear()
        self.logger.info("Cleared content analysis cache")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about cache usage."""
        return {
            'content_cache_size': len(self._content_cache),
            'relationship_cache_size': len(self._relationship_cache)
        }
    
    def _order_setup_steps(self, steps: List[SetupStep]) -> List[SetupStep]:
        """Order setup steps logically."""
        priority_keywords = {'install': 1, 'download': 2, 'setup': 3, 'configure': 4, 'run': 5, 'test': 6}
        
        def get_priority(step: SetupStep) -> tuple:
            keyword_priority = 10
            for keyword, priority in priority_keywords.items():
                if keyword in step.title.lower():
                    keyword_priority = priority
                    break
            return (step.order, keyword_priority)
        
        return sorted(steps, key=get_priority)
    
    def _deduplicate_dependencies(self, dependencies: List[Dependency]) -> List[Dependency]:
        """Remove duplicate dependencies."""
        unique_deps = {}
        for dep in dependencies:
            key = dep.name.lower().strip()
            if key not in unique_deps:
                unique_deps[key] = dep
            elif dep.version and not unique_deps[key].version:
                unique_deps[key] = dep
        return list(unique_deps.values())
    
    def _is_concept_heading(self, heading_text: str) -> bool:
        """Check if a heading represents a concept."""
        return any(keyword in heading_text for keyword in self.concept_keywords)
    
    def _is_setup_heading(self, heading_text: str) -> bool:
        """Check if a heading represents setup information."""
        return any(keyword in heading_text for keyword in self.setup_keywords)
    
    def _calculate_concept_importance(self, level: int, heading: str, content: str) -> int:
        """Calculate the importance of a concept based on various factors."""
        importance = max(1, 7 - level)
        key_terms = ['architecture', 'overview', 'getting started', 'introduction']
        if any(term in heading.lower() for term in key_terms):
            importance = min(10, importance + 2)
        if len(content) > 500:
            importance = min(10, importance + 1)
        return importance
    
    def _extract_concept_description(self, content: str) -> str:
        """Extract a description from concept content."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if paragraphs:
            description = re.sub(r'[*_`]', '', paragraphs[0])
            description = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', description)
            return description[:197] + '...' if len(description) > 200 else description
        return "No description available"
    
    def _extract_prerequisites(self, content: str) -> List[str]:
        """Extract prerequisites from content."""
        prerequisites = []
        patterns = [r'(?:prerequisite|requirement|need|require)s?:?\s*(.+)', r'before\s+(?:you\s+)?(?:can\s+)?(?:start|begin|use)', r'make sure\s+(?:you\s+)?(?:have|install)']
        for pattern in patterns:
            for match in re.findall(pattern, content, re.IGNORECASE):
                for item in re.split(r'[,;]|\sand\s', match):
                    item = item.strip().rstrip('.')
                    if item and len(item) < 100:
                        prerequisites.append(item)
        return list(set(prerequisites))
    
    def _extract_setup_steps_from_section(self, heading: str, content: str, start_order: int) -> List[SetupStep]:
        """Extract setup steps from a content section."""
        steps = []
        patterns = [r'^\d+\.\s+(.+)$', r'^[-*]\s+(.+)$', r'^Step\s+\d+:?\s+(.+)$']
        lines = content.split('\n')
        current_step = None
        step_order = start_order
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            for pattern in patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    if current_step:
                        steps.append(current_step)
                    step_text = match.group(1)
                    current_step = SetupStep(
                        title=step_text[:50] + ('...' if len(step_text) > 50 else ''),
                        description=step_text,
                        commands=self._extract_commands(step_text),
                        prerequisites=[],
                        order=step_order
                    )
                    step_order += 1
                    break
            else:
                if current_step and line:
                    current_step.description += ' ' + line
                    current_step.commands.extend(self._extract_commands(line))
        
        if current_step:
            steps.append(current_step)
        elif content.strip():
            steps.append(SetupStep(
                title=heading,
                description=content[:200] + ('...' if len(content) > 200 else ''),
                commands=self._extract_commands(content),
                prerequisites=[],
                order=start_order
            ))
        return steps
    
    def _extract_commands(self, text: str) -> List[str]:
        """Extract command-line commands from text."""
        commands = []
        for match in re.findall(r'`([^`]+)`', text):
            if self._looks_like_command(match):
                commands.append(match.strip())
        
        patterns = [r'(?:run|execute|type):\s*(.+)', r'\$\s*(.+)', r'>\s*(.+)']
        for pattern in patterns:
            for match in re.findall(pattern, text, re.IGNORECASE):
                if self._looks_like_command(match):
                    commands.append(match.strip())
        return commands
    
    def _looks_like_command(self, text: str) -> bool:
        """Check if text looks like a command."""
        indicators = ['pip install', 'npm install', 'git clone', 'cd ', 'mkdir', 'python ', 'node ', 'java ', 'make', 'cmake', 'docker', 'apt-get', 'yum install', 'brew install']
        return any(indicator in text.lower() for indicator in indicators)
    
    def _extract_code_context(self, content: str, code: str) -> tuple[str, str]:
        """Extract title and description for a code example."""
        code_index = content.find(code)
        if code_index == -1:
            return "Code Example", "Code example from documentation"
        
        before_code = content[:code_index]
        lines_before = before_code.split('\n')
        title, description = "Code Example", "Code example from documentation"
        
        for line in reversed(lines_before):
            line = line.strip()
            if not line:
                continue
            
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                title = heading_match.group(2)
                break
            elif len(line) < 100 and not line.startswith('```'):
                description = line
                if not title or title == "Code Example":
                    title = line[:50] + ('...' if len(line) > 50 else '')
                break
        return title, description
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language from code content."""
        if 'def ' in code and 'import ' in code:
            return 'python'
        elif 'function ' in code or 'const ' in code or 'let ' in code:
            return 'javascript'
        elif 'public class ' in code or 'import java' in code:
            return 'java'
        elif '#include' in code or 'int main(' in code:
            return 'c'
        elif 'echo ' in code or 'ls ' in code or 'cd ' in code:
            return 'bash'
        elif 'SELECT ' in code.upper() or 'FROM ' in code.upper():
            return 'sql'
        return 'text'