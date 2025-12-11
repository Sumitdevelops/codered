#!/bin/bash
# Quick setup and start script for AI Orchestrator

echo "========================================"
echo " AI Workload Orchestrator - Setup"
echo "========================================"

# Step 1: Train ML Model
echo ""
echo "Step 1: Training ML Model..."
cd orchestrator

if [ ! -f "models/model.pkl" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    echo "Training RandomForest classifier..."
    python ai/train_model.py
    
    if [ ! -f "models/model.pkl" ]; then
        echo "ERROR: Model training failed!"
        exit 1
    fi
    echo "✓ Model trained successfully"
else
    echo "✓ Model already exists"
fi

cd ..

# Step 2: Start Docker Services
echo ""
echo "Step 2: Starting Docker services..."
docker-compose down
docker-compose up --build -d

echo ""
echo "========================================"
echo " AI Orchestrator Started!"
echo "========================================"
echo ""
echo "Access Points:"
echo "  Demo UI:         http://localhost:8501"
echo "  Admin Dashboard: http://localhost:8502"
echo "  Orchestrator API: http://localhost:8000"
echo "  Grafana:         http://localhost:3000 (admin/admin)"
echo "  Prometheus:      http://localhost:9090"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop: docker-compose down"
echo ""
