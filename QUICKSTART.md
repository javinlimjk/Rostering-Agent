# Quick Start Guide

Get started with the AI-Driven Rostering Agent in 5 minutes!

## 1. Installation

```bash
# Clone the repository
git clone https://github.com/javinlimjk/Rostering-Agent.git
cd Rostering-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Run Example

The fastest way to see the system in action:

```bash
python example_usage.py
```

This will:
- Load sample workers and requirements
- Optimize a 14-day schedule
- Validate labour law compliance
- Show detailed statistics
- Save the schedule to `example_schedule.json`

## 3. Start the Web Dashboard

```bash
# Option 1: Start services individually in separate terminals
streamlit run src/dashboard/app.py

# Option 2: Use Python main module
python main.py dashboard
```

Then open http://localhost:8501 in your browser.

## 4. Start the API

```bash
# Option 1: Use startup script
./scripts/start_api.sh

# Option 2: Use Python main module
python main.py api

# Option 3: Direct uvicorn
uvicorn src.api.main:app --reload
```

API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs

## 5. Quick API Test

```bash
# Test health endpoint
curl http://localhost:8000/health

# Get sample data
curl http://localhost:8000/sample-data

# Run optimization (using sample data)
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "workers": [
      {
        "id": 1,
        "name": "John Doe",
        "country": "US",
        "skills": ["morning", "afternoon"],
        "max_shifts_per_week": 5,
        "unavailable_days": []
      },
      {
        "id": 2,
        "name": "Jane Smith",
        "country": "UK",
        "skills": ["afternoon", "night"],
        "max_shifts_per_week": 5,
        "unavailable_days": []
      }
    ],
    "num_days": 7,
    "shift_requirements": {
      "morning": 1,
      "afternoon": 1,
      "night": 1
    },
    "track_experiment": false
  }'
```

## 6. Python API Usage

```python
from src.optimization.scheduler import ShiftOptimizer
import json

# Load sample data
with open('data/sample/workers.json') as f:
    workers = json.load(f)

# Initialize optimizer
optimizer = ShiftOptimizer()

# Run optimization
result = optimizer.optimize_schedule(
    workers=workers,
    num_days=7,
    shift_requirements={'morning': 1, 'afternoon': 1, 'night': 1}
)

print(f"Status: {result['status']}")
if result['status'] == 'optimal':
    print(f"Schedule generated for {len(result['schedule'])} days")
```

## Optional: Enable Advanced Features

### Enable RAG-based Compliance Checking

1. Get an OpenAI API key from https://platform.openai.com/
2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Add your API key:
   ```
   OPENAI_API_KEY=your_key_here
   ```
4. Install LangChain:
   ```bash
   pip install langchain langchain-community chromadb openai
   ```

### Enable MLflow Experiment Tracking

1. Install MLflow:
   ```bash
   pip install mlflow
   ```

2. Start MLflow server:
   ```bash
   ./scripts/start_mlflow.sh
   # Or: mlflow server --host 0.0.0.0 --port 5000
   ```

3. Access MLflow UI at http://localhost:5000

## Common Issues

### Port already in use
```bash
# Check what's using the port
lsof -i :8000  # or :8501 for Streamlit

# Kill the process or use a different port
streamlit run src/dashboard/app.py --server.port 8502
```

### Import errors
```bash
# Make sure you're in the project directory
cd /path/to/Rostering-Agent

# Make sure virtual environment is activated
source venv/bin/activate
```

### Optimization infeasible
- Reduce shift requirements
- Add more workers
- Check worker skills match shift types
- Adjust constraints in `config/config.yaml`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [docs/API.md](docs/API.md) for API reference
- See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for development guide
- Customize `config/config.yaml` for your use case
- Add your own labour law documents in `data/labour_laws/`

## Need Help?

- Check the [README.md](README.md) troubleshooting section
- Open an issue on GitHub
- Review example usage in `example_usage.py`
