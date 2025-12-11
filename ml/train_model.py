import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

def generate_synthetic_data(n_samples=1000):
    """
    Generates synthetic data for training.
    Features: Workload CPU, RAM, Priority (encoded), Latency Sensitivity (0/1), GPU Required (0/1)
    Target: Best Node Type (Edge, Cloud, GPU)
    """
    data = []
    for _ in range(n_samples):
        cpu_req = np.random.uniform(1, 32)
        ram_req = np.random.uniform(1, 128)
        priority = np.random.choice([0, 1, 2, 3]) # Low to Critical
        latency_sensitive = np.random.choice([0, 1])
        gpu_required = np.random.choice([0, 1], p=[0.8, 0.2])
        
        # Logic to determine "Ground Truth" label
        if gpu_required:
            label = "gpu"
        elif latency_sensitive and cpu_req < 8:
            label = "edge" # Low latency, low compute -> Edge
        elif cpu_req > 16 or ram_req > 32:
            label = "cloud" # Heavy compute -> Cloud
        else:
            # Randomly assign based on cost/priority trade-off logic (simplified)
            if priority >= 2: # High priority
                label = "cloud" # Reliable
            else:
                label = "edge" # Cheaper/Closer (Mock logic)
        
        data.append([cpu_req, ram_req, priority, latency_sensitive, gpu_required, label])
    
    df = pd.DataFrame(data, columns=['cpu_req', 'ram_req', 'priority', 'latency_sensitive', 'gpu_required', 'target'])
    return df

def train():
    print("Generating synthetic data...")
    df = generate_synthetic_data()
    
    X = df.drop('target', axis=1)
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    print(f"Model Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    
    # Save model
    os.makedirs('ml', exist_ok=True)
    joblib.dump(clf, 'ml/model.pkl')
    print("Model saved to ml/model.pkl")

if __name__ == "__main__":
    train()
