"""
Cloud Node Simulator
Simulates cloud computing with moderate latency, high compute capacity
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import asyncio
import random
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cloud Node", version="1.0.0")


class TaskExecution(BaseModel):
    """Task execution request"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]


@app.post("/execute")
async def execute_task(task: TaskExecution) -> Dict[str, Any]:
    """
    Execute task on cloud node
    
    Characteristics:
    - Moderate latency (200-500ms)
    - High compute capacity
    - Medium cost ($0.025 per task)
    """
    
    logger.info(f"Cloud node executing task {task.task_id}: {task.task_type}")
    
    start_time = time.time()
    
    # Simulate cloud processing
    # Cloud has higher latency but excellent compute
    base_latency = random.uniform(0.2, 0.5)  # 200-500ms
    
    # Cloud excels at batch and compute-heavy tasks
    task_multipliers = {
        "fraud_detection": 1.0,
        "sensor_alert": 1.3,      # Not optimized for real-time
        "image_classification": 0.9,  # Good compute without GPU
        "ml_training": 1.1,       # Better with GPU but can handle
        "daily_report": 0.7       # Excellent for batch processing
    }
    
    multiplier = task_multipliers.get(task.task_type, 1.0)
    processing_time = base_latency * multiplier
    
    # Simulate work
    await asyncio.sleep(processing_time)
    
    execution_time = time.time() - start_time
    
    # Cost calculation (medium cost)
    cost = 0.025 * multiplier
    
    result = {
        "status": "success",
        "node": "CLOUD",
        "task_id": task.task_id,
        "task_type": task.task_type,
        "execution_time": round(execution_time, 3),
        "cost": round(cost, 4),
        "message": f"Task {task.task_type} completed on cloud node",
        "metadata": {
            "node_type": "cloud",
            "latency": "moderate",
            "compute": "high",
            "location": "cloud-region-us-east",
            "scalability": "high"
        }
    }
    
    logger.info(f"Cloud task {task.task_id} completed in {execution_time:.3f}s")
    
    return result


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "node": "CLOUD",
        "capabilities": ["high-compute", "scalable", "batch-processing"]
    }


@app.get("/")
async def root():
    """Node information"""
    return {
        "node": "CLOUD",
        "type": "cloud-compute",
        "characteristics": {
            "latency": "moderate (200-500ms)",
            "compute": "high",
            "cost": "medium ($0.025/task)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
