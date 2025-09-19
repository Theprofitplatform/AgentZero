#!/usr/bin/env python3
"""
Automated demo of AgentZero capabilities
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.agent import Task, Priority
from src.agents.code_agent import CodeAgent


async def run_demo():
    """Run automated demo"""
    print("=" * 60)
    print("🚀 AgentZero - Advanced Multi-Agent System Demo")
    print("=" * 60)
    
    # Initialize agent
    code_agent = CodeAgent(name="DemoCodeAgent")
    print("\n✅ Code Agent initialized")
    
    # Demo 1: Generate Python API
    print("\n" + "=" * 60)
    print("📝 Demo 1: Generating Python FastAPI Application")
    print("=" * 60)
    
    api_task = Task(
        name="Generate User Management API",
        description="Create a REST API for user management",
        priority=Priority.HIGH,
        parameters={
            "type": "generate",
            "language": "python",
            "code_type": "api",
            "specifications": {
                "name": "UserManagementAPI",
                "endpoints": [
                    {"method": "GET", "path": "/users", "name": "list_users", "description": "List all users"},
                    {"method": "GET", "path": "/users/{id}", "name": "get_user", "description": "Get user by ID"},
                    {"method": "POST", "path": "/users", "name": "create_user", "description": "Create new user"},
                    {"method": "PUT", "path": "/users/{id}", "name": "update_user", "description": "Update user"},
                    {"method": "DELETE", "path": "/users/{id}", "name": "delete_user", "description": "Delete user"}
                ],
                "models": [
                    {
                        "name": "User",
                        "fields": [
                            {"name": "id", "type": "int", "required": True},
                            {"name": "username", "type": "str", "required": True},
                            {"name": "email", "type": "str", "required": True},
                            {"name": "full_name", "type": "str", "required": False},
                            {"name": "is_active", "type": "bool", "required": False}
                        ]
                    }
                ]
            }
        }
    )
    
    result = await code_agent.execute(api_task)
    print("\n📄 Generated API Code (first 800 chars):")
    print("-" * 40)
    print(result['code'][:800])
    print("...")
    print("-" * 40)
    print(f"✅ Code is valid: {result['valid']}")
    
    # Demo 2: Analyze Code
    print("\n" + "=" * 60)
    print("🔍 Demo 2: Code Analysis")
    print("=" * 60)
    
    sample_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
"""
    
    analysis_task = Task(
        name="Analyze sorting algorithms",
        description="Analyze code quality and complexity",
        priority=Priority.MEDIUM,
        parameters={
            "type": "analyze",
            "code": sample_code,
            "language": "python"
        }
    )
    
    print("\n📝 Analyzing code with multiple algorithms...")
    analysis = await code_agent.execute(analysis_task)
    
    print("\n📊 Analysis Results:")
    print("-" * 40)
    print(f"📈 Metrics:")
    for key, value in analysis['metrics'].items():
        print(f"   • {key}: {value}")
    
    if analysis['issues']:
        print(f"\n⚠️  Issues Found:")
        for issue in analysis['issues']:
            print(f"   • {issue}")
    else:
        print(f"\n✅ No issues found!")
    
    if analysis['suggestions']:
        print(f"\n💡 Suggestions:")
        for suggestion in analysis['suggestions']:
            print(f"   • {suggestion['message']}")
    
    # Demo 3: Code Generation - CLI Tool
    print("\n" + "=" * 60)
    print("🛠️  Demo 3: Generating CLI Application")
    print("=" * 60)
    
    cli_task = Task(
        name="Generate File Manager CLI",
        description="Create a command-line file management tool",
        priority=Priority.HIGH,
        parameters={
            "type": "generate",
            "language": "python",
            "code_type": "cli",
            "specifications": {
                "name": "filemanager",
                "description": "A powerful file management CLI tool",
                "commands": [
                    {
                        "name": "list",
                        "description": "List files in directory",
                        "arguments": [
                            {"name": "path", "type": "str", "required": False, "help": "Directory path"},
                            {"name": "recursive", "type": "bool", "required": False, "help": "List recursively"}
                        ]
                    },
                    {
                        "name": "copy",
                        "description": "Copy files",
                        "arguments": [
                            {"name": "source", "type": "str", "required": True, "help": "Source file"},
                            {"name": "destination", "type": "str", "required": True, "help": "Destination path"}
                        ]
                    },
                    {
                        "name": "search",
                        "description": "Search for files",
                        "arguments": [
                            {"name": "pattern", "type": "str", "required": True, "help": "Search pattern"},
                            {"name": "path", "type": "str", "required": False, "help": "Search path"}
                        ]
                    }
                ]
            }
        }
    )
    
    cli_result = await code_agent.execute(cli_task)
    print("\n📄 Generated CLI Code (first 600 chars):")
    print("-" * 40)
    print(cli_result['code'][:600])
    print("...")
    print("-" * 40)
    
    # Demo 4: Code Optimization
    print("\n" + "=" * 60)
    print("⚡ Demo 4: Code Optimization")
    print("=" * 60)
    
    unoptimized_code = """
def find_duplicates(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[i] == lst[j] and lst[i] not in duplicates:
                duplicates.append(lst[i])
    return duplicates

def sum_of_squares(n):
    result = 0
    for i in range(1, n + 1):
        result = result + i * i
    return result
"""
    
    optimize_task = Task(
        name="Optimize Python code",
        description="Optimize for performance",
        priority=Priority.MEDIUM,
        parameters={
            "type": "optimize",
            "code": unoptimized_code,
            "language": "python",
            "level": "standard"
        }
    )
    
    print("\n🔧 Optimizing code...")
    optimization = await code_agent.execute(optimize_task)
    
    print("\n📊 Optimization Results:")
    print("-" * 40)
    if optimization['optimizations']:
        print("✅ Optimizations applied:")
        for opt in optimization['optimizations']:
            print(f"   • {opt}")
    print(f"\n📈 Estimated performance gain: {optimization['estimated_gain']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")
    print("=" * 60)
    print("\n📋 Summary of AgentZero Capabilities Demonstrated:")
    print("   ✅ API Generation (FastAPI with models and endpoints)")
    print("   ✅ Code Analysis (metrics, issues, suggestions)")
    print("   ✅ CLI Application Generation (with argparse)")
    print("   ✅ Code Optimization (performance improvements)")
    print("\n🚀 AgentZero is ready for advanced multi-agent operations!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_demo())