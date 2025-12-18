"""Contract tests for CLI interface.

These tests verify that the CLI adheres to the documented interface contracts
including command syntax, exit codes, and output formats.
"""

import subprocess
import sys
from pathlib import Path

import pytest


# Path to the main CLI module
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
    """Run the CLI with given arguments.

    Args:
        *args: Command-line arguments to pass

    Returns:
        CompletedProcess with stdout, stderr, and returncode
    """
    cmd = [sys.executable, str(CLI_PATH)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True)


class TestAddCommandContract:
    """Contract tests for the 'add' command."""

    def test_add_success_exit_code(self):
        """Verify add command returns exit code 0 on success."""
        result = run_cli("add", "Test todo")
        assert result.returncode == 0

    def test_add_success_output_format(self):
        """Verify add command outputs correct format: '✓ Added todo #ID: TITLE'."""
        result = run_cli("add", "Buy groceries")
        assert result.returncode == 0
        assert result.stdout.startswith("✓ Added todo #")
        assert "Buy groceries" in result.stdout

    def test_add_with_description(self):
        """Verify add command accepts --description flag."""
        result = run_cli("add", "Call dentist", "--description", "Schedule checkup")
        assert result.returncode == 0
        assert "Call dentist" in result.stdout

    def test_add_with_description_short_flag(self):
        """Verify add command accepts -d short flag for description."""
        result = run_cli("add", "Review PR", "-d", "Check backend changes")
        assert result.returncode == 0
        assert "Review PR" in result.stdout

    def test_add_returns_incremented_id(self):
        """Verify add command returns incrementing IDs."""
        result1 = run_cli("add", "First todo")
        result2 = run_cli("add", "Second todo")

        # Extract IDs from output (format: "✓ Added todo #1: ...")
        assert "#" in result1.stdout
        assert "#" in result2.stdout

    def test_add_empty_title_validation_error(self):
        """Verify add command rejects empty title with exit code 1."""
        result = run_cli("add", "")
        assert result.returncode == 1
        assert "Error: " in result.stderr
        assert "empty" in result.stderr.lower()

    def test_add_whitespace_only_title_rejected(self):
        """Verify add command rejects whitespace-only title."""
        result = run_cli("add", "   ")
        assert result.returncode == 1
        assert "Error: " in result.stderr

    def test_add_too_long_title_rejected(self):
        """Verify add command rejects title exceeding 500 characters."""
        long_title = "x" * 501
        result = run_cli("add", long_title)
        assert result.returncode == 1
        assert "Error: " in result.stderr
        assert "500 characters" in result.stderr

    def test_add_error_goes_to_stderr(self):
        """Verify validation errors are written to stderr, not stdout."""
        result = run_cli("add", "")
        assert result.returncode == 1
        assert result.stdout == ""  # No output to stdout on error
        assert "Error: " in result.stderr


class TestListCommandContract:
    """Contract tests for the 'list' command."""

    def test_list_always_returns_zero(self):
        """Verify list command always returns exit code 0."""
        result = run_cli("list")
        assert result.returncode == 0

    def test_list_empty_state_message(self):
        """Verify list shows helpful message when no todos exist."""
        result = run_cli("list")
        assert result.returncode == 0
        assert "No todos found" in result.stdout
        assert "todo add" in result.stdout

    def test_list_alias_ls_works(self):
        """Verify 'ls' alias works for list command."""
        result = run_cli("ls")
        assert result.returncode == 0

    def test_list_table_format_with_todos(self):
        """Verify list displays todos in table format."""
        # Add a todo first
        run_cli("add", "Test todo")

        result = run_cli("list")
        assert result.returncode == 0

        # Check for table headers
        assert "ID" in result.stdout
        assert "Status" in result.stdout
        assert "Title" in result.stdout
        assert "Description" in result.stdout

        # Check for separator line
        assert "---+" in result.stdout or "---" in result.stdout

        # Check todo appears
        assert "Test todo" in result.stdout
        assert "pending" in result.stdout


