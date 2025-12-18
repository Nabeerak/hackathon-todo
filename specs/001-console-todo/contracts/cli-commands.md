# CLI Contracts: Console Todo App

**Feature**: Console Todo App (001-console-todo)
**Date**: 2025-12-08
**Phase**: Phase 1 - Interface Contracts

## Overview

This document defines the command-line interface (CLI) contracts for the console todo application. These contracts specify the exact command syntax, arguments, exit codes, and output formats that the CLI must adhere to.

## General CLI Conventions

### Invocation

```bash
# Using uv (recommended)
uv run todo <command> [arguments] [options]

# Using python -m
python -m console_app <command> [arguments] [options]

# Using installed package
todo <command> [arguments] [options]
```

### Exit Codes

| Code | Meaning                 | When Used                          |
|------|-------------------------|------------------------------------|
| 0    | Success                 | Command executed successfully      |
| 1    | Validation error        | Invalid input (empty title, etc.)  |
| 2    | Not found error         | Todo ID does not exist             |
| 3    | Command error           | Unknown command or invalid syntax  |
| 127  | Unexpected error        | Internal error (should not occur)  |

### Output Format

- **Success messages**: Plain text to stdout, ends with newline
- **Error messages**: Plain text to stderr, prefixed with "Error: ", ends with newline
- **List output**: Table format to stdout
- **Help text**: Plain text to stdout

## Commands

### 1. Add Todo

**Purpose**: Create a new todo item

**Syntax**:
```bash
todo add <title> [--description <text>]
todo add <title> [-d <text>]
```

**Arguments**:
- `<title>` (required, positional): Todo title string
- `--description`, `-d` (optional): Additional details

**Examples**:
```bash
$ todo add "Buy groceries"
✓ Added todo #1: Buy groceries

$ todo add "Call dentist" --description "Schedule annual checkup"
✓ Added todo #2: Call dentist

$ todo add "Review PR" -d "Check backend changes in PR #123"
✓ Added todo #3: Review PR
```

**Success Output**:
```
✓ Added todo #{id}: {title}
```

**Error Cases**:
```bash
$ todo add ""
Error: Todo title cannot be empty
Exit code: 1

$ todo add "$(python -c 'print("x"*501)')"
Error: Todo title cannot exceed 500 characters
Exit code: 1
```

**Contract Tests**:
- Verify exit code 0 on success
- Verify todo ID is returned and can be used in subsequent commands
- Verify error exit code 1 for validation failures
- Verify empty title rejected
- Verify title length limit enforced

---

### 2. List Todos

**Purpose**: Display all todos with their status

**Syntax**:
```bash
todo list
todo ls     # alias
```

**Arguments**: None

**Examples**:
```bash
$ todo list
ID | Status   | Title            | Description
---+----------+------------------+------------------------
1  | pending  | Buy groceries    | Milk and bread
2  | complete | Call dentist     | Schedule annual checkup
3  | pending  | Review PR        |

$ todo list  # when empty
No todos found. Use 'todo add "title"' to create one.
```

**Success Output Format**:
```
ID | Status   | Title            | Description
---+----------+------------------+------------------------
{id}  | {status}  | {title}          | {description}
{id}  | {status}  | {title}          | {description}
...
```

**Column Widths**:
- ID: 3 chars (max 999)
- Status: 8 chars ("pending" or "complete")
- Title: 20 chars (truncated with "..." if longer)
- Description: 30 chars (truncated with "..." if longer, empty if None)

**Empty State**:
```
No todos found. Use 'todo add "title"' to create one.
```

**Error Cases**: None (listing empty todos is success)

**Contract Tests**:
- Verify exit code 0 always
- Verify table format matches specification
- Verify empty state message when no todos
- Verify truncation for long titles/descriptions
- Verify pending and complete statuses display correctly

---

### 3. Complete Todo

**Purpose**: Mark a todo as complete

**Syntax**:
```bash
todo complete <id>
todo done <id>      # alias
```

**Arguments**:
- `<id>` (required, positional): Todo ID (integer)

**Examples**:
```bash
$ todo complete 1
✓ Marked todo #1 as complete: Buy groceries

$ todo done 2
✓ Marked todo #2 as complete: Call dentist
```

**Success Output**:
```
✓ Marked todo #{id} as complete: {title}
```

**Error Cases**:
```bash
$ todo complete 999
Error: Todo with ID 999 not found
Exit code: 2

$ todo complete abc
Error: Invalid todo ID 'abc'. Must be a positive integer.
Exit code: 1

$ todo complete 1   # already complete
✓ Marked todo #1 as complete: Buy groceries
Exit code: 0        # idempotent - not an error
```

**Contract Tests**:
- Verify exit code 0 on success
- Verify status changes from pending to complete
- Verify idempotency (completing already-complete todo is success)
- Verify error exit code 2 for non-existent ID
- Verify error exit code 1 for invalid ID format

---

### 4. Delete Todo

**Purpose**: Remove a todo permanently

**Syntax**:
```bash
todo delete <id>
todo rm <id>      # alias
```

**Arguments**:
- `<id>` (required, positional): Todo ID (integer)

**Examples**:
```bash
$ todo delete 1
✓ Deleted todo #1: Buy groceries

$ todo rm 2
✓ Deleted todo #2: Call dentist
```

**Success Output**:
```
✓ Deleted todo #{id}: {title}
```

**Error Cases**:
```bash
$ todo delete 999
Error: Todo with ID 999 not found
Exit code: 2

$ todo delete abc
Error: Invalid todo ID 'abc'. Must be a positive integer.
Exit code: 1
```

**Contract Tests**:
- Verify exit code 0 on success
- Verify todo no longer appears in list after deletion
- Verify error exit code 2 for non-existent ID
- Verify error exit code 1 for invalid ID format

