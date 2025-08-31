"""Tests for error handling and recovery mechanisms."""

import pytest
import logging
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.utils.error_handler import (
    ErrorHandler,
    ErrorType,
    ErrorSeverity,
    ErrorContext,
    SpecOpsError,
    FileSystemError,
    AIProcessingError,
    HookExecutionError,
    ContentParsingError,
    ValidationError,
    get_error_handler,
    handle_error,
    retry_operation
)


class TestErrorTypes:
    """Test error type classes and their initialization."""
    
    def test_specops_error_creation(self):
        """Test basic SpecOpsError creation."""
        context = ErrorContext("test_component", "test_operation")
        error = SpecOpsError(
            "Test error",
            ErrorType.VALIDATION,
            ErrorSeverity.HIGH,
            context
        )
        
        assert error.message == "Test error"
        assert error.error_type == ErrorType.VALIDATION
        assert error.severity == ErrorSeverity.HIGH
        assert error.context == context
        assert error.original_error is None
        assert isinstance(error.timestamp, float)
    
    def test_file_system_error_creation(self):
        """Test FileSystemError creation with context."""
        error = FileSystemError(
            "File not found",
            "/path/to/file.txt",
            "read"
        )
        
        assert error.message == "File not found"
        assert error.error_type == ErrorType.FILE_SYSTEM
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.context.component == "file_system"
        assert error.context.operation == "read"
        assert error.context.file_path == "/path/to/file.txt"
    
    def test_ai_processing_error_creation(self):
        """Test AIProcessingError creation with model info."""
        error = AIProcessingError(
            "AI model failed",
            model="gpt-3.5-turbo",
            prompt_type="task_generation"
        )
        
        assert error.message == "AI model failed"
        assert error.error_type == ErrorType.AI_PROCESSING
        assert error.severity == ErrorSeverity.HIGH
        assert error.context.component == "ai_processing"
        assert error.context.additional_info["model"] == "gpt-3.5-turbo"
        assert error.context.additional_info["prompt_type"] == "task_generation"
    
    def test_hook_execution_error_creation(self):
        """Test HookExecutionError creation."""
        error = HookExecutionError(
            "Hook failed",
            hook_type="feature_created",
            hook_path="/path/to/hook.py"
        )
        
        assert error.message == "Hook failed"
        assert error.error_type == ErrorType.HOOK_EXECUTION
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.context.component == "hook_manager"
        assert error.context.additional_info["hook_type"] == "feature_created"
        assert error.context.file_path == "/path/to/hook.py"
    
    def test_content_parsing_error_creation(self):
        """Test ContentParsingError creation."""
        error = ContentParsingError(
            "Invalid markdown",
            file_path="/path/to/doc.md",
            content_type="markdown"
        )
        
        assert error.message == "Invalid markdown"
        assert error.error_type == ErrorType.CONTENT_PARSING
        assert error.severity == ErrorSeverity.LOW
        assert error.context.component == "content_analyzer"
        assert error.context.file_path == "/path/to/doc.md"
        assert error.context.additional_info["content_type"] == "markdown"
    
    def test_validation_error_creation(self):
        """Test ValidationError creation."""
        error = ValidationError(
            "Invalid field value",
            field_name="importance",
            value=15
        )
        
        assert error.message == "Invalid field value"
        assert error.error_type == ErrorType.VALIDATION
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.context.component == "validation"
        assert error.context.additional_info["field_name"] == "importance"
        assert error.context.additional_info["value"] == "15"


class TestErrorContext:
    """Test ErrorContext functionality."""
    
    def test_error_context_creation(self):
        """Test ErrorContext creation with defaults."""
        context = ErrorContext("test_component", "test_operation")
        
        assert context.component == "test_component"
        assert context.operation == "test_operation"
        assert context.file_path is None
        assert context.additional_info == {}
    
    def test_error_context_with_all_fields(self):
        """Test ErrorContext creation with all fields."""
        additional_info = {"key": "value", "number": 42}
        context = ErrorContext(
            "test_component",
            "test_operation",
            "/path/to/file.txt",
            additional_info
        )
        
        assert context.component == "test_component"
        assert context.operation == "test_operation"
        assert context.file_path == "/path/to/file.txt"
        assert context.additional_info == additional_info


