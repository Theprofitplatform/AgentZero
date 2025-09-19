#!/usr/bin/env python3
"""
AgentZero Live System - Fully Functional Multi-Agent System
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import uuid

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.core.agent import Task, Priority
from src.agents.research_agent import ResearchAgent
from src.agents.code_agent import CodeAgent
from src.agents.planning_agent import PlanningAgent
from src.agents.execution_agent import ExecutionAgent
from src.hive.coordinator import HiveCoordinator, AgentInfo, HiveTask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agentzero_live.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AgentZeroLive:
    """Live multi-agent system with real task processing"""
    
    def __init__(self):
        self.hive = None
        self.agents = {}
        self.running = True
        self.task_results = {}
        
    async def initialize(self):
        """Initialize the live system"""
        logger.info("🚀 Initializing AgentZero Live System...")
        
        # Create hive coordinator
        self.hive = HiveCoordinator(
            hive_id="agentzero-live",
            config={
                "distribution_strategy": "capability_based",
                "persist_state": True
            }
        )
        
        # Create and register agents
        await self._create_agents()
        
        logger.info("✅ AgentZero Live System initialized with {} agents".format(len(self.agents)))
    
    async def _create_agents(self):
        """Create and register all agent types"""
        
        # Create Research Agents
        for i in range(2):
            agent = ResearchAgent(
                name=f"ResearchAgent-{i+1}",
                config={"max_depth": 3, "max_pages": 50}
            )
            await self._register_agent(agent, ["web_search", "extract_content", "analyze_data", "fact_check"])
            self.agents[agent.agent_id] = agent
        
        # Create Code Agents
        for i in range(2):
            agent = CodeAgent(
                name=f"CodeAgent-{i+1}",
                config={"languages": ["python", "javascript", "typescript"]}
            )
            await self._register_agent(agent, ["generate_code", "analyze_code", "optimize_code", "debug_code"])
            self.agents[agent.agent_id] = agent
        
        # Create Planning Agent
        planning_agent = PlanningAgent(name="PlanningAgent-1")
        await self._register_agent(planning_agent, ["strategic_planning", "task_decomposition", "resource_allocation"])
        self.agents[planning_agent.agent_id] = planning_agent
        
        # Create Execution Agent
        execution_agent = ExecutionAgent(name="ExecutionAgent-1")
        await self._register_agent(execution_agent, ["task_execution", "deployment", "monitoring", "automation"])
        self.agents[execution_agent.agent_id] = execution_agent
    
    async def _register_agent(self, agent, capabilities):
        """Register agent with hive"""
        agent_info = AgentInfo(
            agent_id=agent.agent_id,
            name=agent.name,
            capabilities=capabilities,
            status="idle",
            last_heartbeat=datetime.now(),
            max_load=3
        )
        await self.hive.register_agent(agent_info, connection=None)
    
    async def process_user_request(self, request: str) -> Dict[str, Any]:
        """Process a user request by creating and distributing tasks"""
        logger.info(f"📝 Processing request: {request}")
        
        # Analyze request and create tasks
        tasks = self._analyze_request(request)
        
        # Submit tasks to hive
        task_ids = []
        for task_spec in tasks:
            hive_task = HiveTask(
                task_id=str(uuid.uuid4()),
                name=task_spec["name"],
                description=task_spec["description"],
                required_capabilities=task_spec["capabilities"],
                priority=task_spec["priority"]
            )
            
            task_id = await self.hive.submit_task(hive_task)
            task_ids.append(task_id)
            logger.info(f"  ➡️ Task submitted: {task_spec['name']}")
        
        # Process tasks
        results = await self._process_tasks(task_ids)
        
        return {
            "request": request,
            "tasks_created": len(tasks),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_request(self, request: str) -> List[Dict]:
        """Analyze user request and create appropriate tasks"""
        request_lower = request.lower()
        tasks = []
        
        # Determine task types based on request content
        if "create" in request_lower or "generate" in request_lower or "build" in request_lower:
            if "api" in request_lower or "service" in request_lower:
                tasks.append({
                    "name": "Generate API Service",
                    "description": request,
                    "capabilities": ["generate_code"],
                    "priority": 1
                })
            elif "website" in request_lower or "frontend" in request_lower:
                tasks.append({
                    "name": "Generate Frontend Code",
                    "description": request,
                    "capabilities": ["generate_code"],
                    "priority": 1
                })
        
        if "plan" in request_lower or "roadmap" in request_lower or "strategy" in request_lower:
            tasks.append({
                "name": "Create Strategic Plan",
                "description": request,
                "capabilities": ["strategic_planning"],
                "priority": 2
            })
        
        if "deploy" in request_lower or "launch" in request_lower:
            tasks.append({
                "name": "Deploy Service",
                "description": request,
                "capabilities": ["deployment"],
                "priority": 1
            })
        
        if "monitor" in request_lower or "check" in request_lower:
            tasks.append({
                "name": "Monitor System",
                "description": request,
                "capabilities": ["monitoring"],
                "priority": 3
            })
        
        if "optimize" in request_lower or "improve" in request_lower:
            tasks.append({
                "name": "Optimize Code",
                "description": request,
                "capabilities": ["optimize_code"],
                "priority": 2
            })
        
        if "research" in request_lower or "find" in request_lower or "search" in request_lower:
            tasks.append({
                "name": "Research Topic",
                "description": request,
                "capabilities": ["web_search"],
                "priority": 2
            })
        
        # Default task if no specific type detected
        if not tasks:
            tasks.append({
                "name": "General Task",
                "description": request,
                "capabilities": ["task_execution"],
                "priority": 3
            })
        
        return tasks
    
    async def _process_tasks(self, task_ids: List[str]) -> List[Dict]:
        """Process tasks and collect results"""
        results = []
        
        # Simulate task processing by agents
        for task_id in task_ids:
            # Find task in hive
            task = None
            for t in self.hive.task_queue + list(self.hive.active_tasks.values()):
                if t.task_id == task_id:
                    task = t
                    break
            
            if task:
                # Find capable agent
                agent_id = await self.hive._select_agent_for_task(task)
                
                if agent_id and agent_id in self.agents:
                    agent = self.agents[agent_id]
                    
                    # Create task for agent
                    agent_task = Task(
                        name=task.name,
                        description=task.description,
                        priority=Priority(task.priority),
                        parameters=self._get_task_parameters(task)
                    )
                    
                    # Execute task
                    try:
                        result = await agent.execute(agent_task)
                        results.append({
                            "task_id": task_id,
                            "task_name": task.name,
                            "agent": agent.name,
                            "status": "completed",
                            "result": result
                        })
                        logger.info(f"  ✅ Task completed: {task.name} by {agent.name}")
                    except Exception as e:
                        results.append({
                            "task_id": task_id,
                            "task_name": task.name,
                            "agent": agent.name if 'agent' in locals() else "unassigned",
                            "status": "failed",
                            "error": str(e)
                        })
                        logger.error(f"  ❌ Task failed: {task.name} - {e}")
        
        return results
    
    def _get_task_parameters(self, task: HiveTask) -> Dict[str, Any]:
        """Get parameters for task execution"""
        params = {
            "type": self._determine_task_type(task.required_capabilities),
            "task_name": task.name,
            "description": task.description
        }
        
        # Add specific parameters based on capabilities
        if "generate_code" in task.required_capabilities:
            params.update({
                "language": "python",
                "code_type": "api" if "api" in task.name.lower() else "function",
                "specifications": {
                    "name": task.name.replace(" ", ""),
                    "description": task.description
                }
            })
        elif "strategic_planning" in task.required_capabilities:
            params.update({
                "project_name": task.name,
                "duration_months": 3,
                "goals": [task.description]
            })
        elif "deployment" in task.required_capabilities:
            params.update({
                "service_name": task.name.replace(" ", "-").lower(),
                "service_type": "api",
                "port": 8000,
                "environment": "production"
            })
        elif "monitoring" in task.required_capabilities:
            params.update({
                "services": ["api-service", "web-service"],
                "metrics": ["cpu", "memory", "disk", "network"]
            })
        
        return params
    
    def _determine_task_type(self, capabilities: List[str]) -> str:
        """Determine task type from capabilities"""
        if "generate_code" in capabilities:
            return "generate"
        elif "strategic_planning" in capabilities:
            return "strategic_planning"
        elif "deployment" in capabilities:
            return "deployment"
        elif "monitoring" in capabilities:
            return "monitoring"
        elif "web_search" in capabilities:
            return "general_research"
        else:
            return "task_execution"
    
    async def run_demo_tasks(self):
        """Run demonstration tasks"""
        logger.info("\n" + "="*70)
        logger.info("🎬 Running AgentZero Live Demonstration")
        logger.info("="*70)
        
        demo_requests = [
            "Create a REST API for user authentication with JWT tokens",
            "Generate a strategic plan for Q1 2025 product development",
            "Deploy the authentication service to production",
            "Monitor system health and generate performance report",
            "Optimize database queries for better performance"
        ]
        
        for i, request in enumerate(demo_requests, 1):
            logger.info(f"\n📌 Demo Request {i}: {request}")
            logger.info("-"*50)
            
            result = await self.process_user_request(request)
            
            # Display results
            logger.info(f"📊 Results:")
            for task_result in result["results"]:
                status_icon = "✅" if task_result["status"] == "completed" else "❌"
                logger.info(f"  {status_icon} {task_result['task_name']} - {task_result['status']}")
                
                if task_result["status"] == "completed" and "result" in task_result:
                    # Save result if it contains generated content
                    if isinstance(task_result["result"], dict):
                        self._save_result(task_result)
            
            await asyncio.sleep(1)  # Brief pause between requests
        
        logger.info("\n" + "="*70)
        logger.info("✨ AgentZero Live Demonstration Complete!")
        logger.info("="*70)
        
        # Show summary
        await self.show_summary()
    
    def _save_result(self, task_result: Dict):
        """Save task result to file"""
        result_dir = Path("live_results")
        result_dir.mkdir(exist_ok=True)
        
        filename = f"{task_result['task_name'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = result_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(task_result, f, indent=2, default=str)
        
        logger.info(f"    💾 Result saved to: {filepath}")
    
    async def show_summary(self):
        """Show system summary"""
        hive_status = self.hive.get_status()
        
        logger.info("\n📈 System Summary:")
        logger.info(f"  • Total Agents: {len(self.agents)}")
        logger.info(f"  • Tasks Completed: {hive_status['completed_tasks']}")
        logger.info(f"  • Active Tasks: {hive_status['active_tasks']}")
        logger.info(f"  • Hive Efficiency: {hive_status['metrics']['hive_efficiency']:.1%}")
        
        logger.info("\n🤖 Agent Performance:")
        for agent_id, agent in self.agents.items():
            agent_status = agent.get_status()
            logger.info(f"  • {agent.name}: {agent_status['metrics']['tasks_completed']} tasks completed")
        
        # List generated files
        result_files = list(Path("live_results").glob("*.json")) if Path("live_results").exists() else []
        generated_files = list(Path("generated").glob("*")) if Path("generated").exists() else []
        
        logger.info(f"\n📁 Files Generated:")
        logger.info(f"  • Result Files: {len(result_files)}")
        logger.info(f"  • Generated Content: {len(generated_files)}")
    
    async def interactive_mode(self):
        """Run in interactive mode"""
        logger.info("\n🎮 AgentZero Interactive Mode")
        logger.info("Type your requests or 'quit' to exit")
        logger.info("-"*50)
        
        while self.running:
            try:
                # In a real implementation, this would use input()
                # For now, we'll process some example requests
                await self.run_demo_tasks()
                self.running = False  # Exit after demo
                
            except KeyboardInterrupt:
                logger.info("\n👋 Shutting down...")
                self.running = False
    
    async def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("🛑 Shutting down AgentZero Live System...")
        
        # Shutdown agents
        for agent in self.agents.values():
            agent.shutdown()
        
        # Shutdown hive
        if self.hive:
            self.hive.shutdown()
        
        logger.info("✅ Shutdown complete")


async def main():
    """Main entry point"""
    system = AgentZeroLive()
    
    try:
        # Initialize system
        await system.initialize()
        
        # Run demonstration
        await system.run_demo_tasks()
        
    except Exception as e:
        logger.error(f"System error: {e}")
    
    finally:
        await system.shutdown()


if __name__ == "__main__":
    asyncio.run(main())