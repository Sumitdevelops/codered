import requests
import time
import sys

API_URL = "http://localhost:8000"

def wait_for_api():
    print("Waiting for API to be ready...")
    for _ in range(10):
        try:
            requests.get(f"{API_URL}/")
            print("API is ready.")
            return True
        except:
            time.sleep(1)
    print("API failed to start.")
    return False

def test_flow():
    if not wait_for_api():
        sys.exit(1)

    # 1. Submit a High Compute Task (Should go to Cloud or GPU)
    print("\nSubmitting High Compute Task...")
    task1 = {
        "name": "Heavy-Compute-Job",
        "priority": "high",
        "required_cpu": 16,
        "required_ram": 32,
        "required_gpu": False,
        "max_latency": 1000
    }
    res1 = requests.post(f"{API_URL}/workloads", json=task1).json()
    print(f"Task 1 Result: {res1['status']}, Assigned Node: {res1.get('assigned_node_id')}")

    # 2. Submit a Low Latency Task (Should go to Edge)
    print("\nSubmitting Low Latency Task...")
    task2 = {
        "name": "RealTime-Sensor-Job",
        "priority": "critical",
        "required_cpu": 2,
        "required_ram": 4,
        "required_gpu": False,
        "max_latency": 10 # Very low latency requirement
    }
    res2 = requests.post(f"{API_URL}/workloads", json=task2).json()
    print(f"Task 2 Result: {res2['status']}, Assigned Node: {res2.get('assigned_node_id')}")

    # 3. Submit a GPU Task
    print("\nSubmitting GPU Task...")
    task3 = {
        "name": "Model-Training-Job",
        "priority": "medium",
        "required_cpu": 8,
        "required_ram": 16,
        "required_gpu": True,
        "max_latency": 500
    }
    res3 = requests.post(f"{API_URL}/workloads", json=task3).json()
    print(f"Task 3 Result: {res3['status']}, Assigned Node: {res3.get('assigned_node_id')}")

    # Verify Cluster State
    print("\nChecking Cluster State...")
    state = requests.get(f"{API_URL}/cluster/state").json()
    print(f"Active Workloads: {len(state['active_workloads'])}")
    print(f"Total Nodes: {len(state['nodes'])}")

if __name__ == "__main__":
    test_flow()
