"""Hook Manager for Kiro integration and event handling."""

import logging
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import json
import traceback

from ..models import HookConfig, FeatureAnalysis, AppConfig
from ..interfaces import HookManagerInterface
from ..ai.processing_engine import AIProcessingEngine
from ..generators.task_generator import TaskGenerator
from ..generators.faq_generator import FAQGenerator
from ..generators.quick_start_generator import QuickStartGenerator
from ..analyzers.content_analyzer import ContentAnalyzer


class HookError(Exception):
    """Raised when hook operations fail."""
    pass


class HookManager(HookManagerInterface):
    """Manages Kiro hook registration and execution coordination."""
    
    def __init__(self, config: Optional[HookConfig] = None, workspace_path: str = '.'):
        """Initialize the hook manager with configuration.
        
        Args:
            config: Hook configuration settings
            workspace_path: Path to the workspace root
        """
        self.config = config or HookConfig()
        self.workspace_path = Path(workspace_path)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Hook handlers registry
        self._handlers: Dict[str, Callable] = {}
        
        # Hook execution state
        self._hook_registry: Dict[str, Dict[str, Any]] = {}
        
        # Initialize components for hook processing
        self._initialize_components()
        
        # Initialize hook registry
        self._initialize_registry()
    
    def _setup_logging(self) -> None:
        """Configure logging for hook operations."""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _initialize_components(self) -> None:
        """Initialize the processing components for hook operations."""
        try:
            # Initialize content analyzer
            self.content_analyzer = ContentAnalyzer(str(self.workspace_path))
            
            # Initialize AI processing engine
            self.ai_engine = AIProcessingEngine()
            
            # Initialize generators
            self.task_generator = TaskGenerator()
            self.faq_generator = FAQGenerator()
            self.quick_start_generator = QuickStartGenerator()
            
            self.logger.info("Successfully initialized all processing components")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize processing components: {str(e)}")
            # Set components to None to handle gracefully
            self.content_analyzer = None
            self.ai_engine = None
            self.task_generator = None
            self.faq_generator = None
            self.quick_start_generator = None
    
    def _initialize_registry(self) -> None:
        """Initialize the hook registry with default configurations."""
        self._hook_registry = {
            'feature_created': {
                'enabled': self.config.feature_created_enabled,
                'handler': 'handle_feature_created',
                'timeout': self.config.hook_timeout,
                'max_retries': self.config.max_retries,
                'description': 'Triggered when a new feature is created'
            },
            'readme_save': {
                'enabled': self.config.readme_save_enabled,
                'handler': 'handle_readme_saved',
                'timeout': self.config.hook_timeout,
                'max_retries': self.config.max_retries,
                'description': 'Triggered when README files are saved'
            }
        }
        
        self.logger.info(f"Initialized hook registry with {len(self._hook_registry)} hooks")
    
    def register_feature_created_hook(self) -> None:
        """Register the feature-created hook with Kiro.
        
        This method sets up the hook configuration and registers it
        with Kiro's hook system for automatic triggering.
        """
        if not self.config.is_hook_enabled('feature_created'):
            self.logger.info("Feature created hook is disabled, skipping registration")
            return
        
        try:
            hook_config = {
                'name': 'specops_feature_created',
                'event': 'feature_created',
                'handler': self.handle_feature_created,
                'timeout': self.config.hook_timeout,
                'max_retries': self.config.max_retries,
                'description': 'SpecOps onboarding factory feature creation handler'
            }
            
            # Register handler in internal registry
            self._handlers['feature_created'] = self.handle_feature_created
            
            # Update registry status
            self._hook_registry['feature_created']['registered'] = True
            self._hook_registry['feature_created']['config'] = hook_config
            
            self.logger.info("Successfully registered feature_created hook")
            
        except Exception as e:
            error_msg = f"Failed to register feature_created hook: {str(e)}"
            self.logger.error(error_msg)
            raise HookError(error_msg) from e
    
    def register_readme_save_hook(self) -> None:
        """Register the README-save hook with Kiro.
        
        This method sets up the hook configuration and registers it
        with Kiro's hook system for automatic triggering.
        """
        if not self.config.is_hook_enabled('readme_save'):
            self.logger.info("README save hook is disabled, skipping registration")
            return
        
        try:
            hook_config = {
                'name': 'specops_readme_save',
                'event': 'readme_save',
                'handler': self.handle_readme_saved,
                'timeout': self.config.hook_timeout,
                'max_retries': self.config.max_retries,
                'description': 'SpecOps onboarding factory README save handler'
            }
            
            # Register handler in internal registry
            self._handlers['readme_save'] = self.handle_readme_saved
            
            # Update registry status
            self._hook_registry['readme_save']['registered'] = True
            self._hook_registry['readme_save']['config'] = hook_config
            
            self.logger.info("Successfully registered readme_save hook")
            
        except Exception as e:
            error_msg = f"Failed to register readme_save hook: {str(e)}"
            self.logger.error(error_msg)
            raise HookError(error_msg) from e
    
    def register_all_hooks(self) -> None:
        """Register all enabled hooks with Kiro."""
        self.logger.info("Registering all enabled hooks")
        
        try:
            self.register_feature_created_hook()
            self.register_readme_save_hook()
            self.logger.info("Successfully registered all hooks")
        except Exception as e:
            self.logger.error(f"Failed to register some hooks: {str(e)}")
            raise
    
    def handle_feature_created(self, feature_path: str) -> None:
        """Handle feature creation event.
        
        This method is called when a new feature is created and processes
        the feature to generate corresponding onboarding tasks.
        
        Args:
            feature_path: Path to the newly created feature file
            
        Raises:
            HookError: If feature processing fails
        """
        self.logger.info(f"Handling feature_created event for: {feature_path}")
        
        if not self.config.is_hook_enabled('feature_created'):
            self.logger.warning("Feature created hook is disabled, ignoring event")
            return
        
        try:
            # Validate feature path
            if not feature_path or not isinstance(feature_path, str):
                raise HookError("Invalid feature_path provided")
            
            feature_file = Path(feature_path)
            if not feature_file.exists():
                raise HookError(f"Feature file does not exist: {feature_path}")
            
            # Log the event
            self.logger.info(f"Processing new feature: {feature_file.name}")
            
            # Check if components are available
            if not self.ai_engine or not self.task_generator:
                self.logger.warning("Required components not available, skipping feature processing")
                return
            
            # Analyze the feature code
            feature_analysis = self.ai_engine.analyze_feature_code(feature_path)
            self.logger.info(f"Analyzed feature: {feature_analysis.feature_path}")
            
            # Find existing tasks.md file
            tasks_file = self._find_tasks_file()
            if not tasks_file:
                self.logger.warning("No tasks.md file found, cannot append feature tasks")
                return
            
            # Generate tasks for the new feature
            try:
                # Read existing tasks
                existing_tasks = self.task_generator.load_tasks_from_file(str(tasks_file))
                
                # Append new feature tasks
                updated_tasks = self.task_generator.append_feature_tasks(feature_analysis, existing_tasks)
                
                # Write updated tasks back to file
                tasks_markdown = self.task_generator.format_tasks_markdown(updated_tasks)
                with open(tasks_file, 'w', encoding='utf-8') as f:
                    f.write(tasks_markdown)
                
                self.logger.info(f"Successfully updated tasks.md with new feature tasks")
                
            except Exception as task_error:
                self.logger.error(f"Failed to update tasks: {str(task_error)}")
                # Continue with graceful degradation
            
            self._log_hook_execution('feature_created', feature_path, 'success')
            self.logger.info(f"Successfully processed feature: {feature_path}")
            
        except Exception as e:
            error_msg = f"Failed to handle feature_created event for {feature_path}: {str(e)}"
            self.logger.error(error_msg)
            self.logger.debug(traceback.format_exc())
            self._log_hook_execution('feature_created', feature_path, 'error', str(e))
            
            # Apply graceful degradation - don't re-raise to avoid breaking the hook system
            if self.config.max_retries > 0:
                self.logger.info(f"Hook will be retried up to {self.config.max_retries} times")
            else:
                self.logger.warning("Hook execution failed and retries are disabled")
    
    def handle_readme_saved(self, readme_path: str) -> None:
        """Handle README save event.
        
        This method is called when a README file is saved and triggers
        updates to Quick Start sections and FAQ content.
        
        Args:
            readme_path: Path to the saved README file
            
        Raises:
            HookError: If README processing fails
        """
        self.logger.info(f"Handling readme_saved event for: {readme_path}")
        
        if not self.config.is_hook_enabled('readme_save'):
            self.logger.warning("README save hook is disabled, ignoring event")
            return
        
        try:
            # Validate README path
            if not readme_path or not isinstance(readme_path, str):
                raise HookError("Invalid readme_path provided")
            
            readme_file = Path(readme_path)
            if not readme_file.exists():
                raise HookError(f"README file does not exist: {readme_path}")
            
            # Log the event
            self.logger.info(f"Processing README save: {readme_file.name}")
            
            # Check if components are available
            if not self.content_analyzer or not self.ai_engine:
                self.logger.warning("Required components not available, skipping README processing")
                return
            
            # Re-analyze repository content
            repo_analysis = self.content_analyzer.analyze_repository(str(self.workspace_path))
            self.logger.info(f"Re-analyzed repository content")
            
            # Update Quick Start section if components are available
            if self.quick_start_generator:
                try:
                    # Generate Quick Start guide from analysis
                    quick_start_guide = self.ai_engine.extract_quick_start_steps(repo_analysis)
                    
                    # Generate Quick Start content
                    quick_start_content = self.quick_start_generator.generate_quick_start(quick_start_guide)
                    
                    # Update README with Quick Start content
                    self.quick_start_generator.update_readme_section(readme_path, quick_start_content)
                    
                    self.logger.info("Successfully updated Quick Start section")
                    
                except Exception as qs_error:
                    self.logger.error(f"Failed to update Quick Start section: {str(qs_error)}")
                    # Continue with graceful degradation
            
            # Update FAQ content if components are available
            if self.faq_generator:
                try:
                    # Generate FAQ pairs from analysis
                    faq_pairs = self.ai_engine.create_faq_pairs(repo_analysis)
                    
                    # Find or create FAQ file
                    faq_file = self._find_or_create_faq_file()
                    
                    # Generate FAQ content
                    faq_content = self.faq_generator.generate_faqs(faq_pairs)
                    
                    # Merge with existing FAQ content
                    final_faq_content = self.faq_generator.merge_with_existing(faq_content, str(faq_file))
                    
                    # Write updated FAQ content
                    with open(faq_file, 'w', encoding='utf-8') as f:
                        f.write(final_faq_content)
                    
                    self.logger.info("Successfully updated FAQ content")
                    
                except Exception as faq_error:
                    self.logger.error(f"Failed to update FAQ content: {str(faq_error)}")
                    # Continue with graceful degradation
            
            self._log_hook_execution('readme_save', readme_path, 'success')
            self.logger.info(f"Successfully processed README: {readme_path}")
            
        except Exception as e:
            error_msg = f"Failed to handle readme_saved event for {readme_path}: {str(e)}"
            self.logger.error(error_msg)
            self.logger.debug(traceback.format_exc())
            self._log_hook_execution('readme_save', readme_path, 'error', str(e))
            
            # Apply graceful degradation - don't re-raise to avoid breaking the hook system
            if self.config.max_retries > 0:
                self.logger.info(f"Hook will be retried up to {self.config.max_retries} times")
            else:
                self.logger.warning("Hook execution failed and retries are disabled")
    
    def _log_hook_execution(self, hook_type: str, file_path: str, status: str, error: Optional[str] = None) -> None:
        """Log hook execution details for monitoring and debugging.
        
        Args:
            hook_type: Type of hook that was executed
            file_path: Path of the file that triggered the hook
            status: Execution status ('success', 'error', 'retry')
            error: Error message if status is 'error'
        """
        log_entry = {
            'hook_type': hook_type,
            'file_path': file_path,
            'status': status,
            'timestamp': None,  # Would be set by logging system
        }
        
        if error:
            log_entry['error'] = error
        
        if status == 'success':
            self.logger.info(f"Hook execution completed: {json.dumps(log_entry, indent=2)}")
        elif status == 'error':
            self.logger.error(f"Hook execution failed: {json.dumps(log_entry, indent=2)}")
        else:
            self.logger.debug(f"Hook execution status: {json.dumps(log_entry, indent=2)}")
    
    def get_hook_status(self) -> Dict[str, Any]:
        """Get current status of all registered hooks.
        
        Returns:
            Dictionary containing hook status information
        """
        status = {
            'hooks': {},
            'config': {
                'feature_created_enabled': self.config.feature_created_enabled,
                'readme_save_enabled': self.config.readme_save_enabled,
                'hook_timeout': self.config.hook_timeout,
                'max_retries': self.config.max_retries,
                'log_level': self.config.log_level
            }
        }
        
        for hook_name, hook_info in self._hook_registry.items():
            status['hooks'][hook_name] = {
                'enabled': hook_info['enabled'],
                'registered': hook_info.get('registered', False),
                'handler': hook_info['handler'],
                'description': hook_info['description']
            }
        
        return status
    
    def unregister_hook(self, hook_type: str) -> None:
        """Unregister a specific hook.
        
        Args:
            hook_type: Type of hook to unregister ('feature_created' or 'readme_save')
        """
        if hook_type not in self._hook_registry:
            self.logger.warning(f"Unknown hook type: {hook_type}")
            return
        
        try:
            # Remove from handlers registry
            if hook_type in self._handlers:
                del self._handlers[hook_type]
            
            # Update registry status
            self._hook_registry[hook_type]['registered'] = False
            if 'config' in self._hook_registry[hook_type]:
                del self._hook_registry[hook_type]['config']
            
            self.logger.info(f"Successfully unregistered {hook_type} hook")
            
        except Exception as e:
            error_msg = f"Failed to unregister {hook_type} hook: {str(e)}"
            self.logger.error(error_msg)
            raise HookError(error_msg) from e
    
    def unregister_all_hooks(self) -> None:
        """Unregister all hooks."""
        self.logger.info("Unregistering all hooks")
        
        for hook_type in list(self._hook_registry.keys()):
            try:
                self.unregister_hook(hook_type)
            except Exception as e:
                self.logger.error(f"Failed to unregister {hook_type}: {str(e)}")
        
        self.logger.info("Finished unregistering hooks")
    
    def update_config(self, new_config: HookConfig) -> None:
        """Update hook configuration and re-register hooks if needed.
        
        Args:
            new_config: New hook configuration
        """
        old_config = self.config
        self.config = new_config
        
        # Update logging level if changed
        if old_config.log_level != new_config.log_level:
            self._setup_logging()
        
        # Re-initialize registry with new config
        self._initialize_registry()
        
        # Re-register hooks if they were previously registered
        try:
            if old_config.feature_created_enabled and new_config.feature_created_enabled:
                self.register_feature_created_hook()
            elif not new_config.feature_created_enabled:
                self.unregister_hook('feature_created')
            
            if old_config.readme_save_enabled and new_config.readme_save_enabled:
                self.register_readme_save_hook()
            elif not new_config.readme_save_enabled:
                self.unregister_hook('readme_save')
                
        except Exception as e:
            self.logger.error(f"Failed to update hook registrations: {str(e)}")
            raise
        
        self.logger.info("Successfully updated hook configuration")
    
    def _find_tasks_file(self) -> Optional[Path]:
        """Find the tasks.md file in the workspace.
        
        Returns:
            Path to tasks.md file or None if not found
        """
        # Look for tasks.md in common locations
        possible_paths = [
            self.workspace_path / 'tasks.md',
            self.workspace_path / '.kiro' / 'specs' / '*' / 'tasks.md',
            self.workspace_path / 'docs' / 'tasks.md',
        ]
        
        for path_pattern in possible_paths:
            if '*' in str(path_pattern):
                # Handle glob patterns
                from glob import glob
                matches = glob(str(path_pattern))
                if matches:
                    return Path(matches[0])  # Return first match
            else:
                if path_pattern.exists():
                    return path_pattern
        
        # If not found, look recursively
        for tasks_file in self.workspace_path.rglob('tasks.md'):
            return tasks_file
        
        return None
    
    def _find_or_create_faq_file(self) -> Path:
        """Find existing FAQ file or determine where to create one.
        
        Returns:
            Path to FAQ file (existing or where it should be created)
        """
        # Look for existing FAQ files
        possible_names = ['faq.md', 'FAQ.md', 'frequently-asked-questions.md']
        
        for name in possible_names:
            faq_path = self.workspace_path / name
            if faq_path.exists():
                return faq_path
        
        # Look in common directories
        common_dirs = ['docs', '.kiro/specs']
        for dir_name in common_dirs:
            dir_path = self.workspace_path / dir_name
            if dir_path.exists():
                for name in possible_names:
                    faq_path = dir_path / name
                    if faq_path.exists():
                        return faq_path
        
        # Look recursively for any FAQ file
        for faq_file in self.workspace_path.rglob('*faq*.md'):
            return faq_file
        
        # If no FAQ file found, create in workspace root
        return self.workspace_path / 'faq.md'