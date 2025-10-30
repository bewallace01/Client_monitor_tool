# Test Suite Documentation

Comprehensive testing documentation for the Client Intelligence Monitor application.

## Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Fixtures](#fixtures)
6. [Writing Tests](#writing-tests)
7. [CI/CD Integration](#cicd-integration)

## Overview

This test suite provides comprehensive coverage of the Client Intelligence Monitor application, including:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows end-to-end
- **Fixtures**: Reusable test data and mocks

### Test Statistics

- **Total Test Files**: 6+
- **Test Categories**: Unit, Integration, Slow, Database, API, UI
- **Coverage Goal**: 80%+

## Test Structure

```
tests/
├── __init__.py                 # Package initialization
├── conftest.py                 # Shared pytest fixtures
├── pytest.ini                  # Pytest configuration (in project root)
│
├── fixtures/                   # Test data
│   ├── sample_clients.json    # Sample client data
│   ├── sample_events.json     # Sample event data
│   └── mock_api_responses.json # Mock API responses
│
├── unit/                       # Unit tests
│   ├── test_models.py         # DTO model tests
│   ├── test_storage.py        # Database operation tests
│   ├── test_collectors.py     # Collector tests
│   └── test_processors.py     # Processor tests (classifier, scorer, dedup)
│
└── integration/                # Integration tests
    └── test_integration.py    # End-to-end workflow tests
```

## Running Tests

### Prerequisites

```bash
# Install pytest and dependencies
pip install pytest pytest-cov

# Install application dependencies
pip install -r requirements.txt
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only database tests
pytest -m database

# Exclude slow tests
pytest -m "not slow"
```

### Run Specific Test Files

```bash
# Run model tests
pytest tests/unit/test_models.py

# Run storage tests
pytest tests/unit/test_storage.py

# Run integration tests
pytest tests/integration/test_integration.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/unit/test_models.py::TestClientDTO

# Run a specific test function
pytest tests/unit/test_models.py::TestClientDTO::test_create_client_dto

# Run tests matching a pattern
pytest -k "client"
```

## Test Categories

Tests are organized using pytest markers:

### Unit Tests (`@pytest.mark.unit`)

Test individual components in isolation:

- **Models**: DTO validation, serialization
- **Storage**: CRUD operations
- **Collectors**: Mock and factory patterns
- **Processors**: Classification, scoring, deduplication

```python
@pytest.mark.unit
def test_client_dto_validation():
    client = ClientDTO(name="Test", ...)
    is_valid, error = client.validate()
    assert is_valid is True
```

### Integration Tests (`@pytest.mark.integration`)

Test complete workflows:

- Client lifecycle (create, update, delete)
- Event processing pipeline
- Multi-client monitoring
- Search and filtering

```python
@pytest.mark.integration
def test_full_event_workflow(test_storage):
    # Test complete workflow
    ...
```

### Database Tests (`@pytest.mark.database`)

Tests that interact with database:

- Connection management
- Schema initialization
- CRUD operations
- Transactions

```python
@pytest.mark.database
def test_storage_connection(test_storage):
    assert test_storage.is_connected() is True
```

### Slow Tests (`@pytest.mark.slow`)

Tests that take longer to run:

- Bulk operations
- Performance tests
- Large dataset handling

```python
@pytest.mark.slow
def test_bulk_operations():
    # Test with 1000+ records
    ...
```

## Fixtures

Pytest fixtures provide reusable test data and setup.

### Data Loading Fixtures

```python
# Load sample clients from JSON
def test_with_clients(sample_clients_data):
    assert len(sample_clients_data) >= 3

# Load sample events from JSON
def test_with_events(sample_events_data):
    assert len(sample_events_data) >= 5
```

### Model Fixtures

```python
# Single client DTO
def test_with_client(sample_client_dto):
    assert sample_client_dto.name == "Test Company"

# Single event DTO
def test_with_event(sample_event_dto):
    assert sample_event_dto.event_type == "funding"

# Multiple DTOs from fixtures
def test_with_multiple(multiple_client_dtos, multiple_event_dtos):
    assert len(multiple_client_dtos) >= 3
```

### Storage Fixtures

```python
# Empty test database
def test_with_storage(test_storage):
    # Fresh database for each test
    ...

# Pre-populated database
def test_with_data(populated_storage):
    # Database with clients and events
    ...
```

### Factory Fixtures

```python
# Create custom clients
def test_custom_client(client_factory):
    client = client_factory(
        name="Custom Name",
        industry="Finance"
    )
    assert client.industry == "Finance"

# Create custom events
def test_custom_event(event_factory):
    event = event_factory(
        title="Custom Event",
        event_type="funding"
    )
    assert event.event_type == "funding"
```

## Writing Tests

### Test Naming Conventions

```python
# ✅ Good test names
def test_create_client_with_valid_data():
    ...

def test_client_validation_fails_with_empty_name():
    ...

def test_event_scoring_considers_recency():
    ...

# ❌ Bad test names
def test_1():
    ...

def test_client():
    ...
```

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_update_client(test_storage, client_factory):
    # Arrange: Set up test data
    client = client_factory(name="Original Name")
    test_storage.create_client(client)

    # Act: Perform the action
    updated = test_storage.update_client(
        client.id,
        {"name": "New Name"}
    )

    # Assert: Verify the results
    assert updated.name == "New Name"
```

### Using Fixtures

```python
# Request fixtures as function parameters
def test_with_fixtures(test_storage, sample_client_dto):
    # Fixtures are automatically injected
    created = test_storage.create_client(sample_client_dto)
    assert created is not None
```

### Testing Exceptions

```python
def test_invalid_data_raises_error(test_storage):
    invalid_client = ClientDTO(name="")  # Invalid

    with pytest.raises(ValueError):
        test_storage.create_client(invalid_client)
```

### Parameterized Tests

```python
@pytest.mark.parametrize("priority,valid", [
    ("low", True),
    ("medium", True),
    ("high", True),
    ("invalid", False),
])
def test_priority_validation(client_factory, priority, valid):
    client = client_factory(priority=priority)
    is_valid, _ = client.validate()
    assert is_valid == valid
```

## Best Practices

### 1. Test Isolation

Each test should be independent:

```python
# ✅ Good: Independent tests
def test_create_client(test_storage):
    # Uses fresh test_storage fixture
    ...

def test_update_client(test_storage):
    # Uses fresh test_storage fixture
    ...

# ❌ Bad: Tests depend on each other
client_id = None

def test_create_client(test_storage):
    global client_id
    client = test_storage.create_client(...)
    client_id = client.id

def test_update_client(test_storage):
    global client_id
    test_storage.update_client(client_id, ...)  # Depends on previous test
```

### 2. Clear Assertions

```python
# ✅ Good: Clear assertion with message
assert len(results) == 3, f"Expected 3 results, got {len(results)}"

# ✅ Good: Multiple specific assertions
assert client.name == "Test Company"
assert client.industry == "Technology"
assert client.is_active is True

# ❌ Bad: Vague assertion
assert client  # What are we checking?
```

### 3. Test One Thing

```python
# ✅ Good: Tests one behavior
def test_client_creation():
    client = create_client(...)
    assert client.id is not None

def test_client_validation():
    is_valid = validate_client(...)
    assert is_valid is True

# ❌ Bad: Tests multiple things
def test_client_stuff():
    client = create_client(...)
    assert client.id is not None
    validate_client(...)
    assert is_valid is True
    update_client(...)
    # Too much in one test!
```

### 4. Use Descriptive Names

```python
# ✅ Good: Describes what and why
def test_relevance_score_increases_for_recent_events():
    ...

# ❌ Bad: Unclear purpose
def test_score():
    ...
```

## CI/CD Integration

### GitHub Actions Example

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
        pip install -r requirements.txt
        pip install pytest pytest-cov

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

echo "Running tests..."
pytest -m "not slow"

if [ $? -ne 0 ]; then
    echo "Tests failed! Commit aborted."
    exit 1
fi
```

## Coverage Reports

### Generate HTML Coverage Report

```bash
pytest --cov=src --cov-report=html

# Open htmlcov/index.html in browser
```

### Coverage Goals

- **Overall**: 80%+
- **Critical Paths**: 90%+
- **Models**: 95%+
- **Storage**: 90%+

### Check Coverage

```bash
# Show missing lines
pytest --cov=src --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80
```

## Troubleshooting

### Tests Failing Locally

```bash
# Clean Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Lock Issues

```bash
# Tests leave database locked
# Solution: Ensure fixtures properly clean up

# Or manually remove test databases
rm -f test_*.db
```

### Import Errors

```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install package in development mode
pip install -e .
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

**Last Updated**: 2025-10-15
**Version**: 1.0.0
