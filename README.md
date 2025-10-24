# 🤖 AI-Driven Multi-Country Rostering Agent

An intelligent shift scheduling system that optimizes worker rosters while ensuring compliance with labour laws across multiple countries (US, UK, Singapore, Germany, Japan).

## ✨ Features

- **🎯 Intelligent Optimization**: Uses OR-Tools CP-SAT solver for constraint-based shift optimization
- **🌍 Multi-Country Support**: Built-in labour law compliance for 5 countries
- **🔍 RAG-Based Compliance**: LangChain + Chroma for intelligent labour law verification
- **📊 Experiment Tracking**: MLflow integration for tracking optimization runs
- **🚀 REST API**: FastAPI endpoints for easy integration
- **📈 Interactive Dashboard**: Streamlit-based UI for visualization and control
- **✅ Real-time Validation**: Schedule validation against labour law constraints

## 🏗️ Architecture

```
rostering-agent/
├── src/
│   ├── optimization/      # OR-Tools CP-SAT scheduler
│   ├── compliance/        # LangChain + Chroma RAG checker
│   ├── api/              # FastAPI endpoints
│   ├── dashboard/        # Streamlit UI
│   └── tracking/         # MLflow experiment tracking
├── data/
│   ├── labour_laws/      # Labour law documents by country
│   └── sample/           # Sample data for testing
├── config/               # Configuration files
├── scripts/              # Startup scripts
└── tests/               # Unit and integration tests
```

## 📋 Requirements

- Python 3.8 or higher
- pip package manager
- (Optional) OpenAI API key for advanced RAG features

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/javinlimjk/Rostering-Agent.git
cd Rostering-Agent
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key (optional but recommended)
```

### 5. Run the Application

#### Option A: Start All Services at Once

```bash
./scripts/start_all.sh
```

#### Option B: Start Services Individually

**Terminal 1 - MLflow Tracking Server:**
```bash
./scripts/start_mlflow.sh
```

**Terminal 2 - FastAPI Server:**
```bash
./scripts/start_api.sh
```

**Terminal 3 - Streamlit Dashboard:**
```bash
./scripts/start_dashboard.sh
```

### 6. Access the Application

- **Streamlit Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Endpoint**: http://localhost:8000
- **MLflow UI**: http://localhost:5000

## 📖 Usage Guide

### Using the Streamlit Dashboard

1. Navigate to http://localhost:8501
2. Click **"Load Sample Data"** or manually configure workers
3. Set schedule parameters (number of days, shift requirements)
4. Click **"Optimize Schedule"** to generate an optimal roster
5. View the generated schedule and analytics
6. Validate schedules using the **"Validate Schedule"** tab

### Using the REST API

#### Optimize a Schedule

```bash
curl -X POST "http://localhost:8000/optimize" \
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
      }
    ],
    "num_days": 14,
    "shift_requirements": {
      "morning": 2,
      "afternoon": 2,
      "night": 1
    },
    "track_experiment": true
  }'
```

#### Validate a Schedule

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": [...],
    "workers": [...]
  }'
```

#### Query Labour Laws

```bash
curl "http://localhost:8000/labour-laws/US?query=What%20are%20the%20overtime%20rules?"
```

### Using Python API Directly

```python
from src.optimization.scheduler import ShiftOptimizer
from src.compliance.checker import ComplianceChecker
from src.tracking.mlflow_tracker import ExperimentTracker

# Initialize components
optimizer = ShiftOptimizer()
compliance_checker = ComplianceChecker()
tracker = ExperimentTracker()

# Define workers and requirements
workers = [
    {
        "id": 1,
        "name": "John Doe",
        "country": "US",
        "skills": ["morning", "afternoon"],
        "max_shifts_per_week": 5,
        "unavailable_days": []
    }
]

shift_requirements = {
    "morning": 2,
    "afternoon": 2,
    "night": 1
}

# Optimize schedule
result = optimizer.optimize_schedule(
    workers=workers,
    num_days=14,
    shift_requirements=shift_requirements
)

# Validate compliance
if result['status'] in ['optimal', 'feasible']:
    validation = compliance_checker.check_compliance(
        schedule=result['schedule'],
        workers=workers
    )
    print(f"Compliant: {validation['overall_compliant']}")
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_optimization.py
```

## 🌍 Supported Countries

| Country | Code | Max Hours/Week | Max Consecutive Days | Min Rest Hours |
|---------|------|----------------|---------------------|----------------|
| United States | US | 40 | 6 | 11 |
| United Kingdom | UK | 48 | 6 | 11 |
| Singapore | SG | 44 | 7 | 12 |
| Germany | DE | 48 | 6 | 11 |
| Japan | JP | 40 | 6 | 8 |

## 🔧 Configuration

Edit `config/config.yaml` to customize:

- Country-specific labour law constraints
- Shift types and durations
- Optimization parameters
- Solver time limits

Example:

```yaml
countries:
  US:
    name: "United States"
    max_hours_per_week: 40
    max_consecutive_days: 6
    min_rest_hours: 11

shifts:
  morning:
    start_hour: 6
    duration_hours: 8

optimization:
  solver_time_limit_seconds: 300
  num_workers: 5
  num_days: 14
```

## 📊 MLflow Tracking

All optimization runs are automatically tracked in MLflow:

1. Open MLflow UI at http://localhost:5000
2. View experiment runs with parameters and metrics
3. Compare different optimization strategies
4. Download schedule artifacts

## 🛠️ Development

### Project Structure

```
├── src/
│   ├── optimization/scheduler.py    # OR-Tools optimization logic
│   ├── compliance/checker.py        # RAG-based compliance checking
│   ├── api/main.py                  # FastAPI application
│   ├── dashboard/app.py             # Streamlit dashboard
│   └── tracking/mlflow_tracker.py   # MLflow integration
├── data/
│   ├── labour_laws/                 # Labour law documents
│   └── sample/                      # Sample test data
├── config/config.yaml               # Main configuration
├── tests/                           # Test suite
└── scripts/                         # Utility scripts
```

### Adding a New Country

1. Add labour law document to `data/labour_laws/{COUNTRY_CODE}.txt`
2. Update `config/config.yaml` with country constraints:

```yaml
countries:
  FR:  # France
    name: "France"
    max_hours_per_week: 35
    max_consecutive_days: 6
    min_rest_hours: 11
```

3. Reinitialize the Chroma vector store (delete `chroma_db/` directory)

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 🐛 Troubleshooting

### API Connection Issues

- Ensure all services are running on the correct ports
- Check firewall settings
- Review logs in the `logs/` directory

### MLflow Issues

- Delete `mlflow.db` and `mlruns/` to reset tracking
- Ensure port 5000 is not in use by another application

### Chroma/RAG Issues

- Set `OPENAI_API_KEY` in `.env` file for full RAG functionality
- Without OpenAI key, basic rule-based compliance checking will be used
- Delete `chroma_db/` directory to rebuild the vector store

### Optimization Infeasibility

- Reduce shift requirements or increase number of workers
- Check worker skills match shift types needed
- Adjust max_consecutive_days or other constraints
- Increase solver time limit in config

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- **OR-Tools**: Google's constraint programming solver
- **LangChain**: Framework for LLM applications
- **FastAPI**: Modern Python web framework
- **Streamlit**: Data app framework
- **MLflow**: ML lifecycle management

---

Built with ❤️ using Python, OR-Tools, LangChain, FastAPI, Streamlit, and MLflow
