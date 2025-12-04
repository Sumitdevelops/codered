import random
import time
import asyncio
from typing import List
from models import Node, NodeMetrics, NodeType, NodeStatus

class NodeSimulator:
    def __init__(self, nodes: List[Node]):
        self.nodes = nodes
        self.running = False

    def _generate_initial_metrics(self, node_type: NodeType) -> NodeMetrics:
        if node_type == NodeType.EDGE:
            return NodeMetrics(
                cpu_usage=random.uniform(10, 40),
                ram_usage=random.uniform(20, 50),
                latency_ms=random.uniform(5, 20), # Low latency
                power_consumption=random.uniform(10, 30),
                cost_per_hour=0.5
            )
        elif node_type == NodeType.CLOUD:
            return NodeMetrics(
                cpu_usage=random.uniform(20, 60),
                ram_usage=random.uniform(30, 70),
                latency_ms=random.uniform(50, 150), # Higher latency
                power_consumption=random.uniform(100, 200),
                cost_per_hour=2.0
            )
        elif node_type == NodeType.GPU:
            return NodeMetrics(
                cpu_usage=random.uniform(10, 50),
                ram_usage=random.uniform(40, 80),
                latency_ms=random.uniform(60, 160),
                power_consumption=random.uniform(200, 400),
                cost_per_hour=5.0,
                available_gpu_memory=random.uniform(4, 16)
            )
        return NodeMetrics(cpu_usage=0, ram_usage=0, latency_ms=0, power_consumption=0, cost_per_hour=0)

    def update_metrics(self):
        """Random walk simulation for metrics"""
        for node in self.nodes:
            if node.status == NodeStatus.OFFLINE:
                continue
            
            # Fluctuate CPU
            change = random.uniform(-5, 5)
            node.metrics.cpu_usage = max(0, min(100, node.metrics.cpu_usage + change))
            
            # Fluctuate RAM
            change = random.uniform(-2, 2)
            node.metrics.ram_usage = max(0, min(100, node.metrics.ram_usage + change))
            
            # Fluctuate Latency (occasional spikes)
            if random.random() < 0.05: # 5% chance of spike
                node.metrics.latency_ms += random.uniform(50, 200)
            else:
                # Return to baseline slowly
                baseline = 10 if node.type == NodeType.EDGE else 80
                node.metrics.latency_ms = (node.metrics.latency_ms * 0.9) + (baseline * 0.1)

    async def run_simulation(self):
        self.running = True
        while self.running:
            self.update_metrics()
            await asyncio.sleep(2) # Update every 2 seconds

    def stop(self):
        self.running = False
