"""
Hive Coordinator System for AgentZero
Manages multi-agent orchestration and collaboration
"""

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
import heapq
import uuid


class TaskDistributionStrategy(Enum):
    """Task distribution strategies"""
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"
    CAPABILITY_BASED = "capability_based"
    AUCTION_BASED = "auction_based"
    PRIORITY_BASED = "priority_based"


class HiveMessageType(Enum):
    """Message types for hive communication"""
    REGISTER = "register"
    UNREGISTER = "unregister"
    HEARTBEAT = "heartbeat"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    BROADCAST = "broadcast"
    DIRECT_MESSAGE = "direct_message"
    CAPABILITY_QUERY = "capability_query"
    STATUS_UPDATE = "status_update"
    RESOURCE_REQUEST = "resource_request"


@dataclass
class AgentInfo:
    """Information about a registered agent"""
    agent_id: str
    name: str
    capabilities: List[str]
    status: str
    last_heartbeat: datetime
    current_load: int = 0
    max_load: int = 5
    success_rate: float = 1.0
    average_task_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HiveTask:
    """Task managed by the hive"""
    task_id: str
    name: str
    description: str
    required_capabilities: List[str]
    priority: int
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Any] = None
    error: Optional[str] = None


class HiveCoordinator:
    """
    Central coordinator for multi-agent collaboration
    """
    
    def __init__(self, 
                 hive_id: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize hive coordinator
        
        Args:
            hive_id: Unique identifier for the hive
            config: Configuration dictionary
        """
        self.hive_id = hive_id or str(uuid.uuid4())
        self.config = config or {}
        
        # Agent registry
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_connections: Dict[str, Any] = {}
        
        # Task management
        self.task_queue: List[HiveTask] = []
        self.active_tasks: Dict[str, HiveTask] = {}
        self.completed_tasks: List[HiveTask] = []
        self.task_dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        # Communication
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_handlers = self._setup_message_handlers()
        
        # Strategy
        self.distribution_strategy = TaskDistributionStrategy(
            self.config.get("distribution_strategy", TaskDistributionStrategy.CAPABILITY_BASED)
        )
        
        # Metrics
        self.metrics = {
            "total_agents": 0,
            "active_agents": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_completion_time": 0.0,
            "hive_efficiency": 0.0
        }
        
        # Logging
        self.logger = logging.getLogger(f"HiveCoordinator:{self.hive_id[:8]}")
        self.logger.setLevel(logging.INFO)
        
        # Knowledge base
        self.knowledge_base = {
            "agent_specializations": {},
            "task_patterns": {},
            "optimization_rules": []
        }
        
        self.running = False
    
    def _setup_message_handlers(self) -> Dict[str, callable]:
        """Setup message handlers"""
        return {
            HiveMessageType.REGISTER: self._handle_register,
            HiveMessageType.UNREGISTER: self._handle_unregister,
            HiveMessageType.HEARTBEAT: self._handle_heartbeat,
            HiveMessageType.TASK_COMPLETE: self._handle_task_complete,
            HiveMessageType.TASK_FAILED: self._handle_task_failed,
            HiveMessageType.CAPABILITY_QUERY: self._handle_capability_query,
            HiveMessageType.STATUS_UPDATE: self._handle_status_update,
            HiveMessageType.RESOURCE_REQUEST: self._handle_resource_request
        }
    
    async def start(self):
        """Start the hive coordinator"""
        self.logger.info(f"Starting Hive Coordinator {self.hive_id}")
        self.running = True
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._process_messages()),
            asyncio.create_task(self._task_scheduler()),
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._optimize_hive())
        ]
        
        await asyncio.gather(*tasks)
    
    async def register_agent(self, agent_info: AgentInfo, connection: Any):
        """
        Register an agent with the hive
        
        Args:
            agent_info: Agent information
            connection: Communication connection to agent
        """
        self.agents[agent_info.agent_id] = agent_info
        self.agent_connections[agent_info.agent_id] = connection
        
        self.metrics["total_agents"] += 1
        self.metrics["active_agents"] += 1
        
        self.logger.info(f"Agent registered: {agent_info.name} ({agent_info.agent_id[:8]})")
        
        # Send welcome message
        await self.send_message(
            agent_info.agent_id,
            HiveMessageType.DIRECT_MESSAGE,
            {"message": "Welcome to the hive!", "hive_id": self.hive_id}
        )
    
    async def unregister_agent(self, agent_id: str):
        """Unregister an agent from the hive"""
        if agent_id in self.agents:
            agent_info = self.agents[agent_id]
            del self.agents[agent_id]
            del self.agent_connections[agent_id]
            
            self.metrics["active_agents"] -= 1
            
            self.logger.info(f"Agent unregistered: {agent_info.name}")
            
            # Reassign any active tasks
            await self._reassign_agent_tasks(agent_id)
    
    async def submit_task(self, task: HiveTask) -> str:
        """
        Submit a task to the hive
        
        Args:
            task: Task to submit
            
        Returns:
            Task ID
        """
        self.task_queue.append(task)
        self.metrics["total_tasks"] += 1
        
        # Sort by priority
        self.task_queue.sort(key=lambda t: t.priority)
        
        self.logger.info(f"Task submitted: {task.name} (ID: {task.task_id[:8]})")
        
        # Trigger immediate scheduling
        await self._schedule_task(task)
        
        return task.task_id
    
    async def _schedule_task(self, task: HiveTask):
        """Schedule a task to an appropriate agent"""
        # Check dependencies
        if task.dependencies:
            incomplete_deps = [
                dep for dep in task.dependencies 
                if dep not in [t.task_id for t in self.completed_tasks]
            ]
            if incomplete_deps:
                self.task_dependencies[task.task_id] = set(incomplete_deps)
                return
        
        # Find suitable agent
        agent_id = await self._select_agent_for_task(task)
        
        if agent_id:
            await self._assign_task_to_agent(task, agent_id)
        else:
            self.logger.warning(f"No suitable agent found for task: {task.name}")
    
    async def _select_agent_for_task(self, task: HiveTask) -> Optional[str]:
        """Select best agent for task based on strategy"""
        available_agents = self._get_available_agents(task.required_capabilities)
        
        if not available_agents:
            return None
        
        if self.distribution_strategy == TaskDistributionStrategy.CAPABILITY_BASED:
            # Select agent with best capability match
            return self._select_by_capability(available_agents, task)
        
        elif self.distribution_strategy == TaskDistributionStrategy.LOAD_BALANCED:
            # Select agent with lowest load
            return min(available_agents, key=lambda a: self.agents[a].current_load)
        
        elif self.distribution_strategy == TaskDistributionStrategy.AUCTION_BASED:
            # Agents bid for tasks
            return await self._run_task_auction(available_agents, task)
        
        elif self.distribution_strategy == TaskDistributionStrategy.PRIORITY_BASED:
            # Select based on agent success rate and speed
            return self._select_by_performance(available_agents)
        
        else:  # ROUND_ROBIN
            return available_agents[0]
    
    def _get_available_agents(self, required_capabilities: List[str]) -> List[str]:
        """Get agents that can handle the task"""
        available = []
        
        for agent_id, agent_info in self.agents.items():
            # Check capabilities
            if all(cap in agent_info.capabilities for cap in required_capabilities):
                # Check load
                if agent_info.current_load < agent_info.max_load:
                    # Check if agent is responsive
                    if (datetime.now() - agent_info.last_heartbeat).seconds < 30:
                        available.append(agent_id)
        
        return available
    
    def _select_by_capability(self, agents: List[str], task: HiveTask) -> str:
        """Select agent with best capability match"""
        scores = {}
        
        for agent_id in agents:
            agent_info = self.agents[agent_id]
            # Score based on capability overlap
            overlap = len(set(task.required_capabilities) & set(agent_info.capabilities))
            total_caps = len(agent_info.capabilities)
            
            # Prefer specialists over generalists
            scores[agent_id] = overlap / total_caps if total_caps > 0 else 0
        
        return max(scores, key=scores.get)
    
    def _select_by_performance(self, agents: List[str]) -> str:
        """Select agent based on performance metrics"""
        scores = {}
        
        for agent_id in agents:
            agent_info = self.agents[agent_id]
            # Composite score: success rate + speed
            score = agent_info.success_rate * 0.7
            if agent_info.average_task_time > 0:
                score += (1 / agent_info.average_task_time) * 0.3
            scores[agent_id] = score
        
        return max(scores, key=scores.get)
    
    async def _run_task_auction(self, agents: List[str], task: HiveTask) -> Optional[str]:
        """Run auction for task assignment"""
        # Send bid requests
        bids = {}
        
        for agent_id in agents:
            response = await self.send_message(
                agent_id,
                HiveMessageType.RESOURCE_REQUEST,
                {"task": task.__dict__, "request": "bid"}
            )
            if response:
                bids[agent_id] = response.get("bid", float('inf'))
        
        # Select lowest bidder
        if bids:
            return min(bids, key=bids.get)
        
        return None
    
    async def _assign_task_to_agent(self, task: HiveTask, agent_id: str):
        """Assign task to specific agent"""
        task.assigned_to = agent_id
        task.started_at = datetime.now()
        
        self.active_tasks[task.task_id] = task
        self.agents[agent_id].current_load += 1
        
        # Send task to agent
        await self.send_message(
            agent_id,
            HiveMessageType.TASK_ASSIGNMENT,
            {"task": task.__dict__}
        )
        
        self.logger.info(f"Task {task.name} assigned to {self.agents[agent_id].name}")
    
    async def _reassign_agent_tasks(self, agent_id: str):
        """Reassign tasks from disconnected agent"""
        tasks_to_reassign = [
            task for task in self.active_tasks.values()
            if task.assigned_to == agent_id
        ]
        
        for task in tasks_to_reassign:
            task.assigned_to = None
            task.started_at = None
            self.task_queue.append(task)
            del self.active_tasks[task.task_id]
        
        self.logger.info(f"Reassigning {len(tasks_to_reassign)} tasks from agent {agent_id[:8]}")
    
    async def send_message(self, agent_id: str, msg_type: HiveMessageType, content: Dict[str, Any]):
        """Send message to agent"""
        if agent_id in self.agent_connections:
            connection = self.agent_connections[agent_id]
            message = {
                "type": msg_type.value,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            # Actual send implementation depends on connection type
            # await connection.send(json.dumps(message))
            return True
        return False
    
    async def broadcast_message(self, msg_type: HiveMessageType, content: Dict[str, Any]):
        """Broadcast message to all agents"""
        for agent_id in self.agents:
            await self.send_message(agent_id, msg_type, content)
    
    async def _process_messages(self):
        """Process incoming messages"""
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                msg_type = HiveMessageType(message.get("type"))
                
                if msg_type in self.message_handlers:
                    handler = self.message_handlers[msg_type]
                    await handler(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    async def _task_scheduler(self):
        """Background task scheduler"""
        while self.running:
            # Check for tasks ready to schedule
            ready_tasks = []
            
            for task_id, deps in list(self.task_dependencies.items()):
                completed_ids = {t.task_id for t in self.completed_tasks}
                if deps.issubset(completed_ids):
                    # Find task in queue
                    task = next((t for t in self.task_queue if t.task_id == task_id), None)
                    if task:
                        ready_tasks.append(task)
                        del self.task_dependencies[task_id]
            
            # Schedule ready tasks
            for task in ready_tasks:
                self.task_queue.remove(task)
                await self._schedule_task(task)
            
            await asyncio.sleep(1)
    
    async def _health_monitor(self):
        """Monitor agent health"""
        while self.running:
            current_time = datetime.now()
            
            for agent_id, agent_info in list(self.agents.items()):
                # Check heartbeat timeout (30 seconds)
                if (current_time - agent_info.last_heartbeat).seconds > 30:
                    self.logger.warning(f"Agent {agent_info.name} is unresponsive")
                    await self.unregister_agent(agent_id)
            
            await asyncio.sleep(10)
    
    async def _optimize_hive(self):
        """Optimize hive operations based on patterns"""
        while self.running:
            # Analyze task patterns
            self._analyze_task_patterns()
            
            # Optimize agent specializations
            self._optimize_agent_specializations()
            
            # Calculate hive efficiency
            self._calculate_hive_efficiency()
            
            await asyncio.sleep(60)  # Run every minute
    
    def _analyze_task_patterns(self):
        """Analyze patterns in completed tasks"""
        if len(self.completed_tasks) < 10:
            return
        
        # Analyze task types and frequencies
        task_types = defaultdict(int)
        capability_usage = defaultdict(int)
        
        for task in self.completed_tasks[-100:]:  # Last 100 tasks
            task_types[task.name] += 1
            for cap in task.required_capabilities:
                capability_usage[cap] += 1
        
        self.knowledge_base["task_patterns"] = {
            "frequent_tasks": dict(task_types),
            "capability_demand": dict(capability_usage)
        }
    
    def _optimize_agent_specializations(self):
        """Suggest agent specialization based on demand"""
        if not self.knowledge_base.get("task_patterns"):
            return
        
        capability_demand = self.knowledge_base["task_patterns"].get("capability_demand", {})
        
        # Calculate optimal agent distribution
        total_demand = sum(capability_demand.values())
        if total_demand > 0:
            optimal_distribution = {
                cap: count / total_demand 
                for cap, count in capability_demand.items()
            }
            
            self.knowledge_base["agent_specializations"] = optimal_distribution
    
    def _calculate_hive_efficiency(self):
        """Calculate overall hive efficiency"""
        if self.metrics["total_tasks"] > 0:
            completion_rate = self.metrics["completed_tasks"] / self.metrics["total_tasks"]
            
            # Average agent utilization
            if self.agents:
                total_utilization = sum(
                    agent.current_load / agent.max_load 
                    for agent in self.agents.values()
                )
                avg_utilization = total_utilization / len(self.agents)
            else:
                avg_utilization = 0
            
            # Composite efficiency score
            self.metrics["hive_efficiency"] = (completion_rate * 0.6 + avg_utilization * 0.4)
    
    # Message handlers
    async def _handle_register(self, message: Dict[str, Any]):
        """Handle agent registration"""
        content = message.get("content", {})
        agent_info = AgentInfo(**content.get("agent_info", {}))
        connection = content.get("connection")
        await self.register_agent(agent_info, connection)
    
    async def _handle_unregister(self, message: Dict[str, Any]):
        """Handle agent unregistration"""
        agent_id = message.get("content", {}).get("agent_id")
        if agent_id:
            await self.unregister_agent(agent_id)
    
    async def _handle_heartbeat(self, message: Dict[str, Any]):
        """Handle agent heartbeat"""
        agent_id = message.get("sender")
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = datetime.now()
    
    async def _handle_task_complete(self, message: Dict[str, Any]):
        """Handle task completion"""
        content = message.get("content", {})
        task_id = content.get("task_id")
        result = content.get("result")
        
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.completed_at = datetime.now()
            task.result = result
            
            # Update agent metrics
            if task.assigned_to in self.agents:
                agent = self.agents[task.assigned_to]
                agent.current_load -= 1
                
                # Update task time
                task_time = (task.completed_at - task.started_at).total_seconds()
                agent.average_task_time = (
                    (agent.average_task_time * self.metrics["completed_tasks"] + task_time) /
                    (self.metrics["completed_tasks"] + 1)
                )
            
            # Move to completed
            self.completed_tasks.append(task)
            del self.active_tasks[task_id]
            
            self.metrics["completed_tasks"] += 1
            
            self.logger.info(f"Task completed: {task.name}")
    
    async def _handle_task_failed(self, message: Dict[str, Any]):
        """Handle task failure"""
        content = message.get("content", {})
        task_id = content.get("task_id")
        error = content.get("error")
        
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.error = error
            
            # Update agent metrics
            if task.assigned_to in self.agents:
                agent = self.agents[task.assigned_to]
                agent.current_load -= 1
                agent.success_rate *= 0.95  # Decrease success rate
            
            # Retry or mark as failed
            if task.priority < 3:  # High priority tasks get retried
                task.assigned_to = None
                task.started_at = None
                self.task_queue.append(task)
                del self.active_tasks[task_id]
                self.logger.info(f"Retrying failed task: {task.name}")
            else:
                self.completed_tasks.append(task)
                del self.active_tasks[task_id]
                self.metrics["failed_tasks"] += 1
                self.logger.error(f"Task failed: {task.name} - {error}")
    
    async def _handle_capability_query(self, message: Dict[str, Any]):
        """Handle capability query"""
        content = message.get("content", {})
        required_capabilities = content.get("capabilities", [])
        
        matching_agents = [
            {
                "agent_id": agent_id,
                "name": agent.name,
                "capabilities": agent.capabilities
            }
            for agent_id, agent in self.agents.items()
            if all(cap in agent.capabilities for cap in required_capabilities)
        ]
        
        return {"agents": matching_agents}
    
    async def _handle_status_update(self, message: Dict[str, Any]):
        """Handle agent status update"""
        agent_id = message.get("sender")
        status = message.get("content", {}).get("status")
        
        if agent_id in self.agents:
            self.agents[agent_id].status = status
    
    async def _handle_resource_request(self, message: Dict[str, Any]):
        """Handle resource request from agent"""
        # Implementation depends on resource type
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get hive status report"""
        return {
            "hive_id": self.hive_id,
            "agents": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "metrics": self.metrics,
            "knowledge_base": self.knowledge_base
        }
    
    def shutdown(self):
        """Gracefully shutdown hive"""
        self.logger.info("Shutting down hive coordinator")
        self.running = False
        
        # Save state if configured
        if self.config.get("persist_state"):
            self._save_state()
    
    def _save_state(self):
        """Save hive state to disk"""
        state_file = Path(f"hive_state/{self.hive_id}.json")
        state_file.parent.mkdir(exist_ok=True)
        
        state = {
            "hive_id": self.hive_id,
            "metrics": self.metrics,
            "knowledge_base": self.knowledge_base,
            "completed_tasks": len(self.completed_tasks)
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)