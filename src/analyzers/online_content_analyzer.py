"""Online repository content analyzer for remote repositories."""

import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import requests
from urllib.parse import urlparse

try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

try:
    from github import Github
    GITHUB_API_AVAILABLE = True
except ImportError:
    GITHUB_API_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    # Try relative imports first (when used as package)
    from .content_analyzer import ContentAnalyzer
    from ..models import RepositoryAnalysis
except ImportError:
    # Fall back to absolute imports (when run directly)
    from content_analyzer import ContentAnalyzer
    from models import RepositoryAnalysis


class OnlineContentAnalyzer(ContentAnalyzer):
    """Analyzer that can work with online repositories."""
    
    def __init__(self, github_token: Optional[str] = None):
        super().__init__()
        self.github_token = github_token
        self.logger = logging.getLogger(__name__)
        
        if github_token and GITHUB_API_AVAILABLE:
            self.github = Github(github_token)
        else:
            self.github = None
    
    def analyze_online_repository(self, repo_url: str) -> RepositoryAnalysis:
        """Analyze an online repository using the best available method."""
        
        # Determine repository type and choose strategy
        if 'github.com' in repo_url:
            return self._analyze_github_repo(repo_url)
        elif 'gitlab.com' in repo_url:
            return self._analyze_gitlab_repo(repo_url)
        else:
            # Fallback to git clone if available
            if GIT_AVAILABLE:
                return self._analyze_via_git_clone(repo_url)
            else:
                raise ValueError(f"Unsupported repository URL: {repo_url}")
    
    def _analyze_github_repo(self, repo_url: str) -> RepositoryAnalysis:
        """Analyze GitHub repository using API or cloning."""
        
        # Try GitHub API first if available
        if self.github and GITHUB_API_AVAILABLE:
            try:
                return self._analyze_via_github_api(repo_url)
            except Exception as e:
                self.logger.warning(f"GitHub API failed: {e}, falling back to clone")
        
        # Fallback to cloning
        if GIT_AVAILABLE:
            return self._analyze_via_git_clone(repo_url)
        else:
            # Last resort: raw file access
            return self._analyze_via_raw_files(repo_url)
    
    def _analyze_via_github_api(self, repo_url: str) -> RepositoryAnalysis:
        """Analyze using GitHub API."""
        # Extract owner/repo from URL
        repo_path = self._extract_github_repo_path(repo_url)
        repo = self.github.get_repo(repo_path)
        
        # Get all markdown files
        markdown_files = self._get_github_markdown_files(repo)
        
        # Analyze content
        all_concepts, all_setup_steps, all_code_examples, all_dependencies = [], [], [], []
        
        for file_path in markdown_files:
            try:
                content = self._get_github_file_content(repo, file_path)
                if content:
                    all_concepts.extend(self.extract_concepts(content, file_path))
                    all_setup_steps.extend(self.identify_setup_steps(content, file_path))
                    all_code_examples.extend(self.find_code_examples(content, file_path))
                    all_dependencies.extend(self._extract_dependencies(content, file_path))
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        return RepositoryAnalysis(
            concepts=self._deduplicate_concepts(all_concepts),
            setup_steps=self._order_setup_steps(all_setup_steps),
            code_examples=all_code_examples,
            file_structure=self._build_github_file_structure(repo),
            dependencies=self._deduplicate_dependencies(all_dependencies)
        )
    
    def _analyze_via_git_clone(self, repo_url: str) -> RepositoryAnalysis:
        """Analyze by cloning repository temporarily."""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                self.logger.info(f"Cloning repository: {repo_url}")
                git.Repo.clone_from(repo_url, temp_dir, depth=1)  # Shallow clone
                
                # Use existing local analyzer
                return self.analyze_repository(temp_dir)
                
            except Exception as e:
                self.logger.error(f"Failed to clone repository: {e}")
                raise
    
    def _analyze_via_raw_files(self, repo_url: str) -> RepositoryAnalysis:
        """Analyze by downloading raw files (GitHub only)."""
        if 'github.com' not in repo_url:
            raise ValueError("Raw file access only supported for GitHub")
        
        # Convert GitHub URL to raw content base URL
        raw_base_url = self._get_github_raw_base_url(repo_url)
        
        # Try to get common markdown files
        common_files = ['README.md', 'readme.md', 'docs/README.md', 'CONTRIBUTING.md', 'INSTALL.md']
        
        all_concepts, all_setup_steps, all_code_examples, all_dependencies = [], [], [], []
        
        for file_path in common_files:
            try:
                content = self._download_raw_file(raw_base_url, file_path)
                if content:
                    all_concepts.extend(self.extract_concepts(content, file_path))
                    all_setup_steps.extend(self.identify_setup_steps(content, file_path))
                    all_code_examples.extend(self.find_code_examples(content, file_path))
                    all_dependencies.extend(self._extract_dependencies(content, file_path))
            except Exception as e:
                self.logger.debug(f"Could not download {file_path}: {e}")
                continue
        
        return RepositoryAnalysis(
            concepts=self._deduplicate_concepts(all_concepts),
            setup_steps=self._order_setup_steps(all_setup_steps),
            code_examples=all_code_examples,
            file_structure={'_files': common_files},
            dependencies=self._deduplicate_dependencies(all_dependencies)
        )
    
    def _analyze_gitlab_repo(self, repo_url: str) -> RepositoryAnalysis:
        """Analyze GitLab repository."""
        # Similar to GitHub but using GitLab API
        # For now, fallback to git clone
        if GIT_AVAILABLE:
            return self._analyze_via_git_clone(repo_url)
        else:
            raise ValueError("GitLab analysis requires git to be installed")
    
    def _extract_github_repo_path(self, repo_url: str) -> str:
        """Extract owner/repo from GitHub URL."""
        # https://github.com/owner/repo -> owner/repo
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 2:
            return f"{path_parts[0]}/{path_parts[1]}"
        else:
            raise ValueError(f"Invalid GitHub URL: {repo_url}")
    
    def _get_github_markdown_files(self, repo) -> List[str]:
        """Get all markdown files from GitHub repository."""
        markdown_files = []
        
        def traverse_contents(contents, path=""):
            for content in contents:
                if content.type == "dir":
                    # Skip common directories
                    if content.name in {'.git', '.kiro', '__pycache__', 'node_modules'}:
                        continue
                    try:
                        sub_contents = repo.get_contents(content.path)
                        traverse_contents(sub_contents, content.path)
                    except Exception as e:
                        self.logger.debug(f"Could not access directory {content.path}: {e}")
                elif content.name.endswith(('.md', '.markdown', '.mdown', '.mkd')):
                    markdown_files.append(content.path)
        
        try:
            root_contents = repo.get_contents("")
            traverse_contents(root_contents)
        except Exception as e:
            self.logger.error(f"Error traversing repository contents: {e}")
        
        return markdown_files
    
    def _get_github_file_content(self, repo, file_path: str) -> Optional[str]:
        """Get file content from GitHub repository."""
        try:
            file_content = repo.get_contents(file_path)
            return file_content.decoded_content.decode('utf-8')
        except Exception as e:
            self.logger.warning(f"Could not read file {file_path}: {e}")
            return None
    
    def _build_github_file_structure(self, repo) -> Dict[str, Any]:
        """Build file structure from GitHub repository."""
        structure = {}
        
        def build_structure(contents, current_dict):
            for content in contents:
                if content.type == "dir":
                    if content.name not in {'.git', '.kiro', '__pycache__', 'node_modules'}:
                        current_dict[content.name] = {}
                        try:
                            sub_contents = repo.get_contents(content.path)
                            build_structure(sub_contents, current_dict[content.name])
                        except Exception:
                            pass
                else:
                    if '_files' not in current_dict:
                        current_dict['_files'] = []
                    current_dict['_files'].append(content.name)
        
        try:
            root_contents = repo.get_contents("")
            build_structure(root_contents, structure)
        except Exception as e:
            self.logger.error(f"Error building file structure: {e}")
            structure = {'error': str(e)}
        
        return structure
    
    def _get_github_raw_base_url(self, repo_url: str) -> str:
        """Convert GitHub URL to raw content base URL."""
        # https://github.com/owner/repo -> https://raw.githubusercontent.com/owner/repo/main/
        repo_path = self._extract_github_repo_path(repo_url)
        return f"https://raw.githubusercontent.com/{repo_path}/main/"
    
    def _download_raw_file(self, base_url: str, file_path: str) -> Optional[str]:
        """Download raw file content."""
        url = base_url + file_path
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                # Try with 'master' branch instead of 'main'
                master_url = base_url.replace('/main/', '/master/') + file_path
                response = requests.get(master_url, timeout=10)
                if response.status_code == 200:
                    return response.text
        except Exception as e:
            self.logger.debug(f"Error downloading {url}: {e}")
        
        return None
    
    @staticmethod
    def is_supported_url(repo_url: str) -> bool:
        """Check if the repository URL is supported."""
        supported_hosts = ['github.com', 'gitlab.com']
        return any(host in repo_url for host in supported_hosts) or GIT_AVAILABLE
    
    @staticmethod
    def get_required_dependencies() -> Dict[str, str]:
        """Get required dependencies for online analysis."""
        deps = {}
        if not GIT_AVAILABLE:
            deps['GitPython'] = 'pip install GitPython'
        if not GITHUB_API_AVAILABLE:
            deps['PyGithub'] = 'pip install PyGithub'
        if not REQUESTS_AVAILABLE:
            deps['requests'] = 'pip install requests'
        return deps