"""Dependency file analyzer for extracting dependencies from various file formats."""

import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import configparser

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from ..models import Dependency


class DependencyAnalyzer:
    """Analyzes dependency files to extract structured dependency information."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_dependency_files(self, repo_path: str) -> List[Dependency]:
        """Analyze all dependency files in the repository."""
        repo_path = Path(repo_path)
        dependencies = []
        
        # Python dependencies
        dependencies.extend(self._analyze_python_deps(repo_path))
        
        # JavaScript/Node.js dependencies
        dependencies.extend(self._analyze_javascript_deps(repo_path))
        
        # Ruby dependencies
        dependencies.extend(self._analyze_ruby_deps(repo_path))
        
        # Rust dependencies
        dependencies.extend(self._analyze_rust_deps(repo_path))
        
        # Go dependencies
        dependencies.extend(self._analyze_go_deps(repo_path))
        
        # PHP dependencies
        dependencies.extend(self._analyze_php_deps(repo_path))
        
        return dependencies
    
    def _analyze_python_deps(self, repo_path: Path) -> List[Dependency]:
        """Analyze Python dependency files."""
        dependencies = []
        
        # requirements.txt
        req_file = repo_path / 'requirements.txt'
        if req_file.exists():
            dependencies.extend(self._parse_requirements_txt(req_file))
        
        # setup.py
        setup_file = repo_path / 'setup.py'
        if setup_file.exists():
            dependencies.extend(self._parse_setup_py(setup_file))
        
        # pyproject.toml
        pyproject_file = repo_path / 'pyproject.toml'
        if pyproject_file.exists() and TOML_AVAILABLE:
            dependencies.extend(self._parse_pyproject_toml(pyproject_file))
        
        # Pipfile
        pipfile = repo_path / 'Pipfile'
        if pipfile.exists() and TOML_AVAILABLE:
            dependencies.extend(self._parse_pipfile(pipfile))
        
        return dependencies
    
    def _parse_requirements_txt(self, file_path: Path) -> List[Dependency]:
        """Parse requirements.txt file."""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse package==version or package>=version
                        match = re.match(r'^([a-zA-Z0-9_-]+)([><=!]+)(.+)$', line)
                        if match:
                            name, operator, version = match.groups()
                            dependencies.append(Dependency(
                                name=name,
                                version=f"{operator}{version}",
                                type='runtime',
                                description=f"Python dependency from {file_path.name}"
                            ))
                        else:
                            # Simple package name
                            dependencies.append(Dependency(
                                name=line,
                                version=None,
                                type='runtime',
                                description=f"Python dependency from {file_path.name}"
                            ))
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _parse_setup_py(self, file_path: Path) -> List[Dependency]:
        """Parse setup.py file for dependencies."""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Look for install_requires
                install_requires_match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if install_requires_match:
                    deps_str = install_requires_match.group(1)
                    # Extract quoted strings
                    for match in re.findall(r'["\']([^"\']+)["\']', deps_str):
                        dep_match = re.match(r'^([a-zA-Z0-9_-]+)([><=!]+)(.+)$', match)
                        if dep_match:
                            name, operator, version = dep_match.groups()
                            dependencies.append(Dependency(
                                name=name,
                                version=f"{operator}{version}",
                                type='runtime',
                                description=f"Python dependency from {file_path.name}"
                            ))
                        else:
                            dependencies.append(Dependency(
                                name=match,
                                version=None,
                                type='runtime',
                                description=f"Python dependency from {file_path.name}"
                            ))
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _parse_pyproject_toml(self, file_path: Path) -> List[Dependency]:
        """Parse pyproject.toml file."""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
                
                # Check different sections for dependencies
                sections = [
                    ('project', 'dependencies'),
                    ('tool.poetry', 'dependencies'),
                    ('build-system', 'requires')
                ]
                
                for section_path, dep_key in sections:
                    section = data
                    for key in section_path.split('.'):
                        section = section.get(key, {})
                    
                    if dep_key in section:
                        deps = section[dep_key]
                        if isinstance(deps, list):
                            for dep in deps:
                                dependencies.append(Dependency(
                                    name=dep.split('>=')[0].split('==')[0].split('>')[0].split('<')[0],
                                    version=None,
                                    type='runtime',
                                    description=f"Python dependency from {file_path.name}"
                                ))
                        elif isinstance(deps, dict):
                            for name, version in deps.items():
                                dependencies.append(Dependency(
                                    name=name,
                                    version=str(version) if version else None,
                                    type='runtime',
                                    description=f"Python dependency from {file_path.name}"
                                ))
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _parse_pipfile(self, file_path: Path) -> List[Dependency]:
        """Parse Pipfile."""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
                
                for section in ['packages', 'dev-packages']:
                    if section in data:
                        for name, version in data[section].items():
                            dependencies.append(Dependency(
                                name=name,
                                version=str(version) if version != "*" else None,
                                type='runtime',
                                description=f"Python dependency from {file_path.name}"
                            ))
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _analyze_javascript_deps(self, repo_path: Path) -> List[Dependency]:
        """Analyze JavaScript/Node.js dependency files."""
        dependencies = []
        
        # package.json
        package_file = repo_path / 'package.json'
        if package_file.exists():
            dependencies.extend(self._parse_package_json(package_file))
        
        return dependencies
    
    def _parse_package_json(self, file_path: Path) -> List[Dependency]:
        """Parse package.json file."""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for section in ['dependencies', 'devDependencies', 'peerDependencies']:
                    if section in data:
                        for name, version in data[section].items():
                            dependencies.append(Dependency(
                                name=name,
                                version=version,
                                type='runtime',
                                description=f"JavaScript dependency from {file_path.name}"
                            ))
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _analyze_ruby_deps(self, repo_path: Path) -> List[Dependency]:
        """Analyze Ruby dependency files."""
        dependencies = []
        
        # Gemfile
        gemfile = repo_path / 'Gemfile'
        if gemfile.exists():
            dependencies.extend(self._parse_gemfile(gemfile))
        
        return dependencies
    
    def _parse_gemfile(self, file_path: Path) -> List[Dependency]:
        """Parse Gemfile."""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('gem '):
                        # Extract gem name and version
                        match = re.match(r"gem\s+['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?", line)
                        if match:
                            name = match.group(1)
                            version = match.group(2) if match.group(2) else None
                            dependencies.append(Dependency(
                                name=name,
                                version=version,
                                type='runtime',
                                description=f"Ruby dependency from {file_path.name}"
                            ))
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _analyze_rust_deps(self, repo_path: Path) -> List[Dependency]:
        """Analyze Rust dependency files."""
        dependencies = []
        
        # Cargo.toml
        cargo_file = repo_path / 'Cargo.toml'
        if cargo_file.exists() and TOML_AVAILABLE:
            dependencies.extend(self._parse_cargo_toml(cargo_file))
        
        return dependencies
    
    def _parse_cargo_toml(self, file_path: Path) -> List[Dependency]:
        """Parse Cargo.toml file."""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
                
                for section in ['dependencies', 'dev-dependencies']:
                    if section in data:
                        for name, version in data[section].items():
                            dependencies.append(Dependency(
                                name=name,
                                version=str(version) if isinstance(version, str) else None,
                                type='runtime',
                                description=f"Rust dependency from {file_path.name}"
                            ))
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _analyze_go_deps(self, repo_path: Path) -> List[Dependency]:
        """Analyze Go dependency files."""
        dependencies = []
        
        # go.mod
        go_mod = repo_path / 'go.mod'
        if go_mod.exists():
            dependencies.extend(self._parse_go_mod(go_mod))
        
        return dependencies
    
    def _parse_go_mod(self, file_path: Path) -> List[Dependency]:
        """Parse go.mod file."""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                in_require = False
                for line in f:
                    line = line.strip()
                    if line == 'require (':
                        in_require = True
                        continue
                    elif line == ')' and in_require:
                        in_require = False
                        continue
                    elif in_require or line.startswith('require '):
                        # Parse dependency line
                        if line.startswith('require '):
                            line = line[8:]  # Remove 'require '
                        
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            version = parts[1]
                            dependencies.append(Dependency(
                                name=name,
                                version=version,
                                type='runtime',
                                description=f"Go dependency from {file_path.name}"
                            ))
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _analyze_php_deps(self, repo_path: Path) -> List[Dependency]:
        """Analyze PHP dependency files."""
        dependencies = []
        
        # composer.json
        composer_file = repo_path / 'composer.json'
        if composer_file.exists():
            dependencies.extend(self._parse_composer_json(composer_file))
        
        return dependencies
    
    def _parse_composer_json(self, file_path: Path) -> List[Dependency]:
        """Parse composer.json file."""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for section in ['require', 'require-dev']:
                    if section in data:
                        for name, version in data[section].items():
                            dependencies.append(Dependency(
                                name=name,
                                version=version,
                                type='runtime',
                                description=f"PHP dependency from {file_path.name}"
                            ))
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies