"""
Machine Learning Model Training for Workload Orchestration
Generates synthetic training data and trains a RandomForest classifier
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os
from typing import Tuple


def generate_synthetic_dataset(n_samples: int = 10000) -> pd.DataFrame:
    """
    Generate synthetic training data for workload routing
    
    Features:
    - priority: 1-10 (higher = more urgent)
    - latency_requirement: 1-10 (higher = more latency-sensitive)
    - requires_gpu: 0 or 1
    - edge_load: 0-100 (% utilization)
    - cloud_load: 0-100
    - gpu_load: 0-100
    - network_latency: 10-500 ms
    - cost_sensitivity: 1-10 (higher = more cost-sensitive)
    
    Target:
    - node: 0=EDGE, 1=CLOUD, 2=GPU
    """
    
    np.random.seed(42)
    
    data = {
        'priority': np.random.randint(1, 11, n_samples),
        'latency_requirement': np.random.randint(1, 11, n_samples),
        'requires_gpu': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'edge_load': np.random.randint(0, 101, n_samples),
        'cloud_load': np.random.randint(0, 101, n_samples),
        'gpu_load': np.random.randint(0, 101, n_samples),
        'network_latency': np.random.randint(10, 501, n_samples),
        'cost_sensitivity': np.random.randint(1, 11, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Create target labels based on rules
    def assign_node(row) -> int:
        """Rule-based node assignment for training"""
        
        # GPU required tasks MUST go to GPU
        if row['requires_gpu'] == 1:
            # Unless GPU is extremely overloaded and task is not critical
            if row['gpu_load'] > 90 and row['priority'] < 4:
                return 1  # CLOUD as fallback
            return 2  # GPU
        
        # High latency-sensitive tasks prefer EDGE
        if row['latency_requirement'] >= 8:
            if row['edge_load'] < 80:
                return 0  # EDGE
            elif row['cloud_load'] < 70:
                return 1  # CLOUD
            return 2  # GPU as last resort
        
        # Cost-sensitive batch jobs prefer CLOUD
        if row['cost_sensitivity'] >= 8 and row['priority'] <= 4:
            if row['cloud_load'] < 85:
                return 1  # CLOUD
            return 0  # EDGE
        
        # High priority tasks with moderate latency
        if row['priority'] >= 7 and row['latency_requirement'] >= 6:
            if row['edge_load'] < 75:
                return 0  # EDGE
            return 1  # CLOUD
        
        # Compute-intensive tasks without GPU requirement
        if row['priority'] >= 6 and row['latency_requirement'] < 5:
            if row['cloud_load'] < 70:
                return 1  # CLOUD
            elif row['gpu_load'] < 60:
                return 2  # GPU
            return 0  # EDGE
        
        # Default distribution based on current load
        loads = {
            0: row['edge_load'],
            1: row['cloud_load'],
            2: row['gpu_load']
        }
        
        # Choose least loaded node
        return min(loads, key=loads.get)
    
    df['node'] = df.apply(assign_node, axis=1)
    
    return df


def train_model(df: pd.DataFrame) -> Tuple[RandomForestClassifier, float]:
    """Train RandomForest classifier on the dataset"""
    
    # Features and target
    X = df.drop('node', axis=1)
    y = df['node']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train RandomForest
    print("Training RandomForest classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['EDGE', 'CLOUD', 'GPU']))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance)
    
    return model, accuracy


def save_model(model: RandomForestClassifier, path: str = "models/model.pkl") -> None:
    """Save trained model to disk"""
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\nModel saved to {path}")


def main():
    """Main training pipeline"""
    
    print("="*60)
    print("AI Workload Orchestrator - Model Training")
    print("="*60)
    
    # Generate dataset
    print("\n1. Generating synthetic dataset...")
    df = generate_synthetic_dataset(n_samples=10000)
    print(f"Generated {len(df)} training samples")
    print(f"\nNode distribution:")
    print(df['node'].value_counts().sort_index())
    
    # Train model
    print("\n2. Training model...")
    model, accuracy = train_model(df)
    
    # Save model
    print("\n3. Saving model...")
    save_model(model)
    
    print("\n" + "="*60)
    print("Training complete!")
    print("="*60)


if __name__ == "__main__":
    main()
