"""Agent API Routes"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from ..models.agent import (
    Agent, AgentCreate, AgentUpdate, AgentResponse,
    AgentDetailResponse, AgentControlRequest, AgentStatus
)
from ..models.auth import User, UserRole
from ..services.auth import auth_service, require_role
from ..services.hive import hive_service

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    status: Optional[AgentStatus] = Query(None, description="Filter by status"),
    agent_type: Optional[str] = Query(None, description="Filter by type"),
    skip: int = Query(0, ge=0, description="Number of agents to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of agents to return"),
    current_user: User = Depends(auth_service.get_current_user)
) -> List[AgentResponse]:
    """
    List all registered agents with optional filtering.

    - **status**: Filter by agent status (idle, working, thinking, error, terminated)
    - **agent_type**: Filter by agent type (planning, execution, research, code)
    - **skip**: Number of agents to skip for pagination
    - **limit**: Maximum number of agents to return
    """
    agents = await hive_service.get_agents(
        status=status,
        agent_type=agent_type,
        skip=skip,
        limit=limit
    )
    return agents

@router.get("/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(
    agent_id: str,
    current_user: User = Depends(auth_service.get_current_user)
) -> AgentDetailResponse:
    """
    Get detailed information about a specific agent.

    Returns comprehensive agent information including:
    - Basic agent details
    - Current status and metrics
    - Recent logs
    - Task history
    """
    agent = await hive_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    return agent

@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def register_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> AgentResponse:
    """
    Register a new agent with the hive.

    Requires ADMIN role. Creates and registers a new agent with the specified
    configuration and capabilities.
    """
    agent_id = f"agent-{uuid.uuid4().hex[:8]}"
    agent = Agent(
        id=agent_id,
        agent_id=agent_id,
        name=agent_data.name,
        type=agent_data.type,
        capabilities=agent_data.capabilities,
        metadata=agent_data.metadata,
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow(),
        last_heartbeat=datetime.utcnow(),
        registered_at=datetime.utcnow(),
        last_updated=datetime.utcnow()
    )

    registered_agent = await hive_service.register_agent(agent)
    return registered_agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    update_data: AgentUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> AgentResponse:
    """
    Update agent configuration.

    Requires ADMIN role. Updates the specified agent's configuration,
    status, or capabilities.
    """
    agent = await hive_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    updated_agent = await hive_service.update_agent(agent_id, update_data)
    return updated_agent

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_agent(
    agent_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> None:
    """
    Unregister an agent from the hive.

    Requires ADMIN role. Removes the agent from the hive and
    terminates any running tasks.
    """
    agent = await hive_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    await hive_service.unregister_agent(agent_id)

@router.post("/{agent_id}/control")
async def control_agent(
    agent_id: str,
    control_request: AgentControlRequest,
    current_user: User = Depends(auth_service.get_current_user)
) -> dict:
    """
    Control agent operations.

    Send control commands to an agent:
    - **pause**: Pause agent execution
    - **resume**: Resume agent execution
    - **restart**: Restart the agent
    - **terminate**: Terminate the agent
    """
    agent = await hive_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    # Only admins can terminate agents
    if control_request.action == "terminate" and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can terminate agents"
        )

    result = await hive_service.control_agent(agent_id, control_request.action)
    return {
        "agent_id": agent_id,
        "action": control_request.action,
        "status": "success",
        "result": result
    }

@router.get("/{agent_id}/metrics")
async def get_agent_metrics(
    agent_id: str,
    current_user: User = Depends(auth_service.get_current_user)
) -> dict:
    """
    Get performance metrics for a specific agent.

    Returns detailed metrics including:
    - Task completion statistics
    - Resource usage
    - Performance indicators
    """
    agent = await hive_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    metrics = await hive_service.get_agent_metrics(agent_id)
    return metrics

@router.get("/{agent_id}/logs")
async def get_agent_logs(
    agent_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Number of log lines to return"),
    since: Optional[datetime] = Query(None, description="Get logs since this timestamp"),
    current_user: User = Depends(auth_service.get_current_user)
) -> dict:
    """
    Get execution logs for an agent.

    Returns recent log entries from the agent's execution.
    """
    agent = await hive_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    logs = await hive_service.get_agent_logs(agent_id, limit=limit, since=since)
    return {
        "agent_id": agent_id,
        "logs": logs,
        "count": len(logs)
    }

@router.post("/{agent_id}/heartbeat")
async def agent_heartbeat(
    agent_id: str,
    current_user: User = Depends(auth_service.get_current_user)
) -> dict:
    """
    Update agent heartbeat.

    Agents should call this endpoint periodically to indicate they are alive.
    """
    agent = await hive_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    await hive_service.update_heartbeat(agent_id)
    return {
        "agent_id": agent_id,
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }