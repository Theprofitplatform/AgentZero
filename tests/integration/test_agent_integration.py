"""Agent Integration Tests"""
import pytest
from datetime import datetime
import asyncio

from src.api.models.agent import Agent, AgentType, AgentStatus, AgentControlAction
from src.agents.planning_agent import PlanningAgent
from src.agents.execution_agent import ExecutionAgent
from src.core.hive_coordinator import HiveCoordinator

@pytest.mark.asyncio
class TestAgentIntegration:
    """Test agent integration with HiveCoordinator"""

    async def test_agent_registration(self):
        """Test agent registration with the hive"""
        hive = HiveCoordinator()

        # Create and register planning agent
        planning_agent = PlanningAgent(
            agent_id="plan-001",
            name="TestPlanner",
            capabilities=["task_decomposition", "resource_planning"]
        )

        # Register agent
        success = await hive.register_agent(planning_agent)
        assert success is True

        # Verify agent is registered
        agents = await hive.get_agents()
        assert len(agents) == 1
        assert agents[0].agent_id == "plan-001"

    async def test_agent_heartbeat(self):
        """Test agent heartbeat mechanism"""
        hive = HiveCoordinator()

        # Register agent
        agent = ExecutionAgent(
            agent_id="exec-001",
            name="TestExecutor",
            capabilities=["code_execution", "testing"]
        )
        await hive.register_agent(agent)

        # Send heartbeat
        initial_heartbeat = agent.last_heartbeat
        await asyncio.sleep(0.1)
        await agent.send_heartbeat()

        # Verify heartbeat updated
        assert agent.last_heartbeat > initial_heartbeat

    async def test_inter_agent_communication(self):
        """Test communication between agents"""
        hive = HiveCoordinator()

        # Create agents
        planner = PlanningAgent(
            agent_id="plan-001",
            name="Planner",
            capabilities=["planning"]
        )
        executor = ExecutionAgent(
            agent_id="exec-001",
            name="Executor",
            capabilities=["execution"]
        )

        # Register agents
        await hive.register_agent(planner)
        await hive.register_agent(executor)

        # Create a task
        task = {
            "id": "task-001",
            "name": "Test Task",
            "description": "Test inter-agent communication",
            "type": "complex",
            "priority": "high"
        }

        # Planner decomposes task
        subtasks = await planner.decompose_task(task)
        assert len(subtasks) > 0

        # Assign subtask to executor
        subtask = subtasks[0]
        success = await hive.assign_task_to_agent(subtask["id"], executor.agent_id)
        assert success is True

        # Verify executor received task
        assert executor.current_task is not None
        assert executor.current_task["id"] == subtask["id"]

    async def test_agent_failure_recovery(self):
        """Test agent failure and recovery scenarios"""
        hive = HiveCoordinator()

        # Register agent
        agent = ExecutionAgent(
            agent_id="exec-001",
            name="TestExecutor",
            capabilities=["execution"]
        )
        await hive.register_agent(agent)

        # Simulate agent failure
        agent.status = AgentStatus.ERROR
        agent.error_count += 1

        # Hive should detect failed agent
        failed_agents = await hive.get_failed_agents()
        assert len(failed_agents) == 1
        assert failed_agents[0].agent_id == "exec-001"

        # Attempt recovery
        success = await hive.recover_agent(agent.agent_id)
        assert success is True
        assert agent.status == AgentStatus.IDLE

    async def test_task_distribution(self):
        """Test task distribution across multiple agents"""
        hive = HiveCoordinator()

        # Register multiple execution agents
        agents = []
        for i in range(3):
            agent = ExecutionAgent(
                agent_id=f"exec-{i:03d}",
                name=f"Executor-{i}",
                capabilities=["execution"]
            )
            await hive.register_agent(agent)
            agents.append(agent)

        # Submit multiple tasks
        tasks = []
        for i in range(5):
            task = {
                "id": f"task-{i:03d}",
                "name": f"Task {i}",
                "type": "execution",
                "priority": "normal"
            }
            await hive.submit_task(task)
            tasks.append(task)

        # Wait for distribution
        await asyncio.sleep(0.5)

        # Verify tasks are distributed
        assigned_count = sum(1 for agent in agents if agent.current_task is not None)
        assert assigned_count > 0

        # Verify load balancing
        task_counts = [len(agent.task_history) for agent in agents]
        max_diff = max(task_counts) - min(task_counts)
        assert max_diff <= 2  # Reasonable balance

    async def test_agent_control_actions(self):
        """Test agent control actions (pause, resume, restart, terminate)"""
        hive = HiveCoordinator()

        # Register agent
        agent = ExecutionAgent(
            agent_id="exec-001",
            name="TestExecutor",
            capabilities=["execution"]
        )
        await hive.register_agent(agent)
        agent.status = AgentStatus.WORKING

        # Test pause
        success = await hive.control_agent(agent.agent_id, AgentControlAction.PAUSE)
        assert success is True
        assert agent.status == AgentStatus.IDLE

        # Test resume
        success = await hive.control_agent(agent.agent_id, AgentControlAction.RESUME)
        assert success is True
        assert agent.status == AgentStatus.WORKING

        # Test restart
        success = await hive.control_agent(agent.agent_id, AgentControlAction.RESTART)
        assert success is True
        assert agent.status == AgentStatus.IDLE
        assert agent.current_task is None

        # Test terminate
        success = await hive.control_agent(agent.agent_id, AgentControlAction.TERMINATE)
        assert success is True
        assert agent.status == AgentStatus.TERMINATED

        # Verify agent is removed from hive
        agents = await hive.get_agents()
        assert len(agents) == 0

    async def test_agent_capability_matching(self):
        """Test task assignment based on agent capabilities"""
        hive = HiveCoordinator()

        # Register agents with different capabilities
        planner = PlanningAgent(
            agent_id="plan-001",
            name="Planner",
            capabilities=["planning", "analysis"]
        )
        executor = ExecutionAgent(
            agent_id="exec-001",
            name="Executor",
            capabilities=["execution", "testing"]
        )

        await hive.register_agent(planner)
        await hive.register_agent(executor)

        # Submit planning task
        planning_task = {
            "id": "task-001",
            "name": "Planning Task",
            "type": "planning",
            "required_capabilities": ["planning"]
        }
        await hive.submit_task(planning_task)

        # Submit execution task
        execution_task = {
            "id": "task-002",
            "name": "Execution Task",
            "type": "execution",
            "required_capabilities": ["execution"]
        }
        await hive.submit_task(execution_task)

        # Wait for assignment
        await asyncio.sleep(0.5)

        # Verify correct assignment
        assert planner.current_task is not None
        assert planner.current_task["type"] == "planning"

        assert executor.current_task is not None
        assert executor.current_task["type"] == "execution"