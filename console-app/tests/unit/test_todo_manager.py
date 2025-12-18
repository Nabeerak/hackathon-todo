"""Unit tests for TodoManager business logic."""

import pytest

from console_app.lib.todo_manager import TodoManager, TodoNotFoundError, ValidationError
from console_app.models.todo import Todo


class TestTodoManagerAdd:
    """Unit tests for TodoManager.add() method."""

    def test_add_creates_todo_with_auto_incremented_id(self):
        """Test that add assigns auto-incremented IDs starting from 1."""
        manager = TodoManager()

        todo1 = manager.add("First todo")
        todo2 = manager.add("Second todo")
        todo3 = manager.add("Third todo")

        assert todo1.id == 1
        assert todo2.id == 2
        assert todo3.id == 3

    def test_add_stores_title(self):
        """Test that add stores the provided title."""
        manager = TodoManager()
        todo = manager.add("Buy groceries")

        assert todo.title == "Buy groceries"

    def test_add_stores_description(self):
        """Test that add stores optional description."""
        manager = TodoManager()
        todo = manager.add("Call dentist", "Schedule checkup")

        assert todo.description == "Schedule checkup"

    def test_add_without_description(self):
        """Test that add works without description."""
        manager = TodoManager()
        todo = manager.add("Test task")

        assert todo.description is None

    def test_add_sets_status_pending(self):
        """Test that new todos start with pending status."""
        manager = TodoManager()
        todo = manager.add("Test task")

        assert todo.status == "pending"

    def test_add_stores_in_internal_dict(self):
        """Test that add stores todo in internal dictionary."""
        manager = TodoManager()
        todo = manager.add("Test")

        # Should be retrievable by ID
        assert todo.id in manager._todos
        assert manager._todos[todo.id] == todo

    def test_add_empty_title_raises_validation_error(self):
        """Test that add raises ValidationError for empty title."""
        manager = TodoManager()

        with pytest.raises(ValidationError) as exc_info:
            manager.add("")

        assert "empty" in str(exc_info.value).lower()

    def test_add_whitespace_only_title_raises_validation_error(self):
        """Test that add raises ValidationError for whitespace-only title."""
        manager = TodoManager()

        with pytest.raises(ValidationError):
            manager.add("   ")

    def test_add_too_long_title_raises_validation_error(self):
        """Test that add raises ValidationError for title > 500 chars."""
        manager = TodoManager()
        long_title = "x" * 501

        with pytest.raises(ValidationError) as exc_info:
            manager.add(long_title)

        assert "500 characters" in str(exc_info.value)

    def test_add_too_long_description_raises_validation_error(self):
        """Test that add raises ValidationError for description > 2000 chars."""
        manager = TodoManager()
        long_desc = "x" * 2001

        with pytest.raises(ValidationError) as exc_info:
            manager.add("Title", long_desc)

        assert "2000 characters" in str(exc_info.value)


class TestTodoManagerGet:
    """Unit tests for TodoManager.get() method."""

    def test_get_returns_todo_by_id(self):
        """Test that get retrieves todo by ID."""
        manager = TodoManager()
        added = manager.add("Test")

        retrieved = manager.get(added.id)

        assert retrieved == added
        assert retrieved.title == "Test"

    def test_get_nonexistent_id_raises_not_found(self):
        """Test that get raises TodoNotFoundError for nonexistent ID."""
        manager = TodoManager()

        with pytest.raises(TodoNotFoundError) as exc_info:
            manager.get(999)

        assert "999" in str(exc_info.value)
        assert "not found" in str(exc_info.value).lower()

    def test_get_after_multiple_adds(self):
        """Test that get works correctly after multiple adds."""
        manager = TodoManager()
        todo1 = manager.add("First")
        todo2 = manager.add("Second")
        todo3 = manager.add("Third")

        assert manager.get(1) == todo1
        assert manager.get(2) == todo2
        assert manager.get(3) == todo3


class TestTodoManagerListAll:
    """Unit tests for TodoManager.list_all() method."""

    def test_list_all_empty_returns_empty_list(self):
        """Test that list_all returns empty list when no todos."""
        manager = TodoManager()

        todos = manager.list_all()

        assert todos == []

    def test_list_all_returns_all_todos(self):
        """Test that list_all returns all added todos."""
        manager = TodoManager()
        todo1 = manager.add("First")
        todo2 = manager.add("Second")
        todo3 = manager.add("Third")

        todos = manager.list_all()

        assert len(todos) == 3
        assert todo1 in todos
        assert todo2 in todos
        assert todo3 in todos

    def test_list_all_sorted_by_id(self):
        """Test that list_all returns todos sorted by ID."""
        manager = TodoManager()
        manager.add("First")
        manager.add("Second")
        manager.add("Third")

        todos = manager.list_all()

        # Should be in ID order
        assert todos[0].id == 1
        assert todos[1].id == 2
        assert todos[2].id == 3

    def test_list_all_after_delete(self):
        """Test that list_all doesn't include deleted todos."""
        manager = TodoManager()
        manager.add("First")
        manager.add("Second")
        manager.add("Third")

        manager.delete(2)  # Delete middle one

        todos = manager.list_all()

        assert len(todos) == 2
        assert all(t.id != 2 for t in todos)


