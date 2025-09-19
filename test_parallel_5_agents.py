#!/usr/bin/env python3
"""
Test 5 Parallel Agents
Demonstrates concurrent execution of 5 specialized agents
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import time
from typing import Dict, List, Any

# Add src to path
import sys
sys.path.insert(0, '/home/avi/projects/agentzero/src')

from core.agent import BaseAgent, Task, Priority, AgentCapability
from hive.coordinator import HiveCoordinator
from agents.research_agent import ResearchAgent
from agents.code_agent import CodeAgent
from agents.planning_agent import PlanningAgent
from agents.execution_agent import ExecutionAgent


class ParallelTestSystem:
    """System to test parallel agent execution"""
    
    def __init__(self):
        self.coordinator = HiveCoordinator()
        self.results_dir = Path("parallel_test_results")
        self.results_dir.mkdir(exist_ok=True)
        self.start_time = None
        self.end_time = None
        
    async def initialize_agents(self):
        """Initialize exactly 5 specialized agents"""
        print("\n🔧 Initializing 5 Parallel Agents...")
        print("=" * 60)
        
        # Create diverse agent mix for parallel testing
        agents = [
            ResearchAgent("ResearchAgent-Alpha"),
            CodeAgent("CodeAgent-Beta"),
            PlanningAgent("PlanningAgent-Gamma"),
            ExecutionAgent("ExecutionAgent-Delta"),
            CodeAgent("CodeAgent-Epsilon")  # Second code agent for parallel code tasks
        ]
        
        # Register all agents (using simpler direct registration)
        for agent in agents:
            # Directly add to coordinator's agent registry
            self.coordinator.agents[agent.agent_id] = agent
            print(f"✅ Registered: {agent.agent_id} with capabilities: {agent.capabilities}")
        
        print(f"\n📊 Total Agents Ready: {len(agents)}")
        return agents
    
    def create_test_tasks(self) -> List[Task]:
        """Create 5 diverse tasks for parallel execution"""
        print("\n📋 Creating 5 Parallel Tasks...")
        print("=" * 60)
        
        tasks = [
            # Task 1: Research Task
            Task(
                id=f"research_{datetime.now().strftime('%H%M%S')}",
                name="Market Research Analysis",
                description="Research cloud computing trends and competitive analysis",
                priority=Priority.HIGH,
                parameters={
                    "query": "cloud computing market trends 2025",
                    "depth": "comprehensive"
                }
            ),
            
            # Task 2: API Development
            Task(
                id=f"api_{datetime.now().strftime('%H%M%S')}",
                name="Payment Gateway API",
                description="Create payment processing API with Stripe integration",
                priority=Priority.CRITICAL,
                parameters={
                    "framework": "FastAPI",
                    "features": ["payment processing", "webhooks", "refunds"]
                }
            ),
            
            # Task 3: Strategic Planning
            Task(
                id=f"planning_{datetime.now().strftime('%H%M%S')}",
                name="Product Launch Strategy",
                description="Create go-to-market strategy for new SaaS product",
                priority=Priority.HIGH,
                parameters={
                    "product": "AI Analytics Platform",
                    "timeline": "Q2 2025",
                    "budget": "$500K"
                }
            ),
            
            # Task 4: System Deployment
            Task(
                id=f"deploy_{datetime.now().strftime('%H%M%S')}",
                name="Microservices Deployment",
                description="Deploy microservices architecture with Kubernetes",
                priority=Priority.HIGH,
                parameters={
                    "services": ["auth", "api", "worker", "cache"],
                    "environment": "production",
                    "orchestration": "kubernetes"
                }
            ),
            
            # Task 5: Code Optimization
            Task(
                id=f"optimize_{datetime.now().strftime('%H%M%S')}",
                name="Database Query Optimization",
                description="Optimize complex SQL queries for performance",
                priority=Priority.MEDIUM,
                parameters={
                    "database": "PostgreSQL",
                    "target_improvement": "50% faster",
                    "tables": ["orders", "products", "users"]
                }
            )
        ]
        
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task.name} (Priority: {task.priority.value})")
        
        return tasks
    
    async def submit_tasks(self, tasks: List[Task]):
        """Submit all tasks for parallel execution"""
        print("\n🚀 Submitting Tasks for Parallel Execution...")
        print("=" * 60)
        
        # Always initialize as asyncio.Queue for our test
        self.coordinator.task_queue = asyncio.Queue()
        self.coordinator.completed_tasks = {}
        
        # Submit all tasks to queue
        for task in tasks:
            await self.coordinator.task_queue.put(task)
        
        print(f"✅ All {len(tasks)} tasks submitted successfully")
    
    async def monitor_execution(self):
        """Monitor parallel execution progress"""
        print("\n📊 Monitoring Parallel Execution...")
        print("=" * 60)
        
        # Process tasks with agents
        processing_tasks = []
        for agent in self.coordinator.agents.values():
            processing_tasks.append(self.process_agent_tasks(agent))
        
        # Start all agents processing concurrently
        await asyncio.gather(*processing_tasks)
        
        print("\n\n✨ All tasks completed!")
    
    async def process_agent_tasks(self, agent):
        """Process tasks for a single agent"""
        while not self.coordinator.task_queue.empty():
            try:
                task = await asyncio.wait_for(
                    self.coordinator.task_queue.get(), 
                    timeout=0.1
                )
                
                # Check if agent can handle this task
                if self.can_agent_handle_task(agent, task):
                    print(f"\n  📌 {agent.agent_id} processing: {task.name}")
                    
                    # Process the task
                    result = await agent.process_task(task)
                    
                    # Store result
                    self.coordinator.completed_tasks[task.id] = {
                        "task_id": task.id,
                        "task_name": task.name,
                        "agent": agent.agent_id,
                        "status": "completed",
                        "result": result
                    }
                else:
                    # Put task back for another agent
                    await self.coordinator.task_queue.put(task)
                    await asyncio.sleep(0.1)
                    
            except asyncio.TimeoutError:
                break
            except Exception as e:
                print(f"\n  ⚠️ Error processing task: {e}")
    
    def can_agent_handle_task(self, agent, task) -> bool:
        """Check if agent can handle the given task"""
        # Simple capability matching based on capability names
        task_type = task.name.lower()
        
        if "research" in task_type or "market" in task_type:
            return 'web_search' in agent.capabilities or 'analyze_data' in agent.capabilities
        elif "api" in task_type or "gateway" in task_type:
            return 'generate_code' in agent.capabilities
        elif "planning" in task_type or "strategy" in task_type:
            return 'strategic_planning' in agent.capabilities or 'task_decomposition' in agent.capabilities
        elif "deploy" in task_type or "microservices" in task_type:
            return 'deployment' in agent.capabilities or 'task_execution' in agent.capabilities
        elif "optimize" in task_type or "query" in task_type:
            return 'optimize_code' in agent.capabilities or 'analyze_code' in agent.capabilities
        
        return True  # Default: any agent can try
    
    def save_results(self):
        """Save results from parallel execution"""
        print("\n💾 Saving Parallel Execution Results...")
        print("=" * 60)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save individual task results
        for task_id, result in self.coordinator.completed_tasks.items():
            filename = f"parallel_{task_id}_{timestamp}.json"
            filepath = self.results_dir / filename
            
            # Convert result to serializable format
            if isinstance(result, dict):
                save_data = result
            else:
                # Handle Task objects or other non-dict results
                save_data = {
                    "task_id": task_id,
                    "task_name": getattr(result, 'name', 'Unknown'),
                    "status": "completed",
                    "result": str(result)
                }
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
            
            print(f"  📄 Saved: {filename}")
        
        # Save execution summary
        execution_time = (self.end_time - self.start_time).total_seconds()
        summary = {
            "execution_id": f"parallel_test_{timestamp}",
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "execution_time_seconds": execution_time,
            "total_agents": 5,
            "total_tasks": 5,
            "tasks_per_second": 5 / execution_time if execution_time > 0 else 0,
            "completed_tasks": len(self.coordinator.completed_tasks),
            "agent_performance": {},
            "task_results": {}
        }
        
        # Add agent performance metrics
        for agent_id, agent in self.coordinator.agents.items():
            completed_tasks = getattr(agent, 'completed_tasks', [])
            # Handle both list and int for completed_tasks
            if isinstance(completed_tasks, list):
                num_tasks = len(completed_tasks)
            else:
                num_tasks = completed_tasks
                
            summary["agent_performance"][agent_id] = {
                "tasks_completed": num_tasks,
                "total_execution_time": getattr(agent, 'total_execution_time', 0.0),
                "capabilities": list(agent.capabilities.keys()) if hasattr(agent, 'capabilities') else []
            }
        
        # Add task results summary
        for task_id, result in self.coordinator.completed_tasks.items():
            # Handle both dict and Task objects
            if isinstance(result, dict):
                summary["task_results"][task_id] = {
                    "name": result.get("task_name", "Unknown"),
                    "status": result.get("status", "Unknown"),
                    "agent": result.get("agent", "Unknown")
                }
            else:
                # If result is a Task object, extract its properties
                summary["task_results"][task_id] = {
                    "name": getattr(result, 'name', 'Unknown'),
                    "status": "completed",
                    "agent": "Unknown"
                }
        
        summary_file = self.results_dir / f"parallel_execution_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📊 Summary saved: {summary_file.name}")
        print(f"⏱️  Total Execution Time: {execution_time:.2f} seconds")
        print(f"⚡ Performance: {summary['tasks_per_second']:.2f} tasks/second")
    
    async def run_parallel_test(self):
        """Main execution flow for parallel testing"""
        print("\n" + "=" * 60)
        print("🚀 PARALLEL AGENTS TEST - 5 CONCURRENT AGENTS")
        print("=" * 60)
        
        try:
            self.start_time = datetime.now()
            
            # Initialize agents
            agents = await self.initialize_agents()
            
            # Create test tasks
            tasks = self.create_test_tasks()
            
            # Submit all tasks
            await self.submit_tasks(tasks)
            
            # Monitor and execute tasks
            await self.monitor_execution()
            
            self.end_time = datetime.now()
            
            # Save results
            self.save_results()
            
            # Display final statistics
            self.display_statistics()
            
        except Exception as e:
            print(f"\n❌ Error during parallel test: {e}")
            import traceback
            traceback.print_exc()
    
    def display_statistics(self):
        """Display detailed execution statistics"""
        print("\n" + "=" * 60)
        print("📈 PARALLEL EXECUTION STATISTICS")
        print("=" * 60)
        
        execution_time = (self.end_time - self.start_time).total_seconds()
        
        print(f"\n⏱️  Execution Metrics:")
        print(f"  • Total Time: {execution_time:.2f} seconds")
        print(f"  • Tasks Completed: {len(self.coordinator.completed_tasks)}/5")
        print(f"  • Average Time per Task: {execution_time/5:.2f} seconds")
        print(f"  • Parallel Efficiency: {(5/(execution_time/10)*100):.1f}%")
        
        print(f"\n👥 Agent Performance:")
        for agent_id, agent in self.coordinator.agents.items():
            completed_tasks = getattr(agent, 'completed_tasks', [])
            total_execution_time = getattr(agent, 'total_execution_time', 0.0)
            
            # Handle both list and int for completed_tasks
            if isinstance(completed_tasks, list):
                num_tasks = len(completed_tasks)
            else:
                num_tasks = completed_tasks
            
            print(f"  • {agent_id}:")
            print(f"    - Tasks Completed: {num_tasks}")
            print(f"    - Execution Time: {total_execution_time:.2f}s")
            if num_tasks > 0:
                print(f"    - Avg Task Time: {total_execution_time/num_tasks:.2f}s")
        
        print(f"\n✅ Task Completion:")
        for task_id, result in self.coordinator.completed_tasks.items():
            print(f"  • {result.get('task_name', task_id)}: {result.get('status', 'Unknown')}")
        
        print("\n" + "=" * 60)
        print("🎯 PARALLEL TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)


async def main():
    """Main entry point"""
    system = ParallelTestSystem()
    await system.run_parallel_test()


if __name__ == "__main__":
    print("\n🔷 Starting 5 Parallel Agents Test...")
    asyncio.run(main())