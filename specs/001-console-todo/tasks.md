# Tasks: Console Todo App

**Input**: Design documents from `/specs/001-console-todo/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per constitution requirement (Principle V: Testing Strategy)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `console-app/src/`, `console-app/tests/` at repository root
- Paths shown below use single project structure per plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create console-app/ directory structure with src/ and tests/ subdirectories
- [x] T002 Initialize UV project with pyproject.toml in console-app/ (Python 3.13+, pytest dependency)
- [x] T003 [P] Create __init__.py files in console-app/src/, console-app/src/models/, console-app/src/lib/, console-app/src/cli/
- [x] T004 [P] Create __init__.py files in console-app/tests/, console-app/tests/contract/, console-app/tests/integration/, console-app/tests/unit/
- [x] T005 [P] Create console-app/README.md with project overview and quick start
- [x] T006 [P] Create console-app/src/__main__.py to enable python -m console_app invocation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Implement Todo model dataclass in console-app/src/models/todo.py with id, title, description, status, created_at fields
- [x] T008 Add validation methods to Todo model: validate_title (max 500 chars, non-empty), validate_description (max 2000 chars)
- [x] T009 Implement TodoManager class skeleton in console-app/src/lib/todo_manager.py with __init__ method (dict storage, _next_id counter)
- [x] T010 Add custom exceptions in console-app/src/lib/todo_manager.py: TodoNotFoundError, ValidationError
- [x] T011 Create CLI argument parser skeleton in console-app/src/cli/main.py with argparse setup and subparser structure

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Todo Items (Priority: P1) 🎯 MVP

**Goal**: Users can quickly capture tasks with title and optional description

**Independent Test**: Can be fully tested by running add command with various inputs and verifying todos are stored

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T012 [P] [US1] Contract test for add command in console-app/tests/contract/test_cli_contract.py - verify success exit code, output format, ID returned
- [x] T013 [P] [US1] Contract test for add validation errors in console-app/tests/contract/test_cli_contract.py - empty title, too long title
- [x] T014 [P] [US1] Integration test for US1 acceptance scenarios in console-app/tests/integration/test_user_journeys.py - add with title only, add with description, reject empty
- [x] T015 [P] [US1] Unit test for TodoManager.add() method in console-app/tests/unit/test_todo_manager.py - ID assignment, validation, storage

### Implementation for User Story 1

- [x] T016 [US1] Implement TodoManager.add(title, description) method in console-app/src/lib/todo_manager.py - create Todo, assign ID, store in dict, return Todo
- [x] T017 [US1] Implement CLI add command handler in console-app/src/cli/main.py - parse arguments, call TodoManager.add(), format success output
- [x] T018 [US1] Add error handling for add command in console-app/src/cli/main.py - catch ValidationError, output to stderr, exit code 1
- [x] T019 [US1] Add success output formatting for add command in console-app/src/cli/main.py - print "✓ Added todo #{id}: {title}"

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View All Todos (Priority: P2)

**Goal**: Users can see all their todos at a glance with status

**Independent Test**: Can be fully tested by adding several todos then viewing list to verify all items appear

### Tests for User Story 2

- [x] T020 [P] [US2] Contract test for list command in console-app/tests/contract/test_cli_contract.py - verify table format, exit code 0, empty state message
- [x] T021 [P] [US2] Integration test for US2 acceptance scenarios in console-app/tests/integration/test_user_journeys.py - list multiple todos, empty list, status display
- [x] T022 [P] [US2] Unit test for TodoManager.list_all() method in console-app/tests/unit/test_todo_manager.py - return all todos, empty list, ordering

### Implementation for User Story 2

- [x] T023 [US2] Implement TodoManager.list_all() method in console-app/src/lib/todo_manager.py - return list of all Todo objects sorted by ID
- [x] T024 [US2] Implement CLI list command handler in console-app/src/cli/main.py - call TodoManager.list_all(), format table output
- [x] T025 [US2] Add table formatting logic in console-app/src/cli/main.py - column headers, separators, truncation for long text
- [x] T026 [US2] Add empty state handling for list command in console-app/src/cli/main.py - detect empty list, print helpful message

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Mark Todos Complete (Priority: P3)

**Goal**: Users can mark tasks as complete when finished

**Independent Test**: Can be fully tested by adding todos, marking specific ones complete, verifying status changes

### Tests for User Story 3

- [x] T027 [P] [US3] Contract test for complete command in console-app/tests/contract/test_cli_contract.py - success case, not found error, invalid ID error, idempotency
- [x] T028 [P] [US3] Integration test for US3 acceptance scenarios in console-app/tests/integration/test_user_journeys.py - mark pending complete, error cases, already complete
- [x] T029 [P] [US3] Unit test for TodoManager.complete(id) method in console-app/tests/unit/test_todo_manager.py - status change, not found error, idempotency

### Implementation for User Story 3

- [x] T030 [US3] Implement TodoManager.get(id) method in console-app/src/lib/todo_manager.py - retrieve Todo by ID, raise TodoNotFoundError if missing
- [x] T031 [US3] Implement TodoManager.complete(id) method in console-app/src/lib/todo_manager.py - get todo, set status="complete", return updated Todo
- [x] T032 [US3] Implement CLI complete command handler in console-app/src/cli/main.py - parse ID, call TodoManager.complete(), format success output
- [x] T033 [US3] Add error handling for complete command in console-app/src/cli/main.py - catch TodoNotFoundError (exit 2), invalid ID format (exit 1)

**Checkpoint**: All user stories 1-3 should now be independently functional

---

## Phase 6: User Story 4 - Delete Todos (Priority: P4)

**Goal**: Users can remove todos that are no longer relevant

**Independent Test**: Can be fully tested by adding todos, deleting specific ones, verifying they no longer appear

### Tests for User Story 4

- [x] T034 [P] [US4] Contract test for delete command in console-app/tests/contract/test_cli_contract.py - success case, not found error, verify removal
- [x] T035 [P] [US4] Integration test for US4 acceptance scenarios in console-app/tests/integration/test_user_journeys.py - delete existing, error cases, verify list updated
- [x] T036 [P] [US4] Unit test for TodoManager.delete(id) method in console-app/tests/unit/test_todo_manager.py - removal from dict, not found error

### Implementation for User Story 4

- [x] T037 [US4] Implement TodoManager.delete(id) method in console-app/src/lib/todo_manager.py - get todo, remove from dict, return deleted Todo
- [x] T038 [US4] Implement CLI delete command handler in console-app/src/cli/main.py - parse ID, call TodoManager.delete(), format success output
- [x] T039 [US4] Add error handling for delete command in console-app/src/cli/main.py - catch TodoNotFoundError (exit 2), invalid ID format (exit 1)

**Checkpoint**: All user stories 1-4 should be independently functional

---

## Phase 7: User Story 5 - Update Todo Content (Priority: P5)

**Goal**: Users can modify todo titles and descriptions

**Independent Test**: Can be fully tested by adding todo, updating fields, verifying changes persist

### Tests for User Story 5

- [x] T040 [P] [US5] Contract test for update command in console-app/tests/contract/test_cli_contract.py - title update, description update, both, validation errors
- [x] T041 [P] [US5] Integration test for US5 acceptance scenarios in console-app/tests/integration/test_user_journeys.py - update scenarios, error cases
- [x] T042 [P] [US5] Unit test for TodoManager.update(id, title, description) method in console-app/tests/unit/test_todo_manager.py - field updates, validation, not found

### Implementation for User Story 5

- [x] T043 [US5] Implement TodoManager.update(id, title, description) method in console-app/src/lib/todo_manager.py - get todo, validate inputs, update fields, return updated Todo
- [x] T044 [US5] Implement CLI update command handler in console-app/src/cli/main.py - parse ID and optional --title/--description flags, call TodoManager.update()
- [x] T045 [US5] Add validation for update command in console-app/src/cli/main.py - require at least one of title or description, validate empty title
- [x] T046 [US5] Add error handling for update command in console-app/src/cli/main.py - catch validation errors and not found errors with appropriate exit codes

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T047 [P] Add help command handler in console-app/src/cli/main.py - display general help text with all commands
- [x] T048 [P] Add --version flag in console-app/src/cli/main.py - display version string
- [x] T049 [P] Add command aliases in console-app/src/cli/main.py - ls for list, done for complete, rm for delete
- [x] T050 [P] Create unit tests for Todo model validation in console-app/tests/unit/test_todo.py - test all validation rules
- [x] T051 [P] Add performance timing test in console-app/tests/integration/test_user_journeys.py - verify all commands execute in <100ms
- [x] T052 [P] Update console-app/README.md with usage examples and all commands documentation
- [x] T053 Run full test suite with coverage report - ensure all tests pass and coverage >80% (COMPLETE: All 112/112 tests passing! Added simple file-based persistence (storage.py) to enable CLI data persistence. Core business logic has 100% coverage.)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses TodoManager.list_all() but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses TodoManager.get() method (new) but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Uses TodoManager.get() method but independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Uses TodoManager.get() method but independently testable

### Within Each User Story

- Tests (if included) SHOULD be written and FAIL before implementation (TDD encouraged, not mandatory per constitution)
- Models before services
- Services before CLI handlers
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005, T006)
- Within Foundational: T007-T008 (Todo model) can run parallel to T009-T010 (TodoManager)
- Once Foundational phase completes, all user story test tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members after Phase 2

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for add command in console-app/tests/contract/test_cli_contract.py"
Task: "Contract test for add validation errors in console-app/tests/contract/test_cli_contract.py"
Task: "Integration test for US1 acceptance scenarios in console-app/tests/integration/test_user_journeys.py"
Task: "Unit test for TodoManager.add() method in console-app/tests/unit/test_todo_manager.py"

# These can all be written in parallel since they test different layers
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T011) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T012-T019)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (T012-T019) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (T020-T026) → Test independently → Deploy/Demo
4. Add User Story 3 (T027-T033) → Test independently → Deploy/Demo
5. Add User Story 4 (T034-T039) → Test independently → Deploy/Demo
6. Add User Story 5 (T040-T046) → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T012-T019)
   - Developer B: User Story 2 (T020-T026)
   - Developer C: User Story 3 (T027-T033)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests should be written first per TDD approach (strongly encouraged)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

## Task Summary

**Total Tasks**: 53 tasks
- Setup (Phase 1): 6 tasks
- Foundational (Phase 2): 5 tasks
- User Story 1 (Phase 3): 8 tasks (4 tests, 4 implementation)
- User Story 2 (Phase 4): 7 tasks (3 tests, 4 implementation)
- User Story 3 (Phase 5): 7 tasks (3 tests, 4 implementation)
- User Story 4 (Phase 6): 6 tasks (3 tests, 3 implementation)
- User Story 5 (Phase 7): 7 tasks (3 tests, 4 implementation)
- Polish (Phase 8): 7 tasks

**Parallel Opportunities**: 23 tasks marked with [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Run add command, verify storage
- US2: Add todos, list them, verify display
- US3: Add todos, mark complete, verify status change
- US4: Add todos, delete one, verify removal
- US5: Add todo, update fields, verify changes

**Suggested MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1) = 19 tasks
