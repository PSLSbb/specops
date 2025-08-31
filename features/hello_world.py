"""
Hello World sample feature for SpecOps onboarding.

This module demonstrates basic function structure, type hints, docstrings,
and error handling patterns used throughout the SpecOps project.
"""

from typing import Optional


def hello_world(name: Optional[str] = None) -> str:
    """
    Generate a greeting message.
    
    This function serves as a simple example of the coding patterns and
    structure used in the SpecOps project. It demonstrates proper type
    hints, documentation, and basic error handling.
    
    Args:
        name: The name to include in the greeting. If None or empty,
              defaults to "World".
    
    Returns:
        A formatted greeting string.
        
    Raises:
        TypeError: If name is not a string or None.
        
    Examples:
        >>> hello_world()
        'Hello, World!'
        >>> hello_world("SpecOps")
        'Hello, SpecOps!'
        >>> hello_world("")
        'Hello, World!'
    """
    if name is not None and not isinstance(name, str):
        raise TypeError(f"Expected string or None for name, got {type(name).__name__}")
    
    # Handle empty string or None by defaulting to "World"
    if not name:
        name = "World"
    
    return f"Hello, {name}!"


def hello_world_advanced(name: Optional[str] = None, greeting: str = "Hello") -> str:
    """
    Generate a customizable greeting message.
    
    This function extends the basic hello_world functionality to demonstrate
    more complex parameter handling and validation patterns.
    
    Args:
        name: The name to include in the greeting. If None or empty,
              defaults to "World".
        greeting: The greeting word to use. Defaults to "Hello".
    
    Returns:
        A formatted greeting string with custom greeting.
        
    Raises:
        TypeError: If name is not a string or None, or if greeting is not a string.
        ValueError: If greeting is empty.
        
    Examples:
        >>> hello_world_advanced()
        'Hello, World!'
        >>> hello_world_advanced("SpecOps", "Hi")
        'Hi, SpecOps!'
        >>> hello_world_advanced(greeting="Welcome")
        'Welcome, World!'
    """
    if name is not None and not isinstance(name, str):
        raise TypeError(f"Expected string or None for name, got {type(name).__name__}")
    
    if not isinstance(greeting, str):
        raise TypeError(f"Expected string for greeting, got {type(greeting).__name__}")
    
    if not greeting.strip():
        raise ValueError("Greeting cannot be empty")
    
    # Handle empty string or None by defaulting to "World"
    if not name:
        name = "World"
    
    return f"{greeting}, {name}!"