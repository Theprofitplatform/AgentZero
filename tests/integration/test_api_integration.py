"""API Integration Tests"""
import pytest
import asyncio
import json
from httpx import AsyncClient

@pytest.mark.asyncio
class TestAPIIntegration:
    """Test API endpoints integration"""

    async def test_authentication_flow(self, async_client: AsyncClient):
        """Test complete authentication flow"""
        # Test login
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "secret"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

        # Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        user = response.json()
        assert user["username"] == "admin"

        # Test token refresh
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": data["refresh_token"]}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_agent_endpoints(self, async_client: AsyncClient, auth_headers):
        """Test all agent-related endpoints"""
        # Create agent
        agent_data = {
            "name": "TestAgent",
            "type": "execution",
            "capabilities": ["test", "execution"]
        }
        response = await async_client.post(
            "/api/v1/agents",
            json=agent_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        agent = response.json()
        agent_id = agent["id"]

        # Get all agents
        response = await async_client.get(
            "/api/v1/agents",
            headers=auth_headers
        )
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) > 0

        # Get specific agent
        response = await async_client.get(
            f"/api/v1/agents/{agent_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["id"] == agent_id

        # Update agent
        update_data = {"status": "working"}
        response = await async_client.put(
            f"/api/v1/agents/{agent_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200

        # Control agent
        control_data = {"action": "pause"}
        response = await async_client.post(
            f"/api/v1/agents/{agent_id}/control",
            json=control_data,
            headers=auth_headers
        )
        assert response.status_code == 200

        # Get agent metrics
        response = await async_client.get(
            f"/api/v1/agents/{agent_id}/metrics",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Delete agent
        response = await async_client.delete(
            f"/api/v1/agents/{agent_id}",
            headers=auth_headers
        )
        assert response.status_code == 204

    async def test_task_endpoints(self, async_client: AsyncClient, auth_headers):
        """Test all task-related endpoints"""
        # Create task
        task_data = {
            "name": "Test Task",
            "description": "Testing task endpoints",
            "type": "general",
            "priority": "normal",
            "tags": ["test"]
        }
        response = await async_client.post(
            "/api/v1/tasks",
            json=task_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        task = response.json()
        task_id = task["id"]

        # Get all tasks
        response = await async_client.get(
            "/api/v1/tasks",
            headers=auth_headers
        )
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) > 0

        # Get specific task
        response = await async_client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["id"] == task_id

        # Update task
        update_data = {"priority": "high"}
        response = await async_client.put(
            f"/api/v1/tasks/{task_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200

        # Get task logs
        response = await async_client.get(
            f"/api/v1/tasks/{task_id}/logs",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Cancel task
        response = await async_client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )
        assert response.status_code == 204

    async def test_batch_operations(self, async_client: AsyncClient, auth_headers):
        """Test batch task creation"""
        tasks = [
            {
                "name": f"Batch Task {i}",
                "description": f"Task {i} description",
                "type": "general",
                "priority": "normal"
            }
            for i in range(5)
        ]

        response = await async_client.post(
            "/api/v1/tasks/batch",
            json=tasks,
            headers=auth_headers
        )
        assert response.status_code == 200
        created_tasks = response.json()
        assert len(created_tasks) == 5

    async def test_filtering_and_pagination(self, async_client: AsyncClient, auth_headers, sample_agent):
        """Test filtering and pagination on list endpoints"""
        # Test agent filtering by status
        response = await async_client.get(
            "/api/v1/agents?status=idle",
            headers=auth_headers
        )
        assert response.status_code == 200
        agents = response.json()
        assert all(agent["status"] == "idle" for agent in agents)

        # Test pagination
        response = await async_client.get(
            "/api/v1/agents?skip=0&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Test task filtering by priority
        response = await async_client.get(
            "/api/v1/tasks?priority=high",
            headers=auth_headers
        )
        assert response.status_code == 200

    async def test_error_handling(self, async_client: AsyncClient, auth_headers):
        """Test API error handling"""
        # Test 404 - Not Found
        response = await async_client.get(
            "/api/v1/agents/non-existent-id",
            headers=auth_headers
        )
        assert response.status_code == 404

        # Test 401 - Unauthorized
        response = await async_client.get("/api/v1/agents")
        assert response.status_code == 401

        # Test 400 - Bad Request
        response = await async_client.post(
            "/api/v1/tasks",
            json={"invalid": "data"},
            headers=auth_headers
        )
        assert response.status_code == 422  # FastAPI validation error

    async def test_concurrent_requests(self, async_client: AsyncClient, auth_headers):
        """Test handling of concurrent API requests"""
        # Create multiple tasks concurrently
        tasks = []
        for i in range(10):
            task = async_client.post(
                "/api/v1/tasks",
                json={
                    "name": f"Concurrent Task {i}",
                    "description": "Testing concurrency",
                    "type": "general",
                    "priority": "normal"
                },
                headers=auth_headers
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        assert all(r.status_code == 201 for r in responses)

        # Verify all tasks were created
        response = await async_client.get(
            "/api/v1/tasks",
            headers=auth_headers
        )
        created_tasks = response.json()
        assert len(created_tasks) >= 10

    async def test_task_statistics(self, async_client: AsyncClient, auth_headers, sample_task):
        """Test task statistics endpoint"""
        response = await async_client.get(
            "/api/v1/tasks/stats/summary",
            headers=auth_headers
        )
        assert response.status_code == 200
        stats = response.json()
        assert "stats" in stats
        assert stats["stats"]["total"] > 0