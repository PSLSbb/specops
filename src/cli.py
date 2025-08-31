"""Command-line interface for SpecOps onboarding factory."""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

try:
    # Try relative imports first (when used as package)
    from .main import SpecOpsApp, create_app, SpecOpsError
    from .models import AppConfig
    from .config_loader import ConfigLoader
except ImportError:
    # Fall back to absolute imports (when run directly)
    from main import SpecOpsApp, create_app, SpecOpsError
    from models import AppConfig
    from config_loader import ConfigLoader


class CLIError(Exception):
    """Raised when CLI operations fail."""
    pass


class ProgressReporter:
    """Simple progress reporting for CLI operations."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.current_step = 0
        self.total_steps = 0
    
    def start(self, total_steps: int, operation: str) -> None:
        """Start progress reporting for an operation."""
        self.total_steps = total_steps
        self.current_step = 0
        if self.verbose:
            print(f"Starting {operation}...")
    
    def step(self, message: str) -> None:
        """Report progress for a single step."""
        self.current_step += 1
        if self.verbose:
            progress = f"[{self.current_step}/{self.total_steps}]"
            print(f"{progress} {message}")
    
    def complete(self, message: str) -> None:
        """Report completion of the operation."""
        if self.verbose:
            print(f"✓ {message}")
        else:
            print(message)
    
    def error(self, message: str) -> None:
        """Report an error."""
        print(f"✗ Error: {message}", file=sys.stderr)
    
    def warning(self, message: str) -> None:
        """Report a warning."""
        if self.verbose:
            print(f"⚠ Warning: {message}")


class SpecOpsCLI:
    """Command-line interface for SpecOps operations."""
    
    def __init__(self):
        self.app: Optional[SpecOpsApp] = None
        self.reporter = ProgressReporter()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser for the CLI."""
        parser = argparse.ArgumentParser(
            prog='specops',
            description='SpecOps: AI-powered spec-first onboarding factory',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  specops analyze                    # Analyze repository content
  specops generate --all             # Generate all documents
  specops generate --tasks           # Generate only tasks.md
  specops generate --faq             # Generate only faq.md
  specops generate --quick-start     # Update README Quick Start
  specops hooks --register           # Register Kiro hooks
  specops hooks --status             # Show hook status
  specops status                     # Show application status
            """
        )
        
        # Global options
        parser.add_argument(
            '--workspace', '-w',
            type=str,
            default='.',
            help='Workspace directory path (default: current directory)'
        )
        parser.add_argument(
            '--config', '-c',
            type=str,
            help='Path to configuration file'
        )
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode'
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Analyze command
        analyze_parser = subparsers.add_parser(
            'analyze',
            help='Analyze repository content and extract structured information'
        )
        analyze_parser.add_argument(
            '--output', '-o',
            type=str,
            help='Output file for analysis results (JSON format)'
        )
        analyze_parser.add_argument(
            '--repo-url', '-r',
            type=str,
            help='URL of online repository to analyze (GitHub, GitLab, etc.)'
        )
        analyze_parser.add_argument(
            '--github-token',
            type=str,
            help='GitHub API token for private repositories'
        )
        
        # Generate command
        generate_parser = subparsers.add_parser(
            'generate',
            help='Generate onboarding documents'
        )
        generate_group = generate_parser.add_mutually_exclusive_group()
        generate_group.add_argument(
            '--all',
            action='store_true',
            help='Generate all documents (tasks, FAQ, Quick Start)'
        )
        generate_group.add_argument(
            '--tasks',
            action='store_true',
            help='Generate tasks.md document'
        )
        generate_group.add_argument(
            '--faq',
            action='store_true',
            help='Generate faq.md document'
        )
        generate_group.add_argument(
            '--quick-start',
            action='store_true',
            help='Update README Quick Start section'
        )
        generate_parser.add_argument(
            '--analysis-file',
            type=str,
            help='Use pre-computed analysis from JSON file'
        )
        
        # Hooks command
        hooks_parser = subparsers.add_parser(
            'hooks',
            help='Manage Kiro hook integration'
        )
        hooks_group = hooks_parser.add_mutually_exclusive_group(required=True)
        hooks_group.add_argument(
            '--register',
            action='store_true',
            help='Register all enabled hooks'
        )
        hooks_group.add_argument(
            '--status',
            action='store_true',
            help='Show hook registration status'
        )
        hooks_group.add_argument(
            '--feature-created',
            type=str,
            metavar='PATH',
            help='Manually trigger feature-created hook for specified path'
        )
        hooks_group.add_argument(
            '--readme-saved',
            type=str,
            metavar='PATH',
            help='Manually trigger README-saved hook for specified path'
        )
        
        # Status command
        status_parser = subparsers.add_parser(
            'status',
            help='Show application status and component health'
        )
        status_parser.add_argument(
            '--json',
            action='store_true',
            help='Output status in JSON format'
        )
        
        # Config command
        config_parser = subparsers.add_parser(
            'config',
            help='Configuration management'
        )
        config_group = config_parser.add_mutually_exclusive_group(required=True)
        config_group.add_argument(
            '--show',
            action='store_true',
            help='Show current configuration'
        )
        config_group.add_argument(
            '--validate',
            action='store_true',
            help='Validate configuration files'
        )
        
        return parser
    
    def initialize_app(self, workspace: str, config_path: Optional[str] = None, debug: bool = False) -> None:
        """Initialize the SpecOps application."""
        try:
            # Load configuration
            config = None
            if config_path:
                config_loader = ConfigLoader(workspace)
                config = config_loader.load_from_file(config_path)
            
            # Override debug mode if specified
            if config and debug:
                config.debug_mode = debug
            elif debug:
                config = AppConfig(workspace_path=workspace, debug_mode=debug)
            
            # Create application
            self.app = create_app(workspace_path=workspace, config=config)
            
        except Exception as e:
            raise CLIError(f"Failed to initialize application: {e}")
    
    def cmd_analyze(self, args: argparse.Namespace) -> int:
        """Execute the analyze command."""
        if not self.app:
            self.reporter.error("Application not initialized")
            return 1
        
        try:
            self.reporter.start(3, "repository analysis")
            
            if args.repo_url:
                self.reporter.step(f"Analyzing online repository: {args.repo_url}")
                # Set GitHub token if provided
                if args.github_token:
                    self.app.config.github_token = args.github_token
                analysis = self.app.analyze_repository(repo_url=args.repo_url)
            else:
                self.reporter.step("Scanning repository content...")
                analysis = self.app.analyze_repository()
            
            self.reporter.step("Processing analysis results...")
            
            # Output results
            if args.output:
                self.reporter.step(f"Writing results to {args.output}...")
                output_path = Path(args.output)
                
                # Convert analysis to JSON-serializable format
                analysis_dict = {
                    'concepts': [
                        {
                            'name': c.name,
                            'description': c.description,
                            'importance': c.importance,
                            'related_files': c.related_files,
                            'prerequisites': c.prerequisites
                        } for c in analysis.concepts
                    ],
                    'setup_steps': [
                        {
                            'title': s.title,
                            'description': s.description,
                            'commands': s.commands,
                            'prerequisites': s.prerequisites,
                            'order': s.order
                        } for s in analysis.setup_steps
                    ],
                    'code_examples': [
                        {
                            'title': e.title,
                            'code': e.code,
                            'language': e.language,
                            'description': e.description,
                            'file_path': e.file_path
                        } for e in analysis.code_examples
                    ],
                    'dependencies': [
                        {
                            'name': d.name,
                            'version': d.version,
                            'type': d.type,
                            'description': d.description
                        } for d in analysis.dependencies
                    ],
                    'file_structure': analysis.file_structure
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
                
                self.reporter.complete(f"Analysis results saved to {args.output}")
            else:
                # Print summary to console
                self.reporter.complete("Repository analysis complete")
                print(f"Found {len(analysis.concepts)} concepts")
                print(f"Found {len(analysis.setup_steps)} setup steps")
                print(f"Found {len(analysis.code_examples)} code examples")
                print(f"Found {len(analysis.dependencies)} dependencies")
            
            return 0
            
        except Exception as e:
            self.reporter.error(f"Analysis failed: {e}")
            return 1
    
    def cmd_generate(self, args: argparse.Namespace) -> int:
        """Execute the generate command."""
        if not self.app:
            self.reporter.error("Application not initialized")
            return 1
        
        try:
            # Load analysis if provided
            analysis = None
            if args.analysis_file:
                self.reporter.step(f"Loading analysis from {args.analysis_file}...")
                # For now, we'll re-analyze since loading from JSON would require more complex deserialization
                self.reporter.warning("Analysis file loading not yet implemented, performing fresh analysis")
            
            # Determine what to generate
            generate_all = args.all or not any([args.tasks, args.faq, args.quick_start])
            
            if generate_all:
                self.reporter.start(4, "document generation")
                self.reporter.step("Analyzing repository...")
                generated_docs = self.app.generate_all_documents(analysis)
                
                self.reporter.step("Generating documents...")
                success_count = len(generated_docs)
                
                self.reporter.complete(f"Generated {success_count} documents: {', '.join(generated_docs.keys())}")
                
                for doc_type, path in generated_docs.items():
                    print(f"  {doc_type}: {path}")
            
            else:
                # Generate specific documents
                if not analysis:
                    self.reporter.step("Analyzing repository...")
                    analysis = self.app.analyze_repository()
                
                generated = []
                
                if args.tasks:
                    self.reporter.step("Generating tasks document...")
                    tasks_path = self.app._generate_tasks_document(analysis)
                    if tasks_path:
                        generated.append(f"tasks: {tasks_path}")
                
                if args.faq:
                    self.reporter.step("Generating FAQ document...")
                    faq_path = self.app._generate_faq_document(analysis)
                    if faq_path:
                        generated.append(f"faq: {faq_path}")
                
                if args.quick_start:
                    self.reporter.step("Updating Quick Start section...")
                    readme_path = self.app._update_quick_start_section(analysis)
                    if readme_path:
                        generated.append(f"quick_start: {readme_path}")
                
                if generated:
                    self.reporter.complete(f"Generated {len(generated)} documents")
                    for doc in generated:
                        print(f"  {doc}")
                else:
                    self.reporter.error("No documents were generated")
                    return 1
            
            return 0
            
        except Exception as e:
            self.reporter.error(f"Generation failed: {e}")
            return 1
    
    def cmd_hooks(self, args: argparse.Namespace) -> int:
        """Execute the hooks command."""
        if not self.app:
            self.reporter.error("Application not initialized")
            return 1
        
        try:
            if args.register:
                self.reporter.start(2, "hook registration")
                self.reporter.step("Registering Kiro hooks...")
                self.app.register_hooks()
                self.reporter.complete("Hooks registered successfully")
            
            elif args.status:
                status = self.app.get_status()
                hooks_config = status['config']['hooks_enabled']
                
                print("Hook Status:")
                print(f"  Feature Created: {'✓ enabled' if hooks_config['feature_created'] else '✗ disabled'}")
                print(f"  README Save: {'✓ enabled' if hooks_config['readme_save'] else '✗ disabled'}")
            
            elif args.feature_created:
                self.reporter.step(f"Triggering feature-created hook for {args.feature_created}...")
                self.app.handle_feature_created(args.feature_created)
                self.reporter.complete("Feature-created hook executed")
            
            elif args.readme_saved:
                self.reporter.step(f"Triggering README-saved hook for {args.readme_saved}...")
                self.app.handle_readme_saved(args.readme_saved)
                self.reporter.complete("README-saved hook executed")
            
            return 0
            
        except Exception as e:
            self.reporter.error(f"Hook operation failed: {e}")
            return 1
    
    def cmd_status(self, args: argparse.Namespace) -> int:
        """Execute the status command."""
        if not self.app:
            self.reporter.error("Application not initialized")
            return 1
        
        try:
            status = self.app.get_status()
            
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print("SpecOps Status:")
                print(f"  Workspace: {status['workspace_path']}")
                print(f"  AI Model: {status['config']['ai_model']}")
                print(f"  Debug Mode: {status['config']['debug_mode']}")
                
                print("\nComponents:")
                for component, initialized in status['components'].items():
                    status_icon = "✓" if initialized else "✗"
                    print(f"  {component}: {status_icon}")
                
                print("\nHooks:")
                hooks = status['config']['hooks_enabled']
                for hook, enabled in hooks.items():
                    status_icon = "✓" if enabled else "✗"
                    print(f"  {hook}: {status_icon}")
            
            return 0
            
        except Exception as e:
            self.reporter.error(f"Status check failed: {e}")
            return 1
    
    def cmd_config(self, args: argparse.Namespace) -> int:
        """Execute the config command."""
        try:
            if args.show:
                if self.app:
                    config_dict = self.app.config.to_dict()
                    print(json.dumps(config_dict, indent=2))
                else:
                    # Load config without initializing full app
                    config_loader = ConfigLoader(args.workspace if hasattr(args, 'workspace') else '.')
                    config = config_loader.load_config()
                    print(json.dumps(config.to_dict(), indent=2))
            
            elif args.validate:
                config_loader = ConfigLoader(args.workspace if hasattr(args, 'workspace') else '.')
                try:
                    config = config_loader.load_config()
                    config.validate()
                    self.reporter.complete("Configuration is valid")
                except Exception as e:
                    self.reporter.error(f"Configuration validation failed: {e}")
                    return 1
            
            return 0
            
        except Exception as e:
            self.reporter.error(f"Config operation failed: {e}")
            return 1
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with the given arguments."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Set up progress reporter
        self.reporter = ProgressReporter(verbose=parsed_args.verbose)
        
        # Handle case where no command is specified
        if not parsed_args.command:
            parser.print_help()
            return 1
        
        # Initialize app for most commands (except config show/validate)
        needs_app = True
        if parsed_args.command == 'config' and (parsed_args.show or parsed_args.validate):
            needs_app = False
        
        if needs_app:
            try:
                self.initialize_app(
                    workspace=parsed_args.workspace,
                    config_path=getattr(parsed_args, 'config', None),
                    debug=parsed_args.debug
                )
            except CLIError as e:
                self.reporter.error(str(e))
                return 1
        
        # Execute command
        try:
            if parsed_args.command == 'analyze':
                return self.cmd_analyze(parsed_args)
            elif parsed_args.command == 'generate':
                return self.cmd_generate(parsed_args)
            elif parsed_args.command == 'hooks':
                return self.cmd_hooks(parsed_args)
            elif parsed_args.command == 'status':
                return self.cmd_status(parsed_args)
            elif parsed_args.command == 'config':
                return self.cmd_config(parsed_args)
            else:
                self.reporter.error(f"Unknown command: {parsed_args.command}")
                return 1
                
        except KeyboardInterrupt:
            self.reporter.error("Operation cancelled by user")
            return 130
        except Exception as e:
            self.reporter.error(f"Unexpected error: {e}")
            if parsed_args.debug:
                import traceback
                traceback.print_exc()
            return 1
        finally:
            # Cleanup
            if self.app:
                self.app.shutdown()


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    cli = SpecOpsCLI()
    return cli.run(args)


if __name__ == '__main__':
    sys.exit(main())