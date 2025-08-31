"""AI provider implementations for various platforms."""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AIResponse:
    """Standardized AI response format."""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, api_key: str, model: str, temperature: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> AIResponse:
        """Generate content using the AI provider."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass
    
    @classmethod
    @abstractmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available models for this provider."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI ChatGPT provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        super().__init__(api_key, model, temperature)
        self._client = None
    
    def _get_client(self):
        """Get OpenAI client, lazy loading."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
        return self._client
    
    def generate(self, prompt: str, system_prompt: str = "") -> AIResponse:
        """Generate content using OpenAI."""
        try:
            client = self._get_client()
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=2000
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                model=self.model,
                provider="openai",
                tokens_used=response.usage.total_tokens if response.usage else None
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        try:
            import openai
            return bool(self.api_key)
        except ImportError:
            return False
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get available OpenAI models."""
        return [
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", temperature: float = 0.7):
        super().__init__(api_key, model, temperature)
        self._client = None
    
    def _get_client(self):
        """Get Anthropic client, lazy loading."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        return self._client
    
    def generate(self, prompt: str, system_prompt: str = "") -> AIResponse:
        """Generate content using Claude."""
        try:
            client = self._get_client()
            
            kwargs = {
                "model": self.model,
                "max_tokens": 2000,
                "temperature": self.temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = client.messages.create(**kwargs)
            
            return AIResponse(
                content=response.content[0].text,
                model=self.model,
                provider="anthropic",
                tokens_used=response.usage.input_tokens + response.usage.output_tokens if response.usage else None
            )
            
        except Exception as e:
            self.logger.error(f"Anthropic generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        try:
            import anthropic
            return bool(self.api_key)
        except ImportError:
            return False
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get available Claude models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]


class GoogleAIProvider(AIProvider):
    """Google AI Studio (Gemini) provider."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro", temperature: float = 0.7):
        super().__init__(api_key, model, temperature)
        self._client = None
    
    def _get_client(self):
        """Get Google AI client, lazy loading."""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai
            except ImportError:
                raise ImportError("Google AI package not installed. Run: pip install google-generativeai")
        return self._client
    
    def generate(self, prompt: str, system_prompt: str = "") -> AIResponse:
        """Generate content using Gemini."""
        try:
            client = self._get_client()
            
            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            model = client.GenerativeModel(self.model)
            response = model.generate_content(
                full_prompt,
                generation_config=client.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=2000
                )
            )
            
            return AIResponse(
                content=response.text,
                model=self.model,
                provider="google",
                tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else None
            )
            
        except Exception as e:
            self.logger.error(f"Google AI generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Google AI is available."""
        try:
            import google.generativeai
            return bool(self.api_key)
        except ImportError:
            return False
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get available Gemini models."""
        return [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro"
        ]


class OpenRouterProvider(AIProvider):
    """OpenRouter provider (50+ models)."""
    
    def __init__(self, api_key: str, model: str = "deepseek/deepseek-chat", temperature: float = 0.7):
        super().__init__(api_key, model, temperature)
    
    def generate(self, prompt: str, system_prompt: str = "") -> AIResponse:
        """Generate content using OpenRouter."""
        try:
            import requests
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            return AIResponse(
                content=data["choices"][0]["message"]["content"],
                model=self.model,
                provider="openrouter",
                tokens_used=data.get("usage", {}).get("total_tokens")
            )
            
        except Exception as e:
            self.logger.error(f"OpenRouter generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if OpenRouter is available."""
        try:
            import requests
            return bool(self.api_key)
        except ImportError:
            return False
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get popular OpenRouter models."""
        return [
            "deepseek/deepseek-chat",
            "qwen/qwen-2.5-72b-instruct",
            "meta-llama/llama-3.1-70b-instruct",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-pro-1.5",
            "mistralai/mistral-large",
            "cohere/command-r-plus"
        ]


class GroqProvider(AIProvider):
    """Groq provider (fast inference)."""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile", temperature: float = 0.7):
        super().__init__(api_key, model, temperature)
        self._client = None
    
    def _get_client(self):
        """Get Groq client, lazy loading."""
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError("Groq package not installed. Run: pip install groq")
        return self._client
    
    def generate(self, prompt: str, system_prompt: str = "") -> AIResponse:
        """Generate content using Groq."""
        try:
            client = self._get_client()
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=2000
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                model=self.model,
                provider="groq",
                tokens_used=response.usage.total_tokens if response.usage else None
            )
            
        except Exception as e:
            self.logger.error(f"Groq generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Groq is available."""
        try:
            from groq import Groq
            return bool(self.api_key)
        except ImportError:
            return False
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get available Groq models."""
        return [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]


class IBMWatsonProvider(AIProvider):
    """IBM Watson provider."""
    
    def __init__(self, api_key: str, model: str = "ibm/granite-13b-chat-v2", temperature: float = 0.7, url: str = None):
        super().__init__(api_key, model, temperature)
        self.url = url or os.getenv('IBM_WATSON_URL')
    
    def generate(self, prompt: str, system_prompt: str = "") -> AIResponse:
        """Generate content using IBM Watson."""
        try:
            import requests
            
            # Combine prompts for Watson
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:" if system_prompt else f"User: {prompt}\nAssistant:"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model_id": self.model,
                "input": full_prompt,
                "parameters": {
                    "temperature": self.temperature,
                    "max_new_tokens": 2000
                }
            }
            
            response = requests.post(
                f"{self.url}/ml/v1/text/generation",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"IBM Watson API error: {response.status_code} - {response.text}")
            
            result = response.json()
            
            return AIResponse(
                content=result["results"][0]["generated_text"],
                model=self.model,
                provider="ibm_watson",
                tokens_used=result["results"][0].get("token_count")
            )
            
        except Exception as e:
            self.logger.error(f"IBM Watson generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if IBM Watson is available."""
        try:
            import requests
            return bool(self.api_key and self.url)
        except ImportError:
            return False
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get available IBM Watson models."""
        return [
            "ibm/granite-13b-chat-v2",
            "ibm/granite-13b-instruct-v2",
            "meta-llama/llama-3-70b-instruct",
            "mistralai/mixtral-8x7b-instruct-v01"
        ]


class MockProvider(AIProvider):
    """Mock provider for testing and fallback."""
    
    def __init__(self, model: str = "mock-model", temperature: float = 0.7):
        super().__init__("mock-key", model, temperature)
    
    def generate(self, prompt: str, system_prompt: str = "") -> AIResponse:
        """Generate mock content."""
        time.sleep(0.1)  # Simulate API delay
        
        if "task suggestions" in prompt.lower() and "json" in prompt.lower():
            content = """[
    {
        "title": "Set up development environment",
        "description": "Install required dependencies and configure the development environment.",
        "acceptance_criteria": [
            "Repository cloned locally",
            "Dependencies installed successfully", 
            "Development server runs without errors"
        ],
        "prerequisites": ["Git installed", "Code editor"],
        "estimated_time": 30,
        "difficulty": "easy"
    },
    {
        "title": "Understand project structure",
        "description": "Explore the codebase and understand the main components.",
        "acceptance_criteria": [
            "Main directories identified",
            "Key files understood",
            "Documentation read"
        ],
        "prerequisites": ["Set up development environment"],
        "estimated_time": 45,
        "difficulty": "medium"
    }
]"""
        elif "task suggestions" in prompt.lower():
            content = """# Onboarding Tasks

## Task 1: Set up development environment
**Description:** Install required dependencies and configure the development environment.
**Prerequisites:** Git installed, Code editor
**Acceptance Criteria:**
- [ ] Repository cloned locally
- [ ] Dependencies installed successfully
- [ ] Development server runs without errors
**Estimated Time:** 30 minutes
**Difficulty:** beginner

## Task 2: Understand project structure
**Description:** Explore the codebase and understand the main components.
**Prerequisites:** Development environment set up
**Acceptance Criteria:**
- [ ] Main directories identified
- [ ] Key files understood
- [ ] Documentation read
**Estimated Time:** 45 minutes
**Difficulty:** intermediate"""
        
        elif "faq" in prompt.lower() and "json" in prompt.lower():
            content = """[
    {
        "question": "What is this project?",
        "answer": "This is a comprehensive project that provides solutions for modern development needs.",
        "category": "Getting Started"
    },
    {
        "question": "How do I get started?",
        "answer": "1. Clone the repository\\n2. Install dependencies\\n3. Follow setup instructions\\n4. Start developing",
        "category": "Getting Started"
    },
    {
        "question": "What are the requirements?",
        "answer": "- Modern operating system\\n- Required runtime environment\\n- Internet connection for dependencies",
        "category": "Getting Started"
    },
    {
        "question": "How do I contribute?",
        "answer": "1. Fork the repository\\n2. Create a feature branch\\n3. Make changes\\n4. Submit a pull request",
        "category": "Development"
    }
]"""
        elif "faq" in prompt.lower():
            content = """# FAQ

## Getting Started

### What is this project?
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
        
        elif "quick start" in prompt.lower():
            content = """# Quick Start Guide

## Prerequisites
- Git
- Node.js or Python (depending on project)
- Code editor

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-name>
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
        
        else:
            content = f"Mock AI response for prompt: {prompt[:100]}..."
        
        return AIResponse(
            content=content,
            model=self.model,
            provider="mock",
            tokens_used=len(content.split())
        )
    
    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get mock models."""
        return ["mock-model", "mock-advanced"]


# Provider registry
PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleAIProvider,
    "openrouter": OpenRouterProvider,
    "groq": GroqProvider,
    "ibm_watson": IBMWatsonProvider,
    "mock": MockProvider
}


