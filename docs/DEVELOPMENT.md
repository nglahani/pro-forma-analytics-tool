# Development Guide

This document provides comprehensive guidance for setting up and contributing to the Pro-Forma Analytics Tool development environment.

## 🛠️ Development Environment Setup

### Prerequisites

- **Python**: 3.8 or higher
- **Git**: Latest version
- **SQLite**: 3.30 or higher
- **IDE**: VS Code, PyCharm, or similar

### System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux

## 🚀 Local Development Setup

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone <repository-url>
cd pro-forma-analytics-tool

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Database Setup

```bash
# Initialize databases
python -m data.databases.database_manager init

# Verify database connections
python -m data.databases.database_manager test
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///data/databases/
MARKET_DATA_DB=data/databases/market_data.db
ECONOMIC_DATA_DB=data/databases/economic_data.db
PROPERTY_DATA_DB=data/databases/property_data.db
FORECAST_CACHE_DB=data/databases/forecast_cache.db

# API Configuration
API_HOST=localhost
API_PORT=8000
DEBUG=True

# External Services
MARKET_DATA_API_KEY=your_api_key_here
ECONOMIC_DATA_API_KEY=your_api_key_here
```

## 📁 Project Structure

```
pro-forma-analytics-tool/
├── src/                      # Source code
│   ├── core/                # Core business logic
│   │   ├── models/         # Data models
│   │   ├── services/       # Business services
│   │   └── utils/          # Utility functions
│   ├── api/                # API layer
│   │   ├── routes/         # API endpoints
│   │   ├── middleware/     # Middleware components
│   │   └── schemas/        # API schemas
│   ├── data/               # Data layer
│   │   ├── databases/      # Database management
│   │   ├── repositories/   # Data access layer
│   │   └── migrations/     # Database migrations
│   └── visualization/      # Data visualization
│       ├── charts/         # Chart components
│       └── dashboards/     # Dashboard components
├── tests/                   # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test data
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── config/                 # Configuration files
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src --cov-report=html

# Run performance tests
pytest tests/performance/
```

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Performance Tests**: Test system performance under load
- **API Tests**: Test API endpoints and responses

## 🔧 Code Quality

### Linting and Formatting

```bash
# Run linting
flake8 src/
black src/
isort src/

# Run type checking
mypy src/
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📊 Database Development

### Database Schema Management

```bash
# Generate new migration
python -m data.databases.migration_manager create_migration

# Apply migrations
python -m data.databases.migration_manager migrate

# Rollback migration
python -m data.databases.migration_manager rollback
```

### Database Seeding

```bash
# Seed development data
python -m data.databases.seed_manager seed_dev

# Seed test data
python -m data.databases.seed_manager seed_test
```

## 🚀 Running the Application

### Development Server

```bash
# Start development server
python -m src.main

# Start with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Development

```bash
# Build development image
docker build -f Dockerfile.dev -t pro-forma-dev .

# Run development container
docker-compose -f docker-compose.dev.yml up
```

## 🔍 Debugging

### VS Code Configuration

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "src.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 📦 Package Management

### Adding Dependencies

```bash
# Add production dependency
pip install package_name
pip freeze > requirements.txt

# Add development dependency
pip install package_name
pip freeze > requirements-dev.txt
```

### Dependency Management

- **requirements.txt**: Production dependencies
- **requirements-dev.txt**: Development dependencies
- **requirements-test.txt**: Testing dependencies

## 🔄 Git Workflow

### Branch Naming Convention

- `feature/feature-name`: New features
- `bugfix/bug-description`: Bug fixes
- `hotfix/urgent-fix`: Critical fixes
- `docs/documentation-update`: Documentation updates

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database file permissions
   ls -la data/databases/
   
   # Reinitialize database
   python -m data.databases.database_manager init
   ```

2. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   
   # Install missing dependencies
   pip install -r requirements.txt
   ```

3. **Test Failures**
   ```bash
   # Clear test cache
   pytest --cache-clear
   
   # Run tests with verbose output
   pytest -v
   ```

## 📚 Additional Resources

- [Python Documentation](https://docs.python.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Pytest Documentation](https://docs.pytest.org/)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## 📞 Support

For development-related questions:
- Create an issue on GitHub
- Contact the development team
- Check the troubleshooting section above