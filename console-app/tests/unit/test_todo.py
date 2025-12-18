"""Unit tests for Todo model."""

import pytest
from datetime import datetime

from console_app.models.todo import Todo


class TestTodoCreation:
    """Tests for creating Todo instances."""

    def test_create_todo_with_required_fields(self):
        """Test creating a todo with only required fields."""
        todo = Todo(id=1, title="Test task")

        assert todo.id == 1
        assert todo.title == "Test task"
        assert todo.description is None
        assert todo.status == "pending"
        assert isinstance(todo.created_at, datetime)

    def test_create_todo_with_all_fields(self):
        """Test creating a todo with all fields."""
        created = datetime(2025, 12, 8, 10, 30, 0)
        todo = Todo(
            id=1,
            title="Test task",
            description="Test description",
            status="complete",
            created_at=created
        )

        assert todo.id == 1
        assert todo.title == "Test task"
        assert todo.description == "Test description"
        assert todo.status == "complete"
        assert todo.created_at == created

    def test_created_at_defaults_to_now(self):
        """Test that created_at defaults to current time."""
        before = datetime.now()
        todo = Todo(id=1, title="Test")
        after = datetime.now()

        assert before <= todo.created_at <= after

    def test_status_defaults_to_pending(self):
        """Test that status defaults to 'pending'."""
        todo = Todo(id=1, title="Test")

        assert todo.status == "pending"


class TestTodoTitleValidation:
    """Tests for title validation."""

    def test_title_whitespace_stripped(self):
        """Test that title whitespace is stripped."""
        todo = Todo(id=1, title="  Test task  ")

        assert todo.title == "Test task"

    def test_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            Todo(id=1, title="")

        assert "empty" in str(exc_info.value).lower()

    def test_whitespace_only_title_raises_error(self):
        """Test that whitespace-only title raises ValueError."""
        with pytest.raises(ValueError):
            Todo(id=1, title="   ")

    def test_title_max_length_500(self):
        """Test that title can be up to 500 characters."""
        title_500 = "x" * 500
        todo = Todo(id=1, title=title_500)

        assert len(todo.title) == 500

    def test_title_over_500_raises_error(self):
        """Test that title over 500 characters raises ValueError."""
        title_501 = "x" * 501

        with pytest.raises(ValueError) as exc_info:
            Todo(id=1, title=title_501)

        assert "500 characters" in str(exc_info.value)

    def test_validate_title_static_method(self):
        """Test validate_title static method directly."""
        # Valid title
        assert Todo.validate_title("Test") == "Test"

        # Strips whitespace
        assert Todo.validate_title("  Test  ") == "Test"

        # Rejects empty
        with pytest.raises(ValueError):
            Todo.validate_title("")

        # Rejects too long
        with pytest.raises(ValueError):
            Todo.validate_title("x" * 501)


class TestTodoDescriptionValidation:
    """Tests for description validation."""

    def test_description_none_allowed(self):
        """Test that description can be None."""
        todo = Todo(id=1, title="Test", description=None)

        assert todo.description is None

    def test_description_max_length_2000(self):
        """Test that description can be up to 2000 characters."""
        desc_2000 = "x" * 2000
        todo = Todo(id=1, title="Test", description=desc_2000)

        assert len(todo.description) == 2000

    def test_description_over_2000_raises_error(self):
        """Test that description over 2000 characters raises ValueError."""
        desc_2001 = "x" * 2001

        with pytest.raises(ValueError) as exc_info:
            Todo(id=1, title="Test", description=desc_2001)

        assert "2000 characters" in str(exc_info.value)

    def test_validate_description_static_method(self):
        """Test validate_description static method directly."""
        # Valid description
        assert Todo.validate_description("Test") == "Test"

        # None allowed
        assert Todo.validate_description(None) is None

        # Rejects too long
        with pytest.raises(ValueError):
            Todo.validate_description("x" * 2001)


class TestTodoStatusValidation:
    """Tests for status validation."""

    def test_pending_status_valid(self):
        """Test that 'pending' is a valid status."""
        todo = Todo(id=1, title="Test", status="pending")

        assert todo.status == "pending"

    def test_complete_status_valid(self):
        """Test that 'complete' is a valid status."""
        todo = Todo(id=1, title="Test", status="complete")

        assert todo.status == "complete"

    def test_invalid_status_raises_error(self):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            Todo(id=1, title="Test", status="invalid")

        assert "invalid" in str(exc_info.value).lower()
        assert "pending" in str(exc_info.value)
        assert "complete" in str(exc_info.value)

    def test_validate_status_static_method(self):
        """Test validate_status static method directly."""
        # Valid statuses
        assert Todo.validate_status("pending") == "pending"
        assert Todo.validate_status("complete") == "complete"

        # Invalid status
        with pytest.raises(ValueError):
            Todo.validate_status("archived")


class TestTodoMutability:
    """Tests for modifying todo fields."""

    def test_status_can_be_changed(self):
        """Test that status can be changed after creation."""
        todo = Todo(id=1, title="Test")
        assert todo.status == "pending"

        todo.status = "complete"
        assert todo.status == "complete"

    def test_title_can_be_changed(self):
        """Test that title can be changed after creation."""
        todo = Todo(id=1, title="Old title")

        # Validate manually when changing
        todo.title = Todo.validate_title("New title")

        assert todo.title == "New title"

    def test_description_can_be_changed(self):
        """Test that description can be changed after creation."""
        todo = Todo(id=1, title="Test", description="Old")

        todo.description = "New description"

        assert todo.description == "New description"


class TestTodoEquality:
    """Tests for todo equality comparison."""

    def test_todos_with_same_id_equal(self):
        """Test that dataclass equality works."""
        created = datetime(2025, 12, 10, 10, 0, 0)
        todo1 = Todo(id=1, title="Test", created_at=created)
        todo2 = Todo(id=1, title="Test", created_at=created)

        assert todo1 == todo2

    def test_todos_with_different_id_not_equal(self):
        """Test that todos with different IDs are not equal."""
        todo1 = Todo(id=1, title="Test")
        todo2 = Todo(id=2, title="Test")

        assert todo1 != todo2
