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
const API_BASE_URL = ''; // No API needed for demo mode
const USE_MOCK_DATA = true; // Using mock data for GitHub Pages demo

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
    
    const tasks = `# Onboarding Tasks for ${repoName}

Welcome to the ${repoName} project! These tasks will help you get up and running quickly and understand the codebase.

## Task 1: Environment Setup 🚀

**Description:** Set up your local development environment and get the project running on your machine.

**Prerequisites:**
- Git installed on your system
- Node.js (version 14 or higher) or Python 3.8+
- Code editor (VS Code recommended)
- Terminal/command line access

**Acceptance Criteria:**
- [ ] Repository cloned to your local machine
- [ ] All dependencies installed successfully
- [ ] Development server starts without errors
- [ ] Basic tests pass (if applicable)
- [ ] Environment variables configured

**Estimated Time:** 30-45 minutes
**Difficulty:** beginner

**Helpful Commands:**
\`\`\`bash
git clone ${analysis.url || 'https://github.com/example/repo.git'}
cd ${repoName.toLowerCase().replace(/\s+/g, '-')}
npm install  # or pip install -r requirements.txt
npm start    # or python main.py
\`\`\`

---

## Task 2: Code Exploration 🔍

**Description:** Explore the codebase structure and understand the main components, architecture patterns, and key files.

**Prerequisites:**
- Development environment set up successfully
- Basic familiarity with the technology stack
- Project running locally

**Acceptance Criteria:**
- [ ] Main directories and their purposes identified
- [ ] Key configuration files understood (package.json, config files)
- [ ] Entry points and main modules located
- [ ] Core business logic components identified
- [ ] Documentation and README files reviewed
- [ ] Test structure understood

**Estimated Time:** 45-60 minutes
**Difficulty:** intermediate

**Key Areas to Explore:**
- Main source code directory
- Configuration files
- Test directories
- Documentation
- Build/deployment scripts

---

## Task 3: First Contribution 🎯

**Description:** Make your first meaningful contribution to understand the development workflow and coding standards.

**Prerequisites:**
- Project structure understood
- Development environment working
- Contributing guidelines read
- Issue or improvement area identified

**Acceptance Criteria:**
- [ ] Good first issue identified or small improvement planned
- [ ] Feature branch created following naming conventions
- [ ] Changes implemented following project coding standards
- [ ] Tests added or updated as needed
- [ ] Code reviewed and formatted properly
- [ ] Pull request created with clear description
- [ ] CI/CD checks passing

**Estimated Time:** 1-2 hours
**Difficulty:** intermediate

**Workflow Steps:**
1. Create feature branch: \`git checkout -b feature/your-feature-name\`
2. Make your changes
3. Run tests: \`npm test\` or equivalent
4. Commit changes: \`git commit -m "feat: your descriptive message"\`
5. Push and create PR

---

## Task 4: Advanced Understanding 🧠

**Description:** Dive deeper into advanced concepts and contribute to more complex features.

**Prerequisites:**
- First contribution completed successfully
- Good understanding of project architecture
- Familiarity with team workflows

**Acceptance Criteria:**
- [ ] Advanced features or patterns understood
- [ ] Performance considerations identified
- [ ] Security best practices applied
- [ ] Documentation updated where needed
- [ ] Code review process participated in

**Estimated Time:** 2-3 hours
**Difficulty:** advanced

**Focus Areas:**
- Performance optimization
- Security considerations  
- Advanced testing strategies
- Documentation improvements`;

    const faq = `# Frequently Asked Questions

## 🚀 Getting Started

### What is ${repoName}?

${analysis.description}. This project provides a comprehensive solution for developers looking to build modern, scalable applications with best practices built in.

### How do I get started quickly?

The fastest way to get started:

1. **Clone the repository**: \`git clone ${analysis.url || 'https://github.com/example/repo.git'}\`
2. **Install dependencies**: \`npm install\` or \`pip install -r requirements.txt\`
3. **Start development server**: \`npm start\` or \`python main.py\`
4. **Open your browser**: Navigate to \`http://localhost:3000\` (or shown port)
5. **Start exploring**: Check out the examples and documentation

### What are the system requirements?

**Minimum Requirements:**
- **OS**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Memory**: 4GB RAM (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Stable internet connection for dependencies

**Development Tools:**
- Git 2.20+
- Node.js 14+ (if JavaScript/TypeScript project)
- Python 3.8+ (if Python project)
- Code editor (VS Code recommended)

### Is this project beginner-friendly?

Absolutely! We've designed the onboarding process to be accessible to developers of all levels:
- **Beginners**: Start with our guided tasks and comprehensive documentation
- **Intermediate**: Jump into feature development with our contribution guidelines
- **Advanced**: Explore architecture decisions and contribute to core features

## 💻 Development

### How do I run tests?

**For JavaScript/Node.js projects:**
\`\`\`bash
npm test              # Run all tests
npm run test:watch    # Run tests in watch mode
npm run test:coverage # Run with coverage report
\`\`\`

**For Python projects:**
\`\`\`bash
pytest                # Run all tests
pytest --cov         # Run with coverage
pytest -v            # Verbose output
\`\`\`

### What's the development workflow?

1. **Create a branch**: \`git checkout -b feature/your-feature\`
2. **Make changes**: Follow our coding standards
3. **Test locally**: Run tests and linting
4. **Commit**: Use conventional commit messages
5. **Push & PR**: Create a pull request with description
6. **Review**: Address feedback from maintainers
7. **Merge**: Celebrate your contribution! 🎉

### How do I contribute?

We welcome contributions! Here's how:

**First-time contributors:**
- Look for issues labeled "good first issue"
- Read our CONTRIBUTING.md guide
- Join our community discussions

**Regular contributors:**
- Pick up issues that match your expertise
- Propose new features via GitHub issues
- Help review other contributors' PRs

### What coding standards should I follow?

We maintain consistent code quality through:
- **Linting**: ESLint/Pylint configurations included
- **Formatting**: Prettier/Black for automatic formatting
- **Testing**: Comprehensive test coverage required
- **Documentation**: Clear comments and README updates
- **Commits**: Conventional commit message format

## 🔧 Troubleshooting

### Common Setup Issues

**"Dependencies won't install"**
- Clear your package cache: \`npm cache clean --force\` or \`pip cache purge\`
- Delete node_modules/venv and reinstall
- Check your Node.js/Python version compatibility

**"Tests are failing"**
- Ensure all dependencies are installed
- Check environment variables are set correctly
- Run tests individually to isolate issues: \`npm test -- --testNamePattern="specific test"\`

**"Build/compilation errors"**
- Verify you're using the correct runtime version
- Check for missing environment variables
- Review recent changes that might have introduced issues

**"Port already in use"**
- Kill processes using the port: \`lsof -ti:3000 | xargs kill\` (macOS/Linux)
- Use a different port: \`PORT=3001 npm start\`
- Check for other running development servers

### Performance Issues

**"Application is slow"**
- Check your system meets minimum requirements
- Monitor memory usage during development
- Use development tools for profiling
- Consider using production builds for testing

### Where can I get help?

**Community Support:**
- 💬 [GitHub Discussions](./discussions) - General questions and ideas
- 🐛 [Issue Tracker](./issues) - Bug reports and feature requests
- 📖 [Documentation](./docs) - Comprehensive guides and API reference
- 💡 [Stack Overflow](https://stackoverflow.com/questions/tagged/${repoName.toLowerCase()}) - Technical questions

**Direct Contact:**
- 📧 Email maintainers for security issues
- 🐦 Follow us on social media for updates
- 🤝 Join our community chat/Discord

**Response Times:**
- Issues: Usually within 24-48 hours
- Pull requests: Within 1 week
- Security issues: Within 24 hours

## 🎯 Advanced Topics

### How do I deploy this project?

Deployment options vary by project type. Common approaches:
- **Static sites**: GitHub Pages, Netlify, Vercel
- **Web applications**: Heroku, AWS, Google Cloud
- **Containers**: Docker with Kubernetes or cloud container services

### Can I use this in production?

Yes! This project is production-ready with:
- Comprehensive testing
- Security best practices
- Performance optimizations
- Monitoring and logging support

### How do I customize for my needs?

The project is designed to be flexible:
- Configuration files for easy customization
- Plugin/extension system (if applicable)
- Clear separation of concerns for modifications
- Detailed architecture documentation`;

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
    
    // Update document content with enhanced formatting
    document.getElementById('tasksMarkdown').innerHTML = formatTasksContent(documents.tasks);
    document.getElementById('faqMarkdown').innerHTML = formatMarkdownContent(documents.faq);
    document.getElementById('quickstartMarkdown').innerHTML = formatMarkdownContent(documents.quickstart);
    
    // Apply syntax highlighting
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
    
    // Show results with animation
    const results = document.getElementById('results');
    results.classList.remove('hidden');
    results.classList.add('fade-in');
    
    // Show first tab by default
    showTab('tasks');
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth' });
}

