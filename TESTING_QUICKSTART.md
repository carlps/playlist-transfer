# Quick Start: Testing

## Setup (One Time)

```bash
# Install development dependencies
pip install -e ".[dev]"
```

## Daily Workflow

### Before You Start Coding

```bash
# Make sure tests pass
pytest
```

### While Coding

```bash
# Run tests for the module you're working on
pytest tests/test_models.py -v

# Run tests matching a pattern
pytest -k "track" -v
```

### Before Committing

```bash
# Run all CI checks
make ci
```

This will:
1. ✅ Check code formatting
2. ✅ Run linting
3. ✅ Run type checking
4. ✅ Run all tests with coverage

If anything fails, fix it before committing!

### Quick Commands

```bash
make test          # Run tests
make test-cov      # Run tests with coverage report
make lint          # Check code style
make format        # Auto-format code
make clean         # Clean up generated files
```

## Common Tasks

### Run specific test

```bash
pytest tests/test_models.py::TestTrack::test_track_creation
```

### Run tests with output

```bash
pytest -s -v
```

### Check coverage

```bash
make test-cov
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Format your code

```bash
make format
```

### Fix linting issues

Most issues can be auto-fixed:
```bash
black playlist_transfer tests
```

For manual fixes, run:
```bash
flake8 playlist_transfer tests
```

## What Gets Tested in CI?

Every push and PR runs:
- ✅ Tests on Python 3.8, 3.9, 3.10, 3.11, 3.12
- ✅ Tests on Ubuntu, macOS, Windows
- ✅ Code formatting check
- ✅ Linting
- ✅ Type checking
- ✅ Coverage reporting

## Need More Help?

See `TESTING.md` for detailed documentation.
