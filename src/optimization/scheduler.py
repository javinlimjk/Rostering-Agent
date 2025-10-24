"""
Shift optimization using OR-Tools CP-SAT solver.
"""
from typing import List, Dict, Any, Optional
from ortools.sat.python import cp_model
import yaml
from pathlib import Path


class ShiftOptimizer:
    """Optimizes shift assignments using constraint programming."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the optimizer with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
    def optimize_schedule(
        self, 
        workers: List[Dict[str, Any]], 
        num_days: int,
        shift_requirements: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Optimize shift schedule for given workers and requirements.
        
        Args:
            workers: List of worker dictionaries with id, name, country, skills
            num_days: Number of days to schedule
            shift_requirements: Daily demand for each shift type
            
        Returns:
            Dictionary with schedule and optimization statistics
        """
        shift_types = list(shift_requirements.keys())
        num_workers = len(workers)
        num_shifts = len(shift_types)
        
        # Create shift variables: shifts[(w, d, s)] = 1 if worker w works shift s on day d
        shifts = {}
        for w in range(num_workers):
            for d in range(num_days):
                for s in range(num_shifts):
                    shifts[(w, d, s)] = self.model.NewBoolVar(f'shift_w{w}_d{d}_s{s}')
        
        # Constraint 1: Meet shift requirements
        for d in range(num_days):
            for s, shift_type in enumerate(shift_types):
                required = shift_requirements[shift_type]
                # Only workers with the skill can work this shift
                eligible_workers = [
                    w for w in range(num_workers) 
                    if shift_type in workers[w]['skills']
                ]
                # Exactly meet the requirement (not more, not less)
                self.model.Add(
                    sum(shifts[(w, d, s)] for w in eligible_workers) == required
                )
        
        # Constraint 2: Each worker works at most one shift per day
        for w in range(num_workers):
            for d in range(num_days):
                self.model.Add(sum(shifts[(w, d, s)] for s in range(num_shifts)) <= 1)
        
        # Constraint 3: Respect worker availability
        for w, worker in enumerate(workers):
            for d in worker.get('unavailable_days', []):
                if 0 <= d < num_days:
                    for s in range(num_shifts):
                        self.model.Add(shifts[(w, d, s)] == 0)
        
        # Constraint 4: Min/Max shifts per worker
        opt_config = self.config.get('optimization', {})
        min_shifts = opt_config.get('min_shifts_per_worker', 8)
        max_shifts = opt_config.get('max_shifts_per_worker', 10)
        
        for w, worker in enumerate(workers):
            total_shifts = sum(
                shifts[(w, d, s)] 
                for d in range(num_days) 
                for s in range(num_shifts)
            )
            self.model.Add(total_shifts >= min_shifts)
            self.model.Add(total_shifts <= max_shifts)
            
            # Per week limit
            max_per_week = worker.get('max_shifts_per_week', 5)
            for week_start in range(0, num_days, 7):
                week_end = min(week_start + 7, num_days)
                week_shifts = sum(
                    shifts[(w, d, s)]
                    for d in range(week_start, week_end)
                    for s in range(num_shifts)
                )
                self.model.Add(week_shifts <= max_per_week)
        
        # Constraint 5: No consecutive day limit (country-specific)
        for w, worker in enumerate(workers):
            country = worker.get('country', 'US')
            country_config = self.config['countries'].get(country, {})
            max_consecutive = country_config.get('max_consecutive_days', 6)
            
            for d in range(num_days - max_consecutive):
                consecutive_work = sum(
                    shifts[(w, d + i, s)]
                    for i in range(max_consecutive + 1)
                    for s in range(num_shifts)
                )
                # If working max_consecutive+1 days, at least one must be off
                self.model.Add(consecutive_work <= max_consecutive)
        
        # Objective: Minimize variation in shift distribution
        shift_counts = []
        for w in range(num_workers):
            shift_count = self.model.NewIntVar(0, num_days * num_shifts, f'count_w{w}')
            self.model.Add(
                shift_count == sum(
                    shifts[(w, d, s)] 
                    for d in range(num_days) 
                    for s in range(num_shifts)
                )
            )
            shift_counts.append(shift_count)
        
        # Minimize maximum shifts (load balancing)
        max_shifts_var = self.model.NewIntVar(0, num_days * num_shifts, 'max_shifts')
        for count in shift_counts:
            self.model.Add(max_shifts_var >= count)
        
        self.model.Minimize(max_shifts_var)
        
        # Solve
        time_limit = opt_config.get('solver_time_limit_seconds', 300)
        self.solver.parameters.max_time_in_seconds = time_limit
        
        status = self.solver.Solve(self.model)
        
        # Build result
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            schedule = []
            for d in range(num_days):
                day_schedule = {'day': d, 'shifts': {}}
                for s, shift_type in enumerate(shift_types):
                    day_schedule['shifts'][shift_type] = []
                    for w in range(num_workers):
                        if self.solver.Value(shifts[(w, d, s)]) == 1:
                            day_schedule['shifts'][shift_type].append({
                                'worker_id': workers[w]['id'],
                                'worker_name': workers[w]['name'],
                                'country': workers[w]['country']
                            })
                schedule.append(day_schedule)
            
            return {
                'status': 'optimal' if status == cp_model.OPTIMAL else 'feasible',
                'schedule': schedule,
                'objective_value': self.solver.ObjectiveValue(),
                'solve_time': self.solver.WallTime(),
                'statistics': {
                    'num_workers': num_workers,
                    'num_days': num_days,
                    'num_shifts': num_shifts
                }
            }
        else:
            return {
                'status': 'infeasible',
                'error': 'Could not find a feasible solution',
                'statistics': {
                    'num_workers': num_workers,
                    'num_days': num_days,
                    'num_shifts': num_shifts
                }
            }
    
    def validate_schedule(
        self,
        schedule: List[Dict[str, Any]],
        workers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate a schedule against labour law constraints.
        
        Args:
            schedule: List of daily schedules
            workers: List of worker dictionaries
            
        Returns:
            Dictionary with validation results and violations
        """
        violations = []
        worker_hours = {w['id']: [] for w in workers}
        worker_map = {w['id']: w for w in workers}
        
        # Track shifts per worker
        for day_idx, day in enumerate(schedule):
            for shift_type, assignments in day['shifts'].items():
                shift_hours = self.config['shifts'][shift_type]['duration_hours']
                for assignment in assignments:
                    worker_id = assignment['worker_id']
                    worker_hours[worker_id].append({
                        'day': day_idx,
                        'shift_type': shift_type,
                        'hours': shift_hours
                    })
        
        # Check constraints for each worker
        for worker_id, shifts in worker_hours.items():
            worker = worker_map[worker_id]
            country = worker.get('country', 'US')
            country_config = self.config['countries'].get(country, {})
            
            # Check weekly hours
            max_hours = country_config.get('max_hours_per_week', 40)
            for week_start in range(0, len(schedule), 7):
                week_end = min(week_start + 7, len(schedule))
                week_shifts = [s for s in shifts if week_start <= s['day'] < week_end]
                week_hours = sum(s['hours'] for s in week_shifts)
                
                if week_hours > max_hours:
                    violations.append({
                        'worker_id': worker_id,
                        'worker_name': worker['name'],
                        'type': 'weekly_hours_exceeded',
                        'country': country,
                        'limit': max_hours,
                        'actual': week_hours,
                        'week': week_start // 7
                    })
            
            # Check consecutive days
            max_consecutive = country_config.get('max_consecutive_days', 6)
            if shifts:
                working_days = sorted(set(s['day'] for s in shifts))
                consecutive_count = 1
                for i in range(1, len(working_days)):
                    if working_days[i] == working_days[i-1] + 1:
                        consecutive_count += 1
                        if consecutive_count > max_consecutive:
                            violations.append({
                                'worker_id': worker_id,
                                'worker_name': worker['name'],
                                'type': 'consecutive_days_exceeded',
                                'country': country,
                                'limit': max_consecutive,
                                'actual': consecutive_count,
                                'ending_day': working_days[i]
                            })
                    else:
                        consecutive_count = 1
        
        return {
            'valid': len(violations) == 0,
            'violations': violations,
            'total_violations': len(violations)
        }
