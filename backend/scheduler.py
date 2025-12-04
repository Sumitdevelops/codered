from typing import List, Optional
import joblib
import pandas as pd
import os
from models import Node, Workload, NodeStatus, NodeType

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ml', 'model.pkl')

class Scheduler:
    def __init__(self, nodes: List[Node]):
        self.nodes = nodes
        self.model = None
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                print("AI Model loaded successfully.")
            else:
                print(f"AI Model not found at {MODEL_PATH}")
        except Exception as e:
            print(f"Failed to load AI model: {e}")

    def schedule(self, workload: Workload) -> Optional[Node]:
        """
        Basic Greedy Scheduler:
        Finds the first node that meets the resource requirements.
        """
        candidates = [n for n in self.nodes if n.status == NodeStatus.ACTIVE]
        
        # Filter by requirements
        valid_nodes = []
        for node in candidates:
            if node.metrics.cpu_usage + workload.required_cpu <= node.max_cpu * 100: # Simplified check
                 # In reality, cpu_usage is %, required_cpu might be cores or %. 
                 # Let's assume required_cpu is % of a standard unit or we check against capacity.
                 # For this prototype, let's assume required_cpu is % of the node's capacity for simplicity, 
                 # OR better, let's assume we check if adding it keeps it under 100%.
                 # But wait, node.metrics.cpu_usage is current load.
                 # Let's assume workload.required_cpu is estimated % load it adds.
                 if (node.metrics.cpu_usage + 10) <= 100: # Placeholder logic: assume task adds 10% load
                     valid_nodes.append(node)
        
        if not valid_nodes:
            return None

        # Sort by cost (Greedy approach for cost)
        # valid_nodes.sort(key=lambda n: n.metrics.cost_per_hour)
        
        # For now, just return the first one
        return valid_nodes[0] if valid_nodes else None

    def ai_schedule(self, workload: Workload) -> Optional[Node]:
        """
        AI-Powered Scheduler:
        1. Predicts best node type using ML model.
        2. Filters nodes by that type.
        3. Selects best node within that type (e.g. lowest CPU).
        """
        if not self.model:
            print("Model not loaded, falling back to greedy scheduler.")
            return self.schedule(workload)

        # Prepare features for prediction
        # Features: cpu_req, ram_req, priority, latency_sensitive, gpu_required
        priority_map = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        features = pd.DataFrame([[
            workload.required_cpu,
            workload.required_ram,
            priority_map.get(workload.priority.value, 0),
            1 if workload.max_latency and workload.max_latency < 50 else 0, # Simple heuristic for latency sensitivity
            1 if workload.required_gpu else 0
        ]], columns=['cpu_req', 'ram_req', 'priority', 'latency_sensitive', 'gpu_required'])

        try:
            predicted_type = self.model.predict(features)[0]
            print(f"AI Predicted Node Type: {predicted_type}")
        except Exception as e:
            print(f"Prediction failed: {e}")
            return self.schedule(workload)

        # Filter nodes by predicted type
        candidates = [n for n in self.nodes if n.status == NodeStatus.ACTIVE and n.type.value == predicted_type]
        
        if not candidates:
            print(f"No active nodes of type {predicted_type} found. Falling back to greedy.")
            return self.schedule(workload)

        # Pick best candidate (e.g. lowest CPU usage)
        candidates.sort(key=lambda n: n.metrics.cpu_usage)
        return candidates[0]
