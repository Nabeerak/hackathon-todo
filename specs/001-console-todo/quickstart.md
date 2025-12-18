# Quickstart Guide: Console Todo App

**Feature**: Console Todo App (001-console-todo)
**Date**: 2025-12-08
**Phase**: Phase 1 - Quickstart Documentation

## Prerequisites

- Python 3.13 or higher
- UV package manager

### Install Prerequisites

#### Python 3.13+

```bash
# Check current version
python --version

# If not 3.13+, install via pyenv (recommended)
curl https://pyenv.run | bash
pyenv install 3.13.0
pyenv global 3.13.0
```

#### UV Package Manager

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

## Installation

### Option 1: From Source (Development)

```bash
# Clone or navigate to project
cd hackathon-todo

# Navigate to Phase I directory
cd console-app

# Install dependencies (if any)
uv sync

# Run tests to verify setup
uv run pytest

# Run the application
uv run todo --help
```

### Option 2: Install Locally

```bash
cd console-app

# Install in editable mode
uv pip install -e .

# Now 'todo' command is available
todo --help
```

## Quick Tour (5 minutes)

### Step 1: Add Your First Todo

```bash
$ uv run todo add "Buy groceries"
✓ Added todo #1: Buy groceries
```

### Step 2: Add a Todo with Description

```bash
$ uv run todo add "Call dentist" --description "Schedule annual checkup"
✓ Added todo #2: Call dentist
```

### Step 3: View All Todos

```bash
$ uv run todo list
ID | Status   | Title         | Description
---+----------+---------------+------------------------
1  | pending  | Buy groceries |
2  | pending  | Call dentist  | Schedule annual checkup
```

### Step 4: Mark a Todo Complete

```bash
$ uv run todo complete 1
✓ Marked todo #1 as complete: Buy groceries

$ uv run todo list
ID | Status   | Title         | Description
---+----------+---------------+------------------------
1  | complete | Buy groceries |
2  | pending  | Call dentist  | Schedule annual checkup
```

### Step 5: Update a Todo

```bash
$ uv run todo update 2 --title "Call dentist ASAP"
✓ Updated todo #2

$ uv run todo list
ID | Status   | Title              | Description
---+----------+--------------------+------------------------
1  | complete | Buy groceries      |
2  | pending  | Call dentist ASAP  | Schedule annual checkup
```

### Step 6: Delete a Todo

```bash
$ uv run todo delete 1
✓ Deleted todo #1: Buy groceries

$ uv run todo list
ID | Status   | Title              | Description
---+----------+--------------------+------------------------
2  | pending  | Call dentist ASAP  | Schedule annual checkup
```

🎉 **Congratulations!** You've completed the basic workflow.

## Common Workflows

### Daily Task Management

```bash
# Morning: Add today's tasks
uv run todo add "Team standup at 9am"
uv run todo add "Review PRs"
uv run todo add "Write feature spec"

# View your task list
uv run todo list

# As you complete tasks
uv run todo complete 1
uv run todo complete 2

# Check progress
uv run todo list
```

### Quick Task Capture

```bash
# Capture ideas quickly
uv run todo add "Research Kubernetes deployment strategies"
uv run todo add "Update project README"
uv run todo add "Fix bug in auth flow"

# Add details later
uv run todo update 1 --description "Focus on Helm charts and ArgoCD"
```

### Managing Long-Term Tasks

```bash
# Add a detailed task
uv run todo add "Prepare quarterly presentation" \
  --description "Include metrics, roadmap, and team highlights. Due: Dec 31"

# Update as you make progress
uv run todo update 1 --description "Status: 50% done. Metrics section complete."

# Complete when done
uv run todo complete 1
```

## All Commands Reference

### Add

```bash
# Basic
uv run todo add "Task title"

# With description
uv run todo add "Task title" --description "Details here"
uv run todo add "Task title" -d "Details here"
```

### List

```bash
# List all todos
uv run todo list
uv run todo ls     # short alias
```

### Complete

```bash
# Mark as complete
uv run todo complete 1
uv run todo done 1     # alias
```

### Delete

```bash
# Delete a todo
uv run todo delete 1
uv run todo rm 1       # alias
```

### Update

```bash
# Update title
uv run todo update 1 --title "New title"
uv run todo update 1 -t "New title"

# Update description
uv run todo update 1 --description "New description"
uv run todo update 1 -d "New description"

# Update both
uv run todo update 1 --title "New title" --description "New description"
```

### Help

```bash
# General help
uv run todo --help
uv run todo -h

# Command-specific help
uv run todo add --help
uv run todo list --help
```

### Version

```bash
uv run todo --version
uv run todo -v
```

## Tips & Tricks

### Use Shell Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias todo='uv run todo'
```

Then use directly:

```bash
todo add "Buy milk"
todo list
```

### Batch Operations

```bash
# Add multiple todos quickly
todo add "Task 1"
todo add "Task 2"
todo add "Task 3"

# Complete multiple in sequence
todo complete 1 && todo complete 2 && todo complete 3
```

### Pipe to grep for Filtering

```bash
# Show only pending todos
todo list | grep pending

