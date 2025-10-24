"""
Example usage script demonstrating the Rostering Agent capabilities.
"""
import json
from src.optimization.scheduler import ShiftOptimizer
from src.compliance.checker import ComplianceChecker
from src.tracking.mlflow_tracker import ExperimentTracker


def main():
    """Run example optimization and validation."""
    print("=" * 60)
    print("AI-Driven Multi-Country Rostering Agent - Example Usage")
    print("=" * 60)
    
    # Load sample data
    print("\n1. Loading sample data...")
    with open('data/sample/workers.json') as f:
        workers = json.load(f)
    
    with open('data/sample/requirements.json') as f:
        requirements = json.load(f)
    
    print(f"   - Workers loaded: {len(workers)}")
    print(f"   - Countries: {set(w['country'] for w in workers)}")
    print(f"   - Shift requirements: {requirements['demand']}")
    
    # Initialize components
    print("\n2. Initializing components...")
    optimizer = ShiftOptimizer()
    compliance_checker = ComplianceChecker()
    tracker = ExperimentTracker()
    print("   ✓ All components initialized")
    
    # Run optimization
    print("\n3. Running shift optimization...")
    num_days = 14
    result = optimizer.optimize_schedule(
        workers=workers,
        num_days=num_days,
        shift_requirements=requirements['demand']
    )
    
    print(f"   Status: {result['status'].upper()}")
    if result['status'] in ['optimal', 'feasible']:
        print(f"   Solve Time: {result['solve_time']:.3f}s")
        print(f"   Objective Value: {result['objective_value']:.2f}")
        print(f"   Schedule Days: {len(result['schedule'])}")
        
        # Show sample day
        print("\n4. Sample Schedule (Day 1):")
        day1 = result['schedule'][0]
        for shift_type, assignments in day1['shifts'].items():
            if assignments:
                workers_list = [a['worker_name'] for a in assignments]
                countries = [a['country'] for a in assignments]
                print(f"   {shift_type.capitalize():12} -> {', '.join(workers_list):30} ({', '.join(countries)})")
        
        # Validate compliance
        print("\n5. Validating labour law compliance...")
        validation = compliance_checker.check_compliance(
            schedule=result['schedule'],
            workers=workers
        )
        
        if validation['overall_compliant']:
            print("   ✅ Schedule is COMPLIANT with labour laws")
            print(f"   Countries checked: {', '.join(validation['countries_checked'])}")
        else:
            print("   ❌ Schedule has compliance violations:")
            for violation in validation['violations'][:3]:
                print(f"      - {violation['type']}: {violation.get('description', 'N/A')}")
        
        # Track with MLflow
        print("\n6. Tracking experiment with MLflow...")
        params = {
            'num_workers': len(workers),
            'num_days': num_days,
            'shift_types': ','.join(requirements['demand'].keys())
        }
        run_id = tracker.log_optimization_run(params, result, run_name="example_run")
        if run_id and run_id != "no_tracking":
            print(f"   ✓ Logged to MLflow (Run ID: {run_id})")
        else:
            print("   ℹ MLflow tracking unavailable (install mlflow to enable)")
        
        # Save schedule
        output_file = "example_schedule.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n7. Schedule saved to: {output_file}")
        
        # Summary statistics
        print("\n" + "=" * 60)
        print("Summary Statistics:")
        print("=" * 60)
        
        # Count shifts per worker
        worker_shifts = {w['id']: 0 for w in workers}
        for day in result['schedule']:
            for shift_type, assignments in day['shifts'].items():
                for assignment in assignments:
                    worker_shifts[assignment['worker_id']] += 1
        
        print("\nShifts per Worker:")
        for worker in workers:
            shifts = worker_shifts[worker['id']]
            print(f"   {worker['name']:20} -> {shifts} shifts ({worker['country']})")
        
        # Count shifts by type
        shift_counts = {st: 0 for st in requirements['demand'].keys()}
        for day in result['schedule']:
            for shift_type, assignments in day['shifts'].items():
                shift_counts[shift_type] += len(assignments)
        
        print("\nShifts by Type:")
        for shift_type, count in shift_counts.items():
            print(f"   {shift_type.capitalize():12} -> {count} shifts")
        
        print("\n" + "=" * 60)
        print("✅ Example completed successfully!")
        print("=" * 60)
        
    else:
        print(f"   ❌ Optimization failed: {result.get('error', 'Unknown error')}")
        print("\nTips:")
        print("   - Try reducing shift requirements")
        print("   - Add more workers")
        print("   - Adjust constraints in config/config.yaml")


if __name__ == '__main__':
    main()
