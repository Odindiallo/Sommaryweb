# Contributing Guide

Thank you for considering contributing to the Documentation Management System! This guide will help you get started.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/documentation-system.git
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Style

We follow the PEP 8 style guide for Python code. Key points:

1. Use 4 spaces for indentation
2. Maximum line length is 79 characters
3. Use meaningful variable and function names
4. Write docstrings for all public modules, functions, classes, and methods

Example:
```python
def calculate_total(items):
    """
    Calculate the total value of all items.

    Args:
        items (list): List of items with 'price' attribute

    Returns:
        float: Total value of all items
    """
    return sum(item.price for item in items)
```

## Testing

1. Write tests for all new features
2. Ensure all tests pass before submitting:
   ```bash
   python manage.py test
   ```
3. Aim for high test coverage

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure CI passes
4. Update CHANGELOG.md
5. Request review from maintainers

## Commit Messages

Follow conventional commits:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance tasks

Example:
```
feat: Add document version control

- Add version history table
- Implement diff viewing
- Add restore functionality
```

## Documentation

1. Update README.md if needed
2. Add API documentation for new endpoints
3. Include examples in docstrings
4. Update installation guide if needed

## Code Review

We use a collaborative code review process:
1. Be respectful and constructive
2. Focus on code, not the author
3. Explain your reasoning
4. Suggest improvements

## Development Workflow

1. Create feature branch
2. Write tests
3. Implement feature
4. Update documentation
5. Submit pull request
6. Address review feedback
7. Merge when approved

## Getting Help

- Open an issue for bugs
- Join our community chat
- Check existing documentation
- Contact maintainers
