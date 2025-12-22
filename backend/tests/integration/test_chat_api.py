"""Integration tests for chat API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from unittest.mock import patch, MagicMock

from src.models import User


class TestChatAPI:
    """Test suite for /api/v1/chat endpoints."""

    @patch('src.api.chat.NLPService')
    def test_send_message_success(self, mock_nlp_service, client: TestClient, auth_headers: dict, test_user: User):
        """Test successfully sending a chat message."""
        # Mock NLP service response
        mock_nlp_instance = MagicMock()
        mock_nlp_instance.extract_task_parameters.return_value = {
            "action_type": "create",
            "confidence": 0.95,
            "parameters": {
                "title": "Buy groceries",
                "description": "Milk, bread, eggs"
            },
            "ai_message": "I'll create a task for buying groceries."
        }
        mock_nlp_service.return_value = mock_nlp_instance

        response = client.post(
            "/api/v1/chat/messages",
            json={"content": "Add buy groceries task"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "user_message" in data
        assert "ai_response" in data
        assert data["user_message"]["content"] == "Add buy groceries task"

    def test_send_message_requires_auth(self, client: TestClient):
        """Test that sending message requires authentication."""
        response = client.post(
            "/api/v1/chat/messages",
            json={"content": "Add task"}
        )

        assert response.status_code == 401

    def test_send_message_validates_input(self, client: TestClient, auth_headers: dict):
        """Test input validation for chat messages."""
        # Empty content
        response = client.post(
            "/api/v1/chat/messages",
            json={"content": ""},
            headers=auth_headers
        )

        assert response.status_code == 422

    @patch('src.api.chat.settings')
    def test_send_message_respects_ai_features_disabled(self, mock_settings, client: TestClient, auth_headers: dict):
        """Test that AI features can be disabled."""
        mock_settings.ai_features_enabled = False

        response = client.post(
            "/api/v1/chat/messages",
            json={"content": "Add task"},
            headers=auth_headers
        )

        assert response.status_code == 503
        assert "disabled" in response.json()["detail"].lower()

    @patch('src.api.chat.rate_limiter')
    def test_send_message_enforces_rate_limit(self, mock_rate_limiter, client: TestClient, auth_headers: dict):
        """Test that rate limiting is enforced."""
        from datetime import datetime, timedelta

        # Mock rate limiter to return limit exceeded
        mock_rate_limiter.check_limit.return_value = (
            False,  # not allowed
            0,  # remaining
            datetime.utcnow() + timedelta(hours=1)  # resets_at
        )

        response = client.post(
            "/api/v1/chat/messages",
            json={"content": "Add task"},
            headers=auth_headers
        )

        assert response.status_code == 429
        data = response.json()
        assert "limit" in data["detail"]["message"].lower()


class TestAIActionsAPI:
    """Test suite for /api/v1/ai/actions endpoints."""

    def test_confirm_action_success(self, client: TestClient, auth_headers: dict, db_session: Session, test_user: User):
        """Test confirming a pending action."""
        from src.models import TaskAction, ActionType, ConfirmationStatus
        from uuid import uuid4

        # Create a pending action
        action = TaskAction(
            action_id=uuid4(),
            user_id=test_user.id,
            action_type=ActionType.CREATE,
            parameters={"title": "Test Task", "description": "Test"},
            confidence=0.95,
            confirmation_status=ConfirmationStatus.PENDING
        )
        db_session.add(action)
        db_session.commit()
        db_session.refresh(action)

        response = client.post(
            f"/api/v1/ai/actions/{action.action_id}/confirm",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "executed"
        assert "result" in data

    def test_confirm_action_not_found(self, client: TestClient, auth_headers: dict):
        """Test confirming non-existent action."""
        from uuid import uuid4

        response = client.post(
            f"/api/v1/ai/actions/{uuid4()}/confirm",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_reject_action_success(self, client: TestClient, auth_headers: dict, db_session: Session, test_user: User):
        """Test rejecting a pending action."""
        from src.models import TaskAction, ActionType, ConfirmationStatus
        from uuid import uuid4

        # Create a pending action
        action = TaskAction(
            action_id=uuid4(),
            user_id=test_user.id,
            action_type=ActionType.DELETE,
            parameters={"task_id": 123},
            confidence=0.85,
            confirmation_status=ConfirmationStatus.PENDING
        )
        db_session.add(action)
        db_session.commit()
        db_session.refresh(action)

        response = client.post(
            f"/api/v1/ai/actions/{action.action_id}/reject",
            json={"reason": "Not what I wanted"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"


class TestAIPreferencesAPI:
    """Test suite for /api/v1/ai/preferences endpoints."""

    def test_get_preferences_success(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test retrieving user preferences."""
        response = client.get(
            "/api/v1/ai/preferences",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "ai_tone" in data
        assert "preferred_language" in data
        assert "enable_proactive_suggestions" in data

    def test_update_preferences_success(self, client: TestClient, auth_headers: dict):
        """Test updating user preferences."""
        response = client.patch(
            "/api/v1/ai/preferences",
            json={"ai_tone": "casual"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ai_tone"] == "casual"

    def test_update_preferences_invalid_tone(self, client: TestClient, auth_headers: dict):
        """Test that invalid AI tone is rejected."""
        response = client.patch(
            "/api/v1/ai/preferences",
            json={"ai_tone": "invalid_tone"},
            headers=auth_headers
        )

        assert response.status_code == 422


class TestAIQuotaAPI:
    """Test suite for /api/v1/ai/quota endpoint."""

    @patch('src.api.ai_quota.rate_limiter')
    def test_get_quota_success(self, mock_rate_limiter, client: TestClient, auth_headers: dict, test_user: User):
        """Test retrieving quota information."""
        from datetime import datetime, timedelta

        mock_rate_limiter.get_usage_stats.return_value = {
            "user_id": test_user.id,
            "period": "day",
            "limit": 100,
            "used": 25,
            "remaining": 75,
            "resets_at": (datetime.utcnow() + timedelta(hours=12)).isoformat()
        }

        response = client.get(
            "/api/v1/ai/quota",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["remaining"] == 75
        assert data["limit"] == 100
