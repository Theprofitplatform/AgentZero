"""Task API Routes"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from ..models.task import (
    Task, TaskCreate, TaskUpdate, TaskResponse,
    TaskDetailResponse, TaskStatus, TaskPriority
)
from ..models.auth import User, UserRole
from ..services.auth import auth_service, require_role
from ..services.hive import hive_service

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    assigned_agent: Optional[str] = Query(None, description="Filter by assigned agent"),
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of tasks to return"),
    current_user: User = Depends(auth_service.get_current_user)
) -> List[TaskResponse]:
    """
    List all tasks with optional filtering.

    - **status**: Filter by task status
    - **priority**: Filter by priority (low, normal, high)
    - **assigned_agent**: Filter by assigned agent ID
    - **skip**: Number of tasks to skip for pagination
    - **limit**: Maximum number of tasks to return
    """
    tasks = await hive_service.get_tasks(
        status=status,
        priority=priority,
        assigned_agent=assigned_agent,
        skip=skip,
        limit=limit
    )
    return tasks

@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(auth_service.get_current_user)
) -> TaskDetailResponse:
    """
    Get detailed information about a specific task.

    Returns comprehensive task information including:
    - Task configuration and parameters
    - Current status and progress
    - Execution logs
    - Result or error information
    """
    task = await hive_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(auth_service.get_current_user)
) -> TaskResponse:
    """
    Create a new task.

    Submits a new task to the hive for execution. The task will be queued
    and assigned to an appropriate agent based on type and availability.
    """
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    task = Task(
        id=task_id,
        name=task_data.name,
        description=task_data.description,
        type=task_data.type,
        priority=task_data.priority,
        parameters=task_data.parameters,
        dependencies=task_data.dependencies,
        tags=task_data.tags,
        metadata=task_data.metadata,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    created_task = await hive_service.submit_task(task)
    return created_task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    update_data: TaskUpdate,
    current_user: User = Depends(auth_service.get_current_user)
) -> TaskResponse:
    """
    Update task configuration.

    Updates task properties. Note that some properties cannot be changed
    once the task has started execution.
    """
    task = await hive_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Can't update running or completed tasks (except status)
    if task.status in [TaskStatus.RUNNING, TaskStatus.COMPLETED] and \
       update_data.status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot modify {task.status.value} task"
        )

    updated_task = await hive_service.update_task(task_id, update_data)
    return updated_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_task(
    task_id: str,
    current_user: User = Depends(auth_service.get_current_user)
) -> None:
    """
    Cancel a pending or running task.

    Cancels task execution. Running tasks will be terminated gracefully
    when possible.
    """
    task = await hive_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel {task.status.value} task"
        )

    await hive_service.cancel_task(task_id)

@router.post("/{task_id}/retry")
async def retry_task(
    task_id: str,
    current_user: User = Depends(auth_service.get_current_user)
) -> TaskResponse:
    """
    Retry a failed task.

    Creates a new task instance with the same parameters as the failed task.
    """
    task = await hive_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    if task.status != TaskStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only retry failed tasks"
        )

    new_task = await hive_service.retry_task(task_id)
    return new_task

@router.get("/{task_id}/logs")
async def get_task_logs(
    task_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Number of log lines"),
    since: Optional[datetime] = Query(None, description="Get logs since this timestamp"),
    current_user: User = Depends(auth_service.get_current_user)
) -> dict:
    """
    Get execution logs for a task.

    Returns log entries generated during task execution.
    """
    task = await hive_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    logs = await hive_service.get_task_logs(task_id, limit=limit, since=since)
    return {
        "task_id": task_id,
        "logs": logs,
        "count": len(logs)
    }

@router.get("/{task_id}/result")
async def get_task_result(
    task_id: str,
    current_user: User = Depends(auth_service.get_current_user)
) -> dict:
    """
    Get the result of a completed task.

    Returns the task execution result if available.
    """
    task = await hive_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task is {task.status.value}, not completed"
        )

    return {
        "task_id": task_id,
        "result": task.result,
        "execution_time": (task.completed_at - task.started_at).total_seconds()
            if task.started_at and task.completed_at else None
    }

@router.post("/batch", response_model=List[TaskResponse])
async def create_batch_tasks(
    tasks: List[TaskCreate],
    current_user: User = Depends(auth_service.get_current_user)
) -> List[TaskResponse]:
    """
    Create multiple tasks in a single request.

    Useful for submitting related tasks or task pipelines.
    Maximum 100 tasks per batch.
    """
    if len(tasks) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 tasks per batch"
        )

    created_tasks = []
    for task_data in tasks:
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        task = Task(
            id=task_id,
            name=task_data.name,
            description=task_data.description,
            type=task_data.type,
            priority=task_data.priority,
            parameters=task_data.parameters,
            dependencies=task_data.dependencies,
            tags=task_data.tags,
            metadata=task_data.metadata,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        created_task = await hive_service.submit_task(task)
        created_tasks.append(created_task)

    return created_tasks

@router.get("/stats/summary")
async def get_task_statistics(
    since: Optional[datetime] = Query(None, description="Calculate stats since this time"),
    current_user: User = Depends(auth_service.get_current_user)
) -> dict:
    """
    Get task execution statistics.

    Returns aggregated statistics about task execution including:
    - Total tasks by status
    - Success rate
    - Average execution time
    - Task distribution by type
    """
    stats = await hive_service.get_task_statistics(since=since)
    return stats