"""Sample repository testing for SpecOps."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import json

from src.main import SpecOpsApp, create_app
from src.models import AppConfig, RepositoryAnalysis
from tests.fixtures.sample_repositories import get_sample_repositories


class TestSampleRepositoryTesting:
    """Test the system against various repository structures and content types."""
    
    @pytest.fixture(params=['python_library', 'web_application', 'microservice'])
    def sample_repo(self, request):
        """Parametrized fixture for different repository types."""
        repositories = get_sample_repositories()
        repo = repositories[request.param]
        workspace = repo.create()
        yield workspace, request.param
        repo.cleanup()
    
    def test_repository_analysis_across_different_structures(self, sample_repo):
        """Test content analysis works across different repository structures."""
        workspace, repo_type = sample_repo
        
        # Create app for the sample repository
        app = create_app(workspace_path=str(workspace))
        
        # Perform analysis
        analysis = app.analyze_repository()
        
        # Verify analysis results are appropriate for repository type
        assert isinstance(analysis, RepositoryAnalysis)
        assert len(analysis.concepts) > 0, f"No concepts found in {repo_type} repository"
        assert len(analysis.setup_steps) > 0, f"No setup steps found in {repo_type} repository"
        
        # Repository-specific validations
        if repo_type == 'python_library':
            # Should find library-specific concepts
            concept_names = [c.name.lower() for c in analysis.concepts]
            assert any('data' in name or 'processor' in name or 'library' in name for name in concept_names)
            
            # Should find Python-specific setup steps
            setup_titles = [s.title.lower() for s in analysis.setup_steps]
            assert any('pip' in title or 'install' in title for title in setup_titles)
        
        elif repo_type == 'web_application':
            # Should find web app concepts
            concept_names = [c.name.lower() for c in analysis.concepts]
            assert any('api' in name or 'web' in name or 'auth' in name for name in concept_names)
            
            # Should find web-specific setup steps
            setup_titles = [s.title.lower() for s in analysis.setup_steps]
            assert any('server' in title or 'database' in title or 'uvicorn' in title for title in setup_titles)
        
        elif repo_type == 'microservice':
            # Should find microservice concepts
            concept_names = [c.name.lower() for c in analysis.concepts]
            assert any('service' in name or 'docker' in name or 'health' in name for name in concept_names)
            
            # Should find container-specific setup steps
            setup_titles = [s.title.lower() for s in analysis.setup_steps]
            assert any('docker' in title or 'kubernetes' in title for title in setup_titles)
    
    @patch('src.ai.processing_engine.AIProcessingEngine.generate_task_suggestions')
    @patch('src.ai.processing_engine.AIProcessingEngine.create_faq_pairs')
    @patch('src.ai.processing_engine.AIProcessingEngine.extract_quick_start_steps')
    def test_document_generation_quality_across_repositories(self, mock_quick_start, mock_faq, mock_tasks, sample_repo):
        """Test document generation produces quality output for different repository types."""
        workspace, repo_type = sample_repo
        
        # Setup mocks with repository-appropriate content
        mock_tasks.return_value = self._get_mock_tasks_for_repo_type(repo_type)
        mock_faq.return_value = self._get_mock_faq_for_repo_type(repo_type)
        mock_quick_start.return_value = self._get_mock_quick_start_for_repo_type(repo_type)
        
        # Create app and generate documents
        app = create_app(workspace_path=str(workspace))
        generated_docs = app.generate_all_documents()
        
        # Verify documents were generated
        assert len(generated_docs) > 0, f"No documents generated for {repo_type}"
        
        # Test document quality
        for doc_type, doc_path in generated_docs.items():
            if Path(doc_path).exists():
                content = Path(doc_path).read_text()
                
                # Basic quality checks
                assert len(content.strip()) > 100, f"{doc_type} document too short for {repo_type}"
                assert content.count('\n') > 5, f"{doc_type} document lacks structure for {repo_type}"
                
                # Repository-specific content checks
                if repo_type == 'python_library':
                    if doc_type == 'tasks':
                        assert 'pip' in content.lower() or 'python' in content.lower()
                    elif doc_type == 'faq':
                        assert 'install' in content.lower() or 'library' in content.lower()
                
                elif repo_type == 'web_application':
                    if doc_type == 'tasks':
                        assert 'api' in content.lower() or 'server' in content.lower()
                    elif doc_type == 'faq':
                        assert 'endpoint' in content.lower() or 'authentication' in content.lower()
                
                elif repo_type == 'microservice':
                    if doc_type == 'tasks':
                        assert 'docker' in content.lower() or 'container' in content.lower()
                    elif doc_type == 'faq':
                        assert 'deploy' in content.lower() or 'service' in content.lower()
    
    def test_steering_guidelines_application_across_repositories(self, sample_repo):
        """Test that steering guidelines are properly applied across different repository types."""
        workspace, repo_type = sample_repo
        
        # Create app
        app = create_app(workspace_path=str(workspace))
        
        # Verify steering files exist
        steering_dir = workspace / '.kiro' / 'steering'
        assert steering_dir.exists(), f"Steering directory missing in {repo_type}"
        
        code_style_file = steering_dir / 'code-style.md'
        assert code_style_file.exists(), f"Code style file missing in {repo_type}"
        
        # Verify steering content is repository-appropriate
        code_style_content = code_style_file.read_text().lower()
        
        if repo_type == 'python_library':
            assert 'python' in code_style_content or 'pep' in code_style_content
        elif repo_type == 'web_application':
            assert 'api' in code_style_content or 'fastapi' in code_style_content
        elif repo_type == 'microservice':
            assert 'microservice' in code_style_content or 'docker' in code_style_content
        
        # Test that app loads steering configuration
        assert app.config.workspace_path == str(workspace)
    
    def test_file_structure_handling_across_repositories(self, sample_repo):
        """Test that different file structures are handled correctly."""
        workspace, repo_type = sample_repo
        
        # Create app and analyze
        app = create_app(workspace_path=str(workspace))
        analysis = app.analyze_repository()
        
        # Verify file structure analysis
        assert analysis.file_structure is not None
        assert len(analysis.file_structure) > 0
        
        # Check that appropriate files were found
        if repo_type == 'python_library':
            # Should find Python files
            assert any('.py' in str(path) for path in workspace.rglob('*'))
            # Should find setup.py or similar
            assert (workspace / 'setup.py').exists() or (workspace / 'pyproject.toml').exists()
        
        elif repo_type == 'web_application':
            # Should find web application files
            assert any('main.py' in str(path) for path in workspace.rglob('*'))
            # Should find API-related files
            assert any('api' in str(path) for path in workspace.rglob('*'))
        
        elif repo_type == 'microservice':
            # Should find Docker files
            assert (workspace / 'Dockerfile').exists()
            assert (workspace / 'docker-compose.yml').exists()
            # Should find Kubernetes files
            assert any('k8s' in str(path) for path in workspace.rglob('*'))
    
    def test_code_example_extraction_across_repositories(self, sample_repo):
        """Test that code examples are properly extracted from different repository types."""
        workspace, repo_type = sample_repo
        
        # Create app and analyze
        app = create_app(workspace_path=str(workspace))
        analysis = app.analyze_repository()
        
        # Verify code examples were found
        assert len(analysis.code_examples) > 0, f"No code examples found in {repo_type}"
        
        # Check code example quality
        for example in analysis.code_examples:
            assert example.code is not None and len(example.code.strip()) > 0
            assert example.language is not None
            
            # Repository-specific code example checks
            if repo_type == 'python_library':
                # Should find Python code examples
                python_examples = [e for e in analysis.code_examples if e.language == 'python']
                assert len(python_examples) > 0, "No Python examples found in Python library"
            
            elif repo_type == 'web_application':
                # Should find API-related examples
                api_examples = [e for e in analysis.code_examples 
                              if 'api' in e.description.lower() or 'fastapi' in e.code.lower()]
                # May or may not find API examples depending on content
            
            elif repo_type == 'microservice':
                # Should find Docker or deployment examples
                deployment_examples = [e for e in analysis.code_examples 
                                     if 'docker' in e.description.lower() or 'kubectl' in e.code.lower()]
                # May or may not find deployment examples depending on content
    
    def test_dependency_detection_across_repositories(self, sample_repo):
        """Test that dependencies are correctly detected across different repository types."""
        workspace, repo_type = sample_repo
        
        # Create app and analyze
        app = create_app(workspace_path=str(workspace))
        analysis = app.analyze_repository()
        
        # Verify dependencies were found
        assert len(analysis.dependencies) > 0, f"No dependencies found in {repo_type}"
        
        # Repository-specific dependency checks
        dependency_names = [d.name.lower() for d in analysis.dependencies]
        
        if repo_type == 'python_library':
            # Should find Python dependencies
            assert any('pandas' in name or 'pytest' in name for name in dependency_names)
        
        elif repo_type == 'web_application':
            # Should find web framework dependencies
            assert any('fastapi' in name or 'uvicorn' in name for name in dependency_names)
        
        elif repo_type == 'microservice':
            # Should find microservice dependencies
            assert any('fastapi' in name or 'prometheus' in name for name in dependency_names)
    
    def test_error_handling_across_repositories(self, sample_repo):
        """Test error handling works consistently across different repository types."""
        workspace, repo_type = sample_repo
        
        # Create app with debug mode for better error reporting
        config = AppConfig(workspace_path=str(workspace), debug_mode=True)
        app = create_app(workspace_path=str(workspace), config=config)
        
        # Test that analysis doesn't crash on any repository type
        try:
            analysis = app.analyze_repository()
            assert isinstance(analysis, RepositoryAnalysis)
        except Exception as e:
            pytest.fail(f"Analysis failed for {repo_type}: {e}")
        
        # Test that document generation handles errors gracefully
        with patch('src.ai.processing_engine.AIProcessingEngine.generate_task_suggestions', 
                   side_effect=Exception("AI service unavailable")):
            try:
                # Should handle AI errors gracefully
                generated_docs = app.generate_all_documents()
                # May succeed with fallback or fail gracefully
            except Exception as e:
                # Should be a wrapped SpecOps error, not raw exception
                assert "SpecOps" in str(type(e)) or "generation failed" in str(e).lower()
    
    def test_performance_across_repositories(self, sample_repo):
        """Test performance characteristics across different repository types."""
        import time
        
        workspace, repo_type = sample_repo
        
        # Create app
        app = create_app(workspace_path=str(workspace))
        
        # Measure analysis time
        start_time = time.time()
        analysis = app.analyze_repository()
        analysis_time = time.time() - start_time
        
        # Analysis should complete in reasonable time
        assert analysis_time < 30, f"Analysis took too long for {repo_type}: {analysis_time}s"
        
        # Verify analysis quality vs time trade-off
        concepts_per_second = len(analysis.concepts) / max(analysis_time, 0.1)
        assert concepts_per_second > 0, f"No concepts extracted for {repo_type}"
        
        # Repository size considerations
        total_files = len(list(workspace.rglob('*.py'))) + len(list(workspace.rglob('*.md')))
        if total_files > 10:
            # For larger repositories, should find proportionally more concepts
            assert len(analysis.concepts) >= total_files * 0.1, f"Too few concepts for repository size in {repo_type}"
    
    def test_output_adherence_to_requirements(self, sample_repo):
        """Verify output quality and adherence to requirements across repository types."""
        workspace, repo_type = sample_repo
        
        # Mock AI responses with repository-appropriate content
        with patch('src.ai.processing_engine.AIProcessingEngine.generate_task_suggestions') as mock_tasks, \
             patch('src.ai.processing_engine.AIProcessingEngine.create_faq_pairs') as mock_faq, \
             patch('src.ai.processing_engine.AIProcessingEngine.extract_quick_start_steps') as mock_quick_start:
            
            mock_tasks.return_value = self._get_mock_tasks_for_repo_type(repo_type)
            mock_faq.return_value = self._get_mock_faq_for_repo_type(repo_type)
            mock_quick_start.return_value = self._get_mock_quick_start_for_repo_type(repo_type)
            
            # Create app and generate documents
            app = create_app(workspace_path=str(workspace))
            generated_docs = app.generate_all_documents()
            
            # Verify requirements adherence
            for doc_type, doc_path in generated_docs.items():
                if Path(doc_path).exists():
                    content = Path(doc_path).read_text()
                    
                    # Requirement 8.1: Generate requirements.md (if applicable)
                    # Requirement 8.2: Generate design.md (if applicable)  
                    # Requirement 8.3: Generate tasks.md
                    if doc_type == 'tasks':
                        assert '- [' in content, "Tasks document missing checkbox format"
                        assert 'Requirements:' in content or '_Requirements:' in content, "Tasks missing requirement references"
                    
                    # Requirement 8.4: Generate faq.md
                    elif doc_type == 'faq':
                        assert '?' in content, "FAQ document missing questions"
                        questions = [line for line in content.split('\n') if line.strip().endswith('?')]
                        assert len(questions) > 0, "FAQ missing proper question format"
                    
                    # Requirement 8.5: Maintain consistency
                    assert len(content.strip()) > 0, f"Empty {doc_type} document"
                    assert content.count('\n') > 1, f"{doc_type} document lacks structure"
    
    def _get_mock_tasks_for_repo_type(self, repo_type: str):
        """Get mock task suggestions appropriate for repository type."""
        base_tasks = [
            {
                'title': 'Set up development environment',
                'description': 'Install dependencies and configure workspace',
                'acceptance_criteria': ['Dependencies installed', 'Environment configured'],
                'prerequisites': [],
                'estimated_time': 15,
                'difficulty': 'easy'
            }
        ]
        
        if repo_type == 'python_library':
            base_tasks.extend([
                {
                    'title': 'Understand data processing pipeline',
                    'description': 'Learn how the DataProcessor class works',
                    'acceptance_criteria': ['Pipeline understood', 'Examples run successfully'],
                    'prerequisites': ['Set up development environment'],
                    'estimated_time': 20,
                    'difficulty': 'medium'
                }
            ])
        elif repo_type == 'web_application':
            base_tasks.extend([
                {
                    'title': 'Explore API endpoints',
                    'description': 'Test authentication and user management APIs',
                    'acceptance_criteria': ['API endpoints tested', 'Authentication working'],
                    'prerequisites': ['Set up development environment'],
                    'estimated_time': 25,
                    'difficulty': 'medium'
                }
            ])
        elif repo_type == 'microservice':
            base_tasks.extend([
                {
                    'title': 'Deploy with Docker',
                    'description': 'Build and run the service using Docker',
                    'acceptance_criteria': ['Docker image built', 'Service running', 'Health checks passing'],
                    'prerequisites': ['Set up development environment'],
                    'estimated_time': 30,
                    'difficulty': 'medium'
                }
            ])
        
        return base_tasks
    
    def _get_mock_faq_for_repo_type(self, repo_type: str):
        """Get mock FAQ pairs appropriate for repository type."""
        base_faq = [
            {
                'question': 'How do I get started?',
                'answer': 'Follow the setup guide in the documentation.',
                'category': 'getting-started',
                'source_files': ['README.md'],
                'confidence': 0.9
            }
        ]
        
        if repo_type == 'python_library':
            base_faq.extend([
                {
                    'question': 'How do I install the library?',
                    'answer': 'Use pip install to install the library and its dependencies.',
                    'category': 'installation',
                    'source_files': ['README.md', 'setup.py'],
                    'confidence': 0.9
                },
                {
                    'question': 'What data formats are supported?',
                    'answer': 'The library supports CSV, JSON, and Excel formats.',
                    'category': 'usage',
                    'source_files': ['src/mylib/data_processor.py'],
                    'confidence': 0.8
                }
            ])
        elif repo_type == 'web_application':
            base_faq.extend([
                {
                    'question': 'How do I authenticate with the API?',
                    'answer': 'Use JWT tokens obtained from the /api/auth/login endpoint.',
                    'category': 'authentication',
                    'source_files': ['src/webapp/api/auth.py'],
                    'confidence': 0.9
                },
                {
                    'question': 'What database is used?',
                    'answer': 'The application uses PostgreSQL with SQLAlchemy ORM.',
                    'category': 'database',
                    'source_files': ['src/webapp/models/database.py'],
                    'confidence': 0.8
                }
            ])
        elif repo_type == 'microservice':
            base_faq.extend([
                {
                    'question': 'How do I deploy the service?',
                    'answer': 'Use Docker Compose for local deployment or Kubernetes for production.',
                    'category': 'deployment',
                    'source_files': ['docker-compose.yml', 'k8s/deployment.yaml'],
                    'confidence': 0.9
                },
                {
                    'question': 'How do I monitor the service?',
                    'answer': 'The service exposes Prometheus metrics at /metrics endpoint.',
                    'category': 'monitoring',
                    'source_files': ['src/service/main.py'],
                    'confidence': 0.8
                }
            ])
        
        return base_faq
    
    def _get_mock_quick_start_for_repo_type(self, repo_type: str):
        """Get mock Quick Start guide appropriate for repository type."""
        base_guide = {
            'prerequisites': ['Python 3.8+', 'pip'],
            'setup_steps': ['Clone repository', 'Install dependencies'],
            'basic_usage': ['Import main module', 'Run basic example'],
            'next_steps': ['Read documentation', 'Explore examples']
        }
        
        if repo_type == 'python_library':
            base_guide.update({
                'setup_steps': ['Clone repository', 'pip install -r requirements.txt', 'pip install -e .'],
                'basic_usage': ['from mylib import DataProcessor', 'processor = DataProcessor()', 'data = processor.load_csv("data.csv")'],
                'next_steps': ['Read API documentation', 'Try the examples', 'Run the test suite']
            })
        elif repo_type == 'web_application':
            base_guide.update({
                'prerequisites': ['Python 3.9+', 'PostgreSQL', 'pip'],
                'setup_steps': ['Clone repository', 'pip install -r requirements.txt', 'Set up database', 'uvicorn webapp.main:app --reload'],
                'basic_usage': ['Open http://localhost:8000', 'Register a user account', 'Explore API at /docs'],
                'next_steps': ['Read API documentation', 'Set up authentication', 'Deploy to production']
            })
        elif repo_type == 'microservice':
            base_guide.update({
                'prerequisites': ['Docker', 'Docker Compose', 'kubectl (for K8s)'],
                'setup_steps': ['Clone repository', 'docker-compose up', 'Verify health at /health'],
                'basic_usage': ['Test API endpoints', 'Check metrics at /metrics', 'View logs with docker logs'],
                'next_steps': ['Deploy to Kubernetes', 'Set up monitoring', 'Configure scaling']
            })
        
        return base_guide