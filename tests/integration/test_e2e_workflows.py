"""End-to-End Workflow Integration Tests"""
import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.api.models.agent import Agent, AgentType, AgentStatus
from src.api.models.task import Task, TaskType, TaskPriority, TaskStatus
from src.core.hive_coordinator import HiveCoordinator
from src.agents.planning_agent import PlanningAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.research_agent import ResearchAgent

@pytest.mark.asyncio
class TestE2EWorkflows:
    """Test complete end-to-end workflows"""

    async def test_complete_task_workflow(self):
        """Test complete task lifecycle from creation to completion"""
        hive = HiveCoordinator()

        # Setup agents
        planner = PlanningAgent(
            agent_id="plan-001",
            name="MasterPlanner",
            capabilities=["planning", "task_decomposition"]
        )

        executors = []
        for i in range(3):
            executor = ExecutionAgent(
                agent_id=f"exec-{i:03d}",
                name=f"Executor-{i}",
                capabilities=["execution", "testing"]
            )
            await hive.register_agent(executor)
            executors.append(executor)

        await hive.register_agent(planner)

        # Create complex task
        main_task = {
            "id": "main-001",
            "name": "Build Feature X",
            "description": "Complete implementation of Feature X",
            "type": "complex",
            "priority": "high",
            "requirements": [
                "Design API",
                "Implement backend",
                "Create UI",
                "Write tests",
                "Deploy to staging"
            ]
        }

        # Submit task to hive
        await hive.submit_task(main_task)

        # Planner decomposes task
        subtasks = await planner.decompose_task(main_task)
        assert len(subtasks) >= 5

        # Submit subtasks
        for subtask in subtasks:
            await hive.submit_task(subtask)

        # Wait for task distribution
        await asyncio.sleep(0.5)

        # Verify all subtasks are assigned
        assigned_tasks = []
        for executor in executors:
            if executor.current_task:
                assigned_tasks.append(executor.current_task)

        assert len(assigned_tasks) > 0

        # Simulate task execution
        for executor in executors:
            if executor.current_task:
                # Execute task
                result = await executor.execute_task(executor.current_task)
                assert result["status"] == "completed"

                # Report completion to hive
                await hive.complete_task(
                    executor.current_task["id"],
                    result
                )

        # Verify main task status
        main_task_status = await hive.get_task_status(main_task["id"])
        assert main_task_status in ["in_progress", "completed"]

        # Get execution metrics
        metrics = await hive.get_execution_metrics()
        assert metrics["tasks_completed"] > 0
        assert metrics["average_execution_time"] > 0

    async def test_multi_agent_collaboration(self):
        """Test collaboration between different agent types"""
        hive = HiveCoordinator()

        # Setup diverse agent team
        planner = PlanningAgent(
            agent_id="plan-001",
            name="Planner",
            capabilities=["planning", "analysis"]
        )

        researcher = ResearchAgent(
            agent_id="research-001",
            name="Researcher",
            capabilities=["research", "data_gathering"]
        )

        executor = ExecutionAgent(
            agent_id="exec-001",
            name="Executor",
            capabilities=["execution", "implementation"]
        )

        # Register all agents
        for agent in [planner, researcher, executor]:
            await hive.register_agent(agent)

        # Create research-driven task
        research_task = {
            "id": "research-001",
            "name": "Analyze Market Trends",
            "description": "Research and analyze current market trends",
            "type": "research",
            "priority": "high",
            "phases": ["research", "analysis", "report"]
        }

        # Phase 1: Research
        await hive.submit_task(research_task)
        research_result = await researcher.conduct_research(research_task)
        assert research_result["status"] == "completed"
        assert "findings" in research_result

        # Phase 2: Planning based on research
        planning_task = {
            "id": "plan-001",
            "name": "Create Strategy",
            "description": "Plan strategy based on research",
            "type": "planning",
            "priority": "high",
            "input_data": research_result["findings"]
        }

        await hive.submit_task(planning_task)
        plan = await planner.create_plan(planning_task)
        assert plan["status"] == "completed"
        assert "action_items" in plan

        # Phase 3: Execute plan
        for idx, action_item in enumerate(plan["action_items"][:3]):
            execution_task = {
                "id": f"exec-{idx:03d}",
                "name": action_item["name"],
                "description": action_item["description"],
                "type": "execution",
                "priority": action_item.get("priority", "normal")
            }

            await hive.submit_task(execution_task)
            result = await executor.execute_task(execution_task)
            assert result["status"] == "completed"

        # Verify collaboration metrics
        collab_metrics = await hive.get_collaboration_metrics()
        assert collab_metrics["agents_involved"] == 3
        assert collab_metrics["tasks_completed"] >= 4

    async def test_failure_recovery_workflow(self):
        """Test workflow recovery from agent failures"""
        hive = HiveCoordinator()

        # Setup redundant executors
        executors = []
        for i in range(5):
            executor = ExecutionAgent(
                agent_id=f"exec-{i:03d}",
                name=f"Executor-{i}",
                capabilities=["execution"]
            )
            await hive.register_agent(executor)
            executors.append(executor)

        # Submit critical tasks
        critical_tasks = []
        for i in range(10):
            task = {
                "id": f"critical-{i:03d}",
                "name": f"Critical Task {i}",
                "type": "execution",
                "priority": "critical",
                "retry_on_failure": True,
                "max_retries": 3
            }
            await hive.submit_task(task)
            critical_tasks.append(task)

        # Wait for initial distribution
        await asyncio.sleep(0.5)

        # Simulate failures in some agents
        failed_agents = executors[:2]
        for agent in failed_agents:
            agent.status = AgentStatus.ERROR
            agent.error_count = 3

            # Get task that was assigned to failed agent
            if agent.current_task:
                failed_task_id = agent.current_task["id"]

                # Hive should detect failure and reassign
                await hive.handle_agent_failure(agent.agent_id)

                # Wait for reassignment
                await asyncio.sleep(0.2)

                # Verify task was reassigned
                new_assignment = await hive.get_task_assignment(failed_task_id)
                assert new_assignment is not None
                assert new_assignment["agent_id"] != agent.agent_id

        # Healthy agents complete tasks
        for agent in executors[2:]:
            while agent.current_task:
                result = await agent.execute_task(agent.current_task)
                await hive.complete_task(agent.current_task["id"], result)

                # Get next task
                next_task = await hive.get_next_task_for_agent(agent.agent_id)
                if next_task:
                    agent.current_task = next_task
                else:
                    agent.current_task = None

        # Verify all critical tasks completed despite failures
        completed_count = 0
        for task in critical_tasks:
            status = await hive.get_task_status(task["id"])
            if status == "completed":
                completed_count += 1

        assert completed_count == len(critical_tasks)

    async def test_priority_based_scheduling(self):
        """Test priority-based task scheduling"""
        hive = HiveCoordinator()

        # Setup executor
        executor = ExecutionAgent(
            agent_id="exec-001",
            name="PriorityExecutor",
            capabilities=["execution"]
        )
        await hive.register_agent(executor)

        # Submit tasks with different priorities
        tasks = []
        priorities = ["critical", "high", "normal", "low"]
        for priority in priorities:
            for i in range(3):
                task = {
                    "id": f"{priority}-{i:03d}",
                    "name": f"{priority.title()} Priority Task {i}",
                    "type": "execution",
                    "priority": priority,
                    "submitted_at": datetime.utcnow()
                }
                await hive.submit_task(task)
                tasks.append(task)

        # Track execution order
        execution_order = []

        while True:
            task = await hive.get_next_task_for_agent(executor.agent_id)
            if not task:
                break

            execution_order.append(task["priority"])

            # Simulate execution
            result = await executor.execute_task(task)
            await hive.complete_task(task["id"], result)

        # Verify priority order
        # Critical tasks should be executed first
        critical_count = execution_order[:3].count("critical")
        assert critical_count == 3

        # High priority should come before normal and low
        high_index = execution_order.index("high")
        normal_index = execution_order.index("normal")
        low_index = execution_order.index("low")
        assert high_index < normal_index < low_index

    async def test_resource_optimization_workflow(self):
        """Test workflow that optimizes resource usage"""
        hive = HiveCoordinator()

        # Setup agents with different resource profiles
        agents = []

        # High-performance agent
        high_perf = ExecutionAgent(
            agent_id="high-001",
            name="HighPerformance",
            capabilities=["heavy_computation", "ml_training"],
            max_concurrent_tasks=1,
            resource_tier="high"
        )
        agents.append(high_perf)

        # Medium-performance agents
        for i in range(2):
            med_perf = ExecutionAgent(
                agent_id=f"med-{i:03d}",
                name=f"MediumPerf-{i}",
                capabilities=["general_execution", "data_processing"],
                max_concurrent_tasks=3,
                resource_tier="medium"
            )
            agents.append(med_perf)

        # Low-performance agents
        for i in range(3):
            low_perf = ExecutionAgent(
                agent_id=f"low-{i:03d}",
                name=f"LowPerf-{i}",
                capabilities=["simple_tasks", "monitoring"],
                max_concurrent_tasks=5,
                resource_tier="low"
            )
            agents.append(low_perf)

        # Register all agents
        for agent in agents:
            await hive.register_agent(agent)

        # Submit tasks with resource requirements
        heavy_task = {
            "id": "heavy-001",
            "name": "Train ML Model",
            "type": "ml_training",
            "required_capabilities": ["ml_training"],
            "resource_requirement": "high",
            "estimated_duration": 3600
        }

        medium_tasks = []
        for i in range(5):
            task = {
                "id": f"medium-{i:03d}",
                "name": f"Process Dataset {i}",
                "type": "data_processing",
                "required_capabilities": ["data_processing"],
                "resource_requirement": "medium",
                "estimated_duration": 600
            }
            medium_tasks.append(task)

        light_tasks = []
        for i in range(10):
            task = {
                "id": f"light-{i:03d}",
                "name": f"Monitor Service {i}",
                "type": "monitoring",
                "required_capabilities": ["monitoring"],
                "resource_requirement": "low",
                "estimated_duration": 60
            }
            light_tasks.append(task)

        # Submit all tasks
        await hive.submit_task(heavy_task)
        for task in medium_tasks + light_tasks:
            await hive.submit_task(task)

        # Wait for distribution
        await asyncio.sleep(1)

        # Verify appropriate assignment
        assert high_perf.current_task is not None
        assert high_perf.current_task["id"] == "heavy-001"

        # Check medium agents got medium tasks
        for agent in agents[1:3]:
            if agent.current_task:
                assert "medium" in agent.current_task["id"]

        # Check low agents got light tasks
        for agent in agents[3:]:
            if agent.current_task:
                assert "light" in agent.current_task["id"]

        # Verify resource utilization metrics
        metrics = await hive.get_resource_metrics()
        assert metrics["resource_efficiency"] > 0.7
        assert metrics["task_distribution_score"] > 0.8

    async def test_real_time_adaptation(self):
        """Test system adaptation to changing conditions"""
        hive = HiveCoordinator()

        # Start with minimal agents
        initial_agents = []
        for i in range(2):
            agent = ExecutionAgent(
                agent_id=f"adaptive-{i:03d}",
                name=f"AdaptiveAgent-{i}",
                capabilities=["execution", "scaling"]
            )
            await hive.register_agent(agent)
            initial_agents.append(agent)

        # Submit initial load
        for i in range(5):
            task = {
                "id": f"initial-{i:03d}",
                "name": f"Initial Task {i}",
                "type": "execution",
                "priority": "normal"
            }
            await hive.submit_task(task)

        # Monitor queue depth
        initial_queue_depth = await hive.get_queue_depth()
        assert initial_queue_depth > 0

        # Simulate load spike
        for i in range(20):
            task = {
                "id": f"spike-{i:03d}",
                "name": f"Spike Task {i}",
                "type": "execution",
                "priority": "high"
            }
            await hive.submit_task(task)

        # System should detect high load
        queue_depth = await hive.get_queue_depth()
        assert queue_depth > initial_queue_depth

        # Add more agents to handle load
        additional_agents = []
        for i in range(3):
            agent = ExecutionAgent(
                agent_id=f"scale-{i:03d}",
                name=f"ScaledAgent-{i}",
                capabilities=["execution", "scaling"]
            )
            await hive.register_agent(agent)
            additional_agents.append(agent)

        # Wait for rebalancing
        await asyncio.sleep(1)

        # Verify load is distributed
        all_agents = initial_agents + additional_agents
        working_agents = sum(1 for a in all_agents if a.current_task is not None)
        assert working_agents >= 4

        # Process tasks
        for _ in range(25):
            for agent in all_agents:
                if agent.current_task:
                    result = await agent.execute_task(agent.current_task)
                    await hive.complete_task(agent.current_task["id"], result)

                    # Get next task
                    next_task = await hive.get_next_task_for_agent(agent.agent_id)
                    agent.current_task = next_task

        # Verify adaptation metrics
        adaptation_metrics = await hive.get_adaptation_metrics()
        assert adaptation_metrics["scale_up_triggered"] is True
        assert adaptation_metrics["response_time_improved"] is True
        assert adaptation_metrics["throughput_increased"] is True