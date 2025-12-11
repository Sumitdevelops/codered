import asyncio
import random
from typing import List
from models import Node, NodeStatus, NodeType, NodeMetrics, Workload

class NodeSimulator:
    def __init__(self):
        self.running = False

    def _generate_initial_metrics(self, node_type: NodeType) -> NodeMetrics:
        # Keep same logic or simplified
        return NodeMetrics(
            cpu_usage=random.uniform(0, 10),
            ram_usage=random.uniform(0, 10),
            latency_ms=random.uniform(10, 50),
            power_consumption=random.uniform(50, 100),
            cost_per_hour=random.uniform(0.1, 2.0),
            available_gpu_memory=None
        )

    async def run_simulation(self):
        self.running = True
        print("Simulation started...")
        while self.running:
            # Fetch all active nodes from DB
            nodes = await Node.find(Node.status == NodeStatus.ACTIVE).to_list()
            
            for node in nodes:
                # Update metrics
                node.cpu_usage = max(0, min(100, node.cpu_usage + random.uniform(-5, 5)))
                node.ram_usage = max(0, min(100, node.ram_usage + random.uniform(-2, 2)))
                
                # Simulate Latency Fluctuations
                if node.type == NodeType.EDGE:
                    node.latency_ms = max(5, node.latency_ms + random.uniform(-2, 2))
                elif node.type == NodeType.CLOUD:
                    node.latency_ms = max(20, node.latency_ms + random.uniform(-1, 1))

                # Save updates to DB
                await node.save()

            # Update Workloads
            active_workloads = await Workload.find(Workload.status == "assigned").to_list()
            for workload in active_workloads:
                workload.progress += random.randint(5, 15)
                if workload.progress >= 100:
                    workload.progress = 100
                    workload.status = "completed"
                    # Ideally, free up node resources here (simplified for prototype)
                await workload.save()
            
            await asyncio.sleep(2) # Update every 2 seconds

    def stop(self):
        self.running = False
        print("Simulation stopped.")
