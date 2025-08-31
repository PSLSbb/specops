"""Error handling and recovery mechanisms for SpecOps components."""

import logging
import time
from typing import Optional, Dict, Any, Callable, Type, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class ErrorType(Enum):
    """Types of errors that can occur in the system."""
    FILE_SYSTEM = "file_system"
    AI_PROCESSING = "ai_processing"
    HOOK_EXECUTION = "hook_execution"
    CONTENT_PARSING = "content_parsing"
    VALIDATION = "validation"
    NETWORK = "network"
    CONFIGURATION = "configuration"


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Context information for error handling."""
    component: str
    operation: str
    file_path: Optional[str] = None
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}


class SpecOpsError(Exception):
    """Base exception class for SpecOps-specific errors."""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.severity = severity
        self.context = context
        self.original_error = original_error
        self.timestamp = time.time()


class FileSystemError(SpecOpsError):
    """Error related to file system operations."""
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: str = "unknown",
        original_error: Optional[Exception] = None
    ):
        context = ErrorContext(
            component="file_system",
            operation=operation,
            file_path=file_path
        )
        super().__init__(
            message,
            ErrorType.FILE_SYSTEM,
            ErrorSeverity.MEDIUM,
            context,
            original_error
        )


class AIProcessingError(SpecOpsError):
    """Error related to AI processing operations."""
    
    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        prompt_type: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        context = ErrorContext(
            component="ai_processing",
            operation="generate_content",
            additional_info={
                "model": model,
                "prompt_type": prompt_type
            }
        )
        super().__init__(
            message,
            ErrorType.AI_PROCESSING,
            ErrorSeverity.HIGH,
            context,
            original_error
        )


class HookExecutionError(SpecOpsError):
    """Error related to hook execution."""
    
    def __init__(
        self,
        message: str,
        hook_type: Optional[str] = None,
        hook_path: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        context = ErrorContext(
            component="hook_manager",
            operation="execute_hook",
            file_path=hook_path,
            additional_info={"hook_type": hook_type}
        )
        super().__init__(
            message,
            ErrorType.HOOK_EXECUTION,
            ErrorSeverity.MEDIUM,
            context,
            original_error
        )


class ContentParsingError(SpecOpsError):
    """Error related to content parsing operations."""
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        content_type: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        context = ErrorContext(
            component="content_analyzer",
            operation="parse_content",
            file_path=file_path,
            additional_info={"content_type": content_type}
        )
        super().__init__(
            message,
            ErrorType.CONTENT_PARSING,
            ErrorSeverity.LOW,
            context,
            original_error
        )


class ValidationError(SpecOpsError):
    """Error related to data validation."""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        value: Any = None,
        original_error: Optional[Exception] = None
    ):
        context = ErrorContext(
            component="validation",
            operation="validate_data",
            additional_info={
                "field_name": field_name,
                "value": str(value) if value is not None else None
            }
        )
        super().__init__(
            message,
            ErrorType.VALIDATION,
            ErrorSeverity.MEDIUM,
            context,
            original_error
        )


class ErrorHandler:
    """Central error handling and recovery system."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize error handler with optional logger."""
        self.logger = logger or self._setup_default_logger()
        self.error_counts: Dict[ErrorType, int] = {}
        self.recovery_strategies: Dict[ErrorType, Callable] = {}
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
        # Register default recovery strategies
        self._register_default_strategies()
    
    def _setup_default_logger(self) -> logging.Logger:
        """Set up default logger for error handling."""
        logger = logging.getLogger("specops.error_handler")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _register_default_strategies(self) -> None:
        """Register default recovery strategies for different error types."""
        self.recovery_strategies[ErrorType.FILE_SYSTEM] = self._handle_file_system_error
        self.recovery_strategies[ErrorType.AI_PROCESSING] = self._handle_ai_processing_error
        self.recovery_strategies[ErrorType.HOOK_EXECUTION] = self._handle_hook_execution_error
        self.recovery_strategies[ErrorType.CONTENT_PARSING] = self._handle_content_parsing_error
        self.recovery_strategies[ErrorType.VALIDATION] = self._handle_validation_error
    
    def handle_error(
        self,
        error: Union[Exception, SpecOpsError],
        context: Optional[ErrorContext] = None
    ) -> Optional[Any]:
        """
        Handle an error with appropriate recovery strategy.
        
        Args:
            error: The error to handle
            context: Additional context for error handling
            
        Returns:
            Recovery result if successful, None if no recovery possible
        """
        # Convert to SpecOpsError if needed
        if not isinstance(error, SpecOpsError):
            specops_error = self._convert_to_specops_error(error, context)
        else:
            specops_error = error
        
        # Log the error
        self._log_error(specops_error)
        
        # Update error counts
        self._update_error_counts(specops_error.error_type)
        
        # Apply recovery strategy
        recovery_strategy = self.recovery_strategies.get(specops_error.error_type)
        if recovery_strategy:
            try:
                return recovery_strategy(specops_error)
            except Exception as recovery_error:
                self.logger.error(
                    f"Recovery strategy failed for {specops_error.error_type}: {recovery_error}"
                )
        
        return None
    
    def _convert_to_specops_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> SpecOpsError:
        """Convert a generic exception to a SpecOpsError."""
        error_type = self._classify_error(error)
        
        if isinstance(error, (FileNotFoundError, PermissionError, OSError)):
            return FileSystemError(
                str(error),
                context.file_path if context else None,
                context.operation if context else "unknown",
                error
            )
        elif isinstance(error, ValueError):
            return ValidationError(str(error), original_error=error)
        else:
            return SpecOpsError(
                str(error),
                error_type,
                ErrorSeverity.MEDIUM,
                context,
                error
            )
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify an exception into an ErrorType."""
        if isinstance(error, (FileNotFoundError, PermissionError, OSError)):
            return ErrorType.FILE_SYSTEM
        elif isinstance(error, ValueError):
            return ErrorType.VALIDATION
        elif "network" in str(error).lower() or "connection" in str(error).lower():
            return ErrorType.NETWORK
        else:
            return ErrorType.CONFIGURATION
    
    def _log_error(self, error: SpecOpsError) -> None:
        """Log an error with appropriate level based on severity."""
        log_message = f"[{error.error_type.value}] {error.message}"
        
        if error.context:
            log_message += f" (Component: {error.context.component}, Operation: {error.context.operation}"
            if error.context.file_path:
                log_message += f", File: {error.context.file_path}"
            log_message += ")"
        
        if error.original_error:
            log_message += f" | Original: {error.original_error}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _update_error_counts(self, error_type: ErrorType) -> None:
        """Update error count statistics."""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def _handle_file_system_error(self, error: FileSystemError) -> Optional[str]:
        """Handle file system errors with fallback strategies."""
        if not error.context or not error.context.file_path:
            return None
        
        file_path = Path(error.context.file_path)
        
        # Strategy 1: Create parent directories if they don't exist
        if error.context.operation in ["write", "create"]:
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created missing directories for {file_path}")
                return "directories_created"
            except Exception as e:
                self.logger.warning(f"Could not create directories: {e}")
        
        # Strategy 2: Use alternative file path
        if error.context.operation == "read":
            alternatives = [
                file_path.with_suffix('.md'),
                file_path.with_suffix('.txt'),
                file_path.parent / f"README{file_path.suffix}",
                file_path.parent / "README.md"
            ]
            
            for alt_path in alternatives:
                if alt_path.exists():
                    self.logger.info(f"Using alternative file: {alt_path}")
                    return str(alt_path)
        
        # Strategy 3: Create empty file for missing files
        if isinstance(error.original_error, FileNotFoundError) and error.context.operation == "read":
            try:
                file_path.touch()
                self.logger.info(f"Created empty file: {file_path}")
                return "empty_file_created"
            except Exception as e:
                self.logger.warning(f"Could not create empty file: {e}")
        
        return None
    
    def _handle_ai_processing_error(self, error: AIProcessingError) -> Optional[str]:
        """Handle AI processing errors with fallback strategies."""
        # Strategy 1: Retry with simplified prompt
        if error.context and error.context.additional_info.get("prompt_type"):
            self.logger.info("Attempting AI processing with simplified prompt")
            return "retry_simplified"
        
        # Strategy 2: Use template-based generation
        self.logger.info("Falling back to template-based generation")
        return "template_fallback"
    
    def _handle_hook_execution_error(self, error: HookExecutionError) -> Optional[str]:
        """Handle hook execution errors with graceful degradation."""
        # Strategy 1: Disable problematic hook temporarily
        if error.context and error.context.additional_info.get("hook_type"):
            hook_type = error.context.additional_info["hook_type"]
            self.logger.warning(f"Temporarily disabling hook: {hook_type}")
            return f"hook_disabled_{hook_type}"
        
        # Strategy 2: Continue without hook execution
        self.logger.info("Continuing operation without hook execution")
        return "hook_bypassed"
    
    def _handle_content_parsing_error(self, error: ContentParsingError) -> Optional[str]:
        """Handle content parsing errors with fallback strategies."""
        # Strategy 1: Try basic text extraction
        if error.context and error.context.file_path:
            try:
                with open(error.context.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.logger.info("Using basic text extraction as fallback")
                return content
            except Exception as e:
                self.logger.warning(f"Basic text extraction failed: {e}")
        
        # Strategy 2: Skip problematic content
        self.logger.info("Skipping problematic content")
        return "content_skipped"
    
    def _handle_validation_error(self, error: ValidationError) -> Optional[str]:
        """Handle validation errors with data correction strategies."""
        # Strategy 1: Use default values for invalid fields
        if error.context and error.context.additional_info.get("field_name"):
            field_name = error.context.additional_info["field_name"]
            self.logger.info(f"Using default value for invalid field: {field_name}")
            return "default_value_used"
        
        # Strategy 2: Skip invalid data
        self.logger.info("Skipping invalid data")
        return "invalid_data_skipped"
    
    def retry_operation(
        self,
        operation: Callable,
        max_retries: Optional[int] = None,
        delay: Optional[float] = None,
        context: Optional[ErrorContext] = None
    ) -> Any:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation: The operation to retry
            max_retries: Maximum number of retries (uses instance default if None)
            delay: Initial delay between retries (uses instance default if None)
            context: Context for error handling
            
        Returns:
            Result of the operation if successful
            
        Raises:
            The last exception if all retries fail
        """
        max_retries = max_retries or self.max_retries
        delay = delay or self.retry_delay
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    wait_time = delay * (2 ** attempt)  # Exponential backoff
                    self.logger.info(
                        f"Operation failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {wait_time:.1f}s: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Operation failed after {max_retries + 1} attempts")
        
        # Handle the final error
        self.handle_error(last_exception, context)
        raise last_exception
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring and debugging."""
        return {
            "error_counts": {error_type.value: count for error_type, count in self.error_counts.items()},
            "total_errors": sum(self.error_counts.values()),
            "most_common_error": max(self.error_counts.items(), key=lambda x: x[1])[0].value if self.error_counts else None
        }
    
    def reset_error_counts(self) -> None:
        """Reset error count statistics."""
        self.error_counts.clear()
        self.logger.info("Error count statistics reset")
    
    def register_recovery_strategy(
        self,
        error_type: ErrorType,
        strategy: Callable[[SpecOpsError], Optional[Any]]
    ) -> None:
        """Register a custom recovery strategy for an error type."""
        self.recovery_strategies[error_type] = strategy
        self.logger.info(f"Registered custom recovery strategy for {error_type.value}")
    
    def set_retry_config(self, max_retries: int, delay: float) -> None:
        """Set retry configuration."""
        self.max_retries = max_retries
        self.retry_delay = delay
        self.logger.info(f"Updated retry config: max_retries={max_retries}, delay={delay}")
    
    def handle_analysis_error(self, error: Exception, workspace_path: str) -> Optional[Any]:
        """Handle repository analysis errors with fallback strategies."""
        self.logger.warning(f"Analysis error in {workspace_path}: {error}")
        
        # Try to create a minimal analysis result
        try:
            from ..models import RepositoryAnalysis
            return RepositoryAnalysis()
        except Exception as e:
            self.logger.error(f"Could not create fallback analysis: {e}")
            return None
    
    def handle_generation_error(self, error: Exception, doc_type: str) -> None:
        """Handle document generation errors."""
        self.logger.error(f"Failed to generate {doc_type} document: {error}")
        
        # Could implement fallback generation strategies here
        # For now, just log the error
    
    def handle_hook_error(self, error: Exception, hook_type: str, file_path: str) -> None:
        """Handle hook execution errors."""
        self.logger.error(f"Hook {hook_type} failed for {file_path}: {error}")
        
        # Could implement hook recovery strategies here
        # For now, just log the error


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def handle_error(
    error: Union[Exception, SpecOpsError],
    context: Optional[ErrorContext] = None
) -> Optional[Any]:
    """Convenience function to handle errors using the global error handler."""
    return get_error_handler().handle_error(error, context)


def retry_operation(
    operation: Callable,
    max_retries: Optional[int] = None,
    delay: Optional[float] = None,
    context: Optional[ErrorContext] = None
) -> Any:
    """Convenience function to retry operations using the global error handler."""
    return get_error_handler().retry_operation(operation, max_retries, delay, context)