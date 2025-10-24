#!/bin/bash
# Start all services in the background

echo "Starting all services..."

# Create logs directory
mkdir -p logs

# Start MLflow
./scripts/start_mlflow.sh > logs/mlflow.log 2>&1 &
echo "MLflow started (PID: $!)"

# Wait for MLflow to initialize
sleep 3

# Start FastAPI
./scripts/start_api.sh > logs/api.log 2>&1 &
echo "FastAPI started (PID: $!)"

# Wait for API to initialize
sleep 3

# Start Streamlit
./scripts/start_dashboard.sh > logs/dashboard.log 2>&1 &
echo "Streamlit started (PID: $!)"

echo ""
echo "All services started!"
echo "- MLflow UI: http://localhost:5000"
echo "- FastAPI: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- Streamlit Dashboard: http://localhost:8501"
echo ""
echo "Logs are available in the logs/ directory"