class TestErrorHandler:
    """Test ErrorHandler functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()
        self.handler.logger = Mock()
    
    def test_error_handler_initialization(self):
        """Test ErrorHandler initialization."""
        handler = ErrorHandler()
        
        assert handler.error_counts == {}
        assert len(handler.recovery_strategies) == 5  # Default strategies
        assert handler.max_retries == 3
        assert handler.retry_delay == 1.0
        assert isinstance(handler.logger, logging.Logger)
    
    def test_error_handler_with_custom_logger(self):
        """Test ErrorHandler with custom logger."""
        custom_logger = Mock()
        handler = ErrorHandler(custom_logger)
        
        assert handler.logger == custom_logger
    
    def test_handle_specops_error(self):
        """Test handling a SpecOpsError."""
        error = SpecOpsError("Test error", ErrorType.VALIDATION)
        
        result = self.handler.handle_error(error)
        
        # Should log the error
        assert self.handler.logger.warning.called
        
        # Should update error counts
        assert self.handler.error_counts[ErrorType.VALIDATION] == 1
        
        # Should return recovery result (validation errors return "invalid_data_skipped" by default)
        assert result == "invalid_data_skipped"
    
    def test_handle_generic_exception(self):
        """Test handling a generic exception."""
        error = ValueError("Invalid value")
        context = ErrorContext("test_component", "test_operation")
        
        result = self.handler.handle_error(error, context)
        
        # Should convert to SpecOpsError and handle
        self.handler.logger.warning.assert_called_once()
        assert self.handler.error_counts[ErrorType.VALIDATION] == 1
    
    def test_handle_file_not_found_error(self):
        """Test handling FileNotFoundError."""
        error = FileNotFoundError("File not found")
        context = ErrorContext("test_component", "read", "/path/to/file.txt")
        
        result = self.handler.handle_error(error, context)
        
        # Should convert to FileSystemError and handle
        assert self.handler.logger.warning.called
        assert self.handler.error_counts[ErrorType.FILE_SYSTEM] == 1
    
    def test_error_classification(self):
        """Test error classification for different exception types."""
        # File system errors
        assert self.handler._classify_error(FileNotFoundError()) == ErrorType.FILE_SYSTEM
        assert self.handler._classify_error(PermissionError()) == ErrorType.FILE_SYSTEM
        assert self.handler._classify_error(OSError()) == ErrorType.FILE_SYSTEM
        
        # Validation errors
        assert self.handler._classify_error(ValueError()) == ErrorType.VALIDATION
        
        # Network errors
        network_error = Exception("Network connection failed")
        assert self.handler._classify_error(network_error) == ErrorType.NETWORK
        
        # Default classification
        generic_error = Exception("Generic error")
        assert self.handler._classify_error(generic_error) == ErrorType.CONFIGURATION
    
    def test_error_logging_by_severity(self):
        """Test that errors are logged with appropriate levels."""
        # Critical error
        critical_error = SpecOpsError("Critical", ErrorType.VALIDATION, ErrorSeverity.CRITICAL)
        self.handler.handle_error(critical_error)
        assert self.handler.logger.critical.called
        
        # High severity error
        self.handler.logger.reset_mock()
        high_error = SpecOpsError("High", ErrorType.VALIDATION, ErrorSeverity.HIGH)
        self.handler.handle_error(high_error)
        assert self.handler.logger.error.called
        
        # Medium severity error
        self.handler.logger.reset_mock()
        medium_error = SpecOpsError("Medium", ErrorType.VALIDATION, ErrorSeverity.MEDIUM)
        self.handler.handle_error(medium_error)
        assert self.handler.logger.warning.called
        
        # Low severity error
        self.handler.logger.reset_mock()
        low_error = SpecOpsError("Low", ErrorType.VALIDATION, ErrorSeverity.LOW)
        self.handler.handle_error(low_error)
        assert self.handler.logger.info.called
    
    def test_error_statistics(self):
        """Test error statistics tracking."""
        # Generate some errors
        self.handler.handle_error(SpecOpsError("Error 1", ErrorType.VALIDATION))
        self.handler.handle_error(SpecOpsError("Error 2", ErrorType.VALIDATION))
        self.handler.handle_error(SpecOpsError("Error 3", ErrorType.FILE_SYSTEM))
        
        stats = self.handler.get_error_statistics()
        
        assert stats["total_errors"] == 3
        assert stats["error_counts"]["validation"] == 2
        assert stats["error_counts"]["file_system"] == 1
        assert stats["most_common_error"] == "validation"
    
    def test_reset_error_counts(self):
        """Test resetting error count statistics."""
        # Generate some errors
        self.handler.handle_error(SpecOpsError("Error 1", ErrorType.VALIDATION))
        self.handler.handle_error(SpecOpsError("Error 2", ErrorType.FILE_SYSTEM))
        
        assert self.handler.get_error_statistics()["total_errors"] == 2
        
        # Reset counts
        self.handler.reset_error_counts()
        
        assert self.handler.get_error_statistics()["total_errors"] == 0
        assert self.handler.error_counts == {}
    
    def test_custom_recovery_strategy(self):
        """Test registering and using custom recovery strategies."""
        def custom_strategy(error):
            return "custom_recovery_result"
        
        self.handler.register_recovery_strategy(ErrorType.VALIDATION, custom_strategy)
        
        error = SpecOpsError("Test error", ErrorType.VALIDATION)
        result = self.handler.handle_error(error)
        
        assert result == "custom_recovery_result"
    
    def test_retry_configuration(self):
        """Test setting retry configuration."""
        self.handler.set_retry_config(5, 2.0)
        
        assert self.handler.max_retries == 5
        assert self.handler.retry_delay == 2.0


class TestRecoveryStrategies:
    """Test specific recovery strategies."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()
        self.handler.logger = Mock()
    
    def test_file_system_error_recovery_create_directories(self):
        """Test file system error recovery by creating directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "subdir" / "file.txt"
            error = FileSystemError(
                "Directory not found",
                str(file_path),
                "write"
            )
            
            result = self.handler._handle_file_system_error(error)
            
            assert result == "directories_created"
            assert file_path.parent.exists()
    
    def test_file_system_error_recovery_alternative_file(self):
        """Test file system error recovery using alternative files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create an alternative file
            alt_file = Path(temp_dir) / "README.md"
            alt_file.write_text("Alternative content")
            
            # Try to read non-existent file
            missing_file = Path(temp_dir) / "missing.txt"
            error = FileSystemError(
                "File not found",
                str(missing_file),
                "read"
            )
            
            result = self.handler._handle_file_system_error(error)
            
            assert result == str(alt_file)
    
    def test_file_system_error_recovery_create_empty_file(self):
        """Test file system error recovery by creating empty file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "empty.txt"
            error = FileSystemError(
                "File not found",
                str(file_path),
                "read",
                FileNotFoundError()
            )
            
            result = self.handler._handle_file_system_error(error)
            
            assert result == "empty_file_created"
            assert file_path.exists()
    
    def test_ai_processing_error_recovery(self):
        """Test AI processing error recovery strategies."""
        # Test retry with simplified prompt
        error = AIProcessingError(
            "AI failed",
            prompt_type="complex_task"
        )
        
        result = self.handler._handle_ai_processing_error(error)
        assert result == "retry_simplified"
        
        # Test template fallback
        error_no_prompt = AIProcessingError("AI failed")
        result = self.handler._handle_ai_processing_error(error_no_prompt)
        assert result == "template_fallback"
    
    def test_hook_execution_error_recovery(self):
        """Test hook execution error recovery strategies."""
        error = HookExecutionError(
            "Hook failed",
            hook_type="feature_created"
        )
        
        result = self.handler._handle_hook_execution_error(error)
        assert result == "hook_disabled_feature_created"
        
        # Test hook bypass
        error_no_type = HookExecutionError("Hook failed")
        result = self.handler._handle_hook_execution_error(error_no_type)
        assert result == "hook_bypassed"
    
    def test_content_parsing_error_recovery(self):
        """Test content parsing error recovery strategies."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write("Test content")
            temp_file_path = temp_file.name
        
        try:
            error = ContentParsingError(
                "Parse failed",
                file_path=temp_file_path
            )
            
            result = self.handler._handle_content_parsing_error(error)
            assert result == "Test content"
        finally:
            Path(temp_file_path).unlink()
        
        # Test content skipping
        error_no_file = ContentParsingError("Parse failed")
        result = self.handler._handle_content_parsing_error(error_no_file)
        assert result == "content_skipped"
    
    def test_validation_error_recovery(self):
        """Test validation error recovery strategies."""
        error = ValidationError(
            "Invalid field",
            field_name="importance"
        )
        
        result = self.handler._handle_validation_error(error)
        assert result == "default_value_used"
        
        # Test data skipping
        error_no_field = ValidationError("Invalid data")
        result = self.handler._handle_validation_error(error_no_field)
        assert result == "invalid_data_skipped"


