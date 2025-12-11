# Quick setup and start script for AI Orchestrator (Windows)

Write-Host "========================================"
Write-Host " AI Workload Orchestrator - Setup"
Write-Host "========================================"

# Step 1: Train ML Model
Write-Host ""
Write-Host "Step 1: Training ML Model..."
Set-Location orchestrator

if (-not (Test-Path "models\model.pkl")) {
    Write-Host "Installing dependencies..."
    pip install -r requirements.txt
    
    Write-Host "Training RandomForest classifier..."
    python ai\train_model.py
    
    if (-not (Test-Path "models\model.pkl")) {
        Write-Host "ERROR: Model training failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Model trained successfully" -ForegroundColor Green
} else {
    Write-Host "✓ Model already exists" -ForegroundColor Green
}

Set-Location ..

# Step 2: Start Docker Services
Write-Host ""
Write-Host "Step 2: Starting Docker services..."
docker-compose down
docker-compose up --build -d

Write-Host ""
Write-Host "========================================"
Write-Host " AI Orchestrator Started!"
Write-Host "========================================"
Write-Host ""
Write-Host "Access Points:"
Write-Host "  Demo UI:          http://localhost:8501"
Write-Host "  Admin Dashboard:  http://localhost:8502"
Write-Host "  Orchestrator API: http://localhost:8000"
Write-Host "  Grafana:          http://localhost:3000 (admin/admin)"
Write-Host "  Prometheus:       http://localhost:9090"
Write-Host ""
Write-Host "View logs: docker-compose logs -f"
Write-Host "Stop: docker-compose down"
Write-Host ""