class TestTodoManagerComplete:
    """Unit tests for TodoManager.complete() method."""

    def test_complete_changes_status(self):
        """Test that complete changes status to 'complete'."""
        manager = TodoManager()
        todo = manager.add("Test")

        assert todo.status == "pending"

        completed = manager.complete(todo.id)

        assert completed.status == "complete"
        assert completed == todo  # Same object

    def test_complete_nonexistent_raises_not_found(self):
        """Test that complete raises TodoNotFoundError for nonexistent ID."""
        manager = TodoManager()

        with pytest.raises(TodoNotFoundError):
            manager.complete(999)

    def test_complete_already_complete_succeeds(self):
        """Test that completing already-complete todo succeeds (idempotent)."""
        manager = TodoManager()
        todo = manager.add("Test")
        manager.complete(todo.id)

        # Complete again
        result = manager.complete(todo.id)

        assert result.status == "complete"

    def test_complete_returns_updated_todo(self):
        """Test that complete returns the updated todo."""
        manager = TodoManager()
        todo = manager.add("Test task")

        result = manager.complete(todo.id)

        assert result.title == "Test task"
        assert result.status == "complete"


class TestTodoManagerDelete:
    """Unit tests for TodoManager.delete() method."""

    def test_delete_removes_from_dict(self):
        """Test that delete removes todo from internal storage."""
        manager = TodoManager()
        todo = manager.add("Test")

        manager.delete(todo.id)

        assert todo.id not in manager._todos

    def test_delete_returns_deleted_todo(self):
        """Test that delete returns the deleted todo."""
        manager = TodoManager()
        todo = manager.add("Test task")

        deleted = manager.delete(todo.id)

        assert deleted == todo
        assert deleted.title == "Test task"

    def test_delete_nonexistent_raises_not_found(self):
        """Test that delete raises TodoNotFoundError for nonexistent ID."""
        manager = TodoManager()

        with pytest.raises(TodoNotFoundError):
            manager.delete(999)

    def test_delete_prevents_subsequent_get(self):
        """Test that get fails after delete."""
        manager = TodoManager()
        todo = manager.add("Test")
        manager.delete(todo.id)

        with pytest.raises(TodoNotFoundError):
            manager.get(todo.id)

    def test_delete_multiple(self):
        """Test deleting multiple todos."""
        manager = TodoManager()
        manager.add("First")
        manager.add("Second")
        manager.add("Third")

        manager.delete(1)
        manager.delete(3)

        todos = manager.list_all()
        assert len(todos) == 1
        assert todos[0].id == 2


class TestTodoManagerUpdate:
    """Unit tests for TodoManager.update() method."""

    def test_update_title_only(self):
        """Test updating only the title."""
        manager = TodoManager()
        todo = manager.add("Old title", "Description")

        updated = manager.update(todo.id, title="New title")

        assert updated.title == "New title"
        assert updated.description == "Description"  # Unchanged

    def test_update_description_only(self):
        """Test updating only the description."""
        manager = TodoManager()
        todo = manager.add("Title", "Old description")

        updated = manager.update(todo.id, description="New description")

        assert updated.title == "Title"  # Unchanged
        assert updated.description == "New description"

    def test_update_both_fields(self):
        """Test updating both title and description."""
        manager = TodoManager()
        todo = manager.add("Old title", "Old description")

        updated = manager.update(todo.id, title="New title", description="New description")

        assert updated.title == "New title"
        assert updated.description == "New description"

    def test_update_nonexistent_raises_not_found(self):
        """Test that update raises TodoNotFoundError for nonexistent ID."""
        manager = TodoManager()

        with pytest.raises(TodoNotFoundError):
            manager.update(999, title="New")

    def test_update_empty_title_raises_validation_error(self):
        """Test that update raises ValidationError for empty title."""
        manager = TodoManager()
        todo = manager.add("Test")

        with pytest.raises(ValidationError):
            manager.update(todo.id, title="")

    def test_update_too_long_title_raises_validation_error(self):
        """Test that update raises ValidationError for title > 500 chars."""
        manager = TodoManager()
        todo = manager.add("Test")
        long_title = "x" * 501

        with pytest.raises(ValidationError):
            manager.update(todo.id, title=long_title)

    def test_update_too_long_description_raises_validation_error(self):
        """Test that update raises ValidationError for description > 2000 chars."""
        manager = TodoManager()
        todo = manager.add("Test")
        long_desc = "x" * 2001

        with pytest.raises(ValidationError):
            manager.update(todo.id, description=long_desc)

    def test_update_neither_field(self):
        """Test that update with no fields returns unchanged todo."""
        manager = TodoManager()
        todo = manager.add("Test", "Description")

        updated = manager.update(todo.id)

        assert updated.title == "Test"
        assert updated.description == "Description"

    def test_update_persists_in_storage(self):
        """Test that update changes persist in storage."""
        manager = TodoManager()
        todo = manager.add("Old")
        manager.update(todo.id, title="New")

        # Get again
        retrieved = manager.get(todo.id)
        assert retrieved.title == "New"
