import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def login_user(username, password):
    try:
        response = requests.post(
            f"{API_URL}/auth/login", 
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json() # Returns access_token
        else:
            return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

def signup_user(username, password):
    try:
        response = requests.post(
            f"{API_URL}/auth/signup", 
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

def get_headers(token):
    return {"Authorization": f"Bearer {token}"}

def get_nodes():
    try:
        # Nodes are public for now, but good to support auth future
        response = requests.get(f"{API_URL}/nodes")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def get_workloads(token):
    try:
        response = requests.get(f"{API_URL}/workloads", headers=get_headers(token))
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def submit_workload(token, name, priority, cpu, ram, gpu, latency):
    payload = {
        "name": name,
        "priority": priority,
        "required_cpu": cpu,
        "required_ram": ram,
        "required_gpu": gpu,
        "max_latency": latency
    }
    try:
        response = requests.post(f"{API_URL}/workloads", json=payload, headers=get_headers(token))
        return response.json()
    except Exception as e:
        return {"error": str(e)}
