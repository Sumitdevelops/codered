"""
AI Workload Orchestrator - Main Application
FastAPI service for dynamic workload routing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from routes import tasks, metrics
from utils.logging import setup_logging
from utils.database import get_database

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Workload Orchestrator",
    description="Dynamic workload routing across Edge, Cloud, and GPU nodes using ML",
    version="1.0.0"
)

# CORS middleware for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router)
app.include_router(metrics.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    
    logger.info("="*60)
    logger.info("AI Workload Orchestrator Starting")
    logger.info("="*60)
    
    # Initialize database
    db = await get_database()
    logger.info("Database initialized")
    
    # Load ML model
    try:
        from ai.decision_engine import get_decision_engine
        decision_engine = get_decision_engine()
        logger.info("ML decision engine loaded")
    except Exception as e:
        logger.error(f"Failed to load decision engine: {str(e)}")
        logger.error("Please run 'python ai/train_model.py' first")
    
    logger.info("Orchestrator ready to receive tasks")
    logger.info("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Orchestrator shutting down")


@app.get("/")
async def root():
    """Root endpoint with service information"""
    
    return {
        "service": "AI Workload Orchestrator",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "submit_task": "/api/submit-task",
            "task_history": "/api/task-history",
            "statistics": "/api/statistics",
            "node_status": "/api/node-status",
            "system_metrics": "/api/system-metrics",
            "prometheus": "/api/metrics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
