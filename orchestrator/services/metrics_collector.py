"""
Metrics Collector - Provides simulated system metrics
"""

import random
import time
from typing import Dict
from datetime import datetime


class MetricsCollector:
    """Simulates real-time system metrics for decision making"""
    
    def __init__(self):
        """Initialize with baseline metrics"""
        
        self.start_time = time.time()
        
        # Simulate varying loads over time
        self.base_edge_load = 45.0
        self.base_cloud_load = 55.0
        self.base_gpu_load = 35.0
        
        # Track task counts for load simulation
        self.edge_tasks = 0
        self.cloud_tasks = 0
        self.gpu_tasks = 0
    
    def get_metrics(self) -> Dict[str, float]:
        """
        Get current system metrics
        
        Returns:
            Dictionary with node loads, latency, and cost multipliers
        """
        
        # Add time-based variation (simulate daily patterns)
        time_factor = (time.time() - self.start_time) / 100.0
        time_variation = 10 * abs(time_factor % 2.0 - 1.0)  # Oscillates 0-10
        
        # Simulate load with random noise and task-based increases
        edge_load = min(100, self.base_edge_load + time_variation + 
                       random.uniform(-5, 5) + (self.edge_tasks * 2))
        
        cloud_load = min(100, self.base_cloud_load + time_variation +
                        random.uniform(-5, 5) + (self.cloud_tasks * 1.5))
        
        gpu_load = min(100, self.base_gpu_load + time_variation +
                      random.uniform(-5, 5) + (self.gpu_tasks * 3))
        
        # Network latency varies based on congestion
        base_latency = 100
        congestion_factor = (edge_load + cloud_load) / 100.0
        network_latency = base_latency * (1 + congestion_factor) + random.uniform(-20, 20)
        
        # Cost multipliers (normalized)
        edge_cost = 1.0
        cloud_cost = 2.5
        gpu_cost = 5.0
        
        return {
            "edge_load": round(edge_load, 2),
            "cloud_load": round(cloud_load, 2),
            "gpu_load": round(gpu_load, 2),
            "network_latency": round(max(10, network_latency), 2),
            "edge_cost_multiplier": edge_cost,
            "cloud_cost_multiplier": cloud_cost,
            "gpu_cost_multiplier": gpu_cost,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def record_task_execution(self, node: str) -> None:
        """Record task execution to simulate load changes"""
        
        if node == "EDGE":
            self.edge_tasks += 1
        elif node == "CLOUD":
            self.cloud_tasks += 1
        elif node == "GPU":
            self.gpu_tasks += 1
        
        # Decay old tasks (simulate completion)
        if random.random() < 0.3:
            self.edge_tasks = max(0, self.edge_tasks - 1)
            self.cloud_tasks = max(0, self.cloud_tasks - 1)
            self.gpu_tasks = max(0, self.gpu_tasks - 1)
    
    def get_node_status(self) -> Dict[str, Dict[str, any]]:
        """Get detailed status for each node"""
        
        metrics = self.get_metrics()
        
        def get_health_status(load: float) -> str:
            """Determine health status based on load"""
            if load < 60:
                return "healthy"
            elif load < 80:
                return "warning"
            else:
                return "critical"
        
        return {
            "EDGE": {
                "load": metrics["edge_load"],
                "latency": round(50 + random.uniform(-20, 20), 2),
                "cost_per_task": 0.01,
                "health": get_health_status(metrics["edge_load"]),
                "active_tasks": self.edge_tasks
            },
            "CLOUD": {
                "load": metrics["cloud_load"],
                "latency": round(250 + random.uniform(-50, 50), 2),
                "cost_per_task": 0.025,
                "health": get_health_status(metrics["cloud_load"]),
                "active_tasks": self.cloud_tasks
            },
            "GPU": {
                "load": metrics["gpu_load"],
                "latency": round(400 + random.uniform(-100, 100), 2),
                "cost_per_task": 0.05,
                "health": get_health_status(metrics["gpu_load"]),
                "active_tasks": self.gpu_tasks
            }
        }


# Singleton instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create singleton metrics collector"""
    
    global _metrics_collector
    
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    
    return _metrics_collector
