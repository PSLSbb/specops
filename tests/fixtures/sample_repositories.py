"""Sample repository fixtures for testing different repository structures."""

from pathlib import Path
from typing import Dict, Any
import tempfile
import shutil


class SampleRepository:
    """Base class for sample repository fixtures."""
    
    def __init__(self, name: str):
        self.name = name
        self.temp_dir = None
        self.workspace = None
    
    def create(self) -> Path:
        """Create the sample repository and return its path."""
        self.temp_dir = tempfile.mkdtemp(prefix=f"specops_test_{self.name}_")
        self.workspace = Path(self.temp_dir)
        self._create_structure()
        return self.workspace
    
    def cleanup(self):
        """Clean up the temporary repository."""
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_structure(self):
        """Override in subclasses to create specific repository structure."""
        raise NotImplementedError
    
    def __enter__(self):
        return self.create()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class PythonLibraryRepository(SampleRepository):
    """Sample Python library repository with typical structure."""
    
    def __init__(self):
        super().__init__("python_library")
    
    def _create_structure(self):
        """Create Python library structure."""
        # Create directories
        (self.workspace / 'src').mkdir()
        (self.workspace / 'src' / 'mylib').mkdir()
        (self.workspace / 'tests').mkdir()
        (self.workspace / 'docs').mkdir()
        (self.workspace / 'examples').mkdir()
        (self.workspace / '.kiro').mkdir()
        (self.workspace / '.kiro' / 'steering').mkdir()
        
        # README.md
        readme_content = """# MyLib - A Python Library

A comprehensive Python library for data processing and analysis.

## Features

- Data validation and cleaning
- Statistical analysis functions
- Export to multiple formats
- Extensible plugin system

## Installation

```bash
pip install mylib
```

## Quick Start

```python
from mylib import DataProcessor

processor = DataProcessor()
data = processor.load_csv('data.csv')
cleaned_data = processor.clean(data)
results = processor.analyze(cleaned_data)
```

## Documentation

See the [full documentation](docs/) for detailed usage instructions.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.
"""
        (self.workspace / 'README.md').write_text(readme_content, encoding='utf-8')
        
        # Main library code
        init_content = '''"""MyLib - A Python library for data processing."""

__version__ = "1.0.0"
__author__ = "Test Author"

from .data_processor import DataProcessor
from .validators import DataValidator
from .exporters import CSVExporter, JSONExporter

__all__ = ["DataProcessor", "DataValidator", "CSVExporter", "JSONExporter"]
'''
        (self.workspace / 'src' / 'mylib' / '__init__.py').write_text(init_content, encoding='utf-8')
        
        # Data processor module
        data_processor_content = '''"""Core data processing functionality."""

import pandas as pd
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Main class for data processing operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the data processor.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.data = None
        self.processed_data = None
        
    def load_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Load data from CSV file.
        
        Args:
            file_path: Path to CSV file
            **kwargs: Additional arguments for pandas.read_csv
            
        Returns:
            Loaded DataFrame
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        try:
            self.data = pd.read_csv(file_path, **kwargs)
            logger.info(f"Loaded {len(self.data)} rows from {file_path}")
            return self.data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise ValueError(f"Invalid CSV format: {e}")
    
    def clean(self, data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Clean the data by removing duplicates and handling missing values.
        
        Args:
            data: DataFrame to clean (uses self.data if None)
            
        Returns:
            Cleaned DataFrame
        """
        if data is None:
            data = self.data
        
        if data is None:
            raise ValueError("No data to clean. Load data first.")
        
        # Remove duplicates
        cleaned = data.drop_duplicates()
        
        # Handle missing values
        numeric_columns = cleaned.select_dtypes(include=['number']).columns
        cleaned[numeric_columns] = cleaned[numeric_columns].fillna(cleaned[numeric_columns].mean())
        
        # Handle categorical missing values
        categorical_columns = cleaned.select_dtypes(include=['object']).columns
        cleaned[categorical_columns] = cleaned[categorical_columns].fillna('Unknown')
        
        self.processed_data = cleaned
        logger.info(f"Cleaned data: {len(cleaned)} rows remaining")
        return cleaned
    
    def analyze(self, data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Perform statistical analysis on the data.
        
        Args:
            data: DataFrame to analyze (uses processed_data if None)
            
        Returns:
            Dictionary containing analysis results
        """
        if data is None:
            data = self.processed_data
        
        if data is None:
            raise ValueError("No data to analyze. Process data first.")
        
        analysis = {
            'row_count': len(data),
            'column_count': len(data.columns),
            'numeric_summary': data.describe().to_dict(),
            'missing_values': data.isnull().sum().to_dict(),
            'data_types': data.dtypes.to_dict()
        }
        
        logger.info("Analysis completed")
        return analysis
'''
        (self.workspace / 'src' / 'mylib' / 'data_processor.py').write_text(data_processor_content, encoding='utf-8')
        
        # Validators module
        validators_content = '''"""Data validation utilities."""

import pandas as pd
from typing import List, Dict, Any, Callable
import re


class ValidationError(Exception):
    """Raised when data validation fails."""
    pass


class DataValidator:
    """Validates data according to specified rules."""
    
    def __init__(self):
        """Initialize the validator."""
        self.rules = []
        self.errors = []
    
    def add_rule(self, column: str, rule: Callable, message: str):
        """Add a validation rule.
        
        Args:
            column: Column name to validate
            rule: Validation function that returns True if valid
            message: Error message if validation fails
        """
        self.rules.append({
            'column': column,
            'rule': rule,
            'message': message
        })
    
    def validate_email(self, email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email string to validate
            
        Returns:
            True if valid email format
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format.
        
        Args:
            phone: Phone number string to validate
            
        Returns:
            True if valid phone format
        """
        # Simple phone validation - digits and common separators
        pattern = r'^[\d\s\-\(\)\+\.]{10,}$'
        return bool(re.match(pattern, phone))
    
    def validate_dataframe(self, data: pd.DataFrame) -> bool:
        """Validate entire DataFrame against all rules.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if all validations pass
            
        Raises:
            ValidationError: If any validation fails
        """
        self.errors = []
        
        for rule in self.rules:
            column = rule['column']
            validation_func = rule['rule']
            message = rule['message']
            
            if column not in data.columns:
                self.errors.append(f"Column '{column}' not found in data")
                continue
            
            # Apply validation to each row
            for idx, value in data[column].items():
                if pd.isna(value):
                    continue  # Skip NaN values
                
                try:
                    if not validation_func(value):
                        self.errors.append(f"Row {idx}, Column '{column}': {message}")
                except Exception as e:
                    self.errors.append(f"Row {idx}, Column '{column}': Validation error - {e}")
        
        if self.errors:
            raise ValidationError(f"Validation failed with {len(self.errors)} errors: {self.errors[:5]}")
        
        return True
'''
        (self.workspace / 'src' / 'mylib' / 'validators.py').write_text(validators_content, encoding='utf-8')
        
        # Exporters module
        exporters_content = '''"""Data export utilities."""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseExporter:
    """Base class for data exporters."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the exporter.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    def export(self, data: pd.DataFrame, output_path: str) -> None:
        """Export data to specified format.
        
        Args:
            data: DataFrame to export
            output_path: Path for output file
        """
        raise NotImplementedError


class CSVExporter(BaseExporter):
    """Export data to CSV format."""
    
    def export(self, data: pd.DataFrame, output_path: str) -> None:
        """Export DataFrame to CSV file.
        
        Args:
            data: DataFrame to export
            output_path: Path for CSV output file
        """
        try:
            data.to_csv(output_path, index=False, **self.config)
            logger.info(f"Exported {len(data)} rows to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            raise


class JSONExporter(BaseExporter):
    """Export data to JSON format."""
    
    def export(self, data: pd.DataFrame, output_path: str) -> None:
        """Export DataFrame to JSON file.
        
        Args:
            data: DataFrame to export
            output_path: Path for JSON output file
        """
        try:
            # Convert DataFrame to JSON
            json_data = data.to_dict(orient='records')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, **self.config)
            
            logger.info(f"Exported {len(data)} rows to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            raise


class ExcelExporter(BaseExporter):
    """Export data to Excel format."""
    
    def export(self, data: pd.DataFrame, output_path: str) -> None:
        """Export DataFrame to Excel file.
        
        Args:
            data: DataFrame to export
            output_path: Path for Excel output file
        """
        try:
            data.to_excel(output_path, index=False, **self.config)
            logger.info(f"Exported {len(data)} rows to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export Excel: {e}")
            raise
'''
        (self.workspace / 'src' / 'mylib' / 'exporters.py').write_text(exporters_content, encoding='utf-8')
        
        # Test files
        test_data_processor = '''"""Tests for data processor module."""

import pytest
import pandas as pd
import tempfile
from pathlib import Path

from src.mylib.data_processor import DataProcessor


class TestDataProcessor:
    """Test cases for DataProcessor class."""
    
    @pytest.fixture
    def sample_csv(self):
        """Create a sample CSV file for testing."""
        data = {
            'name': ['Alice', 'Bob', 'Charlie', 'Alice', 'David'],
            'age': [25, 30, None, 25, 35],
            'email': ['alice@test.com', 'bob@test.com', 'charlie@test.com', 'alice@test.com', 'david@test.com'],
            'score': [85.5, 92.0, 78.5, 85.5, None]
        }
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            return f.name
    
    def test_initialization(self):
        """Test DataProcessor initialization."""
        processor = DataProcessor()
        assert processor.config == {}
        assert processor.data is None
        assert processor.processed_data is None
        
        config = {'test': 'value'}
        processor_with_config = DataProcessor(config)
        assert processor_with_config.config == config
    
    def test_load_csv(self, sample_csv):
        """Test CSV loading functionality."""
        processor = DataProcessor()
        data = processor.load_csv(sample_csv)
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 5
        assert list(data.columns) == ['name', 'age', 'email', 'score']
        assert processor.data is not None
    
    def test_load_csv_file_not_found(self):
        """Test CSV loading with non-existent file."""
        processor = DataProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.load_csv('non_existent_file.csv')
    
    def test_clean_data(self, sample_csv):
        """Test data cleaning functionality."""
        processor = DataProcessor()
        processor.load_csv(sample_csv)
        
        cleaned_data = processor.clean()
        
        # Should remove duplicates
        assert len(cleaned_data) == 4  # One duplicate removed
        
        # Should fill missing values
        assert cleaned_data['age'].isnull().sum() == 0
        assert cleaned_data['score'].isnull().sum() == 0
        
        assert processor.processed_data is not None
    
    def test_clean_no_data(self):
        """Test cleaning without loaded data."""
        processor = DataProcessor()
        
        with pytest.raises(ValueError, match="No data to clean"):
            processor.clean()
    
    def test_analyze_data(self, sample_csv):
        """Test data analysis functionality."""
        processor = DataProcessor()
        processor.load_csv(sample_csv)
        processor.clean()
        
        analysis = processor.analyze()
        
        assert isinstance(analysis, dict)
        assert 'row_count' in analysis
        assert 'column_count' in analysis
        assert 'numeric_summary' in analysis
        assert 'missing_values' in analysis
        assert 'data_types' in analysis
        
        assert analysis['row_count'] == 4  # After cleaning
        assert analysis['column_count'] == 4
    
    def test_analyze_no_data(self):
        """Test analysis without processed data."""
        processor = DataProcessor()
        
        with pytest.raises(ValueError, match="No data to analyze"):
            processor.analyze()
'''
        (self.workspace / 'tests' / 'test_data_processor.py').write_text(test_data_processor, encoding='utf-8')
        
        # Documentation
        api_docs = """# API Documentation

## DataProcessor

The main class for data processing operations.

### Methods

#### `__init__(config=None)`
Initialize the data processor with optional configuration.

#### `load_csv(file_path, **kwargs)`
Load data from a CSV file.

**Parameters:**
- `file_path` (str): Path to the CSV file
- `**kwargs`: Additional arguments passed to pandas.read_csv

**Returns:**
- `pd.DataFrame`: The loaded data

**Example:**
```python
processor = DataProcessor()
data = processor.load_csv('data.csv')
```

#### `clean(data=None)`
Clean the data by removing duplicates and handling missing values.

**Parameters:**
- `data` (pd.DataFrame, optional): Data to clean. Uses loaded data if None.

**Returns:**
- `pd.DataFrame`: Cleaned data

#### `analyze(data=None)`
Perform statistical analysis on the data.

**Parameters:**
- `data` (pd.DataFrame, optional): Data to analyze. Uses processed data if None.

**Returns:**
- `dict`: Analysis results including summary statistics

## DataValidator

Validates data according to specified rules.

### Methods

#### `add_rule(column, rule, message)`
Add a validation rule for a specific column.

#### `validate_email(email)`
Validate email format.

#### `validate_phone(phone)`
Validate phone number format.

#### `validate_dataframe(data)`
Validate entire DataFrame against all rules.

## Exporters

### CSVExporter
Export data to CSV format.

### JSONExporter  
Export data to JSON format.

### ExcelExporter
Export data to Excel format.
"""
        (self.workspace / 'docs' / 'api.md').write_text(api_docs, encoding='utf-8')
        
        # Setup guide
        setup_guide = """# Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

## Installation

### From PyPI (Recommended)

```bash
pip install mylib
```

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/example/mylib.git
   cd mylib
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

## Verification

Run the test suite to verify installation:

```bash
pytest tests/
```

## Configuration

Create a configuration file `config.json`:

```json
{
    "log_level": "INFO",
    "default_encoding": "utf-8",
    "export_settings": {
        "csv": {"sep": ","},
        "json": {"indent": 2}
    }
}
```
"""
        (self.workspace / 'docs' / 'setup.md').write_text(setup_guide, encoding='utf-8')
        
        # Examples
        example_basic = '''"""Basic usage example for MyLib."""

from src.mylib import DataProcessor, DataValidator, CSVExporter

def main():
    """Demonstrate basic MyLib functionality."""
    
    # Initialize processor
    processor = DataProcessor()
    
    # Load data
    print("Loading data...")
    data = processor.load_csv('sample_data.csv')
    print(f"Loaded {len(data)} rows")
    
    # Clean data
    print("Cleaning data...")
    cleaned_data = processor.clean(data)
    print(f"Cleaned data has {len(cleaned_data)} rows")
    
    # Analyze data
    print("Analyzing data...")
    analysis = processor.analyze(cleaned_data)
    print(f"Analysis complete: {analysis['row_count']} rows, {analysis['column_count']} columns")
    
    # Validate data
    print("Validating data...")
    validator = DataValidator()
    validator.add_rule('email', validator.validate_email, 'Invalid email format')
    
    try:
        validator.validate_dataframe(cleaned_data)
        print("Data validation passed")
    except Exception as e:
        print(f"Validation failed: {e}")
    
    # Export results
    print("Exporting data...")
    exporter = CSVExporter()
    exporter.export(cleaned_data, 'output.csv')
    print("Export complete")

if __name__ == '__main__':
    main()
'''
        (self.workspace / 'examples' / 'basic_usage.py').write_text(example_basic, encoding='utf-8')
        
        # Configuration files
        (self.workspace / 'requirements.txt').write_text("""pandas>=1.3.0
pytest>=7.0.0
openpyxl>=3.0.0
""", encoding='utf-8')
        
        (self.workspace / 'setup.py').write_text('''"""Setup script for MyLib."""

from setuptools import setup, find_packages

setup(
    name="mylib",
    version="1.0.0",
    description="A Python library for data processing and analysis",
    author="Test Author",
    author_email="test@example.com",
    packages=find_packages(where="src", encoding='utf-8'),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
''')
        
        # Steering files
        (self.workspace / '.kiro' / 'steering' / 'code-style.md').write_text("""# Code Style Guidelines

## Python Style

- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Write comprehensive docstrings using Google style
- Maximum line length: 100 characters
- Use meaningful variable and function names

## Documentation

- All public functions must have docstrings
- Include parameter types and descriptions
- Provide usage examples for complex functions
- Document exceptions that may be raised

## Testing

- Write unit tests for all public functions
- Use descriptive test names
- Include edge cases and error conditions
- Aim for high test coverage
""", encoding='utf-8')
        
        (self.workspace / '.kiro' / 'steering' / 'structure.md').write_text("""# Project Structure Guidelines

## Directory Organization

```
mylib/
├── src/mylib/          # Main package code
├── tests/              # Unit tests
├── docs/               # Documentation
├── examples/           # Usage examples
├── .kiro/steering/     # SpecOps configuration
└── requirements.txt    # Dependencies
```

## Module Organization

- Keep modules focused on single responsibilities
- Use clear, descriptive module names
- Separate core logic from utilities
- Group related functionality together

## Import Guidelines

- Use absolute imports from package root
- Group imports: standard library, third-party, local
- Avoid circular imports
- Use __all__ to control public API
""", encoding='utf-8')
        
        (self.workspace / '.kiro' / 'steering' / 'onboarding-style.md').write_text("""# Onboarding Style Guidelines

## Documentation Tone

- Be clear and concise
- Use active voice
- Provide practical examples
- Explain the "why" not just the "how"

## Task Structure

- Break complex tasks into smaller steps
- Include verification steps
- Provide expected outcomes
- Reference relevant documentation

## Code Examples

- Use realistic, practical examples
- Include error handling
- Show both basic and advanced usage
- Provide complete, runnable code
""", encoding='utf-8')


