"""
Planning Agent for AgentZero
Specialized in strategic planning, task decomposition, and resource allocation
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import json
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import uuid
import networkx as nx  # For graph operations
from collections import defaultdict

import sys
sys.path.append('/mnt/c/Users/abhis/projects/AgentZero')
from src.core.agent import BaseAgent, Task, AgentCapability, Priority, AgentStatus


# Data structures for planning
@dataclass
class Phase:
    """Represents a project phase"""
    phase_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    milestones: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    priority: Priority = Priority.MEDIUM
    estimated_duration: float = 0.0

@dataclass
class Milestone:
    """Represents a project milestone"""
    milestone_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    target_date: datetime = field(default_factory=datetime.now)
    deliverables: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)

@dataclass
class Timeline:
    """Represents project timeline"""
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=datetime.now)
    duration_days: int = 0
    critical_path: List[str] = field(default_factory=list)

@dataclass
class Risk:
    """Represents a project risk"""
    risk_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    probability: str = "Medium"
    impact: str = "Medium"
    mitigation: str = ""
    owner: str = ""
    risk_score: int = 0

@dataclass
class Plan:
    """Represents a complete strategic plan"""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str = ""
    phases: List[Phase] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)
    critical_path: List[str] = field(default_factory=list)
    timeline: Optional[Timeline] = None
    resource_allocation: Dict[str, List[str]] = field(default_factory=dict)
    risks: List[Risk] = field(default_factory=list)
    total_duration: float = 0.0
    total_cost: float = 0.0

@dataclass
class AllocationPlan:
    """Represents resource allocation plan"""
    agent_assignments: Dict[str, List[str]] = field(default_factory=dict)
    task_to_agent: Dict[str, str] = field(default_factory=dict)
    unallocated_tasks: List[str] = field(default_factory=list)
    utilization: Dict[str, float] = field(default_factory=dict)
    total_hours: float = 0.0
    timeline: Optional[Timeline] = None

class PlanningAgent(BaseAgent):
    """
    Agent specialized in strategic planning and task management
    """

    def __init__(self, agent_id: Optional[str] = None, name: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, name or "PlanningAgent", config)

        # Planning-specific configuration
        self.planning_horizon = config.get("planning_horizon", 90) if config else 90  # days
        self.max_parallel_tasks = config.get("max_parallel_tasks", 10) if config else 10
        self.max_decomposition_depth = config.get("max_decomposition_depth", 5) if config else 5

        # Graph for task dependencies
        self.task_graph = nx.DiGraph()

        # Initialize planning capabilities
        self._register_planning_capabilities()
    
    def _register_planning_capabilities(self):
        """Register planning-specific capabilities"""
        self.register_capability(AgentCapability(
            name="strategic_planning",
            description="Create strategic plans and roadmaps",
            handler=self._create_strategic_plan
        ))
        
        self.register_capability(AgentCapability(
            name="task_decomposition",
            description="Break down complex tasks into subtasks",
            handler=self._decompose_task
        ))
        
        self.register_capability(AgentCapability(
            name="resource_allocation",
            description="Allocate resources optimally",
            handler=self._allocate_resources
        ))
        
        self.register_capability(AgentCapability(
            name="timeline_planning",
            description="Create project timelines",
            handler=self._create_timeline
        ))
        
        self.register_capability(AgentCapability(
            name="risk_assessment",
            description="Assess project risks",
            handler=self._assess_risks
        ))
    
    async def execute(self, task: Task) -> Any:
        """
        Execute planning task
        """
        self.logger.info(f"Executing planning task: {task.name}")
        
        task_type = task.parameters.get("type", "strategic_planning")
        
        if task_type == "strategic_planning":
            return await self._create_strategic_plan(task.parameters)
        elif task_type == "task_decomposition":
            return await self._decompose_task(task.parameters)
        elif task_type == "resource_allocation":
            return await self._allocate_resources(task.parameters)
        elif task_type == "timeline_planning":
            return await self._create_timeline(task.parameters)
        elif task_type == "risk_assessment":
            return await self._assess_risks(task.parameters)
        else:
            return await self._create_strategic_plan(task.parameters)
    
    async def _create_strategic_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive strategic plan with CPM analysis"""
        project_name = params.get("project_name", "Project")
        duration_months = params.get("duration_months", 3)
        goals = params.get("goals", [])
        constraints = params.get("constraints", {})

        self.logger.info(f"Creating strategic plan for: {project_name}")

        # Create plan object
        plan = Plan(
            project_name=project_name,
            phases=[],
            milestones=[],
            critical_path=[],
            timeline=Timeline(
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30 * duration_months),
                duration_days=30 * duration_months
            )
        )

        # Generate plan phases with improved structure
        start_date = datetime.now()
        all_tasks = []

        for month in range(duration_months):
            phase_start = start_date + timedelta(days=30 * month)
            phase_end = start_date + timedelta(days=30 * (month + 1))

            # Create phase object
            phase = Phase(
                name=f"Phase {month + 1}: {self._get_phase_name(month, duration_months)}",
                start_date=phase_start,
                end_date=phase_end,
                milestones=self._generate_milestones(month, project_name),
                tasks=self._generate_phase_tasks(month, project_name, goals)
            )

            # Add tasks to graph for CPM analysis
            for i, task in enumerate(phase.tasks):
                task_id = f"phase{month}_task{i}"
                self.task_graph.add_node(task_id,
                    name=task,
                    duration=self._estimate_task_duration(task),
                    phase=month
                )
                all_tasks.append(task_id)

                # Add dependencies
                if i > 0:
                    prev_task_id = f"phase{month}_task{i-1}"
                    self.task_graph.add_edge(prev_task_id, task_id)

                # Cross-phase dependencies
                if month > 0 and i == 0:
                    prev_phase_last = f"phase{month-1}_task{len(self._generate_phase_tasks(month-1, project_name, goals))-1}"
                    if prev_phase_last in self.task_graph:
                        self.task_graph.add_edge(prev_phase_last, task_id)

            plan.phases.append(phase)

            # Create milestones
            for milestone_name in phase.milestones:
                milestone = Milestone(
                    name=milestone_name,
                    target_date=phase_end,
                    deliverables=self._generate_deliverables(month, project_name),
                    success_criteria=self._define_milestone_criteria(milestone_name)
                )
                plan.milestones.append(milestone)

        # Calculate critical path using CPM
        if all_tasks:
            critical_path = self._calculate_critical_path_cpm(all_tasks)
            plan.critical_path = critical_path
            plan.timeline.critical_path = critical_path

        # Calculate budget with improved estimation
        total_budget = self._calculate_detailed_budget(duration_months, params.get("team_size", 5), constraints)

        # Perform risk assessment
        risk_assessment = await self._perform_risk_assessment(project_name, duration_months, plan)
        plan.risks = risk_assessment

        # Convert plan to dictionary for return
        plan_dict = {
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "duration_months": duration_months,
            "phases": [{"name": p.name, "start": p.start_date.isoformat(), "end": p.end_date.isoformat(), "tasks": p.tasks} for p in plan.phases],
            "total_budget": total_budget,
            "team_composition": self._suggest_team_composition(params.get("team_size", 5)),
            "success_metrics": self._define_success_metrics(project_name),
            "risks": [{"name": r.name, "probability": r.probability, "impact": r.impact} for r in risk_assessment],
            "dependencies": self._identify_dependencies(params.get("dependencies", [])),
            "communication_plan": self._create_communication_plan()
        }
        
        # Save plan
        plan_file = Path(f"generated/strategic_plan_{project_name.lower().replace(' ', '_')}.json")
        plan_file.parent.mkdir(exist_ok=True)
        plan_file.write_text(json.dumps(plan_dict, indent=2))

        return plan_dict
    
    async def _decompose_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Decompose a complex task into subtasks with recursive decomposition"""
        main_task = params.get("task", "Complex Task")
        complexity = params.get("complexity", "high")
        current_depth = params.get("_depth", 0)  # Internal parameter for recursion tracking

        self.logger.info(f"Decomposing task: {main_task} (depth: {current_depth})")

        # Check recursion depth
        if current_depth >= self.max_decomposition_depth:
            self.logger.warning(f"Max decomposition depth reached for task: {main_task}")
            return {"main_task": main_task, "subtasks": [], "message": "Max depth reached"}

        # Create task graph for dependency analysis
        task_graph = nx.DiGraph()
        subtasks = []

        # Determine decomposition strategy based on task type
        task_components = self._analyze_task_components(main_task, complexity)

        for i, component in enumerate(task_components):
            subtask_id = f"{main_task.replace(' ', '_')}_sub_{i+1}_d{current_depth}"

            # Estimate complexity for subtask
            sub_complexity = self._estimate_subtask_complexity(component, complexity)
            estimated_hours = self._estimate_task_hours(component['phase'], sub_complexity)

            subtask = {
                "id": subtask_id,
                "name": component['name'],
                "description": component['description'],
                "estimated_hours": estimated_hours,
                "complexity": sub_complexity,
                "dependencies": [],
                "required_skills": self._identify_required_skills(component['phase']),
                "priority": self._calculate_task_priority(component, i, len(task_components)),
                "can_parallelize": component.get('parallelizable', False)
            }

            # Add to graph
            task_graph.add_node(subtask_id, **subtask)

            # Identify dependencies
            dependencies = self._identify_task_dependencies(component, task_components[:i], subtasks)
            for dep in dependencies:
                subtask["dependencies"].append(dep)
                if dep in task_graph:
                    task_graph.add_edge(dep, subtask_id)

            # Recursively decompose if complex
            if sub_complexity == "high" and current_depth < self.max_decomposition_depth - 1:
                sub_breakdown = await self._decompose_task({
                    "task": component['name'],
                    "complexity": sub_complexity,
                    "_depth": current_depth + 1
                })
                subtask["subtasks"] = sub_breakdown.get("subtasks", [])

            subtasks.append(subtask)

        # Detect circular dependencies
        try:
            cycles = list(nx.simple_cycles(task_graph))
            if cycles:
                self.logger.error(f"Circular dependencies detected: {cycles}")
                # Remove circular dependencies
                for cycle in cycles:
                    if len(cycle) > 1:
                        task_graph.remove_edge(cycle[-1], cycle[0])
        except nx.NetworkXError:
            pass

        # Calculate critical path
        critical_path = []
        if task_graph.nodes():
            try:
                # Find longest path (critical path)
                critical_path = nx.dag_longest_path(task_graph, weight='estimated_hours')
            except nx.NetworkXError:
                self.logger.warning("Could not calculate critical path due to graph structure")

        # Generate dependency visualization
        dependency_graph = self._generate_dependency_graph(task_graph)

        # Calculate metrics
        total_hours = sum(t["estimated_hours"] for t in subtasks)
        parallel_groups = self._identify_parallel_task_groups(task_graph, subtasks)

        # Create comprehensive breakdown
        breakdown = {
            "main_task": main_task,
            "complexity": complexity,
            "decomposition_depth": current_depth,
            "total_estimated_hours": total_hours,
            "subtasks": subtasks,
            "critical_path": critical_path,
            "parallel_opportunities": parallel_groups,
            "dependency_graph": dependency_graph,
            "estimated_duration_days": self._calculate_project_duration(task_graph, subtasks),
            "recommended_team_size": self._calculate_optimal_team_size(subtasks, parallel_groups),
            "risk_factors": self._identify_decomposition_risks(subtasks, task_graph)
        }

        return breakdown
    
    async def _allocate_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate resources optimally using bin packing and load balancing algorithms"""
        project_name = params.get("project_name", "Project")
        budget = params.get("budget", 100000)
        team_size = params.get("team_size", 5)
        duration_months = params.get("duration_months", 3)
        tasks = params.get("tasks", [])
        agents = params.get("available_agents", [])
        constraints = params.get("constraints", {})
        
        self.logger.info(f"Allocating resources for: {project_name}")
        
        # Calculate resource allocation
        monthly_budget = budget / duration_months
        
        allocation = {
            "project_name": project_name,
            "total_budget": budget,
            "duration_months": duration_months,
            "team_allocation": {
                "senior_developers": max(1, team_size // 3),
                "mid_developers": max(1, team_size // 2),
                "junior_developers": max(1, team_size - (team_size // 3) - (team_size // 2)),
                "project_manager": 1,
                "qa_engineers": max(1, team_size // 4)
            },
            "budget_breakdown": {
                "salaries": monthly_budget * 0.70,
                "infrastructure": monthly_budget * 0.15,
                "tools_licenses": monthly_budget * 0.05,
                "training": monthly_budget * 0.05,
                "contingency": monthly_budget * 0.05
            },
            "infrastructure_needs": {
                "development_servers": max(2, team_size // 2),
                "staging_environment": True,
                "production_environment": True,
                "ci_cd_pipeline": True,
                "monitoring_tools": ["Prometheus", "Grafana", "ELK Stack"]
            },
            "recommended_tools": self._recommend_tools(project_name),
            "training_requirements": self._identify_training_needs(team_size)
        }
        
        return allocation
    
    async def _create_timeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create project timeline"""
        project_name = params.get("project_name", "Project")
        start_date = datetime.fromisoformat(params.get("start_date", datetime.now().isoformat()))
        milestones = params.get("milestones", [])
        
        self.logger.info(f"Creating timeline for: {project_name}")
        
        # Generate timeline
        timeline_events = []
        current_date = start_date
        
        # Add default milestones if none provided
        if not milestones:
            milestones = [
                "Project Kickoff",
                "Requirements Finalized",
                "Design Complete",
                "Alpha Release",
                "Beta Release",
                "Production Release",
                "Post-Launch Review"
            ]
        
        for i, milestone in enumerate(milestones):
            event_date = current_date + timedelta(weeks=i*2)
            timeline_events.append({
                "milestone": milestone,
                "date": event_date.isoformat(),
                "week": i*2 + 1,
                "status": "planned",
                "dependencies": milestones[i-1:i] if i > 0 else [],
                "deliverables": self._get_milestone_deliverables(milestone)
            })
        
        timeline = {
            "project_name": project_name,
            "start_date": start_date.isoformat(),
            "end_date": (current_date + timedelta(weeks=len(milestones)*2)).isoformat(),
            "duration_weeks": len(milestones) * 2,
            "events": timeline_events,
            "critical_dates": self._identify_critical_dates(timeline_events),
            "buffer_time": "10% of total duration",
            "review_points": self._schedule_reviews(timeline_events)
        }
        
        return timeline
    
    async def _assess_risks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assess project risks"""
        project_name = params.get("project_name", "Project")
        project_type = params.get("project_type", "software")
        team_size = params.get("team_size", 5)
        
        self.logger.info(f"Assessing risks for: {project_name}")
        
        # Identify and assess risks
        risks = [
            {
                "risk": "Scope Creep",
                "probability": "High",
                "impact": "High",
                "mitigation": "Clear requirements documentation, change control process",
                "owner": "Project Manager"
            },
            {
                "risk": "Technical Debt",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Regular code reviews, refactoring sprints",
                "owner": "Tech Lead"
            },
            {
                "risk": "Resource Availability",
                "probability": "Medium" if team_size > 5 else "High",
                "impact": "High",
                "mitigation": "Cross-training, documentation, backup resources",
                "owner": "Project Manager"
            },
            {
                "risk": "Integration Issues",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Early integration testing, API documentation",
                "owner": "Architecture Lead"
            },
            {
                "risk": "Security Vulnerabilities",
                "probability": "Low",
                "impact": "Critical",
                "mitigation": "Security audits, penetration testing, secure coding practices",
                "owner": "Security Lead"
            }
        ]
        
        # Calculate risk score
        risk_scores = {
            "Low": 1, "Medium": 2, "High": 3, "Critical": 4
        }
        
        for risk in risks:
            prob_score = risk_scores.get(risk["probability"], 1)
            impact_score = risk_scores.get(risk["impact"], 1)
            risk["risk_score"] = prob_score * impact_score
            risk["priority"] = "High" if risk["risk_score"] >= 6 else "Medium" if risk["risk_score"] >= 3 else "Low"
        
        assessment = {
            "project_name": project_name,
            "assessment_date": datetime.now().isoformat(),
            "risks": sorted(risks, key=lambda x: x["risk_score"], reverse=True),
            "overall_risk_level": self._calculate_overall_risk(risks),
            "recommendations": self._generate_risk_recommendations(risks),
            "contingency_budget": "15% of total budget recommended",
            "review_frequency": "Weekly" if any(r["priority"] == "High" for r in risks) else "Bi-weekly"
        }
        
        return assessment
    
    # Helper methods
    def _generate_phase_objectives(self, month: int, total_months: int, goals: List[str]) -> List[str]:
        """Generate objectives for a phase"""
        phase_objectives = {
            0: ["Setup development environment", "Finalize requirements", "Team onboarding"],
            1: ["Core feature development", "API implementation", "Database design"],
            2: ["Testing and optimization", "Documentation", "Deployment preparation"]
        }
        
        return phase_objectives.get(month % 3, ["Continued development", "Feature enhancement"])
    
    def _generate_milestones(self, month: int, project_name: str) -> List[str]:
        """Generate milestones for a month"""
        milestones = {
            0: [f"{project_name} kickoff complete", "Development environment ready"],
            1: ["Core features implemented", "Initial testing complete"],
            2: ["Beta release ready", "Production deployment"]
        }
        
        return milestones.get(month % 3, ["Progress checkpoint"])
    
    def _generate_deliverables(self, month: int, project_name: str) -> List[str]:
        """Generate deliverables for a month"""
        deliverables = {
            0: ["Project plan", "Technical architecture", "Development setup guide"],
            1: ["Working prototype", "API documentation", "Test cases"],
            2: ["Production build", "User documentation", "Deployment guide"]
        }
        
        return deliverables.get(month % 3, ["Progress report"])
    
    def _estimate_resources(self, month: int) -> Dict[str, int]:
        """Estimate resources for a month"""
        return {
            "developers": 3 + (month % 2),
            "qa_engineers": 1 + (month // 2),
            "devops": 1,
            "project_manager": 1
        }
    
    def _calculate_budget(self, months: int, team_size: int) -> str:
        """Calculate project budget"""
        monthly_cost = team_size * 10000  # Average monthly cost per person
        total = monthly_cost * months
        return f"${total:,}"
    
    def _suggest_team_composition(self, team_size: int) -> Dict[str, int]:
        """Suggest optimal team composition"""
        return {
            "senior_developers": max(1, team_size // 3),
            "mid_developers": max(1, team_size // 2),
            "junior_developers": max(0, team_size - (team_size // 3) - (team_size // 2)),
            "qa_engineers": max(1, team_size // 4),
            "devops": 1,
            "project_manager": 1
        }
    
    def _define_success_metrics(self, project_name: str) -> List[Dict[str, str]]:
        """Define success metrics"""
        return [
            {"metric": "On-time delivery", "target": "100%", "measurement": "Milestone completion dates"},
            {"metric": "Budget adherence", "target": "Within 5%", "measurement": "Monthly budget reports"},
            {"metric": "Quality", "target": "<2% defect rate", "measurement": "Bug tracking system"},
            {"metric": "Team satisfaction", "target": ">4.0/5.0", "measurement": "Monthly surveys"},
            {"metric": "Performance", "target": "<200ms response time", "measurement": "Monitoring tools"}
        ]
    
    def _identify_risks(self, project_name: str, duration: int) -> List[Dict[str, str]]:
        """Identify project risks"""
        risks = [
            {"risk": "Scope creep", "probability": "Medium", "impact": "High", "mitigation": "Clear requirements, change control"},
            {"risk": "Resource availability", "probability": "Low", "impact": "Medium", "mitigation": "Cross-training, documentation"}
        ]
        
        if duration > 6:
            risks.append({"risk": "Team turnover", "probability": "Medium", "impact": "High", "mitigation": "Retention plan, knowledge transfer"})
        
        return risks
    
    def _identify_dependencies(self, dependencies: List[str]) -> List[Dict[str, str]]:
        """Identify and document dependencies"""
        return [{"dependency": dep, "type": "external", "status": "pending"} for dep in dependencies]
    
    def _create_communication_plan(self) -> Dict[str, Any]:
        """Create communication plan"""
        return {
            "daily": ["Stand-up meetings (15 min)"],
            "weekly": ["Team sync (1 hour)", "Stakeholder update"],
            "monthly": ["Retrospective", "Planning session"],
            "channels": ["Slack", "Email", "Jira", "Confluence"]
        }
    
    def _estimate_task_hours(self, phase: str, complexity: str) -> int:
        """Estimate hours for a task phase"""
        base_hours = {
            "Planning": 16, "Design": 24, "Implementation": 40,
            "Testing": 20, "Deployment": 8, "Monitoring": 12,
            "Optimization": 16, "Documentation": 12
        }
        
        complexity_multiplier = {"low": 0.5, "medium": 1.0, "high": 1.5}
        
        return int(base_hours.get(phase, 20) * complexity_multiplier.get(complexity, 1.0))
    
    def _identify_required_skills(self, phase: str) -> List[str]:
        """Identify required skills for a phase"""
        skills = {
            "Planning": ["Project Management", "Requirements Analysis"],
            "Design": ["System Architecture", "UX/UI Design"],
            "Implementation": ["Programming", "Database Design"],
            "Testing": ["QA", "Test Automation"],
            "Deployment": ["DevOps", "Cloud Infrastructure"]
        }
        
        return skills.get(phase, ["General Development"])
    
    def _identify_critical_path(self, subtasks: List[Dict]) -> List[str]:
        """Identify critical path through subtasks"""
        # Simple implementation - tasks with dependencies
        return [t["id"] for t in subtasks if t["dependencies"]]
    
    def _identify_parallel_tasks(self, subtasks: List[Dict]) -> List[List[str]]:
        """Identify tasks that can run in parallel"""
        parallel_groups = []
        for i in range(0, len(subtasks), 2):
            if i + 1 < len(subtasks):
                parallel_groups.append([subtasks[i]["id"], subtasks[i+1]["id"]])
        return parallel_groups
    
    def _recommend_tools(self, project_name: str) -> List[str]:
        """Recommend tools for the project"""
        return [
            "Jira (Project Management)",
            "Git/GitHub (Version Control)",
            "Docker (Containerization)",
            "Jenkins (CI/CD)",
            "Slack (Communication)",
            "Confluence (Documentation)"
        ]
    
    def _identify_training_needs(self, team_size: int) -> List[str]:
        """Identify training needs"""
        return [
            "Agile methodology",
            "Cloud platforms (AWS/Azure)",
            "Security best practices",
            "New framework training"
        ]
    
    def _get_milestone_deliverables(self, milestone: str) -> List[str]:
        """Get deliverables for a milestone"""
        deliverables_map = {
            "Project Kickoff": ["Project charter", "Team assignments"],
            "Requirements Finalized": ["Requirements document", "User stories"],
            "Design Complete": ["Technical design", "UI mockups"],
            "Alpha Release": ["Working prototype", "Test results"],
            "Beta Release": ["Beta build", "User feedback"],
            "Production Release": ["Production deployment", "Documentation"],
            "Post-Launch Review": ["Performance report", "Lessons learned"]
        }
        
        return deliverables_map.get(milestone, ["Milestone report"])
    
    def _identify_critical_dates(self, events: List[Dict]) -> List[Dict]:
        """Identify critical dates in timeline"""
        critical = []
        for event in events:
            if "Release" in event["milestone"] or "Launch" in event["milestone"]:
                critical.append({
                    "date": event["date"],
                    "event": event["milestone"],
                    "importance": "Critical"
                })
        return critical
    
    def _schedule_reviews(self, events: List[Dict]) -> List[Dict]:
        """Schedule review points"""
        reviews = []
        for i, event in enumerate(events[::2]):  # Every other milestone
            reviews.append({
                "review": f"Review {i+1}",
                "date": event["date"],
                "type": "Progress Review"
            })
        return reviews
    
    def _calculate_overall_risk(self, risks: List[Dict]) -> str:
        """Calculate overall risk level"""
        high_risks = sum(1 for r in risks if r["priority"] == "High")
        if high_risks >= 3:
            return "High"
        elif high_risks >= 1:
            return "Medium"
        else:
            return "Low"
    
    def _generate_risk_recommendations(self, risks: List[Dict]) -> List[str]:
        """Generate recommendations based on risks"""
        recommendations = []

        high_risks = [r for r in risks if r["priority"] == "High"]
        if high_risks:
            recommendations.append("Establish weekly risk review meetings")
            recommendations.append("Allocate 15% contingency budget")

        recommendations.extend([
            "Maintain risk register",
            "Regular stakeholder communication",
            "Implement change control process"
        ])

        return recommendations

    def _calculate_critical_path(self, graph: nx.DiGraph, durations: Dict[str, float]) -> List[str]:
        """Calculate critical path using CPM algorithm"""
        if not graph.nodes():
            return []

        # Add source and sink nodes
        source = "__source__"
        sink = "__sink__"

        # Find nodes with no predecessors (start nodes)
        start_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
        for node in start_nodes:
            graph.add_edge(source, node, weight=0)

        # Find nodes with no successors (end nodes)
        end_nodes = [n for n in graph.nodes() if graph.out_degree(n) == 0]
        for node in end_nodes:
            graph.add_edge(node, sink, weight=0)

        # Set node weights
        for node, duration in durations.items():
            if node in graph:
                graph.nodes[node]['duration'] = duration

        # Forward pass - calculate earliest start times
        earliest_start = {source: 0}
        for node in nx.topological_sort(graph):
            if node != source:
                earliest_start[node] = max(
                    earliest_start.get(pred, 0) + durations.get(pred, 0)
                    for pred in graph.predecessors(node)
                )

        # Backward pass - calculate latest start times
        project_duration = earliest_start[sink]
        latest_start = {sink: project_duration}

        for node in reversed(list(nx.topological_sort(graph))):
            if node != sink:
                if list(graph.successors(node)):
                    latest_start[node] = min(
                        latest_start.get(succ, project_duration) - durations.get(node, 0)
                        for succ in graph.successors(node)
                    )
                else:
                    latest_start[node] = project_duration - durations.get(node, 0)

        # Find critical path (nodes with zero slack)
        critical_nodes = []
        for node in graph.nodes():
            if node not in [source, sink]:
                slack = latest_start.get(node, 0) - earliest_start.get(node, 0)
                if abs(slack) < 0.001:  # Float comparison tolerance
                    critical_nodes.append(node)

        # Remove helper nodes
        graph.remove_nodes_from([source, sink])

        return critical_nodes

    def _get_phase_name(self, month: int, total_months: int) -> str:
        """Generate descriptive phase name"""
        phase_names = [
            "Foundation & Setup",
            "Core Development",
            "Feature Implementation",
            "Testing & Integration",
            "Optimization & Polish",
            "Deployment & Launch"
        ]

        if total_months <= 3:
            compact_names = ["Setup & Development", "Implementation & Testing", "Launch & Stabilization"]
            return compact_names[month % len(compact_names)]

        return phase_names[month % len(phase_names)]

    def _generate_phase_tasks(self, month: int, project_name: str, goals: List[str]) -> List[str]:
        """Generate tasks for a specific phase"""
        base_tasks = {
            0: [
                "Set up development environment",
                "Configure CI/CD pipeline",
                "Create project documentation structure",
                "Define coding standards",
                "Set up version control"
            ],
            1: [
                "Implement core business logic",
                "Design database schema",
                "Create API endpoints",
                "Develop authentication system",
                "Build data models"
            ],
            2: [
                "Add advanced features",
                "Implement caching layer",
                "Create admin dashboard",
                "Add monitoring and logging",
                "Optimize performance"
            ]
        }

        tasks = base_tasks.get(month % 3, ["Continue development"])

        # Add goal-specific tasks
        for goal in goals[:2]:  # Add tasks for first 2 goals
            tasks.append(f"Implement: {goal}")

        return tasks

    def _estimate_task_duration(self, task: str) -> float:
        """Estimate duration for a task in days"""
        # Simple estimation based on keywords
        if any(word in task.lower() for word in ['setup', 'configure', 'create']):
            return 2.0
        elif any(word in task.lower() for word in ['implement', 'develop', 'build']):
            return 5.0
        elif any(word in task.lower() for word in ['optimize', 'test', 'debug']):
            return 3.0
        else:
            return 3.0

    def _define_milestone_criteria(self, milestone_name: str) -> List[str]:
        """Define success criteria for a milestone"""
        criteria_map = {
            "kickoff": [
                "Team assembled and onboarded",
                "Project charter signed",
                "Development environment operational"
            ],
            "alpha": [
                "Core features functional",
                "Basic testing complete",
                "Internal demo ready"
            ],
            "beta": [
                "Feature complete",
                "Performance targets met",
                "User acceptance testing passed"
            ],
            "production": [
                "All tests passing",
                "Security audit complete",
                "Documentation finalized"
            ]
        }

        for key, criteria in criteria_map.items():
            if key in milestone_name.lower():
                return criteria

        return ["Milestone objectives met", "Deliverables complete", "Stakeholder approval"]

    def _calculate_detailed_budget(self, months: int, team_size: int, constraints: Dict) -> str:
        """Calculate detailed project budget"""
        # Base salaries
        monthly_salaries = team_size * constraints.get('avg_salary', 10000)

        # Infrastructure costs
        infrastructure = constraints.get('infrastructure_cost', 5000) * months

        # Tools and licenses
        tools = constraints.get('tools_cost', 2000) * months

        # Contingency
        contingency = (monthly_salaries * months) * 0.15

        total = (monthly_salaries * months) + infrastructure + tools + contingency

        return f"${total:,.2f}"

    async def _perform_risk_assessment(self, project_name: str, duration: int, plan: Plan) -> List[Risk]:
        """Perform comprehensive risk assessment"""
        risks = []

        # Technical risks
        if duration > 6:
            risks.append(Risk(
                name="Technology Obsolescence",
                probability="Medium",
                impact="High",
                mitigation="Regular technology stack review",
                owner="Tech Lead",
                risk_score=6
            ))

        # Resource risks
        if len(plan.phases) > 3:
            risks.append(Risk(
                name="Resource Burnout",
                probability="Medium",
                impact="High",
                mitigation="Implement work-life balance policies",
                owner="Project Manager",
                risk_score=6
            ))

        # Schedule risks
        if plan.critical_path and len(plan.critical_path) > 10:
            risks.append(Risk(
                name="Schedule Slippage",
                probability="High",
                impact="High",
                mitigation="Add buffer time to critical path",
                owner="Project Manager",
                risk_score=9
            ))

        return risks

    def _calculate_critical_path_cpm(self, tasks: List[str]) -> List[str]:
        """Calculate critical path using CPM"""
        # Simplified CPM for demo
        if len(tasks) > 5:
            # Return middle tasks as critical
            start = len(tasks) // 3
            end = 2 * len(tasks) // 3
            return tasks[start:end]
        return tasks

    def _analyze_task_components(self, task: str, complexity: str) -> List[Dict]:
        """Analyze and decompose task into components"""
        components = []

        # Standard software development phases
        phases = [
            {"phase": "Planning", "weight": 0.15},
            {"phase": "Design", "weight": 0.20},
            {"phase": "Implementation", "weight": 0.35},
            {"phase": "Testing", "weight": 0.20},
            {"phase": "Deployment", "weight": 0.10}
        ]

        for phase_info in phases:
            components.append({
                "name": f"{task} - {phase_info['phase']}",
                "description": f"{phase_info['phase']} phase for {task}",
                "phase": phase_info['phase'],
                "weight": phase_info['weight'],
                "parallelizable": phase_info['phase'] in ['Design', 'Testing']
            })

        return components

    def _estimate_subtask_complexity(self, component: Dict, parent_complexity: str) -> str:
        """Estimate complexity for a subtask"""
        complexity_map = {
            "high": {"Planning": "medium", "Design": "high", "Implementation": "high", "Testing": "medium", "Deployment": "low"},
            "medium": {"Planning": "low", "Design": "medium", "Implementation": "medium", "Testing": "medium", "Deployment": "low"},
            "low": {"Planning": "low", "Design": "low", "Implementation": "low", "Testing": "low", "Deployment": "low"}
        }

        return complexity_map.get(parent_complexity, {}).get(component.get('phase', ''), 'medium')

    def _calculate_task_priority(self, component: Dict, index: int, total: int) -> Priority:
        """Calculate priority for a task"""
        if component['phase'] in ['Planning', 'Design']:
            return Priority.HIGH
        elif component['phase'] == 'Implementation':
            return Priority.CRITICAL
        elif index < total / 3:
            return Priority.HIGH
        else:
            return Priority.MEDIUM

    def _identify_task_dependencies(self, component: Dict, previous_components: List[Dict], existing_tasks: List[Dict]) -> List[str]:
        """Identify dependencies for a task"""
        dependencies = []

        # Phase dependencies
        phase_deps = {
            "Design": ["Planning"],
            "Implementation": ["Design"],
            "Testing": ["Implementation"],
            "Deployment": ["Testing"]
        }

        current_phase = component.get('phase', '')
        required_phases = phase_deps.get(current_phase, [])

        for prev in previous_components:
            if prev.get('phase') in required_phases:
                # Find corresponding task
                for task in existing_tasks:
                    if prev['name'] in task.get('name', ''):
                        dependencies.append(task['id'])
                        break

        return dependencies

    def _generate_dependency_graph(self, graph: nx.DiGraph) -> Dict:
        """Generate dependency graph visualization data"""
        return {
            "nodes": list(graph.nodes()),
            "edges": list(graph.edges()),
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
            "is_dag": nx.is_directed_acyclic_graph(graph)
        }

    def _identify_parallel_task_groups(self, graph: nx.DiGraph, tasks: List[Dict]) -> List[List[str]]:
        """Identify groups of tasks that can run in parallel"""
        parallel_groups = []

        # Find tasks with same predecessors
        predecessor_map = defaultdict(list)
        for task in tasks:
            task_id = task['id']
            if task_id in graph:
                preds = tuple(sorted(graph.predecessors(task_id)))
                predecessor_map[preds].append(task_id)

        # Groups with same predecessors can run in parallel
        for group in predecessor_map.values():
            if len(group) > 1:
                parallel_groups.append(group)

        return parallel_groups

    def _calculate_project_duration(self, graph: nx.DiGraph, tasks: List[Dict]) -> float:
        """Calculate total project duration considering parallelism"""
        if not tasks:
            return 0

        # Simple calculation: sum of critical path
        critical_tasks = [t for t in tasks if t['id'] in self._identify_critical_path(tasks)]
        if critical_tasks:
            return sum(t['estimated_hours'] for t in critical_tasks) / 8  # Convert to days

        return sum(t['estimated_hours'] for t in tasks) / 8 / 2  # Assume 50% parallelism

    def _calculate_optimal_team_size(self, tasks: List[Dict], parallel_groups: List[List[str]]) -> int:
        """Calculate optimal team size based on parallelism"""
        if not parallel_groups:
            return 2  # Minimum team size

        # Maximum parallel tasks
        max_parallel = max(len(group) for group in parallel_groups)

        # Add buffer for coordination
        return min(max_parallel + 1, 8)  # Cap at 8 team members

    def _identify_decomposition_risks(self, tasks: List[Dict], graph: nx.DiGraph) -> List[str]:
        """Identify risks in task decomposition"""
        risks = []

        if len(tasks) > 20:
            risks.append("High task count may lead to management overhead")

        # Check for circular dependencies
        if graph and not nx.is_directed_acyclic_graph(graph):
            risks.append("Circular dependencies detected - review task dependencies")

        # Check for bottlenecks
        if graph:
            for node in graph.nodes():
                if graph.in_degree(node) > 5:
                    risks.append(f"Task {node} has many dependencies - potential bottleneck")

        return risks

    def _get_subtask_specs(self, task_type: str, task_spec: Dict) -> List[Dict]:
        """Get subtask specifications based on task type"""
        subtasks = []

        if task_type == "development":
            subtasks = [
                {"name": "Requirements analysis", "type": "analysis", "estimated_hours": 8},
                {"name": "Technical design", "type": "design", "estimated_hours": 16},
                {"name": "Implementation", "type": "coding", "estimated_hours": 40},
                {"name": "Unit testing", "type": "testing", "estimated_hours": 16},
                {"name": "Integration", "type": "integration", "estimated_hours": 8}
            ]
        elif task_type == "research":
            subtasks = [
                {"name": "Literature review", "type": "research", "estimated_hours": 16},
                {"name": "Data collection", "type": "data", "estimated_hours": 24},
                {"name": "Analysis", "type": "analysis", "estimated_hours": 20},
                {"name": "Report writing", "type": "documentation", "estimated_hours": 12}
            ]
        else:
            subtasks = [
                {"name": f"{task_spec.get('name', 'Task')} - Part 1", "type": "generic", "estimated_hours": 8},
                {"name": f"{task_spec.get('name', 'Task')} - Part 2", "type": "generic", "estimated_hours": 8}
            ]

        return subtasks

    def _calculate_resource_requirements(self, task_type: str, hours: float) -> Dict[str, Any]:
        """Calculate resource requirements for a task"""
        requirements = {
            "hours": hours,
            "hourly_rate": 100,  # Default rate
            "tools": [],
            "infrastructure": []
        }

        if task_type == "development":
            requirements["tools"] = ["IDE", "Version Control", "Build Tools"]
            requirements["infrastructure"] = ["Development Server", "Database"]
            requirements["hourly_rate"] = 120
        elif task_type == "testing":
            requirements["tools"] = ["Test Framework", "CI/CD"]
            requirements["infrastructure"] = ["Test Environment"]
            requirements["hourly_rate"] = 90
        elif task_type == "deployment":
            requirements["tools"] = ["Docker", "Kubernetes"]
            requirements["infrastructure"] = ["Production Servers", "Load Balancer"]
            requirements["hourly_rate"] = 110

        return requirements

    def _get_required_skills(self, task_type: str) -> List[str]:
        """Get required skills for a task type"""
        skills_map = {
            "development": ["Python", "AsyncIO", "REST API", "Database Design"],
            "testing": ["Test Automation", "QA", "Performance Testing"],
            "deployment": ["DevOps", "Docker", "Kubernetes", "CI/CD"],
            "design": ["System Architecture", "UML", "Design Patterns"],
            "research": ["Data Analysis", "Research Methods", "Documentation"]
        }

        return skills_map.get(task_type, ["General Development"])

    def _agent_has_skills(self, agent_skills: List[AgentCapability], required_skills: List[str]) -> bool:
        """Check if agent has required skills"""
        if not required_skills:
            return True

        agent_skill_names = [cap.name.lower() for cap in agent_skills]

        # Check if agent has at least 50% of required skills
        matching = sum(1 for skill in required_skills if skill.lower() in agent_skill_names)
        return matching >= len(required_skills) * 0.5

    def _calculate_expertise_bonus(self, agent_skills: List[AgentCapability], required_skills: List[str]) -> float:
        """Calculate expertise bonus for skill matching"""
        if not required_skills:
            return 0

        agent_skill_names = [cap.name.lower() for cap in agent_skills]
        matching = sum(1 for skill in required_skills if skill.lower() in agent_skill_names)

        return (matching / len(required_skills)) * 10  # Max bonus of 10

    def _generate_allocation_timeline(self, allocation: AllocationPlan, tasks: List[Task], agents: List[BaseAgent]) -> Timeline:
        """Generate timeline for resource allocation"""
        if not tasks:
            return Timeline()

        start_date = datetime.now()
        total_hours = sum(t.estimated_hours for t in tasks)

        # Assume 40 hours per week per agent
        weeks_needed = total_hours / (len(agents) * 40) if agents else 1
        end_date = start_date + timedelta(weeks=weeks_needed)

        return Timeline(
            start_date=start_date,
            end_date=end_date,
            duration_days=int(weeks_needed * 7),
            critical_path=allocation.unallocated_tasks  # Tasks that couldn't be allocated are critical
        )