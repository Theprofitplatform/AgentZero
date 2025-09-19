#!/usr/bin/env python3
"""
Quick start example for AgentZero
Demonstrates basic usage of the multi-agent system
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from main import AgentZeroSystem


async def quick_start_demo():
    """
    Simple demonstration of AgentZero capabilities
    """
    print("=" * 50)
    print("AgentZero Quick Start Demo")
    print("=" * 50)
    
    # Initialize the system with 2 research and 2 code agents
    print("\n1. Initializing AgentZero system...")
    system = AgentZeroSystem({
        "research_agents": 2,
        "code_agents": 2
    })
    await system.initialize()
    
    # Start the system in background
    print("2. Starting agents and hive coordinator...")
    asyncio.create_task(system.start())
    await asyncio.sleep(2)  # Give system time to start
    
    # Submit a research task
    print("\n3. Submitting research task...")
    research_task = await system.submit_task(
        "Research the top 3 Python web frameworks and their key features",
        task_type="research"
    )
    print(f"   Research task ID: {research_task}")
    
    # Submit a code generation task
    print("\n4. Submitting code generation task...")
    code_task = await system.submit_task(
        "Generate a simple Python function to calculate fibonacci numbers",
        task_type="code_generation"
    )
    print(f"   Code task ID: {code_task}")
    
    # Monitor progress
    print("\n5. Monitoring task progress...")
    for i in range(10):
        status = await system.get_status()
        active = status['hive']['active_tasks']
        queued = status['hive']['queued_tasks']
        completed = status['hive']['completed_tasks']
        
        print(f"   [{i+1}/10] Active: {active}, Queued: {queued}, Completed: {completed}")
        
        if active == 0 and queued == 0:
            print("\n   All tasks completed!")
            break
        
        await asyncio.sleep(3)
    
    # Show final status
    print("\n6. Final System Status:")
    final_status = await system.get_status()
    print(f"   Total Agents: {final_status['hive']['agents']}")
    print(f"   Completed Tasks: {final_status['hive']['completed_tasks']}")
    print(f"   Hive Efficiency: {final_status['hive']['metrics']['hive_efficiency']:.2%}")
    
    # Show agent performance
    print("\n7. Agent Performance:")
    for agent in final_status['agents']:
        name = agent['name']
        success_rate = agent['metrics']['success_rate']
        tasks_completed = agent['metrics']['tasks_completed']
        print(f"   {name}: {tasks_completed} tasks, {success_rate:.0%} success rate")
    
    # Shutdown
    print("\n8. Shutting down system...")
    system.shutdown()
    print("\nDemo complete!")


if __name__ == "__main__":
    print("Starting AgentZero Quick Start Demo")
    print("This will demonstrate basic multi-agent task processing")
    print("-" * 50)
    
    try:
        asyncio.run(quick_start_demo())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()