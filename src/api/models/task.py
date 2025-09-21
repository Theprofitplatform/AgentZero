"""Task Models"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class TaskType(str, Enum):
    GENERAL = "general"
    RESEARCH = "research"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"

class TaskBase(BaseModel):
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    type: TaskType = Field(TaskType.GENERAL, description="Task type")
    priority: TaskPriority = Field(TaskPriority.NORMAL, description="Task priority")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class TaskCreate(TaskBase):
    """Task creation model"""
    pass

class TaskUpdate(BaseModel):
    """Task update model"""
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class Task(TaskBase):
    """Task model"""
    id: str = Field(..., description="Unique task ID")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Task status")
    assigned_agent: Optional[str] = Field(None, description="Assigned agent ID")
    assigned_to: Optional[str] = Field(None, description="Assigned to (agent name)")
    progress: float = Field(0.0, description="Task progress (0-100)")
    result: Optional[Any] = Field(None, description="Task result")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(None, description="Task start time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class TaskResponse(Task):
    """Task response model"""
    pass

class TaskDetailResponse(Task):
    """Detailed task response with additional information"""
    logs: List[str] = Field(default_factory=list, description="Execution logs")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")

class TaskStats(BaseModel):
    """Task statistics"""
    total: int = 0
    pending: int = 0
    running: int = 0
    completed: int = 0
    failed: int = 0
    success_rate: float = 0.0