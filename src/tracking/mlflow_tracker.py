"""
MLflow experiment tracking for optimization runs.
"""
from typing import Dict, Any, Optional
import os
from datetime import datetime

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None


class ExperimentTracker:
    """Track optimization experiments with MLflow."""
    
    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        experiment_name: str = "rostering_optimization"
    ):
        """Initialize MLflow tracking."""
        if not MLFLOW_AVAILABLE:
            print("Warning: MLflow not installed. Experiment tracking disabled.")
            self.experiment_id = None
            return
            
        self.tracking_uri = tracking_uri or os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')
        self.experiment_name = experiment_name
        
        mlflow.set_tracking_uri(self.tracking_uri)
        
        # Create or get experiment
        try:
            self.experiment = mlflow.get_experiment_by_name(experiment_name)
            if self.experiment is None:
                self.experiment_id = mlflow.create_experiment(experiment_name)
            else:
                self.experiment_id = self.experiment.experiment_id
            mlflow.set_experiment(experiment_name)
        except Exception as e:
            print(f"Warning: Could not set up MLflow experiment: {e}")
            self.experiment_id = None
    
    def start_run(self, run_name: Optional[str] = None) -> str:
        """Start a new MLflow run."""
        if not MLFLOW_AVAILABLE or self.experiment_id is None:
            return "no_tracking"
            
        if run_name is None:
            run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            mlflow.start_run(run_name=run_name)
            return mlflow.active_run().info.run_id
        except Exception as e:
            print(f"Warning: Could not start MLflow run: {e}")
            return "no_tracking"
    
    def log_parameters(self, params: Dict[str, Any]):
        """Log parameters to MLflow."""
        if not MLFLOW_AVAILABLE:
            return
        try:
            for key, value in params.items():
                mlflow.log_param(key, value)
        except Exception as e:
            print(f"Warning: Could not log parameters: {e}")
    
    def log_metrics(self, metrics: Dict[str, float]):
        """Log metrics to MLflow."""
        if not MLFLOW_AVAILABLE:
            return
        try:
            for key, value in metrics.items():
                mlflow.log_metric(key, value)
        except Exception as e:
            print(f"Warning: Could not log metrics: {e}")
    
    def log_artifact(self, artifact_path: str):
        """Log an artifact file to MLflow."""
        if not MLFLOW_AVAILABLE:
            return
        try:
            mlflow.log_artifact(artifact_path)
        except Exception as e:
            print(f"Warning: Could not log artifact: {e}")
    
    def log_schedule(self, schedule: Dict[str, Any]):
        """Log optimization schedule as artifact."""
        if not MLFLOW_AVAILABLE:
            return
        try:
            import json
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(schedule, f, indent=2)
                temp_path = f.name
            
            mlflow.log_artifact(temp_path, "schedules")
            
            # Clean up temp file
            os.remove(temp_path)
        except Exception as e:
            print(f"Warning: Could not log schedule: {e}")
    
    def end_run(self):
        """End the current MLflow run."""
        if not MLFLOW_AVAILABLE:
            return
        try:
            mlflow.end_run()
        except Exception as e:
            print(f"Warning: Could not end MLflow run: {e}")
    
    def log_optimization_run(
        self,
        params: Dict[str, Any],
        result: Dict[str, Any],
        run_name: Optional[str] = None
    ):
        """
        Log a complete optimization run.
        
        Args:
            params: Optimization parameters
            result: Optimization results
            run_name: Optional run name
        """
        if not MLFLOW_AVAILABLE or self.experiment_id is None:
            return "no_tracking"
            
        run_id = self.start_run(run_name)
        
        try:
            # Log parameters
            self.log_parameters(params)
            
            # Log metrics
            if 'statistics' in result:
                self.log_metrics({
                    f"stat_{k}": v 
                    for k, v in result['statistics'].items()
                    if isinstance(v, (int, float))
                })
            
            if 'objective_value' in result:
                self.log_metrics({'objective_value': result['objective_value']})
            
            if 'solve_time' in result:
                self.log_metrics({'solve_time': result['solve_time']})
            
            # Log schedule as artifact
            if 'schedule' in result:
                self.log_schedule(result)
            
            # Log status
            if MLFLOW_AVAILABLE:
                mlflow.log_param('status', result.get('status', 'unknown'))
            
        finally:
            self.end_run()
        
        return run_id
