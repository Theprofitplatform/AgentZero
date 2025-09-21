"""AgentZero REST API & WebSocket Server"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from contextlib import asynccontextmanager

from .config import settings
from .routers import agents, tasks, auth
from .websocket import websocket_endpoint, manager
from .services.hive import hive_service

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    print("🚀 Starting AgentZero API...")

    # Start background tasks
    asyncio.create_task(manager.heartbeat_check())

    # Initialize demo data (remove in production)
    await initialize_demo_data()

    print(f"✅ API ready at http://localhost:{settings.port}")
    print(f"📚 Documentation at http://localhost:{settings.port}/docs")

    yield

    # Shutdown
    print("👋 Shutting down AgentZero API...")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## AgentZero API

    Multi-agent orchestration system providing comprehensive REST API and WebSocket interface.

    ### Features
    - 🤖 Agent management and monitoring
    - 📋 Task creation and orchestration
    - 🔐 JWT-based authentication
    - 🔌 Real-time WebSocket updates
    - 📊 Performance metrics and analytics

    ### Authentication
    All endpoints (except `/docs` and `/health`) require JWT authentication.
    Obtain a token via `/api/v1/auth/login`.

    Default credentials for testing:
    - Username: `admin`, Password: `secret` (Admin role)
    - Username: `user`, Password: `secret` (User role)

    ### WebSocket
    Connect to `/ws?token=<jwt_token>` for real-time updates.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(tasks.router)

# WebSocket endpoint
app.add_websocket_route("/ws", websocket_endpoint)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "agents": len(hive_service.agents),
        "tasks": len(hive_service.tasks)
    }

# Ready check endpoint
@app.get("/ready")
async def ready_check():
    """Readiness check for deployment"""
    # Add any readiness checks here
    return {"ready": True}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "type": type(exc).__name__
        }
    )

# Initialize demo data
async def initialize_demo_data():
    """Create some demo agents and tasks for testing"""
    from .models.agent import Agent, AgentType, AgentStatus
    from .models.task import Task, TaskType, TaskPriority
    from datetime import datetime

    # Create demo agents
    demo_agents = [
        Agent(
            id="agent-demo-001",
            agent_id="agent-demo-001",
            name="PlanningAgent-1",
            type=AgentType.PLANNING,
            status=AgentStatus.IDLE,
            capabilities=["task_planning", "resource_allocation"],
            cpu_usage=15.5,
            memory_usage=23.8,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            last_heartbeat=datetime.utcnow(),
            registered_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        ),
        Agent(
            id="agent-demo-002",
            agent_id="agent-demo-002",
            name="ExecutionAgent-1",
            type=AgentType.EXECUTION,
            status=AgentStatus.WORKING,
            current_task="task-demo-001",
            capabilities=["task_execution", "parallel_processing"],
            cpu_usage=45.2,
            memory_usage=38.4,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            last_heartbeat=datetime.utcnow(),
            registered_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        ),
        Agent(
            id="agent-demo-003",
            agent_id="agent-demo-003",
            name="ResearchAgent-1",
            type=AgentType.RESEARCH,
            status=AgentStatus.IDLE,
            capabilities=["web_search", "data_extraction", "summarization"],
            cpu_usage=8.3,
            memory_usage=15.6,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            last_heartbeat=datetime.utcnow(),
            registered_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        ),
    ]

    for agent in demo_agents:
        await hive_service.register_agent(agent)

    # Create demo tasks
    demo_tasks = [
        Task(
            id="task-demo-001",
            name="Research Market Trends",
            description="Research and analyze current market trends in AI",
            type=TaskType.RESEARCH,
            priority=TaskPriority.HIGH,
            status="running",
            assigned_agent="agent-demo-002",
            assigned_to="ExecutionAgent-1",
            progress=65.0,
            parameters={"keywords": ["AI", "market", "trends"]},
            tags=["research", "ai", "market"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            started_at=datetime.utcnow()
        ),
        Task(
            id="task-demo-002",
            name="Generate Weekly Report",
            description="Generate comprehensive weekly activity report",
            type=TaskType.GENERAL,
            priority=TaskPriority.NORMAL,
            status="pending",
            parameters={"format": "pdf", "include_graphs": True},
            tags=["reporting", "weekly"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Task(
            id="task-demo-003",
            name="Code Review",
            description="Review and optimize authentication module",
            type=TaskType.CODE_GENERATION,
            priority=TaskPriority.LOW,
            status="completed",
            progress=100.0,
            result={"files_reviewed": 12, "issues_found": 3},
            parameters={"module": "authentication", "depth": "thorough"},
            tags=["code", "review", "security"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        ),
    ]

    for task in demo_tasks:
        hive_service.tasks[task.id] = task

    print("✅ Demo data initialized")

def run_server():
    """Run the API server"""
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )

if __name__ == "__main__":
    run_server()