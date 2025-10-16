# Badges and Status for Main README

Add these to the top of your main `README.md` to show test status:

## GitHub Actions Badge

```markdown
![CI](https://github.com/YOUR_USERNAME/playlist-transfer/workflows/CI/badge.svg)
```

Replace `YOUR_USERNAME` with your GitHub username.

## Codecov Badge (if you set it up)

```markdown
[![codecov](https://codecov.io/gh/YOUR_USERNAME/playlist-transfer/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/playlist-transfer)
```

## Full Example Header

```markdown
# Playlist Transfer

![CI](https://github.com/YOUR_USERNAME/playlist-transfer/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/playlist-transfer/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/playlist-transfer)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Transfer playlists between music streaming platforms.

## Features
- ✅ Transfer between Spotify and Tidal
- ✅ Smart track matching
- ✅ Detailed transfer logs
- ✅ 45 automated tests
- ✅ CI/CD pipeline
```

## Testing Section for Main README

Add this section to your main `README.md`:

```markdown
## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
make test-cov

# Run all CI checks
make ci
```

See [Testing Guide](TESTING.md) for more details.

### Code Quality

This project uses:
- **pytest** for testing
- **black** for code formatting
- **flake8** for linting
- **mypy** for type checking

All checks run automatically in CI.
```

## Quick Stats Badge

```markdown
![Tests](https://img.shields.io/badge/tests-45%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-85%25+-green)
```

---

**To use these:**
1. Copy the badges you want
2. Add them to the top of your main README.md
3. Replace `YOUR_USERNAME` with your GitHub username
4. Commit and push to see them in action!
