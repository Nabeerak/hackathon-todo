"""Command-line interface for the console todo app."""

import argparse
import sys
from console_app.lib.todo_manager import TodoManager, TodoNotFoundError, ValidationError
from console_app.lib.storage import load_state, save_state


# Global TodoManager instance (persisted to disk for CLI)
todo_manager = TodoManager()


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser with all subcommands
    """
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Console todo app - manage your tasks from the command line",
    )

    parser.add_argument(
        "--version", "-v", action="version", version="console-todo version 1.0.0"
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="Todo title (required)")
    add_parser.add_argument(
        "--description", "-d", help="Optional additional details", default=None
    )

    # List command
    list_parser = subparsers.add_parser(
        "list", aliases=["ls"], help="List all todos"
    )

    # Complete command
    complete_parser = subparsers.add_parser(
        "complete", aliases=["done"], help="Mark a todo as complete"
    )
    complete_parser.add_argument("id", type=int, help="Todo ID to complete")

    # Delete command
    delete_parser = subparsers.add_parser(
        "delete", aliases=["rm"], help="Delete a todo"
    )
    delete_parser.add_argument("id", type=int, help="Todo ID to delete")

    # Update command
    update_parser = subparsers.add_parser(
        "update", help="Update todo title or description"
    )
    update_parser.add_argument("id", type=int, help="Todo ID to update")
    update_parser.add_argument("--title", "-t", help="New title", default=None)
    update_parser.add_argument(
        "--description", "-d", help="New description", default=None
    )

    return parser


def cmd_add(args: argparse.Namespace) -> int:
    """Handle the 'add' command.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        todo = todo_manager.add(args.title, args.description)
        print(f"✓ Added todo #{todo.id}: {todo.title}")
        return 0
    except ValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """Handle the 'list' command.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (always 0)
    """
    todos = todo_manager.list_all()

    if not todos:
        print('No todos found. Use \'todo add "title"\' to create one.')
        return 0

    # Print table header
    print("ID | Status   | Title            | Description")
    print("---+----------+------------------+------------------------")

    # Print each todo
    for todo in todos:
        # Truncate title and description to fit column widths
        title = todo.title[:17] + "..." if len(todo.title) > 20 else todo.title
        desc = ""
        if todo.description:
            desc = (
                todo.description[:27] + "..."
                if len(todo.description) > 30
                else todo.description
            )

        # Format status to be consistent width
        status = todo.status.ljust(8)

        # Print row
        print(f"{todo.id:<3}| {status} | {title:<20} | {desc}")

    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    """Handle the 'complete' command.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for validation error, 2 for not found)
    """
    try:
        todo = todo_manager.complete(args.id)
        print(f"✓ Marked todo #{todo.id} as complete: {todo.title}")
        return 0
    except TodoNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"Error: Invalid todo ID '{args.id}'. Must be a positive integer.", file=sys.stderr)
        return 1


def cmd_delete(args: argparse.Namespace) -> int:
    """Handle the 'delete' command.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for validation error, 2 for not found)
    """
    try:
        todo = todo_manager.delete(args.id)
        print(f"✓ Deleted todo #{todo.id}: {todo.title}")
        return 0
    except TodoNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"Error: Invalid todo ID '{args.id}'. Must be a positive integer.", file=sys.stderr)
        return 1


def cmd_update(args: argparse.Namespace) -> int:
    """Handle the 'update' command.

    Args:
        args: Parsed command arguments

    Returns:
        Exit code (0 for success, 1 for validation error, 2 for not found)
    """
    # Validate that at least one field is provided
    if args.title is None and args.description is None:
        print("Error: Must provide at least --title or --description", file=sys.stderr)
        return 1

    try:
        todo = todo_manager.update(args.id, args.title, args.description)
        print(f"✓ Updated todo #{todo.id}")
        return 0
    except TodoNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except ValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: Invalid todo ID '{args.id}'. Must be a positive integer.", file=sys.stderr)
        return 1


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # If no command provided, show help
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Load saved state from disk
    load_state(todo_manager)

    # Dispatch to command handlers
    command_handlers = {
        "add": cmd_add,
        "list": cmd_list,
        "ls": cmd_list,
        "complete": cmd_complete,
        "done": cmd_complete,
        "delete": cmd_delete,
        "rm": cmd_delete,
        "update": cmd_update,
    }

    handler = command_handlers.get(args.command)
    if handler:
        exit_code = handler(args)

        # Save state after modifying commands (if successful)
        if exit_code == 0 and args.command in ["add", "complete", "done", "delete", "rm", "update"]:
            save_state(todo_manager)

        sys.exit(exit_code)
    else:
        print(f"Error: Unknown command '{args.command}'. Run 'todo --help' for usage.", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
