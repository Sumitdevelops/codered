from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
import uuid
from datetime import datetime

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

class Node(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: NodeType
    status: NodeStatus
    metrics: NodeMetrics
    location: str
    max_cpu: int
    max_ram: int
    tags: List[str] = []

class Workload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    priority: WorkloadPriority
    required_cpu: float
    required_ram: float
    required_gpu: bool = False
    max_latency: Optional[float] = None
    submitted_at: datetime = Field(default_factory=datetime.now)
    assigned_node_id: Optional[str] = None
    status: str = "pending" # pending, assigned, running, completed, failed

class ClusterState(BaseModel):
    nodes: List[Node]
    active_workloads: List[Workload]
    timestamp: datetime = Field(default_factory=datetime.now)
