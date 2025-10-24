"""
Main entry point for the Rostering Agent application.
Provides CLI interface for starting services and running optimizations.
"""
import argparse
import json
from pathlib import Path

from src.optimization.scheduler import ShiftOptimizer
from src.compliance.checker import ComplianceChecker
from src.tracking.mlflow_tracker import ExperimentTracker


def load_json_file(filepath: str):
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def optimize_from_files(workers_file: str, requirements_file: str, num_days: int):
    """Run optimization from JSON files."""
    # Load data
    workers = load_json_file(workers_file)
    requirements_data = load_json_file(requirements_file)
    shift_requirements = requirements_data.get('demand', requirements_data)
    
    # Initialize components
    optimizer = ShiftOptimizer()
    tracker = ExperimentTracker()
    compliance_checker = ComplianceChecker()
    
    print(f"Optimizing schedule for {len(workers)} workers over {num_days} days...")
    
    # Optimize
    result = optimizer.optimize_schedule(
        workers=workers,
        num_days=num_days,
        shift_requirements=shift_requirements
    )
    
    print(f"\nOptimization Status: {result['status']}")
    
    if result['status'] in ['optimal', 'feasible']:
        print(f"Objective Value: {result.get('objective_value', 'N/A')}")
        print(f"Solve Time: {result.get('solve_time', 0):.2f}s")
        
        # Check compliance
        print("\nChecking compliance...")
        compliance = compliance_checker.check_compliance(
            schedule=result['schedule'],
            workers=workers
        )
        
        print(f"Compliance: {'✅ PASS' if compliance['overall_compliant'] else '❌ FAIL'}")
        if not compliance['overall_compliant']:
            print(f"Violations: {len(compliance['violations'])}")
            for violation in compliance['violations'][:3]:  # Show first 3
                print(f"  - {violation.get('type', 'Unknown')}: {violation.get('description', 'N/A')}")
        
        # Track with MLflow
        print("\nTracking with MLflow...")
        params = {
            'num_workers': len(workers),
            'num_days': num_days,
        }
        run_id = tracker.log_optimization_run(params, result)
        print(f"MLflow Run ID: {run_id}")
        
        # Save schedule
        output_file = "schedule_output.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nSchedule saved to: {output_file}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='AI-Driven Multi-Country Rostering Agent'
    )
    
    parser.add_argument(
        'command',
        choices=['optimize', 'api', 'dashboard'],
        help='Command to run'
    )
    
    parser.add_argument(
        '--workers',
        default='data/sample/workers.json',
        help='Path to workers JSON file'
    )
    
    parser.add_argument(
        '--requirements',
        default='data/sample/requirements.json',
        help='Path to requirements JSON file'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=14,
        help='Number of days to schedule'
    )
    
    args = parser.parse_args()
    
    if args.command == 'optimize':
        optimize_from_files(args.workers, args.requirements, args.days)
    elif args.command == 'api':
        print("Starting FastAPI server...")
        import uvicorn
        from src.api.main import app
        uvicorn.run(app, host="0.0.0.0", port=8000)
    elif args.command == 'dashboard':
        print("Starting Streamlit dashboard...")
        import subprocess
        subprocess.run([
            'streamlit', 'run', 'src/dashboard/app.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0'
        ])


if __name__ == '__main__':
    main()
