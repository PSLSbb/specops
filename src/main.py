"""Main application orchestrator for SpecOps onboarding factory."""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import traceback

try:
    # Try relative imports first (when used as package)
    from .models import AppConfig, RepositoryAnalysis, StyleConfig, HookConfig
    from .config_loader import ConfigLoader
    from .analyzers.content_analyzer import ContentAnalyzer
    from .analyzers.online_content_analyzer import OnlineContentAnalyzer
    from .ai.processing_engine import AIProcessingEngine
    from .generators.task_generator import TaskGenerator
    from .generators.faq_generator import FAQGenerator
    from .generators.quick_start_generator import QuickStartGenerator
    from .hooks.hook_manager import HookManager
    from .utils.error_handler import ErrorHandler
except ImportError:
    # Fall back to absolute imports (when run directly)
    from models import AppConfig, RepositoryAnalysis, StyleConfig, HookConfig
    from config_loader import ConfigLoader
    from analyzers.content_analyzer import ContentAnalyzer
    from analyzers.online_content_analyzer import OnlineContentAnalyzer
    from ai.processing_engine import AIProcessingEngine
    from generators.task_generator import TaskGenerator
    from generators.faq_generator import FAQGenerator
    from generators.quick_start_generator import QuickStartGenerator
    from hooks.hook_manager import HookManager
    from utils.error_handler import ErrorHandler


class SpecOpsError(Exception):
    """Base exception for SpecOps application errors."""
    pass


