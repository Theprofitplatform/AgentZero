"""Load and Performance Testing Suite"""
import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from httpx import AsyncClient

from src.core.hive_coordinator import HiveCoordinator
from src.agents.execution_agent import ExecutionAgent
from src.api.models.task import Task, TaskType, TaskPriority

class PerformanceMetrics:
    """Class to collect and analyze performance metrics"""

    def __init__(self):
        self.response_times: List[float] = []
        self.throughput_data: List[int] = []
        self.error_count = 0
        self.success_count = 0
        self.start_time = None
        self.end_time = None

    def add_response_time(self, duration: float):
        """Add a response time measurement"""
        self.response_times.append(duration)

    def add_throughput(self, count: int):
        """Add throughput data point"""
        self.throughput_data.append(count)

    def record_success(self):
        """Record successful operation"""
        self.success_count += 1

    def record_error(self):
        """Record failed operation"""
        self.error_count += 1

    def start(self):
        """Start timing"""
        self.start_time = time.time()

    def stop(self):
        """Stop timing"""
        self.end_time = time.time()

    def get_statistics(self) -> Dict[str, Any]:
        """Calculate and return performance statistics"""
        if not self.response_times:
            return {}

        duration = (self.end_time or time.time()) - (self.start_time or 0)

        return {
            "duration": duration,
            "total_requests": len(self.response_times),
            "success_count": self.success_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / (self.success_count + self.error_count) if (self.success_count + self.error_count) > 0 else 0,
            "avg_response_time": statistics.mean(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "p50_response_time": statistics.median(self.response_times),
            "p95_response_time": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) > 20 else max(self.response_times),
            "p99_response_time": statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) > 100 else max(self.response_times),
            "throughput": (self.success_count + self.error_count) / duration if duration > 0 else 0
        }

