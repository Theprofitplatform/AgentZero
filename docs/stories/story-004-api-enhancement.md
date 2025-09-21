# Story 004: REST API & WebSocket Enhancement

## Story Overview
**Epic**: API Enhancement
**Story ID**: STORY-004
**Priority**: P1 (High)
**Estimated Effort**: 8 story points
**Status**: Ready for Development
**Dependencies**: Should be developed before or in parallel with Dashboard (STORY-003)

## User Story
**As a** developer
**I want to** have a comprehensive REST API and WebSocket interface
**So that** I can integrate AgentZero with external systems and build custom interfaces

## Acceptance Criteria

### AC1: Core REST API Endpoints
- [ ] Implement complete CRUD operations for agents
- [ ] Add full task management endpoints
- [ ] Create hive coordination endpoints
- [ ] Implement metrics and monitoring endpoints
- [ ] Add system configuration endpoints
- [ ] Include health check and readiness endpoints

### AC2: Authentication & Authorization
- [ ] Implement JWT-based authentication
- [ ] Add role-based access control (Admin, User, Viewer)
- [ ] Create API key management system
- [ ] Implement token refresh mechanism
- [ ] Add session management
- [ ] Include audit logging for all API calls

### AC3: WebSocket Implementation
- [ ] Create WebSocket server with Socket.io or native WS
- [ ] Implement connection authentication
- [ ] Add event subscription system
- [ ] Support bi-directional communication
- [ ] Implement message queuing for offline clients
- [ ] Add heartbeat/ping-pong mechanism

### AC4: Rate Limiting & Security
- [ ] Implement per-user rate limiting
- [ ] Add IP-based rate limiting
- [ ] Implement request validation
- [ ] Add input sanitization
- [ ] Include CORS configuration
- [ ] Implement API versioning

### AC5: API Documentation
- [ ] Generate OpenAPI/Swagger specification
- [ ] Create interactive API explorer
- [ ] Add code examples for multiple languages
- [ ] Document WebSocket protocol
- [ ] Include authentication guide
- [ ] Add troubleshooting section

## Technical Implementation Details

### API Structure Implementation
```python
# src/api/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

app = FastAPI(
    title="AgentZero API",
    version="1.0.0",
    description="Multi-agent orchestration system API",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Dashboard URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize rate limiter
@app.on_event("startup")
async def startup():
    redis_client = await redis.from_url("redis://localhost:6379")
    await FastAPILimiter.init(redis_client)

# Security
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Verify JWT token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Agent Endpoints
```python
# src/api/routers/agents.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    status: Optional[str] = Query(None, description="Filter by status"),
    agent_type: Optional[str] = Query(None, description="Filter by type"),
    user=Depends(verify_token),
    _=Depends(RateLimiter(times=100, seconds=60))
):
    """List all registered agents with optional filtering"""
    agents = await hive.get_agents(status=status, agent_type=agent_type)
    return agents

@router.get("/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(
    agent_id: str,
    user=Depends(verify_token)
):
    """Get detailed information about a specific agent"""
    agent = await hive.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/", response_model=AgentResponse)
async def register_agent(
    agent_data: AgentCreateRequest,
    user=Depends(verify_token),
    _=Depends(require_role("admin"))
):
    """Register a new agent with the hive"""
    agent = await hive.register_agent(agent_data)
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    update_data: AgentUpdateRequest,
    user=Depends(verify_token),
    _=Depends(require_role("admin"))
):
    """Update agent configuration"""
    agent = await hive.update_agent(agent_id, update_data)
    return agent

@router.delete("/{agent_id}")
async def unregister_agent(
    agent_id: str,
    user=Depends(verify_token),
    _=Depends(require_role("admin"))
):
    """Unregister an agent from the hive"""
    await hive.unregister_agent(agent_id)
    return {"message": "Agent unregistered successfully"}

@router.post("/{agent_id}/control")
async def control_agent(
    agent_id: str,
    action: AgentControlAction,
    user=Depends(verify_token)
):
    """Control agent operations (pause, resume, restart)"""
    result = await hive.control_agent(agent_id, action)
    return result
```

### Task Endpoints
```python
# src/api/routers/tasks.py
@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreateRequest,
    user=Depends(verify_token),
    _=Depends(RateLimiter(times=50, seconds=60))
):
    """Create a new task"""
    task = Task(
        name=task_data.name,
        description=task_data.description,
        priority=task_data.priority,
        parameters=task_data.parameters,
        dependencies=task_data.dependencies
    )

    task_id = await hive.submit_task(task)
    return {"task_id": task_id, "status": "queued"}

@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    task_id: str,
    user=Depends(verify_token)
):
    """Get task details including execution status"""
    task = await hive.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    user=Depends(verify_token)
):
    """Cancel a pending or running task"""
    result = await hive.cancel_task(task_id)
    return {"message": "Task cancelled", "result": result}

@router.get("/{task_id}/logs")
async def get_task_logs(
    task_id: str,
    limit: int = Query(100, description="Number of log lines"),
    user=Depends(verify_token)
):
    """Get execution logs for a task"""
    logs = await hive.get_task_logs(task_id, limit=limit)
    return {"task_id": task_id, "logs": logs}
