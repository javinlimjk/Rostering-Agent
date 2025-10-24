# System Architecture

## Overview

The AI-Driven Multi-Country Rostering Agent follows a modular, layered architecture with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                          │
├──────────────────────────┬──────────────────────────────────────┤
│   Streamlit Dashboard    │           REST API Clients            │
│   (Port 8501)           │     (curl, httpx, browser, etc.)      │
└──────────┬───────────────┴────────────────┬─────────────────────┘
           │                                │
           │                                │
┌──────────▼────────────────────────────────▼─────────────────────┐
│                      API Layer (FastAPI)                         │
│                         Port 8000                                │
├──────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                      │
│  • POST /optimize      - Generate optimal schedules             │
│  • POST /validate      - Validate schedule compliance           │
│  • GET /labour-laws    - Query labour law information           │
│  • GET /countries      - List available countries               │
│  • GET /health         - Health check                           │
└──────┬────────────────┬────────────────┬─────────────────┬──────┘
       │                │                │                 │
       │                │                │                 │
┌──────▼───────┐ ┌──────▼──────┐ ┌──────▼────────┐ ┌─────▼──────┐
│ Optimization │ │ Compliance  │ │   Tracking    │ │   Config   │
│    Module    │ │   Module    │ │    Module     │ │   Module   │
│  (OR-Tools)  │ │ (LangChain) │ │   (MLflow)    │ │   (YAML)   │
└──────┬───────┘ └──────┬──────┘ └──────┬────────┘ └─────┬──────┘
       │                │                │                 │
       │                │                │                 │