@pytest.mark.asyncio
class TestLoadPerformance:
    """Test system performance under load"""

    async def test_api_endpoint_load(self):
        """Test API endpoints under concurrent load"""
        metrics = PerformanceMetrics()
        base_url = "http://localhost:8000"

        # Get authentication token
        async with AsyncClient(base_url=base_url) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"username": "admin", "password": "secret"}
            )
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

        async def make_request(session: aiohttp.ClientSession, endpoint: str) -> float:
            """Make a single request and measure time"""
            start = time.time()
            try:
                async with session.get(f"{base_url}{endpoint}", headers=headers) as response:
                    await response.json()
                    duration = time.time() - start
                    metrics.add_response_time(duration)
                    metrics.record_success()
                    return duration
            except Exception as e:
                metrics.record_error()
                return time.time() - start

        # Test parameters
        concurrent_users = 100
        requests_per_user = 10
        endpoints = [
            "/api/v1/agents",
            "/api/v1/tasks",
            "/api/v1/agents/stats",
            "/api/v1/tasks/stats/summary"
        ]

        metrics.start()

        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(concurrent_users):
                for _ in range(requests_per_user):
                    endpoint = endpoints[len(tasks) % len(endpoints)]
                    tasks.append(make_request(session, endpoint))

            await asyncio.gather(*tasks)

        metrics.stop()

        # Analyze results
        stats = metrics.get_statistics()

        # Performance assertions
        assert stats["avg_response_time"] < 0.5  # Average response under 500ms
        assert stats["p95_response_time"] < 1.0  # 95th percentile under 1s
        assert stats["error_rate"] < 0.05  # Less than 5% errors
        assert stats["throughput"] > 50  # At least 50 requests per second

    async def test_agent_scalability(self):
        """Test system scalability with increasing number of agents"""
        metrics = PerformanceMetrics()
        hive = HiveCoordinator()

        agent_counts = [10, 50, 100, 200]
        performance_by_scale = {}

        for count in agent_counts:
            scale_metrics = PerformanceMetrics()
            scale_metrics.start()

            # Create and register agents
            agents = []
            for i in range(count):
                agent = ExecutionAgent(
                    agent_id=f"scale-{i:04d}",
                    name=f"ScaleAgent-{i}",
                    capabilities=["execution"]
                )

                start = time.time()
                await hive.register_agent(agent)
                scale_metrics.add_response_time(time.time() - start)
                scale_metrics.record_success()
                agents.append(agent)

            # Submit tasks
            for i in range(count * 2):  # 2 tasks per agent
                task = {
                    "id": f"task-{count}-{i:04d}",
                    "name": f"Task {i}",
                    "type": "execution",
                    "priority": "normal"
                }

                start = time.time()
                await hive.submit_task(task)
                scale_metrics.add_response_time(time.time() - start)

            scale_metrics.stop()
            performance_by_scale[count] = scale_metrics.get_statistics()

            # Cleanup
            for agent in agents:
                await hive.unregister_agent(agent.agent_id)

        # Verify scalability
        # Response time should not degrade significantly with scale
        degradation = (
            performance_by_scale[200]["avg_response_time"] /
            performance_by_scale[10]["avg_response_time"]
        )
        assert degradation < 3.0  # Less than 3x degradation at 20x scale

    async def test_task_throughput(self):
        """Test task processing throughput"""
        metrics = PerformanceMetrics()
        hive = HiveCoordinator()

        # Setup agents
        agent_count = 20
        agents = []
        for i in range(agent_count):
            agent = ExecutionAgent(
                agent_id=f"throughput-{i:03d}",
                name=f"ThroughputAgent-{i}",
                capabilities=["execution"]
            )
            await hive.register_agent(agent)
            agents.append(agent)

        # Submit tasks
        task_count = 1000
        metrics.start()

        submission_tasks = []
        for i in range(task_count):
            task = {
                "id": f"throughput-{i:04d}",
                "name": f"Throughput Task {i}",
                "type": "execution",
                "priority": "normal",
                "estimated_duration": 0.1  # 100ms per task
            }
            submission_tasks.append(hive.submit_task(task))

        await asyncio.gather(*submission_tasks)

        # Process tasks
        processed_count = 0
        start_processing = time.time()

        while processed_count < task_count and (time.time() - start_processing) < 30:
            processing_tasks = []

            for agent in agents:
                if agent.current_task is None:
                    task = await hive.get_next_task_for_agent(agent.agent_id)
                    if task:
                        agent.current_task = task

                if agent.current_task:
                    # Simulate processing
                    await asyncio.sleep(0.01)  # Reduced for testing

                    await hive.complete_task(
                        agent.current_task["id"],
                        {"status": "completed"}
                    )
                    processed_count += 1
                    agent.current_task = None
                    metrics.record_success()

            metrics.add_throughput(processed_count)

        metrics.stop()

        # Calculate throughput
        stats = metrics.get_statistics()
        actual_throughput = processed_count / stats["duration"]

        # Performance assertions
        assert actual_throughput > 50  # At least 50 tasks per second
        assert processed_count >= task_count * 0.95  # At least 95% completion

    async def test_concurrent_websocket_connections(self):
        """Test WebSocket server with concurrent connections"""
        metrics = PerformanceMetrics()
        ws_url = "ws://localhost:8000/ws"
        connection_count = 100
        messages_per_connection = 10

        async def websocket_client(client_id: int):
            """Simulate WebSocket client"""
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(ws_url) as ws:
                        # Send messages
                        for i in range(messages_per_connection):
                            start = time.time()
                            await ws.send_json({
                                "type": "ping",
                                "client_id": client_id,
                                "message_id": i
                            })

                            # Wait for response
                            response = await ws.receive_json()
                            duration = time.time() - start
                            metrics.add_response_time(duration)
                            metrics.record_success()

                        await ws.close()
            except Exception as e:
                metrics.record_error()

        metrics.start()

        # Create concurrent connections
        tasks = []
        for i in range(connection_count):
            tasks.append(websocket_client(i))

        await asyncio.gather(*tasks, return_exceptions=True)

        metrics.stop()

        # Analyze results
        stats = metrics.get_statistics()

        # Performance assertions
        assert stats["error_rate"] < 0.1  # Less than 10% connection errors
        assert stats["avg_response_time"] < 0.1  # Average response under 100ms
        assert stats["throughput"] > 100  # At least 100 messages per second

    async def test_memory_stability(self):
        """Test memory usage stability under sustained load"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        hive = HiveCoordinator()

        # Initial memory baseline
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create agents
        agents = []
        for i in range(50):
            agent = ExecutionAgent(
                agent_id=f"memory-{i:03d}",
                name=f"MemoryAgent-{i}",
                capabilities=["execution"]
            )
            await hive.register_agent(agent)
            agents.append(agent)

        # Run sustained load
        iterations = 100
        memory_samples = []

        for iteration in range(iterations):
            # Submit batch of tasks
            for i in range(20):
                task = {
                    "id": f"mem-{iteration}-{i:03d}",
                    "name": f"Memory Task {iteration}-{i}",
                    "type": "execution",
                    "priority": "normal"
                }
                await hive.submit_task(task)

            # Process tasks
            for agent in agents:
                if task := await hive.get_next_task_for_agent(agent.agent_id):
                    await hive.complete_task(task["id"], {"status": "completed"})

            # Sample memory
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_samples.append(current_memory)

            # Brief pause
            await asyncio.sleep(0.1)

        # Analyze memory usage
        max_memory = max(memory_samples)
        avg_memory = statistics.mean(memory_samples)
        memory_growth = max_memory - initial_memory

        # Memory stability assertions
        assert memory_growth < 100  # Less than 100MB growth
        assert avg_memory < initial_memory + 50  # Average within 50MB of baseline

    async def test_database_query_performance(self):
        """Test database query performance under load"""
        metrics = PerformanceMetrics()
        hive = HiveCoordinator()

        # Populate with test data
        for i in range(1000):
            task = {
                "id": f"db-task-{i:04d}",
                "name": f"DB Task {i}",
                "type": "execution",
                "priority": ["low", "normal", "high", "critical"][i % 4],
                "tags": [f"tag-{i % 10}", f"category-{i % 5}"]
            }
            await hive.submit_task(task)

        # Test query performance
        query_types = [
            ("filter_by_priority", {"priority": "high"}),
            ("filter_by_status", {"status": "pending"}),
            ("filter_by_tags", {"tags": ["tag-5"]}),
            ("pagination", {"skip": 100, "limit": 50}),
            ("sorting", {"sort_by": "created_at", "order": "desc"})
        ]

        metrics.start()

        for query_name, params in query_types:
            for _ in range(100):  # 100 queries of each type
                start = time.time()
                try:
                    result = await hive.query_tasks(**params)
                    duration = time.time() - start
                    metrics.add_response_time(duration)
                    metrics.record_success()
                except Exception:
                    metrics.record_error()

        metrics.stop()

        # Analyze results
        stats = metrics.get_statistics()

        # Query performance assertions
        assert stats["avg_response_time"] < 0.05  # Average query under 50ms
        assert stats["p99_response_time"] < 0.2  # 99th percentile under 200ms
        assert stats["error_rate"] == 0  # No query errors