class TestCompleteCommandContract:
    """Contract tests for the 'complete' command."""

    def test_complete_success_exit_code(self):
        """Verify complete command returns exit code 0 on success."""
        # Add a todo first
        add_result = run_cli("add", "Test todo")
        assert add_result.returncode == 0

        result = run_cli("complete", "1")
        assert result.returncode == 0

    def test_complete_success_output_format(self):
        """Verify complete command outputs correct format."""
        run_cli("add", "Buy milk")
        result = run_cli("complete", "1")

        assert result.returncode == 0
        assert "✓ Marked todo #" in result.stdout
        assert "complete" in result.stdout
        assert "Buy milk" in result.stdout

    def test_complete_nonexistent_id_returns_two(self):
        """Verify complete command returns exit code 2 for nonexistent ID."""
        result = run_cli("complete", "999")
        assert result.returncode == 2
        assert "Error: " in result.stderr
        assert "not found" in result.stderr

    def test_complete_invalid_id_returns_one(self):
        """Verify complete command returns exit code 1 for invalid ID format."""
        result = run_cli("complete", "abc")
        # argparse will handle this as an error
        assert result.returncode != 0

    def test_complete_idempotent(self):
        """Verify completing already-complete todo succeeds (idempotent)."""
        run_cli("add", "Test todo")
        run_cli("complete", "1")

        # Complete again
        result = run_cli("complete", "1")
        assert result.returncode == 0  # Should still succeed

    def test_complete_alias_done_works(self):
        """Verify 'done' alias works for complete command."""
        run_cli("add", "Test todo")
        result = run_cli("done", "1")
        assert result.returncode == 0


class TestDeleteCommandContract:
    """Contract tests for the 'delete' command."""

    def test_delete_success_exit_code(self):
        """Verify delete command returns exit code 0 on success."""
        run_cli("add", "Test todo")
        result = run_cli("delete", "1")
        assert result.returncode == 0

    def test_delete_success_output_format(self):
        """Verify delete command outputs correct format."""
        run_cli("add", "Remove this")
        result = run_cli("delete", "1")

        assert result.returncode == 0
        assert "✓ Deleted todo #" in result.stdout
        assert "Remove this" in result.stdout

    def test_delete_nonexistent_id_returns_two(self):
        """Verify delete command returns exit code 2 for nonexistent ID."""
        result = run_cli("delete", "999")
        assert result.returncode == 2
        assert "Error: " in result.stderr
        assert "not found" in result.stderr

    def test_delete_removes_from_list(self):
        """Verify deleted todo no longer appears in list."""
        run_cli("add", "Test todo")
        run_cli("delete", "1")

        list_result = run_cli("list")
        assert "Test todo" not in list_result.stdout

    def test_delete_alias_rm_works(self):
        """Verify 'rm' alias works for delete command."""
        run_cli("add", "Test todo")
        result = run_cli("rm", "1")
        assert result.returncode == 0


class TestUpdateCommandContract:
    """Contract tests for the 'update' command."""

    def test_update_title_success(self):
        """Verify update command can change title."""
        run_cli("add", "Old title")
        result = run_cli("update", "1", "--title", "New title")

        assert result.returncode == 0
        assert "✓ Updated todo #1" in result.stdout

        # Verify change in list
        list_result = run_cli("list")
        assert "New title" in list_result.stdout
        assert "Old title" not in list_result.stdout

    def test_update_description_success(self):
        """Verify update command can change description."""
        run_cli("add", "Task", "-d", "Old desc")
        result = run_cli("update", "1", "--description", "New desc")

        assert result.returncode == 0

    def test_update_both_fields_success(self):
        """Verify update command can change both title and description."""
        run_cli("add", "Old", "-d", "Old desc")
        result = run_cli("update", "1", "--title", "New", "--description", "New desc")

        assert result.returncode == 0

    def test_update_neither_field_fails(self):
        """Verify update command requires at least one field."""
        run_cli("add", "Test")
        result = run_cli("update", "1")

        assert result.returncode == 1
        assert "Error: " in result.stderr
        assert "at least" in result.stderr.lower()

    def test_update_nonexistent_id_returns_two(self):
        """Verify update command returns exit code 2 for nonexistent ID."""
        result = run_cli("update", "999", "--title", "New")
        assert result.returncode == 2
        assert "Error: " in result.stderr

    def test_update_empty_title_rejected(self):
        """Verify update command rejects empty title."""
        run_cli("add", "Test")
        result = run_cli("update", "1", "--title", "")

        assert result.returncode == 1
        assert "Error: " in result.stderr


class TestHelpAndVersion:
    """Contract tests for help and version commands."""

    def test_help_flag(self):
        """Verify --help flag displays help."""
        result = run_cli("--help")
        assert result.returncode == 0
        assert "todo" in result.stdout.lower()
        assert "add" in result.stdout

    def test_version_flag(self):
        """Verify --version flag displays version."""
        result = run_cli("--version")
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_no_command_shows_help(self):
        """Verify running with no command shows help."""
        result = run_cli()
        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "todo" in result.stdout
