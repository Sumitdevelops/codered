"""
Task routing endpoints for the orchestrator
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid
import logging

from ai.decision_engine import get_decision_engine
from services.metrics_collector import get_metrics_collector
from services.scheduler import get_scheduler
from utils.database import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tasks"])


class TaskSubmission(BaseModel):
    """Task submission request model"""
    
    taskType: str = Field(..., description="Type of task (e.g., fraud_detection, image_classification)")
    priority: int = Field(5, ge=1, le=10, description="Task priority (1-10)")
    latency: int = Field(5, ge=1, le=10, description="Latency requirement (1-10, higher = more sensitive)")
    requiresGPU: bool = Field(False, description="Whether task requires GPU")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Task payload data")
    cost_sensitivity: Optional[int] = Field(5, ge=1, le=10, description="Cost sensitivity (1-10)")


class TaskResponse(BaseModel):
    """Task submission response model"""
    
    task_id: str
    chosen_node: str
    confidence: float
    explanation: str
    execution_time: float
    cost: float
    status: str
    node_response: Dict[str, Any]


@router.post("/submit-task", response_model=TaskResponse)
async def submit_task(task: TaskSubmission) -> TaskResponse:
    """
    Submit a task for routing and execution
    
    This endpoint:
    1. Collects current system metrics
    2. Uses ML model to decide optimal node
    3. Dispatches task to selected node
    4. Logs execution results
    5. Returns complete execution details
    """
    
    task_id = str(uuid.uuid4())
    
    logger.info(f"Received task {task_id}: {task.taskType}")
    
    try:
        # Get decision engine and metrics collector
        decision_engine = get_decision_engine()
        metrics_collector = get_metrics_collector()
        scheduler = get_scheduler()
        db = await get_database()
        
        # Collect current metrics
        system_metrics = metrics_collector.get_metrics()
        logger.info(f"System metrics: {system_metrics}")
        
        # Make routing decision
        task_metadata = task.model_dump()
        decision = decision_engine.decide(task_metadata, system_metrics)
        
        logger.info(
            f"Decision for {task_id}: {decision['best_node']} "
            f"(confidence: {decision['confidence']:.2%})"
        )
        
        # Dispatch to selected node
        chosen_node = decision['best_node']
        execution_result = await scheduler.dispatch_task(
            chosen_node,
            {
                "task_id": task_id,
                "task_type": task.taskType,
                "payload": task.payload or {}
            }
        )
        
        # Update metrics with task execution
        metrics_collector.record_task_execution(chosen_node)
        
        # Log to database
        await db.log_task(task_id, task_metadata, decision, execution_result)
        
        logger.info(
            f"Task {task_id} completed on {chosen_node}: "
            f"{execution_result.get('execution_time', 0):.3f}s, "
            f"${execution_result.get('cost', 0):.4f}"
        )
        
        return TaskResponse(
            task_id=task_id,
            chosen_node=chosen_node,
            confidence=decision['confidence'],
            explanation=decision['explanation'],
            execution_time=execution_result.get('execution_time', 0.0),
            cost=execution_result.get('cost', 0.0),
            status=execution_result.get('status', 'unknown'),
            node_response=execution_result
        )
    
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task-history")
async def get_task_history(limit: int = 100, node: Optional[str] = None):
    """
    Retrieve task execution history
    
    Query parameters:
    - limit: Maximum number of records to return (default: 100)
    - node: Filter by node name (EDGE, CLOUD, GPU)
    """
    
    try:
        db = await get_database()
        history = await db.get_task_history(limit=limit, node=node)
        
        return {
            "total": len(history),
            "tasks": history
        }
    
    except Exception as e:
        logger.error(f"Error fetching task history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics():
    """Get aggregated task statistics"""
    
    try:
        db = await get_database()
        stats = await db.get_statistics()
        
        return stats
    
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
