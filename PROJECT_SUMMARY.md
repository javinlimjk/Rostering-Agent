# AI-Driven Multi-Country Rostering Agent - Project Summary

## 🎯 Project Overview

A complete, production-ready AI-driven shift scheduling system that optimizes worker rosters while ensuring compliance with labour laws across multiple countries. The system uses constraint programming (OR-Tools CP-SAT), retrieval-augmented generation (LangChain + Chroma), and modern web technologies (FastAPI, Streamlit, MLflow).

## ✅ Completed Features

### Core Optimization Engine
- **OR-Tools CP-SAT Solver**: Constraint-based optimization for shift scheduling
- **Multi-shift Support**: Morning, afternoon, and night shifts
- **Worker Skills Matching**: Ensures workers are assigned to shifts they can handle
- **Load Balancing**: Distributes shifts fairly across workers
- **Country-specific Constraints**: Different labour law rules per country
- **Configurable Parameters**: YAML-based configuration for easy customization

### Labour Law Compliance
- **5 Countries Supported**: US, UK, Singapore, Germany, Japan
- **Rule-based Validation**: Fast, reliable compliance checking
- **RAG-based Checking** (optional): Intelligent, context-aware validation using LangChain + Chroma
- **Labour Law Documents**: Comprehensive documents for each supported country
- **Violation Detection**: Detailed reporting of any compliance issues

### REST API (FastAPI)
- **POST /optimize**: Generate optimal shift schedules
- **POST /validate**: Validate schedules against labour laws
- **GET /labour-laws/{country}**: Query labour law information
- **GET /countries**: List supported countries
- **GET /sample-data**: Get sample test data
- **GET /health**: Health check endpoint
- **Interactive Documentation**: Swagger UI and ReDoc auto-generated

### Interactive Dashboard (Streamlit)
- **Visual Configuration**: Configure workers and requirements through UI
- **Real-time Optimization**: Generate schedules with one click
- **Schedule Visualization**: Interactive charts and tables with Plotly
- **Analytics**: Detailed statistics and breakdowns
- **Validation Interface**: Check schedule compliance
- **Multi-tab Interface**: Organized workflow

### Experiment Tracking (MLflow)
- **Automatic Logging**: Track all optimization runs
- **Parameter Tracking**: Record input parameters
- **Metric Tracking**: Log solve times, objective values
- **Artifact Storage**: Save generated schedules
- **Run Comparison**: Compare different optimization strategies

### Development & Deployment
- **Comprehensive Tests**: 8/8 tests passing with pytest
- **Security Hardened**: 0 CodeQL alerts, sanitized error messages
- **Docker Support**: Dockerfile and docker-compose.yml included
- **Documentation**: README, QuickStart, API docs, Development guide
- **Example Scripts**: Working example demonstrating all features
- **Optional Dependencies**: Graceful fallbacks when optional packages unavailable

## 📁 Project Structure

```
Rostering-Agent/
├── src/                          # Source code
│   ├── optimization/             # OR-Tools scheduler
│   ├── compliance/               # LangChain RAG compliance
│   ├── api/                      # FastAPI application
│   ├── dashboard/                # Streamlit UI
│   └── tracking/                 # MLflow integration
├── data/                         # Data files
│   ├── labour_laws/              # Country labour law documents
│   └── sample/                   # Sample workers and requirements
├── config/                       # Configuration files
│   └── config.yaml               # Main configuration
├── tests/                        # Test suite
├── scripts/                      # Utility scripts
├── docs/                         # Additional documentation
├── example_usage.py              # Working example
├── main.py                       # CLI entry point
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Multi-container setup
├── README.md                     # Main documentation
├── QUICKSTART.md                 # Quick start guide
├── CHANGELOG.md                  # Version history
└── LICENSE                       # MIT License
```

## 🔧 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|----------|
| Optimization | OR-Tools | 9.8 | Constraint programming solver |
| API | FastAPI | 0.109.1 | REST API framework |
| Dashboard | Streamlit | 1.29.0 | Interactive web UI |
| RAG | LangChain | 0.1.0 | Language model framework |
| Vector DB | Chroma | 0.4.22 | Document embedding storage |
| Tracking | MLflow | 2.17.1 | Experiment tracking |
| Visualization | Plotly | 5.18.0 | Interactive charts |
| Data | Pandas | 2.1.4 | Data manipulation |
| Validation | Pydantic | 2.5.0 | Data validation |
| Testing | pytest | 7.4.3 | Test framework |
| Python | CPython | 3.8+ | Runtime |

## 📊 Key Statistics

- **Total Files**: 40+ source and configuration files
- **Lines of Code**: ~3,000+ lines
- **Test Coverage**: 8 tests, 100% pass rate
- **Security Alerts**: 0 (all fixed)
- **API Endpoints**: 7 functional endpoints
- **Countries Supported**: 5 (US, UK, SG, DE, JP)
- **Shift Types**: 3 (morning, afternoon, night)

## 🎨 Key Features Implemented