```

### WebSocket Implementation
```python
# src/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        self.subscriptions.pop(client_id, None)

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, event_type: str, data: dict):
        """Broadcast to all clients subscribed to this event type"""
        message = {"type": event_type, "data": data}
        for client_id, subscriptions in self.subscriptions.items():
            if event_type in subscriptions or "*" in subscriptions:
                await self.send_message(client_id, message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT token")
):
    # Verify token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        client_id = payload["sub"]
    except:
        await websocket.close(code=1008)  # Policy violation
        return

    await manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_json()

            # Handle different message types
            if data["type"] == "subscribe":
                events = data.get("events", ["*"])
                for event in events:
                    manager.subscriptions[client_id].add(event)
                await manager.send_message(client_id, {
                    "type": "subscribed",
                    "events": events
                })

            elif data["type"] == "unsubscribe":
                events = data.get("events", [])
                for event in events:
                    manager.subscriptions[client_id].discard(event)

            elif data["type"] == "ping":
                await manager.send_message(client_id, {"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(client_id)

# Event emitter for system events
async def emit_event(event_type: str, data: dict):
    """Emit event to all subscribed WebSocket clients"""
    await manager.broadcast(event_type, data)

# Hook into hive events
hive.on_agent_registered = lambda agent: emit_event("agent.registered", agent.dict())
hive.on_task_completed = lambda task: emit_event("task.completed", task.dict())
hive.on_agent_status_changed = lambda agent: emit_event("agent.status_changed", agent.dict())
```

### Authentication Implementation
```python
# src/api/auth.py
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(hours=1))
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

@router.post("/api/v1/auth/login")
async def login(credentials: LoginRequest):
    # Verify credentials (implement your user verification)
    user = await verify_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = auth_service.create_access_token(
        data={"sub": user.id, "role": user.role}
    )
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user.id}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

### Rate Limiting Configuration
```python
# src/api/middleware.py
from fastapi_limiter.depends import RateLimiter

# Different rate limits for different operations
rate_limits = {
    "read": RateLimiter(times=100, seconds=60),  # 100 requests per minute
    "write": RateLimiter(times=20, seconds=60),   # 20 writes per minute
    "heavy": RateLimiter(times=5, seconds=60),    # 5 heavy operations per minute
}

# Role-based rate limits
def get_rate_limit(role: str, operation: str):
    multipliers = {
        "admin": 2.0,
        "user": 1.0,
        "viewer": 0.5
    }

    base_limit = rate_limits[operation]
    multiplier = multipliers.get(role, 1.0)

    return RateLimiter(
        times=int(base_limit.times * multiplier),
        seconds=base_limit.seconds
    )
```

### OpenAPI Documentation
```python
# Auto-generated by FastAPI, customize with:
app = FastAPI(
    title="AgentZero API",
    description="""
    ## Overview
    AgentZero API provides comprehensive access to the multi-agent orchestration system.

    ## Authentication
    All endpoints require JWT authentication. Obtain a token via `/api/v1/auth/login`.

    ## Rate Limiting
    API calls are rate-limited based on user role and operation type.

    ## WebSocket
    Real-time updates available via WebSocket at `/ws`.
    """,
    version="1.0.0",
    terms_of_service="https://agentzero.com/terms",
    contact={
        "name": "AgentZero Support",
        "email": "support@agentzero.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Add response examples
@router.get("/agents", responses={
    200: {
        "description": "Successful response",
        "content": {
            "application/json": {
                "example": [
                    {
                        "agent_id": "agent-123",
                        "name": "ResearchAgent-1",
                        "status": "idle",
                        "capabilities": ["web_search", "data_extraction"]
                    }
                ]
            }
        }
    }
})
```

## Testing Requirements

### Unit Tests
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}

def test_list_agents(client, auth_headers):
    response = client.get("/api/v1/agents", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_task(client, auth_headers):
    task_data = {
        "name": "Test Task",
        "description": "Test Description",
        "priority": "medium"
    }
    response = client.post("/api/v1/tasks", json=task_data, headers=auth_headers)
    assert response.status_code == 200
    assert "task_id" in response.json()

def test_rate_limiting(client, auth_headers):
    # Exceed rate limit
    for _ in range(101):
        response = client.get("/api/v1/agents", headers=auth_headers)

    assert response.status_code == 429  # Too Many Requests

def test_websocket_connection():
    with client.websocket_connect(f"/ws?token={create_test_token()}") as websocket:
        websocket.send_json({"type": "ping"})
        data = websocket.receive_json()
        assert data["type"] == "pong"
```

## Definition of Done

- [ ] All REST endpoints implemented and tested
- [ ] Authentication and authorization working
- [ ] WebSocket server stable with reconnection support
- [ ] Rate limiting functioning correctly
- [ ] API documentation complete and accurate
- [ ] All tests passing (>90% coverage)
- [ ] No security vulnerabilities (OWASP scan clean)
- [ ] Performance benchmarks met (<200ms p95 latency)
- [ ] Deployment ready with environment configuration

## Implementation Notes

### Security Considerations
- Use HTTPS in production
- Implement request signing for sensitive operations
- Add API key rotation mechanism
- Log all authentication attempts
- Implement IP allowlisting for admin operations
- Use prepared statements for database queries

### Performance Optimization
- Implement response caching for read operations
- Use connection pooling for database
- Add pagination for list endpoints
- Implement field filtering for responses
- Use compression for large responses
- Consider GraphQL for complex queries

## Dependencies
Add to `requirements.txt`:
```txt
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
fastapi-limiter>=0.1.5
websockets>=11.0
```

## Related Documents
- PRD: `/docs/prd.md#FR-4`
- Architecture: `/docs/architecture.md#2.4`
- Dashboard Story: STORY-003

## Post-Implementation Tasks
- Add GraphQL endpoint for complex queries
- Implement API versioning strategy
- Add response caching with Redis
- Create SDK libraries (Python, JS, Go)
- Implement webhook system for events
- Add batch operations support

---
**Created**: 2025-09-21
**Last Updated**: 2025-09-21
**Author**: BMad Workflow System