class WebApplicationRepository(SampleRepository):
    """Sample web application repository with typical structure."""
    
    def __init__(self):
        super().__init__("web_application")
    
    def _create_structure(self):
        """Create web application structure."""
        # Create directories
        (self.workspace / 'src').mkdir()
        (self.workspace / 'src' / 'webapp').mkdir()
        (self.workspace / 'src' / 'webapp' / 'api').mkdir()
        (self.workspace / 'src' / 'webapp' / 'models').mkdir()
        (self.workspace / 'src' / 'webapp' / 'services').mkdir()
        (self.workspace / 'tests').mkdir()
        (self.workspace / 'tests' / 'unit').mkdir()
        (self.workspace / 'tests' / 'integration').mkdir()
        (self.workspace / 'docs').mkdir()
        (self.workspace / 'config').mkdir()
        (self.workspace / 'static').mkdir()
        (self.workspace / 'templates').mkdir()
        (self.workspace / '.kiro').mkdir()
        (self.workspace / '.kiro' / 'steering').mkdir()
        
        # README.md
        readme_content = """# WebApp - Modern Web Application

A modern web application built with Python and FastAPI.

## Features

- RESTful API with FastAPI
- User authentication and authorization
- Database integration with SQLAlchemy
- Real-time notifications
- Responsive web interface

## Architecture

- **Backend**: FastAPI with Python 3.9+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML/CSS/JavaScript with Bootstrap
- **Authentication**: JWT tokens
- **Testing**: pytest with coverage

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up database:
   ```bash
   python -m webapp.database init
   ```

3. Run the application:
   ```bash
   uvicorn webapp.main:app --reload
   ```

4. Open http://localhost:8000 in your browser

## API Documentation

Interactive API documentation is available at http://localhost:8000/docs

## Testing

Run the test suite:
```bash
pytest tests/ -v --cov=webapp
```
"""
        (self.workspace / 'README.md').write_text(readme_content, encoding='utf-8')
        
        # Main application
        main_app = '''"""Main FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from .api import users, auth, items
from .models.database import engine, Base
from .services.auth_service import AuthService

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="WebApp API",
    description="A modern web application API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Security
security = HTTPBearer()
auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    token = credentials.credentials
    user = await auth_service.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(items.router, prefix="/api/items", tags=["items"])

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebApp</title>
        <link href="/static/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <h1>Welcome to WebApp</h1>
            <p>A modern web application built with FastAPI.</p>
            <a href="/docs" class="btn btn-primary">API Documentation</a>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        (self.workspace / 'src' / 'webapp' / 'main.py').write_text(main_app, encoding='utf-8')
        
        # User model
        user_model = '''"""User model and database schema."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from .database import Base


class User(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response data."""
    
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    
    username: str
    password: str
