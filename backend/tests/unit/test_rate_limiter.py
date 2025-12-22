"""Unit tests for rate limiter service."""
import pytest
from datetime import datetime, timedelta

from src.services.ai.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test suite for RateLimiter class."""

    def test_check_limit_allows_requests_under_limit(self):
        """Test that requests under the limit are allowed."""
        limiter = RateLimiter(default_limit_per_day=100)
        user_id = 1

        allowed, remaining, resets_at = limiter.check_limit(user_id)

        assert allowed is True
        assert remaining == 100
        assert resets_at > datetime.utcnow()

    def test_increment_usage_decreases_remaining(self):
        """Test that incrementing usage decreases remaining count."""
        limiter = RateLimiter(default_limit_per_day=100)
        user_id = 1

        limiter.increment_usage(user_id, count=5)
        allowed, remaining, resets_at = limiter.check_limit(user_id)

        assert allowed is True
        assert remaining == 95

    def test_check_limit_blocks_when_exceeded(self):
        """Test that requests are blocked when limit is exceeded."""
        limiter = RateLimiter(default_limit_per_day=10)
        user_id = 1

        # Use up all requests
        limiter.increment_usage(user_id, count=10)
        allowed, remaining, resets_at = limiter.check_limit(user_id)

        assert allowed is False
        assert remaining == 0

    def test_custom_limit_override(self):
        """Test that custom limits override defaults."""
        limiter = RateLimiter(default_limit_per_day=100)
        user_id = 1
        custom_limit = 50

        allowed, remaining, resets_at = limiter.check_limit(user_id, custom_limit=custom_limit)

        assert remaining == custom_limit

    def test_get_usage_stats(self):
        """Test retrieving usage statistics."""
        limiter = RateLimiter(default_limit_per_day=100)
        user_id = 1

        limiter.increment_usage(user_id, count=25)
        stats = limiter.get_usage_stats(user_id)

        assert stats["user_id"] == user_id
        assert stats["period"] == "day"
        assert stats["limit"] == 100
        assert stats["used"] == 25
        assert stats["remaining"] == 75
        assert stats["allowed"] is True

    def test_reset_user_usage(self):
        """Test resetting usage for a specific user."""
        limiter = RateLimiter(default_limit_per_day=100)
        user_id = 1

        limiter.increment_usage(user_id, count=50)
        limiter.reset_user_usage(user_id)

        allowed, remaining, resets_at = limiter.check_limit(user_id)
        assert remaining == 100

    def test_multiple_users_isolated(self):
        """Test that usage tracking is isolated per user."""
        limiter = RateLimiter(default_limit_per_day=100)
        user1_id = 1
        user2_id = 2

        limiter.increment_usage(user1_id, count=30)
        limiter.increment_usage(user2_id, count=10)

        _, remaining1, _ = limiter.check_limit(user1_id)
        _, remaining2, _ = limiter.check_limit(user2_id)

        assert remaining1 == 70
        assert remaining2 == 90

    def test_resets_at_is_next_day(self):
        """Test that reset time is midnight of next day."""
        limiter = RateLimiter(default_limit_per_day=100)
        user_id = 1

        _, _, resets_at = limiter.check_limit(user_id)

        now = datetime.utcnow()
        expected_reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        # Allow 1 second tolerance
        assert abs((resets_at - expected_reset).total_seconds()) < 1
