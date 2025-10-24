# Changelog

All notable changes to the AI-Driven Rostering Agent project will be documented in this file.

## [1.0.0] - 2025-10-24

### Added
- Initial release of AI-Driven Multi-Country Rostering Agent
- OR-Tools CP-SAT based shift optimization engine
  - Support for multiple shift types (morning, afternoon, night)
  - Worker skills matching
  - Country-specific labour law constraints
  - Load balancing across workers
- FastAPI REST API with endpoints:
  - `/optimize` - Generate optimal shift schedules
  - `/validate` - Validate schedules against labour laws
  - `/labour-laws/{country}` - Query labour law information
  - `/countries` - List supported countries
  - `/sample-data` - Get sample test data
- LangChain + Chroma RAG-based compliance checking
  - Semantic search over labour law documents
  - Intelligent violation detection
  - Graceful fallback to rule-based checking
- Streamlit interactive dashboard
  - Visual schedule configuration
  - Real-time optimization
  - Schedule visualization with Plotly
  - Analytics and statistics
- MLflow experiment tracking integration
  - Automatic logging of optimization runs
  - Parameter and metric tracking
  - Schedule artifact storage
- Multi-country support (US, UK, Singapore, Germany, Japan)
  - Country-specific labour law documents
  - Configurable constraints per country
- Comprehensive documentation
  - Detailed README with examples
  - API documentation
  - Development guide
  - Quick start guide
- Test suite with pytest
  - API endpoint tests
  - Optimization module tests
  - 100% test pass rate
- Sample data and configuration
  - Example workers and requirements
  - Labour law documents for 5 countries
  - Configurable YAML settings
- Utility scripts
  - Service startup scripts
  - All-in-one launcher
- Security improvements
  - Updated FastAPI to 0.109.1 (fixed ReDoS vulnerability)
  - Updated MLflow to 2.17.1 (fixed multiple vulnerabilities)
  - Input validation with Pydantic v2

### Features
- Constraint programming for optimal scheduling
- Multi-country labour law compliance
- Real-time schedule validation
- Interactive web dashboard
- REST API for programmatic access
- Experiment tracking and versioning
- Extensible architecture
- Optional dependency support

### Technical Details
- Python 3.8+ support
- OR-Tools 9.8 for optimization
- FastAPI 0.109.1 for API
- Streamlit 1.29.0 for dashboard
- LangChain 0.1.0 for RAG (optional)
- MLflow 2.17.1 for tracking (optional)
- Pydantic v2 for data validation
- Plotly for visualizations

### Documentation
- README.md - Main documentation
- QUICKSTART.md - Quick start guide
- docs/API.md - API reference
- docs/DEVELOPMENT.md - Development guide
- Example usage script
- Inline code documentation

## [Unreleased]

### Planned
- Additional country support
- Advanced constraint customization
- Schedule templates
- Historical data analysis
- Performance optimizations
- Docker containerization
- CI/CD pipeline
- More test coverage
