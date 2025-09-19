#!/usr/bin/env python3
"""
Simple test of AgentZero components without full async infrastructure
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.agent import Task, Priority
from src.agents.research_agent import ResearchAgent
from src.agents.code_agent import CodeAgent


async def test_research_agent():
    """Test the research agent"""
    print("\n=== Testing Research Agent ===")
    
    agent = ResearchAgent(
        name="TestResearchAgent",
        config={"max_depth": 2, "max_pages": 10}
    )
    
    # Create a research task
    task = Task(
        name="Research Python frameworks",
        description="Research popular Python web frameworks",
        priority=Priority.MEDIUM,
        parameters={
            "type": "general_research",
            "query": "Python web frameworks FastAPI Django Flask"
        }
    )
    
    try:
        print(f"Executing task: {task.name}")
        result = await agent.execute(task)
        print(f"Result: {result}")
        print("✓ Research Agent test passed")
    except Exception as e:
        print(f"✗ Research Agent test failed: {e}")


async def test_code_agent():
    """Test the code agent"""
    print("\n=== Testing Code Agent ===")
    
    agent = CodeAgent(
        name="TestCodeAgent",
        config={"languages": ["python", "javascript"]}
    )
    
    # Create a code generation task
    task = Task(
        name="Generate API",
        description="Generate a simple REST API",
        priority=Priority.HIGH,
        parameters={
            "type": "generate",
            "language": "python",
            "code_type": "api",
            "specifications": {
                "name": "UserAPI",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/users",
                        "name": "get_users",
                        "description": "Get all users"
                    },
                    {
                        "method": "POST",
                        "path": "/users",
                        "name": "create_user",
                        "description": "Create a new user"
                    }
                ],
                "models": [
                    {
                        "name": "User",
                        "fields": [
                            {"name": "id", "type": "int", "required": True},
                            {"name": "name", "type": "str", "required": True},
                            {"name": "email", "type": "str", "required": True}
                        ]
                    }
                ]
            }
        }
    )
    
    try:
        print(f"Executing task: {task.name}")
        result = await agent.execute(task)
        print(f"Generated code:\n{result['code'][:500]}...")  # First 500 chars
        print(f"Valid: {result['valid']}")
        print("✓ Code Agent test passed")
    except Exception as e:
        print(f"✗ Code Agent test failed: {e}")


async def test_code_analysis():
    """Test code analysis"""
    print("\n=== Testing Code Analysis ===")
    
    agent = CodeAgent(name="TestAnalyzer")
    
    # Sample code to analyze
    code = """
def calculate_factorial(n):
    if n == 0:
        return 1
    else:
        return n * calculate_factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    task = Task(
        name="Analyze code",
        description="Analyze Python code",
        priority=Priority.MEDIUM,
        parameters={
            "type": "analyze",
            "code": code,
            "language": "python"
        }
    )
    
    try:
        print("Analyzing code...")
        result = await agent.execute(task)
        print(f"Analysis results:")
        print(f"  Metrics: {result['metrics']}")
        print(f"  Issues: {result['issues']}")
        print(f"  Suggestions: {result['suggestions']}")
        print("✓ Code Analysis test passed")
    except Exception as e:
        print(f"✗ Code Analysis test failed: {e}")


async def main():
    """Run all tests"""
    print("=" * 50)
    print("AgentZero Component Tests")
    print("=" * 50)
    
    # Test individual agents
    await test_code_agent()
    await test_code_analysis()
    
    # Note: Research agent requires actual web access or mocked responses
    print("\n=== Research Agent Test Skipped ===")
    print("(Requires web access or mocked API responses)")
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())