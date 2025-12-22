"""Task management API endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional
import html
import logging
import asyncio

from ..models import Task
from ..db import get_db_session
from ..auth.middleware import get_current_user_id, validate_user_id_match
from ..services.ai.chat_service import ChatService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    """Create task request model."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

    @field_validator('title')
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        """Sanitize title to prevent XSS attacks."""
        return html.escape(v.strip())

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description to prevent XSS attacks."""
        if v is None:
            return None
        return html.escape(v.strip())


class UpdateTaskRequest(BaseModel):
    """Update task request model."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

    @field_validator('title')
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize title to prevent XSS attacks."""
        if v is None:
            return None
        return html.escape(v.strip())

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description to prevent XSS attacks."""
        if v is None:
            return None
        return html.escape(v.strip())


class TaskResponse(BaseModel):
    """Task response model."""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: str
    updated_at: str


@router.get("/{user_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    List all tasks for the authenticated user with pagination.

    - Requires JWT authentication
    - Validates user_id matches authenticated user
    - Returns tasks in reverse chronological order
    - Supports pagination via skip and limit parameters
    - Default limit is 100 tasks
    """
    validate_user_id_match(user_id, current_user_id)

    # Validate pagination parameters
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip parameter must be non-negative"
        )
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit parameter must be between 1 and 1000"
        )

    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    tasks = session.exec(statement).all()

    return [
        TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
        )
        for task in tasks
    ]


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: int,
    request: CreateTaskRequest,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Create a new task.

    - Requires JWT authentication
    - Validates user_id matches authenticated user
    - Title is required (max 200 chars)
    - Description is optional (max 1000 chars)
    """
    validate_user_id_match(user_id, current_user_id)

    task = Task(
        user_id=user_id,
        title=request.title,
        description=request.description,
        is_completed=False,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    logger.info(f"Task created: ID={task.id}, User={user_id}, Title='{task.title}'")

    # Emit SSE event for real-time sync (T078)
    task_data = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }
    try:
        asyncio.create_task(
            ChatService.broadcast_event(user_id, "task_created", task_data)
        )
    except Exception as e:
        # Don't fail the request if SSE broadcast fails
        logger.warning(f"Failed to broadcast task_created SSE event: {str(e)}")

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: int,
    task_id: int,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get a specific task by ID.

    - Requires JWT authentication
    - Validates user_id matches authenticated user
    - Returns 404 if task doesn't exist or doesn't belong to user
    """
    validate_user_id_match(user_id, current_user_id)

    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: int,
    task_id: int,
    request: UpdateTaskRequest,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Update a task's title and/or description.

    - Requires JWT authentication
    - Validates user_id matches authenticated user
    - Returns 404 if task doesn't exist or doesn't belong to user
    """
    validate_user_id_match(user_id, current_user_id)

    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update fields if provided
    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description

    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    logger.info(f"Task updated: ID={task_id}, User={user_id}")

    # Emit SSE event for real-time sync (T077)
    task_data = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }
    try:
        asyncio.create_task(
            ChatService.broadcast_event(user_id, "task_updated", task_data)
        )
    except Exception as e:
        # Don't fail the request if SSE broadcast fails
        logger.warning(f"Failed to broadcast task_updated SSE event: {str(e)}")

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: int,
    task_id: int,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Delete a task.

    - Requires JWT authentication
    - Validates user_id matches authenticated user
    - Returns 404 if task doesn't exist or doesn't belong to user
    """
    validate_user_id_match(user_id, current_user_id)

    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    logger.info(f"Task deleted: ID={task_id}, User={user_id}")

    # Emit SSE event for real-time sync (T079) - before deletion
    task_data = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
    }
    try:
        asyncio.create_task(
            ChatService.broadcast_event(user_id, "task_deleted", task_data)
        )
    except Exception as e:
        # Don't fail the request if SSE broadcast fails
        logger.warning(f"Failed to broadcast task_deleted SSE event: {str(e)}")

    session.delete(task)
    session.commit()


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    user_id: int,
    task_id: int,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Toggle task completion status.

    - Requires JWT authentication
    - Validates user_id matches authenticated user
    - Returns 404 if task doesn't exist or doesn't belong to user
    """
    validate_user_id_match(user_id, current_user_id)

    task = session.get(Task, task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task.is_completed = not task.is_completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    logger.info(f"Task completion toggled: ID={task_id}, User={user_id}, Completed={task.is_completed}")

    # Emit SSE event for real-time sync (T077)
    task_data = {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }
    try:
        asyncio.create_task(
            ChatService.broadcast_event(user_id, "task_updated", task_data)
        )
    except Exception as e:
        # Don't fail the request if SSE broadcast fails
        logger.warning(f"Failed to broadcast task_updated SSE event: {str(e)}")

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )
