from typing import List, Optional
from enum import Enum
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from beanie import Document

class NodeType(str, Enum):
    EDGE = "edge"
    CLOUD = "cloud"
    GPU = "gpu"

class NodeStatus(str, Enum):
    ACTIVE = "active"
    OFFLINE = "offline"
    BUSY = "busy"

class WorkloadPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NodeMetrics(BaseModel):
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    ram_usage: float = Field(..., ge=0, le=100, description="RAM usage percentage")
    latency_ms: float = Field(..., ge=0, description="Network latency in milliseconds")
    power_consumption: float = Field(..., ge=0, description="Power consumption in Watts")
    cost_per_hour: float = Field(..., ge=0, description="Operational cost per hour")
    available_gpu_memory: Optional[float] = Field(None, description="Available GPU memory in GB")

class Node(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: NodeType
    status: NodeStatus
    
    # Flattened metrics
    cpu_usage: float = Field(default=0.0)
    ram_usage: float = Field(default=0.0)
    latency_ms: float = Field(default=0.0)
    power_consumption: float = Field(default=0.0)
    cost_per_hour: float = Field(default=0.0)
    available_gpu_memory: Optional[float] = Field(default=None)
        
    location: str
    max_cpu: int
    max_ram: int
    tags: List[str] = []

    class Settings:
        name = "nodes"

    @property
    def metrics(self) -> NodeMetrics:
        return NodeMetrics(
            cpu_usage=self.cpu_usage,
            ram_usage=self.ram_usage,
            latency_ms=self.latency_ms,
            power_consumption=self.power_consumption,
            cost_per_hour=self.cost_per_hour,
            available_gpu_memory=self.available_gpu_memory
        )

    @metrics.setter
    def metrics(self, value: NodeMetrics):
        self.cpu_usage = value.cpu_usage
        self.ram_usage = value.ram_usage
        self.latency_ms = value.latency_ms
        self.power_consumption = value.power_consumption
        self.cost_per_hour = value.cost_per_hour
        self.available_gpu_memory = value.available_gpu_memory

class User(Document):
    username: str = Field(unique=True) # Beanie supports unique index
    password_hash: str

    class Settings:
        name = "users"

class Workload(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    priority: WorkloadPriority
    required_cpu: float
    required_ram: float
    required_gpu: bool = Field(default=False)
    max_latency: Optional[float] = Field(default=None)
    submitted_at: datetime = Field(default_factory=datetime.now)
    assigned_node_id: Optional[str] = Field(default=None)
    status: str = Field(default="pending")
    progress: int = Field(default=0)
    owner_id: Optional[str] = Field(default=None) # Link to User

    class Settings:
        name = "workloads"

class ClusterState(BaseModel):
    nodes: List[Node]
    active_workloads: List[Workload]
    timestamp: datetime = Field(default_factory=datetime.now)
