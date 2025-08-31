"""
SpecOps Web API - Flask backend for the web interface
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import tempfile
import shutil
from pathlib import Path
import logging

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from main import create_app as create_specops_app
    from analyzers.online_content_analyzer import OnlineContentAnalyzer
    SPECOPS_AVAILABLE = True
except ImportError as e:
    print(f"SpecOps not available: {e}")
    SPECOPS_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'SpecOps API',
        'version': '1.0.0',
        'specops_available': SPECOPS_AVAILABLE
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_repository():
    """Analyze a repository and return structured data."""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({'error': 'repo_url is required'}), 400
        
        if not SPECOPS_AVAILABLE:
            # Return mock data if SpecOps is not available
            return jsonify(get_mock_analysis(repo_url))
        
        # Validate URL
        if not OnlineContentAnalyzer.is_supported_url(repo_url):
            return jsonify({'error': 'Unsupported repository URL'}), 400
        
        logger.info(f"Analyzing repository: {repo_url}")
        
        # Create SpecOps app and analyze
        specops_app = create_specops_app()
        analysis = specops_app.analyze_repository(repo_url=repo_url)
        
        # Convert analysis to JSON-serializable format
        result = {
            'status': 'success',
            'repo_url': repo_url,
            'analysis': {
                'concepts': len(analysis.concepts),
                'setup_steps': len(analysis.setup_steps),
                'code_examples': len(analysis.code_examples),
                'dependencies': len(analysis.dependencies)
            },
            'concepts': [
                {
                    'name': c.name,
                    'description': c.description,
                    'importance': c.importance,
                    'related_files': c.related_files,
                    'prerequisites': c.prerequisites
                } for c in analysis.concepts[:10]  # Limit to top 10
            ],
            'setup_steps': [
                {
                    'title': s.title,
                    'description': s.description,
                    'commands': s.commands,
                    'prerequisites': s.prerequisites,
                    'order': s.order
                } for s in analysis.setup_steps[:10]  # Limit to top 10
            ],
            'code_examples': [
                {
                    'title': e.title,
                    'language': e.language,
                    'description': e.description,
                    'file_path': e.file_path
                } for e in analysis.code_examples[:5]  # Limit to top 5
            ],
            'dependencies': [
                {
                    'name': d.name,
                    'version': d.version,
                    'type': d.type,
                    'description': d.description
                } for d in analysis.dependencies
            ]
        }
        
        logger.info(f"Analysis complete: {result['analysis']}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/generate', methods=['POST'])
def generate_documents():
    """Generate onboarding documents from analysis data."""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        analysis_data = data.get('analysis')
        
        if not repo_url:
            return jsonify({'error': 'repo_url is required'}), 400
        
        if not SPECOPS_AVAILABLE:
            # Return mock documents if SpecOps is not available
            return jsonify(get_mock_documents(repo_url))
        
        logger.info(f"Generating documents for: {repo_url}")
        
        # Create SpecOps app
        specops_app = create_specops_app()
        
        # If analysis data is provided, use it; otherwise analyze fresh
        if analysis_data:
            # For now, we'll do a fresh analysis
            # In a full implementation, you'd reconstruct the analysis object
            analysis = specops_app.analyze_repository(repo_url=repo_url)
        else:
            analysis = specops_app.analyze_repository(repo_url=repo_url)
        
        # Generate documents
        generated_docs = specops_app.generate_all_documents(analysis)
        
        # Read generated files
        documents = {}
        for doc_type, file_path in generated_docs.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    documents[doc_type] = f.read()
            except Exception as e:
                logger.warning(f"Could not read {doc_type} file: {e}")
                documents[doc_type] = f"# {doc_type.title()}\n\nGeneration failed: {e}"
        
        result = {
            'status': 'success',
            'repo_url': repo_url,
            'documents': documents
        }
        
        logger.info(f"Document generation complete: {list(documents.keys())}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Document generation failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

def get_mock_analysis(repo_url):
    """Return mock analysis data for demo purposes."""
    import re
    
    # Extract repo name from URL
    match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
    if match:
        owner, repo = match.groups()
        repo = repo.replace('.git', '')
    else:
        owner, repo = 'unknown', 'repository'
    
    # Mock data based on popular repositories
    mock_data = {
        'facebook/react': {
            'concepts': 15, 'setup_steps': 8, 'code_examples': 25, 'dependencies': 12,
            'description': 'A JavaScript library for building user interfaces'
        },
        'microsoft/vscode': {
            'concepts': 22, 'setup_steps': 12, 'code_examples': 18, 'dependencies': 8,
            'description': 'Visual Studio Code - Open Source'
        },
        'python/cpython': {
            'concepts': 18, 'setup_steps': 15, 'code_examples': 30, 'dependencies': 6,
            'description': 'The Python programming language'
        }
    }
    
    repo_key = f"{owner}/{repo}"
    base_data = mock_data.get(repo_key, {
        'concepts': 10, 'setup_steps': 6, 'code_examples': 15, 'dependencies': 5,
        'description': f'Repository: {repo_key}'
    })
    
    return {
        'status': 'success',
        'repo_url': repo_url,
        'analysis': base_data,
        'mock': True
    }

def get_mock_documents(repo_url):
    """Return mock documents for demo purposes."""
    import re
    
    # Extract repo name
    match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
    repo_name = match.group(2) if match else 'repository'
    
    tasks = f"""# Onboarding Tasks for {repo_name}

## Task 1: Set up development environment

**Description:** Install required dependencies and configure the development environment.

**Prerequisites:**
- Git installed
- Node.js (if applicable)
- Code editor

**Acceptance Criteria:**
- [ ] Repository cloned locally
- [ ] Dependencies installed successfully
- [ ] Development server runs without errors

**Estimated Time:** 30 minutes
**Difficulty:** beginner

---

## Task 2: Understand project structure

**Description:** Explore the codebase and understand the main components.

**Prerequisites:**
- Development environment set up

**Acceptance Criteria:**
- [ ] Main directories identified
- [ ] Key files understood
- [ ] Documentation read

**Estimated Time:** 45 minutes
**Difficulty:** intermediate"""

    faq = f"""# FAQ for {repo_name}

## Getting Started

### What is {repo_name}?

This is a comprehensive project that provides solutions for modern development needs.

### How do I get started?

1. Clone the repository
2. Install dependencies
3. Follow setup instructions
4. Start developing

### What are the requirements?

- Modern operating system
- Required runtime environment
- Internet connection for dependencies

## Development

### How do I contribute?

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Submit a pull request

### How do I run tests?

Use the standard testing commands provided in the project documentation."""

    quickstart = f"""# Quick Start Guide for {repo_name}

## Prerequisites

- Git
- Node.js or Python (depending on project)
- Code editor

## Installation

1. **Clone the repository**
   ```bash
   git clone {repo_url}
   cd {repo_name}
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   npm start
   # or
   python main.py
   ```

## Next Steps

- Read the documentation
- Explore examples
- Join the community"""

    return {
        'status': 'success',
        'repo_url': repo_url,
        'documents': {
            'tasks': tasks,
            'faq': faq,
            'quickstart': quickstart
        },
        'mock': True
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)