# Show only complete todos
todo list | grep complete

# Search for specific keywords
todo list | grep "dentist"
```

### Special Characters

```bash
# Quotes in titles
todo add "Review \"API design\" document"

# Apostrophes
todo add 'Update John'\''s code'

# Emojis
todo add "🚀 Launch feature"
```

## Troubleshooting

### Command Not Found

**Problem**: `todo: command not found`

**Solution**:
```bash
# Use full path
uv run todo --help

# Or install package locally
cd console-app
uv pip install -e .
```

### Python Version Too Old

**Problem**: `Python 3.13+ required`

**Solution**:
```bash
# Install Python 3.13 via pyenv
pyenv install 3.13.0
pyenv local 3.13.0
```

### UV Not Installed

**Problem**: `uv: command not found`

**Solution**:
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart shell or source profile
source ~/.bashrc  # or ~/.zshrc
```

### Tests Failing

**Problem**: `pytest` fails

**Solution**:
```bash
# Ensure dependencies installed
uv sync

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_todo.py
```

## Testing

### Run All Tests

```bash
cd console-app
uv run pytest
```

### Run Specific Test Layers

```bash
# Contract tests only
uv run pytest tests/contract/

# Integration tests only
uv run pytest tests/integration/

# Unit tests only
uv run pytest tests/unit/
```

### Run with Coverage

```bash
uv run pytest --cov=src --cov-report=html
```

### Run Tests in Watch Mode

```bash
uv run pytest-watch
```

## Performance

**Expected Performance** (per constitution requirement: <100ms):

| Command         | Typical Time | Max (p95) |
|-----------------|--------------|-----------|
| `todo add`      | 5-10ms       | <100ms    |
| `todo list`     | 10-20ms      | <100ms    |
| `todo complete` | 5-10ms       | <100ms    |
| `todo delete`   | 5-10ms       | <100ms    |
| `todo update`   | 5-10ms       | <100ms    |

All operations are in-memory, so performance should be excellent.

## Limitations (Phase I)

- **No persistence**: Data is lost when app exits
- **Single user**: No multi-user support
- **In-memory only**: Limited to available RAM
- **No sync**: Cannot share todos between devices
- **No reminders**: No notification system

**Phase II (Coming Soon)**: Web application with database persistence, multi-user support, and authentication.

## Project Structure

```text
console-app/
├── src/
│   ├── models/         # Data models (Todo entity)
│   ├── lib/            # Core business logic
│   └── cli/            # Command-line interface
├── tests/
│   ├── contract/       # CLI interface tests
│   ├── integration/    # End-to-end tests
│   └── unit/           # Unit tests
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

## Development

### Code Structure

The codebase follows **library-first architecture** (Constitution Principle III):

- **`src/models/`**: Pure data models (Todo entity)
- **`src/lib/`**: Core business logic (TodoManager)
- **`src/cli/`**: Thin CLI wrapper (argument parsing, output formatting)

This separation enables:
- Easy testing (business logic has no CLI dependencies)
- Code reuse in Phase II (web API will import `lib/` module)
- Clear separation of concerns

### Adding Features

To add a new feature:

1. **Specify**: Update [spec.md](spec.md) with requirements
2. **Plan**: Update [plan.md](plan.md) with design
3. **Implement**: Follow library-first pattern
4. **Test**: Add contract, integration, and unit tests
5. **Document**: Update this quickstart guide

## What's Next?

### Phase II: Web Application

Coming next:
- FastAPI backend with PostgreSQL database
- Next.js frontend with modern UI
- Multi-user support with authentication
- Data persistence
- REST API

The `lib/` module from Phase I will be reused without modification!

### Phase III: AI Chatbot

Future enhancements:
- Natural language todo management
- OpenAI ChatKit frontend
- MCP server for tool integration
- Conversational interface

## Get Help

- **Bugs**: Check test failures with `uv run pytest -v`
- **Questions**: Review [spec.md](spec.md) and [plan.md](plan.md)
- **Contributing**: Follow spec-driven development workflow

## Validation Tests

Run these tests to verify everything works:

```bash
# Test 1: Add and list
todo add "Test todo"
todo list | grep "Test todo"

# Test 2: Complete
todo complete 1
todo list | grep "complete"

# Test 3: Update
todo update 1 --title "Updated test"
todo list | grep "Updated test"

# Test 4: Delete
todo delete 1
[ "$(todo list | grep -c 'Test todo')" -eq "0" ] && echo "✓ Delete works"

# Test 5: Error handling
todo add "" 2>&1 | grep "Error: Todo title cannot be empty"

# Test 6: All tests pass
pytest
```

If all validation tests pass: **✅ Setup complete!**

## References

- **Feature Spec**: [spec.md](spec.md)
- **Implementation Plan**: [plan.md](plan.md)
- **Data Model**: [data-model.md](data-model.md)
- **CLI Contracts**: [contracts/cli-commands.md](contracts/cli-commands.md)
- **Constitution**: `../.specify/memory/constitution.md`
