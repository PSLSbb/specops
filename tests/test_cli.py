"""Tests for SpecOps CLI interface."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
from pathlib import Path
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.cli import SpecOpsCLI, CLIError, ProgressReporter
from src.models import AppConfig, RepositoryAnalysis


class TestProgressReporter(unittest.TestCase):
    """Test progress reporting functionality."""
    
    def setUp(self):
        self.reporter = ProgressReporter(verbose=True)
    
    def test_progress_reporting(self):
        """Test basic progress reporting flow."""
        with patch('builtins.print') as mock_print:
            self.reporter.start(3, "test operation")
            self.reporter.step("step 1")
            self.reporter.step("step 2")
            self.reporter.complete("done")
            
            # Verify print calls
            self.assertEqual(mock_print.call_count, 4)
    
    def test_non_verbose_mode(self):
        """Test progress reporting in non-verbose mode."""
        reporter = ProgressReporter(verbose=False)
        
        with patch('builtins.print') as mock_print:
            reporter.start(2, "test operation")
            reporter.step("step 1")
            reporter.complete("done")
            
            # Only complete message should be printed in non-verbose mode
            mock_print.assert_called_once_with("done")


class TestSpecOpsCLI(unittest.TestCase):
    """Test SpecOps CLI functionality."""
    
    def setUp(self):
        self.cli = SpecOpsCLI()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        # Cleanup temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_parser(self):
        """Test argument parser creation."""
        parser = self.cli.create_parser()
        
        # Test basic parsing
        args = parser.parse_args(['analyze'])
        self.assertEqual(args.command, 'analyze')
        
        # Test with options
        args = parser.parse_args(['--verbose', '--workspace', '/tmp', 'status'])
        self.assertTrue(args.verbose)
        self.assertEqual(args.workspace, '/tmp')
        self.assertEqual(args.command, 'status')
    
    def test_generate_command_parsing(self):
        """Test generate command argument parsing."""
        parser = self.cli.create_parser()
        
        # Test --all flag
        args = parser.parse_args(['generate', '--all'])
        self.assertTrue(args.all)
        
        # Test specific document flags
        args = parser.parse_args(['generate', '--tasks'])
        self.assertTrue(args.tasks)
        
        args = parser.parse_args(['generate', '--faq'])
        self.assertTrue(args.faq)
        
        args = parser.parse_args(['generate', '--quick-start'])
        self.assertTrue(args.quick_start)
    
    def test_hooks_command_parsing(self):
        """Test hooks command argument parsing."""
        parser = self.cli.create_parser()
        
        # Test register flag
        args = parser.parse_args(['hooks', '--register'])
        self.assertTrue(args.register)
        
        # Test status flag
        args = parser.parse_args(['hooks', '--status'])
        self.assertTrue(args.status)
        
        # Test manual triggers
        args = parser.parse_args(['hooks', '--feature-created', 'path/to/feature.py'])
        self.assertEqual(args.feature_created, 'path/to/feature.py')
        
        args = parser.parse_args(['hooks', '--readme-saved', 'README.md'])
        self.assertEqual(args.readme_saved, 'README.md')
    
    @patch('src.cli.create_app')
    def test_initialize_app(self, mock_create_app):
        """Test application initialization."""
        mock_app = Mock()
        mock_create_app.return_value = mock_app
        
        # Test basic initialization
        self.cli.initialize_app(str(self.temp_path))
        
        mock_create_app.assert_called_once()
        self.assertEqual(self.cli.app, mock_app)
    
    @patch('src.cli.create_app')
    def test_initialize_app_with_config(self, mock_create_app):
        """Test application initialization with config file."""
        mock_app = Mock()
        mock_create_app.return_value = mock_app
        
        # Create a mock config file
        config_file = self.temp_path / 'config.json'
        config_data = {
            'ai_model': 'gpt-4',
            'debug_mode': True
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        with patch('src.cli.ConfigLoader') as mock_config_loader:
            mock_loader = Mock()
            mock_config = Mock()
            mock_loader.load_from_file.return_value = mock_config
            mock_config_loader.return_value = mock_loader
            
            self.cli.initialize_app(str(self.temp_path), str(config_file))
            
            mock_create_app.assert_called_once()
            mock_loader.load_from_file.assert_called_once_with(str(config_file))
    
    def test_cmd_analyze_without_app(self):
        """Test analyze command without initialized app."""
        args = Mock()
        args.output = None
        
        result = self.cli.cmd_analyze(args)
        self.assertEqual(result, 1)
    
    @patch('src.cli.create_app')
    def test_cmd_analyze_with_output(self, mock_create_app):
        """Test analyze command with output file."""
        # Setup mock app
        mock_app = Mock()
        mock_analysis = RepositoryAnalysis()
        mock_app.analyze_repository.return_value = mock_analysis
        mock_create_app.return_value = mock_app
        
        self.cli.initialize_app(str(self.temp_path))
        
        # Setup args
        args = Mock()
        output_file = self.temp_path / 'analysis.json'
        args.output = str(output_file)
        
        # Run command
        result = self.cli.cmd_analyze(args)
        
        # Verify success
        self.assertEqual(result, 0)
        mock_app.analyze_repository.assert_called_once()
        
        # Verify output file was created
        self.assertTrue(output_file.exists())
        
        # Verify JSON content
        with open(output_file) as f:
            data = json.load(f)
            self.assertIn('concepts', data)
            self.assertIn('setup_steps', data)
            self.assertIn('code_examples', data)
            self.assertIn('dependencies', data)
    
    @patch('src.cli.create_app')
    def test_cmd_generate_all(self, mock_create_app):
        """Test generate command with --all flag."""
        # Setup mock app
        mock_app = Mock()
        mock_app.generate_all_documents.return_value = {
            'tasks': 'tasks.md',
            'faq': 'faq.md',
            'quick_start': 'README.md'
        }
        mock_create_app.return_value = mock_app
        
        self.cli.initialize_app(str(self.temp_path))
        
        # Setup args
        args = Mock()
        args.all = True
        args.tasks = False
        args.faq = False
        args.quick_start = False
        args.analysis_file = None
        
        # Run command
        result = self.cli.cmd_generate(args)
        
        # Verify success
        self.assertEqual(result, 0)
        mock_app.generate_all_documents.assert_called_once()
    
    @patch('src.cli.create_app')
    def test_cmd_hooks_register(self, mock_create_app):
        """Test hooks register command."""
        # Setup mock app
        mock_app = Mock()
        mock_create_app.return_value = mock_app
        
        self.cli.initialize_app(str(self.temp_path))
        
        # Setup args
        args = Mock()
        args.register = True
        args.status = False
        args.feature_created = None
        args.readme_saved = None
        
        # Run command
        result = self.cli.cmd_hooks(args)
        
        # Verify success
        self.assertEqual(result, 0)
        mock_app.register_hooks.assert_called_once()
    
    @patch('src.cli.create_app')
    def test_cmd_status(self, mock_create_app):
        """Test status command."""
        # Setup mock app
        mock_app = Mock()
        mock_status = {
            'workspace_path': str(self.temp_path),
            'config': {
                'ai_model': 'gpt-3.5-turbo',
                'debug_mode': False,
                'hooks_enabled': {
                    'feature_created': True,
                    'readme_save': True
                }
            },
            'components': {
                'content_analyzer': True,
                'ai_engine': True,
                'task_generator': True,
                'faq_generator': True,
                'quick_start_generator': True,
                'hook_manager': True
            }
        }
        mock_app.get_status.return_value = mock_status
        mock_create_app.return_value = mock_app
        
        self.cli.initialize_app(str(self.temp_path))
        
        # Setup args
        args = Mock()
        args.json = False
        
        # Run command
        with patch('builtins.print') as mock_print:
            result = self.cli.cmd_status(args)
        
        # Verify success
        self.assertEqual(result, 0)
        mock_app.get_status.assert_called_once()
        
        # Verify output was printed
        self.assertTrue(mock_print.called)
    
    @patch('src.cli.create_app')
    def test_cmd_status_json(self, mock_create_app):
        """Test status command with JSON output."""
        # Setup mock app
        mock_app = Mock()
        mock_status = {'test': 'data'}
        mock_app.get_status.return_value = mock_status
        mock_create_app.return_value = mock_app
        
        self.cli.initialize_app(str(self.temp_path))
        
        # Setup args
        args = Mock()
        args.json = True
        
        # Run command
        with patch('builtins.print') as mock_print:
            result = self.cli.cmd_status(args)
        
        # Verify success
        self.assertEqual(result, 0)
        
        # Verify JSON output
        mock_print.assert_called_once_with(json.dumps(mock_status, indent=2))
    
    def test_run_no_command(self):
        """Test running CLI without a command."""
        with patch('argparse.ArgumentParser.print_help') as mock_help:
            result = self.cli.run([])
            
            self.assertEqual(result, 1)
            mock_help.assert_called_once()
    
    @patch('src.cli.create_app')
    def test_run_with_command(self, mock_create_app):
        """Test running CLI with a valid command."""
        mock_app = Mock()
        mock_app.get_status.return_value = {
            'workspace_path': '.',
            'config': {
                'ai_model': 'gpt-3.5-turbo',
                'debug_mode': False,
                'hooks_enabled': {
                    'feature_created': True,
                    'readme_save': True
                }
            },
            'components': {
                'content_analyzer': True,
                'ai_engine': True,
                'task_generator': True,
                'faq_generator': True,
                'quick_start_generator': True,
                'hook_manager': True
            }
        }
        mock_app.shutdown = Mock()  # Add shutdown method
        mock_create_app.return_value = mock_app
        
        with patch('builtins.print'):
            result = self.cli.run(['status'])
        
        self.assertEqual(result, 0)
    
    def test_run_keyboard_interrupt(self):
        """Test handling of keyboard interrupt."""
        with patch.object(self.cli, 'cmd_status', side_effect=KeyboardInterrupt):
            with patch.object(self.cli, 'initialize_app'):
                result = self.cli.run(['status'])
        
        self.assertEqual(result, 130)
    
    @patch('src.cli.create_app')
    def test_run_unexpected_error(self, mock_create_app):
        """Test handling of unexpected errors."""
        mock_create_app.side_effect = Exception("Test error")
        
        result = self.cli.run(['status'])
        self.assertEqual(result, 1)


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create a minimal workspace structure
        (self.temp_path / 'README.md').write_text('# Test Project\n\nThis is a test.')
        (self.temp_path / 'src').mkdir()
        (self.temp_path / 'src' / '__init__.py').write_text('')
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_help_output(self):
        """Test that help output is generated correctly."""
        cli = SpecOpsCLI()
        parser = cli.create_parser()
        
        # This should not raise an exception
        help_text = parser.format_help()
        self.assertIn('SpecOps', help_text)
        self.assertIn('analyze', help_text)
        self.assertIn('generate', help_text)
        self.assertIn('hooks', help_text)
        self.assertIn('status', help_text)


if __name__ == '__main__':
    unittest.main()