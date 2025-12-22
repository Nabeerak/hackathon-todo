"""AI health check endpoint."""
from fastapi import APIRouter, HTTPException, status
from openai import AsyncOpenAI, APIError, APIConnectionError, APITimeoutError
import logging
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Health"])


@router.get("/health")
async def check_health():
    """
    Check OpenAI API connectivity and service health.

    Performs a lightweight API call to verify:
    - OpenAI API key is configured
    - API key is valid
    - OpenAI service is reachable
    - No rate limiting or quota issues

    Returns:
        - status: "healthy" or "unhealthy"
        - openai_configured: Whether API key is set
        - openai_reachable: Whether OpenAI API responds successfully
        - model: Configured model name
        - message: Human-readable status message

    Example Response (Healthy):
        {
            "status": "healthy",
            "openai_configured": true,
            "openai_reachable": true,
            "model": "gpt-4o-mini",
            "message": "AI service is operational"
        }

    Example Response (Unhealthy):
        {
            "status": "unhealthy",
            "openai_configured": false,
            "openai_reachable": false,
            "model": "gpt-4o-mini",
            "message": "OpenAI API key not configured",
            "error": "Missing API key"
        }
    """
    # Check if OpenAI API key is configured
    if not settings.openai_api_key:
        return {
            "status": "unhealthy",
            "openai_configured": False,
            "openai_reachable": False,
            "model": settings.openai_model,
            "message": "OpenAI API key not configured",
            "error": "Missing API key"
        }

    # Check if AI features are enabled
    if not settings.ai_features_enabled:
        return {
            "status": "unhealthy",
            "openai_configured": True,
            "openai_reachable": False,
            "model": settings.openai_model,
            "message": "AI features are disabled",
            "error": "Feature flag disabled"
        }

    # Try to make a lightweight API call to verify connectivity
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)

        # Use the simplest possible API call - just list models to verify auth
        # This is cheaper than making an actual completion call
        response = await client.models.retrieve(model=settings.openai_model)

        # If we get here, the API is reachable and key is valid
        logger.info(f"OpenAI health check passed: model={settings.openai_model}")

        return {
            "status": "healthy",
            "openai_configured": True,
            "openai_reachable": True,
            "model": settings.openai_model,
            "message": "AI service is operational"
        }

    except APIConnectionError as e:
        logger.error(f"OpenAI connection error during health check: {str(e)}")
        return {
            "status": "unhealthy",
            "openai_configured": True,
            "openai_reachable": False,
            "model": settings.openai_model,
            "message": "Cannot connect to OpenAI API",
            "error": "Connection error"
        }

    except APITimeoutError as e:
        logger.error(f"OpenAI timeout error during health check: {str(e)}")
        return {
            "status": "unhealthy",
            "openai_configured": True,
            "openai_reachable": False,
            "model": settings.openai_model,
            "message": "OpenAI API timeout",
            "error": "Timeout error"
        }

    except APIError as e:
        logger.error(f"OpenAI API error during health check: {str(e)}")
        error_message = "API error"

        # Check for specific error types
        if hasattr(e, 'status_code'):
            if e.status_code == 401:
                error_message = "Invalid API key"
            elif e.status_code == 429:
                error_message = "Rate limit exceeded"
            elif e.status_code >= 500:
                error_message = "OpenAI service error"

        return {
            "status": "unhealthy",
            "openai_configured": True,
            "openai_reachable": False,
            "model": settings.openai_model,
            "message": f"OpenAI API error: {error_message}",
            "error": error_message
        }

    except Exception as e:
        logger.error(f"Unexpected error during OpenAI health check: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "openai_configured": True,
            "openai_reachable": False,
            "model": settings.openai_model,
            "message": "Unexpected error checking OpenAI connectivity",
            "error": "Unknown error"
        }