class SpecOpsApp:
    """Main application orchestrator that coordinates all SpecOps components."""
    
    def __init__(self, config: Optional[AppConfig] = None, workspace_path: str = '.'):
        """Initialize the SpecOps application.
        
        Args:
            config: Application configuration
            workspace_path: Path to the workspace root
        """
        self.workspace_path = Path(workspace_path).resolve()
        self.config = config or self._load_default_config()
        self.logger = self._setup_logging()
        
        # Initialize error handler
        self.error_handler = ErrorHandler(logger=self.logger)
        
        # Component instances
        self._content_analyzer: Optional[ContentAnalyzer] = None
        self._ai_engine: Optional[AIProcessingEngine] = None
        self._task_generator: Optional[TaskGenerator] = None
        self._faq_generator: Optional[FAQGenerator] = None
        self._quick_start_generator: Optional[QuickStartGenerator] = None
        self._hook_manager: Optional[HookManager] = None
        
        # Initialize components
        self._initialize_components()
        
        self.logger.info(f"SpecOps initialized for workspace: {self.workspace_path}")
    
    def _load_default_config(self) -> AppConfig:
        """Load default configuration from workspace."""
        try:
            config_loader = ConfigLoader(str(self.workspace_path))
            return config_loader.load_config()
        except Exception as e:
            # Fallback to basic config
            return AppConfig(
                workspace_path=str(self.workspace_path),
                output_dir=str(self.workspace_path)
            )
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('specops')
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        # Set log level from config
        log_level = getattr(logging, self.config.hook_config.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        return logger
    
    def _initialize_components(self) -> None:
        """Initialize all SpecOps components with proper configuration."""
        try:
            # Load style configuration content
            self.config.load_from_steering()
            
            # Initialize content analyzer
            self._content_analyzer = ContentAnalyzer(str(self.workspace_path))
            
            # Initialize AI processing engine
            self._ai_engine = AIProcessingEngine(
                model=self.config.ai_model,
                temperature=self.config.ai_temperature,
                style_config=self.config.style_config
            )
            
            # Initialize generators
            self._task_generator = TaskGenerator(style_config=self.config.style_config)
            self._faq_generator = FAQGenerator(style_config=self.config.style_config)
            self._quick_start_generator = QuickStartGenerator(style_config=self.config.style_config)
            
            # Initialize hook manager
            self._hook_manager = HookManager(
                config=self.config.hook_config,
                workspace_path=str(self.workspace_path)
            )
            
            # Wire up hook manager with other components
            self._wire_hook_manager()
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            if self.config.debug_mode:
                self.logger.error(traceback.format_exc())
            raise SpecOpsError(f"Component initialization failed: {e}")
    
    def _wire_hook_manager(self) -> None:
        """Wire the hook manager with other components for coordinated operations."""
        if not self._hook_manager:
            return
        
        # Set component references in hook manager
        self._hook_manager._content_analyzer = self._content_analyzer
        self._hook_manager._ai_engine = self._ai_engine
        self._hook_manager._task_generator = self._task_generator
        self._hook_manager._faq_generator = self._faq_generator
        self._hook_manager._quick_start_generator = self._quick_start_generator
    
    @property
    def content_analyzer(self) -> ContentAnalyzer:
        """Get the content analyzer instance."""
        if not self._content_analyzer:
            raise SpecOpsError("Content analyzer not initialized")
        return self._content_analyzer
    
    @property
    def ai_engine(self) -> AIProcessingEngine:
        """Get the AI processing engine instance."""
        if not self._ai_engine:
            raise SpecOpsError("AI engine not initialized")
        return self._ai_engine
    
    @property
    def task_generator(self) -> TaskGenerator:
        """Get the task generator instance."""
        if not self._task_generator:
            raise SpecOpsError("Task generator not initialized")
        return self._task_generator
    
    @property
    def faq_generator(self) -> FAQGenerator:
        """Get the FAQ generator instance."""
        if not self._faq_generator:
            raise SpecOpsError("FAQ generator not initialized")
        return self._faq_generator
    
    @property
    def quick_start_generator(self) -> QuickStartGenerator:
        """Get the Quick Start generator instance."""
        if not self._quick_start_generator:
            raise SpecOpsError("Quick Start generator not initialized")
        return self._quick_start_generator
    
    @property
    def hook_manager(self) -> HookManager:
        """Get the hook manager instance."""
        if not self._hook_manager:
            raise SpecOpsError("Hook manager not initialized")
        return self._hook_manager
    
    def analyze_repository(self, repo_url: Optional[str] = None) -> RepositoryAnalysis:
        """Perform full repository analysis and return structured results.
        
        Args:
            repo_url: Optional URL for online repository analysis
        """
        if repo_url:
            self.logger.info(f"Starting online repository analysis: {repo_url}")
            return self._analyze_online_repository(repo_url)
        else:
            self.logger.info("Starting local repository analysis...")
            return self._analyze_local_repository()
    
    def _analyze_local_repository(self) -> RepositoryAnalysis:
        """Analyze local repository."""
        try:
            analysis = self.content_analyzer.analyze_repository(str(self.workspace_path))
            
            self.logger.info(f"Repository analysis complete:")
            self.logger.info(f"  - {len(analysis.concepts)} concepts found")
            self.logger.info(f"  - {len(analysis.setup_steps)} setup steps found")
            self.logger.info(f"  - {len(analysis.code_examples)} code examples found")
            self.logger.info(f"  - {len(analysis.dependencies)} dependencies found")
            
            return analysis
            
        except Exception as e:
            error_msg = f"Repository analysis failed: {e}"
            self.logger.error(error_msg)
            if self.config.debug_mode:
                self.logger.error(traceback.format_exc())
            
            # Use error handler for recovery
            recovery_result = self.error_handler.handle_analysis_error(e, str(self.workspace_path))
            if recovery_result:
                self.logger.info("Using fallback analysis results")
                return recovery_result
            
            raise SpecOpsError(error_msg)
    
    def _analyze_online_repository(self, repo_url: str) -> RepositoryAnalysis:
        """Analyze online repository."""
        try:
            # Check if URL is supported
            if not OnlineContentAnalyzer.is_supported_url(repo_url):
                raise SpecOpsError(f"Unsupported repository URL: {repo_url}")
            
            # Check dependencies
            missing_deps = OnlineContentAnalyzer.get_required_dependencies()
            if missing_deps:
                self.logger.warning("Missing dependencies for online analysis:")
                for dep, install_cmd in missing_deps.items():
                    self.logger.warning(f"  {dep}: {install_cmd}")
            
            # Create online analyzer
            github_token = getattr(self.config, 'github_token', None)
            online_analyzer = OnlineContentAnalyzer(github_token=github_token)
            
            # Perform analysis
            analysis = online_analyzer.analyze_online_repository(repo_url)
            
            self.logger.info(f"Online repository analysis complete:")
            self.logger.info(f"  - {len(analysis.concepts)} concepts found")
            self.logger.info(f"  - {len(analysis.setup_steps)} setup steps found")
            self.logger.info(f"  - {len(analysis.code_examples)} code examples found")
            self.logger.info(f"  - {len(analysis.dependencies)} dependencies found")
            
            return analysis
            
        except Exception as e:
            error_msg = f"Online repository analysis failed: {e}"
            self.logger.error(error_msg)
            if self.config.debug_mode:
                self.logger.error(traceback.format_exc())
            raise SpecOpsError(error_msg)
    
    def generate_all_documents(self, analysis: Optional[RepositoryAnalysis] = None) -> Dict[str, str]:
        """Generate all onboarding documents from repository analysis.
        
        Args:
            analysis: Optional pre-computed repository analysis
            
        Returns:
            Dictionary mapping document types to their file paths
        """
        self.logger.info("Starting full document generation...")
        
        if analysis is None:
            analysis = self.analyze_repository()
        
        generated_docs = {}
        
        try:
            # Generate tasks document
            tasks_path = self._generate_tasks_document(analysis)
            if tasks_path:
                generated_docs['tasks'] = tasks_path
            
            # Generate FAQ document
            faq_path = self._generate_faq_document(analysis)
            if faq_path:
                generated_docs['faq'] = faq_path
            
            # Generate/update Quick Start in README
            readme_path = self._update_quick_start_section(analysis)
            if readme_path:
                generated_docs['quick_start'] = readme_path
            
            self.logger.info(f"Document generation complete. Generated: {list(generated_docs.keys())}")
            return generated_docs
            
        except Exception as e:
            error_msg = f"Document generation failed: {e}"
            self.logger.error(error_msg)
            if self.config.debug_mode:
                self.logger.error(traceback.format_exc())
            raise SpecOpsError(error_msg)
    
    def _generate_tasks_document(self, analysis: RepositoryAnalysis) -> Optional[str]:
        """Generate tasks.md document from repository analysis."""
        try:
            self.logger.info("Generating tasks document...")
            
            # Generate task suggestions using AI
            task_suggestions = self.ai_engine.generate_task_suggestions(analysis)
            
            # Convert to structured tasks
            task_document = self.task_generator.generate_onboarding_tasks(task_suggestions)
            
            # Format as markdown (temporary workaround)
            if hasattr(self.task_generator, 'format_tasks_markdown'):
                markdown_content = self.task_generator.format_tasks_markdown(task_document)
            else:
                # Fallback formatting
                markdown_content = "# Onboarding Tasks\n\n"
                for i, task in enumerate(task_document, 1):
                    markdown_content += f"## Task {i}: {getattr(task, 'title', 'Untitled Task')}\n\n"
                    if hasattr(task, 'description') and task.description:
                        markdown_content += f"**Description:** {task.description}\n\n"
                    markdown_content += "---\n\n"
            
            # Write to file
            tasks_path = self.workspace_path / 'tasks.md'
            with open(tasks_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.logger.info(f"Tasks document generated: {tasks_path}")
            return str(tasks_path)
            
        except Exception as e:
            self.logger.error(f"Failed to generate tasks document: {e}")
            self.error_handler.handle_generation_error(e, 'tasks')
            return None
    
    def _generate_faq_document(self, analysis: RepositoryAnalysis) -> Optional[str]:
        """Generate faq.md document from repository analysis."""
        try:
            self.logger.info("Generating FAQ document...")
            
            # Generate FAQ pairs using AI
            faq_pairs = self.ai_engine.create_faq_pairs(analysis)
            
            # Generate FAQ content
            faq_content = self.faq_generator.generate_faqs(faq_pairs)
            
            # Check for existing FAQ and merge if needed
            faq_path = self.workspace_path / 'faq.md'
            if faq_path.exists():
                faq_content = self.faq_generator.merge_with_existing(faq_content, str(faq_path))
            
            # Write to file
            with open(faq_path, 'w', encoding='utf-8') as f:
                f.write(faq_content)
            
            self.logger.info(f"FAQ document generated: {faq_path}")
            return str(faq_path)
            
        except Exception as e:
            self.logger.error(f"Failed to generate FAQ document: {e}")
            self.error_handler.handle_generation_error(e, 'faq')
            return None
    
    def _update_quick_start_section(self, analysis: RepositoryAnalysis) -> Optional[str]:
        """Update Quick Start section in README from repository analysis."""
        try:
            self.logger.info("Updating Quick Start section...")
            
            # Generate Quick Start guide using AI
            quick_start_guide = self.ai_engine.extract_quick_start_steps(analysis)
            
            # Generate Quick Start content
            quick_start_content = self.quick_start_generator.generate_quick_start(quick_start_guide)
            
            # Find README file
            readme_path = self._find_readme_file()
            if not readme_path:
                self.logger.warning("No README file found, skipping Quick Start update")
                return None
            
            # Update README with Quick Start section
            self.quick_start_generator.update_readme_section(str(readme_path), quick_start_content)
            
            self.logger.info(f"Quick Start section updated in: {readme_path}")
            return str(readme_path)
            
        except Exception as e:
            self.logger.error(f"Failed to update Quick Start section: {e}")
            self.error_handler.handle_generation_error(e, 'quick_start')
            return None
    
    def _find_readme_file(self) -> Optional[Path]:
        """Find README file in the workspace."""
        readme_names = ['README.md', 'readme.md', 'Readme.md', 'README.txt', 'readme.txt']
        
        for name in readme_names:
            readme_path = self.workspace_path / name
            if readme_path.exists():
                return readme_path
        
        return None
    
    def register_hooks(self) -> None:
        """Register all Kiro hooks for automatic content updates."""
        try:
            self.logger.info("Registering Kiro hooks...")
            
            if self.config.hook_config.feature_created_enabled:
                self.hook_manager.register_feature_created_hook()
                self.logger.info("Feature-created hook registered")
            
            if self.config.hook_config.readme_save_enabled:
                self.hook_manager.register_readme_save_hook()
                self.logger.info("README-save hook registered")
            
            self.logger.info("Hook registration complete")
            
        except Exception as e:
            self.logger.error(f"Failed to register hooks: {e}")
            if self.config.debug_mode:
                self.logger.error(traceback.format_exc())
            raise SpecOpsError(f"Hook registration failed: {e}")
    
    def handle_feature_created(self, feature_path: str) -> None:
        """Handle feature creation event."""
        try:
            self.logger.info(f"Handling feature created: {feature_path}")
            self.hook_manager.handle_feature_created(feature_path)
        except Exception as e:
            self.logger.error(f"Failed to handle feature created event: {e}")
            self.error_handler.handle_hook_error(e, 'feature_created', feature_path)
    
    def handle_readme_saved(self, readme_path: str) -> None:
        """Handle README save event."""
        try:
            self.logger.info(f"Handling README saved: {readme_path}")
            self.hook_manager.handle_readme_saved(readme_path)
        except Exception as e:
            self.logger.error(f"Failed to handle README saved event: {e}")
            self.error_handler.handle_hook_error(e, 'readme_saved', readme_path)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current application status and component health."""
        status = {
            'workspace_path': str(self.workspace_path),
            'config': {
                'ai_model': self.config.ai_model,
                'debug_mode': self.config.debug_mode,
                'hooks_enabled': {
                    'feature_created': self.config.hook_config.feature_created_enabled,
                    'readme_save': self.config.hook_config.readme_save_enabled
                }
            },
            'components': {
                'content_analyzer': self._content_analyzer is not None,
                'ai_engine': self._ai_engine is not None,
                'task_generator': self._task_generator is not None,
                'faq_generator': self._faq_generator is not None,
                'quick_start_generator': self._quick_start_generator is not None,
                'hook_manager': self._hook_manager is not None
            }
        }
        
        return status
    
    def shutdown(self) -> None:
        """Gracefully shutdown the application and cleanup resources."""
        self.logger.info("Shutting down SpecOps application...")
        
        try:
            # Cleanup hook manager
            if self._hook_manager:
                # Hook manager cleanup would go here if needed
                pass
            
            # Clear component references
            self._content_analyzer = None
            self._ai_engine = None
            self._task_generator = None
            self._faq_generator = None
            self._quick_start_generator = None
            self._hook_manager = None
            
            self.logger.info("SpecOps application shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


def create_app(workspace_path: str = '.', config: Optional[AppConfig] = None) -> SpecOpsApp:
    """Factory function to create a SpecOps application instance.
    
    Args:
        workspace_path: Path to the workspace root
        config: Optional application configuration
        
    Returns:
        Configured SpecOps application instance
    """
    return SpecOpsApp(config=config, workspace_path=workspace_path)