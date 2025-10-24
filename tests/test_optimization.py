"""
Tests for shift optimization module.
"""
import pytest
from src.optimization.scheduler import ShiftOptimizer


@pytest.fixture
def sample_workers():
    """Sample workers for testing."""
    return [
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
        },
        {
            "id": 3,
            "name": "Alice Johnson",
            "country": "SG",
            "skills": ["morning", "afternoon", "night"],
            "max_shifts_per_week": 6,
            "unavailable_days": []
        }
    ]


@pytest.fixture
def shift_requirements():
    """Sample shift requirements."""
    return {
        "morning": 1,
        "afternoon": 1,
        "night": 1
    }


def test_optimizer_initialization():
    """Test optimizer can be initialized."""
    optimizer = ShiftOptimizer()
    assert optimizer is not None
    assert optimizer.config is not None


def test_optimize_schedule(sample_workers, shift_requirements):
    """Test schedule optimization."""
    optimizer = ShiftOptimizer()
    
    result = optimizer.optimize_schedule(
        workers=sample_workers,
        num_days=7,
        shift_requirements=shift_requirements
    )
    
    assert result is not None
    assert 'status' in result
    assert result['status'] in ['optimal', 'feasible', 'infeasible']
    
    if result['status'] in ['optimal', 'feasible']:
        assert 'schedule' in result
        assert len(result['schedule']) == 7


def test_validate_schedule(sample_workers):
    """Test schedule validation."""
    optimizer = ShiftOptimizer()
    
    # Create a simple schedule
    schedule = [
        {
            "day": 0,
            "shifts": {
                "morning": [{"worker_id": 1, "worker_name": "John Doe", "country": "US"}],
                "afternoon": [{"worker_id": 2, "worker_name": "Jane Smith", "country": "UK"}],
                "night": [{"worker_id": 3, "worker_name": "Alice Johnson", "country": "SG"}]
            }
        }
    ]
    
    result = optimizer.validate_schedule(schedule, sample_workers)
    
    assert result is not None
    assert 'valid' in result
    assert 'violations' in result
