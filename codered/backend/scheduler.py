from typing import List, Optional
import joblib
import pandas as pd
import os
from models import Node, Workload, NodeStatus, NodeType

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ml', 'model.pkl')

class Scheduler:
    def __init__(self):
        self.model = None
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                print("AI Model loaded successfully.")
            else:
                print(f"AI Model not found at {MODEL_PATH}")
        except Exception as e:
            print(f"Failed to load AI model: {e}")

    async def get_active_nodes(self) -> List[Node]:
        return await Node.find(Node.status == NodeStatus.ACTIVE).to_list()

    async def schedule(self, workload: Workload) -> Optional[Node]:
        """
        Basic Greedy Scheduler
        """
        candidates = await self.get_active_nodes()
        
        # Filter by requirements
        valid_nodes = []
        for node in candidates:
            if node.metrics.cpu_usage + 10 <= 100: # Simple check
                 valid_nodes.append(node)
        
        if not valid_nodes:
            return None

        return valid_nodes[0]

    async def ai_schedule(self, workload: Workload) -> Optional[Node]:
        """
        AI-Powered Scheduler
        """
        if not self.model:
            print("Model not loaded, falling back to greedy scheduler.")
            return await self.schedule(workload)

        # Prepare features for prediction
        priority_map = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        features = pd.DataFrame([[
            workload.required_cpu,
            workload.required_ram,
            priority_map.get(workload.priority.value, 0),
            1 if workload.max_latency and workload.max_latency < 50 else 0,
            1 if workload.required_gpu else 0
        ]], columns=['cpu_req', 'ram_req', 'priority', 'latency_sensitive', 'gpu_required'])

        try:
            predicted_type = self.model.predict(features)[0]
            print(f"AI Predicted Node Type: {predicted_type}")
        except Exception as e:
            print(f"Prediction failed: {e}")
            return await self.schedule(workload)

        # Filter nodes by predicted type (Queries DB for that type)
        # Note: We could do this via DB query for efficiency
        candidates = await Node.find(
            Node.status == NodeStatus.ACTIVE,
            Node.type == predicted_type
        ).to_list()
        
        if not candidates:
            print(f"No active nodes of type {predicted_type} found. Falling back to greedy.")
            return await self.schedule(workload)

        # Pick best candidate (e.g. lowest CPU usage)
        candidates.sort(key=lambda n: n.metrics.cpu_usage)
        return candidates[0]
