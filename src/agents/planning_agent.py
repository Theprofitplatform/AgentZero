"""
Planning Agent for AgentZero
Specialized in strategic planning, task decomposition, and resource allocation
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json
from pathlib import Path

import sys
sys.path.append('/home/avi/projects/agentzero')
from src.core.agent import BaseAgent, Task, AgentCapability


class PlanningAgent(BaseAgent):
    """
    Agent specialized in strategic planning and task management
    """
    
    def __init__(self, agent_id: Optional[str] = None, name: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, name or "PlanningAgent", config)
        
        # Planning-specific configuration
        self.planning_horizon = config.get("planning_horizon", 90) if config else 90  # days
        self.max_parallel_tasks = config.get("max_parallel_tasks", 10) if config else 10
        
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
        """Create a strategic plan"""
        project_name = params.get("project_name", "Project")
        duration_months = params.get("duration_months", 3)
        goals = params.get("goals", [])
        
        self.logger.info(f"Creating strategic plan for: {project_name}")
        
        # Generate plan phases
        phases = []
        start_date = datetime.now()
        
        for month in range(duration_months):
            phase_start = start_date + timedelta(days=30 * month)
            phase_end = start_date + timedelta(days=30 * (month + 1))
            
            phase = {
                "phase_number": month + 1,
                "month": phase_start.strftime("%B %Y"),
                "start_date": phase_start.isoformat(),
                "end_date": phase_end.isoformat(),
                "objectives": self._generate_phase_objectives(month, duration_months, goals),
                "milestones": self._generate_milestones(month, project_name),
                "deliverables": self._generate_deliverables(month, project_name),
                "resources_required": self._estimate_resources(month)
            }
            phases.append(phase)
        
        # Calculate budget
        total_budget = self._calculate_budget(duration_months, params.get("team_size", 5))
        
        # Identify risks
        risks = self._identify_risks(project_name, duration_months)
        
        plan = {
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "duration_months": duration_months,
            "phases": phases,
            "total_budget": total_budget,
            "team_composition": self._suggest_team_composition(params.get("team_size", 5)),
            "success_metrics": self._define_success_metrics(project_name),
            "risks": risks,
            "dependencies": self._identify_dependencies(params.get("dependencies", [])),
            "communication_plan": self._create_communication_plan()
        }
        
        # Save plan
        plan_file = Path(f"generated/strategic_plan_{project_name.lower().replace(' ', '_')}.json")
        plan_file.parent.mkdir(exist_ok=True)
        plan_file.write_text(json.dumps(plan, indent=2))
        
        return plan
    
    async def _decompose_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Decompose a complex task into subtasks"""
        main_task = params.get("task", "Complex Task")
        complexity = params.get("complexity", "high")
        
        self.logger.info(f"Decomposing task: {main_task}")
        
        # Generate subtasks based on complexity
        subtasks = []
        
        if complexity == "high":
            num_subtasks = 8
        elif complexity == "medium":
            num_subtasks = 5
        else:
            num_subtasks = 3
        
        # Create logical subtasks
        task_phases = ["Planning", "Design", "Implementation", "Testing", "Deployment", "Monitoring", "Optimization", "Documentation"]
        
        for i in range(min(num_subtasks, len(task_phases))):
            subtask = {
                "id": f"subtask_{i+1}",
                "name": f"{task_phases[i]} - {main_task}",
                "description": f"Complete {task_phases[i].lower()} phase for {main_task}",
                "estimated_hours": self._estimate_task_hours(task_phases[i], complexity),
                "dependencies": [f"subtask_{i}"] if i > 0 else [],
                "required_skills": self._identify_required_skills(task_phases[i]),
                "priority": "high" if i < 3 else "medium"
            }
            subtasks.append(subtask)
        
        # Create task breakdown structure
        breakdown = {
            "main_task": main_task,
            "complexity": complexity,
            "total_estimated_hours": sum(t["estimated_hours"] for t in subtasks),
            "subtasks": subtasks,
            "critical_path": self._identify_critical_path(subtasks),
            "parallel_opportunities": self._identify_parallel_tasks(subtasks),
            "recommended_team_size": max(2, len(subtasks) // 3)
        }
        
        return breakdown
    
    async def _allocate_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate resources for a project"""
        project_name = params.get("project_name", "Project")
        budget = params.get("budget", 100000)
        team_size = params.get("team_size", 5)
        duration_months = params.get("duration_months", 3)
        
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