// Content formatting functions
function formatMarkdownContent(content) {
    if (typeof marked !== 'undefined') {
        // Configure marked for better rendering
        marked.setOptions({
            breaks: true,
            gfm: true,
            highlight: function(code, lang) {
                if (typeof Prism !== 'undefined' && Prism.languages[lang]) {
                    return Prism.highlight(code, Prism.languages[lang], lang);
                }
                return code;
            }
        });
        return marked.parse(content);
    }
    
    // Fallback: basic markdown-like formatting
    return content
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/^(.+)$/gm, '<p>$1</p>')
        .replace(/<p><\/p>/g, '')
        .replace(/^---$/gm, '<hr>');
}

function formatTasksContent(content) {
    // Enhanced formatting specifically for tasks
    let formatted = formatMarkdownContent(content);
    
    // Add task card styling
    formatted = formatted.replace(
        /(<h2>.*?<\/h2>)([\s\S]*?)(?=<h2>|$)/g,
        function(match, title, body) {
            // Extract task metadata
            const difficultyMatch = body.match(/\*\*Difficulty:\*\*\s*(\w+)/);
            const timeMatch = body.match(/\*\*Estimated Time:\*\*\s*([^<]+)/);
            
            let difficulty = difficultyMatch ? difficultyMatch[1] : 'intermediate';
            let time = timeMatch ? timeMatch[1].trim() : 'Unknown';
            
            // Create task card
            return `
                <div class="task-card">
                    <div class="task-header">
                        ${title}
                        <div class="task-meta">
                            <span class="badge badge-${difficulty}">${difficulty}</span>
                            <span class="text-gray-600">⏱️ ${time}</span>
                        </div>
                    </div>
                    ${body}
                </div>
            `;
        }
    );
    
    // Format checklists
    formatted = formatted.replace(
        /<ul>([\s\S]*?)<\/ul>/g,
        function(match, content) {
            if (content.includes('[ ]')) {
                return '<ul class="checklist">' + content + '</ul>';
            }
            return match;
        }
    );
    
    // Format checkbox items
    formatted = formatted.replace(/- \[ \]/g, '<li>');
    formatted = formatted.replace(/- \[x\]/g, '<li class="completed">');
    
    return formatted;
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            // Show success feedback
            showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Copied to clipboard!', 'success');
    } catch (err) {
        showNotification('Failed to copy to clipboard', 'error');
    }
    
    document.body.removeChild(textArea);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-4 py-2 rounded-lg text-white z-50 transition-all duration-300 ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 'bg-blue-500'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
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