'''
        (self.workspace / 'src' / 'webapp' / 'models' / 'user.py').write_text(user_model, encoding='utf-8')
        
        # Auth API
        auth_api = '''"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.user import UserCreate, UserLogin, UserResponse
from ..services.auth_service import AuthService
from ..services.user_service import UserService

router = APIRouter()
auth_service = AuthService()
user_service = UserService()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = await user_service.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = await user_service.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = await user_service.create_user(db, user_data)
    return user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = await auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout():
    """Logout user (client should discard token)."""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(auth_service.get_current_user)):
    """Get current user information."""
    return current_user
'''
        (self.workspace / 'src' / 'webapp' / 'api' / 'auth.py').write_text(auth_api, encoding='utf-8')
        
        # Tests
        test_auth = '''"""Tests for authentication functionality."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from webapp.main import app
from webapp.models.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_user(self):
        """Test user registration."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert "id" in data
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username."""
        user_data = {
            "username": "testuser",
            "email": "another@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    def test_login_success(self):
        """Test successful login."""
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_get_current_user(self):
        """Test getting current user information."""
        # First login to get token
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        login_response = client.post("/api/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Use token to get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
'''
        (self.workspace / 'tests' / 'unit' / 'test_auth.py').write_text(test_auth, encoding='utf-8')
        
        # Configuration files
        (self.workspace / 'requirements.txt').write_text("""fastapi>=0.100.0
