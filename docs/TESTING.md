# Testing & Quality Assurance

Complete testing strategy and implementation for Client Intelligence Monitor.

## Overview

The application now includes a comprehensive test suite with:

- **170+ test cases** across unit and integration tests
- **Test fixtures** with realistic sample data
- **Automated test runner** for convenience
- **Coverage reporting** to track test coverage
- **CI/CD ready** for automated testing pipelines

## Quick Start

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run Tests

```bash
# Run all tests
pytest

# Run fast tests only (skip slow tests)
python run_tests.py fast

# Run with coverage report
python run_tests.py coverage

# Run specific category
python run_tests.py unit        # Unit tests only
python run_tests.py integration  # Integration tests only
```

## Test Suite Structure

### Unit Tests (`tests/unit/`)

**test_models.py** - 40+ tests
- ClientDTO validation and operations
- EventDTO validation and operations
- SearchCacheDTO validation
- Edge cases and boundary conditions
- Unicode and special character handling

**test_storage.py** - 60+ tests
- Connection management
- Client CRUD operations
- Event CRUD operations
- Search and filtering
- Statistics and analytics
- Cascade deletes
- Transaction handling
- Data integrity

**test_collectors.py** - 20+ tests
- MockCollector functionality
- CollectorFactory patterns
- API response handling
- Fallback mechanisms

**test_processors.py** - 30+ tests
- Event classification accuracy
- Relevance scoring
- Deduplication logic
- Score boundary tests
- Similarity thresholds

### Integration Tests (`tests/integration/`)

**test_integration.py** - 20+ tests
- Complete client lifecycle
- Full event workflow
- Multi-client monitoring
- Search and filter workflows
- Error handling
- Performance with bulk data
- Data integrity across operations

## Test Fixtures

### Sample Data (`tests/fixtures/`)

**sample_clients.json**
- 3 diverse client companies
- Different industries and tiers
- Realistic metadata

**sample_events.json**
- 5 sample events across types
- Various relevance scores
- Different statuses and sentiments

**mock_api_responses.json**
- Google Search mock responses
- NewsAPI mock responses
- Error response scenarios

### Pytest Fixtures (`tests/conftest.py`)

**Data Loaders**
- `sample_clients_data` - Load clients from JSON
- `sample_events_data` - Load events from JSON
- `mock_api_responses` - Load API responses

**Model Fixtures**
- `sample_client_dto` - Single client instance
- `sample_event_dto` - Single event instance
- `multiple_client_dtos` - Multiple clients
- `multiple_event_dtos` - Multiple events

**Storage Fixtures**
- `temp_db_path` - Temporary database file
- `test_storage` - Empty test database
- `populated_storage` - Pre-populated database

**Factory Fixtures**
- `client_factory` - Create custom clients
- `event_factory` - Create custom events

## Running Tests

### Basic Commands

```bash
# All tests with verbose output
pytest -v

# Fast tests only (exclude slow tests)
pytest -m "not slow"

# Specific test file
pytest tests/unit/test_models.py

# Specific test class
pytest tests/unit/test_models.py::TestClientDTO

# Specific test function
pytest tests/unit/test_models.py::TestClientDTO::test_create_client_dto

# Tests matching keyword
pytest -k "validation"
```

### Using the Test Runner

```bash
# All tests
python run_tests.py all

# Unit tests only
python run_tests.py unit

# Integration tests only
python run_tests.py integration

# Fast tests (skip slow tests)
python run_tests.py fast

# With coverage report
python run_tests.py coverage

# Verbose output
python run_tests.py all -v

# Specific file
python run_tests.py -f tests/unit/test_models.py

# Keyword filter
python run_tests.py -k "client"
```

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (end-to-end)
- `@pytest.mark.database` - Tests using database
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.api` - Tests using external APIs
- `@pytest.mark.ui` - UI component tests

## Coverage Goals

### Current Status

- **Overall Coverage**: 80%+
- **Critical Paths**: 90%+
- **Models**: 95%+
- **Storage**: 90%+

### Generate Coverage Report

```bash
# HTML report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html

# Terminal report with missing lines
pytest --cov=src --cov-report=term-missing

# Fail if below threshold
pytest --cov=src --cov-fail-under=80
```

## Writing New Tests

### Test Template

```python
import pytest
from src.models import ClientDTO

@pytest.mark.unit
class TestNewFeature:
    """Tests for new feature."""

    def test_feature_works(self, test_storage):
        """Test that feature works correctly."""
        # Arrange
        client = ClientDTO(name="Test", ...)

        # Act
        result = test_storage.create_client(client)

        # Assert
        assert result is not None
        assert result.name == "Test"

    def test_feature_handles_errors(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            # Test error condition
            ...
```

### Best Practices

1. **One test, one behavior**: Each test should verify one specific behavior
2. **Clear names**: Use descriptive test names that explain what is being tested
3. **Arrange-Act-Assert**: Structure tests with clear setup, action, and verification
4. **Use fixtures**: Leverage existing fixtures for common setup
5. **Test edge cases**: Include boundary conditions and error scenarios
6. **Keep tests fast**: Mock external dependencies when possible

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements-test.txt

    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running fast tests before commit..."
pytest -m "not slow" -q

if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Commit aborted."
    exit 1
fi

echo "✅ Tests passed!"
```

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Solution: Install package in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database Lock**
```bash
# Solution: Clean up test databases
rm -f test_*.db *.db-journal

# Ensure fixtures properly disconnect
```

**Stale Python Cache**
```bash
# Solution: Clean cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

**Slow Tests**
```bash
# Solution: Run fast tests only
pytest -m "not slow"

# Or run tests in parallel
pytest -n auto  # Requires pytest-xdist
```

## Test Data Management

### Creating New Fixtures

```python
# In tests/conftest.py
@pytest.fixture
def my_custom_fixture():
    """Description of fixture."""
    # Setup code
    data = create_test_data()

    yield data

    # Teardown code (optional)
    cleanup(data)
```

### Using Factories

```python
def test_with_custom_data(client_factory, event_factory):
    """Test with customized data."""
    # Create custom client
    client = client_factory(
        name="Custom Corp",
        industry="Healthcare",
        priority="high"
    )

    # Create custom event
    event = event_factory(
        client_id=client.id,
        title="Custom Event",
        event_type="funding",
        relevance_score=0.95
    )

    # Use in test
    ...
```

## Performance Testing

### Bulk Operation Tests

```python
@pytest.mark.slow
def test_bulk_operations(test_storage, client_factory):
    """Test performance with many records."""
    # Create 1000 clients
    clients = [client_factory(id=f"bulk-{i}")
               for i in range(1000)]

    for client in clients:
        test_storage.create_client(client)

    # Verify performance
    import time
    start = time.time()
    all_clients = test_storage.get_all_clients()
    duration = time.time() - start

    assert len(all_clients) == 1000
    assert duration < 1.0  # Should complete in under 1 second
```

## Continuous Improvement

### Adding New Tests

1. Identify untested code paths
2. Write failing test first (TDD)
3. Implement feature
4. Verify test passes
5. Refactor if needed

### Maintaining Coverage

```bash
# Check coverage regularly
pytest --cov=src --cov-report=term-missing

# Identify gaps
# Write tests for uncovered code
# Verify improvement
```

## Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Testing Best Practices**: https://docs.python-guide.org/writing/tests/
- **Coverage Documentation**: https://coverage.readthedocs.io/
- **Project Tests README**: `tests/README.md`

---

**Last Updated**: 2025-10-15
**Test Suite Version**: 1.0.0
