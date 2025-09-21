"""Pytest configuration and fixtures"""
import pytest
import asyncio
from typing import AsyncGenerator
import httpx
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.main import app
from src.api.services.hive import hive_service
from src.api.services.auth import auth_service

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Create an async test client for the FastAPI app"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def auth_token():
    """Get an authentication token for testing"""
    token = auth_service.create_access_token(
        data={"sub": "admin", "role": "admin"}
    )
    return token

@pytest.fixture
async def auth_headers(auth_token):
    """Get authentication headers for testing"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture(autouse=True)
async def reset_hive():
    """Reset the hive service before each test"""
    hive_service.agents.clear()
    hive_service.tasks.clear()
    hive_service.agent_tasks.clear()
    hive_service.agent_logs.clear()
    hive_service.task_logs.clear()
    yield
    # Cleanup after test
    hive_service.agents.clear()
    hive_service.tasks.clear()

@pytest.fixture
async def sample_agent():
    """Create a sample agent for testing"""
    from src.api.models.agent import Agent, AgentType, AgentStatus
    from datetime import datetime

    agent = Agent(
        id="test-agent-001",
        agent_id="test-agent-001",
        name="TestAgent",
        type=AgentType.EXECUTION,
        status=AgentStatus.IDLE,
        capabilities=["test", "execution"],
        cpu_usage=10.0,
        memory_usage=20.0,
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow(),
        last_heartbeat=datetime.utcnow(),
        registered_at=datetime.utcnow(),
        last_updated=datetime.utcnow()
    )
    await hive_service.register_agent(agent)
    return agent

@pytest.fixture
async def sample_task():
    """Create a sample task for testing"""
    from src.api.models.task import Task, TaskType, TaskPriority, TaskStatus
    from datetime import datetime

    task = Task(
        id="test-task-001",
        name="Test Task",
        description="A test task",
        type=TaskType.GENERAL,
        priority=TaskPriority.NORMAL,
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await hive_service.submit_task(task)
    return task