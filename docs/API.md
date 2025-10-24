# API Documentation

## Endpoints

### GET /
Root endpoint returning API information.

**Response:**
```json
{
  "message": "AI-Driven Rostering Agent API",
  "version": "1.0.0",
  "endpoints": {
    "optimize": "/optimize",
    "validate": "/validate",
    "health": "/health"
  }
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "optimizer": "ready",
    "compliance_checker": "ready",
    "mlflow_tracker": "ready"
  }
}
```

### POST /optimize
Optimize shift schedule for given workers and requirements.

**Request Body:**
```json
{
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
  "track_experiment": true,
  "run_name": "test_run"
}
```

**Response:**
```json
{
  "status": "optimal",
  "schedule": [...],
  "objective_value": 10.0,
  "solve_time": 2.5,
  "statistics": {
    "num_workers": 5,
    "num_days": 14,
    "num_shifts": 3
  },
  "mlflow_run_id": "abc123"
}
```

### POST /validate
Validate a schedule against labour law constraints.

**Request Body:**
```json
{
  "schedule": [
    {
      "day": 0,
      "shifts": {
        "morning": [
          {
            "worker_id": 1,
            "worker_name": "John Doe",
            "country": "US"
          }
        ]
      }
    }
  ],
  "workers": [...]
}
```

**Response:**
```json
{
  "valid": true,
  "violations": [],
  "total_violations": 0,
  "compliance_check": {
    "overall_compliant": true,
    "countries_checked": ["US", "UK"],
    "violations": []
  }
}
```

### GET /labour-laws/{country}
Query labour law information for a specific country.

**Parameters:**
- `country` (path): Country code (US, UK, SG, DE, JP)
- `query` (query): Question about labour laws

**Response:**
```json
{
  "country": "US",
  "query": "What are the overtime rules?",
  "answer": "In the United States, overtime pay is required..."
}
```

### GET /countries
List available countries with their labour law constraints.

**Response:**
```json
{
  "countries": {
    "US": {
      "name": "United States",
      "max_hours_per_week": 40,
      "max_consecutive_days": 6,
      "min_rest_hours": 11
    },
    ...
  }
}
```

### GET /sample-data
Get sample workers and requirements for testing.

**Response:**
```json
{
  "workers": [...],
  "requirements": {
    "days": 14,
    "shifts_per_day": 3,
    "shift_types": ["morning", "afternoon", "night"],
    "demand": {
      "morning": 2,
      "afternoon": 2,
      "night": 1
    }
  }
}
```

## Error Responses

All endpoints may return error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request
- 500: Internal Server Error

## Interactive Documentation

The API provides interactive documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
