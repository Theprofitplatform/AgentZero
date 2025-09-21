"""
Test suite for Planning Agent
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime
from pathlib import Path
import sys
sys.path.append('/mnt/c/Users/abhis/projects/AgentZero')

from src.agents.planning_agent import PlanningAgent, Phase, Plan, AllocationPlan
from src.core.agent import Task, Priority, AgentStatus, BaseAgent


class TestPlanningAgent:
    """Test Planning Agent functionality"""

    @pytest_asyncio.fixture
    async def planning_agent(self):
        """Create Planning Agent instance"""
        config = {
            "planning_horizon": 90,
            "max_parallel_tasks": 10,
            "max_decomposition_depth": 5
        }
        return PlanningAgent(agent_id="test-planner", name="TestPlanner", config=config)

    @pytest.mark.asyncio
    async def test_agent_initialization(self, planning_agent):
        """Test agent initialization"""
        assert planning_agent.name == "TestPlanner"
        assert planning_agent.agent_id == "test-planner"
        assert planning_agent.planning_horizon == 90
        assert planning_agent.max_parallel_tasks == 10
        assert len(planning_agent.capabilities) >= 5  # Should have planning capabilities

    @pytest.mark.asyncio
    async def test_create_strategic_plan(self, planning_agent):
        """Test strategic plan creation"""
        params = {
            "project_name": "Test Project",
            "duration_months": 3,
            "goals": ["Build MVP", "Launch Beta", "Production Release"],
            "constraints": {
                "budget": 150000,
                "team_size": 5
            }
        }

        plan = await planning_agent._create_strategic_plan(params)

        assert plan["project_name"] == "Test Project"
        assert plan["duration_months"] == 3
        assert "phases" in plan
        assert "total_budget" in plan
        assert "team_composition" in plan
        assert "success_metrics" in plan

    @pytest.mark.asyncio
    async def test_task_decomposition(self, planning_agent):
        """Test task decomposition"""
        params = {
            "task": "Build Authentication System",
            "complexity": "high"
        }

        breakdown = await planning_agent._decompose_task(params)

        assert breakdown["main_task"] == "Build Authentication System"
        assert "subtasks" in breakdown
        assert len(breakdown["subtasks"]) > 0
        assert "total_estimated_hours" in breakdown
        assert "critical_path" in breakdown
        assert "parallel_opportunities" in breakdown

    @pytest.mark.asyncio
    async def test_recursive_decomposition_depth_limit(self, planning_agent):
        """Test that recursive decomposition respects depth limit"""
        params = {
            "task": "Complex System",
            "complexity": "high",
            "_depth": 4  # Near max depth
        }

        breakdown = await planning_agent._decompose_task(params)

        # Should stop at max depth
        assert breakdown["decomposition_depth"] == 4
        if breakdown["decomposition_depth"] >= planning_agent.max_decomposition_depth - 1:
            # Subtasks should not have further decomposition
            for subtask in breakdown["subtasks"]:
                assert "subtasks" not in subtask or len(subtask.get("subtasks", [])) == 0

    @pytest.mark.asyncio
    async def test_resource_allocation(self, planning_agent):
        """Test resource allocation"""
        params = {
            "project_name": "Test Allocation",
            "budget": 100000,
            "team_size": 5,
            "duration_months": 3
        }

        allocation = await planning_agent._allocate_resources(params)

        assert allocation["project_name"] == "Test Allocation"
        assert allocation["total_budget"] == 100000
        assert "team_allocation" in allocation
        assert "budget_breakdown" in allocation
        assert "infrastructure_needs" in allocation
        assert allocation["team_allocation"]["senior_developers"] >= 1

    @pytest.mark.asyncio
    async def test_timeline_creation(self, planning_agent):
        """Test timeline creation"""
        params = {
            "project_name": "Timeline Test",
            "start_date": datetime.now().isoformat(),
            "milestones": ["Alpha", "Beta", "Production"]
        }

        timeline = await planning_agent._create_timeline(params)

        assert timeline["project_name"] == "Timeline Test"
        assert "events" in timeline
        assert len(timeline["events"]) == 3
        assert "critical_dates" in timeline
        assert "review_points" in timeline

    @pytest.mark.asyncio
    async def test_risk_assessment(self, planning_agent):
        """Test risk assessment"""
        params = {
            "project_name": "Risk Test",
            "project_type": "software",
            "team_size": 3
        }

        assessment = await planning_agent._assess_risks(params)

        assert assessment["project_name"] == "Risk Test"
        assert "risks" in assessment
        assert len(assessment["risks"]) > 0
        assert "overall_risk_level" in assessment
        assert "recommendations" in assessment

        # Check risk scoring
        for risk in assessment["risks"]:
            assert "risk_score" in risk
            assert "priority" in risk

    @pytest.mark.asyncio
    async def test_execute_task(self, planning_agent):
        """Test task execution"""
        task = Task(
            name="Create Project Plan",
            description="Create strategic plan for new project",
            priority=Priority.HIGH,
            parameters={
                "type": "strategic_planning",
                "project_name": "Execute Test",
                "duration_months": 2
            }
        )

        result = await planning_agent.execute(task)

        assert result is not None
        assert "project_name" in result
        assert result["project_name"] == "Execute Test"

    @pytest.mark.asyncio
    async def test_critical_path_calculation(self, planning_agent):
        """Test critical path calculation"""
        import networkx as nx

        # Create test graph
        graph = nx.DiGraph()
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        graph.add_edge("B", "D")
        graph.add_edge("C", "D")

        durations = {"A": 5, "B": 3, "C": 7, "D": 2}

        critical_path = planning_agent._calculate_critical_path(graph, durations)

        assert critical_path is not None
        assert len(critical_path) > 0
        # Path A->C->D should be critical (5+7+2=14 vs 5+3+2=10)
        assert "C" in critical_path

    @pytest.mark.asyncio
    async def test_parallel_task_identification(self, planning_agent):
        """Test parallel task identification"""
        graph = planning_agent.task_graph
        tasks = [
            {"id": "task1", "dependencies": []},
            {"id": "task2", "dependencies": []},
            {"id": "task3", "dependencies": ["task1"]},
            {"id": "task4", "dependencies": ["task2"]}
        ]

        # Add to graph
        for task in tasks:
            graph.add_node(task["id"])
            for dep in task["dependencies"]:
                if dep in graph:
                    graph.add_edge(dep, task["id"])

        parallel_groups = planning_agent._identify_parallel_task_groups(graph, tasks)

        # task1 and task2 should be identified as parallel
        assert len(parallel_groups) > 0

    def test_phase_name_generation(self, planning_agent):
        """Test phase name generation"""
        name = planning_agent._get_phase_name(0, 3)
        assert name is not None
        assert len(name) > 0

        # Test different months
        for month in range(6):
            name = planning_agent._get_phase_name(month, 6)
            assert name is not None

    def test_task_duration_estimation(self, planning_agent):
        """Test task duration estimation"""
        setup_duration = planning_agent._estimate_task_duration("Setup environment")
        impl_duration = planning_agent._estimate_task_duration("Implement feature")
        test_duration = planning_agent._estimate_task_duration("Test functionality")

        assert setup_duration == 2.0  # Setup tasks
        assert impl_duration == 5.0   # Implementation tasks
        assert test_duration == 3.0   # Testing tasks

    def test_budget_calculation(self, planning_agent):
        """Test budget calculation"""
        budget = planning_agent._calculate_detailed_budget(
            months=3,
            team_size=5,
            constraints={"avg_salary": 10000, "infrastructure_cost": 5000, "tools_cost": 2000}
        )

        assert budget is not None
        assert "$" in budget
        assert "," in budget  # Should be formatted

    @pytest.mark.asyncio
    async def test_skill_matching(self, planning_agent):
        """Test skill matching for resource allocation"""
        # Create mock agent class
        class MockAgent(BaseAgent):
            async def execute(self, task):
                return {"status": "completed"}

        # Create mock agent
        agent = MockAgent(agent_id="test-agent", name="TestAgent")
        agent.capabilities = []  # Empty capabilities

        required_skills = ["Python", "AsyncIO", "REST API"]

        has_skills = planning_agent._agent_has_skills(agent.capabilities, required_skills)
        assert has_skills is False  # Agent has no capabilities

        # Calculate expertise bonus
        bonus = planning_agent._calculate_expertise_bonus(agent.capabilities, required_skills)
        assert bonus == 0  # No matching skills

    @pytest.mark.asyncio
    async def test_decomposition_risk_identification(self, planning_agent):
        """Test risk identification in decomposition"""
        import networkx as nx

        # Create complex task structure
        tasks = [{"id": f"task_{i}", "estimated_hours": 8} for i in range(25)]
        graph = nx.DiGraph()

        # Add many dependencies to one task (bottleneck)
        for i in range(10):
            graph.add_edge(f"task_{i}", "task_20")

        risks = planning_agent._identify_decomposition_risks(tasks, graph)

        assert len(risks) > 0
        assert any("task count" in risk for risk in risks)  # High task count risk
        assert any("bottleneck" in risk for risk in risks)  # Bottleneck risk


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])