┌──────▼────────────────▼────────────────▼─────────────────▼──────┐
│                       Data Layer                                 │
├──────────────────────────────────────────────────────────────────┤
│  • config/config.yaml           - Configuration                  │
│  • data/labour_laws/*.txt       - Labour law documents           │
│  • data/sample/*.json           - Sample data                    │
│  • chroma_db/                   - Vector database (RAG)          │
│  • mlruns/                      - MLflow tracking data           │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

#### Streamlit Dashboard
- **Purpose**: Interactive web-based UI for end users
- **Port**: 8501
- **Features**:
  - Worker configuration
  - Schedule optimization
  - Visualization and analytics
  - Validation interface
- **Tech**: Streamlit 1.29.0, Plotly 5.18.0

#### REST API
- **Purpose**: Programmatic access for integrations
- **Port**: 8000
- **Format**: JSON
- **Documentation**: Auto-generated Swagger UI at `/docs`
- **Tech**: FastAPI 0.109.1, Uvicorn

### 2. Business Logic Layer

#### Optimization Module (`src/optimization/`)
```
ShiftOptimizer
├── optimize_schedule()
│   ├── Create CP-SAT model
│   ├── Add constraints
│   │   ├── Shift requirements
│   │   ├── Worker availability
│   │   ├── Skills matching
│   │   ├── Weekly limits
│   │   └── Consecutive days
│   ├── Define objective
│   └── Solve and return schedule
└── validate_schedule()
    ├── Check weekly hours
    └── Check consecutive days
```

**Key Technology**: Google OR-Tools CP-SAT Solver

**Constraints Implemented**:
1. Exact shift requirement matching
2. One shift per worker per day
3. Worker availability respect
4. Min/max shifts per worker
5. Weekly shift limits
6. Maximum consecutive working days
7. Worker skill matching
8. Load balancing

#### Compliance Module (`src/compliance/`)
```
ComplianceChecker
├── check_compliance()
│   ├── RAG-based checking (if available)
│   └── Rule-based checking (always)
├── _check_with_rag()
│   ├── Query vector database
│   └── LLM-based analysis
└── _basic_compliance_check()
    ├── Consecutive days check
    └── Weekly hours check
```

**Key Technology**: LangChain + Chroma + OpenAI (optional)

**Checking Methods**:
1. **RAG-based** (requires LangChain + OpenAI API key):
   - Semantic search over labour law documents
   - Context-aware violation detection
   - Natural language explanations

2. **Rule-based** (always available):
   - Fast, deterministic checking
   - Hard-coded country constraints
   - Reliable fallback

#### Tracking Module (`src/tracking/`)
```
ExperimentTracker
├── log_optimization_run()
│   ├── log_parameters()
│   ├── log_metrics()
│   └── log_schedule()
└── MLflow backend
    ├── SQLite database
    └── Artifact storage
```

**Key Technology**: MLflow 2.17.1

**Tracked Information**:
- Input parameters (workers, days, requirements)
- Performance metrics (solve time, objective value)
- Schedule artifacts (JSON format)
- Run metadata

### 3. Data Layer

#### Configuration (`config/`)
- **config.yaml**: Main configuration file
  - Country constraints
  - Shift definitions
  - Optimization parameters

#### Labour Law Documents (`data/labour_laws/`)
- Plain text documents per country
- Indexed by Chroma for RAG
- Human-readable format

#### Sample Data (`data/sample/`)
- Example workers (5 workers, 5 countries)
- Example requirements (3 shift types)
- Used for testing and demonstrations

#### Vector Database (`chroma_db/`)
- Persistent Chroma database
- Embeddings of labour law documents
- Created on first run if LangChain available

#### MLflow Storage (`mlruns/`, `mlartifacts/`)
- Experiment tracking data
- Run parameters and metrics
- Schedule artifacts

## Data Flow

### Optimization Flow
```
User Request
    ↓
API Endpoint (/optimize)
    ↓
ShiftOptimizer.optimize_schedule()
    ↓
OR-Tools CP-SAT Solver
    ↓
Schedule Generated
    ↓
[Optional] MLflow Logging
    ↓
Response to User
```

### Validation Flow
```
User Request (with schedule)
    ↓
API Endpoint (/validate)
    ↓
ShiftOptimizer.validate_schedule()
    ↓
Rule-based Validation
    ↓
ComplianceChecker.check_compliance()
    ↓
[Optional] RAG-based Validation
    ↓
Violation Report
    ↓
Response to User
```

### RAG Query Flow
```
User Query about Labour Law
    ↓
API Endpoint (/labour-laws/{country})
    ↓
ComplianceChecker.get_labour_law_info()
    ↓
Chroma Vector Search
    ↓
LangChain Retrieval QA
    ↓
OpenAI LLM
    ↓
Answer with Sources
    ↓
Response to User
```

## Deployment Architecture

### Development (Local)
```
Terminal 1: MLflow Server (port 5000)
Terminal 2: FastAPI Server (port 8000)
Terminal 3: Streamlit Dashboard (port 8501)
```

### Docker Compose
```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┐
    │         │              │
┌───▼───┐ ┌──▼────┐ ┌───────▼────┐
│  API  │ │  UI   │ │   MLflow   │
│ :8000 │ │ :8501 │ │   :5000    │
└───┬───┘ └───┬───┘ └──────┬─────┘
    │         │             │
    └─────────┴─────────────┘
              │
         Shared Network
```

## Security Architecture

### Input Validation
```
Request
    ↓
Pydantic Models (Type + Constraint Validation)
    ↓
Business Logic
```

### Error Handling
```
Exception
    ↓
Sanitization (Remove Stack Traces)
    ↓
Generic Error Message
    ↓
HTTP Error Response
```

### Authentication (Future)
```
Request
    ↓
API Key / JWT Verification
    ↓
Rate Limiting
    ↓
Business Logic
```

## Scalability Considerations

### Current Architecture
- Single instance deployment
- SQLite for MLflow
- In-memory Chroma database

### Future Scaling Options

#### Horizontal Scaling
```
Load Balancer
    ↓
Multiple API Instances
    ↓
Shared Data Layer (PostgreSQL, S3)
```

#### Database Scaling
- Replace SQLite with PostgreSQL for MLflow
- Use persistent volume for Chroma
- Object storage (S3) for artifacts

#### Caching Layer
- Redis for frequent queries
- Cache optimization results
- Cache labour law lookups

## Technology Dependencies

### Core Dependencies (Required)
- Python 3.8+
- OR-Tools 9.8
- FastAPI 0.109.1
- Pydantic 2.5.0
- PyYAML 6.0.1

### Optional Dependencies
- LangChain 0.1.0 (for RAG)
- Chroma 0.4.22 (for RAG)
- OpenAI 1.6.1 (for RAG)
- MLflow 2.17.1 (for tracking)
- Streamlit 1.29.0 (for UI)

### Development Dependencies
- pytest 7.4.3
- black 23.12.1
- flake8 6.1.0
- mypy 1.7.1

## Extension Points

### Adding New Countries
1. Create labour law document: `data/labour_laws/{COUNTRY}.txt`
2. Update `config/config.yaml` with constraints
3. Rebuild Chroma database

### Adding New Shift Types
1. Update `config/config.yaml` shifts section
2. Update sample data
3. No code changes needed

### Adding New Constraints
1. Modify `src/optimization/scheduler.py`
2. Add constraint to CP-SAT model
3. Update tests

### Custom Validation Rules
1. Extend `ComplianceChecker` class
2. Add methods to `src/compliance/checker.py`
3. Update API validation endpoint

## Monitoring and Observability

### Available Metrics
- Solve time per optimization
- Success/failure rates
- Schedule compliance rates
- API response times

### Logging
- Application logs to `logs/` directory
- MLflow experiment logs
- API access logs

### Health Checks
- `/health` endpoint for API status
- Component status reporting
- Database connectivity checks

## Best Practices Implemented

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Components are loosely coupled
3. **Error Handling**: Comprehensive exception handling
4. **Input Validation**: Pydantic models for all inputs
5. **Documentation**: Inline comments and docstrings
6. **Testing**: Unit and integration tests
7. **Configuration**: External YAML files
8. **Security**: Sanitized errors, updated dependencies
9. **Scalability**: Modular design for future growth
10. **Observability**: Logging and monitoring hooks

---

This architecture supports the current requirements while remaining flexible for future enhancements and scaling.
