"""
FastAPI application for shift optimization and validation.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from src.optimization.scheduler import ShiftOptimizer
from src.compliance.checker import ComplianceChecker
from src.tracking.mlflow_tracker import ExperimentTracker

app = FastAPI(
    title="AI-Driven Rostering Agent API",
    description="Multi-country shift optimization with labour law compliance",
    version="1.0.0"
)

# Initialize components
optimizer = ShiftOptimizer()
compliance_checker = ComplianceChecker()
tracker = ExperimentTracker()


# Pydantic models
class Worker(BaseModel):
    """Worker model."""
    id: int
    name: str
    country: str = Field(description="Country code (US, UK, SG, DE, JP)")
    skills: List[str] = Field(description="List of shift types worker can handle")
    max_shifts_per_week: int = Field(default=5, ge=1, le=7)
    unavailable_days: List[int] = Field(default=[])


class OptimizationRequest(BaseModel):
    """Request model for optimization."""
    workers: List[Worker]
    num_days: int = Field(default=14, ge=1, le=365)
    shift_requirements: Dict[str, int] = Field(
        description="Daily demand for each shift type",
        example={"morning": 2, "afternoon": 2, "night": 1}
    )
    track_experiment: bool = Field(default=True)
    run_name: Optional[str] = None


class ValidationRequest(BaseModel):
    """Request model for schedule validation."""
    schedule: List[Dict[str, Any]]
    workers: List[Worker]


class OptimizationResponse(BaseModel):
    """Response model for optimization."""
    status: str
    schedule: Optional[List[Dict[str, Any]]] = None
    objective_value: Optional[float] = None
    solve_time: Optional[float] = None
    statistics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    mlflow_run_id: Optional[str] = None


class ValidationResponse(BaseModel):
    """Response model for validation."""
    valid: bool
    violations: List[Dict[str, Any]]
    total_violations: int
    compliance_check: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI-Driven Rostering Agent API",
        "version": "1.0.0",
        "endpoints": {
            "optimize": "/optimize",
            "validate": "/validate",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "optimizer": "ready",
            "compliance_checker": "ready",
            "mlflow_tracker": "ready"
        }
    }


@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_schedule(request: OptimizationRequest):
    """
    Optimize shift schedule for given workers and requirements.
    
    This endpoint uses OR-Tools CP-SAT solver to create an optimal shift schedule
    that respects labour law constraints for multiple countries.
    """
    try:
        # Convert workers to dict format
        workers = [w.dict() for w in request.workers]
        
        # Run optimization
        result = optimizer.optimize_schedule(
            workers=workers,
            num_days=request.num_days,
            shift_requirements=request.shift_requirements
        )
        
        # Track with MLflow if requested
        mlflow_run_id = None
        if request.track_experiment and result['status'] in ['optimal', 'feasible']:
            params = {
                'num_workers': len(workers),
                'num_days': request.num_days,
                'shift_types': ','.join(request.shift_requirements.keys()),
            }
            mlflow_run_id = tracker.log_optimization_run(
                params=params,
                result=result,
                run_name=request.run_name
            )
        
        return OptimizationResponse(
            **result,
            mlflow_run_id=mlflow_run_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate", response_model=ValidationResponse)
async def validate_schedule(request: ValidationRequest):
    """
    Validate a schedule against labour law constraints.
    
    This endpoint checks if a given schedule complies with labour laws
    using both rule-based validation and RAG-based compliance checking.
    """
    try:
        # Convert workers to dict format
        workers = [w.dict() for w in request.workers]
        
        # Validate with optimizer
        validation_result = optimizer.validate_schedule(
            schedule=request.schedule,
            workers=workers
        )
        
        # Check compliance with labour laws using RAG
        compliance_result = compliance_checker.check_compliance(
            schedule=request.schedule,
            workers=workers
        )
        
        return ValidationResponse(
            valid=validation_result['valid'] and compliance_result['overall_compliant'],
            violations=validation_result['violations'] + compliance_result['violations'],
            total_violations=validation_result['total_violations'] + len(compliance_result['violations']),
            compliance_check=compliance_result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/labour-laws/{country}")
async def get_labour_law_info(country: str, query: str = "What are the working hour limits?"):
    """
    Query labour law information for a specific country using RAG.
    
    Args:
        country: Country code (US, UK, SG, DE, JP)
        query: Question about labour laws
    """
    try:
        answer = compliance_checker.get_labour_law_info(country, query)
        return {
            "country": country,
            "query": query,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/countries")
async def list_countries():
    """List available countries with their labour law constraints."""
    return {
        "countries": optimizer.config.get('countries', {})
    }


@app.get("/sample-data")
async def get_sample_data():
    """Get sample workers and requirements for testing."""
    try:
        workers_path = Path("data/sample/workers.json")
        requirements_path = Path("data/sample/requirements.json")
        
        with open(workers_path) as f:
            workers = json.load(f)
        
        with open(requirements_path) as f:
            requirements = json.load(f)
        
        return {
            "workers": workers,
            "requirements": requirements
        }
    except Exception as e:
        return {
            "error": "Sample data not available",
            "message": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
