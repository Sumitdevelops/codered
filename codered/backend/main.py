from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
import asyncio
from contextlib import asynccontextmanager
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from models import Node, Workload, ClusterState, NodeType, NodeStatus, NodeMetrics, User
from simulator import NodeSimulator
from scheduler import Scheduler
from database import init_db
from auth import verify_password, get_password_hash, create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Scheduler and Simulator will now need to be stateless or fetch from DB
simulator: NodeSimulator = None
scheduler: Scheduler = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = await User.find_one(User.username == username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def initialize_nodes():
    """Create a set of dummy nodes if they don't exist"""
    if await Node.count() == 0:
        nodes = [
            Node(name="Edge-01", type=NodeType.EDGE, status=NodeStatus.ACTIVE, metrics=NodeMetrics(cpu_usage=0, ram_usage=0, latency_ms=0, power_consumption=0, cost_per_hour=0), location="Factory Floor", max_cpu=4, max_ram=8),
            Node(name="Edge-02", type=NodeType.EDGE, status=NodeStatus.ACTIVE, metrics=NodeMetrics(cpu_usage=0, ram_usage=0, latency_ms=0, power_consumption=0, cost_per_hour=0), location="Warehouse", max_cpu=4, max_ram=8),
            Node(name="Cloud-AWS-East", type=NodeType.CLOUD, status=NodeStatus.ACTIVE, metrics=NodeMetrics(cpu_usage=0, ram_usage=0, latency_ms=0, power_consumption=0, cost_per_hour=0), location="us-east-1", max_cpu=16, max_ram=64),
            Node(name="Cloud-GCP-West", type=NodeType.CLOUD, status=NodeStatus.ACTIVE, metrics=NodeMetrics(cpu_usage=0, ram_usage=0, latency_ms=0, power_consumption=0, cost_per_hour=0), location="us-west1", max_cpu=16, max_ram=64),
            Node(name="GPU-Cluster-01", type=NodeType.GPU, status=NodeStatus.ACTIVE, metrics=NodeMetrics(cpu_usage=0, ram_usage=0, latency_ms=0, power_consumption=0, cost_per_hour=0), location="Data Center", max_cpu=32, max_ram=128),
        ]
        for node in nodes:
            await node.insert()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await initialize_nodes()
    
    global simulator, scheduler
    simulator = NodeSimulator() 
    scheduler = Scheduler()    
    
    # Start simulation task
    sim_task = asyncio.create_task(simulator.run_simulation())
    yield
    # Shutdown
    if simulator:
        simulator.stop()
    sim_task.cancel()

app = FastAPI(title="AI Workload Orchestrator", lifespan=lifespan)

@app.post("/auth/signup", response_model=Token)
async def signup(user_data: UserCreate):
    existing_user = await User.find_one(User.username == user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, password_hash=hashed_password)
    await new_user.insert()
    
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.find_one(User.username == form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def root():
    return {"message": "AI Orchestrator API is running"}

@app.get("/nodes", response_model=List[Node])
async def list_nodes():
    return await Node.find_all().to_list()

@app.get("/workloads", response_model=List[Workload])
async def list_workloads(current_user: User = Depends(get_current_user)):
    # Filter workloads by the current user
    return await Workload.find(Workload.owner_id == str(current_user.id)).to_list()

@app.post("/workloads", response_model=Workload)
async def submit_workload(workload: Workload, current_user: User = Depends(get_current_user)):
    workload.status = "pending"
    workload.owner_id = str(current_user.id) # Assign owner
    await workload.insert()
    
    # Attempt to schedule
    assigned_node = await scheduler.ai_schedule(workload)
    
    if assigned_node:
        workload.assigned_node_id = assigned_node.id
        workload.status = "assigned"
        # Simulate resource reservation (simplified)
        assigned_node.metrics.cpu_usage += 5
        await assigned_node.save()
    else:
        workload.status = "failed" # No resources
        
    await workload.save()
    return workload

@app.get("/cluster/state", response_model=ClusterState)
async def get_cluster_state():
    nodes = await Node.find_all().to_list()
    # Admin view? Or just active workloads overall?
    # Let's show all active workloads for cluster state visualization to see load
    active_workloads = await Workload.find(Workload.status != "completed").to_list()
    return ClusterState(nodes=nodes, active_workloads=active_workloads)
