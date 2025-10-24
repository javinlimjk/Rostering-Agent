#!/bin/bash
# Start Streamlit dashboard

echo "Starting Streamlit dashboard..."
cd "$(dirname "$0")/.."
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
