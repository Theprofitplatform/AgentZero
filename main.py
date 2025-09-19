#!/usr/bin/env python3
"""
AgentZero Main Application
Orchestrates the multi-agent system with hive intelligence
"""

import asyncio
import argparse
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.hive.coordinator import HiveCoordinator
from src.agents.research_agent import ResearchAgent
from src.agents.code_agent import CodeAgent
from src.core.agent import Task, Priority


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentZeroSystem:
    """Main system orchestrator"""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.hive = None
        self.agents = []
        self.running = False
    
    async def initialize(self):
        """Initialize the system"""
        logger.info("Initializing AgentZero System...")
        
        # Create hive coordinator
        self.hive = HiveCoordinator(
            config={
                "distribution_strategy": "capability_based",
                "persist_state": True
            }
        )
        
        # Create agents
        num_research = self.config.get("research_agents", 2)
        num_code = self.config.get("code_agents", 2)
        
        # Create research agents
        for i in range(num_research):
            agent = ResearchAgent(
                name=f"ResearchAgent-{i+1}",
                config={"max_depth": 3, "max_pages": 50}
            )
            self.agents.append(agent)
            
            # Register with hive (create AgentInfo object)
            from src.hive.coordinator import AgentInfo
            agent_info = AgentInfo(
                agent_id=agent.agent_id,
                name=agent.name,
                capabilities=["web_search", "extract_content", "analyze_data"],
                status="idle",
                last_heartbeat=datetime.now()
            )
            await self.hive.register_agent(agent_info, connection=None)
        
        # Create code agents
        for i in range(num_code):
            agent = CodeAgent(
                name=f"CodeAgent-{i+1}",
                config={"languages": ["python", "javascript"]}
            )
            self.agents.append(agent)
            
            # Register with hive (create AgentInfo object)
            agent_info = AgentInfo(
                agent_id=agent.agent_id,
                name=agent.name,
                capabilities=["generate_code", "analyze_code", "debug_code"],
                status="idle",
                last_heartbeat=datetime.now()
            )
            await self.hive.register_agent(agent_info, connection=None)
        
        logger.info(f"System initialized with {len(self.agents)} agents")
    
    async def start(self):
        """Start the system"""
        logger.info("Starting AgentZero System...")
        self.running = True
        
        # Start hive coordinator
        hive_task = asyncio.create_task(self.hive.start())
        
        # Start all agents
        agent_tasks = []
        for agent in self.agents:
            task = asyncio.create_task(agent.run())
            agent_tasks.append(task)
        
        # Wait for all components
        await asyncio.gather(hive_task, *agent_tasks)
    
    async def submit_task(self, task_description: str, task_type: str = "general"):
        """Submit a task to the system"""
        task = Task(
            name=task_description,
            description=task_description,
            priority=Priority.MEDIUM,
            parameters={"type": task_type}
        )
        
        # Determine required capabilities
        required_capabilities = []
        if "research" in task_type.lower() or "search" in task_type.lower():
            required_capabilities.append("web_search")
        if "code" in task_type.lower() or "generate" in task_type.lower():
            required_capabilities.append("generate_code")
        
        # Submit to hive
        from src.hive.coordinator import HiveTask
        hive_task = HiveTask(
            task_id=task.id,
            name=task.name,
            description=task.description,
            required_capabilities=required_capabilities,
            priority=task.priority.value
        )
        
        task_id = await self.hive.submit_task(hive_task)
        logger.info(f"Task submitted: {task_id}")
        
        return task_id
    
    async def get_status(self):
        """Get system status"""
        hive_status = self.hive.get_status()
        
        agent_statuses = []
        for agent in self.agents:
            agent_statuses.append(agent.get_status())
        
        return {
            "hive": hive_status,
            "agents": agent_statuses
        }
    
    def shutdown(self):
        """Shutdown the system"""
        logger.info("Shutting down AgentZero System...")
        self.running = False
        
        # Shutdown hive
        if self.hive:
            self.hive.shutdown()
        
        # Shutdown agents
        for agent in self.agents:
            agent.shutdown()
        
        logger.info("System shutdown complete")


