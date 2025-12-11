"""
GPU Node Simulator
Simulates GPU computing with higher base latency but exceptional compute for ML tasks
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

app = FastAPI(title="GPU Node", version="1.0.0")


class TaskExecution(BaseModel):
    """Task execution request"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]


@app.post("/execute")
async def execute_task(task: TaskExecution) -> Dict[str, Any]:
    """
    Execute task on GPU node
    
    Characteristics:
    - Higher initial latency (300-600ms)
    - Very high compute capacity (GPU-accelerated)
    - Highest cost ($0.05 per task)
    - Specialized for ML/AI workloads
    """
    
    logger.info(f"GPU node executing task {task.task_id}: {task.task_type}")
    
    start_time = time.time()
    
    # Simulate GPU processing
    # Higher initial latency but massive speedup for GPU tasks
    base_latency = random.uniform(0.3, 0.6)  # 300-600ms
    
    # GPU dramatically accelerates certain workloads
    task_multipliers = {
        "fraud_detection": 1.2,   # Better on edge
        "sensor_alert": 1.5,      # Overkill for simple tasks
        "image_classification": 0.4,  # GPU shines here!
        "ml_training": 0.3,       # Massive GPU acceleration
        "daily_report": 1.3       # Not GPU-optimized
    }
    
    multiplier = task_multipliers.get(task.task_type, 1.0)
    processing_time = base_latency * multiplier
    
    # Simulate GPU work
    await asyncio.sleep(processing_time)
    
    execution_time = time.time() - start_time
    
    # Cost calculation (highest cost but worth it for GPU tasks)
    cost = 0.05 * multiplier
    
    # Special GPU metadata
    gpu_utilization = random.uniform(60, 95) if multiplier < 1.0 else random.uniform(20, 40)
    
    result = {
        "status": "success",
        "node": "GPU",
        "task_id": task.task_id,
        "task_type": task.task_type,
        "execution_time": round(execution_time, 3),
        "cost": round(cost, 4),
        "message": f"Task {task.task_type} completed on GPU node with acceleration",
        "metadata": {
            "node_type": "gpu",
            "latency": "moderate-high",
            "compute": "very-high",
            "gpu_model": "NVIDIA A100",
            "gpu_utilization": round(gpu_utilization, 1),
            "cuda_cores": 6912,
            "location": "gpu-cluster-01"
        }
    }
    
    logger.info(
        f"GPU task {task.task_id} completed in {execution_time:.3f}s "
        f"(GPU utilization: {gpu_utilization:.1f}%)"
    )
    
    return result


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "node": "GPU",
        "capabilities": ["gpu-accelerated", "ml-optimized", "deep-learning", "image-processing"]
    }


@app.get("/")
async def root():
    """Node information"""
    return {
        "node": "GPU",
        "type": "gpu-compute",
        "characteristics": {
            "latency": "moderate-high (300-600ms base)",
            "compute": "very-high (GPU-accelerated)",
            "cost": "high ($0.05/task)",
            "specialization": "ML/AI workloads"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
