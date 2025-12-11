from fastapi import FastAPI, HTTPException
from typing import List
import asyncio
from contextlib import asynccontextmanager

from models import Node, Workload, ClusterState, NodeType, NodeStatus, NodeMetrics
from simulator import NodeSimulator
from scheduler import Scheduler

# In-memory storage
nodes: List[Node] = []
workloads: List[Workload] = []
simulator: NodeSimulator = None
scheduler: Scheduler = None

def initialize_nodes():
    """Create a set of dummy nodes"""
    global nodes
    nodes = [
        Node(name="Edge-01", type=NodeType.EDGE, status=NodeStatus.ACTIVE, metrics=NodeMetrics(cpu_usage=0, ram_usage=0, latency_ms=0, power_consumption=0, cost_per_hour=0), location="Factory Floor", max_cpu=4, max_ram=8),
        Node(name="Edge-02", type=NodeType.EDGE, status=NodeStatus.ACTIVE, metrics=NodeMetrics(cpu_usage=0, ram_usage=0, latency_ms=0, power_consumption=0, cost_per_hour=0), location="Warehouse", max_cpu=4, max_ram=8),
        Node(name="Cloud-AWS-East", type=NodeType.CLOUD, status=NodeStatus.ACTIVE, metrics=NodeMetrics(cpu_usage=0, ram_usage=0, latency_ms=0, power_consumption=0, cost_per_hour=0), location="us-east-1", max_cpu=16, max_ram=64),
        Node(name="Cloud-GCP-West", type=NodeType.CLOUD, status=NodeStatus.ACTIVE, metrics=NodeMetrics(cpu_usage=0, ram_usage=0, latency_ms=0, power_consumption=0, cost_per_hour=0), location="us-west1", max_cpu=16, max_ram=64),
        Node(name="GPU-Cluster-01", type=NodeType.GPU, status=NodeStatus.ACTIVE, metrics=NodeMetrics(cpu_usage=0, ram_usage=0, latency_ms=0, power_consumption=0, cost_per_hour=0), location="Data Center", max_cpu=32, max_ram=128),
    ]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_nodes()
    global simulator, scheduler
    simulator = NodeSimulator(nodes)
    scheduler = Scheduler(nodes)
    # Initialize metrics
    for node in nodes:
        node.metrics = simulator._generate_initial_metrics(node.type)
    
    # Start simulation task
    asyncio.create_task(simulator.run_simulation())
    yield
    # Shutdown
    if simulator:
        simulator.stop()

app = FastAPI(title="AI Workload Orchestrator", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "AI Orchestrator API is running"}

@app.get("/nodes", response_model=List[Node])
async def list_nodes():
    return nodes

@app.get("/workloads", response_model=List[Workload])
async def list_workloads():
    return workloads

@app.post("/workloads", response_model=Workload)
async def submit_workload(workload: Workload):
    workload.status = "pending"
    
    # Attempt to schedule
    assigned_node = scheduler.ai_schedule(workload)
    if assigned_node:
        workload.assigned_node_id = assigned_node.id
        workload.status = "assigned"
        # Simulate resource reservation (simplified)
        assigned_node.metrics.cpu_usage += 5 # Mock increase
    else:
        workload.status = "failed" # No resources
        
    workloads.append(workload)
    return workload

@app.get("/cluster/state", response_model=ClusterState)
async def get_cluster_state():
    return ClusterState(nodes=nodes, active_workloads=workloads)