def get_provider(provider_name: str, api_key: str = None, model: str = None, **kwargs) -> AIProvider:
    """Get an AI provider instance."""
    if provider_name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(PROVIDERS.keys())}")
    
    provider_class = PROVIDERS[provider_name]
    
    # Use environment variables as fallback
    if not api_key:
        env_keys = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY", 
            "google": "GOOGLE_AI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "groq": "GROQ_API_KEY",
            "ibm_watson": "IBM_WATSON_API_KEY"
        }
        api_key = os.getenv(env_keys.get(provider_name, ""))
    
    # Use default model if not specified
    if not model:
        model = provider_class.get_available_models()[0]
    
    if provider_name == "mock":
        return provider_class(model=model, **kwargs)
    else:
        return provider_class(api_key=api_key, model=model, **kwargs)


def get_available_providers() -> Dict[str, Dict[str, Any]]:
    """Get information about all available providers."""
    providers_info = {}
    
    for name, provider_class in PROVIDERS.items():
        if name == "mock":
            continue
            
        # Try to create instance to check availability
        try:
            provider = get_provider(name)
            available = provider.is_available()
        except:
            available = False
        
        providers_info[name] = {
            "name": name.title(),
            "available": available,
            "models": provider_class.get_available_models(),
            "description": _get_provider_description(name)
        }
    
    return providers_info


def _get_provider_description(provider_name: str) -> str:
    """Get description for a provider."""
    descriptions = {
        "openai": "Access to GPT-4 and ChatGPT models. Industry standard for AI applications.",
        "anthropic": "Claude 3.5 Sonnet and Haiku models. Strong reasoning, multilingual, ethical AI.",
        "google": "Access to Gemini 2.5 and other models. No billing surprises, great for prototyping.",
        "openrouter": "50+ models including DeepSeek, Qwen. One key, easy model switching, great for testing.",
        "groq": "Fast inference for Llama, Mistral. Ideal for real-time bots and low-latency apps.",
        "ibm_watson": "NLP, speech, and vision APIs. Free tier with generous limits."
    }
    return descriptions.get(provider_name, "AI provider")