# Contributing Guide

Thank you for your interest in contributing to the Pro-Forma Analytics Tool! This document provides guidelines and information for contributors.

## How to Contribute
- Data integration (API ingestion scripts)
- Database schema design and improvements
- Analytics and reporting scripts

## Not Yet Ready
- Web dashboard
- REST API endpoints
- Cloud deployment

## Roadmap
As the project matures, contributions to web/API features will be welcomed. For now, focus on data and analytics.

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/your-username/pro-forma-analytics-tool.git
cd pro-forma-analytics-tool

# Add the original repository as upstream
git remote add upstream https://github.com/original-owner/pro-forma-analytics-tool.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Branch

```bash
# Create a new branch for your work
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

## 📝 Development Workflow

### Code Style Guidelines

We follow these coding standards:

- **Python**: PEP 8 with Black formatting
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Follow Google docstring format
- **Comments**: Write clear, concise comments

### Example Code Style

```python
from typing import Optional, List, Dict
from datetime import date
from decimal import Decimal


def calculate_irr(cash_flows: List[Dict[str, float]], 
                  precision: int = 4) -> Optional[float]:
    """
    Calculate the Internal Rate of Return (IRR) for a series of cash flows.
    
    Args:
        cash_flows: List of dictionaries containing cash flow data.
                   Each dict should have 'amount' and 'date' keys.
        precision: Number of decimal places for IRR calculation.
    
    Returns:
        IRR as a decimal, or None if calculation fails.
    
    Raises:
        ValueError: If cash flows are invalid.
    
    Example:
        >>> cash_flows = [
        ...     {'amount': -1000000, 'date': '2024-01-01'},
        ...     {'amount': 500000, 'date': '2025-01-01'}
        ... ]
        >>> calculate_irr(cash_flows)
        0.5
    """
    if not cash_flows:
        raise ValueError("Cash flows cannot be empty")
    
    # Implementation here
    pass
```

### Testing Guidelines

- **Unit Tests**: Write tests for all new functions
- **Integration Tests**: Test component interactions
- **Test Coverage**: Aim for 80%+ coverage
- **Test Naming**: Use descriptive test names

```python
# tests/test_financial_calculations.py
import pytest
from decimal import Decimal
from src.core.calculations import calculate_irr


class TestIRRCalculation:
    """Test cases for IRR calculation functionality."""
    
    def test_irr_with_positive_cash_flows(self):
        """Test IRR calculation with positive cash flows."""
        cash_flows = [
            {'amount': -1000000, 'date': '2024-01-01'},
            {'amount': 500000, 'date': '2025-01-01'},
            {'amount': 600000, 'date': '2026-01-01'}
        ]
        
        result = calculate_irr(cash_flows)
        
        assert result is not None
        assert 0.1 < result < 0.3  # Reasonable IRR range
    
    def test_irr_with_empty_cash_flows(self):
        """Test IRR calculation with empty cash flows."""
        with pytest.raises(ValueError, match="Cash flows cannot be empty"):
            calculate_irr([])
    
    def test_irr_with_invalid_data(self):
        """Test IRR calculation with invalid data."""
        cash_flows = [{'amount': 'invalid', 'date': '2024-01-01'}]
        
        with pytest.raises(ValueError):
            calculate_irr(cash_flows)
```

## 🔄 Pull Request Process

### 1. Prepare Your Changes

```bash
# Make your changes
# Run tests
pytest tests/

# Run linting
flake8 src/
black src/
isort src/

# Check type hints
mypy src/
```

### 2. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat(analysis): add IRR calculation with precision support

- Add calculate_irr function with configurable precision
- Include comprehensive error handling
- Add unit tests with 95% coverage
- Update documentation with examples

Closes #123"
```

### 3. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### 4. Pull Request Guidelines

**Title Format:**
```
type(scope): brief description

Examples:
- feat(analysis): add IRR calculation
- fix(api): resolve database connection timeout
- docs(readme): update installation instructions
- test(calculations): add comprehensive IRR tests
```

**Description Template:**
```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows the style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation made
- [ ] No new warnings generated
- [ ] Tests added that prove fix is effective or feature works

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Additional Notes
Any additional information or context.
```

## 🐛 Bug Reports

### Bug Report Template

```markdown
## Bug Description
Clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g. Ubuntu 22.04]
- Python Version: [e.g. 3.11.0]
- Package Version: [e.g. 1.0.0]

## Additional Context
Any other context about the problem.
```

## ✨ Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear and concise description of the feature.

## Problem Statement
What problem does this feature solve?

## Proposed Solution
Describe the solution you'd like to see.

## Alternative Solutions
Describe any alternative solutions you've considered.

