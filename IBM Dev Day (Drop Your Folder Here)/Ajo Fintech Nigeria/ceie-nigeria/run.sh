#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running data ingestion..."
python backend/ingest.py

echo "Starting FastAPI backend on port 8000..."
uvicorn backend.main:app --port 8000 &
UVICORN_PID=$!

echo "Starting Streamlit frontend on port 8501..."
streamlit run frontend/app.py

# Kill uvicorn on exit
kill $UVICORN_PID