async def interactive_mode(system: AgentZeroSystem):
    """Run in interactive mode"""
    print("\n=== AgentZero Interactive Mode ===")
    print("Commands:")
    print("  research <query> - Research a topic")
    print("  code <description> - Generate code")
    print("  analyze <file> - Analyze code file")
    print("  status - Show system status")
    print("  quit - Exit the system")
    print("=" * 35 + "\n")
    
    while system.running:
        try:
            command = input("AgentZero> ").strip()
            
            if not command:
                continue
            
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            
            if cmd == "quit":
                break
            
            elif cmd == "status":
                status = await system.get_status()
                print(f"\nHive Status:")
                print(f"  Agents: {status['hive']['agents']}")
                print(f"  Active Tasks: {status['hive']['active_tasks']}")
                print(f"  Queued Tasks: {status['hive']['queued_tasks']}")
                print(f"  Completed: {status['hive']['completed_tasks']}")
                print(f"  Efficiency: {status['hive']['metrics']['hive_efficiency']:.2%}")
                
            elif cmd == "research" and len(parts) > 1:
                query = parts[1]
                task_id = await system.submit_task(query, "research")
                print(f"Research task submitted: {task_id}")
                
            elif cmd == "code" and len(parts) > 1:
                description = parts[1]
                task_id = await system.submit_task(description, "code_generation")
                print(f"Code generation task submitted: {task_id}")
                
            elif cmd == "analyze" and len(parts) > 1:
                filepath = parts[1]
                # Read file and submit for analysis
                try:
                    with open(filepath, 'r') as f:
                        code = f.read()
                    task_id = await system.submit_task(f"Analyze code from {filepath}", "code_analysis")
                    print(f"Code analysis task submitted: {task_id}")
                except FileNotFoundError:
                    print(f"File not found: {filepath}")
                
            else:
                print("Unknown command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    system.shutdown()


async def batch_mode(system: AgentZeroSystem, tasks_file: str):
    """Run in batch mode with tasks from file"""
    try:
        with open(tasks_file, 'r') as f:
            tasks = f.readlines()
        
        logger.info(f"Processing {len(tasks)} tasks from {tasks_file}")
        
        for task in tasks:
            task = task.strip()
            if task and not task.startswith('#'):
                await system.submit_task(task)
        
        # Wait for completion
        while True:
            status = await system.get_status()
            if status['hive']['queued_tasks'] == 0 and status['hive']['active_tasks'] == 0:
                break
            await asyncio.sleep(5)
        
        logger.info("Batch processing complete")
        
    except FileNotFoundError:
        logger.error(f"Tasks file not found: {tasks_file}")
    
    system.shutdown()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AgentZero Multi-Agent System")
    parser.add_argument("--mode", choices=["interactive", "batch", "server"], 
                       default="interactive", help="Operation mode")
    parser.add_argument("--tasks", help="Tasks file for batch mode")
    parser.add_argument("--research-agents", type=int, default=2,
                       help="Number of research agents")
    parser.add_argument("--code-agents", type=int, default=2,
                       help="Number of code agents")
    parser.add_argument("--port", type=int, default=8000,
                       help="Port for server mode")
    
    args = parser.parse_args()
    
    # Create system
    system = AgentZeroSystem({
        "research_agents": args.research_agents,
        "code_agents": args.code_agents
    })
    
    # Initialize
    await system.initialize()
    
    # Handle shutdown
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        system.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run based on mode
    if args.mode == "interactive":
        # Start system in background
        asyncio.create_task(system.start())
        await interactive_mode(system)
        
    elif args.mode == "batch":
        if not args.tasks:
            logger.error("Tasks file required for batch mode")
            sys.exit(1)
        asyncio.create_task(system.start())
        await batch_mode(system, args.tasks)
        
    elif args.mode == "server":
        # Import and start API server
        from src.api.server import create_app
        app = create_app(system)
        
        import uvicorn
        await uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    asyncio.run(main())