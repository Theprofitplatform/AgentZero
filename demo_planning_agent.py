#!/usr/bin/env python3
"""
Demo script for Planning Agent
Shows advanced planning capabilities including CPM, decomposition, and resource allocation
"""

import asyncio
import json
from datetime import datetime
import sys
sys.path.append('/mnt/c/Users/abhis/projects/AgentZero')

from src.agents.planning_agent import PlanningAgent
from src.core.agent import Task, Priority


async def demo_strategic_planning():
    """Demo strategic planning capability"""
    print("\n" + "="*60)
    print("DEMO: Strategic Planning with CPM Analysis")
    print("="*60)

    # Initialize Planning Agent
    agent = PlanningAgent(
        agent_id="planner-001",
        name="Strategic Planner",
        config={
            "planning_horizon": 90,
            "max_parallel_tasks": 10,
            "max_decomposition_depth": 5
        }
    )

    # Create a strategic planning request
    params = {
        "project_name": "E-Commerce Platform",
        "duration_months": 3,
        "goals": [
            "Build user authentication system",
            "Implement product catalog",
            "Create shopping cart functionality",
            "Setup payment processing",
            "Deploy to production"
        ],
        "constraints": {
            "budget": 250000,
            "team_size": 8,
            "avg_salary": 12000,
            "infrastructure_cost": 5000,
            "tools_cost": 2000
        },
        "team_size": 8
    }

    print(f"\nProject: {params['project_name']}")
    print(f"Duration: {params['duration_months']} months")
    print(f"Budget: ${params['constraints']['budget']:,}")
    print(f"Team Size: {params['team_size']}")

    # Generate strategic plan
    plan = await agent._create_strategic_plan(params)

    print("\n✅ Strategic Plan Generated!")
    print(f"- Total Phases: {len(plan['phases'])}")
    print(f"- Total Budget: {plan['total_budget']}")
    print(f"- Success Metrics: {len(plan['success_metrics'])}")
    print(f"- Risk Items: {len(plan['risks'])}")

    # Show phases
    print("\n📅 Project Phases:")
    for phase in plan['phases']:
        print(f"  • {phase['name']}")
        print(f"    - Start: {phase['start'][:10]}")
        print(f"    - End: {phase['end'][:10]}")
        print(f"    - Tasks: {len(phase['tasks'])}")

    # Show team composition
    print("\n👥 Recommended Team Composition:")
    for role, count in plan['team_composition'].items():
        if count > 0:
            print(f"  • {role.replace('_', ' ').title()}: {count}")

    return plan


async def demo_task_decomposition():
    """Demo recursive task decomposition"""
    print("\n" + "="*60)
    print("DEMO: Recursive Task Decomposition")
    print("="*60)

    agent = PlanningAgent(
        agent_id="decomposer-001",
        name="Task Decomposer"
    )

    # Complex task to decompose
    params = {
        "task": "Build Real-time Chat System",
        "complexity": "high"
    }

    print(f"\nMain Task: {params['task']}")
    print(f"Complexity: {params['complexity']}")

    # Perform decomposition
    breakdown = await agent._decompose_task(params)

    print("\n✅ Task Decomposition Complete!")
    print(f"- Subtasks Generated: {len(breakdown['subtasks'])}")
    print(f"- Total Estimated Hours: {breakdown['total_estimated_hours']}")
    print(f"- Estimated Duration: {breakdown['estimated_duration_days']} days")
    print(f"- Recommended Team Size: {breakdown['recommended_team_size']}")

    # Show subtasks
    print("\n📋 Subtask Breakdown:")
    for i, subtask in enumerate(breakdown['subtasks'], 1):
        print(f"  {i}. {subtask['name']}")
        print(f"     - Hours: {subtask['estimated_hours']}")
        print(f"     - Complexity: {subtask['complexity']}")
        print(f"     - Priority: {subtask['priority']}")
        if subtask['dependencies']:
            print(f"     - Dependencies: {', '.join(subtask['dependencies'])}")

    # Show critical path
    if breakdown['critical_path']:
        print(f"\n🎯 Critical Path: {' → '.join(breakdown['critical_path'][:3])}...")

    # Show parallel opportunities
    if breakdown['parallel_opportunities']:
        print("\n⚡ Parallel Execution Opportunities:")
        for group in breakdown['parallel_opportunities'][:3]:
            print(f"  • {', '.join(group)}")

    return breakdown


async def demo_resource_allocation():
    """Demo resource allocation"""
    print("\n" + "="*60)
    print("DEMO: Resource Allocation & Budget Planning")
    print("="*60)

    agent = PlanningAgent(
        agent_id="allocator-001",
        name="Resource Allocator"
    )

    params = {
        "project_name": "Mobile App Development",
        "budget": 180000,
        "team_size": 6,
        "duration_months": 4
    }

    print(f"\nProject: {params['project_name']}")
    print(f"Budget: ${params['budget']:,}")
    print(f"Duration: {params['duration_months']} months")
    print(f"Team Size: {params['team_size']}")

    # Perform allocation
    allocation = await agent._allocate_resources(params)

    print("\n✅ Resource Allocation Complete!")

    # Show team allocation
    print("\n👥 Team Allocation:")
    for role, count in allocation['team_allocation'].items():
        if count > 0:
            print(f"  • {role.replace('_', ' ').title()}: {count}")

    # Show budget breakdown
    print("\n💰 Monthly Budget Breakdown:")
    monthly_total = 0
    for category, amount in allocation['budget_breakdown'].items():
        print(f"  • {category.replace('_', ' ').title()}: ${amount:,.2f}")
        monthly_total += amount
    print(f"  ──────────────────")
    print(f"  Total/Month: ${monthly_total:,.2f}")

    # Show infrastructure needs
    print("\n🏗️ Infrastructure Requirements:")
    infra = allocation['infrastructure_needs']
    print(f"  • Development Servers: {infra['development_servers']}")
    print(f"  • Staging Environment: {'Yes' if infra['staging_environment'] else 'No'}")
    print(f"  • Production Environment: {'Yes' if infra['production_environment'] else 'No'}")
    print(f"  • CI/CD Pipeline: {'Yes' if infra['ci_cd_pipeline'] else 'No'}")

    # Show recommended tools
    print("\n🛠️ Recommended Tools:")
    for tool in allocation['recommended_tools'][:5]:
        print(f"  • {tool}")

    return allocation


async def demo_risk_assessment():
    """Demo risk assessment"""
    print("\n" + "="*60)
    print("DEMO: Risk Assessment & Mitigation")
    print("="*60)

    agent = PlanningAgent(
        agent_id="risk-assessor-001",
        name="Risk Assessor"
    )

    params = {
        "project_name": "Blockchain Integration",
        "project_type": "software",
        "team_size": 4
    }

    print(f"\nProject: {params['project_name']}")
    print(f"Type: {params['project_type']}")
    print(f"Team Size: {params['team_size']}")

    # Perform assessment
    assessment = await agent._assess_risks(params)

    print("\n✅ Risk Assessment Complete!")
    print(f"Overall Risk Level: {assessment['overall_risk_level']}")

    # Show top risks
    print("\n⚠️ Top Project Risks:")
    for risk in assessment['risks'][:5]:
        print(f"\n  📌 {risk['risk']}")
        print(f"     Probability: {risk['probability']}")
        print(f"     Impact: {risk['impact']}")
        print(f"     Score: {risk['risk_score']}")
        print(f"     Priority: {risk['priority']}")
        print(f"     Mitigation: {risk['mitigation']}")
        print(f"     Owner: {risk['owner']}")

    # Show recommendations
    print("\n💡 Recommendations:")
    for rec in assessment['recommendations']:
        print(f"  • {rec}")

    print(f"\n📊 Review Frequency: {assessment['review_frequency']}")
    print(f"💵 Contingency Budget: {assessment['contingency_budget']}")

    return assessment


async def demo_timeline_creation():
    """Demo timeline creation"""
    print("\n" + "="*60)
    print("DEMO: Project Timeline Generation")
    print("="*60)

    agent = PlanningAgent(
        agent_id="timeline-001",
        name="Timeline Creator"
    )

    params = {
        "project_name": "AI Integration Project",
        "start_date": datetime.now().isoformat(),
        "milestones": [
            "Requirements Analysis Complete",
            "AI Model Selection",
            "Prototype Development",
            "Integration Testing",
            "User Acceptance Testing",
            "Production Deployment"
        ]
    }

    print(f"\nProject: {params['project_name']}")
    print(f"Start Date: {params['start_date'][:10]}")
    print(f"Milestones: {len(params['milestones'])}")

    # Generate timeline
    timeline = await agent._create_timeline(params)

    print("\n✅ Timeline Generated!")
    print(f"Duration: {timeline['duration_weeks']} weeks")
    print(f"End Date: {timeline['end_date'][:10]}")

    # Show timeline events
    print("\n📅 Timeline Events:")
    for event in timeline['events']:
        print(f"\n  🎯 {event['milestone']}")
        print(f"     Date: {event['date'][:10]}")
        print(f"     Week: {event['week']}")
        print(f"     Status: {event['status']}")
        if event['deliverables']:
            print(f"     Deliverables: {', '.join(event['deliverables'][:3])}")

    # Show critical dates
    if timeline['critical_dates']:
        print("\n⚡ Critical Dates:")
        for critical in timeline['critical_dates']:
            print(f"  • {critical['date'][:10]}: {critical['event']} ({critical['importance']})")

    return timeline


async def main():
    """Run all demos"""
    print("\n" + "🚀 "*20)
    print("  AGENTZERO PLANNING AGENT - ADVANCED CAPABILITIES DEMO")
    print("🚀 "*20)

    # Run demos
    await demo_strategic_planning()
    await demo_task_decomposition()
    await demo_resource_allocation()
    await demo_risk_assessment()
    await demo_timeline_creation()

    print("\n" + "="*60)
    print("✨ Demo Complete! Planning Agent is ready for production use.")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())