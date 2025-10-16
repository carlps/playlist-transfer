# Testing Setup Guide

This guide will help you set up and run the automated test suite for playlist-transfer.

## Quick Start

```bash
# 1. Install dev dependencies
pip install -e ".[dev]"

# 2. Run tests
pytest

# 3. Run tests with coverage
make test-cov

# 4. Run all CI checks locally
make ci
```

## Detailed Setup

### 1. Development Environment Setup

First, make sure you have Python 3.9+ installed:

```bash
python --version  # Should be 3.9 or higher
```

Install the package with development dependencies:

```bash
# From the project root directory
pip install -e ".[dev]"
```

This installs:
- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **black**: Code formatter
- **flake8**: Linter
- **mypy**: Type checker

### 2. Running Tests

#### Basic Test Run

```bash
pytest
```

#### With Coverage Report

```bash
pytest --cov=playlist_transfer --cov-report=html
# Open htmlcov/index.html in your browser
```

#### Verbose Output

```bash
pytest -v
```

#### Run Specific Tests

```bash
# Run a specific test file
pytest tests/test_models.py

# Run a specific test class
pytest tests/test_models.py::TestTrack

# Run a specific test
pytest tests/test_models.py::TestTrack::test_track_creation

# Run tests matching a pattern
pytest -k "track"
```

### 3. Using Make Commands

The project includes a Makefile with convenient shortcuts:

```bash
# Run tests with coverage
make test-cov

# Run linting
make lint

# Format code
make format

# Check formatting without changing files
make format-check

# Run type checking
make type-check

# Run all CI checks locally (recommended before pushing)
make ci

# Clean generated files
make clean
```

### 4. Code Quality Checks

#### Formatting with Black

Black automatically formats your code:

```bash
# Check if code is formatted correctly
black --check playlist_transfer tests

# Format code
black playlist_transfer tests
```

#### Linting with Flake8

Flake8 checks for code style issues and potential errors:

```bash
flake8 playlist_transfer tests
```

Common issues:
- Unused imports
- Undefined variables
- Lines too long (>100 chars)
- Unused variables

#### Type Checking with Mypy

Mypy checks type hints:

```bash
mypy playlist_transfer --ignore-missing-imports
```

Note: Type checking is currently advisory (won't fail CI).

### 5. Pre-Commit Checks

Before committing code, run:

```bash
make ci
```

This runs all checks that will run in CI:
- ✅ Code formatting
- ✅ Linting
- ✅ Type checking
- ✅ Tests with coverage

### 6. Understanding Test Output

#### Successful Test Run

```
tests/test_models.py ............                     [100%]

====== 12 passed in 0.45s ======
```

#### Failed Test

```
FAILED tests/test_models.py::TestTrack::test_track_creation - AssertionError
```

Look for the failure details in the output to understand what went wrong.

#### Coverage Report

```
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
playlist_transfer/__init__.py                 0      0   100%
playlist_transfer/models.py                  45      2    96%   67-68
playlist_transfer/playlist_transfer.py       89      5    94%   45, 89-92
-----------------------------------------------------------------------
TOTAL                                       134      7    95%
```

- **Stmts**: Total statements
- **Miss**: Uncovered statements
- **Cover**: Coverage percentage
- **Missing**: Line numbers not covered

### 7. Writing New Tests

When adding new features:

1. **Create a test file** in `tests/` named `test_<module>.py`
2. **Import necessary fixtures** from `conftest.py`
3. **Write test functions** starting with `test_`
4. **Use descriptive names** that explain what's being tested
5. **Follow the Arrange-Act-Assert pattern**:

```python
def test_my_feature(mock_source_service):
    """Test that my feature works correctly"""
    # Arrange: Set up test data
    service = mock_source_service
    
    # Act: Execute the code being tested
    result = service.my_method()
    
    # Assert: Verify the result
    assert result == expected_value
```

### 8. Continuous Integration

The project uses GitHub Actions for CI. Tests run automatically on:

- Every push to `main` or `develop`
- Every pull request
- Multiple Python versions (3.9, 3.10, 3.11, 3.12)
- Multiple OSes (Ubuntu, macOS, Windows)

View the workflow in `.github/workflows/ci.yml`.

### 9. Troubleshooting

#### Tests Pass Locally But Fail in CI

- Check if you're using environment-specific behavior
- Ensure all dependencies are in `pyproject.toml`
- Check if tests depend on local files

#### Coverage is Lower Than Expected

- Look for branches not covered (if/else statements)
- Check for exception handlers not tested
- Review the HTML coverage report for details

#### Linting Errors

Common fixes:
- **Unused imports**: Remove them or use them
- **Line too long**: Break into multiple lines
- **Undefined name**: Import the missing module/function
- **Trailing whitespace**: Run `black` to auto-fix

#### Import Errors

If you get import errors when running tests:

```bash
# Reinstall in editable mode
pip install -e .

# Or reinstall with dev dependencies
pip install -e ".[dev]"
```

#### Mock Service Not Working

If `MockMusicService` isn't behaving as expected:
- Check that you're calling `authenticate()` before other methods
- Verify you're using the correct fixture (`mock_source_service` vs `mock_destination_service`)
- Set `search_results` dict to customize search behavior

### 10. Test Markers

You can mark tests for selective running:

```python
import pytest

@pytest.mark.unit
def test_something():
    pass

@pytest.mark.slow
def test_long_running():
    pass
```

Run specific markers:

```bash
pytest -m unit      # Run only unit tests
pytest -m "not slow"  # Skip slow tests
```

### 11. Debugging Tests

#### Using Print Statements

```bash
pytest -s  # Don't capture output, show prints
```

#### Using Python Debugger

```python
def test_something():
    import pdb; pdb.set_trace()  # Breakpoint
    result = my_function()
    assert result == expected
```

#### Using pytest's Built-in Debugger

```bash
pytest --pdb  # Drop into debugger on failures
```

### 12. Performance

Keep tests fast:
- Use mocks instead of real API calls
- Avoid `time.sleep()` in tests
- Use fixtures to share setup between tests
- Run expensive tests with `@pytest.mark.slow`

### 13. Best Practices

✅ **DO**:
- Write tests for new features before implementing them (TDD)
- Keep tests independent (don't rely on test order)
- Use descriptive test names
- Test edge cases and error conditions
- Mock external dependencies
- Keep tests fast

❌ **DON'T**:
- Make tests depend on each other
- Test implementation details (test behavior instead)
- Use real API credentials in tests
- Commit `.env` or `config.json` files
- Skip writing tests for "simple" code

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Black documentation](https://black.readthedocs.io/)
- [Flake8 documentation](https://flake8.pycqa.org/)

## Getting Help

If you encounter issues:
1. Check this guide
2. Review the test examples in `tests/`
3. Look at the CI logs in GitHub Actions
4. Ask for help in a GitHub issue
