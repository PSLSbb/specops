"""
Unit tests for hello_world sample feature.

This module demonstrates comprehensive testing patterns used throughout
the SpecOps project, including default behavior testing, custom input
validation, edge case handling, and error condition testing.
"""

import pytest
from features.hello_world import hello_world, hello_world_advanced


class TestHelloWorld:
    """Test cases for basic hello_world function."""

    def test_hello_world_default(self):
        """Test hello_world with default parameters."""
        result = hello_world()
        assert result == "Hello, World!"

    def test_hello_world_with_name(self):
        """Test hello_world with custom name."""
        result = hello_world("SpecOps")
        assert result == "Hello, SpecOps!"

    def test_hello_world_with_empty_string(self):
        """Test hello_world with empty string defaults to World."""
        result = hello_world("")
        assert result == "Hello, World!"

    def test_hello_world_with_none(self):
        """Test hello_world with None explicitly defaults to World."""
        result = hello_world(None)
        assert result == "Hello, World!"

    def test_hello_world_with_whitespace_only(self):
        """Test hello_world with whitespace-only string defaults to World."""
        result = hello_world("   ")
        assert result == "Hello,    !"  # Preserves whitespace as provided

    def test_hello_world_with_special_characters(self):
        """Test hello_world handles special characters correctly."""
        result = hello_world("Alice & Bob")
        assert result == "Hello, Alice & Bob!"

    def test_hello_world_with_unicode(self):
        """Test hello_world handles Unicode characters correctly."""
        result = hello_world("世界")
        assert result == "Hello, 世界!"

    def test_hello_world_with_numbers_in_name(self):
        """Test hello_world handles names with numbers."""
        result = hello_world("User123")
        assert result == "Hello, User123!"

    def test_hello_world_type_error_integer(self):
        """Test hello_world raises TypeError for integer input."""
        with pytest.raises(TypeError, match="Expected string or None for name, got int"):
            hello_world(123)

    def test_hello_world_type_error_list(self):
        """Test hello_world raises TypeError for list input."""
        with pytest.raises(TypeError, match="Expected string or None for name, got list"):
            hello_world(["Alice", "Bob"])

    def test_hello_world_type_error_dict(self):
        """Test hello_world raises TypeError for dict input."""
        with pytest.raises(TypeError, match="Expected string or None for name, got dict"):
            hello_world({"name": "Alice"})

    def test_hello_world_type_error_boolean(self):
        """Test hello_world raises TypeError for boolean input."""
        with pytest.raises(TypeError, match="Expected string or None for name, got bool"):
            hello_world(True)


