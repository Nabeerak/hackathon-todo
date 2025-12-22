"""AI quota and usage endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from ..auth.middleware import get_current_user_id
from ..db import get_db_session
from ..models import User, UserPreferences, AIContext
from ..services.ai.rate_limiter import rate_limiter

router = APIRouter(prefix="/api/v1/ai", tags=["AI Quota"])


@router.get("/quota")
async def get_quota(
    current_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_db_session)
):
    """
    Get AI quota usage and remaining requests for authenticated user.

    Returns:
        - remaining_requests: Number of requests left for the day
        - resets_at: ISO timestamp when quota resets
        - cost_to_date: Total OpenAI API cost for this user (estimated)
        - period: Rate limit period (always 'day')
        - limit: Total requests allowed per period
        - used: Requests used in current period

    Example Response:
        {
            "remaining_requests": 85,
            "resets_at": "2025-12-21T00:00:00",
            "cost_to_date": 0.42,
            "period": "day",
            "limit": 100,
            "used": 15
        }
    """
    # Get user preferences for custom rate limit
    stmt = select(UserPreferences).where(UserPreferences.user_id == current_user_id)
    user_prefs = session.exec(stmt).first()
    custom_limit = user_prefs.rate_limit_override if user_prefs else None

    # Get rate limit stats from rate limiter
    usage_stats = rate_limiter.get_usage_stats(
        user_id=current_user_id,
        custom_limit=custom_limit
    )

    # Get AI context for total cost estimation
    stmt = select(AIContext).where(AIContext.user_id == current_user_id)
    ai_context = session.exec(stmt).first()

    # Estimate cost based on total messages
    # Rough estimate: GPT-4o-mini costs ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
    # Average request: ~200 input tokens, ~100 output tokens
    # Average cost per request: (200 * 0.15 / 1_000_000) + (100 * 0.60 / 1_000_000) ≈ $0.00009
    total_messages = ai_context.total_messages if ai_context else 0
    estimated_cost = total_messages * 0.00009  # Rough estimate

    return {
        "remaining_requests": usage_stats["remaining"],
        "resets_at": usage_stats["resets_at"],
        "cost_to_date": round(estimated_cost, 4),
        "period": usage_stats["period"],
        "limit": usage_stats["limit"],
        "used": usage_stats["used"]
    }
