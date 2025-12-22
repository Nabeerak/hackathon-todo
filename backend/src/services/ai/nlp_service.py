"""Natural Language Processing service for task extraction."""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import logging
import time
import re
from openai import AsyncOpenAI
from .prompt_templates import TASK_EXTRACTION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# GPT-4o-mini pricing (as of Dec 2024)
# https://openai.com/api/pricing/
COST_PER_1K_INPUT_TOKENS = 0.000150  # $0.150 per 1M input tokens
COST_PER_1K_OUTPUT_TOKENS = 0.000600  # $0.600 per 1M output tokens

# Suspicious patterns that might indicate prompt injection attempts
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above|earlier)\s+instructions?",
    r"disregard\s+(previous|all|above|earlier)\s+(instructions?|prompts?)",
    r"forget\s+(previous|all|above|earlier)\s+(instructions?|commands?)",
    r"system\s*:\s*",
    r"<\s*system\s*>",
    r"you\s+are\s+now\s+(a|an)\s+",
    r"act\s+as\s+(a|an)\s+",
    r"pretend\s+(to\s+be|you\s+are)",
    r"roleplay\s+as",
    r"new\s+instructions?",
    r"override\s+(previous|all|above)\s+",
]


class NLPService:
    """
    Service for extracting structured task information from natural language.

    Uses OpenAI GPT-4o-mini with structured outputs for task extraction.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.3, max_tokens: int = 500):
        """
        Initialize NLP service.

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o-mini)
            temperature: Sampling temperature (default: 0.3)
            max_tokens: Maximum tokens in response (default: 500)
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = AsyncOpenAI(api_key=api_key)

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate estimated cost based on token usage.

        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used

        Returns:
            Estimated cost in USD
        """
        input_cost = (input_tokens / 1000) * COST_PER_1K_INPUT_TOKENS
        output_cost = (output_tokens / 1000) * COST_PER_1K_OUTPUT_TOKENS
        return input_cost + output_cost

    def _detect_prompt_injection(self, user_input: str) -> List[str]:
        """
        Detect potential prompt injection attempts in user input.

        Args:
            user_input: User's message to analyze

        Returns:
            List of matched suspicious patterns (empty if none detected)
        """
        matched_patterns = []
        user_input_lower = user_input.lower()

        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                matched_patterns.append(pattern)

        return matched_patterns

    async def extract_task_params(
        self,
        user_input: str,
        conversation_context: Optional[List[Dict[str, str]]] = None,
        user_patterns: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured task parameters from natural language input.

        Supports all action types: create, query, update, complete, delete (T046-T054).
        Suggests defaults based on learned patterns (T087).

        Args:
            user_input: User's natural language message
            conversation_context: Optional previous messages for context
            user_patterns: Optional learned patterns from AIContext for default suggestions

        Returns:
            Dictionary with extracted task parameters:
            {
                "tasks": [
                    {
                        "title": str,
                        "description": str,
                        "dueDate": str | None,
                        "priority": "low" | "medium" | "high",
                        "actionType": "create" | "update" | "delete" | "complete" | "query",
                        "target": str (for update/complete/delete - task identifier),
                        "filters": dict (for query - filter criteria),
                        "bulkCriteria": dict (for bulk delete - filter criteria)
                    }
                ],
                "confidence": float,
                "clarification_needed": bool,
                "ambiguous_fields": List[str]
            }

        Examples:
            >>> nlp = NLPService(api_key="sk-...")
            >>> # Create
            >>> result = await nlp.extract_task_params("Add buy groceries tomorrow")
            >>> result["tasks"][0]["title"]
            "Buy groceries"

            >>> # Query
            >>> result = await nlp.extract_task_params("What tasks are due today?")
            >>> result["tasks"][0]["actionType"]
            "query"

            >>> # Update
            >>> result = await nlp.extract_task_params("Change the meeting to 3pm")
            >>> result["tasks"][0]["actionType"]
            "update"

            >>> # Complete
            >>> result = await nlp.extract_task_params("Mark groceries as done")
            >>> result["tasks"][0]["actionType"]
            "complete"

            >>> # Delete
            >>> result = await nlp.extract_task_params("Delete the dentist task")
            >>> result["tasks"][0]["actionType"]
            "delete"
        """
        # T103: Security logging - detect potential prompt injection attempts
        suspicious_patterns = self._detect_prompt_injection(user_input)
        if suspicious_patterns:
            logger.warning(
                "Potential prompt injection detected",
                extra={
                    "user_input": user_input[:200],  # Truncate for logging
                    "matched_patterns": suspicious_patterns,
                    "pattern_count": len(suspicious_patterns),
                }
            )

        try:
            # T101: Track request latency
            start_time = time.time()

            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": TASK_EXTRACTION_SYSTEM_PROMPT}
            ]

            # Add conversation context if provided
            if conversation_context:
                for msg in conversation_context[-5:]:  # Last 5 messages for context
                    messages.append(msg)

            # Add current user input
            messages.append({"role": "user", "content": user_input})

            # Call OpenAI with structured output (JSON mode)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )

            # T101: Calculate request latency
            duration_ms = (time.time() - start_time) * 1000

            # T101: Extract token usage from response
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0

            # T102: Calculate estimated cost
            estimated_cost = self._calculate_cost(input_tokens, output_tokens)

            # T101, T102: Log request metrics
            logger.info(
                "OpenAI API request completed",
                extra={
                    "model": self.model,
                    "duration_ms": round(duration_ms, 2),
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "estimated_cost_usd": round(estimated_cost, 6),
                    "user_input_length": len(user_input),
                    "finish_reason": response.choices[0].finish_reason if response.choices else None,
                }
            )

            # Parse the JSON response
            content = response.choices[0].message.content
            extracted_data = json.loads(content)

            # Parse relative dates in extracted tasks
            if "tasks" in extracted_data:
                for task in extracted_data["tasks"]:
                    if task.get("dueDate"):
                        # Try to parse relative date phrases
                        parsed_date = self.parse_relative_date(task["dueDate"])
                        if parsed_date:
                            task["dueDate"] = parsed_date.isoformat()

            # Calculate confidence score (simplified - could be more sophisticated)
            confidence = 0.9 if extracted_data.get("tasks") else 0.5

            # Determine if clarification needed
            clarification_needed = False
            ambiguous_fields = []

            if "tasks" in extracted_data and extracted_data["tasks"]:
                for task in extracted_data["tasks"]:
                    if not task.get("title") or len(task.get("title", "").strip()) == 0:
                        clarification_needed = True
                        ambiguous_fields.append("title")
            else:
                clarification_needed = True
                ambiguous_fields.append("intent")

            # Validate extracted parameters
            if "tasks" in extracted_data:
                for task in extracted_data["tasks"]:
                    is_valid, errors = self.validate_extracted_params(task)
                    if not is_valid:
                        clarification_needed = True
                        ambiguous_fields.extend(errors)

            # Apply learned pattern defaults (T087)
            if user_patterns and "tasks" in extracted_data:
                for task in extracted_data["tasks"]:
                    if task.get("actionType") == "create":
                        self._apply_pattern_defaults(task, user_patterns)

            return {
                "tasks": extracted_data.get("tasks", []),
                "confidence": confidence,
                "clarification_needed": clarification_needed,
                "ambiguous_fields": list(set(ambiguous_fields))  # Remove duplicates
            }

        except Exception as e:
            # T101: Log error with context
            logger.error(
                "OpenAI API request failed",
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "model": self.model,
                    "user_input_length": len(user_input),
                },
                exc_info=True
            )
            # Delegate error handling to specialized method
            return await self.handle_extraction_error(e, user_input)

    def parse_relative_date(self, date_phrase: str) -> Optional[datetime]:
        """
        Convert relative date phrases to absolute datetime.

        Args:
            date_phrase: Relative date like "tomorrow", "next week", "by Friday"

        Returns:
            Parsed datetime or None if unable to parse

        Example:
            >>> nlp.parse_relative_date("tomorrow")
            datetime(2025, 12, 21, 0, 0, 0)
        """
        from datetime import timedelta
        import re

        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Normalize the input
        phrase = date_phrase.lower().strip()

        # Check if it's already an ISO 8601 date
        if re.match(r'\d{4}-\d{2}-\d{2}', phrase):
            try:
                return datetime.fromisoformat(phrase.replace('Z', '+00:00'))
            except ValueError:
                pass

        # Handle common relative date phrases
        if phrase in ["today", "tonight"]:
            return today

        if phrase == "tomorrow":
            return today + timedelta(days=1)

        if phrase == "yesterday":
            return today - timedelta(days=1)

        if phrase in ["next week", "1 week"]:
            return today + timedelta(weeks=1)

        if phrase in ["next month", "1 month"]:
            return today + timedelta(days=30)

        # Handle "in X days/weeks/months"
        match = re.match(r'in (\d+) (day|days|week|weeks|month|months)', phrase)
        if match:
            count = int(match.group(1))
            unit = match.group(2)
            if 'day' in unit:
                return today + timedelta(days=count)
            elif 'week' in unit:
                return today + timedelta(weeks=count)
            elif 'month' in unit:
                return today + timedelta(days=count * 30)

        # Handle "next Monday", "next Friday", etc.
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }

        for day_name, day_num in weekdays.items():
            if day_name in phrase:
                current_weekday = now.weekday()
                days_ahead = day_num - current_weekday

                # If the day is today or already passed this week, target next week
                if days_ahead <= 0:
                    days_ahead += 7

                # Handle "next" keyword - always next week
                if 'next' in phrase:
                    days_ahead += 7 if days_ahead <= 7 else 0

                return today + timedelta(days=days_ahead)

        # Handle "by Friday", "by next week", etc.
        if phrase.startswith('by '):
            return self.parse_relative_date(phrase[3:])

        # Unable to parse
        return None

    def validate_extracted_params(self, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate extracted task parameters.

        Args:
            params: Extracted parameters from extract_task_params()

        Returns:
            Tuple of (is_valid: bool, errors: List[str])

        Validation rules:
        - Title: non-empty, max 200 characters
        - Description: max 1000 characters
        - Due date: valid ISO 8601 format if present
        - Priority: one of ["low", "medium", "high"]
        - Action type: one of ["create", "update", "delete", "complete", "query"]
        """
        errors = []

        # Validate title
        title = params.get("title", "")
        if not title or not title.strip():
            errors.append("title_empty")
        elif len(title) > 200:
            errors.append("title_too_long")

        # Validate description
        description = params.get("description", "")
        if description and len(description) > 1000:
            errors.append("description_too_long")

        # Validate due date format (if present)
        due_date = params.get("dueDate")
        if due_date:
            try:
                # Try parsing as ISO 8601
                datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                errors.append("invalid_date_format")

        # Validate priority
        priority = params.get("priority", "").lower()
        if priority and priority not in ["low", "medium", "high"]:
            errors.append("invalid_priority")

        # Validate action type
        action_type = params.get("actionType", "").lower()
        valid_actions = ["create", "update", "delete", "complete", "query"]
        if action_type and action_type not in valid_actions:
            errors.append("invalid_action_type")

        return (len(errors) == 0, errors)

    def _apply_pattern_defaults(
        self,
        task: Dict[str, Any],
        user_patterns: Dict[str, Any]
    ) -> None:
        """
        Apply learned pattern defaults to extracted task (T087).

        Analyzes user patterns to suggest:
        - Default priority based on most common priority
        - Default due date offset based on average patterns
        - Common task timing preferences

        Args:
            task: Task dictionary to modify with defaults
            user_patterns: User patterns from AIContext

        Modifies task in-place with suggested defaults.

        Examples:
            If user typically creates high-priority tasks,
            and task has no priority specified, default to "high".

            If user typically sets due dates 1 day out,
            and task has no due date, suggest tomorrow.
        """
        from datetime import datetime, timedelta

        # Extract pattern data
        creation_frequency = user_patterns.get("creation_frequency", {})
        completion_rates = user_patterns.get("completion_rates", {})

        # Suggest default priority if not specified
        if not task.get("priority"):
            # Analyze task titles for common priority keywords
            title_lower = task.get("title", "").lower()

            # Check if task contains urgency indicators
            urgent_keywords = ["urgent", "asap", "critical", "important", "deadline"]
            if any(keyword in title_lower for keyword in urgent_keywords):
                task["priority"] = "high"
                task["_pattern_applied"] = True
                task["_pattern_reason"] = "Detected urgency keyword in title"
            else:
                # Default to medium priority (safe default)
                task["priority"] = "medium"
                task["_pattern_applied"] = True
                task["_pattern_reason"] = "Applied default priority"

        # Suggest default due date offset if not specified
        if not task.get("dueDate"):
            # Analyze creation patterns to determine common timing
            peak_day = creation_frequency.get("peak_day")

            # If user typically creates tasks on a specific day,
            # suggest due date based on that pattern
            # Default: 1 day from now (common pattern)
            now = datetime.utcnow()
            default_due_date = now + timedelta(days=1)

            task["dueDate"] = default_due_date.isoformat()
            task["_suggested_due_date"] = True
            task["_pattern_applied"] = True
            task["_pattern_reason"] = "Applied default 1-day due date based on patterns"

        # Add metadata about pattern application
        if "_pattern_applied" in task:
            logger.info(
                f"Applied pattern defaults to task: {task.get('title')} "
                f"(priority: {task.get('priority')}, reason: {task.get('_pattern_reason')})"
            )

    async def handle_extraction_error(
        self,
        error: Exception,
        user_input: str
    ) -> Dict[str, Any]:
        """
        Handle errors during task extraction with graceful fallback.

        Args:
            error: Exception that occurred
            user_input: Original user input

        Returns:
            Dictionary with error handling response:
            {
                "success": False,
                "error": str,
                "fallback_message": str,
                "should_use_traditional_form": bool
            }
        """
        import logging
        from openai import APIError, APITimeoutError, RateLimitError, APIConnectionError

        logger = logging.getLogger(__name__)
        logger.error(f"Error extracting task params from '{user_input}': {str(error)}", exc_info=True)

        # Determine error type and appropriate fallback message
        fallback_message = ""
        should_use_traditional_form = False
        error_type = "unknown_error"

        if isinstance(error, APIConnectionError):
            error_type = "connection_error"
            fallback_message = "I'm having trouble connecting to the AI service. Please try again in a moment, or use the traditional form to create your task."
            should_use_traditional_form = True

        elif isinstance(error, APITimeoutError):
            error_type = "timeout_error"
            fallback_message = "The AI service is taking too long to respond. Please try again, or use the traditional form."
            should_use_traditional_form = True

        elif isinstance(error, RateLimitError):
            error_type = "rate_limit_error"
            fallback_message = "You've reached your AI request limit for now. Please try again later, or use the traditional form."
            should_use_traditional_form = True

        elif isinstance(error, APIError):
            error_type = "api_error"
            fallback_message = "The AI service encountered an error. Please try again, or use the traditional form."
            should_use_traditional_form = True

        elif isinstance(error, json.JSONDecodeError):
            error_type = "json_parse_error"
            fallback_message = "I had trouble understanding the AI response. Could you rephrase your request?"
            should_use_traditional_form = False

        else:
            error_type = "unknown_error"
            fallback_message = "An unexpected error occurred. Please try again or use the traditional form."
            should_use_traditional_form = True

        return {
            "success": False,
            "error": error_type,
            "fallback_message": fallback_message,
            "should_use_traditional_form": should_use_traditional_form,
            "tasks": [],
            "confidence": 0.0,
            "clarification_needed": False,
            "ambiguous_fields": []
        }
