"""Core business logic for managing todos."""

from console_app.models.todo import Todo


class TodoNotFoundError(Exception):
    """Raised when a todo with the given ID is not found."""

    pass


class ValidationError(Exception):
    """Raised when validation fails for todo data."""

    pass


class TodoManager:
    """Manages todo items in memory.

    This class provides the core business logic for CRUD operations on todos.
    It maintains an in-memory dictionary of todos and handles ID assignment.
    """

    def __init__(self) -> None:
        """Initialize the TodoManager with empty storage."""
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str | None = None) -> Todo:
        """Add a new todo item.

        Args:
            title: The todo title (required)
            description: Optional additional details

        Returns:
            The created Todo object

        Raises:
            ValidationError: If validation fails
        """
        try:
            todo = Todo(
                id=self._next_id,
                title=title,
                description=description,
                status="pending",
            )
            self._todos[self._next_id] = todo
            self._next_id += 1
            return todo
        except ValueError as e:
            raise ValidationError(str(e)) from e

    def get(self, todo_id: int) -> Todo:
        """Get a todo by ID.

        Args:
            todo_id: The ID of the todo to retrieve

        Returns:
            The Todo object

        Raises:
            TodoNotFoundError: If todo with given ID doesn't exist
        """
        if todo_id not in self._todos:
            raise TodoNotFoundError(f"Todo with ID {todo_id} not found")
        return self._todos[todo_id]

    def list_all(self) -> list[Todo]:
        """Get all todos sorted by ID.

        Returns:
            List of all Todo objects, sorted by ID
        """
        return sorted(self._todos.values(), key=lambda t: t.id)

    def complete(self, todo_id: int) -> Todo:
        """Mark a todo as complete.

        Args:
            todo_id: The ID of the todo to complete

        Returns:
            The updated Todo object

        Raises:
            TodoNotFoundError: If todo with given ID doesn't exist
        """
        todo = self.get(todo_id)
        todo.status = "complete"
        return todo

    def delete(self, todo_id: int) -> Todo:
        """Delete a todo.

        Args:
            todo_id: The ID of the todo to delete

        Returns:
            The deleted Todo object

        Raises:
            TodoNotFoundError: If todo with given ID doesn't exist
        """
        todo = self.get(todo_id)
        del self._todos[todo_id]
        return todo

    def update(
        self, todo_id: int, title: str | None = None, description: str | None = None
    ) -> Todo:
        """Update a todo's title and/or description.

        Args:
            todo_id: The ID of the todo to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            The updated Todo object

        Raises:
            TodoNotFoundError: If todo with given ID doesn't exist
            ValidationError: If validation fails
        """
        todo = self.get(todo_id)

        try:
            if title is not None:
                todo.title = Todo.validate_title(title)
            if description is not None:
                todo.description = Todo.validate_description(description)
        except ValueError as e:
            raise ValidationError(str(e)) from e

        return todo
