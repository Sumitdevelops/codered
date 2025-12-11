"""
Metrics and monitoring endpoints
"""

from fastapi import APIRouter
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import logging

from services.metrics_collector import get_metrics_collector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["metrics"])

# Prometheus metrics
task_counter = Counter(
    'orchestrator_tasks_total',
    'Total number of tasks processed',
    ['node', 'status']
)

task_duration = Histogram(
    'orchestrator_task_duration_seconds',
    'Task execution duration',
    ['node']
)

task_cost = Histogram(
    'orchestrator_task_cost_dollars',
    'Task execution cost',
    ['node']
)

node_load_gauge = Gauge(
    'orchestrator_node_load_percent',
    'Current node load percentage',
    ['node']
)


@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    
    # Update node load gauges
    metrics_collector = get_metrics_collector()
    node_status = metrics_collector.get_node_status()
    
    for node_name, status in node_status.items():
        node_load_gauge.labels(node=node_name).set(status['load'])
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/node-status")
async def get_node_status():
    """Get current status of all compute nodes"""
    
    try:
        metrics_collector = get_metrics_collector()
        status = metrics_collector.get_node_status()
        
        return {
            "nodes": status,
            "timestamp": metrics_collector.get_metrics()['timestamp']
        }
    
    except Exception as e:
        logger.error(f"Error fetching node status: {str(e)}")
        return {"error": str(e)}


@router.get("/system-metrics")
async def get_system_metrics():
    """Get current system-wide metrics"""
    
    try:
        metrics_collector = get_metrics_collector()
        metrics = metrics_collector.get_metrics()
        
        return metrics
    
    except Exception as e:
        logger.error(f"Error fetching system metrics: {str(e)}")
        return {"error": str(e)}