class TestHelloWorldAdvanced:
    """Test cases for advanced hello_world function with custom greeting."""

    def test_hello_world_advanced_default(self):
        """Test hello_world_advanced with all default parameters."""
        result = hello_world_advanced()
        assert result == "Hello, World!"

    def test_hello_world_advanced_custom_name(self):
        """Test hello_world_advanced with custom name."""
        result = hello_world_advanced("SpecOps")
        assert result == "Hello, SpecOps!"

    def test_hello_world_advanced_custom_greeting(self):
        """Test hello_world_advanced with custom greeting."""
        result = hello_world_advanced(greeting="Hi")
        assert result == "Hi, World!"

    def test_hello_world_advanced_both_custom(self):
        """Test hello_world_advanced with both custom name and greeting."""
        result = hello_world_advanced("Alice", "Welcome")
        assert result == "Welcome, Alice!"

    def test_hello_world_advanced_keyword_args(self):
        """Test hello_world_advanced with keyword arguments."""
        result = hello_world_advanced(name="Bob", greeting="Hey")
        assert result == "Hey, Bob!"

    def test_hello_world_advanced_greeting_only_keyword(self):
        """Test hello_world_advanced with greeting as keyword argument."""
        result = hello_world_advanced(greeting="Greetings")
        assert result == "Greetings, World!"

    def test_hello_world_advanced_empty_name(self):
        """Test hello_world_advanced with empty name defaults to World."""
        result = hello_world_advanced("", "Hi")
        assert result == "Hi, World!"

    def test_hello_world_advanced_none_name(self):
        """Test hello_world_advanced with None name defaults to World."""
        result = hello_world_advanced(None, "Hello")
        assert result == "Hello, World!"

    def test_hello_world_advanced_multilingual_greeting(self):
        """Test hello_world_advanced with non-English greetings."""
        result = hello_world_advanced("World", "Hola")
        assert result == "Hola, World!"
        
        result = hello_world_advanced("World", "Bonjour")
        assert result == "Bonjour, World!"

    def test_hello_world_advanced_greeting_with_punctuation(self):
        """Test hello_world_advanced with greeting containing punctuation."""
        result = hello_world_advanced("Alice", "Well, hello")
        assert result == "Well, hello, Alice!"

    def test_hello_world_advanced_name_type_error(self):
        """Test hello_world_advanced raises TypeError for invalid name type."""
        with pytest.raises(TypeError, match="Expected string or None for name, got int"):
            hello_world_advanced(123, "Hello")

    def test_hello_world_advanced_greeting_type_error(self):
        """Test hello_world_advanced raises TypeError for invalid greeting type."""
        with pytest.raises(TypeError, match="Expected string for greeting, got int"):
            hello_world_advanced("Alice", 123)

    def test_hello_world_advanced_greeting_type_error_none(self):
        """Test hello_world_advanced raises TypeError for None greeting."""
        with pytest.raises(TypeError, match="Expected string for greeting, got NoneType"):
            hello_world_advanced("Alice", None)

    def test_hello_world_advanced_empty_greeting_error(self):
        """Test hello_world_advanced raises ValueError for empty greeting."""
        with pytest.raises(ValueError, match="Greeting cannot be empty"):
            hello_world_advanced("Alice", "")

    def test_hello_world_advanced_whitespace_greeting_error(self):
        """Test hello_world_advanced raises ValueError for whitespace-only greeting."""
        with pytest.raises(ValueError, match="Greeting cannot be empty"):
            hello_world_advanced("Alice", "   ")

    def test_hello_world_advanced_tab_greeting_error(self):
        """Test hello_world_advanced raises ValueError for tab-only greeting."""
        with pytest.raises(ValueError, match="Greeting cannot be empty"):
            hello_world_advanced("Alice", "\t\n")


class TestHelloWorldEdgeCases:
    """Test cases for edge cases and boundary conditions."""

    def test_very_long_name(self):
        """Test hello_world with very long name."""
        long_name = "A" * 1000
        result = hello_world(long_name)
        assert result == f"Hello, {long_name}!"
        assert len(result) == 1008  # "Hello, " (7) + 1000 chars + "!" (1) = 1008

    def test_very_long_greeting(self):
        """Test hello_world_advanced with very long greeting."""
        long_greeting = "B" * 500
        result = hello_world_advanced("World", long_greeting)
        assert result == f"{long_greeting}, World!"
        assert len(result) == 508  # 500 chars + ", World!" (8) = 508

    def test_name_with_newlines(self):
        """Test hello_world with name containing newlines."""
        name_with_newlines = "Alice\nBob"
        result = hello_world(name_with_newlines)
        assert result == "Hello, Alice\nBob!"

    def test_greeting_with_newlines(self):
        """Test hello_world_advanced with greeting containing newlines."""
        greeting_with_newlines = "Hello\nThere"
        result = hello_world_advanced("World", greeting_with_newlines)
        assert result == "Hello\nThere, World!"

    def test_name_with_commas(self):
        """Test hello_world with name containing commas."""
        result = hello_world("Smith, John")
        assert result == "Hello, Smith, John!"

    def test_greeting_with_commas(self):
        """Test hello_world_advanced with greeting containing commas."""
        result = hello_world_advanced("Alice", "Well, well, hello")
        assert result == "Well, well, hello, Alice!"


