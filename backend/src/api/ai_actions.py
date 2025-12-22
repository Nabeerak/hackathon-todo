"""AI task action endpoints for confirmation and execution."""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import Optional
from uuid import UUID
from datetime import datetime
import logging

from ..models import TaskAction, Task, ConfirmationStatus, ExecutedStatus, ActionType
from ..db import get_db_session
from ..auth.middleware import get_current_user_id, validate_user_id_match
from ..services.ai.chat_service import ChatService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai/actions", tags=["ai-actions"])


class PendingActionItem(BaseModel):
    """Model for a single pending action."""
    action_id: str
    action_type: str
    extracted_params: dict
    confidence_score: Optional[float]
    created_at: str


class PendingActionsResponse(BaseModel):
    """Response model for pending actions list."""
    pending_actions: List[PendingActionItem]
    count: int


class ConfirmActionResponse(BaseModel):
    """Response model for action confirmation."""
    action_id: str
    confirmation_status: str
    executed_status: str
    task: Optional[dict] = None
    error: Optional[str] = None


@router.get("/pending", response_model=PendingActionsResponse)
async def get_pending_actions(
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get all pending actions awaiting user confirmation (T056).

    Returns a list of TaskAction records with confirmation_status='pending'
    for the authenticated user.

    - Requires JWT authentication
    - Returns only actions belonging to the current user
    - Ordered by created_at (most recent first)

    Security:
    - JWT token required
    - Only returns actions for the authenticated user
    """
    try:
        # Query pending actions for the current user
        statement = (
            select(TaskAction)
            .where(
                TaskAction.user_id == current_user_id,
                TaskAction.confirmation_status == ConfirmationStatus.PENDING
            )
            .order_by(TaskAction.created_at.desc())
        )

        pending_actions = session.exec(statement).all()

        # Convert to response models
        action_items = [
            PendingActionItem(
                action_id=str(action.id),
                action_type=action.action_type.value,
                extracted_params=action.extracted_params,
                confidence_score=action.confidence_score,
                created_at=action.created_at.isoformat()
            )
            for action in pending_actions
        ]

        logger.info(
            f"Retrieved {len(action_items)} pending actions for user {current_user_id}"
        )

        return PendingActionsResponse(
            pending_actions=action_items,
            count=len(action_items)
        )

    except Exception as e:
        logger.error(f"Error retrieving pending actions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving pending actions"
        )


@router.post("/{action_id}/confirm", response_model=ConfirmActionResponse)
async def confirm_action(
    action_id: str,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Confirm and execute a pending AI task action.

    - Requires JWT authentication
    - Validates user owns the action (T032, T033)
    - Executes task creation/update/delete based on action type
    - Updates action status to confirmed and executed
    - Returns created/updated task details

    Security:
    - JWT token required (T032)
    - user_id from JWT must match action.user_id (T033)

    Flow:
    1. Load TaskAction by ID
    2. Validate ownership (user_id match)
    3. Check action is in pending status
    4. Execute action based on action_type
    5. Update action status
    6. Return result
    """
    try:
        # Parse action_id as UUID
        try:
            action_uuid = UUID(action_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action ID format"
            )

        # Load TaskAction
        statement = select(TaskAction).where(TaskAction.id == action_uuid)
        task_action = session.exec(statement).first()

        if not task_action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action not found"
            )

        # T033: Validate user_id from JWT matches action.user_id
        validate_user_id_match(task_action.user_id, current_user_id)

        # Check if action is already confirmed or executed
        if task_action.confirmation_status != ConfirmationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Action already {task_action.confirmation_status.value}"
            )

        # Mark action as confirmed
        task_action.confirmation_status = ConfirmationStatus.CONFIRMED
        task_action.confirmed_at = datetime.utcnow()
        task_action.executed_status = ExecutedStatus.EXECUTING

        session.add(task_action)
        session.commit()

        # Execute action based on type
        created_task = None
        error_message = None

        try:
            if task_action.action_type == ActionType.CREATE:
                # Create task from extracted parameters
                params = task_action.extracted_params

                # Extract and validate parameters
                title = params.get("title", "").strip()
                description = params.get("description", "").strip() or None

                if not title:
                    raise ValueError("Task title is required")

                # Create task
                new_task = Task(
                    user_id=current_user_id,
                    title=title,
                    description=description,
                    is_completed=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                session.add(new_task)
                session.commit()
                session.refresh(new_task)

                # Update action with created task ID
                task_action.task_id = new_task.id
                task_action.executed_status = ExecutedStatus.SUCCESS
                task_action.executed_at = datetime.utcnow()

                created_task = {
                    "id": new_task.id,
                    "user_id": new_task.user_id,
                    "title": new_task.title,
                    "description": new_task.description,
                    "is_completed": new_task.is_completed,
                    "created_at": new_task.created_at.isoformat(),
                    "updated_at": new_task.updated_at.isoformat()
                }

                logger.info(
                    f"Task created via AI: ID={new_task.id}, User={current_user_id}, "
                    f"Title='{new_task.title}', Action={action_id}"
                )

            elif task_action.action_type == ActionType.QUERY:
                # US2 - Query operations (T047, T048)
                from ..services.task_action_service import TaskActionService

                task_service = TaskActionService(user_id=current_user_id, db_session=session)
                filters = task_action.extracted_params.get("filters", {})

                query_result = await task_service.execute_query(filters)

                if query_result["success"]:
                    # Format results for AI response
                    chat_service = ChatService(user_id=current_user_id, db_session=session)
                    formatted_response = await chat_service.format_query_results(
                        query_result["tasks"],
                        filters
                    )

                    task_action.executed_status = ExecutedStatus.SUCCESS
                    task_action.executed_at = datetime.utcnow()

                    created_task = {
                        "query_results": query_result["tasks"],
                        "formatted_response": formatted_response,
                        "count": query_result["count"]
                    }

                    logger.info(
                        f"Query executed via AI: User={current_user_id}, "
                        f"Filters={filters}, Count={query_result['count']}"
                    )
                else:
                    raise ValueError(query_result.get("error", "Query failed"))

            elif task_action.action_type == ActionType.UPDATE:
                # US2 - Update operations (T050, T051)
                from ..services.task_action_service import TaskActionService

                task_service = TaskActionService(user_id=current_user_id, db_session=session)
                target = task_action.extracted_params.get("target", "")
                updates = {}

                if task_action.extracted_params.get("title"):
                    updates["title"] = task_action.extracted_params["title"]
                if task_action.extracted_params.get("description"):
                    updates["description"] = task_action.extracted_params["description"]

                update_result = await task_service.execute_update(target, updates)

                if update_result["success"]:
                    task_action.task_id = update_result["task"]["id"]
                    task_action.executed_status = ExecutedStatus.SUCCESS
                    task_action.executed_at = datetime.utcnow()

                    created_task = update_result["task"]

                    logger.info(
                        f"Task updated via AI: ID={update_result['task']['id']}, "
                        f"User={current_user_id}, Updates={updates}"
                    )
                elif update_result.get("needs_clarification"):
                    raise ValueError(
                        f"{update_result['error']}. Multiple matches: "
                        f"{[t['title'] for t in update_result.get('ambiguous_matches', [])]}"
                    )
                else:
                    raise ValueError(update_result.get("error", "Update failed"))

            elif task_action.action_type == ActionType.COMPLETE:
                # US2 - Complete operations (T053)
                from ..services.task_action_service import TaskActionService

                task_service = TaskActionService(user_id=current_user_id, db_session=session)
                target = task_action.extracted_params.get("target", "")

                complete_result = await task_service.execute_complete(target)

                if complete_result["success"]:
                    task_action.task_id = complete_result["task"]["id"]
                    task_action.executed_status = ExecutedStatus.SUCCESS
                    task_action.executed_at = datetime.utcnow()

                    created_task = complete_result["task"]

                    logger.info(
                        f"Task completion toggled via AI: ID={complete_result['task']['id']}, "
                        f"User={current_user_id}, NewStatus={complete_result['task']['is_completed']}"
                    )
                elif complete_result.get("needs_clarification"):
                    raise ValueError(
                        f"{complete_result['error']}. Multiple matches: "
                        f"{[t['title'] for t in complete_result.get('ambiguous_matches', [])]}"
                    )
                else:
                    raise ValueError(complete_result.get("error", "Complete operation failed"))

            elif task_action.action_type == ActionType.DELETE:
                # US2 - Delete operations (T055)
                from ..services.task_action_service import TaskActionService

                task_service = TaskActionService(user_id=current_user_id, db_session=session)
                target = task_action.extracted_params.get("target")
                bulk_criteria = task_action.extracted_params.get("bulkCriteria")

                delete_result = await task_service.execute_delete(target, bulk_criteria)

                if delete_result.get("requires_confirmation"):
                    # Bulk delete - return confirmation requirement
                    raise ValueError(
                        f"{delete_result['message']} "
                        f"Potential deletes: {delete_result.get('potential_deletes', 0)}"
                    )
                elif delete_result["success"]:
                    task_action.executed_status = ExecutedStatus.SUCCESS
                    task_action.executed_at = datetime.utcnow()

                    created_task = {
                        "deleted_count": delete_result["deleted_count"],
                        "message": delete_result["message"]
                    }

                    logger.info(
                        f"Task(s) deleted via AI: User={current_user_id}, "
                        f"Count={delete_result['deleted_count']}"
                    )
                elif delete_result.get("needs_clarification"):
                    raise ValueError(
                        f"{delete_result['error']}. Multiple matches: "
                        f"{[t['title'] for t in delete_result.get('ambiguous_matches', [])]}"
                    )
                else:
                    raise ValueError(delete_result.get("error", "Delete operation failed"))

            else:
                raise ValueError(f"Unknown action type: {task_action.action_type}")

        except Exception as e:
            # Execution failed
            task_action.executed_status = ExecutedStatus.FAILED
            task_action.error_message = str(e)
            task_action.executed_at = datetime.utcnow()
            error_message = str(e)

            logger.error(
                f"Failed to execute AI action: ID={action_id}, User={current_user_id}, "
                f"Type={task_action.action_type.value}, Error={str(e)}"
            )

        # Save final action status
        session.add(task_action)
        session.commit()
        session.refresh(task_action)

        # Return response
        return ConfirmActionResponse(
            action_id=str(task_action.id),
            confirmation_status=task_action.confirmation_status.value,
            executed_status=task_action.executed_status.value,
            task=created_task,
            error=error_message
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming action: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while confirming the action"
        )


@router.post("/{action_id}/reject", response_model=ConfirmActionResponse)
async def reject_action(
    action_id: str,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Reject a pending AI task action.

    - Requires JWT authentication
    - Validates user owns the action
    - Marks action as rejected without executing
    - Returns updated action status

    Security:
    - JWT token required
    - user_id from JWT must match action.user_id
    """
    try:
        # Parse action_id as UUID
        try:
            action_uuid = UUID(action_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action ID format"
            )

        # Load TaskAction
        statement = select(TaskAction).where(TaskAction.id == action_uuid)
        task_action = session.exec(statement).first()

        if not task_action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action not found"
            )

        # Validate user_id from JWT matches action.user_id
        validate_user_id_match(task_action.user_id, current_user_id)

        # Check if action is already confirmed or rejected
        if task_action.confirmation_status != ConfirmationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Action already {task_action.confirmation_status.value}"
            )

        # Mark action as rejected
        task_action.confirmation_status = ConfirmationStatus.REJECTED
        task_action.confirmed_at = datetime.utcnow()

        session.add(task_action)
        session.commit()
        session.refresh(task_action)

        logger.info(f"AI action rejected: ID={action_id}, User={current_user_id}")

        return ConfirmActionResponse(
            action_id=str(task_action.id),
            confirmation_status=task_action.confirmation_status.value,
            executed_status=task_action.executed_status.value,
            task=None,
            error=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting action: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while rejecting the action"
        )
