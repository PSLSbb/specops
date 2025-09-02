// SpecOps Web Interface JavaScript

// Global state
let currentAnalysis = null;
let generatedContent = {
    tasks: '',
    faq: '',
    quickstart: ''
};

// Utility functions
function scrollToDemo() {
    document.getElementById('demo').scrollIntoView({ behavior: 'smooth' });
}

function setRepo(url) {
    document.getElementById('repoUrl').value = url;
}

function updateProviderOptions() {
    const provider = document.getElementById('aiProvider').value;
    const modelSelect = document.getElementById('aiModel');
    const apiKeySection = document.getElementById('apiKeySection');
    const apiKeyLabel = document.getElementById('apiKeyLabel');
    const providerDescription = document.getElementById('providerDescription');
    
    // Clear existing options
    modelSelect.innerHTML = '';
    
    if (provider === 'mock') {
        // Demo mode
        modelSelect.innerHTML = '<option value="mock-model">Mock Model</option>';
        apiKeySection.classList.add('hidden');
        providerDescription.innerHTML = '🎭 Demo mode uses realistic mock data for testing the interface.';
        providerDescription.className = 'text-sm text-gray-600 bg-blue-50 p-3 rounded-lg';
    } else {
        // Real provider
        const providerInfo = AI_PROVIDERS[provider];
        
        // Populate models
        providerInfo.models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            modelSelect.appendChild(option);
        });
        
        // Show API key section
        apiKeySection.classList.remove('hidden');
        apiKeyLabel.textContent = providerInfo.keyLabel;
        
        // Update description
        providerDescription.innerHTML = `${providerInfo.name}: ${providerInfo.description}`;
        providerDescription.className = 'text-sm text-gray-600 bg-green-50 p-3 rounded-lg';
        
        // Load saved API key
        const savedKey = localStorage.getItem(`${provider}_api_key`);
        if (savedKey) {
            document.getElementById('apiKey').value = savedKey;
        }
    }
}

function saveApiKey() {
    const provider = document.getElementById('aiProvider').value;
    const apiKey = document.getElementById('apiKey').value;
    
    if (provider !== 'mock' && apiKey) {
        localStorage.setItem(`${provider}_api_key`, apiKey);
    }
}

// Initialize provider options on page load
document.addEventListener('DOMContentLoaded', function() {
    updateProviderOptions();
});

function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    // Remove active state from all tabs
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('border-blue-500', 'text-blue-600');
        button.classList.add('border-transparent', 'text-gray-500');
    });
    
    // Show selected tab content
    document.getElementById(tabName + 'Content').classList.remove('hidden');
    
    // Add active state to selected tab
    const activeTab = document.getElementById(tabName + 'Tab');
    activeTab.classList.remove('border-transparent', 'text-gray-500');
    activeTab.classList.add('border-blue-500', 'text-blue-600');
}