class TestRetryMechanism:
    """Test retry mechanism functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()
        self.handler.logger = Mock()
    
    def test_successful_operation_no_retry(self):
        """Test successful operation that doesn't need retry."""
        def successful_operation():
            return "success"
        
        result = self.handler.retry_operation(successful_operation)
        assert result == "success"
    
    def test_operation_succeeds_after_retries(self):
        """Test operation that succeeds after some retries."""
        call_count = 0
        
        def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = self.handler.retry_operation(flaky_operation)
        
        assert result == "success"
        assert call_count == 3
    
    def test_operation_fails_after_max_retries(self):
        """Test operation that fails after maximum retries."""
        def failing_operation():
            raise ValueError("Persistent failure")
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with pytest.raises(ValueError, match="Persistent failure"):
                self.handler.retry_operation(failing_operation, max_retries=2)
        
        # Should have logged retry attempts (2 retries + recovery strategy info)
        assert self.handler.logger.info.call_count >= 2  # At least 2 retry attempts
        assert self.handler.logger.error.call_count == 1  # Final failure
    
    def test_retry_with_custom_parameters(self):
        """Test retry with custom max_retries and delay."""
        call_count = 0
        
        def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return "success"
        
        with patch('time.sleep') as mock_sleep:
            result = self.handler.retry_operation(
                flaky_operation,
                max_retries=1,
                delay=0.5
            )
        
        assert result == "success"
        assert call_count == 2
        mock_sleep.assert_called_once_with(0.5)  # Initial delay
    
    def test_retry_with_exponential_backoff(self):
        """Test retry mechanism uses exponential backoff."""
        def failing_operation():
            raise ValueError("Always fails")
        
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(ValueError):
                self.handler.retry_operation(
                    failing_operation,
                    max_retries=3,
                    delay=1.0
                )
        
        # Check exponential backoff: 1.0, 2.0, 4.0
        expected_calls = [((1.0,),), ((2.0,),), ((4.0,),)]
        assert mock_sleep.call_args_list == expected_calls
    
    def test_retry_with_context(self):
        """Test retry operation with error context."""
        def failing_operation():
            raise ValueError("Test failure")
        
        context = ErrorContext("test_component", "test_operation")
        
        with patch('time.sleep'):
            with pytest.raises(ValueError):
                self.handler.retry_operation(
                    failing_operation,
                    max_retries=1,
                    context=context
                )
        
        # Should have handled the error with context
        assert self.handler.error_counts[ErrorType.VALIDATION] == 1


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    def test_get_error_handler_singleton(self):
        """Test that get_error_handler returns singleton instance."""
        handler1 = get_error_handler()
        handler2 = get_error_handler()
        
        assert handler1 is handler2
        assert isinstance(handler1, ErrorHandler)
    
    def test_global_handle_error(self):
        """Test global handle_error function."""
        error = SpecOpsError("Test error", ErrorType.VALIDATION)
        
        # Should not raise exception
        result = handle_error(error)
        
        # Should return some recovery result
        assert result is not None
    
    def test_global_retry_operation(self):
        """Test global retry_operation function."""
        def successful_operation():
            return "global_success"
        
        result = retry_operation(successful_operation)
        assert result == "global_success"