class TestHelloWorldIntegration:
    """Integration tests demonstrating usage patterns."""

    def test_function_composition(self):
        """Test using hello_world functions together."""
        basic_greeting = hello_world("Developer")
        advanced_greeting = hello_world_advanced("Developer", "Welcome")
        
        assert basic_greeting == "Hello, Developer!"
        assert advanced_greeting == "Welcome, Developer!"
        assert basic_greeting != advanced_greeting

    def test_batch_processing(self):
        """Test processing multiple names."""
        names = ["Alice", "Bob", "Charlie", ""]
        results = [hello_world(name) for name in names]
        
        expected = [
            "Hello, Alice!",
            "Hello, Bob!",
            "Hello, Charlie!",
            "Hello, World!"
        ]
        assert results == expected

    def test_greeting_variations(self):
        """Test various greeting styles."""
        greetings = ["Hello", "Hi", "Hey", "Welcome", "Greetings"]
        name = "SpecOps"
        
        results = [hello_world_advanced(name, greeting) for greeting in greetings]
        expected = [f"{greeting}, {name}!" for greeting in greetings]
        
        assert results == expected

    def test_error_handling_in_batch(self):
        """Test error handling when processing multiple inputs."""
        inputs = ["Alice", 123, "Bob", None, "Charlie"]
        results = []
        errors = []
        
        for input_val in inputs:
            try:
                result = hello_world(input_val)
                results.append(result)
            except TypeError as e:
                errors.append(str(e))
        
        assert len(results) == 4  # Alice, Bob, None->World, Charlie
        assert len(errors) == 1   # Only 123 causes error
        assert "Expected string or None for name, got int" in errors[0]


class TestHelloWorldDocumentation:
    """Tests that verify docstring examples work correctly."""

    def test_docstring_examples_basic(self):
        """Test that basic hello_world docstring examples work."""
        # From hello_world docstring examples
        assert hello_world() == 'Hello, World!'
        assert hello_world("SpecOps") == 'Hello, SpecOps!'
        assert hello_world("") == 'Hello, World!'

    def test_docstring_examples_advanced(self):
        """Test that advanced hello_world docstring examples work."""
        # From hello_world_advanced docstring examples
        assert hello_world_advanced() == 'Hello, World!'
        assert hello_world_advanced("SpecOps", "Hi") == 'Hi, SpecOps!'
        assert hello_world_advanced(greeting="Welcome") == 'Welcome, World!'

    def test_function_signatures_match_docstrings(self):
        """Test that function signatures match their docstring descriptions."""
        import inspect
        
        # Test hello_world signature
        sig = inspect.signature(hello_world)
        params = list(sig.parameters.keys())
        assert params == ['name']
        assert sig.parameters['name'].default is None
        
        # Test hello_world_advanced signature
        sig_advanced = inspect.signature(hello_world_advanced)
        params_advanced = list(sig_advanced.parameters.keys())
        assert params_advanced == ['name', 'greeting']
        assert sig_advanced.parameters['name'].default is None
        assert sig_advanced.parameters['greeting'].default == "Hello"


class TestHelloWorldPerformance:
    """Performance and stress tests for hello_world functions."""

    def test_performance_basic_function(self):
        """Test basic performance of hello_world function."""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            hello_world("TestUser")
        end_time = time.time()
        
        # Should complete 1000 calls in well under a second
        assert (end_time - start_time) < 1.0

    def test_performance_advanced_function(self):
        """Test basic performance of hello_world_advanced function."""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            hello_world_advanced("TestUser", "Hi")
        end_time = time.time()
        
        # Should complete 1000 calls in well under a second
        assert (end_time - start_time) < 1.0

    def test_memory_usage_basic(self):
        """Test that hello_world doesn't leak memory with repeated calls."""
        import gc
        
        # Force garbage collection before test
        gc.collect()
        
        # Create many strings and let them be garbage collected
        for i in range(1000):
            result = hello_world(f"User{i}")
            # Don't store result, let it be garbage collected
            del result
        
        # Force garbage collection after test
        gc.collect()
        
        # Test passes if no memory errors occur
        assert True