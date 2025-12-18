# Console Todo App - Phase I

A simple command-line todo application with in-memory storage built with Python 3.13+ and UV.

## Features

- ✅ Add todo items with title and optional description
- ✅ View all todos with their status
- ✅ Mark todos as complete
- ✅ Delete todos
- ✅ Update todo titles and descriptions

## Quick Start

### Prerequisites

- Python 3.13 or higher
- UV package manager

### Installation

```bash
# Install dependencies
cd console-app
uv sync

# Run the app
uv run todo --help
```

### Basic Usage

```bash
# Add a todo (with title only)
uv run todo add "Buy groceries"

# Add a todo (with title and description)
uv run todo add "Call dentist" --description "Schedule annual checkup"
uv run todo add "Review PR" -d "Check backend changes"  # Short flag

# List all todos
uv run todo list
uv run todo ls  # Alias

# Mark a todo as complete
uv run todo complete 1
uv run todo done 1  # Alias

# Delete a todo
uv run todo delete 2
uv run todo rm 2  # Alias

# Update a todo (title only)
uv run todo update 1 --title "Buy groceries and cook dinner"

# Update a todo (description only)
uv run todo update 1 --description "New details"

# Update a todo (both title and description)
uv run todo update 1 --title "New title" --description "New description"
```

## Commands Reference

### `add` - Add a new todo

**Syntax**: `todo add <title> [--description <text>]`

**Aliases**: None

**Arguments**:
- `title` (required): Todo title (max 500 characters)
- `--description, -d` (optional): Additional details (max 2000 characters)

**Exit Codes**:
- `0`: Success
- `1`: Validation error (empty title, too long, etc.)

**Examples**:
```bash
uv run todo add "Buy milk"
uv run todo add "Meeting" -d "Discuss Q4 roadmap"
```

### `list` / `ls` - View all todos

**Syntax**: `todo list` or `todo ls`

**Aliases**: `ls`

**Arguments**: None

**Exit Codes**:
- `0`: Always (even if empty list)

**Output Format**: Table with columns: ID, Status, Title, Description

**Examples**:
```bash
uv run todo list
uv run todo ls  # Same as list
```

### `complete` / `done` - Mark todo as complete

**Syntax**: `todo complete <id>` or `todo done <id>`

**Aliases**: `done`

**Arguments**:
- `id` (required): Todo ID to complete

**Exit Codes**:
- `0`: Success
- `2`: Todo not found

**Examples**:
```bash
uv run todo complete 3
uv run todo done 3  # Same as complete
```

### `delete` / `rm` - Delete a todo

**Syntax**: `todo delete <id>` or `todo rm <id>`

**Aliases**: `rm`

**Arguments**:
- `id` (required): Todo ID to delete

**Exit Codes**:
- `0`: Success
- `2`: Todo not found

**Examples**:
```bash
uv run todo delete 5
uv run todo rm 5  # Same as delete
```

### `update` - Update todo content

**Syntax**: `todo update <id> [--title <text>] [--description <text>]`

**Aliases**: None

**Arguments**:
- `id` (required): Todo ID to update
- `--title, -t` (optional): New title (max 500 characters)
- `--description, -d` (optional): New description (max 2000 characters)

**Note**: At least one of `--title` or `--description` must be provided.

**Exit Codes**:
- `0`: Success
- `1`: Validation error (empty title, missing fields, etc.)
- `2`: Todo not found

**Examples**:
```bash
# Update title only
uv run todo update 1 --title "Buy groceries and bread"

# Update description only
uv run todo update 1 --description "Updated details"

# Update both
uv run todo update 1 -t "New title" -d "New description"
```

### `--help` - Show help

**Syntax**: `todo --help` or `todo <command> --help`

**Examples**:
```bash
uv run todo --help          # General help
uv run todo add --help      # Help for add command
```

### `--version` - Show version

**Syntax**: `todo --version` or `todo -v`

**Examples**:
```bash
uv run todo --version
uv run todo -v
```

## Development

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test types
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/contract/
```

### Project Structure

```
console-app/
├── src/
│   ├── models/         # Data models (Todo entity)
│   ├── lib/            # Core business logic (TodoManager)
│   └── cli/            # Command-line interface
├── tests/
│   ├── contract/       # CLI interface tests
│   ├── integration/    # End-to-end tests
│   └── unit/           # Unit tests
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

## Architecture

This application follows a **library-first architecture**:

- **`src/models/`**: Pure data models (Todo entity)
- **`src/lib/`**: Core business logic (TodoManager) - reusable in Phase II
- **`src/cli/`**: Thin CLI wrapper (argument parsing, output formatting)

This design enables code reuse in future phases (web API, AI chatbot).

## Performance

All operations execute in < 100ms (per constitution requirement).

## Limitations (Phase I)

- No persistence (data lost when app exits)
- Single user only
- In-memory storage (limited by RAM)

**Phase II**: Web application with database persistence and multi-user support (coming soon).

## License

Hackathon Project - Phase I
