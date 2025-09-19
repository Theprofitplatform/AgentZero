"""
Core Agent Base Class for AgentZero
Provides foundation for all agent types with advanced capabilities
"""

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union
from pathlib import Path


class AgentStatus(Enum):
    """Agent operational states"""
    IDLE = "idle"
    WORKING = "working"
    THINKING = "thinking"
    COMMUNICATING = "communicating"
    ERROR = "error"
    TERMINATED = "terminated"


class Priority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class Task:
    """Represents a task for agent execution"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    priority: Priority = Priority.MEDIUM
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentCapability:
    """Defines an agent's capability"""
    name: str
    description: str
    handler: Callable
    required_tools: List[str] = field(default_factory=list)
    cost_estimate: float = 0.0


class BaseAgent(ABC):
    """
    Advanced base agent with comprehensive capabilities
    """
    
    def __init__(self, 
                 agent_id: Optional[str] = None,
                 name: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize base agent
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name
            config: Configuration dictionary
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or f"Agent-{self.agent_id[:8]}"
        self.config = config or {}
        
        # Core components
        self.status = AgentStatus.IDLE
        self.capabilities: Dict[str, AgentCapability] = {}
        self.tools: Dict[str, Any] = {}
        self.memory: Dict[str, Any] = {}
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.current_task: Optional[Task] = None
        
        # Communication
        self.message_handlers: Dict[str, Callable] = {}
        self.hive_connection = None
        
        # Logging
        self.logger = logging.getLogger(f"{self.__class__.__name__}:{self.agent_id[:8]}")
        self.logger.setLevel(logging.INFO)
        
        # Metrics
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_runtime": 0,
            "average_task_time": 0,
            "success_rate": 0.0
        }
        
        # Initialize agent
        self._initialize()
    
    def _initialize(self):
        """Initialize agent components"""
        self.logger.info(f"Initializing {self.name}")
        self._register_default_capabilities()
        self._load_tools()
        self._setup_memory()
    
    def _register_default_capabilities(self):
        """Register default agent capabilities"""
        self.register_capability(AgentCapability(
            name="execute_task",
            description="Execute a single task",
            handler=self._execute_task_handler
        ))
        
        self.register_capability(AgentCapability(
            name="communicate",
            description="Send/receive messages with other agents",
            handler=self._communicate_handler
        ))
        
        self.register_capability(AgentCapability(
            name="learn",
            description="Learn from experience and update knowledge",
            handler=self._learn_handler
        ))
    
    def register_capability(self, capability: AgentCapability):
        """Register a new capability"""
        self.capabilities[capability.name] = capability
        self.logger.debug(f"Registered capability: {capability.name}")
    
    def _load_tools(self):
        """Load agent tools"""
        # Tool loading will be implemented by specialized agents
        pass
    
    def _setup_memory(self):
        """Setup memory systems"""
        self.memory = {
            "short_term": {},  # Working memory
            "long_term": {},   # Persistent knowledge
            "episodic": [],    # Experience records
            "semantic": {}     # Conceptual knowledge
        }
    
    async def process_task(self, task: Task) -> Any:
        """
        Process a single task
        
        Args:
            task: Task to process
            
        Returns:
            Task result
        """
        self.logger.info(f"Processing task: {task.name}")
        self.current_task = task
        self.status = AgentStatus.WORKING
        
        try:
            # Check dependencies
            if task.dependencies:
                await self._wait_for_dependencies(task.dependencies)
            
            # Execute task
            result = await self.execute(task)
            
            # Update task
            task.completed_at = datetime.now()
            task.result = result
            
            # Update metrics
            self.metrics["tasks_completed"] += 1
            self._update_success_rate()
            
            # Learn from experience
            await self.learn_from_task(task)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task failed: {str(e)}")
            task.error = str(e)
            self.metrics["tasks_failed"] += 1
            self._update_success_rate()
            self.status = AgentStatus.ERROR
            raise
        
        finally:
            self.completed_tasks.append(task)
            self.current_task = None
            self.status = AgentStatus.IDLE
    
    @abstractmethod
    async def execute(self, task: Task) -> Any:
        """
        Execute the main task logic
        Must be implemented by subclasses
        """
        pass
    
    async def learn_from_task(self, task: Task):
        """Learn from completed task"""
        experience = {
            "task_id": task.id,
            "task_name": task.name,
            "success": task.error is None,
            "duration": (task.completed_at - task.created_at).total_seconds() if task.completed_at else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in episodic memory
        if "episodic" not in self.memory:
            self.memory["episodic"] = []
        self.memory["episodic"].append(experience)
        
        # Limit episodic memory size
        if len(self.memory["episodic"]) > 1000:
            self.memory["episodic"] = self.memory["episodic"][-1000:]
    
    async def communicate(self, message: Dict[str, Any], target: Optional[str] = None):
        """
        Send message to other agents or hive
        
        Args:
            message: Message content
            target: Target agent ID or None for broadcast
        """
        if self.hive_connection:
            await self.hive_connection.send_message(
                sender=self.agent_id,
                target=target,
                message=message
            )
    
    async def receive_message(self, message: Dict[str, Any]):
        """Handle incoming message"""
        msg_type = message.get("type", "unknown")
        
        if msg_type in self.message_handlers:
            handler = self.message_handlers[msg_type]
            await handler(message)
        else:
            self.logger.warning(f"No handler for message type: {msg_type}")
    
    def add_task(self, task: Task):
        """Add task to queue"""
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority.value)
    
    async def run(self):
        """Main agent loop"""
        self.logger.info(f"{self.name} starting")
        
        while self.status != AgentStatus.TERMINATED:
            if self.task_queue and self.status == AgentStatus.IDLE:
                task = self.task_queue.pop(0)
                await self.process_task(task)
            else:
                await asyncio.sleep(0.1)
    
    def _update_success_rate(self):
        """Update success rate metric"""
        total = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        if total > 0:
            self.metrics["success_rate"] = self.metrics["tasks_completed"] / total
    
    async def _wait_for_dependencies(self, dependencies: List[str]):
        """Wait for task dependencies to complete"""
        # Implementation would check with hive coordinator
        pass
    
    async def _execute_task_handler(self, params: Dict[str, Any]) -> Any:
        """Default task execution handler"""
        task = Task(**params)
        return await self.process_task(task)
    
    async def _communicate_handler(self, params: Dict[str, Any]) -> Any:
        """Default communication handler"""
        return await self.communicate(params.get("message"), params.get("target"))
    
    async def _learn_handler(self, params: Dict[str, Any]) -> Any:
        """Default learning handler"""
        # Implement learning logic
        pass
    
    def shutdown(self):
        """Gracefully shutdown agent"""
        self.logger.info(f"Shutting down {self.name}")
        self.status = AgentStatus.TERMINATED
        
        # Save memory to disk if configured
        if self.config.get("persist_memory"):
            self._save_memory()
    
    def _save_memory(self):
        """Save memory to persistent storage"""
        memory_file = Path(f"memory/{self.agent_id}.json")
        memory_file.parent.mkdir(exist_ok=True)
        
        with open(memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2, default=str)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status report"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "current_task": self.current_task.name if self.current_task else None,
            "queue_size": len(self.task_queue),
            "capabilities": list(self.capabilities.keys()),
            "metrics": self.metrics
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.agent_id[:8]} name={self.name} status={self.status.value}>"