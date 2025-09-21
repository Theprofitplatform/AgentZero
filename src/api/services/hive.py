"""Hive Service - Core orchestration logic"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
from collections import defaultdict

from ..models.agent import Agent, AgentUpdate, AgentStatus, AgentDetailResponse
from ..models.task import Task, TaskUpdate, TaskStatus, TaskDetailResponse, TaskStats
from ..config import settings

class HiveService:
    """Central service for managing agents and tasks"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.agent_tasks: Dict[str, List[str]] = defaultdict(list)
        self.agent_logs: Dict[str, List[str]] = defaultdict(list)
        self.task_logs: Dict[str, List[str]] = defaultdict(list)

    # Agent Management
    async def get_agents(
        self,
        status: Optional[AgentStatus] = None,
        agent_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Agent]:
        """Get all agents with optional filtering"""
        agents = list(self.agents.values())

        # Filter by status
        if status:
            agents = [a for a in agents if a.status == status]

        # Filter by type
        if agent_type:
            agents = [a for a in agents if a.type == agent_type]

        # Pagination
        return agents[skip:skip + limit]

    async def get_agent(self, agent_id: str) -> Optional[AgentDetailResponse]:
        """Get detailed agent information"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        return AgentDetailResponse(
            **agent.dict(),
            logs=self.agent_logs.get(agent_id, [])[-100:],
            task_history=self.agent_tasks.get(agent_id, [])[-50:]
        )

    async def register_agent(self, agent: Agent) -> Agent:
        """Register a new agent with the hive"""
        if len(self.agents) >= settings.max_agents:
            raise ValueError(f"Maximum number of agents ({settings.max_agents}) reached")

        self.agents[agent.id] = agent
        self.agent_logs[agent.id].append(
            f"[{datetime.utcnow().isoformat()}] Agent registered"
        )

        # Notify WebSocket clients
        from ..websocket import on_agent_registered
        await on_agent_registered(agent)

        return agent

    async def update_agent(self, agent_id: str, update_data: AgentUpdate) -> Agent:
        """Update agent configuration"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(agent, field, value)

        agent.last_updated = datetime.utcnow()

        # Notify if status changed
        if "status" in update_dict:
            from ..websocket import on_agent_status_changed
            await on_agent_status_changed(agent)

        return agent

    async def unregister_agent(self, agent_id: str):
        """Remove an agent from the hive"""
        if agent_id in self.agents:
            # Cancel any assigned tasks
            for task_id in self.agent_tasks.get(agent_id, []):
                task = self.tasks.get(task_id)
                if task and task.status == TaskStatus.RUNNING:
                    task.status = TaskStatus.CANCELLED
                    task.assigned_agent = None

            del self.agents[agent_id]

            # Notify WebSocket clients
            from ..websocket import on_agent_terminated
            await on_agent_terminated(agent_id)

    async def control_agent(self, agent_id: str, action: str) -> dict:
        """Send control command to an agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        result = {}

        if action == "pause":
            agent.status = AgentStatus.IDLE
            result["status"] = "paused"
        elif action == "resume":
            agent.status = AgentStatus.WORKING
            result["status"] = "resumed"
        elif action == "restart":
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            result["status"] = "restarted"
        elif action == "terminate":
            agent.status = AgentStatus.TERMINATED
            await self.unregister_agent(agent_id)
            result["status"] = "terminated"

        self.agent_logs[agent_id].append(
            f"[{datetime.utcnow().isoformat()}] Action: {action}"
        )

        return result

    async def update_heartbeat(self, agent_id: str):
        """Update agent heartbeat timestamp"""
        agent = self.agents.get(agent_id)
        if agent:
            agent.last_heartbeat = datetime.utcnow()
            agent.last_active = datetime.utcnow()

    async def get_agent_metrics(self, agent_id: str) -> dict:
        """Get agent performance metrics"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {}

        return {
            "agent_id": agent_id,
            "metrics": agent.metrics.dict(),
            "current_task": agent.current_task,
            "task_count": len(self.agent_tasks.get(agent_id, [])),
            "uptime": (datetime.utcnow() - agent.created_at).total_seconds()
        }

    async def get_agent_logs(
        self,
        agent_id: str,
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> List[str]:
        """Get agent execution logs"""
        logs = self.agent_logs.get(agent_id, [])

        if since:
            # Filter logs by timestamp
            filtered_logs = []
            for log in logs:
                # Parse timestamp from log line
                try:
                    log_time_str = log[1:20]  # Extract ISO timestamp
                    log_time = datetime.fromisoformat(log_time_str)
                    if log_time >= since:
                        filtered_logs.append(log)
                except:
                    filtered_logs.append(log)
            logs = filtered_logs

        return logs[-limit:]

    # Task Management
    async def get_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[str] = None,
        assigned_agent: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get all tasks with optional filtering"""
        tasks = list(self.tasks.values())

        # Filter by status
        if status:
            tasks = [t for t in tasks if t.status == status]

        # Filter by priority
        if priority:
            tasks = [t for t in tasks if t.priority == priority]

        # Filter by assigned agent
        if assigned_agent:
            tasks = [t for t in tasks if t.assigned_agent == assigned_agent]

        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        # Pagination
        return tasks[skip:skip + limit]

    async def get_task(self, task_id: str) -> Optional[TaskDetailResponse]:
        """Get detailed task information"""
        task = self.tasks.get(task_id)
        if not task:
            return None

        execution_time = None
        if task.started_at and task.completed_at:
            execution_time = (task.completed_at - task.started_at).total_seconds()

        return TaskDetailResponse(
            **task.dict(),
            logs=self.task_logs.get(task_id, [])[-100:],
            execution_time=execution_time
        )

    async def submit_task(self, task: Task) -> Task:
        """Submit a new task to the hive"""
        self.tasks[task.id] = task
        task.status = TaskStatus.QUEUED

        # Add to task queue
        await self.task_queue.put(task.id)

        self.task_logs[task.id].append(
            f"[{datetime.utcnow().isoformat()}] Task created and queued"
        )

        # Notify WebSocket clients
        from ..websocket import on_task_created
        await on_task_created(task)

        # Try to assign to an available agent
        await self.assign_task(task.id)

        return task

    async def update_task(self, task_id: str, update_data: TaskUpdate) -> Task:
        """Update task configuration"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()

        # Notify WebSocket clients
        from ..websocket import on_task_updated
        await on_task_updated(task)

        return task

    async def cancel_task(self, task_id: str):
        """Cancel a task"""
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.utcnow()

            # Remove from agent if assigned
            if task.assigned_agent:
                agent = self.agents.get(task.assigned_agent)
                if agent and agent.current_task == task_id:
                    agent.current_task = None
                    agent.status = AgentStatus.IDLE

            self.task_logs[task_id].append(
                f"[{datetime.utcnow().isoformat()}] Task cancelled"
            )

    async def retry_task(self, task_id: str) -> Task:
        """Retry a failed task"""
        original_task = self.tasks.get(task_id)
        if not original_task:
            raise ValueError(f"Task {task_id} not found")

        # Create new task with same parameters
        new_task = Task(
            id=f"task-retry-{task_id[-8:]}",
            name=f"{original_task.name} (Retry)",
            description=original_task.description,
            type=original_task.type,
            priority=original_task.priority,
            parameters=original_task.parameters,
            dependencies=original_task.dependencies,
            tags=original_task.tags + ["retry"],
            metadata={**original_task.metadata, "original_task": task_id},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        return await self.submit_task(new_task)

    async def assign_task(self, task_id: str):
        """Assign a task to an available agent"""
        task = self.tasks.get(task_id)
        if not task or task.status != TaskStatus.QUEUED:
            return

        # Find an idle agent with matching capabilities
        for agent_id, agent in self.agents.items():
            if agent.status == AgentStatus.IDLE:
                # Check if agent can handle this task type
                # This is a simplified check - implement proper capability matching
                task.assigned_agent = agent_id
                task.assigned_to = agent.name
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.utcnow()

                agent.current_task = task_id
                agent.status = AgentStatus.WORKING

                self.agent_tasks[agent_id].append(task_id)

                self.task_logs[task_id].append(
                    f"[{datetime.utcnow().isoformat()}] Assigned to agent {agent.name}"
                )

                break

    async def complete_task(self, task_id: str, result: Any):
        """Mark a task as completed"""
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            task.progress = 100.0

            # Update agent
            if task.assigned_agent:
                agent = self.agents.get(task.assigned_agent)
                if agent:
                    agent.current_task = None
                    agent.status = AgentStatus.IDLE
                    agent.metrics.tasks_completed += 1

            # Notify WebSocket clients
            from ..websocket import on_task_completed
            await on_task_completed(task)

    async def fail_task(self, task_id: str, error: str):
        """Mark a task as failed"""
        task = self.tasks.get(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error = error
            task.completed_at = datetime.utcnow()

            # Update agent
            if task.assigned_agent:
                agent = self.agents.get(task.assigned_agent)
                if agent:
                    agent.current_task = None
                    agent.status = AgentStatus.IDLE
                    agent.metrics.tasks_failed += 1

            # Notify WebSocket clients
            from ..websocket import on_task_failed
            await on_task_failed(task, error)

    async def get_task_logs(
        self,
        task_id: str,
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> List[str]:
        """Get task execution logs"""
        logs = self.task_logs.get(task_id, [])

        if since:
            # Filter logs by timestamp
            filtered_logs = []
            for log in logs:
                try:
                    log_time_str = log[1:20]
                    log_time = datetime.fromisoformat(log_time_str)
                    if log_time >= since:
                        filtered_logs.append(log)
                except:
                    filtered_logs.append(log)
            logs = filtered_logs

        return logs[-limit:]

    async def get_task_statistics(self, since: Optional[datetime] = None) -> dict:
        """Get aggregated task statistics"""
        tasks = list(self.tasks.values())

        if since:
            tasks = [t for t in tasks if t.created_at >= since]

        stats = TaskStats()
        stats.total = len(tasks)

        status_counts = defaultdict(int)
        for task in tasks:
            status_counts[task.status] += 1

        stats.pending = status_counts[TaskStatus.PENDING]
        stats.running = status_counts[TaskStatus.RUNNING]
        stats.completed = status_counts[TaskStatus.COMPLETED]
        stats.failed = status_counts[TaskStatus.FAILED]

        if stats.total > 0:
            stats.success_rate = stats.completed / stats.total

        return {
            "stats": stats.dict(),
            "by_type": self._get_task_distribution_by_type(tasks),
            "by_priority": self._get_task_distribution_by_priority(tasks),
            "average_execution_time": self._calculate_avg_execution_time(tasks)
        }

    def _get_task_distribution_by_type(self, tasks: List[Task]) -> dict:
        """Get task distribution by type"""
        distribution = defaultdict(int)
        for task in tasks:
            distribution[task.type] += 1
        return dict(distribution)

    def _get_task_distribution_by_priority(self, tasks: List[Task]) -> dict:
        """Get task distribution by priority"""
        distribution = defaultdict(int)
        for task in tasks:
            distribution[task.priority] += 1
        return dict(distribution)

    def _calculate_avg_execution_time(self, tasks: List[Task]) -> float:
        """Calculate average execution time for completed tasks"""
        completed_tasks = [
            t for t in tasks
            if t.status == TaskStatus.COMPLETED and t.started_at and t.completed_at
        ]

        if not completed_tasks:
            return 0.0

        total_time = sum(
            (t.completed_at - t.started_at).total_seconds()
            for t in completed_tasks
        )

        return total_time / len(completed_tasks)

# Create global hive service instance
hive_service = HiveService()