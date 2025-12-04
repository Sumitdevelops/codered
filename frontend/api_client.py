import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def get_nodes():
    try:
        response = requests.get(f"{API_URL}/nodes")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def get_workloads():
    try:
        response = requests.get(f"{API_URL}/workloads")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def submit_workload(name, priority, cpu, ram, gpu, latency):
    payload = {
        "name": name,
        "priority": priority,
        "required_cpu": cpu,
        "required_ram": ram,
        "required_gpu": gpu,
        "max_latency": latency
    }
    try:
        response = requests.post(f"{API_URL}/workloads", json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
