"""
AI Decision Engine for Workload Routing
Loads trained ML model and makes routing decisions
"""

import pickle
import numpy as np
from typing import Dict, Any, Tuple
import os


class DecisionEngine:
    """ML-based decision engine for workload routing"""
    
    NODE_NAMES = {
        0: "EDGE",
        1: "CLOUD", 
        2: "GPU"
    }
    
    def __init__(self, model_path: str = "models/model.pkl"):
        """Initialize decision engine with trained model"""
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Please run train_model.py first."
            )
        
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        print(f"Decision engine loaded model from {model_path}")
    
    def decide(
        self,
        task_metadata: Dict[str, Any],
        system_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Make routing decision based on task metadata and system metrics
        
        Args:
            task_metadata: Task information (priority, latency, requiresGPU, etc.)
            system_metrics: Current system state (node loads, network latency)
        
        Returns:
            Decision dictionary with node, confidence, and explanation
        """
        
        # Extract and transform features
        features = self._extract_features(task_metadata, system_metrics)
        
        # Predict node
        feature_array = np.array([list(features.values())])
        node_prediction = self.model.predict(feature_array)[0]
        
        # Get probability distribution for confidence
        probabilities = self.model.predict_proba(feature_array)[0]
        confidence = float(probabilities[node_prediction])
        
        # Get alternative recommendations
        sorted_indices = np.argsort(probabilities)[::-1]
        alternatives = [
            {
                "node": self.NODE_NAMES[idx],
                "confidence": float(probabilities[idx])
            }
            for idx in sorted_indices[:3]
        ]
        
        # Generate explanation
        explanation = self._generate_explanation(
            task_metadata,
            system_metrics,
            node_prediction,
            confidence,
            features
        )
        
        return {
            "best_node": self.NODE_NAMES[node_prediction],
            "confidence": confidence,
            "explanation": explanation,
            "alternatives": alternatives,
            "features_used": features
        }
    
    def _extract_features(
        self,
        task: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Extract and normalize features for model input"""
        
        return {
            'priority': task.get('priority', 5),
            'latency_requirement': task.get('latency', 5),
            'requires_gpu': 1 if task.get('requiresGPU', False) else 0,
            'edge_load': metrics.get('edge_load', 50),
            'cloud_load': metrics.get('cloud_load', 50),
            'gpu_load': metrics.get('gpu_load', 50),
            'network_latency': metrics.get('network_latency', 100),
            'cost_sensitivity': task.get('cost_sensitivity', 5),
        }
    
    def _generate_explanation(
        self,
        task: Dict[str, Any],
        metrics: Dict[str, float],
        node: int,
        confidence: float,
        features: Dict[str, float]
    ) -> str:
        """Generate human-readable explanation for the decision"""
        
        node_name = self.NODE_NAMES[node]
        task_type = task.get('taskType', 'unknown')
        
        reasons = []
        
        # GPU requirement check
        if features['requires_gpu'] == 1:
            if node == 2:
                reasons.append("Task requires GPU acceleration")
            else:
                reasons.append(f"GPU node overloaded ({features['gpu_load']:.0f}%), using fallback")
        
        # Latency sensitivity
        if features['latency_requirement'] >= 8:
            if node == 0:
                reasons.append(f"Ultra-low latency required ({features['latency_requirement']}/10)")
            else:
                reasons.append(f"Edge node saturated ({features['edge_load']:.0f}%), next best option")
        
        # Priority consideration
        if features['priority'] >= 8:
            reasons.append(f"High priority task (P{int(features['priority'])})")
        
        # Cost optimization
        if features['cost_sensitivity'] >= 7 and node == 1:
            reasons.append("Cost-optimized routing for batch processing")
        
        # Load balancing
        node_loads = {
            'EDGE': features['edge_load'],
            'CLOUD': features['cloud_load'],
            'GPU': features['gpu_load']
        }
        
        if node_loads[node_name] < 70:
            reasons.append(f"{node_name} node has available capacity ({100 - node_loads[node_name]:.0f}% free)")
        
        # Network conditions
        if features['network_latency'] > 300:
            reasons.append(f"High network latency ({features['network_latency']:.0f}ms) factored in")
        
        # Default if no specific reasons
        if not reasons:
            reasons.append(f"Best fit based on current system state")
        
        # Combine explanation
        explanation = f"Routing '{task_type}' to {node_name} node (confidence: {confidence:.1%}). "
        explanation += " | ".join(reasons[:3])  # Limit to top 3 reasons
        
        return explanation


# Singleton instance
_decision_engine = None


def get_decision_engine() -> DecisionEngine:
    """Get or create singleton decision engine instance"""
    
    global _decision_engine
    
    if _decision_engine is None:
        _decision_engine = DecisionEngine()
    
    return _decision_engine