function downloadContent(type) {
    const content = generatedContent[type];
    if (!content) return;
    
    const filename = `${type}.md`;
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Mock analysis function (since we can't run Python in browser)
async function analyzeRepository() {
    const repoUrl = document.getElementById('repoUrl').value.trim();
    
    if (!repoUrl) {
        alert('Please enter a repository URL');
        return;
    }
    
    if (!isValidGitHubUrl(repoUrl)) {
        alert('Please enter a valid GitHub repository URL');
        return;
    }
    
    // Show loading state
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('analyzeBtn').disabled = true;
    
    try {
        // Extract repo info from URL
        const repoInfo = extractRepoInfo(repoUrl);
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Get AI configuration
        const aiProvider = document.getElementById('aiProvider').value;
        const aiModel = document.getElementById('aiModel').value;
        const aiKey = document.getElementById('apiKey').value;
        
        // Save API key if provided
        if (aiProvider !== 'mock' && aiKey) {
            saveApiKey();
        }
        
        // Analyze repository (use real API or mock data)
        const useMock = USE_MOCK_DATA || aiProvider === 'mock';
        const analysis = useMock ? 
            await mockAnalyzeRepo(repoInfo) : 
            await analyzeRepoAPI(repoInfo, { provider: aiProvider, model: aiModel, apiKey: aiKey });
        
        // Generate documents (use real API or mock data)
        const documents = useMock ? 
            await mockGenerateDocuments(analysis) : 
            await generateDocumentsAPI(repoInfo, analysis, { provider: aiProvider, model: aiModel, apiKey: aiKey });
        
        // Display results
        displayResults(analysis, documents);
        
    } catch (error) {
        console.error('Analysis failed:', error);
        alert('Analysis failed. Please try again or check the repository URL.');
    } finally {
        document.getElementById('loadingState').classList.add('hidden');
        document.getElementById('analyzeBtn').disabled = false;
    }
}

function isValidGitHubUrl(url) {
    const githubPattern = /^https:\/\/github\.com\/[\w\-\.]+\/[\w\-\.]+\/?$/;
    return githubPattern.test(url);
}

function extractRepoInfo(url) {
    const match = url.match(/github\.com\/([^\/]+)\/([^\/]+)/);
    if (match) {
        return {
            owner: match[1],
            repo: match[2].replace('.git', ''),
            url: url
        };
    }
    throw new Error('Invalid GitHub URL');
}

// Configuration
const API_BASE_URL = 'https://api.specops.dev'; // Replace with your actual API URL
const USE_MOCK_DATA = true; // Set to false when you have a real API deployed

// AI Provider configurations
const AI_PROVIDERS = {
    openai: {
        name: 'OpenAI ChatGPT',
        models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
        description: 'Industry standard for AI applications',
        keyLabel: 'OpenAI API Key'
    },
    anthropic: {
        name: 'Anthropic Claude',
        models: ['claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022', 'claude-3-opus-20240229'],
        description: 'Strong reasoning, multilingual, ethical AI',
        keyLabel: 'Anthropic API Key'
    },
    google: {
        name: 'Google AI Studio',
        models: ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro'],
        description: 'No billing surprises, great for prototyping',
        keyLabel: 'Google AI API Key'
    },
    openrouter: {
        name: 'OpenRouter',
        models: ['deepseek/deepseek-chat', 'qwen/qwen-2.5-72b-instruct', 'meta-llama/llama-3.1-70b-instruct'],
        description: '50+ models, one key, easy model switching',
        keyLabel: 'OpenRouter API Key'
    },
    groq: {
        name: 'Groq',
        models: ['llama-3.1-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768'],
        description: 'Fast inference, ideal for real-time apps',
        keyLabel: 'Groq API Key'
    }
};

// Real API functions
async function analyzeRepoAPI(repoInfo, aiConfig = {}) {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            repo_url: repoInfo.url,
            ai_config: aiConfig
        })
    });
    
    if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (data.status === 'error') {
        throw new Error(data.error);
    }
    
    return {
        concepts: data.analysis.concepts,
        setupSteps: data.analysis.setup_steps,
        codeExamples: data.analysis.code_examples,
        dependencies: data.analysis.dependencies,
        description: `Repository: ${repoInfo.owner}/${repoInfo.repo}`
    };
}

// Mock functions (for demo when API is not available)
async function mockAnalyzeRepo(repoInfo) {
    const mockData = {
        'facebook/react': {
            concepts: 15,
            setupSteps: 8,
            codeExamples: 25,
            dependencies: 12,
            description: 'A JavaScript library for building user interfaces'
        },
        'microsoft/vscode': {
            concepts: 22,
            setupSteps: 12,
            codeExamples: 18,
            dependencies: 8,
            description: 'Visual Studio Code - Open Source'
        },
        'python/cpython': {
            concepts: 18,
            setupSteps: 15,
            codeExamples: 30,
            dependencies: 6,
            description: 'The Python programming language'
        },
        'tensorflow/tensorflow': {
            concepts: 25,
            setupSteps: 20,
            codeExamples: 40,
            dependencies: 15,
            description: 'An Open Source Machine Learning Framework for Everyone'
        }
    };
    
    const repoKey = `${repoInfo.owner}/${repoInfo.repo}`;
    return mockData[repoKey] || {
        concepts: Math.floor(Math.random() * 20) + 5,
        setupSteps: Math.floor(Math.random() * 15) + 5,
        codeExamples: Math.floor(Math.random() * 30) + 10,
        dependencies: Math.floor(Math.random() * 10) + 3,
        description: `Repository: ${repoKey}`
    };
}

// Real API document generation
async function generateDocumentsAPI(repoInfo, analysis, aiConfig = {}) {
    const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            repo_url: repoInfo.url,
            analysis: analysis,
            ai_config: aiConfig
        })
    });
    
    if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (data.status === 'error') {
        throw new Error(data.error);
    }
    
    return data.documents;
}

