# Research: Console Todo App

**Feature**: Console Todo App (001-console-todo)
**Date**: 2025-12-08
**Phase**: Phase 0 - Research & Decision Documentation

## Overview

This document captures technical research and decisions for implementing the Phase I console todo application. Since requirements are clear and technology stack is mandated by constitution, minimal research was needed.

## Technology Decisions

### Decision 1: Python 3.13+ with UV

**Decision**: Use Python 3.13+ as language and UV as package manager

**Rationale**:
- Mandated by constitution (Principle VI: Technology Standards)
- Python 3.13+ provides modern type hints and performance improvements
- UV is fast, reliable, and supports modern Python packaging standards
- Enables smooth transition to FastAPI in Phase II (same ecosystem)

**Alternatives Considered**:
- None - constitution mandates Python 3.13+ and UV

**Implementation Notes**:
- Use `pyproject.toml` for project configuration
- Leverage dataclasses with type hints for Todo model
- Use standard library only (no external dependencies needed for Phase I)

### Decision 2: In-Memory Storage with Dict

**Decision**: Use Python dict to store todos in memory, keyed by integer ID

**Rationale**:
- Spec requirement: in-memory storage, no persistence
- Simple and performant for single-user, session-scoped use
- Easy to migrate to database in Phase II (same CRUD interface)
- Dict lookup is O(1) for get/update/delete operations

**Alternatives Considered**:
- **List**: Rejected - O(n) lookup by ID, less efficient
- **SQLite in-memory**: Rejected - unnecessary complexity for Phase I, violates YAGNI

**Implementation Notes**:
```python
# Internal storage structure
self._todos: dict[int, Todo] = {}
self._next_id: int = 1
```

### Decision 3: Library-First Architecture

**Decision**: Separate business logic (`lib/`) from CLI interface (`cli/`)

**Rationale**:
- Constitution Principle III: Library-First Architecture
- Enables code reuse in Phase II (FastAPI) and Phase III (AI chatbot)
- Facilitates unit testing without CLI dependencies
- Clear separation of concerns

**Alternatives Considered**:
- **Monolithic CLI script**: Rejected - violates constitution, hard to reuse
- **Service layer pattern**: Rejected - over-engineering for Phase I scope

**Implementation Notes**:
- `lib/todo_manager.py`: Pure Python, no CLI dependencies
- `cli/main.py`: Thin wrapper, only handles arg parsing and formatting
- `models/todo.py`: Shared data model used by both

### Decision 4: CLI Interface Pattern

**Decision**: Use argparse with subcommands (add, list, complete, delete, update)

**Rationale**:
- Standard library solution (no dependencies)
- Natural fit for multiple commands (git-style: `todo add`, `todo list`)
- Built-in help generation
- Easy to test with subprocess

**Alternatives Considered**:
- **Click library**: Rejected - adds dependency, overkill for simple CLI
- **Positional args only**: Rejected - less user-friendly, harder to extend

**Implementation Notes**:
```bash
# Command examples
python -m console_app add "Buy groceries" --description "Milk and bread"
python -m console_app list
python -m console_app complete 1
python -m console_app delete 2
python -m console_app update 3 --title "New title"
```

### Decision 5: Testing Strategy

**Decision**: Three-layer testing with pytest (contract, integration, unit)

**Rationale**:
- Constitution Principle V: Testing Strategy requires all three layers
- pytest is Python standard, mandated in constitution
- Contract tests validate CLI interface stability
- Integration tests verify user journeys end-to-end
- Unit tests ensure business logic correctness

**Alternatives Considered**:
- None - constitution mandates this testing structure

**Implementation Notes**:
- Contract tests: CLI subprocess calls, verify exit codes and output format
- Integration tests: Full user journeys (add → list → complete → list)
- Unit tests: TodoManager methods, Todo model validation

## Performance Considerations

**Target**: <100ms per command execution (p95) per constitution

**Strategy**:
- In-memory operations are naturally fast (no I/O)
- Dict-based storage provides O(1) lookups
- Minimal dependencies reduce startup overhead
- Profile if needed, but expect 5-20ms typical response times

**Monitoring**: Track execution time in integration tests to catch regressions

## Security Considerations

**Phase I Scope**: Single-user, no network, no persistence

**Validation**:
- Input validation: Reject empty titles, validate ID ranges
- No SQL injection risk (no database)
- No XSS risk (terminal output only)
- No auth needed (single-user)

**Future (Phase II)**:
- Will add user authentication (Better Auth)
- Will enforce user_id isolation in database queries
- Will validate all API inputs

## Error Handling

**Strategy**: Clear, actionable error messages per FR-011

**Examples**:
- Empty title: "Error: Todo title cannot be empty"
- Invalid ID: "Error: Todo with ID 99 not found"
- Invalid command: "Error: Unknown command 'foo'. Run 'todo --help' for usage."

**Implementation**: Raise custom exceptions in lib layer, catch and format in CLI layer

## Data Model Considerations

**Todo Entity**:
- ID: int (auto-incremented)
- Title: str (required, max 500 chars)
- Description: str | None (optional, max 2000 chars)
- Status: Literal["pending", "complete"]
- Created: datetime (ISO 8601 format)

**Validation Rules**:
- Title: non-empty, strip whitespace, max length
- Description: optional, max length
- Status: only "pending" or "complete" allowed
- ID: positive integers only

## Migration Path to Phase II

**Reuse Strategy**:
- `models/todo.py` → Maps directly to SQLModel ORM
- `lib/todo_manager.py` → Backend service layer (add user_id parameter)
- CLI → FastAPI endpoints (similar interface)

**Breaking Changes Expected**:
- Add user_id to Todo model
- Change storage from dict to database (PostgreSQL via SQLModel)
- Add authentication/authorization

## Open Questions

None. All requirements clear from specification.

## References

- Feature Spec: [spec.md](spec.md)
- Constitution: `.specify/memory/constitution.md`
- Implementation Plan: [plan.md](plan.md)
