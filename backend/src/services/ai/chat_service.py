"""Chat session and message management service."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
import asyncio
import json
from ...models import ChatSession, ChatMessage, TaskAction, MessageType, ActionType, ConfirmationStatus, ExecutedStatus
from ...db import get_session


# Global SSE connection manager
# Maps user_id -> list of asyncio.Queue objects for SSE clients
_sse_connections: Dict[int, List[asyncio.Queue]] = {}


class ChatService:
    """
    Service for managing chat sessions and messages.

    Handles session lifecycle, message persistence, and real-time updates.
    """

    def __init__(self, user_id: int, db_session: Optional[Session] = None):
        """
        Initialize chat service for a specific user.

        Args:
            user_id: User ID for session isolation
            db_session: Optional database session (for dependency injection)
        """
        self.user_id = user_id
        self.db_session = db_session

    async def get_or_create_session(
        self,
        session_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get existing session or create new one.

        Args:
            session_id: Optional existing session ID to resume

        Returns:
            Dictionary with session details:
            {
                "id": UUID,
                "user_id": int,
                "started_at": datetime,
                "last_activity_at": datetime,
                "is_active": bool,
                "message_count": int
            }
        """
        # Use provided session or create a context manager
        if self.db_session:
            return await self._get_or_create_session_impl(session_id, self.db_session)
        else:
            with get_session() as db:
                return await self._get_or_create_session_impl(session_id, db)

    async def _get_or_create_session_impl(
        self,
        session_id: Optional[UUID],
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of get_or_create_session."""
        if session_id:
            # Try to find existing session
            statement = select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == self.user_id,
                ChatSession.is_active == True
            )
            session = db.exec(statement).first()

            if session:
                # Update last activity
                session.last_activity_at = datetime.utcnow()
                db.add(session)
                db.commit()
                db.refresh(session)

                return {
                    "id": str(session.id),
                    "user_id": session.user_id,
                    "started_at": session.started_at.isoformat(),
                    "last_activity_at": session.last_activity_at.isoformat(),
                    "is_active": session.is_active,
                    "message_count": session.message_count
                }

        # Create new session if not found or session_id not provided
        new_session = ChatSession(
            user_id=self.user_id,
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow(),
            is_active=True,
            message_count=0
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return {
            "id": str(new_session.id),
            "user_id": new_session.user_id,
            "started_at": new_session.started_at.isoformat(),
            "last_activity_at": new_session.last_activity_at.isoformat(),
            "is_active": new_session.is_active,
            "message_count": new_session.message_count
        }

    async def save_message(
        self,
        session_id: UUID,
        content: str,
        message_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save a chat message to the database.

        Args:
            session_id: Session this message belongs to
            content: Message text
            message_type: "user_message", "ai_response", or "system_notification"
            metadata: Optional metadata (AI confidence, token count, etc.)

        Returns:
            Dictionary with saved message:
            {
                "id": UUID,
                "session_id": UUID,
                "content": str,
                "message_type": str,
                "created_at": datetime,
                "metadata": dict
            }
        """
        # Use provided session or create a context manager
        if self.db_session:
            return await self._save_message_impl(session_id, content, message_type, metadata, self.db_session)
        else:
            with get_session() as db:
                return await self._save_message_impl(session_id, content, message_type, metadata, db)

    async def _save_message_impl(
        self,
        session_id: UUID,
        content: str,
        message_type: str,
        metadata: Optional[Dict[str, Any]],
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of save_message."""
        # Convert string message_type to enum
        msg_type_enum = MessageType(message_type)

        # Create message record
        message = ChatMessage(
            user_id=self.user_id,
            session_id=session_id,
            content=content,
            message_type=msg_type_enum,
            created_at=datetime.utcnow(),
            message_metadata=metadata or {}
        )

        db.add(message)

        # Update session message count and last activity
        statement = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == self.user_id
        )
        session = db.exec(statement).first()

        if session:
            session.message_count += 1
            session.last_activity_at = datetime.utcnow()
            db.add(session)

        db.commit()
        db.refresh(message)

        return {
            "id": str(message.id),
            "session_id": str(message.session_id),
            "user_id": message.user_id,
            "content": message.content,
            "message_type": message.message_type.value,
            "created_at": message.created_at.isoformat(),
            "metadata": message.message_metadata
        }

    async def get_session_messages(
        self,
        session_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve messages for a session.

        Args:
            session_id: Session ID
            limit: Maximum number of messages to retrieve (default 50)

        Returns:
            List of message dictionaries ordered by created_at
        """
        # STUB: Implementation in Phase 3 US1
        raise NotImplementedError(
            "ChatService.get_session_messages() will be implemented in Phase 3 US1"
        )

    async def create_pending_action(
        self,
        session_id: UUID,
        message_id: UUID,
        action_type: str,
        extracted_params: Dict[str, Any],
        confidence_score: float
    ) -> Dict[str, Any]:
        """
        Create a pending task action awaiting user confirmation.

        Args:
            session_id: Current chat session
            message_id: AI response message that proposed this action
            action_type: Type of action ("create", "update", "delete", etc.)
            extracted_params: Parameters extracted by NLP service
            confidence_score: AI confidence in extraction (0.0-1.0)

        Returns:
            Dictionary with action details:
            {
                "id": UUID,
                "session_id": UUID,
                "message_id": UUID,
                "action_type": str,
                "extracted_params": dict,
                "confidence_score": float,
                "confirmation_status": "pending",
                "created_at": datetime
            }
        """
        # Use provided session or create a context manager
        if self.db_session:
            return await self._create_pending_action_impl(
                session_id, message_id, action_type, extracted_params, confidence_score, self.db_session
            )
        else:
            with get_session() as db:
                return await self._create_pending_action_impl(
                    session_id, message_id, action_type, extracted_params, confidence_score, db
                )

    async def _create_pending_action_impl(
        self,
        session_id: UUID,
        message_id: UUID,
        action_type: str,
        extracted_params: Dict[str, Any],
        confidence_score: float,
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of create_pending_action."""
        # Convert string action_type to enum
        action_type_enum = ActionType(action_type.lower())

        # Create TaskAction record with pending confirmation
        task_action = TaskAction(
            session_id=session_id,
            message_id=message_id,
            user_id=self.user_id,
            action_type=action_type_enum,
            extracted_params=extracted_params,
            confidence_score=confidence_score,
            confirmation_status=ConfirmationStatus.PENDING,
            executed_status=ExecutedStatus.NOT_EXECUTED,
            created_at=datetime.utcnow()
        )

        db.add(task_action)
        db.commit()
        db.refresh(task_action)

        return {
            "id": str(task_action.id),
            "session_id": str(task_action.session_id),
            "message_id": str(task_action.message_id),
            "user_id": task_action.user_id,
            "action_type": task_action.action_type.value,
            "extracted_params": task_action.extracted_params,
            "confidence_score": task_action.confidence_score,
            "confirmation_status": task_action.confirmation_status.value,
            "executed_status": task_action.executed_status.value,
            "created_at": task_action.created_at.isoformat()
        }

    async def end_session(self, session_id: UUID) -> None:
        """
        Mark a session as inactive.

        Args:
            session_id: Session to end
        """
        # STUB: Implementation in Phase 3 US1
        raise NotImplementedError(
            "ChatService.end_session() will be implemented in Phase 3 US1"
        )

    async def update_session_activity(self, session_id: UUID) -> None:
        """
        Update last_activity_at timestamp for session.

        Args:
            session_id: Session to update
        """
        # STUB: Implementation in Phase 3 US1
        raise NotImplementedError(
            "ChatService.update_session_activity() will be implemented in Phase 3 US1"
        )

    async def format_query_results(
        self,
        tasks: List[Dict[str, Any]],
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format query results for AI response (T048).

        Converts task list to natural language summary.

        Args:
            tasks: List of task dictionaries from execute_query()
            filters: Optional filters that were applied

        Returns:
            Natural language formatted summary

        Examples:
            >>> service = ChatService(user_id=1)
            >>> tasks = [
            ...     {"id": 1, "title": "Buy groceries", "is_completed": False},
            ...     {"id": 2, "title": "Call dentist", "is_completed": False}
            ... ]
            >>> result = await service.format_query_results(tasks)
            >>> "Buy groceries" in result
            True
        """
        if not tasks:
            # No tasks found
            if filters:
                filter_desc = self._describe_filters(filters)
                return f"You don't have any tasks matching {filter_desc}."
            else:
                return "You don't have any tasks yet. Would you like to create one?"

        # Build natural language summary
        count = len(tasks)
        task_word = "task" if count == 1 else "tasks"

        # Describe filters if any
        filter_context = ""
        if filters:
            filter_desc = self._describe_filters(filters)
            filter_context = f" {filter_desc}"

        # Format task list
        lines = [f"You have {count} {task_word}{filter_context}:\n"]

        for i, task in enumerate(tasks[:20], 1):  # Limit to first 20
            title = task.get("title", "Untitled")
            status = "✓" if task.get("is_completed") else "○"
            lines.append(f"{i}. {status} {title}")

        if count > 20:
            lines.append(f"\n...and {count - 20} more.")

        lines.append("\n\nWould you like me to help with any of these tasks?")

        return "\n".join(lines)

    def _describe_filters(self, filters: Dict[str, Any]) -> str:
        """
        Describe filters in natural language.

        Args:
            filters: Filter dictionary

        Returns:
            Human-readable filter description

        Examples:
            >>> service = ChatService(user_id=1)
            >>> service._describe_filters({"status": "completed"})
            "that are completed"
        """
        parts = []

        status = filters.get("status")
        if status == "completed":
            parts.append("that are completed")
        elif status == "pending":
            parts.append("that are pending")

        priority = filters.get("priority")
        if priority:
            parts.append(f"with {priority} priority")

        due_date = filters.get("dueDate")
        if due_date:
            from_date = due_date.get("from")
            to_date = due_date.get("to")
            if from_date == to_date:
                parts.append(f"due on {from_date}")
            elif from_date and to_date:
                parts.append(f"due between {from_date} and {to_date}")
            elif from_date:
                parts.append(f"due after {from_date}")
            elif to_date:
                parts.append(f"due before {to_date}")

        title_contains = filters.get("titleContains")
        if title_contains:
            parts.append(f"containing '{title_contains}'")

        if not parts:
            return ""

        return " ".join(parts)

    async def stream_ai_response(
        self,
        user_message: str
    ) -> Any:
        """
        Stream AI response chunks for real-time display.

        This is used for Server-Sent Events (SSE) streaming.
        Will be implemented in Phase 6 US4 (T076).

        Args:
            user_message: User's input message

        Yields:
            Chunks of AI response as they're generated
        """
        # STUB: Implementation in Phase 6 US4 (T076)
        raise NotImplementedError(
            "ChatService.stream_ai_response() will be implemented in Phase 6 US4 (T076)"
        )

    # ============================================================================
    # Task Assistance and Proactive Features (T067-T069)
    # ============================================================================

    async def detect_overdue_tasks(self) -> List[Dict[str, Any]]:
        """
        Query tasks past due date on chat session start (T067).

        NOTE: Current Task model doesn't have a due_date field.
        This implementation uses task age as a proxy for "overdue" detection.
        When due_date is added to the Task model, this should be updated to:
            Task.due_date < datetime.utcnow() AND Task.is_completed == False

        Returns:
            List of overdue tasks:
            [
                {
                    "id": int,
                    "title": str,
                    "description": str,
                    "created_at": str,
                    "days_old": int
                }
            ]

        Examples:
            >>> service = ChatService(user_id=1)
            >>> overdue = await service.detect_overdue_tasks()
            >>> len(overdue)
            2
        """
        try:
            if self.db_session:
                return await self._detect_overdue_tasks_impl(self.db_session)
            else:
                with get_session() as db:
                    return await self._detect_overdue_tasks_impl(db)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(
                f"Error detecting overdue tasks for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return []

    async def _detect_overdue_tasks_impl(self, db: Session) -> List[Dict[str, Any]]:
        """Internal implementation of detect_overdue_tasks."""
        from ...models import Task
        from datetime import timedelta

        # TEMPORARY: Use task age as proxy for "overdue"
        # Tasks pending for more than 7 days are considered "overdue"
        cutoff_date = datetime.utcnow() - timedelta(days=7)

        statement = select(Task).where(
            Task.user_id == self.user_id,
            Task.is_completed == False,
            Task.created_at < cutoff_date
        )
        overdue_tasks = db.exec(statement).all()

        # Convert to dictionaries
        result = []
        for task in overdue_tasks:
            days_old = (datetime.utcnow() - task.created_at).days
            result.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "days_old": days_old
            })

        return result

    async def generate_proactive_overdue_message(
        self,
        overdue_tasks: List[Dict[str, Any]]
    ) -> str:
        """
        Generate proactive message when overdue tasks detected (T068).

        Asks user if they want to reschedule overdue tasks.

        Args:
            overdue_tasks: List of overdue tasks from detect_overdue_tasks()

        Returns:
            Formatted proactive message string

        Examples:
            >>> service = ChatService(user_id=1)
            >>> tasks = [
            ...     {"id": 1, "title": "Review report", "days_old": 10},
            ...     {"id": 2, "title": "Call client", "days_old": 8}
            ... ]
            >>> message = await service.generate_proactive_overdue_message(tasks)
            >>> "overdue" in message.lower() or "pending" in message.lower()
            True
        """
        if not overdue_tasks:
            return ""

        count = len(overdue_tasks)
        task_word = "task" if count == 1 else "tasks"

        # Build message
        lines = [
            f"Hi! I noticed you have {count} {task_word} that have been pending for a while:\n"
        ]

        # List tasks (max 5)
        for i, task in enumerate(overdue_tasks[:5], 1):
            title = task["title"]
            days = task["days_old"]
            lines.append(f"{i}. {title} (pending for {days} days)")

        if count > 5:
            lines.append(f"\n...and {count - 5} more.")

        lines.append(
            "\n\nWould you like help with any of these? I can help you:\n"
            "- Break them down into smaller tasks\n"
            "- Mark them as complete if they're done\n"
            "- Remove them if they're no longer relevant"
        )

        return "\n".join(lines)

    async def update_session_patterns(
        self,
        session_id: UUID
    ) -> Dict[str, Any]:
        """
        Update AIContext.user_patterns after each session (T069).

        Analyzes the completed session and updates user pattern insights.

        Args:
            session_id: Session that just ended

        Returns:
            Dictionary with update result:
            {
                "success": True,
                "patterns_updated": bool
            }
        """
        try:
            # Import here to avoid circular dependency
            from .ai_context_service import AIContextService

            # Create AI context service
            ai_context_service = AIContextService(
                user_id=self.user_id,
                db_session=self.db_session
            )

            # Store creation frequency patterns (T074)
            await ai_context_service.store_creation_frequency()

            # Store completion rate patterns (T075)
            await ai_context_service.store_completion_rates()

            return {
                "success": True,
                "patterns_updated": True
            }

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(
                f"Error updating session patterns for user {self.user_id}, session {session_id}: {str(e)}",
                exc_info=True
            )
            return {
                "success": False,
                "patterns_updated": False,
                "error": str(e)
            }

    # ============================================================================
    # SSE Connection Management (T080)
    # ============================================================================

    @staticmethod
    def add_sse_connection(user_id: int, queue: asyncio.Queue) -> None:
        """
        Register a new SSE connection for a user.

        Args:
            user_id: User ID to associate with this connection
            queue: AsyncIO queue for sending events to this connection
        """
        if user_id not in _sse_connections:
            _sse_connections[user_id] = []
        _sse_connections[user_id].append(queue)

    @staticmethod
    def remove_sse_connection(user_id: int, queue: asyncio.Queue) -> None:
        """
        Unregister an SSE connection for a user.

        Args:
            user_id: User ID
            queue: Queue to remove
        """
        if user_id in _sse_connections:
            try:
                _sse_connections[user_id].remove(queue)
                # Clean up empty lists
                if not _sse_connections[user_id]:
                    del _sse_connections[user_id]
            except ValueError:
                pass  # Queue not in list

    @staticmethod
    async def broadcast_event(user_id: int, event_type: str, data: Dict[str, Any]) -> None:
        """
        Broadcast an SSE event to all connections for a specific user.

        Args:
            user_id: User ID to broadcast to
            event_type: Event type (e.g., 'task_created', 'task_updated', 'task_deleted')
            data: Event data payload
        """
        if user_id not in _sse_connections:
            return  # No active connections for this user

        # Prepare SSE message
        event_data = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Send to all queues for this user
        dead_queues = []
        for queue in _sse_connections[user_id]:
            try:
                await queue.put(event_data)
            except Exception:
                # Queue is dead, mark for removal
                dead_queues.append(queue)

        # Clean up dead queues
        for dead_queue in dead_queues:
            ChatService.remove_sse_connection(user_id, dead_queue)

    @staticmethod
    def get_active_connections_count(user_id: int) -> int:
        """
        Get count of active SSE connections for a user.

        Args:
            user_id: User ID

        Returns:
            Number of active connections
        """
        return len(_sse_connections.get(user_id, []))
