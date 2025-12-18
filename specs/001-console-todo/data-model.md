# Data Model: Console Todo App

**Feature**: Console Todo App (001-console-todo)
**Date**: 2025-12-08
**Phase**: Phase 1 - Data Model Design

## Overview

This document defines the data model for Phase I console todo application. The model is designed to be simple for in-memory storage while being compatible with future database migration in Phase II.

## Entities

### Todo

Represents a single todo item with its metadata and state.

**Attributes**:

| Attribute   | Type                        | Required | Default   | Validation                                      |
|-------------|-----------------------------|---------|-----------|-------------------------------------------------|
| id          | int                         | Yes     | Auto      | Positive integer, unique, auto-incremented      |
| title       | str                         | Yes     | -         | Non-empty, max 500 chars, stripped whitespace   |
| description | str \| None                 | No      | None      | Max 2000 chars if provided                      |
| status      | Literal["pending", "complete"] | Yes  | "pending" | Only "pending" or "complete" allowed            |
| created_at  | datetime                    | Yes     | Auto      | ISO 8601 format, set on creation                |

**Invariants**:
- ID is immutable once assigned
- created_at is immutable (set once on creation)
- title cannot be empty string (must have at least 1 non-whitespace char)
- status can only transition pending → complete (no rollback in Phase I)

**Relationships**: None (single entity model)

**Example**:
```python
Todo(
    id=1,
    title="Buy groceries",
    description="Milk, bread, and eggs",
    status="pending",
    created_at=datetime(2025, 12, 8, 14, 30, 0)
)
```

## State Transitions

### Todo Status Lifecycle

```
┌─────────┐
│  CREATE │ (status = "pending")
└────┬────┘
     │
     ▼
┌─────────┐    complete()    ┌──────────┐
│ pending ├──────────────────>│ complete │
└─────────┘                   └──────────┘
                                    │
                                    │ (terminal state)
                                    ▼
```

**Transitions**:
- **Create**: New todo starts in "pending" state
- **Complete**: User marks todo as done, status changes to "complete"
- **No Rollback**: Phase I does not support uncompleting todos

**Future (Phase II)**:
- May add "archived" status
- May support pending ← complete transition (uncomplete)

## Storage Model (Phase I)

### In-Memory Storage

**Implementation**: Python dict with integer keys

```python
class TodoManager:
    def __init__(self):
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1
```

**Operations Complexity**:
- Create: O(1) - insert into dict
- Read (by ID): O(1) - dict lookup
- Read (all): O(n) - iterate dict values
- Update: O(1) - dict lookup + modify
- Delete: O(1) - dict.pop()

**ID Assignment**:
- Auto-incremented counter starting at 1
- Never reused (even after deletion)
- Monotonically increasing

**Limitations**:
- No persistence (data lost when app exits)
- Single session only
- No concurrent access (single-threaded)
- Max ~1000 todos recommended (performance, not hard limit)

## Validation Rules

### Title Validation

```python
def validate_title(title: str) -> str:
    """Validate and normalize title"""
    if not title or not title.strip():
        raise ValueError("Todo title cannot be empty")

    normalized = title.strip()
    if len(normalized) > 500:
        raise ValueError("Todo title cannot exceed 500 characters")

    return normalized
```

### Description Validation

```python
def validate_description(description: str | None) -> str | None:
    """Validate and normalize description"""
    if description is None:
        return None

    if len(description) > 2000:
        raise ValueError("Todo description cannot exceed 2000 characters")

    return description
```

### Status Validation

```python
def validate_status(status: str) -> Literal["pending", "complete"]:
    """Validate status value"""
    if status not in ("pending", "complete"):
        raise ValueError(f"Invalid status '{status}'. Must be 'pending' or 'complete'")

    return status  # type: ignore
```

## Migration Path to Phase II

### Database Schema (Future)

When migrating to PostgreSQL with SQLModel in Phase II:

```sql
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),  -- NEW: multi-user support
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),     -- NEW: track modifications
    CHECK (status IN ('pending', 'complete')),
    CHECK (length(title) > 0)
);

CREATE INDEX idx_todos_user_id ON todos(user_id);   -- NEW: user isolation
CREATE INDEX idx_todos_status ON todos(status);     -- NEW: filter by status
```

### Breaking Changes

**Phase I → Phase II**:
1. Add `user_id` field (required for multi-tenancy)
2. Add `updated_at` timestamp
3. Change storage from dict to PostgreSQL
4. Add database indexes for query performance

**Code Compatibility**:
- Todo dataclass → SQLModel (similar syntax)
- TodoManager methods → Service layer (add user_id parameter)
- Status transitions remain the same

## Error Cases

### Validation Errors

| Scenario                     | Error Message                                   | HTTP Status (Phase II) |
|------------------------------|-------------------------------------------------|------------------------|
| Empty title                  | "Todo title cannot be empty"                    | 400 Bad Request        |
| Title too long (>500 chars)  | "Todo title cannot exceed 500 characters"       | 400 Bad Request        |
| Description too long         | "Todo description cannot exceed 2000 characters"| 400 Bad Request        |
| Invalid status               | "Invalid status 'X'. Must be 'pending' or 'complete'" | 400 Bad Request |
| Todo ID not found            | "Todo with ID {id} not found"                   | 404 Not Found          |
| Duplicate ID (internal only) | "Todo with ID {id} already exists"              | 500 Internal Error     |

## Data Integrity

### Constraints

**Phase I (In-Memory)**:
- ID uniqueness enforced by dict keys
- Status validation in Todo constructor
- Title/description length validation

**Phase II (Database)**:
- Primary key constraint (id)
- Foreign key constraint (user_id)
- Check constraints (status enum, title non-empty)
- NOT NULL constraints

### Concurrency

**Phase I**: Single-threaded, no concurrency issues

**Phase II**: Database transactions will handle concurrent updates

## Performance Characteristics

**Phase I Target**: <100ms per operation (constitution requirement)

**Expected Performance**:
- Create todo: ~5-10ms
- Get todo by ID: ~1-5ms
- List all todos: ~10-20ms (for 100 todos)
- Update todo: ~5-10ms
- Delete todo: ~1-5ms

**Bottlenecks**: None expected in Phase I (in-memory is fast)

**Phase II Considerations**:
- Database queries: Add indexes on user_id and status
- N+1 query prevention: Use proper JOINs
- Pagination: Implement for list operations

## Testing Strategy

### Unit Tests (models/todo.py)

- Test Todo creation with valid data
- Test validation errors (empty title, too long, etc.)
- Test status transitions
- Test default values

### Unit Tests (lib/todo_manager.py)

- Test CRUD operations
- Test ID auto-increment
- Test error cases (ID not found, etc.)
- Test list operations (empty, multiple todos)

### Integration Tests

- Test full user journeys using data model
- Verify data persists within session
- Test edge cases (1000 todos, special characters)

## References

- Feature Spec: [spec.md](spec.md)
- Research: [research.md](research.md)
- Implementation Plan: [plan.md](plan.md)