---

### 5. Update Todo

**Purpose**: Modify todo title and/or description

**Syntax**:
```bash
todo update <id> [--title <text>] [--description <text>]
todo update <id> [-t <text>] [-d <text>]
```

**Arguments**:
- `<id>` (required, positional): Todo ID (integer)
- `--title`, `-t` (optional): New title
- `--description`, `-d` (optional): New description

**At least one of --title or --description must be provided.**

**Examples**:
```bash
$ todo update 1 --title "Buy groceries and cook dinner"
✓ Updated todo #1

$ todo update 2 -d "Call before 5pm"
✓ Updated todo #2

$ todo update 3 --title "Review PR #456" --description "Focus on auth changes"
✓ Updated todo #3
```

**Success Output**:
```
✓ Updated todo #{id}
```

**Error Cases**:
```bash
$ todo update 999 --title "New title"
Error: Todo with ID 999 not found
Exit code: 2

$ todo update 1
Error: Must provide at least --title or --description
Exit code: 1

$ todo update abc --title "New"
Error: Invalid todo ID 'abc'. Must be a positive integer.
Exit code: 1

$ todo update 1 --title ""
Error: Todo title cannot be empty
Exit code: 1
```

**Contract Tests**:
- Verify exit code 0 on success
- Verify title updates when --title provided
- Verify description updates when --description provided
- Verify both update when both provided
- Verify error when neither provided
- Verify error exit code 2 for non-existent ID
- Verify validation errors for empty/too-long values

---

### 6. Help

**Purpose**: Display usage information

**Syntax**:
```bash
todo --help
todo -h
todo help
todo <command> --help
```

**Examples**:
```bash
$ todo --help
usage: todo <command> [<args>]

Available commands:
  add        Add a new todo
  list       List all todos (alias: ls)
  complete   Mark todo as complete (alias: done)
  delete     Delete a todo (alias: rm)
  update     Update todo title or description

Run 'todo <command> --help' for command-specific help.

$ todo add --help
usage: todo add <title> [--description <text>]

Add a new todo item.

positional arguments:
  title                 Todo title (required)

optional arguments:
  --description, -d     Additional details (optional)

examples:
  todo add "Buy groceries"
  todo add "Call dentist" -d "Schedule checkup"
```

**Contract Tests**:
- Verify exit code 0
- Verify help text includes all commands
- Verify command-specific help works for each command

---

## Version Command

**Purpose**: Display application version

**Syntax**:
```bash
todo --version
todo -v
```

**Output**:
```
console-todo version 1.0.0
```

**Contract Tests**:
- Verify exit code 0
- Verify version string format

---

## Error Handling

### General Error Format

All errors written to stderr with format:
```
Error: {clear description of what went wrong}
```

### Error Message Guidelines

- Start with "Error: "
- Clear and specific (not generic "An error occurred")
- Suggest how to fix if possible
- No stack traces visible to user (log internally)

**Examples**:
```
Error: Todo title cannot be empty
Error: Todo with ID 999 not found
Error: Unknown command 'foo'. Run 'todo --help' for usage.
Error: Must provide at least --title or --description
```

---

## Special Characters Handling

### Quotes in Arguments

```bash
# Use shell quoting for titles with spaces/special chars
$ todo add "Buy \"milk\" and bread"
✓ Added todo #1: Buy "milk" and bread

$ todo add 'Review John'\''s PR'
✓ Added todo #2: Review John's PR
```

### Newlines and Tabs

```bash
# Newlines in description preserved
$ todo add "Task" --description "Line 1
Line 2"
✓ Added todo #1: Task

$ todo list
ID | Status  | Title | Description
---+---------+-------+--------------------
1  | pending | Task  | Line 1\nLine 2
```

### Emojis and Unicode

```bash
$ todo add "🚀 Launch app"
✓ Added todo #1: 🚀 Launch app

$ todo add "Café meeting"
✓ Added todo #2: Café meeting
```

---

## Performance Contracts

Per constitution (Principle VII):
- All commands must execute in < 100ms (p95)
- Measured from shell invocation to exit

**Monitoring**: Integration tests track execution time

---

## Backward Compatibility (Phase II)

When migrating to web API in Phase II:

| CLI Command        | API Endpoint         | Method | Notes                    |
|--------------------|----------------------|--------|--------------------------|
| `todo add`         | `POST /todos`        | POST   | Add auth header          |
| `todo list`        | `GET /todos`         | GET    | Returns JSON array       |
| `todo complete ID` | `PATCH /todos/:id`   | PATCH  | Set status=complete      |
| `todo delete ID`   | `DELETE /todos/:id`  | DELETE | -                        |
| `todo update ID`   | `PATCH /todos/:id`   | PATCH  | Update fields            |

CLI will remain functional in Phase II as a client to the API.

---

## Testing Requirements

### Contract Test Coverage

For each command:
1. Success case (exit code 0)
2. Validation error cases (exit code 1)
3. Not found error cases (exit code 2)
4. Output format verification
5. Idempotency where applicable

### Test Implementation

```python
# Example contract test structure
def test_add_todo_success():
    result = subprocess.run(
        ["todo", "add", "Test todo"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert result.stdout.startswith("✓ Added todo #")

def test_add_todo_empty_title():
    result = subprocess.run(
        ["todo", "add", ""],
        capture_output=True,
        text=True
    )
    assert result.returncode == 1
    assert "Error: Todo title cannot be empty" in result.stderr
```

---

## References

- Feature Spec: [spec.md](../spec.md)
- Data Model: [data-model.md](../data-model.md)
- Implementation Plan: [plan.md](../plan.md)
