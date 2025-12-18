"""Integration tests for user journeys.

These tests verify end-to-end user scenarios from the specification,
ensuring that user stories work as expected.
"""

import subprocess
import sys
import time
from pathlib import Path

import pytest


CLI_PATH = Path(__file__).parent.parent.parent / "src" / "console_app" / "cli" / "main.py"


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear storage before each test."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from console_app.lib.storage import clear_storage as clear
    clear()
    yield
    clear()


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Run the CLI with given arguments."""
    cmd = [sys.executable, str(CLI_PATH)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True)


class TestUserStory1AddTodos:
    """Integration tests for User Story 1: Add Todo Items (Priority P1).

    User Story: Users need to quickly capture tasks they need to complete.
    They should be able to add a todo with a title and optionally provide
    more details in a description field.
    """

    def test_acceptance_scenario_1_add_with_title_only(self):
        """Given the app is running, When user adds a todo with only a title
        "Buy groceries", Then the todo is created with status "pending" and
        can be viewed.
        """
        # Add todo with title only
        add_result = run_cli("add", "Buy groceries")
        assert add_result.returncode == 0
        assert "Buy groceries" in add_result.stdout

        # Verify it can be viewed
        list_result = run_cli("list")
        assert "Buy groceries" in list_result.stdout
        assert "pending" in list_result.stdout

    def test_acceptance_scenario_2_add_with_title_and_description(self):
        """Given the app is running, When user adds a todo with title
        "Call dentist" and description "Schedule annual checkup",
        Then both title and description are stored.
        """
        # Add todo with title and description
        add_result = run_cli(
            "add", "Call dentist", "--description", "Schedule annual checkup"
        )
        assert add_result.returncode == 0
        assert "Call dentist" in add_result.stdout

        # Verify both are stored (description visible in list)
        list_result = run_cli("list")
        assert "Call dentist" in list_result.stdout
        # Description shows in table
        assert "Schedule annual checkup" in list_result.stdout or "Schedule" in list_result.stdout

    def test_acceptance_scenario_3_reject_empty_title(self):
        """Given the app is running, When user attempts to add a todo with
        an empty title, Then an error message is displayed and no todo
        is created.
        """
        # Attempt to add empty title
        add_result = run_cli("add", "")
        assert add_result.returncode == 1
        assert "Error: " in add_result.stderr
        assert "empty" in add_result.stderr.lower()

        # Verify no todo was created
        list_result = run_cli("list")
        assert "No todos found" in list_result.stdout


class TestUserStory2ViewTodos:
    """Integration tests for User Story 2: View All Todos (Priority P2).

    User Story: Users need to see all their todos at a glance to understand
    what tasks are pending and what has been completed.
    """

    def test_acceptance_scenario_1_view_multiple_todos_with_status(self):
        """Given there are 3 todos (2 pending, 1 complete), When user views
        all todos, Then all 3 todos are displayed with their titles,
        descriptions, and status.
        """
        # Add 3 todos
        run_cli("add", "Todo 1", "-d", "Description 1")
        run_cli("add", "Todo 2", "-d", "Description 2")
        run_cli("add", "Todo 3", "-d", "Description 3")

        # Mark one as complete
        run_cli("complete", "2")

        # View all todos
        list_result = run_cli("list")
        assert list_result.returncode == 0

        # Verify all 3 are displayed
        assert "Todo 1" in list_result.stdout
        assert "Todo 2" in list_result.stdout
        assert "Todo 3" in list_result.stdout

        # Verify statuses (2 pending, 1 complete)
        assert list_result.stdout.count("pending") == 2
        assert list_result.stdout.count("complete") == 1

    def test_acceptance_scenario_2_empty_list_message(self):
        """Given there are no todos, When user views all todos,
        Then a message "No todos found" is displayed.
        """
        list_result = run_cli("list")
        assert list_result.returncode == 0
        assert "No todos found" in list_result.stdout

    def test_acceptance_scenario_3_todos_in_creation_order(self):
        """Given there are multiple todos, When user views all todos,
        Then todos are displayed in the order they were created with
        clear status indicators.
        """
        # Add todos in specific order
        run_cli("add", "First")
        run_cli("add", "Second")
        run_cli("add", "Third")

        list_result = run_cli("list")

        # Check they appear in order (by verifying IDs are sequential)
        lines = list_result.stdout.split("\n")
        todo_lines = [l for l in lines if "First" in l or "Second" in l or "Third" in l]

        # Should be in creation order
        assert len(todo_lines) == 3
        first_line = [l for l in todo_lines if "First" in l][0]
        second_line = [l for l in todo_lines if "Second" in l][0]
        third_line = [l for l in todo_lines if "Third" in l][0]

        # Find positions in output
        first_pos = list_result.stdout.index("First")
        second_pos = list_result.stdout.index("Second")
        third_pos = list_result.stdout.index("Third")

        assert first_pos < second_pos < third_pos


class TestUserStory3MarkComplete:
    """Integration tests for User Story 3: Mark Todos Complete (Priority P3).

    User Story: Users need to mark tasks as complete when they finish them,
    providing a sense of accomplishment and helping track progress.
    """

    def test_acceptance_scenario_1_mark_pending_complete(self):
        """Given there is a pending todo with ID 1, When user marks todo 1
        as complete, Then the todo status changes to "complete".
        """
        # Add a pending todo
        run_cli("add", "Test todo")

        # Mark as complete
        complete_result = run_cli("complete", "1")
        assert complete_result.returncode == 0

        # Verify status changed
        list_result = run_cli("list")
        assert "complete" in list_result.stdout
        assert "Test todo" in list_result.stdout

    def test_acceptance_scenario_2_nonexistent_id_error(self):
        """Given there is a todo with ID 5, When user attempts to mark
        a non-existent todo ID 99 as complete, Then an error message
        is displayed.
        """
        run_cli("add", "Test")

        complete_result = run_cli("complete", "99")
        assert complete_result.returncode == 2
        assert "Error: " in complete_result.stderr
        assert "not found" in complete_result.stderr

    def test_acceptance_scenario_3_already_complete_no_error(self):
        """Given there is already a completed todo, When user marks it
        complete again, Then it remains complete without error.
        """
        run_cli("add", "Test")
        run_cli("complete", "1")

        # Mark complete again (idempotent)
        complete_result = run_cli("complete", "1")
        assert complete_result.returncode == 0

        # Still complete
        list_result = run_cli("list")
        assert "complete" in list_result.stdout


class TestUserStory4DeleteTodos:
    """Integration tests for User Story 4: Delete Todos (Priority P4).

    User Story: Users need to remove todos that are no longer relevant
    or were added by mistake.
    """

    def test_acceptance_scenario_1_delete_removes_todo(self):
        """Given there is a todo with ID 2, When user deletes todo 2,
        Then the todo is removed and no longer appears in the list.
        """
        run_cli("add", "Keep this")
        run_cli("add", "Delete this")
        run_cli("add", "Keep this too")

        # Delete ID 2
        delete_result = run_cli("delete", "2")
        assert delete_result.returncode == 0

        # Verify removed
        list_result = run_cli("list")
        assert "Delete this" not in list_result.stdout
        assert "Keep this" in list_result.stdout
        assert "Keep this too" in list_result.stdout

    def test_acceptance_scenario_2_delete_nonexistent_error(self):
        """Given there are 5 todos, When user attempts to delete todo ID 99,
        Then an error message is displayed and all 5 todos remain.
        """
        for i in range(5):
            run_cli("add", f"Todo {i+1}")

        # Attempt to delete nonexistent
        delete_result = run_cli("delete", "99")
        assert delete_result.returncode == 2
        assert "Error: " in delete_result.stderr

        # All 5 still present
        list_result = run_cli("list")
        for i in range(5):
            assert f"Todo {i+1}" in list_result.stdout

    def test_acceptance_scenario_3_deleted_not_in_list(self):
        """Given a todo has just been deleted, When user views all todos,
        Then the deleted todo does not appear.
        """
        run_cli("add", "Will be deleted")
        run_cli("delete", "1")

        list_result = run_cli("list")
        assert "Will be deleted" not in list_result.stdout
        assert "No todos found" in list_result.stdout


class TestUserStory5UpdateContent:
    """Integration tests for User Story 5: Update Todo Content (Priority P5).

    User Story: Users need to modify todo titles and descriptions when
    details change or mistakes need correction.
    """

    def test_acceptance_scenario_1_update_title(self):
        """Given there is a todo with ID 3 and title "Buy milk",
        When user updates the title to "Buy milk and bread",
        Then the title is changed and persists.
        """
        run_cli("add", "Buy milk")
        run_cli("add", "Other")
        run_cli("add", "Buy milk")

        # Update ID 3
        update_result = run_cli("update", "3", "--title", "Buy milk and bread")
        assert update_result.returncode == 0

        # Verify change persists
        list_result = run_cli("list")
        assert "Buy milk and bread" in list_result.stdout

    def test_acceptance_scenario_2_update_description(self):
        """Given there is a todo with ID 4, When user updates the description
        to "New description text", Then the description is updated while
        title remains unchanged.
        """
        run_cli("add", "Task", "-d", "Old description")

        update_result = run_cli("update", "1", "--description", "New description text")
        assert update_result.returncode == 0

        # Verify title unchanged, description updated
        list_result = run_cli("list")
        assert "Task" in list_result.stdout
        # Description should show in list
        assert "New description" in list_result.stdout or "New desc" in list_result.stdout

    def test_acceptance_scenario_3_update_nonexistent_error(self):
        """Given there is a todo with ID 1, When user attempts to update
        todo ID 99, Then an error message is displayed and no changes occur.
        """
        run_cli("add", "Test")

        update_result = run_cli("update", "99", "--title", "New")
        assert update_result.returncode == 2
        assert "Error: " in update_result.stderr


class TestCompleteWorkflow:
    """Integration test for complete user workflow.

    Success Criteria SC-007: Users can successfully complete their first
    todo workflow (add → view → complete → view) within 30 seconds of first use.
    """

    def test_complete_first_workflow(self):
        """Test the complete workflow: add → view → complete → view."""
        # Step 1: Add a todo
        add_result = run_cli("add", "First task")
        assert add_result.returncode == 0
        assert "First task" in add_result.stdout

        # Step 2: View todos
        view_result_1 = run_cli("list")
        assert view_result_1.returncode == 0
        assert "First task" in view_result_1.stdout
        assert "pending" in view_result_1.stdout

        # Step 3: Complete the todo
        complete_result = run_cli("complete", "1")
        assert complete_result.returncode == 0

        # Step 4: View again to see status changed
        view_result_2 = run_cli("list")
        assert view_result_2.returncode == 0
        assert "First task" in view_result_2.stdout
        assert "complete" in view_result_2.stdout


class TestPerformance:
    """Performance tests for CLI commands.

    Constitution Performance Budget: Console App commands < 100ms (p95)
    """

    def test_add_command_performance(self):
        """Verify add command executes in < 100ms."""
        start = time.perf_counter()
        result = run_cli("add", "Performance test task")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.returncode == 0
        assert elapsed_ms < 100, f"Add command took {elapsed_ms:.2f}ms (expected < 100ms)"

    def test_list_command_performance(self):
        """Verify list command executes in < 100ms."""
        # Add some todos first
        for i in range(10):
            run_cli("add", f"Task {i}")

        start = time.perf_counter()
        result = run_cli("list")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.returncode == 0
        assert elapsed_ms < 100, f"List command took {elapsed_ms:.2f}ms (expected < 100ms)"

    def test_complete_command_performance(self):
        """Verify complete command executes in < 100ms."""
        run_cli("add", "Task to complete")

        start = time.perf_counter()
        result = run_cli("complete", "1")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.returncode == 0
        assert elapsed_ms < 100, f"Complete command took {elapsed_ms:.2f}ms (expected < 100ms)"

    def test_delete_command_performance(self):
        """Verify delete command executes in < 100ms."""
        run_cli("add", "Task to delete")

        start = time.perf_counter()
        result = run_cli("delete", "1")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.returncode == 0
        assert elapsed_ms < 100, f"Delete command took {elapsed_ms:.2f}ms (expected < 100ms)"

    def test_update_command_performance(self):
        """Verify update command executes in < 100ms."""
        run_cli("add", "Task to update")

        start = time.perf_counter()
        result = run_cli("update", "1", "--title", "Updated title")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.returncode == 0
        assert elapsed_ms < 100, f"Update command took {elapsed_ms:.2f}ms (expected < 100ms)"