async function mockGenerateDocuments(analysis) {
    // Mock document generation
    const repoName = analysis.description.split(':')[1] || 'Repository';
    
    const tasks = `# Onboarding Tasks

## Task 1: Set up development environment

**Description:** Install required dependencies and configure the development environment for ${repoName}.

**Prerequisites:**
- Git installed
- Node.js (if applicable)
- Code editor (VS Code recommended)

**Acceptance Criteria:**
- [ ] Repository cloned locally
- [ ] Dependencies installed successfully
- [ ] Development server runs without errors
- [ ] Basic tests pass

**Estimated Time:** 30 minutes
**Difficulty:** beginner

---

## Task 2: Understand project structure

**Description:** Explore the codebase and understand the main components and architecture.

**Prerequisites:**
- Development environment set up
- Basic familiarity with the technology stack

**Acceptance Criteria:**
- [ ] Main directories and their purposes identified
- [ ] Key configuration files understood
- [ ] Entry points and main modules located
- [ ] Documentation read and understood

**Estimated Time:** 45 minutes
**Difficulty:** intermediate

---

## Task 3: Make your first contribution

**Description:** Make a small, meaningful contribution to the project to understand the development workflow.

**Prerequisites:**
- Project structure understood
- Development environment working
- Contributing guidelines read

**Acceptance Criteria:**
- [ ] Issue or improvement identified
- [ ] Changes implemented following project conventions
- [ ] Tests added or updated as needed
- [ ] Pull request created with proper description

**Estimated Time:** 60 minutes
**Difficulty:** intermediate`;

    const faq = `# Frequently Asked Questions

## Getting Started

### What is ${repoName}?

${analysis.description}. This project provides a comprehensive solution for developers looking to build modern applications.

### How do I get started?

1. Clone the repository
2. Install dependencies
3. Follow the setup instructions in the README
4. Run the development server
5. Start exploring the codebase

### What are the system requirements?

- Operating System: Windows, macOS, or Linux
- Memory: At least 4GB RAM recommended
- Storage: 1GB free space
- Network: Internet connection for downloading dependencies

## Development

### How do I run tests?

Tests can be run using the standard testing framework. Check the package.json or Makefile for specific commands.

### How do I contribute?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### What coding standards should I follow?

Follow the existing code style in the project. Most projects include linting rules and formatting configurations.

## Troubleshooting

### Common setup issues

- **Dependencies not installing**: Try clearing cache and reinstalling
- **Tests failing**: Ensure all dependencies are installed and environment is set up correctly
- **Build errors**: Check that you're using the correct version of required tools

### Where can I get help?

- Check the project's issue tracker
- Read the documentation
- Join the community discussions
- Contact the maintainers`;

    const quickstart = `# Quick Start Guide

## Prerequisites

Before you begin, ensure you have the following installed:
- Git
- Node.js (version 14 or higher)
- npm or yarn package manager

## Installation

1. **Clone the repository**
   \`\`\`bash
   git clone ${analysis.url || 'https://github.com/example/repo.git'}
   cd ${repoName.toLowerCase().replace(/\s+/g, '-')}
   \`\`\`

2. **Install dependencies**
   \`\`\`bash
   npm install
   # or
   yarn install
   \`\`\`

3. **Set up environment**
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your configuration
   \`\`\`

## Running the Application

1. **Start development server**
   \`\`\`bash
   npm start
   # or
   yarn start
   \`\`\`

2. **Open your browser**
   Navigate to \`http://localhost:3000\` (or the port shown in terminal)

## Basic Usage

### Example 1: Basic Setup
\`\`\`javascript
// Basic usage example
import { main } from './${repoName.toLowerCase()}';

const result = main();
console.log(result);
\`\`\`

### Example 2: Configuration
\`\`\`javascript
// Configuration example
const config = {
  option1: 'value1',
  option2: 'value2'
};
\`\`\`

## Next Steps

- Read the full documentation
- Explore the examples directory
- Join the community
- Start building your first feature

## Getting Help

- 📖 [Documentation](./docs)
- 🐛 [Report Issues](./issues)
- 💬 [Discussions](./discussions)
- 🤝 [Contributing](./CONTRIBUTING.md)`;

    return { tasks, faq, quickstart };
}

function displayResults(analysis, documents) {
    // Store generated content
    generatedContent = documents;
    
    // Update analysis summary
    const summary = document.getElementById('analysisSummary');
    summary.innerHTML = `
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
                <div class="text-lg font-semibold">${analysis.concepts}</div>
                <div class="text-xs">Concepts</div>
            </div>
            <div>
                <div class="text-lg font-semibold">${analysis.setupSteps}</div>
                <div class="text-xs">Setup Steps</div>
            </div>
            <div>
                <div class="text-lg font-semibold">${analysis.codeExamples}</div>
                <div class="text-xs">Code Examples</div>
            </div>
            <div>
                <div class="text-lg font-semibold">${analysis.dependencies}</div>
                <div class="text-xs">Dependencies</div>
            </div>
        </div>
    `;
    
    // Update document content
    document.getElementById('tasksMarkdown').textContent = documents.tasks;
    document.getElementById('faqMarkdown').textContent = documents.faq;
    document.getElementById('quickstartMarkdown').textContent = documents.quickstart;
    
    // Show results with animation
    const results = document.getElementById('results');
    results.classList.remove('hidden');
    results.classList.add('fade-in');
    
    // Show first tab by default
    showTab('tasks');
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth' });
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Add enter key support for repository input
    document.getElementById('repoUrl').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeRepository();
        }
    });
    
    console.log('SpecOps Web Interface loaded successfully!');
});