uvicorn[standard]>=0.23.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
pytest>=7.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
""", encoding='utf-8')
        
        # Documentation
        api_docs = """# API Documentation

## Authentication

### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
    "username": "string",
    "email": "user@example.com",
    "password": "string",
    "full_name": "string"
}
```

### POST /api/auth/login
Authenticate user and receive access token.

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

### GET /api/auth/me
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

## Users

### GET /api/users
List all users (admin only).

### GET /api/users/{user_id}
Get specific user information.

### PUT /api/users/{user_id}
Update user information.

### DELETE /api/users/{user_id}
Delete user account (admin only).

## Items

### GET /api/items
List all items.

### POST /api/items
Create a new item.

### GET /api/items/{item_id}
Get specific item.

### PUT /api/items/{item_id}
Update item.

### DELETE /api/items/{item_id}
Delete item.
"""
        (self.workspace / 'docs' / 'api.md').write_text(api_docs, encoding='utf-8')
        
        # Steering files
        (self.workspace / '.kiro' / 'steering' / 'code-style.md').write_text("""# Code Style Guidelines

## Python/FastAPI Style

- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Write comprehensive docstrings
- Use async/await for database operations
- Separate concerns: models, services, API endpoints

## API Design

- Use RESTful conventions
- Include proper HTTP status codes
- Provide clear error messages
- Use Pydantic models for request/response validation
- Include comprehensive API documentation

## Database

- Use SQLAlchemy ORM
- Define clear model relationships
- Include database migrations
- Use connection pooling
- Handle database errors gracefully
""", encoding='utf-8')


class MicroserviceRepository(SampleRepository):
    """Sample microservice repository with Docker and API structure."""
    
    def __init__(self):
        super().__init__("microservice")
    
    def _create_structure(self):
        """Create microservice structure."""
        # Create directories
        (self.workspace / 'src').mkdir()
        (self.workspace / 'src' / 'service').mkdir()
        (self.workspace / 'tests').mkdir()
        (self.workspace / 'docker').mkdir()
        (self.workspace / 'k8s').mkdir()
        (self.workspace / 'docs').mkdir()
        (self.workspace / '.kiro').mkdir()
        (self.workspace / '.kiro' / 'steering').mkdir()
        
        # README with microservice-specific content
        readme_content = """# User Service - Microservice

A containerized microservice for user management with REST API.

## Features

- RESTful API for user operations
- Docker containerization
- Kubernetes deployment ready
- Health checks and monitoring
- Structured logging
- Configuration management

## Architecture

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **Message Queue**: RabbitMQ
- **Monitoring**: Prometheus metrics
- **Deployment**: Docker + Kubernetes

## Quick Start

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start dependencies with Docker Compose:
   ```bash
   docker-compose up -d postgres redis rabbitmq
   ```

3. Run the service:
   ```bash
   python -m service.main
   ```

### Docker Deployment

1. Build the image:
   ```bash
   docker build -t user-service:latest .
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up
   ```

### Kubernetes Deployment

```bash
kubectl apply -f k8s/
```

## API Endpoints

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

## Configuration

Environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `RABBITMQ_URL` - RabbitMQ connection string
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
"""
        (self.workspace / 'README.md').write_text(readme_content, encoding='utf-8')
        
        # Dockerfile
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "service.main"]
"""
        (self.workspace / 'Dockerfile').write_text(dockerfile_content, encoding='utf-8')
        
        # Docker Compose
        docker_compose = """version: '3.8'

services:
  user-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/userdb
      - REDIS_URL=redis://redis:6379
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
      - rabbitmq
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=userdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest

volumes:
  postgres_data:
"""
        (self.workspace / 'docker-compose.yml').write_text(docker_compose, encoding='utf-8')
        
        # Kubernetes deployment
        k8s_deployment = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  labels:
    app: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: database-url
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: LOG_LEVEL
          value: "INFO"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
"""
        (self.workspace / 'k8s' / 'deployment.yaml').write_text(k8s_deployment, encoding='utf-8')
        
        # Service code with monitoring
        main_service = '''"""Main microservice application with monitoring."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

from .api import users, health
from .config import get_settings
from .database import init_db
from .logging_config import setup_logging

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    settings = get_settings()
    setup_logging(settings.log_level)
    await init_db()
    logging.info("User service started")
    
    yield
    
    # Shutdown
    logging.info("User service shutting down")

# Create FastAPI app
app = FastAPI(
    title="User Service",
    description="Microservice for user management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus instrumentation
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to response headers."""
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Update metrics
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(process_time)
    
    return response

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "service.main:app",
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower(),
        reload=settings.debug
    )
'''
        (self.workspace / 'src' / 'service' / 'main.py').write_text(main_service, encoding='utf-8')
        
        # Configuration management
        config_module = '''"""Configuration management for the microservice."""

from functools import lru_cache
from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/userdb"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    
    # Application
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str = "your-secret-key-here"
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
'''
        (self.workspace / 'src' / 'service' / 'config.py').write_text(config_module, encoding='utf-8')
        
        # Create API directory first
        (self.workspace / 'src' / 'service' / 'api').mkdir(parents=True)
        
        # Health check endpoint
        health_endpoint = '''"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import asyncio

from ..database import get_db
from ..config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "user-service",
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check with dependency status."""
    settings = get_settings()
    
    health_status = {
        "status": "healthy",
        "service": "user-service",
        "version": "1.0.0",
        "dependencies": {}
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
        health_status["dependencies"]["database"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis (if configured)
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["redis"] = f"unhealthy: {str(e)}"
    
    return health_status


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, str]:
    """Kubernetes readiness probe endpoint."""
    try:
        # Check if we can connect to database
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        return {"status": "not ready"}


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}
'''
        (self.workspace / 'src' / 'service' / 'api' / 'health.py').write_text(health_endpoint, encoding='utf-8')
        
        # Requirements with microservice dependencies
        (self.workspace / 'requirements.txt').write_text("""fastapi>=0.100.0
uvicorn[standard]>=0.23.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
redis>=4.5.0
pika>=1.3.0
prometheus-client>=0.17.0
prometheus-fastapi-instrumentator>=6.1.0
pydantic[email]>=2.0.0
python-multipart>=0.0.6
pytest>=7.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
""", encoding='utf-8')
        
        # Steering files for microservice
        (self.workspace / '.kiro' / 'steering' / 'code-style.md').write_text("""# Microservice Code Style Guidelines

## Python Style

- Follow PEP 8 conventions
- Use type hints extensively
- Write comprehensive docstrings
- Use async/await for I/O operations
- Implement proper error handling

## Microservice Patterns

- Use dependency injection
- Implement circuit breakers for external calls
- Add comprehensive logging and monitoring
- Use structured logging (JSON format, encoding='utf-8')
- Implement health checks and readiness probes

## API Design

- Follow RESTful conventions
- Use proper HTTP status codes
- Implement API versioning
- Add request/response validation
- Include comprehensive OpenAPI documentation

## Testing

- Write unit tests for all business logic
- Include integration tests for API endpoints
- Test error conditions and edge cases
- Use test containers for database testing
- Implement contract testing for API consumers
""")


def get_sample_repositories() -> Dict[str, SampleRepository]:
    """Get all available sample repositories."""
    return {
        'python_library': PythonLibraryRepository(),
        'web_application': WebApplicationRepository(),
        'microservice': MicroserviceRepository()
    }