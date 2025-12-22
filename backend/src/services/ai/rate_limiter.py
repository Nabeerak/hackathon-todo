"""Rate limiter for AI API requests."""
from datetime import datetime, timedelta
from typing import Optional, Dict
from collections import defaultdict


class RateLimiter:
    """
    Per-user rate limiter for AI requests.

    Default limit: 100 requests per user per day.
    Can be overridden per user via UserPreferences.rate_limit_override.
    """

    def __init__(self, default_limit_per_day: int = 100):
        """
        Initialize rate limiter.

        Args:
            default_limit_per_day: Default request limit per user per day
        """
        self.default_limit_per_day = default_limit_per_day

        # In-memory storage: {user_id: [(timestamp, count), ...]}
        # In production, use Redis for distributed rate limiting
        self._usage: Dict[int, list] = defaultdict(list)

    def check_limit(
        self,
        user_id: int,
        custom_limit: Optional[int] = None
    ) -> tuple[bool, int, datetime]:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: User ID to check
            custom_limit: Custom limit override (from UserPreferences)

        Returns:
            Tuple of (allowed: bool, remaining: int, resets_at: datetime)
        """
        limit = custom_limit if custom_limit else self.default_limit_per_day
        now = datetime.utcnow()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        # Clean up old entries (older than 24 hours)
        self._usage[user_id] = [
            (ts, count) for ts, count in self._usage[user_id]
            if ts >= day_start
        ]

        # Count requests in current day
        total_requests = sum(count for _, count in self._usage[user_id])

        remaining = max(0, limit - total_requests)
        allowed = remaining > 0

        return allowed, remaining, day_end

    def increment_usage(
        self,
        user_id: int,
        count: int = 1
    ) -> None:
        """
        Increment usage counter for user.

        Args:
            user_id: User ID
            count: Number of requests to add (default 1)
        """
        now = datetime.utcnow()
        self._usage[user_id].append((now, count))

    def get_usage_stats(
        self,
        user_id: int,
        custom_limit: Optional[int] = None
    ) -> dict:
        """
        Get detailed usage statistics for user.

        Args:
            user_id: User ID
            custom_limit: Custom limit override

        Returns:
            Dictionary with usage statistics
        """
        allowed, remaining, resets_at = self.check_limit(user_id, custom_limit)
        limit = custom_limit if custom_limit else self.default_limit_per_day

        now = datetime.utcnow()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Count requests in current day
        usage_today = [
            (ts, count) for ts, count in self._usage[user_id]
            if ts >= day_start
        ]
        total_requests = sum(count for _, count in usage_today)

        return {
            "user_id": user_id,
            "period": "day",
            "limit": limit,
            "used": total_requests,
            "remaining": remaining,
            "resets_at": resets_at.isoformat(),
            "allowed": allowed
        }

    def reset_user_usage(self, user_id: int) -> None:
        """
        Reset usage counter for a specific user.

        Args:
            user_id: User ID to reset
        """
        self._usage[user_id] = []

    def reset_all_usage(self) -> None:
        """Reset usage counters for all users (use with caution)."""
        self._usage.clear()


# Global rate limiter instance
# In production, replace with Redis-backed implementation
rate_limiter = RateLimiter(default_limit_per_day=100)
