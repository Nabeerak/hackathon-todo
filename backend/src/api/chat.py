"""Chat API endpoints for AI-powered task assistant."""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel import Session
from typing import Optional
from uuid import UUID
import logging
import asyncio
import json

from ..models import MessageType, UserPreferences
from ..db import get_db_session
from ..auth.middleware import get_current_user_id
from ..services.ai.chat_service import ChatService
from ..services.ai.nlp_service import NLPService
from ..services.ai.rate_limiter import rate_limiter
from ..config import settings
from sqlmodel import select

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class SendMessageRequest(BaseModel):
    """Request model for sending a chat message."""
    content: str = Field(min_length=1, max_length=2000)
    session_id: Optional[str] = Field(default=None)


class SendMessageResponse(BaseModel):
    """Response model for chat message."""
    session_id: str
    user_message: dict
    ai_response: dict
    proposed_action: Optional[dict] = None


@router.post("/messages", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Send a chat message and receive AI response with proposed task action.

    - Requires JWT authentication
    - Processes natural language input
    - Extracts task parameters using OpenAI GPT-4o-mini
    - Creates pending action awaiting confirmation
    - Returns AI response with proposed action details

    Flow:
    1. Get or create chat session
    2. Save user message
    3. Extract task parameters via NLP service
    4. Save AI response message
    5. Create pending TaskAction if extraction successful
    6. Return session, messages, and proposed action
    """
    try:
        # Initialize services
        chat_service = ChatService(user_id=current_user_id, db_session=session)

        # Check if AI features are enabled
        if not settings.ai_features_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI features are currently disabled"
            )

        # T096: Check rate limiting
        stmt = select(UserPreferences).where(UserPreferences.user_id == current_user_id)
        user_prefs = session.exec(stmt).first()
        custom_limit = user_prefs.rate_limit_override if user_prefs else None

        allowed, remaining, resets_at = rate_limiter.check_limit(
            user_id=current_user_id,
            custom_limit=custom_limit
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "You have exceeded your AI request limit for today. Please try again later or use the traditional form.",
                    "remaining": 0,
                    "resets_at": resets_at.isoformat(),
                    "limit": custom_limit or settings.ai_rate_limit_per_day
                }
            )

        # Increment usage counter (only after successful rate limit check)
        rate_limiter.increment_usage(user_id=current_user_id)

        # Check if OpenAI API key is configured
        if not settings.openai_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not configured. Please use the traditional form."
            )

        # Get or create session
        session_id_uuid = UUID(request.session_id) if request.session_id else None
        session_data = await chat_service.get_or_create_session(session_id=session_id_uuid)
        session_id = UUID(session_data["id"])

        # Save user message
        user_message = await chat_service.save_message(
            session_id=session_id,
            content=request.content,
            message_type=MessageType.USER_MESSAGE.value,
            metadata={}
        )

        # Extract task parameters using NLP service
        nlp_service = NLPService(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens
        )

        extraction_result = await nlp_service.extract_task_params(
            user_input=request.content,
            conversation_context=None  # TODO: Add conversation history in future
        )

        # Handle extraction errors
        if not extraction_result.get("success", True):
            # Save error message as AI response
            ai_response = await chat_service.save_message(
                session_id=session_id,
                content=extraction_result["fallback_message"],
                message_type=MessageType.AI_RESPONSE.value,
                metadata={
                    "error": extraction_result["error"],
                    "should_use_traditional_form": extraction_result["should_use_traditional_form"]
                }
            )

            return SendMessageResponse(
                session_id=str(session_id),
                user_message=user_message,
                ai_response=ai_response,
                proposed_action=None
            )

        # Check if clarification needed
        if extraction_result.get("clarification_needed"):
            clarification_msg = f"I need some clarification. Could you provide more details about: {', '.join(extraction_result['ambiguous_fields'])}?"
            ai_response = await chat_service.save_message(
                session_id=session_id,
                content=clarification_msg,
                message_type=MessageType.AI_RESPONSE.value,
                metadata={
                    "clarification_needed": True,
                    "ambiguous_fields": extraction_result["ambiguous_fields"]
                }
            )

            return SendMessageResponse(
                session_id=str(session_id),
                user_message=user_message,
                ai_response=ai_response,
                proposed_action=None
            )

        # Successfully extracted task - create AI response message
        tasks = extraction_result.get("tasks", [])
        if not tasks:
            ai_response_content = "I didn't quite understand what task you'd like to create. Could you try rephrasing?"
            ai_response = await chat_service.save_message(
                session_id=session_id,
                content=ai_response_content,
                message_type=MessageType.AI_RESPONSE.value,
                metadata={"confidence": extraction_result.get("confidence", 0.0)}
            )

            return SendMessageResponse(
                session_id=str(session_id),
                user_message=user_message,
                ai_response=ai_response,
                proposed_action=None
            )

        # For now, handle single task creation (US1)
        # Multi-task support will be added in US2
        task = tasks[0]
        action_type = task.get("actionType", "create")

        # Generate confirmation message
        task_title = task.get("title", "")
        task_desc = task.get("description", "")
        task_due = task.get("dueDate")
        task_priority = task.get("priority", "medium")

        confirmation_parts = [f"I'll create a task titled '{task_title}'"]
        if task_desc:
            confirmation_parts.append(f"with description: {task_desc}")
        if task_due:
            confirmation_parts.append(f"due {task_due}")
        if task_priority != "medium":
            confirmation_parts.append(f"with {task_priority} priority")

        confirmation_msg = ". ".join(confirmation_parts) + ". Should I proceed?"

        ai_response = await chat_service.save_message(
            session_id=session_id,
            content=confirmation_msg,
            message_type=MessageType.AI_RESPONSE.value,
            metadata={
                "confidence": extraction_result.get("confidence", 0.0),
                "extracted_task": task
            }
        )

        # Create pending action
        proposed_action = await chat_service.create_pending_action(
            session_id=session_id,
            message_id=UUID(ai_response["id"]),
            action_type=action_type,
            extracted_params=task,
            confidence_score=extraction_result.get("confidence", 0.0)
        )

        logger.info(
            f"Chat message processed: User={current_user_id}, Session={session_id}, "
            f"Action={action_type}, Confidence={extraction_result.get('confidence', 0.0)}"
        )

        return SendMessageResponse(
            session_id=str(session_id),
            user_message=user_message,
            ai_response=ai_response,
            proposed_action=proposed_action
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message. Please try again."
        )


@router.get("/stream")
async def stream_events(
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Server-Sent Events (SSE) endpoint for real-time task updates.

    - Requires JWT authentication
    - Streams events when tasks are created/updated/deleted via traditional UI
    - Maintains connection for real-time sync between chat and traditional UI
    - Automatically reconnects on disconnect

    Event types:
    - task_created: New task created via traditional form
    - task_updated: Task modified via traditional UI (title, description, completion)
    - task_deleted: Task deleted via traditional UI

    Event format (SSE):
    ```
    event: task_created
    data: {"event": "task_created", "data": {"id": 123, "title": "..."}, "timestamp": "..."}

    event: task_updated
    data: {"event": "task_updated", "data": {"id": 123, "title": "..."}, "timestamp": "..."}

    event: task_deleted
    data: {"event": "task_deleted", "data": {"id": 123}, "timestamp": "..."}
    ```

    Returns:
        StreamingResponse with text/event-stream content type
    """
    async def event_generator():
        """Generate SSE events for this connection."""
        # Create queue for this connection
        queue: asyncio.Queue = asyncio.Queue()

        # Register connection
        ChatService.add_sse_connection(current_user_id, queue)
        logger.info(f"SSE connection established for user {current_user_id}")

        try:
            # Send initial connection confirmation
            yield f"event: connected\ndata: {json.dumps({'user_id': current_user_id, 'timestamp': str(asyncio.get_event_loop().time())})}\n\n"

            # Keep connection alive and send events
            while True:
                try:
                    # Wait for event with timeout for keep-alive
                    event_data = await asyncio.wait_for(queue.get(), timeout=30.0)

                    # Format SSE message
                    event_type = event_data.get("event", "message")
                    data_json = json.dumps(event_data)

                    # SSE format: event: <type>\ndata: <json>\n\n
                    yield f"event: {event_type}\ndata: {data_json}\n\n"

                except asyncio.TimeoutError:
                    # Send keep-alive ping every 30 seconds
                    yield f": keep-alive\n\n"

        except asyncio.CancelledError:
            logger.info(f"SSE connection cancelled for user {current_user_id}")
        except Exception as e:
            logger.error(f"Error in SSE stream for user {current_user_id}: {str(e)}", exc_info=True)
        finally:
            # Clean up connection
            ChatService.remove_sse_connection(current_user_id, queue)
            logger.info(f"SSE connection closed for user {current_user_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
