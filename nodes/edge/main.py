"""
Edge Node Simulator
Simulates edge computing with low latency, medium compute capacity
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

app = FastAPI(title="Edge Node", version="1.0.0")


class TaskExecution(BaseModel):
    """Task execution request"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]


@app.post("/execute")
async def execute_task(task: TaskExecution) -> Dict[str, Any]:
    """
    Execute task on edge node
    
    Characteristics:
    - Low latency (50-150ms)
    - Medium compute capacity
    - Low cost ($0.01 per task)
    """
    
    logger.info(f"Edge node executing task {task.task_id}: {task.task_type}")
    
    start_time = time.time()
    
    # Simulate edge processing
    # Edge nodes are fast but have limited compute
    base_latency = random.uniform(0.05, 0.15)  # 50-150ms
    
    # Some task types are faster on edge
    task_multipliers = {
        "fraud_detection": 0.8,  # Optimized for edge
        "sensor_alert": 0.6,      # Very fast on edge
        "image_classification": 1.5,  # Slower without GPU
        "ml_training": 2.0,       # Not ideal for edge
        "daily_report": 1.2       # Medium complexity
    }
    
    multiplier = task_multipliers.get(task.task_type, 1.0)
    processing_time = base_latency * multiplier
    
    # Simulate work
    await asyncio.sleep(processing_time)
    
    execution_time = time.time() - start_time
    
    # Cost calculation (edge is cheapest)
    cost = 0.01 * multiplier
    
    result = {
        "status": "success",
        "node": "EDGE",
        "task_id": task.task_id,
        "task_type": task.task_type,
        "execution_time": round(execution_time, 3),
        "cost": round(cost, 4),
        "message": f"Task {task.task_type} completed on edge node",
        "metadata": {
            "node_type": "edge",
            "latency": "low",
            "compute": "medium",
            "location": "edge-datacenter-01"
        }
    }
    
    logger.info(f"Edge task {task.task_id} completed in {execution_time:.3f}s")
    
    return result


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "node": "EDGE",
        "capabilities": ["low-latency", "real-time", "iot-optimized"]
    }


@app.get("/")
async def root():
    """Node information"""
    return {
        "node": "EDGE",
        "type": "edge-compute",
        "characteristics": {
            "latency": "low (50-150ms)",
            "compute": "medium",
            "cost": "low ($0.01/task)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