### Optimization Constraints
1. ✅ Meet exact shift requirements
2. ✅ One shift per worker per day maximum
3. ✅ Respect worker availability
4. ✅ Min/max shifts per worker
5. ✅ Weekly shift limits
6. ✅ Maximum consecutive working days
7. ✅ Worker skill matching
8. ✅ Load balancing across workers

### Validation Checks
1. ✅ Weekly hour limits (country-specific)
2. ✅ Consecutive day limits (country-specific)
3. ✅ Skill requirements
4. ✅ Worker availability
5. ✅ RAG-based intelligent checking (optional)

### API Capabilities
1. ✅ Schedule optimization
2. ✅ Schedule validation
3. ✅ Labour law queries
4. ✅ Country information
5. ✅ Sample data access
6. ✅ Health monitoring
7. ✅ Error handling with sanitized messages

### Dashboard Features
1. ✅ Worker configuration
2. ✅ Shift requirements setup
3. ✅ Real-time optimization
4. ✅ Schedule visualization
5. ✅ Analytics and statistics
6. ✅ Validation interface
7. ✅ Sample data loading

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/javinlimjk/Rostering-Agent.git
cd Rostering-Agent
pip install -r requirements.txt

# Run example
python example_usage.py

# Start dashboard
streamlit run src/dashboard/app.py

# Start API
uvicorn src.api.main:app --reload
```

## 🔐 Security

- ✅ Updated FastAPI to 0.109.1 (fixed ReDoS vulnerability)
- ✅ Updated MLflow to 2.17.1 (fixed path traversal vulnerabilities)
- ✅ Sanitized all error messages (no stack trace exposure)
- ✅ Input validation with Pydantic v2
- ✅ 0 CodeQL security alerts

## 📈 Testing

All tests passing:
```
tests/test_api.py::test_root PASSED
tests/test_api.py::test_health PASSED
tests/test_api.py::test_list_countries PASSED
tests/test_api.py::test_optimize_endpoint PASSED
tests/test_api.py::test_validate_endpoint PASSED
tests/test_optimization.py::test_optimizer_initialization PASSED
tests/test_optimization.py::test_optimize_schedule PASSED
tests/test_optimization.py::test_validate_schedule PASSED

8 passed in 0.77s
```

## 🎯 Use Cases

1. **Healthcare**: Hospital nurse/doctor scheduling
2. **Retail**: Store staff shift management
3. **Manufacturing**: Production line worker scheduling
4. **Hospitality**: Hotel staff rostering
5. **Call Centers**: Agent shift planning
6. **Transportation**: Driver scheduling
7. **Security**: Guard duty assignment

## 🌍 Multi-Country Support

| Country | Max Hours/Week | Max Consecutive Days | Rest Hours |
|---------|----------------|---------------------|------------|
| US | 40 | 6 | 11 |
| UK | 48 | 6 | 11 |
| Singapore | 44 | 7 | 12 |
| Germany | 48 | 6 | 11 |
| Japan | 40 | 6 | 8 |

## 📚 Documentation

1. **README.md**: Comprehensive main documentation
2. **QUICKSTART.md**: 5-minute getting started guide
3. **docs/API.md**: Complete API reference
4. **docs/DEVELOPMENT.md**: Developer guide
5. **CHANGELOG.md**: Version history
6. **Inline Comments**: Detailed code documentation

## 🔄 Deployment Options

1. **Local Development**: `python main.py`
2. **Docker**: `docker-compose up`
3. **Individual Services**: Startup scripts in `scripts/`
4. **Cloud Ready**: Environment-based configuration

## 💡 Example Output

```
============================================================
AI-Driven Multi-Country Rostering Agent - Example Usage
============================================================

1. Loading sample data...
   - Workers loaded: 5
   - Countries: {'US', 'UK', 'SG', 'DE', 'JP'}

3. Running shift optimization...
   Status: OPTIMAL
   Solve Time: 0.015s
   Schedule Days: 14

Summary Statistics:
   John Doe             -> 9 shifts (US)
   Jane Smith           -> 9 shifts (UK)
   Alice Johnson        -> 9 shifts (SG)
   Bob Wilson           -> 6 shifts (DE)
   Charlie Brown        -> 9 shifts (JP)

✅ Example completed successfully!
```

## 🎓 Learning Resources

- OR-Tools documentation for constraint programming
- FastAPI documentation for API development
- Streamlit documentation for dashboard creation
- LangChain documentation for RAG implementation
- MLflow documentation for experiment tracking

## 🤝 Contributing

The project is ready for contributions with:
- Clear code structure
- Comprehensive tests
- Detailed documentation
- Example usage
- Development guide

## 📝 License

MIT License - See LICENSE file for details

## 🏆 Project Success Criteria

✅ All requirements from problem statement implemented
✅ Clean, modular code architecture
✅ Comprehensive documentation
✅ Working examples
✅ All tests passing
✅ Security hardened
✅ Production ready

---

**Project Status**: ✅ COMPLETE AND PRODUCTION-READY

All features implemented, tested, documented, and ready for deployment!
