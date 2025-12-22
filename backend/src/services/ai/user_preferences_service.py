"""User preferences service for AI personalization and learning."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlmodel import Session, select
import logging
import re

from src.models import UserPreferences, Task
from src.db import get_session

logger = logging.getLogger(__name__)


class UserPreferencesService:
    """
    Service for managing user preferences and learned patterns.

    Handles shortcut learning, phrase recognition, and preference management
    for AI personalization.
    """

    def __init__(self, user_id: int, db_session: Optional[Session] = None):
        """
        Initialize user preferences service.

        Args:
            user_id: User ID for preference isolation
            db_session: Optional database session (for dependency injection)
        """
        self.user_id = user_id
        self.db_session = db_session

    async def update_learned_shortcuts(
        self,
        shortcut_name: str,
        task_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store user-defined shortcuts in JSONB field (T086).

        Allows users to define custom shortcuts for frequently created tasks.
        Shortcuts map a shortcut name to full task parameters.

        Args:
            shortcut_name: Name of the shortcut (e.g., "usual review", "standup")
            task_params: Task parameters to associate with shortcut:
                {
                    "title": str,
                    "description": str,
                    "priority": str,
                    "due_date_offset_days": int  # Optional: days from now
                }

        Returns:
            Dictionary with update result:
            {
                "success": True,
                "shortcut_name": str,
                "shortcut_params": {...},
                "updated_at": datetime
            }

        Examples:
            >>> service = UserPreferencesService(user_id=1)
            >>> result = await service.update_learned_shortcuts(
            ...     shortcut_name="usual review",
            ...     task_params={
            ...         "title": "Code review",
            ...         "description": "Review PRs",
            ...         "priority": "high"
            ...     }
            ... )
            >>> result["success"]
            True
        """
        try:
            if self.db_session:
                return await self._update_learned_shortcuts_impl(
                    shortcut_name, task_params, self.db_session
                )
            else:
                with get_session() as db:
                    return await self._update_learned_shortcuts_impl(
                        shortcut_name, task_params, db
                    )

        except Exception as e:
            logger.error(
                f"Error updating learned shortcuts for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {
                "success": False,
                "error": str(e)
            }

    async def _update_learned_shortcuts_impl(
        self,
        shortcut_name: str,
        task_params: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of update_learned_shortcuts."""
        # Normalize shortcut name
        normalized_name = shortcut_name.lower().strip()

        # Get or create UserPreferences for user
        statement = select(UserPreferences).where(
            UserPreferences.user_id == self.user_id
        )
        preferences = db.exec(statement).first()

        if not preferences:
            # Create new UserPreferences record
            preferences = UserPreferences(
                user_id=self.user_id,
                learned_shortcuts={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(preferences)

        # Update learned_shortcuts JSONB field
        shortcuts = preferences.learned_shortcuts or {}
        shortcuts[normalized_name] = {
            **task_params,
            "learned_at": datetime.utcnow().isoformat(),
            "usage_count": shortcuts.get(normalized_name, {}).get("usage_count", 0)
        }

        preferences.learned_shortcuts = shortcuts
        preferences.updated_at = datetime.utcnow()

        db.add(preferences)
        db.commit()
        db.refresh(preferences)

        logger.info(
            f"Learned shortcut updated for user {self.user_id}: "
            f"'{normalized_name}' → {task_params.get('title', 'untitled')}"
        )

        return {
            "success": True,
            "shortcut_name": normalized_name,
            "shortcut_params": shortcuts[normalized_name],
            "updated_at": preferences.updated_at.isoformat()
        }

    async def get_shortcut(self, shortcut_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a learned shortcut by name.

        Args:
            shortcut_name: Name of the shortcut to retrieve

        Returns:
            Shortcut parameters if found, None otherwise
        """
        try:
            if self.db_session:
                return await self._get_shortcut_impl(shortcut_name, self.db_session)
            else:
                with get_session() as db:
                    return await self._get_shortcut_impl(shortcut_name, db)

        except Exception as e:
            logger.error(
                f"Error getting shortcut for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return None

    async def _get_shortcut_impl(
        self,
        shortcut_name: str,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """Internal implementation of get_shortcut."""
        normalized_name = shortcut_name.lower().strip()

        statement = select(UserPreferences).where(
            UserPreferences.user_id == self.user_id
        )
        preferences = db.exec(statement).first()

        if not preferences or not preferences.learned_shortcuts:
            return None

        return preferences.learned_shortcuts.get(normalized_name)

    async def increment_shortcut_usage(self, shortcut_name: str) -> Dict[str, Any]:
        """
        Increment usage count for a shortcut.

        Args:
            shortcut_name: Name of the shortcut

        Returns:
            Update result dictionary
        """
        try:
            if self.db_session:
                return await self._increment_shortcut_usage_impl(
                    shortcut_name, self.db_session
                )
            else:
                with get_session() as db:
                    return await self._increment_shortcut_usage_impl(
                        shortcut_name, db
                    )

        except Exception as e:
            logger.error(
                f"Error incrementing shortcut usage for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {"success": False, "error": str(e)}

    async def _increment_shortcut_usage_impl(
        self,
        shortcut_name: str,
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of increment_shortcut_usage."""
        normalized_name = shortcut_name.lower().strip()

        statement = select(UserPreferences).where(
            UserPreferences.user_id == self.user_id
        )
        preferences = db.exec(statement).first()

        if not preferences or not preferences.learned_shortcuts:
            return {"success": False, "error": "Shortcut not found"}

        shortcuts = preferences.learned_shortcuts
        if normalized_name not in shortcuts:
            return {"success": False, "error": "Shortcut not found"}

        shortcuts[normalized_name]["usage_count"] = (
            shortcuts[normalized_name].get("usage_count", 0) + 1
        )
        shortcuts[normalized_name]["last_used_at"] = datetime.utcnow().isoformat()

        preferences.learned_shortcuts = shortcuts
        preferences.updated_at = datetime.utcnow()

        db.add(preferences)
        db.commit()

        return {
            "success": True,
            "usage_count": shortcuts[normalized_name]["usage_count"]
        }

    async def recognize_shorthand_phrase(
        self,
        user_input: str
    ) -> Optional[Dict[str, Any]]:
        """
        Map user shorthand phrases to actions (T088).

        Recognizes common shorthand phrases like:
        - "done" → complete action
        - "finished" → complete action
        - "del" → delete action
        - "remove" → delete action
        - "check" → query action

        Also checks for learned shortcuts like "usual [X]" or custom phrases.

        Args:
            user_input: User's natural language input

        Returns:
            Dictionary with recognized action:
            {
                "action_type": str,  # "complete", "delete", "query", "create"
                "matched_phrase": str,
                "confidence": float,
                "shortcut_params": dict  # If matched a learned shortcut
            }

            Returns None if no shorthand recognized.

        Examples:
            >>> service = UserPreferencesService(user_id=1)
            >>> result = await service.recognize_shorthand_phrase("done with groceries")
            >>> result["action_type"]
            "complete"

            >>> result = await service.recognize_shorthand_phrase("add usual review task")
            >>> result["action_type"]
            "create"
            >>> result["shortcut_params"]["title"]
            "Code review"
        """
        try:
            if self.db_session:
                return await self._recognize_shorthand_phrase_impl(
                    user_input, self.db_session
                )
            else:
                with get_session() as db:
                    return await self._recognize_shorthand_phrase_impl(
                        user_input, db
                    )

        except Exception as e:
            logger.error(
                f"Error recognizing shorthand phrase for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return None

    async def _recognize_shorthand_phrase_impl(
        self,
        user_input: str,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """Internal implementation of recognize_shorthand_phrase."""
        input_lower = user_input.lower().strip()

        # Define shorthand mappings
        completion_phrases = [
            r'\b(done|finished|completed?|finish)\b',
            r'\bmark.*(?:done|complete)',
            r'\b(finish|complete).*(?:with|up)\b'
        ]

        delete_phrases = [
            r'\b(del|delete|remove|cancel)\b',
            r'\bget rid of\b',
            r'\bdrop\b'
        ]

        query_phrases = [
            r'\b(check|show|list|what|find)\b',
            r'\bwhat.*tasks?\b',
            r'\bshow.*(?:me|tasks?)\b'
        ]

        # Check completion phrases
        for pattern in completion_phrases:
            if re.search(pattern, input_lower):
                return {
                    "action_type": "complete",
                    "matched_phrase": re.search(pattern, input_lower).group(0),
                    "confidence": 0.9,
                    "shortcut_params": None
                }

        # Check delete phrases
        for pattern in delete_phrases:
            if re.search(pattern, input_lower):
                return {
                    "action_type": "delete",
                    "matched_phrase": re.search(pattern, input_lower).group(0),
                    "confidence": 0.9,
                    "shortcut_params": None
                }

        # Check query phrases
        for pattern in query_phrases:
            if re.search(pattern, input_lower):
                return {
                    "action_type": "query",
                    "matched_phrase": re.search(pattern, input_lower).group(0),
                    "confidence": 0.8,
                    "shortcut_params": None
                }

        # Check for learned shortcuts (e.g., "usual review", "add standup")
        statement = select(UserPreferences).where(
            UserPreferences.user_id == self.user_id
        )
        preferences = db.exec(statement).first()

        if preferences and preferences.learned_shortcuts:
            # Check for "usual [shortcut]" pattern
            usual_match = re.search(r'\busual\s+(\w+(?:\s+\w+)?)', input_lower)
            if usual_match:
                shortcut_name = usual_match.group(1)
                if shortcut_name in preferences.learned_shortcuts:
                    return {
                        "action_type": "create",
                        "matched_phrase": f"usual {shortcut_name}",
                        "confidence": 0.95,
                        "shortcut_params": preferences.learned_shortcuts[shortcut_name]
                    }

            # Check for direct shortcut matches
            for shortcut_name, params in preferences.learned_shortcuts.items():
                # Look for the shortcut name in the input
                if shortcut_name in input_lower:
                    # Higher confidence if preceded by "add" or "create"
                    if re.search(r'\b(add|create)\s+' + re.escape(shortcut_name), input_lower):
                        confidence = 0.95
                    else:
                        confidence = 0.85

                    return {
                        "action_type": "create",
                        "matched_phrase": shortcut_name,
                        "confidence": confidence,
                        "shortcut_params": params
                    }

        # No shorthand recognized
        return None

    async def get_all_shortcuts(self) -> Dict[str, Any]:
        """
        Get all learned shortcuts for the user.

        Returns:
            Dictionary with all shortcuts:
            {
                "success": True,
                "shortcuts": {
                    "shortcut_name": {...},
                    ...
                }
            }
        """
        try:
            if self.db_session:
                return await self._get_all_shortcuts_impl(self.db_session)
            else:
                with get_session() as db:
                    return await self._get_all_shortcuts_impl(db)

        except Exception as e:
            logger.error(
                f"Error getting all shortcuts for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {"success": False, "error": str(e), "shortcuts": {}}

    async def _get_all_shortcuts_impl(self, db: Session) -> Dict[str, Any]:
        """Internal implementation of get_all_shortcuts."""
        statement = select(UserPreferences).where(
            UserPreferences.user_id == self.user_id
        )
        preferences = db.exec(statement).first()

        if not preferences:
            return {"success": True, "shortcuts": {}}

        return {
            "success": True,
            "shortcuts": preferences.learned_shortcuts or {}
        }

    async def get_preferences(self) -> Optional[Dict[str, Any]]:
        """
        Get all user preferences.

        Returns:
            Dictionary with user preferences or None if not found
        """
        try:
            if self.db_session:
                return await self._get_preferences_impl(self.db_session)
            else:
                with get_session() as db:
                    return await self._get_preferences_impl(db)

        except Exception as e:
            logger.error(
                f"Error getting preferences for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return None

    async def _get_preferences_impl(self, db: Session) -> Optional[Dict[str, Any]]:
        """Internal implementation of get_preferences."""
        statement = select(UserPreferences).where(
            UserPreferences.user_id == self.user_id
        )
        preferences = db.exec(statement).first()

        if not preferences:
            return None

        return {
            "user_id": preferences.user_id,
            "preferred_language": preferences.preferred_language,
            "ai_tone": preferences.ai_tone.value,
            "enable_proactive_suggestions": preferences.enable_proactive_suggestions,
            "learned_shortcuts": preferences.learned_shortcuts or {},
            "ai_features_enabled": preferences.ai_features_enabled,
            "created_at": preferences.created_at.isoformat(),
            "updated_at": preferences.updated_at.isoformat()
        }

    async def update_preferences(
        self,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user preferences.

        Args:
            updates: Dictionary with preference updates:
                {
                    "preferred_language": str,
                    "ai_tone": str,
                    "enable_proactive_suggestions": bool,
                    "ai_features_enabled": bool
                }

        Returns:
            Dictionary with update result
        """
        try:
            if self.db_session:
                return await self._update_preferences_impl(updates, self.db_session)
            else:
                with get_session() as db:
                    return await self._update_preferences_impl(updates, db)

        except Exception as e:
            logger.error(
                f"Error updating preferences for user {self.user_id}: {str(e)}",
                exc_info=True
            )
            return {"success": False, "error": str(e)}

    async def _update_preferences_impl(
        self,
        updates: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Internal implementation of update_preferences."""
        # Get or create UserPreferences
        statement = select(UserPreferences).where(
            UserPreferences.user_id == self.user_id
        )
        preferences = db.exec(statement).first()

        if not preferences:
            preferences = UserPreferences(
                user_id=self.user_id,
                learned_shortcuts={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(preferences)

        # Update allowed fields
        if "preferred_language" in updates:
            preferences.preferred_language = updates["preferred_language"]

        if "ai_tone" in updates:
            from src.models import AITone
            tone_value = updates["ai_tone"].upper()
            if hasattr(AITone, tone_value):
                preferences.ai_tone = getattr(AITone, tone_value)

        if "enable_proactive_suggestions" in updates:
            preferences.enable_proactive_suggestions = updates["enable_proactive_suggestions"]

        if "ai_features_enabled" in updates:
            preferences.ai_features_enabled = updates["ai_features_enabled"]

        preferences.updated_at = datetime.utcnow()

        db.add(preferences)
        db.commit()
        db.refresh(preferences)

        logger.info(f"Preferences updated for user {self.user_id}")

        return {
            "success": True,
            "preferences": {
                "user_id": preferences.user_id,
                "preferred_language": preferences.preferred_language,
                "ai_tone": preferences.ai_tone.value,
                "enable_proactive_suggestions": preferences.enable_proactive_suggestions,
                "ai_features_enabled": preferences.ai_features_enabled,
                "updated_at": preferences.updated_at.isoformat()
            }
        }
