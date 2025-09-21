"""Agent Models"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    PLANNING = "planning"
    EXECUTION = "execution"
    RESEARCH = "research"
    CODE = "code"

class AgentStatus(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    THINKING = "thinking"
    ERROR = "error"
    TERMINATED = "terminated"

class AgentMetrics(BaseModel):
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_task_time: float = 0.0
    success_rate: float = 0.0
    uptime: float = 0.0
    avg_completion_time: float = 0.0

class AgentBase(BaseModel):
    name: str = Field(..., description="Agent name")
    type: AgentType = Field(..., description="Agent type")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class AgentCreate(AgentBase):
    """Agent creation model"""
    pass

class AgentUpdate(BaseModel):
    """Agent update model"""
    name: Optional[str] = None
    status: Optional[AgentStatus] = None
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class Agent(AgentBase):
    """Agent model"""
    id: str = Field(..., description="Unique agent ID")
    agent_id: str = Field(..., description="Agent identifier")
    status: AgentStatus = Field(AgentStatus.IDLE, description="Current status")
    current_task: Optional[str] = Field(None, description="Current task ID")
    cpu_usage: float = Field(0.0, description="CPU usage percentage")
    memory_usage: float = Field(0.0, description="Memory usage percentage")
    metrics: AgentMetrics = Field(default_factory=AgentMetrics)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AgentResponse(Agent):
    """Agent response model"""
    pass

class AgentDetailResponse(Agent):
    """Detailed agent response with additional information"""
    logs: List[str] = Field(default_factory=list)
    task_history: List[str] = Field(default_factory=list)

class AgentControlAction(str, Enum):
    PAUSE = "pause"
    RESUME = "resume"
    RESTART = "restart"
    TERMINATE = "terminate"

class AgentControlRequest(BaseModel):
    action: AgentControlAction = Field(..., description="Control action")
    params: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")