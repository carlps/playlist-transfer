# Test Suite

This directory contains the automated test suite for the playlist-transfer project.

## Running Tests

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=playlist_transfer --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see the coverage report.

### Run Specific Test Files

```bash
pytest tests/test_models.py
pytest tests/test_playlist_transfer.py
pytest tests/test_main.py
```

### Run Tests Matching a Pattern

```bash
pytest -k "test_track"  # Run all tests with "track" in the name
```

### Run Tests with Verbose Output

```bash
pytest -v
```

## Test Structure

- **conftest.py**: Shared fixtures and test utilities
  - `MockMusicService`: Mock implementation for testing without API calls
  - Various fixtures for common test data (tracks, playlists)

- **test_models.py**: Tests for Track and Playlist data models
  - Track creation and string representation
  - Feature removal from track titles
  - Playlist creation and visibility

- **test_playlist_transfer.py**: Tests for the main PlaylistTransfer class
  - Successful transfers
  - Error handling (authentication failures, missing tracks)
  - CSV log file generation
  - Edge cases (empty playlists, tracks not found)

- **test_main.py**: Tests for CLI functionality
  - Configuration file loading
  - Environment variable handling
  - Credential priority (CLI > env > config)
  - Template expansion

## Test Coverage Goals

We aim for >85% code coverage. Areas intentionally not covered:

- OAuth browser flows (requires manual interaction)
- Actual API calls to Spotify/Tidal (mocked instead)

## Writing New Tests

When adding new features:

1. Add unit tests for new functions/methods
2. Add integration tests for new workflows
3. Update fixtures in `conftest.py` if needed
4. Ensure tests are isolated (use mocks for external services)

Example test structure:

```python
def test_my_feature(mock_source_service):
    """Test description"""
    # Arrange
    service = mock_source_service
    
    # Act
    result = service.my_method()
    
    # Assert
    assert result == expected_value
```

## Continuous Integration

Tests run automatically on:
- Every push to `main` or `develop` branches
- Every pull request
- Multiple Python versions (3.8-3.12)
- Multiple operating systems (Ubuntu, macOS, Windows)

See `.github/workflows/ci.yml` for CI configuration.

## Linting and Formatting

The CI also checks:
- **flake8**: Code style and potential errors
- **black**: Code formatting
- **mypy**: Type checking (currently advisory)

Run locally:

```bash
# Check formatting
black --check playlist_transfer tests

# Format code
black playlist_transfer tests

# Lint
flake8 playlist_transfer tests

# Type check
mypy playlist_transfer --ignore-missing-imports
```