class TestIntegrationScenarios:
    """Test integration scenarios with multiple error types."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()
        self.handler.logger = Mock()
    
    def test_cascading_errors(self):
        """Test handling cascading errors from different components."""
        # Simulate a file system error leading to AI processing error
        fs_error = FileSystemError("Config file not found", "/path/to/config.json", "read")
        ai_error = AIProcessingError("Cannot process without config", original_error=fs_error)
        
        # Handle both errors
        fs_result = self.handler.handle_error(fs_error)
        ai_result = self.handler.handle_error(ai_error)
        
        # AI error should have recovery strategy
        assert ai_result == "template_fallback"
        
        # Error counts should be tracked
        assert self.handler.error_counts[ErrorType.FILE_SYSTEM] == 1
        assert self.handler.error_counts[ErrorType.AI_PROCESSING] == 1
    
    def test_error_recovery_in_hook_execution(self):
        """Test error recovery during hook execution."""
        # Simulate hook execution that encounters multiple errors
        hook_error = HookExecutionError(
            "Feature analysis failed",
            hook_type="feature_created",
            hook_path="/path/to/feature.py"
        )
        
        result = self.handler.handle_error(hook_error)
        
        assert result == "hook_disabled_feature_created"
        assert self.handler.error_counts[ErrorType.HOOK_EXECUTION] == 1
    
    def test_error_handling_with_logging_verification(self):
        """Test that error handling produces appropriate log messages."""
        context = ErrorContext(
            "content_analyzer",
            "parse_markdown",
            "/path/to/doc.md",
            {"content_type": "markdown", "size": 1024}
        )
        
        error = ContentParsingError(
            "Invalid markdown syntax",
            file_path="/path/to/doc.md",
            content_type="markdown"
        )
        
        self.handler.handle_error(error, context)
        
        # Verify logging was called with appropriate message
        assert self.handler.logger.info.called
        log_calls = [call[0][0] for call in self.handler.logger.info.call_args_list]
        
        # Find the main error log message
        error_log = next((call for call in log_calls if "content_parsing" in call), None)
        assert error_log is not None
        assert "Invalid markdown syntax" in error_log
        assert "content_analyzer" in error_log
        assert "parse_content" in error_log  # This is the operation from the error context
        assert "/path/to/doc.md" in error_log


if __name__ == "__main__":
    pytest.main([__file__])