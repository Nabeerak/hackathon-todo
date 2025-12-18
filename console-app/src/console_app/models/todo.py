"""Todo model for the console todo app."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class Todo:
    """Represents a single todo item.

    Attributes:
        id: Unique identifier (auto-assigned)
        title: Task title (required, max 500 chars)
        description: Optional task details (max 2000 chars)
        status: Current status ("pending" or "complete")
        created_at: Timestamp when todo was created
    """

    id: int
    title: str
    description: str | None = None
    status: Literal["pending", "complete"] = "pending"
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        self.title = self.validate_title(self.title)
        self.description = self.validate_description(self.description)
        self.status = self.validate_status(self.status)

    @staticmethod
    def validate_title(title: str) -> str:
        """Validate and normalize title.

        Args:
            title: The title to validate

        Returns:
            Normalized title (stripped of whitespace)

        Raises:
            ValueError: If title is empty or too long
        """
        if not title or not title.strip():
            raise ValueError("Todo title cannot be empty")

        normalized = title.strip()
        if len(normalized) > 500:
            raise ValueError("Todo title cannot exceed 500 characters")

        return normalized

    @staticmethod
    def validate_description(description: str | None) -> str | None:
        """Validate and normalize description.

        Args:
            description: The description to validate (can be None)

        Returns:
            The description if valid, None if not provided

        Raises:
            ValueError: If description is too long
        """
        if description is None:
            return None

        if len(description) > 2000:
            raise ValueError("Todo description cannot exceed 2000 characters")

        return description

    @staticmethod
    def validate_status(status: str) -> Literal["pending", "complete"]:
        """Validate status value.

        Args:
            status: The status to validate

        Returns:
            The validated status

        Raises:
            ValueError: If status is not "pending" or "complete"
        """
        if status not in ("pending", "complete"):
            raise ValueError(
                f"Invalid status '{status}'. Must be 'pending' or 'complete'"
            )
        return status  # type: ignore
