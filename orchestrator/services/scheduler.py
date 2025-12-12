"""
Scheduler - Dispatches tasks to appropriate compute nodes
"""

import httpx
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


import os

class Scheduler:
    """Handles task dispatching to compute nodes"""
    
    NODE_URLS = {
        "EDGE": os.getenv("EDGE_NODE_URL", "http://localhost:8001"),
        "CLOUD": os.getenv("CLOUD_NODE_URL", "http://localhost:8002"),
        "GPU": os.getenv("GPU_NODE_URL", "http://localhost:8003")
    }
    
    def __init__(self, timeout: float = 30.0):
        """Initialize scheduler with timeout settings"""
        self.timeout = timeout
    
    async def dispatch_task(
        self,
        node: str,
        task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Dispatch task to the specified compute node
        
        Args:
            node: Target node name (EDGE, CLOUD, or GPU)
            task_data: Task payload to execute
        
        Returns:
            Execution result from the node
        """
        
        if node not in self.NODE_URLS:
            raise ValueError(f"Unknown node: {node}")
        
        url = f"{self.NODE_URLS[node]}/execute"
        
        logger.info(f"Dispatching task to {node} node at {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=task_data)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Task completed on {node}: {result.get('status')}")
                
                return result
                
        except httpx.TimeoutException:
            logger.error(f"Timeout while executing task on {node}")
            return {
                "status": "error",
                "error": f"Timeout after {self.timeout}s",
                "node": node,
                "execution_time": self.timeout,
                "cost": 0.0
            }
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from {node}: {e.response.status_code}")
            return {
                "status": "error",
                "error": f"HTTP {e.response.status_code}",
                "node": node,
                "execution_time": 0.0,
                "cost": 0.0
            }
        
        except Exception as e:
            logger.error(f"Error dispatching to {node}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "node": node,
                "execution_time": 0.0,
                "cost": 0.0
            }


# Singleton instance
_scheduler = None


def get_scheduler() -> Scheduler:
    """Get or create singleton scheduler"""
    
    global _scheduler
    
    if _scheduler is None:
        _scheduler = Scheduler()
    
    return _scheduler
