"""Task action execution service for AI-powered task operations."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, or_, and_
import logging

from src.models import Task, TaskAction, ActionType, ExecutedStatus
from src.db import get_session

logger = logging.getLogger(__name__)


class TaskActionService:
    """
    Service for executing AI-interpreted task actions.

    Handles query, update, complete, and delete operations (US2).
    """

    def __init__(self, user_id: int, db_session: Optional[Session] = None):
        """
        Initialize task action service for a specific user.

        Args:
            user_id: User ID for ownership validation and isolation
            db_session: Optional database session (for dependency injection)
        """
        self.user_id = user_id
        self.db_session = db_session

    async def execute_query(
        self,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a query operation to filter and retrieve tasks (T047).

        Filters tasks by user-provided criteria:
        - status: "completed", "pending", "all"
        - dueDate: {"from": "ISO date", "to": "ISO date"}
        - priority: "low", "medium", "high"
        - titleContains: search string

        Args:
            filters: Filter criteria from NLP extraction

        Returns:
            Dictionary with query results:
            {
                "success": True,
                "tasks": [
                    {
                        "id": int,
                        "title": str,
                        "description": str,
                        "is_completed": bool,
                        "created_at": str,
                        "updated_at": str
                    }
                ],
                "count": int
            }

        Examples:
            >>> service = TaskActionService(user_id=1)
            >>> # Get pending tasks
            >>> result = await service.execute_query({"status": "pending"})
            >>> result["count"]
            5
        """
        try:
            # Use provided session or create a context manager
            if self.db_session:
                return await self._execute_query_impl(filters, self.db_session)
            else:
                with get_session() as db:
                    return await self._execute_query_impl(filters, db)

        except Exception as e:
            logger.error(f"Error executing query for user {self.user_id}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "tasks": [],
                "count": 0
            }

    async def _execute_query_impl(
        self,
        filters: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of execute_query."""
        # Build base query - always filter by user_id for isolation
        statement = select(Task).where(Task.user_id == self.user_id)

        # Apply status filter
        status_filter = filters.get("status", "all")
        if status_filter == "completed":
            statement = statement.where(Task.is_completed == True)
        elif status_filter == "pending":
            statement = statement.where(Task.is_completed == False)
        # "all" means no filter

        # Apply priority filter (if supported in future - Task model doesn't have priority yet)
        # priority_filter = filters.get("priority")
        # if priority_filter:
        #     statement = statement.where(Task.priority == priority_filter)

        # Apply date range filter
        due_date_filter = filters.get("dueDate")
        if due_date_filter:
            # Note: Current Task model doesn't have due_date field
            # This is a placeholder for future implementation when due_date is added
            logger.warning(
                f"dueDate filter requested but Task model doesn't have due_date field yet. "
                f"Filter: {due_date_filter}"
            )
            # from_date = due_date_filter.get("from")
            # to_date = due_date_filter.get("to")
            # if from_date:
            #     statement = statement.where(Task.due_date >= from_date)
            # if to_date:
            #     statement = statement.where(Task.due_date <= to_date)

        # Apply title search filter
        title_contains = filters.get("titleContains")
        if title_contains:
            statement = statement.where(Task.title.ilike(f"%{title_contains}%"))

        # Execute query
        tasks = db.exec(statement).all()

        # Convert to dictionaries
        task_list = [
            {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]

        logger.info(
            f"Query executed for user {self.user_id}: {len(task_list)} tasks found. "
            f"Filters: {filters}"
        )

        return {
            "success": True,
            "tasks": task_list,
            "count": len(task_list)
        }

    async def resolve_task(
        self,
        task_identifier: str
    ) -> Optional[Task]:
        """
        Resolve a task by ID or title keyword (T051).

        Supports:
        - Numeric ID: "42" → task with ID 42
        - Title keyword: "groceries" → task with title containing "groceries"

        Args:
            task_identifier: Task ID (numeric) or title keyword

        Returns:
            Task object if found and owned by user, None otherwise

        Examples:
            >>> service = TaskActionService(user_id=1)
            >>> task = await service.resolve_task("42")  # By ID
            >>> task.id
            42
            >>> task = await service.resolve_task("groceries")  # By title
            >>> "groceries" in task.title.lower()
            True
        """
        try:
            # Use provided session or create a context manager
            if self.db_session:
                return await self._resolve_task_impl(task_identifier, self.db_session)
            else:
                with get_session() as db:
                    return await self._resolve_task_impl(task_identifier, db)

        except Exception as e:
            logger.error(
                f"Error resolving task '{task_identifier}' for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return None

    async def _resolve_task_impl(
        self,
        task_identifier: str,
        db: Session
    ) -> Optional[Task]:
        """Internal implementation of resolve_task."""
        # Try to parse as numeric ID first
        try:
            task_id = int(task_identifier)
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == self.user_id  # Ensure user owns the task
            )
            task = db.exec(statement).first()
            if task:
                logger.info(f"Resolved task by ID: {task_id} for user {self.user_id}")
                return task
        except ValueError:
            # Not a numeric ID, treat as title keyword
            pass

        # Search by title keyword (case-insensitive partial match)
        statement = select(Task).where(
            Task.user_id == self.user_id,
            Task.title.ilike(f"%{task_identifier}%")
        )
        tasks = db.exec(statement).all()

        if len(tasks) == 1:
            # Exact match - return the single task
            logger.info(
                f"Resolved task by title keyword '{task_identifier}': "
                f"ID={tasks[0].id}, Title='{tasks[0].title}' for user {self.user_id}"
            )
            return tasks[0]
        elif len(tasks) > 1:
            # Multiple matches - log ambiguity and return None
            logger.warning(
                f"Ambiguous task identifier '{task_identifier}' - found {len(tasks)} matches "
                f"for user {self.user_id}. Returning None."
            )
            return None
        else:
            # No matches
            logger.warning(
                f"No task found for identifier '{task_identifier}' and user {self.user_id}"
            )
            return None

    async def execute_update(
        self,
        task_identifier: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an update operation on a task (T050).

        Validates user ownership and updates task fields.

        Args:
            task_identifier: Task ID or title keyword
            updates: Fields to update (title, description, etc.)

        Returns:
            Dictionary with update result:
            {
                "success": True,
                "task": {...},
                "message": "Task updated successfully"
            }
            or
            {
                "success": False,
                "error": "Task not found",
                "needs_clarification": True,
                "ambiguous_matches": [...]  # If multiple tasks match
            }

        Examples:
            >>> service = TaskActionService(user_id=1)
            >>> result = await service.execute_update("meeting", {"title": "Team standup"})
            >>> result["success"]
            True
        """
        try:
            # Use provided session or create a context manager
            if self.db_session:
                return await self._execute_update_impl(task_identifier, updates, self.db_session)
            else:
                with get_session() as db:
                    return await self._execute_update_impl(task_identifier, updates, db)

        except Exception as e:
            logger.error(
                f"Error updating task '{task_identifier}' for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {
                "success": False,
                "error": str(e)
            }

    async def _execute_update_impl(
        self,
        task_identifier: str,
        updates: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of execute_update."""
        # Resolve task
        task = await self._resolve_task_impl(task_identifier, db)

        if not task:
            # Check if ambiguous (multiple matches)
            statement = select(Task).where(
                Task.user_id == self.user_id,
                Task.title.ilike(f"%{task_identifier}%")
            )
            ambiguous_tasks = db.exec(statement).all()

            if len(ambiguous_tasks) > 1:
                return {
                    "success": False,
                    "error": f"Multiple tasks found matching '{task_identifier}'",
                    "needs_clarification": True,
                    "ambiguous_matches": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "description": t.description
                        }
                        for t in ambiguous_tasks
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Task '{task_identifier}' not found"
                }

        # Apply updates
        updated_fields = []
        if "title" in updates and updates["title"]:
            task.title = updates["title"]
            updated_fields.append("title")

        if "description" in updates:
            task.description = updates["description"]
            updated_fields.append("description")

        # Update timestamp
        task.updated_at = datetime.utcnow()

        # Save changes
        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(
            f"Task updated: ID={task.id}, User={self.user_id}, "
            f"Fields={updated_fields}, NewTitle='{task.title}'"
        )

        return {
            "success": True,
            "task": {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            },
            "message": f"Task '{task.title}' updated successfully"
        }

    async def execute_complete(
        self,
        task_identifier: str
    ) -> Dict[str, Any]:
        """
        Execute a complete operation to toggle task completion status (T053).

        Args:
            task_identifier: Task ID or title keyword

        Returns:
            Dictionary with completion result:
            {
                "success": True,
                "task": {...},
                "message": "Task marked as complete"
            }

        Examples:
            >>> service = TaskActionService(user_id=1)
            >>> result = await service.execute_complete("groceries")
            >>> result["success"]
            True
        """
        try:
            # Use provided session or create a context manager
            if self.db_session:
                return await self._execute_complete_impl(task_identifier, self.db_session)
            else:
                with get_session() as db:
                    return await self._execute_complete_impl(task_identifier, db)

        except Exception as e:
            logger.error(
                f"Error completing task '{task_identifier}' for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {
                "success": False,
                "error": str(e)
            }

    async def _execute_complete_impl(
        self,
        task_identifier: str,
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of execute_complete."""
        # Resolve task
        task = await self._resolve_task_impl(task_identifier, db)

        if not task:
            # Check if ambiguous
            statement = select(Task).where(
                Task.user_id == self.user_id,
                Task.title.ilike(f"%{task_identifier}%")
            )
            ambiguous_tasks = db.exec(statement).all()

            if len(ambiguous_tasks) > 1:
                return {
                    "success": False,
                    "error": f"Multiple tasks found matching '{task_identifier}'",
                    "needs_clarification": True,
                    "ambiguous_matches": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "is_completed": t.is_completed
                        }
                        for t in ambiguous_tasks
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Task '{task_identifier}' not found"
                }

        # Toggle completion status
        old_status = task.is_completed
        task.is_completed = not task.is_completed
        task.updated_at = datetime.utcnow()

        # Save changes
        db.add(task)
        db.commit()
        db.refresh(task)

        status_message = "complete" if task.is_completed else "incomplete"

        logger.info(
            f"Task completion toggled: ID={task.id}, User={self.user_id}, "
            f"OldStatus={old_status}, NewStatus={task.is_completed}"
        )

        return {
            "success": True,
            "task": {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            },
            "message": f"Task '{task.title}' marked as {status_message}"
        }

    async def execute_delete(
        self,
        task_identifier: Optional[str] = None,
        bulk_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a delete operation on one or more tasks (T055).

        Supports:
        - Single task deletion by ID or title
        - Bulk deletion by criteria (requires confirmation)

        Args:
            task_identifier: Task ID or title keyword (for single delete)
            bulk_criteria: Criteria for bulk delete (e.g., {"status": "completed"})

        Returns:
            Dictionary with deletion result:
            {
                "success": True,
                "deleted_count": int,
                "message": "X task(s) deleted",
                "requires_confirmation": bool  # True for bulk deletes
            }

        Examples:
            >>> service = TaskActionService(user_id=1)
            >>> # Single delete
            >>> result = await service.execute_delete(task_identifier="dentist")
            >>> result["success"]
            True

            >>> # Bulk delete (requires confirmation)
            >>> result = await service.execute_delete(bulk_criteria={"status": "completed"})
            >>> result["requires_confirmation"]
            True
        """
        try:
            # Use provided session or create a context manager
            if self.db_session:
                return await self._execute_delete_impl(
                    task_identifier, bulk_criteria, self.db_session
                )
            else:
                with get_session() as db:
                    return await self._execute_delete_impl(
                        task_identifier, bulk_criteria, db
                    )

        except Exception as e:
            logger.error(
                f"Error deleting task for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {
                "success": False,
                "error": str(e)
            }

    async def _execute_delete_impl(
        self,
        task_identifier: Optional[str],
        bulk_criteria: Optional[Dict[str, Any]],
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of execute_delete."""
        # Single task deletion
        if task_identifier and not bulk_criteria:
            task = await self._resolve_task_impl(task_identifier, db)

            if not task:
                # Check if ambiguous
                statement = select(Task).where(
                    Task.user_id == self.user_id,
                    Task.title.ilike(f"%{task_identifier}%")
                )
                ambiguous_tasks = db.exec(statement).all()

                if len(ambiguous_tasks) > 1:
                    return {
                        "success": False,
                        "error": f"Multiple tasks found matching '{task_identifier}'",
                        "needs_clarification": True,
                        "ambiguous_matches": [
                            {
                                "id": t.id,
                                "title": t.title
                            }
                            for t in ambiguous_tasks
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Task '{task_identifier}' not found"
                    }

            # Delete single task
            task_title = task.title
            db.delete(task)
            db.commit()

            logger.info(
                f"Task deleted: ID={task.id}, User={self.user_id}, Title='{task_title}'"
            )

            return {
                "success": True,
                "deleted_count": 1,
                "message": f"Task '{task_title}' deleted successfully",
                "requires_confirmation": False
            }

        # Bulk deletion (requires confirmation flag in TaskAction)
        elif bulk_criteria:
            # Build query based on criteria
            statement = select(Task).where(Task.user_id == self.user_id)

            status_filter = bulk_criteria.get("status")
            if status_filter == "completed":
                statement = statement.where(Task.is_completed == True)
            elif status_filter == "pending":
                statement = statement.where(Task.is_completed == False)

            # Date filter (if supported in future)
            older_than = bulk_criteria.get("olderThan")
            if older_than:
                # Task model doesn't have due_date yet
                # statement = statement.where(Task.created_at < older_than)
                logger.warning(
                    f"olderThan filter requested but Task model doesn't have proper date fields. "
                    f"Filter: {older_than}"
                )

            # Count tasks that would be deleted
            tasks_to_delete = db.exec(statement).all()
            count = len(tasks_to_delete)

            # Don't actually delete yet - return confirmation requirement
            logger.info(
                f"Bulk delete requested for user {self.user_id}: "
                f"{count} tasks match criteria {bulk_criteria}"
            )

            return {
                "success": False,  # Not executed yet
                "deleted_count": 0,
                "potential_deletes": count,
                "message": f"{count} task(s) will be deleted. Please confirm this action.",
                "requires_confirmation": True,
                "preview": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "is_completed": t.is_completed
                    }
                    for t in tasks_to_delete[:10]  # Show first 10
                ]
            }

        else:
            return {
                "success": False,
                "error": "Either task_identifier or bulk_criteria must be provided"
            }
