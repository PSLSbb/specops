# Regenerate all documents

## Table of Contents

- [Getting Started](#getting-started)
- [Setup](#setup)
- [Usage](#usage)
- [Development](#development)
- [Troubleshooting](#troubleshooting)


## Getting Started

Questions about initial setup and first steps.

### What is SpecOps?

SpecOps is an AI-powered spec-first onboarding factory that automatically generates comprehensive onboarding materials from repository content. It analyzes existing Markdown documentation to create structured onboarding tasks, README Quick Start sections, and AI-generated FAQs.

### How does SpecOps work?

SpecOps follows a pipeline architecture where content analysis feeds into multiple generation engines (tasks, FAQs, Quick Start) that produce structured documentation. It uses Kiro's hook system to automatically update documentation when features are created or README files are saved.

### What are the main components of SpecOps?

The main components include: - **Content Analyzer**: Parses and extracts semantic information from Markdown files - **AI Processing Engine**: Leverages language models to understand content and generate insights - **Generation Engines**: Specialized modules for creating tasks, FAQs, and Quick Start content - **Hook Manager**: Coordinates automatic triggers and content updates - **Style Processor**: Ensures all generated content follows steering guidelines.

### What is this project?

This is a comprehensive project that provides solutions for modern development needs.

### How do I get started?

1. Clone the repository 2. Install dependencies 3. Follow setup instructions 4. Start developing.

### What are the requirements?

- Modern operating system - ****Required**** runtime environment - Internet connection for dependencies.

## Setup

Installation, configuration, and environment setup questions.

### What are the system requirements?

- Python 3.8 or higher - Access to AI processing capabilities (configured through the AI Processing Engine) - Write permissions in the workspace directory - Optional: Kiro IDE for hook integration.

### How do I set up SpecOps for my project?

SpecOps uses configuration files in the `.kiro/steering/` directory: - ```code-style.md```: Code style guidelines - ```structure.md```: Project structure guidelines - ```onboarding-style.md```: Onboarding content style guidelines The system automatically loads these configurations during initialization.

### How do I verify my setup is working?

Run the following command to check system status: ```bash ``python -m`` ``src.cli`` status ``` This will show the status of all components and configurations.

### How do I set up the development environment?

Install Python 3.8+, then run '```pip install``` -r ```requirements.txt```' to install dependencies.

## Usage

How to use features and common usage patterns.

### How do I generate onboarding documents?

You can generate documents using the CLI: ```bash ``python -m`` ``src.cli`` generate --all ``python -m`` ``src.cli`` generate --tasks ``python -m`` ``src.cli`` generate --faq ``python -m`` ``src.cli`` generate --quick-start ```.

### How do I analyze my repository content?

Use the analyze command to extract structured information: ```bash ``python -m`` ``src.cli`` analyze ``` You can also save the analysis results to a file: ```bash ``python -m`` ``src.cli`` analyze --output ``analysis.json`` ```.

### How do I register Kiro hooks?

To enable automatic document updates, register the hooks: ```bash ``python -m`` ``src.cli`` hooks --register ``` This will register both the feature-created and README-save hooks.

### How do I manually trigger hooks?

You can manually trigger hooks for testing: ```bash ``python -m`` ``src.cli`` hooks --feature-created path/to/``feature.py`` ``python -m`` ``src.cli`` hooks --readme-saved ``README.md`` ```.

### What files does SpecOps generate or modify?

SpecOps can generate or modify: - ```tasks.md```: Structured onboarding tasks - ```faq.md```: AI-generated frequently asked questions - ```README.md```: Quick Start section updates - Hook configurations in `.kiro/` directory.

## Development

Development workflow, contributing, and building.

### How do I run the tests?

Use pytest to run all tests: ```bash ``python -m`` pytest ``` For specific test files: ```bash ``python -m`` pytest tests/``test_specific.py`` ```.

### How do I contribute to SpecOps?

1. Fork the repository 2. Create a feature branch 3. Follow the code style guidelines in `.kiro/steering/``code-style.md``` 4. Add tests for your changes 5. Run the test suite to ensure everything works 6. Submit a pull request.

### How do I extend the AI processing capabilities?

The AI Processing Engine is located in `src/ai/``processing_engine.py```. You can extend it by: - Adding new prompt templates - Implementing additional analysis methods - Enhancing the content understanding capabilities.

### How do I customize the generated content style?

Modify the steering files in `.kiro/steering/`: - ```onboarding-style.md```: Controls tone and style of generated content - ```code-style.md```: Defines code formatting and structure rules - ```structure.md```: Specifies project organization guidelines.

### How do I contribute?

1. Fork the repository 2. Create a feature branch 3. Make changes 4. Submit a pull request.

## Troubleshooting

Common issues and their solutions.

### Why is my FAQ content not being generated?

Check the following: 1. Ensure your repository has Markdown files for analysis 2. Verify the AI Processing Engine is properly configured 3. Check that the content analyzer can read your files 4. Run ```python -m`` ``src.cli`` status` to verify component health.

### The generated tasks seem incomplete or incorrect?

This can happen if: - The repository content is limited or unclear - The AI processing encounters errors - The content analyzer cannot extract sufficient information **Solution**: Add more detailed documentation in Markdown format and re-run the generation.

### Hooks are not triggering automatically?

Verify that: 1. Hooks are properly registered: ```python -m`` ``src.cli`` hooks --status` 2. You're using Kiro IDE with hook support 3. The hook configuration is enabled in your settings 4. File paths match the expected patterns.

### I'm getting permission errors when generating files?

Ensure that: - You have write permissions in the workspace directory - The target files are not locked by other applications - Your user account has sufficient privileges.

### The generated content doesn't follow my style guidelines?

Check that: 1. Your steering files in `.kiro/steering/` are properly formatted 2. The style processor is loading the guidelines correctly 3. Re-run generation after updating steering files 4. Verify the style configuration is valid.

### How do I reset or regenerate all documentation?

To start fresh: ```bash rm -f ``tasks.md`` ``faq.md`` ``python -m`` ``src.cli`` generate --all ``` ******Note:******: This will overwrite existing generated content but preserve manual additions where possible. *Manual additions and edits are preserved during updates.*. *Manual additions and edits are preserved during updates.*.

---

*This FAQ is automatically generated and updated based on repository analysis.*
*Manual additions and edits are preserved during updates.*