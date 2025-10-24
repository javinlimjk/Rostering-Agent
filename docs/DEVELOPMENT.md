# Development Guide

## Project Structure

```
rostering-agent/
├── src/
│   ├── optimization/          # OR-Tools shift scheduling
│   │   ├── __init__.py
│   │   └── scheduler.py       # ShiftOptimizer class
│   ├── compliance/            # RAG-based compliance checking
│   │   ├── __init__.py
│   │   └── checker.py         # ComplianceChecker class
│   ├── api/                   # FastAPI application
│   │   ├── __init__.py
│   │   └── main.py            # API endpoints
│   ├── dashboard/             # Streamlit UI
│   │   ├── __init__.py
│   │   └── app.py             # Dashboard application
│   ├── tracking/              # MLflow integration
│   │   ├── __init__.py
│   │   └── mlflow_tracker.py  # ExperimentTracker class
│   └── __init__.py
├── data/
│   ├── labour_laws/           # Labour law documents
│   │   ├── US.txt
│   │   ├── UK.txt
│   │   ├── SG.txt
│   │   ├── DE.txt
│   │   └── JP.txt
│   └── sample/                # Sample data
│       ├── workers.json
│       └── requirements.json
├── config/
│   └── config.yaml            # Main configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_optimization.py
│   └── test_api.py
├── scripts/                   # Utility scripts
│   ├── start_mlflow.sh
│   ├── start_api.sh
│   ├── start_dashboard.sh
│   └── start_all.sh
├── docs/                      # Documentation
│   ├── API.md
│   └── DEVELOPMENT.md
├── main.py                    # CLI entry point
├── setup.py                   # Package setup
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── .gitignore
└── README.md
```

## Key Components

### 1. Optimization Module (`src/optimization/`)

The optimization module uses OR-Tools CP-SAT solver to create optimal shift schedules.

**Key Class: `ShiftOptimizer`**

```python
optimizer = ShiftOptimizer()
result = optimizer.optimize_schedule(workers, num_days, shift_requirements)
```

**Constraints implemented:**
- Worker skills matching shift requirements
- Maximum shifts per worker
- Maximum consecutive working days
- Unavailable days
- Country-specific labour law limits
- Balanced workload distribution

### 2. Compliance Module (`src/compliance/`)

The compliance module uses RAG (Retrieval Augmented Generation) for intelligent labour law checking.

**Key Class: `ComplianceChecker`**

```python
checker = ComplianceChecker()
result = checker.check_compliance(schedule, workers)
```

**Features:**
- LangChain + Chroma vector database
- Labour law document indexing
- Semantic search for relevant regulations
- Rule-based fallback when RAG unavailable

### 3. API Module (`src/api/`)

FastAPI-based REST API for programmatic access.

**Key Endpoints:**
- POST `/optimize` - Generate optimal schedule
- POST `/validate` - Validate schedule compliance
- GET `/labour-laws/{country}` - Query labour laws

### 4. Dashboard Module (`src/dashboard/`)

Streamlit-based interactive dashboard.

**Features:**
- Visual schedule configuration
- Real-time optimization
- Schedule visualization
- Analytics and charts

### 5. Tracking Module (`src/tracking/`)

MLflow integration for experiment tracking.

**Key Class: `ExperimentTracker`**

```python
tracker = ExperimentTracker()
run_id = tracker.log_optimization_run(params, result)
```

## Development Setup

### 1. Install Development Dependencies

```bash
pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

### 2. Code Style

We use Black for code formatting and Flake8 for linting:

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/ --max-line-length=100

# Type checking
mypy src/
```

### 3. Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_optimization.py::test_optimizer_initialization -v
```

### 4. Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up git hooks
pre-commit install
```

## Adding New Features

### Adding a New Country

1. **Create labour law document:**
   ```bash
   touch data/labour_laws/FR.txt
   ```

2. **Add content to the document:**
   ```
   France Labour Laws:
   
   1. Working Hours:
      - Maximum 35 hours per week
      ...
   ```

3. **Update config:**
   ```yaml
   countries:
     FR:
       name: "France"
       max_hours_per_week: 35
       max_consecutive_days: 6
       min_rest_hours: 11
   ```

4. **Rebuild Chroma database:**
   ```bash
   rm -rf chroma_db/
   # Restart services to rebuild
   ```

### Adding New Constraints

Edit `src/optimization/scheduler.py`:

```python
# Add constraint after existing ones
# Constraint N: Your new constraint
for w in range(num_workers):
    # Your constraint logic here
    self.model.Add(...)
```

### Extending the API

Add new endpoint in `src/api/main.py`:

```python
@app.get("/your-endpoint")
async def your_function():
    # Your logic here
    return {"result": "data"}
```

## Testing Guidelines

### Unit Tests

Test individual components:

```python
def test_optimizer_initialization():
    optimizer = ShiftOptimizer()
    assert optimizer is not None
```

### Integration Tests

Test component interactions:

```python
def test_full_optimization_flow(sample_workers, shift_requirements):
    optimizer = ShiftOptimizer()
    result = optimizer.optimize_schedule(...)
    checker = ComplianceChecker()
    validation = checker.check_compliance(...)
    assert validation['overall_compliant']
```

### API Tests

Test API endpoints:

```python
def test_optimize_endpoint():
    response = client.post("/optimize", json=payload)
    assert response.status_code == 200
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### MLflow Tracking Issues

```bash
# Check MLflow server logs
tail -f logs/mlflow.log

# Reset MLflow database
rm mlflow.db
rm -rf mlruns/
```

### Optimization Issues

```python
# Increase solver time limit
# In config/config.yaml:
optimization:
  solver_time_limit_seconds: 600  # Increase from 300

# Enable verbose logging in CP-SAT
self.solver.parameters.log_search_progress = True
```

## Performance Optimization

### 1. Solver Performance

- Adjust `solver_time_limit_seconds` based on problem size
- Use `num_workers` and `num_days` constraints wisely
- Consider breaking large problems into smaller chunks

### 2. RAG Performance

- Chroma database is persistent; first load is slow
- Consider batch processing for multiple queries
- Cache frequently accessed labour law information

### 3. API Performance

- Use async endpoints where possible
- Consider caching optimization results
- Use connection pooling for database access

## Continuous Integration

Example GitHub Actions workflow:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=src
      - name: Lint
        run: flake8 src/ tests/
```

## Documentation

- API docs auto-generated via FastAPI at `/docs`
- Keep README.md updated with user-facing changes
- Update this guide for development changes
- Add docstrings to all public functions

## Release Process

1. Update version in `setup.py` and `src/__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create git tag: `git tag v1.0.0`
5. Push tag: `git push origin v1.0.0`
6. Build package: `python setup.py sdist bdist_wheel`