## Additional Context
Any other context, screenshots, or examples.
```

## 📊 Data Contributions

### Market Data Guidelines

If you're contributing market data:

1. **Data Quality**: Ensure data is accurate and from reliable sources
2. **Format**: Follow the established data format
3. **Documentation**: Include source and methodology
4. **Validation**: Provide validation scripts if applicable

### Data Format Example

```python
# market_data_example.py
market_data = {
    "date": "2024-01-15",
    "market_area": "NYC",
    "data_type": "cap_rate",
    "value": 0.045,
    "source": "CBRE",
    "confidence": 0.95,
    "notes": "Q4 2023 average cap rate for Class A multifamily"
}
```

## 🧪 Testing Contributions

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_financial_calculations.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run performance tests
pytest tests/performance/
```

### Writing Tests

```python
# Example test structure
def test_function_name_scenario():
    """Test description."""
    # Arrange
    input_data = {...}
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

## 📚 Documentation Contributions

### Documentation Guidelines

- **Clarity**: Write clear, concise documentation
- **Examples**: Include practical examples
- **Accuracy**: Ensure information is up-to-date
- **Structure**: Follow established documentation structure

### Documentation Types

1. **API Documentation**: Update API.md for new endpoints
2. **Code Comments**: Add docstrings to new functions
3. **User Guides**: Create tutorials and how-to guides
4. **Technical Docs**: Update technical documentation

## 🎨 UI/UX Contributions

### Design Guidelines

- **Consistency**: Follow established design patterns
- **Accessibility**: Ensure accessibility standards are met
- **Responsiveness**: Design for multiple screen sizes
- **Performance**: Optimize for speed and efficiency

### UI Components

```javascript
// Example React component
import React from 'react';

const ProFormaChart = ({ data, options }) => {
  return (
    <div className="pro-forma-chart">
      {/* Chart implementation */}
    </div>
  );
};

export default ProFormaChart;
```

## 🔍 Code Review Process

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Error handling is appropriate

### Review Comments

When reviewing code, be constructive and specific:

```markdown
Good: "Consider using a more descriptive variable name here, like 'monthly_cash_flow' instead of 'mcf'."

Better: "The variable name 'mcf' is unclear. Consider renaming it to 'monthly_cash_flow' to improve readability."
```

## 🏷️ Issue Labels

We use the following labels to categorize issues:

- **bug**: Something isn't working
- **enhancement**: New feature or request
- **documentation**: Improvements or additions to documentation
- **good first issue**: Good for newcomers
- **help wanted**: Extra attention is needed
- **priority: high**: High priority issue
- **priority: low**: Low priority issue
- **priority: medium**: Medium priority issue

## 🏆 Recognition

### Contributors Hall of Fame

We recognize contributors in several ways:

1. **GitHub Contributors**: All contributors appear in the repository contributors list
2. **Release Notes**: Contributors are credited in release notes
3. **Documentation**: Contributors are listed in the documentation
4. **Special Recognition**: Outstanding contributions receive special recognition

### Contribution Levels

- **Bronze**: 1-5 contributions
- **Silver**: 6-15 contributions
- **Gold**: 16+ contributions
- **Platinum**: Major contributions or project leadership

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: For sensitive or private matters
- **Community Forum**: For user support and questions

### Mentorship Program

New contributors can request mentorship:

1. Open an issue with the "mentorship" label
2. Describe what you'd like to work on
3. A maintainer will be assigned to help you

## 📋 Contributor Agreement

By contributing to this project, you agree to:

1. **License**: Your contributions will be licensed under the MIT License
2. **Code of Conduct**: Follow the project's Code of Conduct
3. **Quality**: Maintain high code quality and testing standards
4. **Documentation**: Update documentation as needed

## 🚀 Quick Start for New Contributors

1. **Pick an Issue**: Look for issues labeled "good first issue"
2. **Set Up Environment**: Follow the development setup guide
3. **Make Changes**: Implement your solution
4. **Test**: Ensure all tests pass
5. **Submit**: Create a pull request

## 📈 Contribution Metrics

We track and celebrate contributions:

- **Lines of Code**: Total lines contributed
- **Issues Closed**: Number of issues resolved
- **Pull Requests**: Number of PRs merged
- **Documentation**: Documentation improvements
- **Community**: Community engagement and support

## 🙏 Thank You

Thank you for contributing to the Pro-Forma Analytics Tool! Your contributions help make this project better for everyone in the real estate investment community.

---

**Remember**: Every contribution, no matter how small, makes a difference. Whether you're fixing a typo, adding a feature, or helping others, you're helping to build something valuable for the community.