# Implementation Plan: Console Todo App

**Branch**: `001-console-todo` | **Date**: 2025-12-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-console-todo/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a Python 3.13+ console application for managing todo items with in-memory storage. The app provides CLI commands for adding, viewing, completing, deleting, and updating todos. Core business logic will be implemented as a library-first architecture (per constitution) to enable future reuse in Phase II web application and Phase III AI chatbot.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: UV (package manager), standard library (no external packages needed for Phase I)
**Storage**: In-memory (Python dict/list structures, no persistence)
**Testing**: pytest for all test layers (contract, integration, unit)
**Target Platform**: Console/terminal (Linux, macOS, Windows)
**Project Type**: single (console application with library-first architecture)
**Performance Goals**: <100ms command execution (p95) per constitution
**Constraints**: In-memory only (session-scoped), single-user, max 1000 todos per session
**Scale/Scope**: Single user, ~500 lines of code, 5 CLI commands

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Incremental Evolution**: ✅ PASS - This is Phase I (foundation). No previous phase to break.
- **II. Spec-Driven Development**: ✅ PASS - Using `/sp.specify` → `/sp.plan` → `/sp.tasks` → `/sp.implement` workflow.
- **III. Library-First Architecture**: ✅ PASS - Core logic in `src/lib/todo_manager.py`, CLI in `src/cli/main.py` as thin wrapper.
- **IV. User Isolation by Design**: ✅ N/A - Single-user Phase I. Multi-tenancy starts Phase II.
- **V. Testing Strategy**: ✅ PASS - Contract, integration, and unit tests planned in test structure.
- **VI. Technology Standards**: ✅ PASS - Python 3.13+ with UV per constitution requirements.
- **VII. Performance Budgets**: ✅ PASS - Target <100ms per operation matches console app budget.

**Overall Status**: ✅ ALL GATES PASSED - Proceeding to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
console-app/                    # Phase I implementation root
├── pyproject.toml              # UV project configuration
├── README.md                   # Quick start and usage guide
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── todo.py             # Todo entity (dataclass with validation)
│   ├── lib/
│   │   ├── __init__.py
│   │   └── todo_manager.py     # Core business logic (library-first)
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py             # CLI entry point (thin wrapper over lib)
│   └── __main__.py              # Python -m console_app entry point
└── tests/
    ├── __init__.py
    ├── contract/
    │   ├── __init__.py
    │   └── test_cli_contract.py    # CLI interface contract tests
    ├── integration/
    │   ├── __init__.py
    │   └── test_user_journeys.py   # End-to-end user story tests
    └── unit/
        ├── __init__.py
        ├── test_todo.py             # Todo model unit tests
        └── test_todo_manager.py     # TodoManager unit tests
```

**Structure Decision**: Single project structure selected (Option 1 from template). This is a standalone console application with library-first architecture. The `lib/` module contains all business logic and will be reused in Phase II (web API) and Phase III (AI chatbot) without modification. The `cli/` module is a thin adapter that only handles command-line argument parsing and output formatting.

## Complexity Tracking

No violations. Constitution check passed all gates.
