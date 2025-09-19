#!/usr/bin/env python3
"""
Simplified demo runner for AgentZero
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.agent import Task, Priority
from src.agents.code_agent import CodeAgent
from datetime import datetime


class SimplifiedAgentZero:
    """Simplified version for demo purposes"""
    
    def __init__(self):
        self.code_agent = CodeAgent(name="DemoCodeAgent")
        print("🤖 AgentZero Demo System Initialized")
        print("=" * 50)
    
    async def generate_code(self, description: str, language: str = "python"):
        """Generate code based on description"""
        print(f"\n📝 Generating {language} code...")
        
        task = Task(
            name="Generate code",
            description=description,
            priority=Priority.HIGH,
            parameters={
                "type": "generate",
                "language": language,
                "code_type": "function",
                "specifications": {
                    "name": "generated_function",
                    "description": description,
                    "parameters": [],
                    "body": f"# Implementation for: {description}\n    pass"
                }
            }
        )
        
        result = await self.code_agent.execute(task)
        return result['code']
    
    async def analyze_code(self, code: str, language: str = "python"):
        """Analyze code"""
        print(f"\n🔍 Analyzing {language} code...")
        
        task = Task(
            name="Analyze code",
            description="Code analysis",
            priority=Priority.MEDIUM,
            parameters={
                "type": "analyze",
                "code": code,
                "language": language
            }
        )
        
        result = await self.code_agent.execute(task)
        return result
    
    async def generate_api(self, api_name: str, endpoints: list):
        """Generate API code"""
        print(f"\n🌐 Generating API: {api_name}")
        
        task = Task(
            name="Generate API",
            description=f"Generate {api_name} API",
            priority=Priority.HIGH,
            parameters={
                "type": "generate",
                "language": "python",
                "code_type": "api",
                "specifications": {
                    "name": api_name,
                    "endpoints": endpoints,
                    "models": []
                }
            }
        )
        
        result = await self.code_agent.execute(task)
        return result['code']
    
    async def optimize_code(self, code: str):
        """Optimize code"""
        print("\n⚡ Optimizing code...")
        
        task = Task(
            name="Optimize code",
            description="Code optimization",
            priority=Priority.MEDIUM,
            parameters={
                "type": "optimize",
                "code": code,
                "language": "python",
                "level": "standard"
            }
        )
        
        result = await self.code_agent.execute(task)
        return result


async def interactive_demo():
    """Run interactive demo"""
    system = SimplifiedAgentZero()
    
    print("\n🚀 Welcome to AgentZero Demo")
    print("=" * 50)
    print("\nAvailable commands:")
    print("  1. Generate a function")
    print("  2. Generate an API")
    print("  3. Analyze code")
    print("  4. Optimize code")
    print("  5. Quick demo")
    print("  0. Exit")
    print("=" * 50)
    
    while True:
        try:
            choice = input("\n> Enter choice (0-5): ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye!")
                break
            
            elif choice == "1":
                desc = input("Enter function description: ")
                lang = input("Language (python/javascript) [python]: ").strip() or "python"
                code = await system.generate_code(desc, lang)
                print("\n📄 Generated Code:")
                print("-" * 40)
                print(code)
                print("-" * 40)
            
            elif choice == "2":
                api_name = input("Enter API name: ")
                endpoints = []
                while True:
                    path = input("Enter endpoint path (or press Enter to finish): ").strip()
                    if not path:
                        break
                    method = input("Enter HTTP method (GET/POST/PUT/DELETE): ").upper()
                    name = input("Enter endpoint name: ")
                    desc = input("Enter endpoint description: ")
                    endpoints.append({
                        "path": path,
                        "method": method,
                        "name": name,
                        "description": desc
                    })
                
                if endpoints:
                    code = await system.generate_api(api_name, endpoints)
                    print("\n📄 Generated API:")
                    print("-" * 40)
                    print(code[:1000] + "..." if len(code) > 1000 else code)
                    print("-" * 40)
            
            elif choice == "3":
                print("Enter code to analyze (press Ctrl+D when done):")
                lines = []
                try:
                    while True:
                        lines.append(input())
                except EOFError:
                    pass
                
                code = "\n".join(lines)
                if code:
                    analysis = await system.analyze_code(code)
                    print("\n📊 Analysis Results:")
                    print("-" * 40)
                    print(f"Metrics: {analysis['metrics']}")
                    print(f"Issues: {analysis['issues']}")
                    print(f"Suggestions: {analysis['suggestions']}")
                    print("-" * 40)
            
            elif choice == "4":
                print("Enter code to optimize (press Ctrl+D when done):")
                lines = []
                try:
                    while True:
                        lines.append(input())
                except EOFError:
                    pass
                
                code = "\n".join(lines)
                if code:
                    result = await system.optimize_code(code)
                    print("\n⚡ Optimization Results:")
                    print("-" * 40)
                    print(f"Optimizations applied: {result['optimizations']}")
                    print(f"Estimated improvement: {result['estimated_gain']}")
                    print("\nOptimized code:")
                    print(result['optimized'])
                    print("-" * 40)
            
            elif choice == "5":
                print("\n🎬 Running Quick Demo...")
                print("=" * 50)
                
                # Demo 1: Generate a function
                print("\n1️⃣ Generating a factorial function...")
                code = await system.generate_code("Calculate factorial of a number")
                print(code)
                
                # Demo 2: Generate an API
                print("\n2️⃣ Generating a Todo API...")
                api_code = await system.generate_api(
                    "TodoAPI",
                    [
                        {"path": "/todos", "method": "GET", "name": "get_todos", "description": "Get all todos"},
                        {"path": "/todos", "method": "POST", "name": "create_todo", "description": "Create a todo"}
                    ]
                )
                print(api_code[:500] + "...")
                
                # Demo 3: Analyze code
                print("\n3️⃣ Analyzing sample code...")
                sample = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
                analysis = await system.analyze_code(sample)
                print(f"Analysis: {analysis['metrics']}")
                
                print("\n✅ Demo completed!")
                print("=" * 50)
            
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Main entry point"""
    await interactive_demo()


if __name__ == "__main__":
    asyncio.run(main())