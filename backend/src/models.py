"""SQLModel database models for User and Task entities."""
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum


class User(SQLModel, table=True):
    """User model for authentication and task ownership."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    display_name: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="owner")


class Task(SQLModel, table=True):
    """Task model for todo items."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    owner: Optional[User] = Relationship(back_populates="tasks")


# ============================================================================
# Phase 3: AI-Powered Task Assistant Models
# ============================================================================

class MessageType(str, Enum):
    """Enum for chat message types."""
    USER_MESSAGE = "user_message"
    AI_RESPONSE = "ai_response"
    SYSTEM_NOTIFICATION = "system_notification"


class ActionType(str, Enum):
    """Enum for task action types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    COMPLETE = "complete"
    QUERY = "query"


class ConfirmationStatus(str, Enum):
    """Enum for action confirmation status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class ExecutedStatus(str, Enum):
    """Enum for action executed status."""
    NOT_EXECUTED = "not_executed"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"


class AITone(str, Enum):
    """Enum for AI tone preferences."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    CONCISE = "concise"


class ChatSession(SQLModel, table=True):
    """Chat session between user and AI assistant."""

    __tablename__ = "chat_sessions"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    context_summary: Optional[str] = Field(default=None)
    message_count: int = Field(default=0)


class ChatMessage(SQLModel, table=True):
    """Individual message in a conversation."""

    __tablename__ = "chat_messages"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    session_id: UUID = Field(foreign_key="chat_sessions.id", index=True)
    content: str = Field(min_length=1)
    message_type: MessageType = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)
    message_metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))


class TaskAction(SQLModel, table=True):
    """AI-interpreted action on a task."""

    __tablename__ = "task_actions"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    session_id: Optional[UUID] = Field(default=None, foreign_key="chat_sessions.id")
    message_id: Optional[UUID] = Field(default=None, foreign_key="chat_messages.id")
    user_id: int = Field(foreign_key="users.id", index=True)
    action_type: ActionType = Field()
    extracted_params: dict = Field(default_factory=dict, sa_column=Column(JSON))
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confirmation_status: ConfirmationStatus = Field(default=ConfirmationStatus.PENDING)
    executed_status: ExecutedStatus = Field(default=ExecutedStatus.NOT_EXECUTED)
    task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
    error_message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = Field(default=None)
    executed_at: Optional[datetime] = Field(default=None)


class UserPreferences(SQLModel, table=True):
    """AI personalization settings and learned user patterns."""

    __tablename__ = "user_preferences"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)
    preferred_language: str = Field(default="en", max_length=10)
    ai_tone: AITone = Field(default=AITone.PROFESSIONAL)
    enable_proactive_suggestions: bool = Field(default=False)
    learned_shortcuts: dict = Field(default_factory=dict, sa_column=Column(JSON))
    rate_limit_override: Optional[int] = Field(default=None, gt=0)
    ai_features_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AIContext(SQLModel, table=True):
    """Persistent context for AI interactions across sessions."""

    __tablename__ = "ai_contexts"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)
    conversation_summary: Optional[str] = Field(default=None)
    user_patterns: dict = Field(default_factory=dict, sa_column=Column(JSON))
    total_messages: int = Field(default=0)
    total_sessions: int = Field(default=0)
    average_session_length: float = Field(default=0.0)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
