#!/usr/bin/env python3
"""
Launch Multiple Agent Instances for Parallel Work
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import uuid

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.agent import Task, Priority, BaseAgent
from src.agents.research_agent import ResearchAgent
from src.agents.code_agent import CodeAgent
from src.hive.coordinator import HiveCoordinator, AgentInfo, HiveTask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiAgentLauncher:
    """Launch and manage multiple agent instances"""
    
    def __init__(self):
        self.hive = None
        self.agents = {}
        self.agent_tasks = {}
        self.running = True
        
    async def initialize_hive(self):
        """Initialize the hive coordinator"""
        logger.info("🐝 Initializing Hive Coordinator...")
        self.hive = HiveCoordinator(
            hive_id="multi-agent-hive",
            config={
                "distribution_strategy": "capability_based",
                "persist_state": True
            }
        )
        return self.hive
    
    async def launch_research_agents(self, count: int = 3):
        """Launch multiple research agent instances"""
        logger.info(f"🔍 Launching {count} Research Agent instances...")
        
        research_agents = []
        for i in range(count):
            agent = ResearchAgent(
                name=f"ResearchAgent-{i+1}",
                config={
                    "max_depth": 3,
                    "max_pages": 50,
                    "timeout": 30
                }
            )
            
            # Register with hive
            agent_info = AgentInfo(
                agent_id=agent.agent_id,
                name=agent.name,
                capabilities=["web_search", "extract_content", "analyze_data", "fact_check"],
                status="idle",
                last_heartbeat=datetime.now(),
                max_load=3
            )
            
            await self.hive.register_agent(agent_info, connection=None)
            
            self.agents[agent.agent_id] = agent
            research_agents.append(agent)
            
            # Start agent in background
            task = asyncio.create_task(self._run_agent(agent))
            self.agent_tasks[agent.agent_id] = task
            
            logger.info(f"  ✅ {agent.name} launched (ID: {agent.agent_id[:8]})")
        
        return research_agents
    
    async def launch_code_agents(self, count: int = 3):
        """Launch multiple code agent instances"""
        logger.info(f"💻 Launching {count} Code Agent instances...")
        
        code_agents = []
        for i in range(count):
            agent = CodeAgent(
                name=f"CodeAgent-{i+1}",
                config={
                    "languages": ["python", "javascript", "typescript", "go"],
                }
            )
            
            # Register with hive
            agent_info = AgentInfo(
                agent_id=agent.agent_id,
                name=agent.name,
                capabilities=["generate_code", "analyze_code", "debug_code", "optimize_code", "refactor_code"],
                status="idle",
                last_heartbeat=datetime.now(),
                max_load=3
            )
            
            await self.hive.register_agent(agent_info, connection=None)
            
            self.agents[agent.agent_id] = agent
            code_agents.append(agent)
            
            # Start agent in background
            task = asyncio.create_task(self._run_agent(agent))
            self.agent_tasks[agent.agent_id] = task
            
            logger.info(f"  ✅ {agent.name} launched (ID: {agent.agent_id[:8]})")
        
        return code_agents
    
    async def launch_specialized_agents(self):
        """Launch specialized agent types"""
        logger.info("🚀 Launching Specialized Agents...")
        
        # Planning Agent (simulated)
        planning_agent = type('PlanningAgent', (BaseAgent,), {
            'execute': lambda self, task: self._planning_execute(task),
            '_planning_execute': lambda self, task: {
                "plan": f"Strategic plan for: {task.name}",
                "steps": ["Analysis", "Design", "Implementation", "Testing"],
                "timeline": "2 weeks"
            }
        })(name="PlanningAgent-1")
        
        agent_info = AgentInfo(
            agent_id=planning_agent.agent_id,
            name=planning_agent.name,
            capabilities=["strategic_planning", "task_decomposition", "resource_allocation"],
            status="idle",
            last_heartbeat=datetime.now(),
            max_load=5
        )
        await self.hive.register_agent(agent_info, connection=None)
        self.agents[planning_agent.agent_id] = planning_agent
        
        # Execution Agent (simulated)
        execution_agent = type('ExecutionAgent', (BaseAgent,), {
            'execute': lambda self, task: self._execution_execute(task),
            '_execution_execute': lambda self, task: {
                "status": "executed",
                "task": task.name,
                "result": f"Successfully executed: {task.name}"
            }
        })(name="ExecutionAgent-1")
        
        agent_info = AgentInfo(
            agent_id=execution_agent.agent_id,
            name=execution_agent.name,
            capabilities=["task_execution", "system_operations", "monitoring"],
            status="idle",
            last_heartbeat=datetime.now(),
            max_load=10
        )
        await self.hive.register_agent(agent_info, connection=None)
        self.agents[execution_agent.agent_id] = execution_agent
        
        logger.info(f"  ✅ PlanningAgent-1 launched")
        logger.info(f"  ✅ ExecutionAgent-1 launched")
        
        return [planning_agent, execution_agent]
    
    async def _run_agent(self, agent: BaseAgent):
        """Run agent in background"""
        try:
            # Simulate agent running
            while self.running:
                await asyncio.sleep(1)
                # Agent would process tasks from its queue here
                if agent.task_queue:
                    task = agent.task_queue.pop(0)
                    await agent.process_task(task)
        except Exception as e:
            logger.error(f"Agent {agent.name} error: {e}")
    
    async def submit_parallel_tasks(self):
        """Submit tasks to be processed in parallel"""
        logger.info("\n📋 Submitting Parallel Tasks to Agents...")
        
        tasks = [
            # Research tasks
            {
                "name": "Research AI trends",
                "description": "Research latest AI and ML trends for 2024",
                "capabilities": ["web_search"],
                "priority": 2
            },
            {
                "name": "Analyze competition",
                "description": "Analyze competitor products and strategies",
                "capabilities": ["web_search", "analyze_data"],
                "priority": 2
            },
            
            # Code tasks
            {
                "name": "Generate authentication system",
                "description": "Create JWT-based authentication system",
                "capabilities": ["generate_code"],
                "priority": 1
            },
            {
                "name": "Optimize database queries",
                "description": "Optimize slow SQL queries",
                "capabilities": ["optimize_code"],
                "priority": 2
            },
            {
                "name": "Create microservice",
                "description": "Generate a new microservice for payment processing",
                "capabilities": ["generate_code"],
                "priority": 1
            },
            
            # Planning tasks
            {
                "name": "Project roadmap",
                "description": "Create Q1 2025 project roadmap",
                "capabilities": ["strategic_planning"],
                "priority": 1
            },
            
            # Execution tasks
            {
                "name": "Deploy services",
                "description": "Deploy new services to production",
                "capabilities": ["task_execution"],
                "priority": 3
            }
        ]
        
        submitted_tasks = []
        for task_spec in tasks:
            hive_task = HiveTask(
                task_id=str(uuid.uuid4()),
                name=task_spec["name"],
                description=task_spec["description"],
                required_capabilities=task_spec["capabilities"],
                priority=task_spec["priority"]
            )
            
            task_id = await self.hive.submit_task(hive_task)
            submitted_tasks.append(task_id)
            logger.info(f"  📌 Submitted: {task_spec['name']} (Priority: {task_spec['priority']})")
        
        return submitted_tasks
    
    async def monitor_agents(self, duration: int = 10):
        """Monitor agent activity"""
        logger.info(f"\n📊 Monitoring Agent Activity for {duration} seconds...")
        
        for i in range(duration):
            await asyncio.sleep(1)
            
            if i % 3 == 0:  # Update every 3 seconds
                status = self.hive.get_status()
                active_agents = len([a for a in self.agents.values() if hasattr(a, 'status')])
                
                logger.info(f"  ⚡ Active Agents: {active_agents} | "
                          f"Tasks: Active={status['active_tasks']}, "
                          f"Queued={status['queued_tasks']}, "
                          f"Completed={status['completed_tasks']}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        hive_status = self.hive.get_status() if self.hive else {}
        
        agent_statuses = []
        for agent_id, agent in self.agents.items():
            agent_statuses.append({
                "id": agent_id[:8],
                "name": agent.name,
                "type": agent.__class__.__name__,
                "status": getattr(agent, 'status', 'unknown').value if hasattr(agent, 'status') else 'unknown',
                "tasks_completed": agent.metrics.get("tasks_completed", 0) if hasattr(agent, 'metrics') else 0
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "hive": hive_status,
            "agents": agent_statuses,
            "total_agents": len(self.agents)
        }
    
    async def shutdown(self):
        """Gracefully shutdown all agents"""
        logger.info("\n🛑 Shutting down Multi-Agent System...")
        self.running = False
        
        # Cancel all agent tasks
        for task in self.agent_tasks.values():
            task.cancel()
        
        # Shutdown agents
        for agent in self.agents.values():
            if hasattr(agent, 'shutdown'):
                agent.shutdown()
        
        # Shutdown hive
        if self.hive:
            self.hive.shutdown()
        
        logger.info("✅ System shutdown complete")


async def main():
    """Main entry point"""
    print("=" * 60)
    print("🚀 AGENTZERO MULTI-AGENT SYSTEM LAUNCHER")
    print("=" * 60)
    
    launcher = MultiAgentLauncher()
    
    try:
        # Initialize hive
        await launcher.initialize_hive()
        
        # Launch agents in parallel
        await asyncio.gather(
            launcher.launch_research_agents(3),
            launcher.launch_code_agents(3),
            launcher.launch_specialized_agents()
        )
        
        print("\n" + "=" * 60)
        print("📊 AGENT INSTANCES LAUNCHED:")
        print("=" * 60)
        
        status = launcher.get_system_status()
        print(f"\n🐝 Hive Status:")
        print(f"   Total Agents: {status['total_agents']}")
        
        print(f"\n🤖 Active Agents:")
        for agent in status['agents']:
            print(f"   • {agent['name']} ({agent['type']}) - Status: {agent['status']}")
        
        # Submit parallel tasks
        print("\n" + "=" * 60)
        await launcher.submit_parallel_tasks()
        
        # Monitor for a bit
        await launcher.monitor_agents(5)
        
        # Final status
        print("\n" + "=" * 60)
        print("✅ MULTI-AGENT SYSTEM OPERATIONAL")
        print("=" * 60)
        
        final_status = launcher.get_system_status()
        print(f"\n📈 System Metrics:")
        print(f"   • Active Agents: {final_status['total_agents']}")
        print(f"   • Active Tasks: {final_status['hive'].get('active_tasks', 0)}")
        print(f"   • Queued Tasks: {final_status['hive'].get('queued_tasks', 0)}")
        print(f"   • Completed Tasks: {final_status['hive'].get('completed_tasks', 0)}")
        print(f"   • Hive Efficiency: {final_status['hive'].get('metrics', {}).get('hive_efficiency', 0):.1%}")
        
        print("\n🎯 Agents are now working in parallel on assigned tasks!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Interrupted by user")
    
    finally:
        await launcher.shutdown()


if __name__ == "__main__":
    asyncio.run(main())