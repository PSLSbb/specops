# Integration Tests

This directory contains comprehensive integration tests for the SpecOps onboarding factory system.

## Test Structure

### End-to-End Workflow Tests (`test_end_to_end_workflow.py`)
Tests complete pipelines from content analysis to output generation:
- Repository analysis to document generation pipeline
- Hook integration with file system operations
- Error handling and recovery mechanisms
- Content quality and consistency validation
- Component integration health checks
- Configuration loading and validation
- Concurrent hook execution

### Hook Integration Tests (`test_hook_integration.py`)
Tests hook integration with actual file system operations:
- Hook manager initialization and configuration
- Hook registration and status reporting
- Feature created hook execution
- README saved hook execution
- Error handling and graceful degradation
- Hook configuration updates
- Hook execution logging and monitoring
- Timeout and retry behavior
- Multiple hook types coordination
- Hook state persistence and recovery

### File Operations Tests (`test_file_operations.py`)
Tests file reading, writing, and updating operations:
- Content analyzer file reading across various file types
- Task generator file operations (loading, appending, writing)
- FAQ generator file operations (reading, merging, writing)
- Quick Start generator README operations
- File encoding and special character handling
- Large file and directory handling
- File permission and access error handling
- Concurrent file operations
- File backup and recovery mechanisms

### Sample Repository Testing (`test_sample_repository_testing.py`)
Tests the system against various repository structures and content types:
- Python library repositories
- Web application repositories
- Microservice repositories
- Repository analysis across different structures
- Document generation quality across repositories
- Steering guidelines application
- File structure handling
- Code example extraction
- Dependency detection
- Error handling consistency
- Performance characteristics
- Output adherence to requirements

## Test Fixtures

### Sample Repositories (`fixtures/sample_repositories.py`)
Provides realistic sample repositories for testing:
- **PythonLibraryRepository**: Complete Python library with data processing functionality
- **WebApplicationRepository**: FastAPI web application with authentication and database
- **MicroserviceRepository**: Containerized microservice with Docker and Kubernetes configs

Each sample repository includes:
- Realistic file structure and content
- Appropriate dependencies and configuration
- Documentation and examples
- Test files
- Steering guidelines specific to the repository type

## Running Integration Tests

### Using the Test Runner
```bash
# Run all integration tests
python tests/run_integration_tests.py

# Run with verbose output
python tests/run_integration_tests.py -v

# Run with coverage
python tests/run_integration_tests.py --coverage

# Run specific test categories
python tests/run_integration_tests.py --end-to-end
python tests/run_integration_tests.py --hooks
python tests/run_integration_tests.py --file-ops
python tests/run_integration_tests.py --sample-repos

# Run tests matching a pattern
python tests/run_integration_tests.py -k "test_repository_analysis"
```

### Using pytest directly
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_end_to_end_workflow.py -v

# Run with coverage
pytest tests/integration/ --cov=src --cov-report=html

# Run tests matching pattern
pytest tests/integration/ -k "repository_analysis" -v
```

## Test Requirements

### Dependencies
The integration tests require all standard SpecOps dependencies plus:
- `pytest` >= 7.0.0
- `pytest-asyncio` >= 0.21.0
- `httpx` >= 0.24.0 (for web application testing)

### System Requirements
- Sufficient disk space for temporary test repositories
- Write permissions in the test directory
- Network access for AI service mocking (tests use mocks by default)

### Environment Variables
- `SPECOPS_TEST_TIMEOUT`: Test timeout in seconds (default: 300)
- `SPECOPS_TEST_TEMP_DIR`: Custom temporary directory for test files

## Test Data and Cleanup

### Temporary Files
All tests use temporary directories that are automatically cleaned up after each test. The cleanup happens in the fixture teardown, ensuring no test artifacts remain.

### Sample Repository Content
Sample repositories contain realistic but synthetic data:
- No real API keys or sensitive information
- Placeholder URLs and email addresses
- Generic but representative code examples
- Appropriate file sizes for testing without being excessive

## Mocking Strategy

### AI Service Mocking
Integration tests mock AI service calls by default to:
- Ensure consistent test results
- Avoid external service dependencies
- Speed up test execution
- Test error handling scenarios

### File System Operations
File operations use real file system interactions within temporary directories to:
- Test actual file I/O behavior
- Verify file encoding handling
- Test concurrent access scenarios
- Validate file permission handling

## Performance Considerations

### Test Execution Time
- Individual tests should complete within 30 seconds
- Full integration test suite should complete within 10 minutes
- Sample repository creation is optimized for speed while maintaining realism

### Resource Usage
- Tests clean up temporary files to avoid disk space issues
- Memory usage is monitored for large file handling tests
- Concurrent tests are limited to avoid resource contention

## Troubleshooting

### Common Issues

1. **Test Timeouts**: Increase timeout with `SPECOPS_TEST_TIMEOUT` environment variable
2. **Disk Space**: Ensure sufficient space in temp directory
3. **Permissions**: Verify write permissions in test directory
4. **Dependencies**: Install all required test dependencies

### Debug Mode
Run tests with debug output:
```bash
pytest tests/integration/ -v -s --tb=long
```

### Logging
Enable detailed logging:
```bash
pytest tests/integration/ --log-cli-level=DEBUG
```

## Contributing

When adding new integration tests:

1. Follow the existing test structure and naming conventions
2. Use appropriate fixtures for setup and cleanup
3. Mock external dependencies appropriately
4. Include both success and error scenarios
5. Add performance considerations for long-running tests
6. Update this README with new test descriptions

### Test Categories

Mark tests with appropriate pytest markers:
- `@pytest.mark.integration` - All integration tests
- `@pytest.mark.slow` - Tests taking > 10 seconds
- `@pytest.mark.requires_ai` - Tests requiring AI service
- `@pytest.mark.requires_docker` - Tests requiring Docker

Example:
```python
@pytest.mark.integration
@pytest.mark.slow
def test_large_repository_analysis(self):
    # Test implementation
    pass
```