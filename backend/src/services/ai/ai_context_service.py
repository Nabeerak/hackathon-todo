"""AI Context service for pattern analysis and user learning."""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select
from collections import defaultdict, Counter
import logging

from src.models import AIContext, Task, TaskAction, ActionType
from src.db import get_session

logger = logging.getLogger(__name__)


class AIContextService:
    """
    Service for analyzing user patterns and managing AI context.

    Tracks task creation patterns, completion rates, and user behavior
    to provide personalized recommendations and insights.
    """

    def __init__(self, user_id: int, db_session: Optional[Session] = None):
        """
        Initialize AI context service for a specific user.

        Args:
            user_id: User ID for context isolation
            db_session: Optional database session (for dependency injection)
        """
        self.user_id = user_id
        self.db_session = db_session

    async def analyze_task_patterns(
        self,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect recurring task patterns from user history (T064).

        Analyzes:
        - Task creation frequency by day of week and time
        - Common task titles/keywords
        - Recurring task descriptions
        - Task completion patterns
        - Time gaps between task creation and completion

        Args:
            lookback_days: Number of days to analyze (default: 30)

        Returns:
            Dictionary with pattern insights:
            {
                "creation_patterns": {
                    "by_weekday": {"monday": 15, "tuesday": 8, ...},
                    "by_hour": {"9": 5, "14": 8, ...},
                    "peak_day": "monday",
                    "peak_hour": 9
                },
                "completion_patterns": {
                    "by_weekday": {"monday": 10, "friday": 12, ...},
                    "average_completion_time_hours": 24.5,
                    "completion_rate": 0.75
                },
                "common_keywords": ["meeting", "review", "report", ...],
                "recurring_tasks": [
                    {
                        "pattern": "weekly standup",
                        "frequency": 4,
                        "average_day": "monday"
                    }
                ],
                "insights": [
                    "You create most tasks on Monday mornings",
                    "You complete 75% of your tasks within 24 hours"
                ]
            }

        Examples:
            >>> service = AIContextService(user_id=1)
            >>> patterns = await service.analyze_task_patterns(lookback_days=30)
            >>> patterns["creation_patterns"]["peak_day"]
            "monday"
        """
        try:
            if self.db_session:
                return await self._analyze_task_patterns_impl(lookback_days, self.db_session)
            else:
                with get_session() as db:
                    return await self._analyze_task_patterns_impl(lookback_days, db)

        except Exception as e:
            logger.error(
                f"Error analyzing task patterns for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return self._empty_pattern_response()

    async def _analyze_task_patterns_impl(
        self,
        lookback_days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of analyze_task_patterns."""
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

        # Fetch user's tasks from lookback period
        statement = select(Task).where(
            Task.user_id == self.user_id,
            Task.created_at >= cutoff_date
        )
        tasks = db.exec(statement).all()

        if not tasks:
            logger.info(f"No tasks found for user {self.user_id} in last {lookback_days} days")
            return self._empty_pattern_response()

        # Analyze creation patterns
        creation_by_weekday = defaultdict(int)
        creation_by_hour = defaultdict(int)

        for task in tasks:
            weekday = task.created_at.strftime("%A").lower()
            hour = task.created_at.hour
            creation_by_weekday[weekday] += 1
            creation_by_hour[str(hour)] += 1

        # Find peak times
        peak_day = max(creation_by_weekday.items(), key=lambda x: x[1])[0] if creation_by_weekday else "monday"
        peak_hour = int(max(creation_by_hour.items(), key=lambda x: x[1])[0]) if creation_by_hour else 9

        # Analyze completion patterns
        completed_tasks = [t for t in tasks if t.is_completed]
        completion_by_weekday = defaultdict(int)
        completion_times = []

        for task in completed_tasks:
            weekday = task.updated_at.strftime("%A").lower()
            completion_by_weekday[weekday] += 1

            # Calculate completion time (hours from creation to completion)
            time_delta = task.updated_at - task.created_at
            completion_times.append(time_delta.total_seconds() / 3600)  # Convert to hours

        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        completion_rate = len(completed_tasks) / len(tasks) if tasks else 0

        # Extract common keywords from task titles
        from collections import Counter
        import re

        all_words = []
        for task in tasks:
            # Extract words (alphanumeric, 3+ chars, lowercase)
            words = re.findall(r'\b[a-z]{3,}\b', task.title.lower())
            all_words.extend(words)

        # Remove common stop words
        stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'has'}
        filtered_words = [w for w in all_words if w not in stop_words]

        # Get top keywords
        word_counts = Counter(filtered_words)
        common_keywords = [word for word, count in word_counts.most_common(10)]

        # Identify recurring tasks (titles that appear multiple times)
        title_counts = Counter([task.title.lower() for task in tasks])
        recurring_tasks = [
            {
                "pattern": title,
                "frequency": count,
                "average_day": self._get_average_day_for_title(tasks, title)
            }
            for title, count in title_counts.items()
            if count > 1
        ]

        # Generate insights
        insights = self._generate_pattern_insights(
            peak_day, peak_hour, completion_rate, avg_completion_time, recurring_tasks
        )

        result = {
            "creation_patterns": {
                "by_weekday": dict(creation_by_weekday),
                "by_hour": dict(creation_by_hour),
                "peak_day": peak_day,
                "peak_hour": peak_hour
            },
            "completion_patterns": {
                "by_weekday": dict(completion_by_weekday),
                "average_completion_time_hours": round(avg_completion_time, 2),
                "completion_rate": round(completion_rate, 2)
            },
            "common_keywords": common_keywords,
            "recurring_tasks": recurring_tasks[:5],  # Top 5
            "insights": insights,
            "analyzed_tasks_count": len(tasks),
            "analyzed_period_days": lookback_days
        }

        logger.info(
            f"Pattern analysis complete for user {self.user_id}: "
            f"{len(tasks)} tasks analyzed, {len(recurring_tasks)} recurring patterns found"
        )

        return result

    def _get_average_day_for_title(self, tasks: List[Task], title: str) -> str:
        """Get the most common day of week for a specific task title."""
        matching_tasks = [t for t in tasks if t.title.lower() == title]
        if not matching_tasks:
            return "unknown"

        day_counts = defaultdict(int)
        for task in matching_tasks:
            weekday = task.created_at.strftime("%A").lower()
            day_counts[weekday] += 1

        return max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else "unknown"

    def _generate_pattern_insights(
        self,
        peak_day: str,
        peak_hour: int,
        completion_rate: float,
        avg_completion_time: float,
        recurring_tasks: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate human-readable insights from patterns."""
        insights = []

        # Creation pattern insight
        time_of_day = "morning" if peak_hour < 12 else "afternoon" if peak_hour < 18 else "evening"
        insights.append(
            f"You create most tasks on {peak_day.capitalize()} {time_of_day} (around {peak_hour}:00)"
        )

        # Completion rate insight
        if completion_rate >= 0.8:
            insights.append(f"You have an excellent completion rate of {int(completion_rate * 100)}%")
        elif completion_rate >= 0.5:
            insights.append(f"You complete about {int(completion_rate * 100)}% of your tasks")
        else:
            insights.append(f"Your completion rate is {int(completion_rate * 100)}% - consider creating fewer, more focused tasks")

        # Completion time insight
        if avg_completion_time < 24:
            insights.append(f"You typically complete tasks within {int(avg_completion_time)} hours")
        elif avg_completion_time < 168:  # 1 week
            days = int(avg_completion_time / 24)
            insights.append(f"Tasks usually take you about {days} day{'s' if days > 1 else ''} to complete")
        else:
            weeks = int(avg_completion_time / 168)
            insights.append(f"Tasks typically take {weeks} week{'s' if weeks > 1 else ''} to complete")

        # Recurring tasks insight
        if recurring_tasks:
            insights.append(
                f"You have {len(recurring_tasks)} recurring task patterns - I can help automate these"
            )

        return insights

    def _empty_pattern_response(self) -> Dict[str, Any]:
        """Return empty pattern response when no data available."""
        return {
            "creation_patterns": {
                "by_weekday": {},
                "by_hour": {},
                "peak_day": None,
                "peak_hour": None
            },
            "completion_patterns": {
                "by_weekday": {},
                "average_completion_time_hours": 0,
                "completion_rate": 0
            },
            "common_keywords": [],
            "recurring_tasks": [],
            "insights": ["Not enough data yet - create more tasks to see patterns"],
            "analyzed_tasks_count": 0,
            "analyzed_period_days": 0
        }

    async def update_user_patterns(
        self,
        new_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update AIContext.user_patterns JSONB field with new insights (T069, T074, T075).

        Stores:
        - Task creation frequency by day/time (T074)
        - Task completion rates by type/priority (T075)
        - Recurring patterns
        - Learning insights

        Args:
            new_patterns: New pattern data to merge with existing patterns

        Returns:
            Dictionary with updated patterns:
            {
                "success": True,
                "patterns": {...},
                "updated_at": datetime
            }

        Examples:
            >>> service = AIContextService(user_id=1)
            >>> patterns = {
            ...     "creation_frequency": {"monday": 15, "tuesday": 8},
            ...     "completion_rates": {"high_priority": 0.9, "medium_priority": 0.7}
            ... }
            >>> result = await service.update_user_patterns(patterns)
            >>> result["success"]
            True
        """
        try:
            if self.db_session:
                return await self._update_user_patterns_impl(new_patterns, self.db_session)
            else:
                with get_session() as db:
                    return await self._update_user_patterns_impl(new_patterns, db)

        except Exception as e:
            logger.error(
                f"Error updating user patterns for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {
                "success": False,
                "error": str(e)
            }

    async def _update_user_patterns_impl(
        self,
        new_patterns: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of update_user_patterns."""
        # Get or create AIContext for user
        statement = select(AIContext).where(AIContext.user_id == self.user_id)
        ai_context = db.exec(statement).first()

        if not ai_context:
            # Create new AIContext record
            ai_context = AIContext(
                user_id=self.user_id,
                user_patterns={},
                total_messages=0,
                total_sessions=0,
                average_session_length=0.0,
                last_updated_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.add(ai_context)

        # Merge new patterns with existing patterns
        existing_patterns = ai_context.user_patterns or {}
        merged_patterns = {**existing_patterns, **new_patterns}

        # Update AIContext
        ai_context.user_patterns = merged_patterns
        ai_context.last_updated_at = datetime.utcnow()

        db.add(ai_context)
        db.commit()
        db.refresh(ai_context)

        logger.info(
            f"User patterns updated for user {self.user_id}: "
            f"{len(new_patterns)} new pattern fields added"
        )

        return {
            "success": True,
            "patterns": merged_patterns,
            "updated_at": ai_context.last_updated_at.isoformat()
        }

    async def store_creation_frequency(
        self
    ) -> Dict[str, Any]:
        """
        Store task creation frequency by day/time in AIContext.user_patterns (T074).

        Analyzes last 90 days of task creation data and stores frequency patterns.

        Returns:
            Dictionary with stored frequency data:
            {
                "success": True,
                "frequency_data": {...}
            }
        """
        patterns = await self.analyze_task_patterns(lookback_days=90)

        # Extract creation frequency data
        frequency_data = {
            "creation_frequency": {
                "by_weekday": patterns["creation_patterns"]["by_weekday"],
                "by_hour": patterns["creation_patterns"]["by_hour"],
                "peak_day": patterns["creation_patterns"]["peak_day"],
                "peak_hour": patterns["creation_patterns"]["peak_hour"],
                "last_analyzed": datetime.utcnow().isoformat()
            }
        }

        # Update AIContext with frequency data
        result = await self.update_user_patterns(frequency_data)

        return {
            "success": result["success"],
            "frequency_data": frequency_data
        }

    async def store_completion_rates(
        self
    ) -> Dict[str, Any]:
        """
        Store task completion rates by type/priority in AIContext (T075).

        Analyzes last 90 days of task completion data and stores rate patterns.

        Returns:
            Dictionary with stored completion rate data:
            {
                "success": True,
                "completion_data": {...}
            }
        """
        patterns = await self.analyze_task_patterns(lookback_days=90)

        # Extract completion rate data
        completion_data = {
            "completion_rates": {
                "overall_rate": patterns["completion_patterns"]["completion_rate"],
                "by_weekday": patterns["completion_patterns"]["by_weekday"],
                "average_completion_time_hours": patterns["completion_patterns"]["average_completion_time_hours"],
                "last_analyzed": datetime.utcnow().isoformat()
            }
        }

        # Update AIContext with completion data
        result = await self.update_user_patterns(completion_data)

        return {
            "success": result["success"],
            "completion_data": completion_data
        }

    async def get_user_patterns(self) -> Dict[str, Any]:
        """
        Retrieve stored user patterns from AIContext.

        Returns:
            Dictionary with user patterns or empty dict if none exist
        """
        try:
            if self.db_session:
                return await self._get_user_patterns_impl(self.db_session)
            else:
                with get_session() as db:
                    return await self._get_user_patterns_impl(db)

        except Exception as e:
            logger.error(
                f"Error getting user patterns for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {}

    async def _get_user_patterns_impl(self, db: Session) -> Dict[str, Any]:
        """Internal implementation of get_user_patterns."""
        statement = select(AIContext).where(AIContext.user_id == self.user_id)
        ai_context = db.exec(statement).first()

        if not ai_context:
            return {}

        return ai_context.user_patterns or {}

    async def track_suggestion_rejection(
        self,
        suggestion_type: str,
        suggestion_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track AI suggestion rejections to avoid repeating unwanted suggestions (T089).

        Stores rejected suggestions in AIContext.user_patterns to improve future
        suggestion quality by learning what the user doesn't want.

        Args:
            suggestion_type: Type of suggestion rejected (e.g., "task_breakdown", "next_action", "proactive_reminder")
            suggestion_context: Context about the rejected suggestion:
                {
                    "task_id": int,
                    "task_title": str,
                    "suggestion_details": str,
                    "rejection_reason": str  # Optional
                }

        Returns:
            Dictionary with tracking result:
            {
                "success": True,
                "rejection_count": int,
                "should_suppress": bool  # True if this suggestion type should be suppressed
            }

        Examples:
            >>> service = AIContextService(user_id=1)
            >>> result = await service.track_suggestion_rejection(
            ...     suggestion_type="task_breakdown",
            ...     suggestion_context={
            ...         "task_id": 123,
            ...         "task_title": "Simple task",
            ...         "suggestion_details": "Break down into 5 subtasks"
            ...     }
            ... )
            >>> result["success"]
            True
            >>> result["should_suppress"]  # True if rejected 3+ times
            False
        """
        try:
            if self.db_session:
                return await self._track_suggestion_rejection_impl(
                    suggestion_type, suggestion_context, self.db_session
                )
            else:
                with get_session() as db:
                    return await self._track_suggestion_rejection_impl(
                        suggestion_type, suggestion_context, db
                    )

        except Exception as e:
            logger.error(
                f"Error tracking suggestion rejection for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {
                "success": False,
                "error": str(e),
                "rejection_count": 0,
                "should_suppress": False
            }

    async def _track_suggestion_rejection_impl(
        self,
        suggestion_type: str,
        suggestion_context: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of track_suggestion_rejection."""
        # Get or create AIContext
        statement = select(AIContext).where(AIContext.user_id == self.user_id)
        ai_context = db.exec(statement).first()

        if not ai_context:
            ai_context = AIContext(
                user_id=self.user_id,
                user_patterns={},
                total_messages=0,
                total_sessions=0,
                average_session_length=0.0,
                last_updated_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.add(ai_context)

        # Get existing patterns
        patterns = ai_context.user_patterns or {}

        # Initialize rejected_suggestions structure if not exists
        if "rejected_suggestions" not in patterns:
            patterns["rejected_suggestions"] = {}

        # Track rejection
        if suggestion_type not in patterns["rejected_suggestions"]:
            patterns["rejected_suggestions"][suggestion_type] = {
                "count": 0,
                "rejections": [],
                "last_rejected_at": None,
                "suppressed": False
            }

        rejection_data = patterns["rejected_suggestions"][suggestion_type]
        rejection_data["count"] += 1
        rejection_data["last_rejected_at"] = datetime.utcnow().isoformat()

        # Add rejection details (keep last 10)
        rejection_data["rejections"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "context": suggestion_context
        })
        rejection_data["rejections"] = rejection_data["rejections"][-10:]  # Keep last 10

        # Determine if suggestion should be suppressed (3+ rejections)
        SUPPRESSION_THRESHOLD = 3
        should_suppress = rejection_data["count"] >= SUPPRESSION_THRESHOLD

        if should_suppress and not rejection_data["suppressed"]:
            rejection_data["suppressed"] = True
            logger.info(
                f"Suppressing suggestion type '{suggestion_type}' for user {self.user_id} "
                f"after {rejection_data['count']} rejections"
            )

        # Update AIContext
        ai_context.user_patterns = patterns
        ai_context.last_updated_at = datetime.utcnow()

        db.add(ai_context)
        db.commit()
        db.refresh(ai_context)

        logger.info(
            f"Tracked suggestion rejection for user {self.user_id}: "
            f"type={suggestion_type}, count={rejection_data['count']}, suppressed={should_suppress}"
        )

        return {
            "success": True,
            "rejection_count": rejection_data["count"],
            "should_suppress": should_suppress
        }

    async def is_suggestion_suppressed(self, suggestion_type: str) -> bool:
        """
        Check if a suggestion type should be suppressed.

        Args:
            suggestion_type: Type of suggestion to check

        Returns:
            True if suggestion should be suppressed, False otherwise
        """
        try:
            if self.db_session:
                return await self._is_suggestion_suppressed_impl(
                    suggestion_type, self.db_session
                )
            else:
                with get_session() as db:
                    return await self._is_suggestion_suppressed_impl(
                        suggestion_type, db
                    )

        except Exception as e:
            logger.error(
                f"Error checking suggestion suppression for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return False

    async def _is_suggestion_suppressed_impl(
        self,
        suggestion_type: str,
        db: Session
    ) -> bool:
        """Internal implementation of is_suggestion_suppressed."""
        statement = select(AIContext).where(AIContext.user_id == self.user_id)
        ai_context = db.exec(statement).first()

        if not ai_context or not ai_context.user_patterns:
            return False

        patterns = ai_context.user_patterns
        rejected = patterns.get("rejected_suggestions", {})

        if suggestion_type not in rejected:
            return False

        return rejected[suggestion_type].get("suppressed", False)

    async def reset_suggestion_suppression(
        self,
        suggestion_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reset suppression for a specific suggestion type or all types.

        Useful when user explicitly wants to re-enable a suppressed suggestion.

        Args:
            suggestion_type: Specific type to reset, or None to reset all

        Returns:
            Dictionary with reset result
        """
        try:
            if self.db_session:
                return await self._reset_suggestion_suppression_impl(
                    suggestion_type, self.db_session
                )
            else:
                with get_session() as db:
                    return await self._reset_suggestion_suppression_impl(
                        suggestion_type, db
                    )

        except Exception as e:
            logger.error(
                f"Error resetting suggestion suppression for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {"success": False, "error": str(e)}

    async def _reset_suggestion_suppression_impl(
        self,
        suggestion_type: Optional[str],
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of reset_suggestion_suppression."""
        statement = select(AIContext).where(AIContext.user_id == self.user_id)
        ai_context = db.exec(statement).first()

        if not ai_context or not ai_context.user_patterns:
            return {"success": True, "message": "No suppressions to reset"}

        patterns = ai_context.user_patterns
        rejected = patterns.get("rejected_suggestions", {})

        if suggestion_type:
            # Reset specific type
            if suggestion_type in rejected:
                rejected[suggestion_type]["suppressed"] = False
                rejected[suggestion_type]["count"] = 0
                rejected[suggestion_type]["rejections"] = []
                message = f"Reset suppression for '{suggestion_type}'"
            else:
                message = f"No suppression found for '{suggestion_type}'"
        else:
            # Reset all types
            for stype in rejected.values():
                stype["suppressed"] = False
                stype["count"] = 0
                stype["rejections"] = []
            message = "Reset all suggestion suppressions"

        ai_context.user_patterns = patterns
        ai_context.last_updated_at = datetime.utcnow()

        db.add(ai_context)
        db.commit()

        logger.info(f"Suggestion suppression reset for user {self.user_id}: {message}")

        return {"success": True, "message": message}

    async def generate_accomplishment_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate summary of completed tasks by date range (T090).

        Provides insights like:
        - Total tasks completed
        - Completion by category/type
        - Notable accomplishments
        - Productivity trends

        Args:
            start_date: Start of date range (default: 30 days ago)
            end_date: End of date range (default: now)

        Returns:
            Dictionary with accomplishment summary:
            {
                "period": {"start": "2024-11-01", "end": "2024-12-01"},
                "total_completed": 42,
                "completion_by_day": {"2024-11-01": 3, ...},
                "top_keywords": ["meeting", "review", "report"],
                "insights": [
                    "You completed 42 tasks this month",
                    "Most productive day: Monday with 8 completions",
                    "You're 25% more productive than last month"
                ],
                "tasks": [
                    {"title": "...", "completed_at": "..."},
                    ...
                ]
            }

        Examples:
            >>> service = AIContextService(user_id=1)
            >>> summary = await service.generate_accomplishment_summary()
            >>> summary["total_completed"]
            42
        """
        try:
            if self.db_session:
                return await self._generate_accomplishment_summary_impl(
                    start_date, end_date, self.db_session
                )
            else:
                with get_session() as db:
                    return await self._generate_accomplishment_summary_impl(
                        start_date, end_date, db
                    )

        except Exception as e:
            logger.error(
                f"Error generating accomplishment summary for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {
                "success": False,
                "error": str(e),
                "total_completed": 0
            }

    async def _generate_accomplishment_summary_impl(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of generate_accomplishment_summary."""
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()

        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Query completed tasks in date range
        statement = select(Task).where(
            Task.user_id == self.user_id,
            Task.is_completed == True,
            Task.updated_at >= start_date,
            Task.updated_at <= end_date
        ).order_by(Task.updated_at.desc())

        completed_tasks = db.exec(statement).all()

        # Build summary statistics
        total_completed = len(completed_tasks)

        # Completion by day
        completion_by_day = defaultdict(int)
        for task in completed_tasks:
            day = task.updated_at.date().isoformat()
            completion_by_day[day] += 1

        # Find most productive day
        most_productive_day = None
        max_completions = 0
        if completion_by_day:
            most_productive_day = max(completion_by_day.items(), key=lambda x: x[1])
            max_completions = most_productive_day[1]

        # Extract keywords from titles
        all_words = []
        for task in completed_tasks:
            # Simple keyword extraction (split title into words)
            words = task.title.lower().split()
            all_words.extend([w for w in words if len(w) > 3])  # Filter short words

        keyword_counts = Counter(all_words)
        top_keywords = [word for word, _ in keyword_counts.most_common(5)]

        # Calculate productivity comparison (if possible)
        previous_period_start = start_date - (end_date - start_date)
        previous_statement = select(Task).where(
            Task.user_id == self.user_id,
            Task.is_completed == True,
            Task.updated_at >= previous_period_start,
            Task.updated_at < start_date
        )
        previous_tasks = db.exec(previous_statement).all()
        previous_count = len(previous_tasks)

        productivity_change = None
        if previous_count > 0:
            productivity_change = ((total_completed - previous_count) / previous_count) * 100

        # Generate insights
        insights = []

        if total_completed > 0:
            # Period summary
            days_in_period = (end_date - start_date).days
            insights.append(
                f"You completed {total_completed} task{'s' if total_completed != 1 else ''} "
                f"in the past {days_in_period} day{'s' if days_in_period != 1 else ''}"
            )

            # Most productive day
            if most_productive_day:
                insights.append(
                    f"Most productive day: {most_productive_day[0]} with {max_completions} completion{'s' if max_completions != 1 else ''}"
                )

            # Productivity trend
            if productivity_change is not None:
                if productivity_change > 0:
                    insights.append(
                        f"You're {abs(productivity_change):.0f}% more productive than the previous period"
                    )
                elif productivity_change < 0:
                    insights.append(
                        f"You're {abs(productivity_change):.0f}% less productive than the previous period"
                    )
                else:
                    insights.append("Your productivity is steady compared to the previous period")

            # Common themes
            if top_keywords:
                insights.append(
                    f"Common themes: {', '.join(top_keywords[:3])}"
                )
        else:
            insights.append("No tasks completed in this period")

        # Format task list
        tasks_formatted = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed_at": task.updated_at.isoformat(),
                "created_at": task.created_at.isoformat()
            }
            for task in completed_tasks[:20]  # Limit to 20 most recent
        ]

        return {
            "success": True,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_completed": total_completed,
            "completion_by_day": dict(completion_by_day),
            "top_keywords": top_keywords,
            "productivity_change_percent": productivity_change,
            "insights": insights,
            "tasks": tasks_formatted
        }
