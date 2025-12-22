"""AI Preferences API endpoints for user customization."""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlmodel import Session
from typing import Optional
import logging

from ..models import AITone
from ..db import get_db_session
from ..auth.middleware import get_current_user_id
from ..services.ai.user_preferences_service import UserPreferencesService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai/preferences", tags=["ai-preferences"])


class PreferencesResponse(BaseModel):
    """Response model for user preferences."""
    user_id: int
    preferred_language: str
    ai_tone: str
    enable_proactive_suggestions: bool
    ai_features_enabled: bool
    learned_shortcuts: dict
    created_at: str
    updated_at: str


class PreferencesUpdateRequest(BaseModel):
    """Request model for updating preferences."""
    preferred_language: Optional[str] = None
    ai_tone: Optional[str] = None  # "professional", "casual", "concise"
    enable_proactive_suggestions: Optional[bool] = None
    ai_features_enabled: Optional[bool] = None


@router.get("", response_model=PreferencesResponse)
async def get_preferences(
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get user AI preferences (T091).

    Returns current AI preferences including:
    - Preferred language
    - AI tone (professional/casual/concise)
    - Proactive suggestions enabled/disabled
    - AI features enabled/disabled
    - Learned shortcuts

    - Requires JWT authentication
    - Returns only preferences for authenticated user

    Security:
    - JWT token required
    - User can only access their own preferences
    """
    try:
        service = UserPreferencesService(user_id=current_user_id, db_session=session)
        prefs = await service.get_preferences()

        if not prefs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User preferences not found. Default preferences will be created."
            )

        return PreferencesResponse(**prefs)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preferences for user {current_user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving preferences"
        )


@router.patch("", response_model=PreferencesResponse)
async def update_preferences(
    request: PreferencesUpdateRequest,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Update user AI preferences (T091).

    Allows users to customize AI behavior:
    - Set preferred language (e.g., "en", "es", "fr")
    - Choose AI tone (professional, casual, concise)
    - Enable/disable proactive suggestions
    - Enable/disable AI features globally

    - Requires JWT authentication
    - Only updates fields provided in request
    - Returns updated preferences

    Security:
    - JWT token required
    - User can only update their own preferences
    """
    try:
        # Build updates dictionary from request
        updates = {}

        if request.preferred_language is not None:
            updates["preferred_language"] = request.preferred_language

        if request.ai_tone is not None:
            # Validate AI tone
            tone_value = request.ai_tone.upper()
            if not hasattr(AITone, tone_value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid AI tone. Must be one of: professional, casual, concise"
                )
            updates["ai_tone"] = request.ai_tone

        if request.enable_proactive_suggestions is not None:
            updates["enable_proactive_suggestions"] = request.enable_proactive_suggestions

        if request.ai_features_enabled is not None:
            updates["ai_features_enabled"] = request.ai_features_enabled

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid preferences to update"
            )

        # Update preferences
        service = UserPreferencesService(user_id=current_user_id, db_session=session)
        result = await service.update_preferences(updates)

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to update preferences")
            )

        # Return updated preferences
        prefs = await service.get_preferences()
        if not prefs:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated preferences"
            )

        logger.info(f"Preferences updated for user {current_user_id}: {list(updates.keys())}")

        return PreferencesResponse(**prefs)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences for user {current_user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating preferences"
        )
