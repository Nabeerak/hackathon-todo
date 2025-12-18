# Tasks: Full-Stack Web Application

**Feature Branch**: `002-fullstack-web`
**Input**: Design documents from `/specs/002-fullstack-web/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Monorepo structure**: `backend/src/`, `frontend/src/`
- Backend: Python FastAPI with SQLModel
- Frontend: Next.js 16+ with Better Auth

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and monorepo structure

- [X] T001 Create monorepo directory structure (backend/, frontend/, .env.example, README.md)
- [X] T002 [P] Initialize backend Python project with UV in backend/pyproject.toml
- [X] T003 [P] Initialize frontend Next.js project with TypeScript in frontend/package.json
- [X] T004 [P] Configure backend dependencies (FastAPI, SQLModel, python-jose, passlib, psycopg2) in backend/pyproject.toml
- [X] T005 [P] Configure frontend dependencies (Next.js 16+, Better Auth, React 19+, Tailwind CSS 4+) in frontend/package.json
- [X] T006 [P] Setup environment configuration template in .env.example
- [X] T007 [P] Configure TypeScript strict mode in frontend/tsconfig.json
- [X] T008 [P] Configure Tailwind CSS in frontend/tailwind.config.ts
- [X] T009 Create monorepo README with setup instructions in README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [X] T010 [P] Create database connection management in backend/src/db/connection.py
- [X] T011 [P] Create environment configuration loader in backend/src/config.py
- [X] T012 [P] Setup FastAPI application entry point in backend/src/main.py
- [X] T013 [P] Configure CORS middleware for frontend-backend communication in backend/src/main.py
- [X] T014 Create base SQLModel configuration and database session management in backend/src/db/connection.py

### Frontend Foundation

- [X] T015 [P] Create Next.js root layout with metadata in frontend/src/app/layout.tsx
- [X] T016 [P] Setup Better Auth client configuration in frontend/src/lib/auth.ts
- [X] T017 [P] Create API client with JWT token handling in frontend/src/lib/api.ts
- [X] T018 [P] Create TypeScript types for Task and User entities in frontend/src/types/task.ts
- [X] T019 [P] Setup Tailwind CSS global styles in frontend/src/app/globals.css

### Shared Models

- [X] T020 Create User model with SQLModel in backend/src/models.py (id, email, hashed_password, display_name, created_at)
- [X] T021 Create Task model with SQLModel in backend/src/models.py (id, user_id, title, description, is_completed, created_at, updated_at)
- [X] T022 Create database migration/initialization script in backend/src/db/init_db.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP FOUNDATION

**Goal**: Enable users to create accounts, sign in, and maintain sessions securely

**Independent Test**: Register a new account, sign out, sign back in, verify session persists across browser refresh

### Backend Authentication (US1)

- [X] T023 [P] [US1] Implement password hashing utilities using passlib in backend/src/auth/jwt.py
- [X] T024 [P] [US1] Implement JWT token generation and validation using python-jose in backend/src/auth/jwt.py
- [X] T025 [US1] Create authentication middleware for JWT validation in backend/src/auth/middleware.py
- [X] T026 [US1] Implement signup endpoint (POST /api/auth/signup) in backend/src/api/auth.py
- [X] T027 [US1] Implement signin endpoint (POST /api/auth/signin) in backend/src/api/auth.py
- [X] T028 [US1] Implement signout endpoint (POST /api/auth/signout) in backend/src/api/auth.py
- [X] T029 [US1] Add duplicate email validation to signup endpoint in backend/src/api/auth.py
- [X] T030 [US1] Add password strength validation (min 8 chars) in backend/src/api/auth.py

### Frontend Authentication (US1)

- [X] T031 [P] [US1] Create signup page UI with form validation in frontend/src/app/auth/signup/page.tsx
- [X] T032 [P] [US1] Create signin page UI with form validation in frontend/src/app/auth/signin/page.tsx
- [X] T033 [US1] Integrate Better Auth provider in root layout in frontend/src/app/layout.tsx
- [X] T034 [US1] Implement signup form submission with API integration in frontend/src/app/auth/signup/page.tsx
- [X] T035 [US1] Implement signin form submission with API integration in frontend/src/app/auth/signin/page.tsx
- [X] T036 [US1] Implement signout functionality with session cleanup in frontend/src/components/Header.tsx
- [X] T037 [US1] Add session persistence and automatic token refresh in frontend/src/lib/auth.ts
- [X] T038 [US1] Create landing page with sign in/sign up navigation in frontend/src/app/page.tsx

**Checkpoint**: Users can register, sign in, sign out, and maintain sessions. Authentication is fully functional.

---

## Phase 4: User Story 2 - Create and View Tasks (Priority: P1) 🎯 MVP CORE

**Goal**: Enable authenticated users to create new tasks and view their complete task list

**Independent Test**: Sign in, create multiple tasks with titles and descriptions, refresh page, verify all tasks are displayed

### Backend Task Creation & Viewing (US2)

- [X] T039 [P] [US2] Implement create task endpoint (POST /api/{user_id}/tasks) in backend/src/api/tasks.py
- [X] T040 [P] [US2] Implement list tasks endpoint (GET /api/{user_id}/tasks) in backend/src/api/tasks.py
- [X] T041 [P] [US2] Implement get single task endpoint (GET /api/{user_id}/tasks/{id}) in backend/src/api/tasks.py
- [X] T042 [US2] Add title length validation (max 200 chars) in backend/src/api/tasks.py
- [X] T043 [US2] Add description length validation (max 1000 chars) in backend/src/api/tasks.py
- [X] T044 [US2] Ensure all task queries filter by authenticated user_id in backend/src/api/tasks.py
- [X] T045 [US2] Add automatic timestamp handling (created_at, updated_at) in backend/src/api/tasks.py

### Frontend Task Creation & Viewing (US2)

- [X] T046 [P] [US2] Create main task list page with authentication guard in frontend/src/app/tasks/page.tsx
- [X] T047 [P] [US2] Create TaskList component to display all tasks in frontend/src/components/TaskList.tsx
- [X] T048 [P] [US2] Create TaskItem component to render individual task in frontend/src/components/TaskItem.tsx
- [X] T049 [P] [US2] Create TaskForm component for create/edit in frontend/src/components/TaskForm.tsx
- [X] T050 [US2] Implement task creation form with title and description fields in frontend/src/components/TaskForm.tsx
- [X] T051 [US2] Integrate create task API call with form submission in frontend/src/components/TaskForm.tsx
- [X] T052 [US2] Fetch and display user's task list on page load in frontend/src/app/tasks/page.tsx
- [X] T053 [US2] Add client-side validation (title required, length limits) in frontend/src/components/TaskForm.tsx
- [X] T054 [US2] Display empty state message when no tasks exist in frontend/src/components/TaskList.tsx
- [X] T055 [US2] Add loading and error states for API calls in frontend/src/app/tasks/page.tsx

**Checkpoint**: Users can create tasks and view their complete task list. Core todo functionality is working.

---

## Phase 5: User Story 3 - Mark Tasks as Complete (Priority: P1) 🎯 MVP CORE

**Goal**: Enable users to mark tasks as complete or incomplete and track progress

**Independent Test**: Create tasks, mark some as complete, unmark others, refresh page, verify status persists

### Backend Task Completion (US3)

- [X] T056 [US3] Implement toggle completion endpoint (PATCH /api/{user_id}/tasks/{id}/complete) in backend/src/api/tasks.py
- [X] T057 [US3] Add completion status validation and user ownership check in backend/src/api/tasks.py
- [X] T058 [US3] Update task timestamp (updated_at) on completion toggle in backend/src/api/tasks.py

### Frontend Task Completion (US3)

- [X] T059 [US3] Add completion checkbox/button to TaskItem component in frontend/src/components/TaskItem.tsx
- [X] T060 [US3] Implement toggle completion API call in frontend/src/components/TaskItem.tsx
- [X] T061 [US3] Add visual distinction for completed vs pending tasks (strikethrough, color) in frontend/src/components/TaskItem.tsx
- [X] T062 [US3] Update local state optimistically on completion toggle in frontend/src/app/tasks/page.tsx

**Checkpoint**: Users can mark tasks complete/incomplete. Progress tracking is functional. MVP is feature-complete!

---

## Phase 6: User Story 6 - Multi-User Data Isolation (Priority: P1) 🛡️ SECURITY

**Goal**: Ensure each user can only access their own tasks with proper authentication and authorization

**Independent Test**: Create two user accounts, add tasks to each, verify User A cannot see User B's tasks

### Backend Data Isolation (US6)

- [X] T063 [US6] Add JWT authentication requirement to all task endpoints in backend/src/api/tasks.py
- [X] T064 [US6] Extract user_id from JWT token in authentication middleware in backend/src/auth/middleware.py
- [X] T065 [US6] Validate URL user_id matches authenticated user_id in all task endpoints in backend/src/api/tasks.py
- [X] T066 [US6] Add database query filters to ensure user_id isolation in backend/src/api/tasks.py
- [X] T067 [US6] Return 401 Unauthorized for unauthenticated requests in backend/src/auth/middleware.py
- [X] T068 [US6] Return 403 Forbidden when user_id mismatch detected in backend/src/api/tasks.py

### Frontend Data Isolation (US6)

- [X] T069 [US6] Add JWT token to all API request headers in frontend/src/lib/api.ts
- [X] T070 [US6] Redirect to signin page when authentication fails in frontend/src/lib/api.ts
- [X] T071 [US6] Handle 401/403 errors gracefully with user feedback in frontend/src/lib/api.ts

**Checkpoint**: Multi-user data isolation is enforced. Security requirements are met.

---

## Phase 7: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Enable users to edit task titles and descriptions

**Independent Test**: Create a task, edit its title and/or description, save changes, refresh page, verify updates persisted

### Backend Task Updates (US4)

- [X] T072 [US4] Implement update task endpoint (PUT /api/{user_id}/tasks/{id}) in backend/src/api/tasks.py
- [X] T073 [US4] Add validation for title required and length limits in backend/src/api/tasks.py
- [X] T074 [US4] Verify user ownership before allowing updates in backend/src/api/tasks.py
- [X] T075 [US4] Update timestamp (updated_at) on task modification in backend/src/api/tasks.py

### Frontend Task Updates (US4)

- [X] T076 [US4] Add edit button to TaskItem component in frontend/src/components/TaskItem.tsx
- [X] T077 [US4] Implement edit mode in TaskForm component in frontend/src/components/TaskForm.tsx
- [X] T078 [US4] Pre-populate form with existing task data for editing in frontend/src/components/TaskForm.tsx
- [X] T079 [US4] Implement cancel edit functionality to revert changes in frontend/src/components/TaskForm.tsx
- [X] T080 [US4] Integrate update task API call in frontend/src/components/TaskForm.tsx
- [X] T081 [US4] Update local state after successful edit in frontend/src/app/tasks/page.tsx

**Checkpoint**: Users can edit existing tasks. Task management is more flexible.

---

## Phase 8: User Story 5 - Delete Tasks (Priority: P2)

**Goal**: Enable users to delete tasks they no longer need

**Independent Test**: Create tasks, delete some with confirmation, refresh page, verify deleted tasks don't reappear

### Backend Task Deletion (US5)

- [X] T082 [US5] Implement delete task endpoint (DELETE /api/{user_id}/tasks/{id}) in backend/src/api/tasks.py
- [X] T083 [US5] Verify user ownership before allowing deletion in backend/src/api/tasks.py
- [X] T084 [US5] Return 404 if task doesn't exist or doesn't belong to user in backend/src/api/tasks.py

### Frontend Task Deletion (US5)

- [X] T085 [US5] Add delete button to TaskItem component in frontend/src/components/TaskItem.tsx
- [X] T086 [US5] Implement confirmation dialog for task deletion in frontend/src/components/TaskItem.tsx
- [X] T087 [US5] Integrate delete task API call in frontend/src/components/TaskItem.tsx
- [X] T088 [US5] Remove task from local state after successful deletion in frontend/src/app/tasks/page.tsx

**Checkpoint**: Users can delete tasks with confirmation. Full CRUD functionality is complete.

---

## Phase 9: User Story 7 - Responsive Web Interface (Priority: P2)

**Goal**: Ensure the application works well on desktop, tablet, and mobile devices

**Independent Test**: Access application on desktop, tablet, and mobile browsers; verify all functionality is usable

### Responsive UI Implementation (US7)

- [X] T089 [P] [US7] Add responsive breakpoints using Tailwind CSS in frontend/src/app/layout.tsx
- [X] T090 [P] [US7] Make task list layout responsive (grid/stack) in frontend/src/components/TaskList.tsx
- [X] T091 [P] [US7] Make task form responsive with appropriate input sizing in frontend/src/components/TaskForm.tsx
- [X] T092 [P] [US7] Ensure touch-friendly buttons and checkboxes on mobile in frontend/src/components/TaskItem.tsx
- [X] T093 [P] [US7] Add responsive navigation header in frontend/src/components/Header.tsx
- [X] T094 [P] [US7] Test and adjust spacing for mobile viewport in frontend/src/app/globals.css
- [X] T095 [US7] Add viewport meta tag for mobile rendering in frontend/src/app/layout.tsx

**Checkpoint**: Application is fully responsive across desktop, tablet, and mobile devices.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling & Validation

- [X] T096 [P] Add comprehensive input sanitization to prevent XSS in backend/src/api/tasks.py and backend/src/api/auth.py
- [X] T097 [P] Implement consistent error response format across all endpoints in backend/src/main.py
- [X] T098 [P] Add user-friendly error messages for all validation failures in frontend/src/lib/api.ts
- [X] T099 [P] Add loading spinners for all async operations in frontend/src/components/ui/Spinner.tsx

### Performance & Optimization

- [X] T100 [P] Add database connection pooling configuration in backend/src/db/connection.py
- [X] T101 [P] Optimize task list query with pagination support in backend/src/api/tasks.py
- [X] T102 [P] Add frontend performance monitoring in frontend/src/app/layout.tsx

### Documentation & Deployment

- [X] T103 [P] Create backend README with setup instructions in backend/README.md
- [X] T104 [P] Create frontend README with setup instructions in frontend/README.md
- [X] T105 [P] Document all API endpoints with examples in backend/README.md
- [X] T106 [P] Create deployment guide for Vercel (frontend) in docs/deployment.md
- [X] T107 [P] Document environment variables in .env.example with descriptions

### Testing & Quality

- [X] T108 [P] Add logging for authentication events in backend/src/api/auth.py
- [X] T109 [P] Add logging for task operations in backend/src/api/tasks.py
- [X] T110 Run manual smoke test following acceptance scenarios from spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - US1 (Authentication) MUST complete before US2-US7 (requires user sessions)
  - US2 (Create/View Tasks) SHOULD complete before US3-US5 (requires tasks to exist)
  - US6 (Data Isolation) can be implemented alongside US2-US3 (security enforcement)
  - US4 (Update Tasks) depends on US2 (requires tasks to exist)
  - US5 (Delete Tasks) depends on US2 (requires tasks to exist)
  - US7 (Responsive UI) can be implemented in parallel with any user story
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Setup (Phase 1)
    ↓
Foundational (Phase 2) ← CRITICAL BLOCKER
    ↓
    ├─→ US1: Authentication (Phase 3) ← MUST COMPLETE FIRST
    │       ↓
    │   ├─→ US2: Create/View Tasks (Phase 4)
    │   │       ↓
    │   │   ├─→ US3: Mark Complete (Phase 5)
    │   │   ├─→ US4: Update Tasks (Phase 7)
    │   │   └─→ US5: Delete Tasks (Phase 8)
    │   │
    │   └─→ US6: Data Isolation (Phase 6) ← Can run parallel with US2-US3
    │
    └─→ US7: Responsive UI (Phase 9) ← Can run parallel anytime after US2
        ↓
    Polish (Phase 10)
```

### Critical Path (Sequential Implementation)

1. **Phase 1**: Setup (T001-T009)
2. **Phase 2**: Foundational (T010-T022) ← CRITICAL BLOCKER
3. **Phase 3**: US1 Authentication (T023-T038) ← MUST COMPLETE
4. **Phase 4**: US2 Create/View (T039-T055)
5. **Phase 5**: US3 Mark Complete (T056-T062)
6. **Phase 6**: US6 Data Isolation (T063-T071) ← SECURITY CRITICAL
7. **Phase 7**: US4 Update Tasks (T072-T081)
8. **Phase 8**: US5 Delete Tasks (T082-T088)
9. **Phase 9**: US7 Responsive UI (T089-T095)
10. **Phase 10**: Polish (T096-T110)

### Parallel Opportunities

**Within Setup (Phase 1):**
- T002, T003, T004, T005, T006, T007, T008 can all run in parallel

**Within Foundational (Phase 2):**
- Backend tasks (T010, T011, T012, T013) can run in parallel
- Frontend tasks (T015, T016, T017, T018, T019) can run in parallel
- Models (T020, T021) must complete before T022

**Within US1 (Phase 3):**
- Backend tasks T023, T024 can run in parallel
- Frontend tasks T031, T032 can run in parallel

**Within US2 (Phase 4):**
- Backend tasks T039, T040, T041 can run in parallel
- Frontend tasks T046, T047, T048, T049 can run in parallel

**Within US7 (Phase 9):**
- All responsive UI tasks (T089-T094) can run in parallel

**Within Polish (Phase 10):**
- All tasks (T096-T109) can run in parallel

---

## Parallel Example: User Story 2 (Create and View Tasks)

```bash
# Launch backend endpoints in parallel:
Task: "Implement create task endpoint (POST /api/{user_id}/tasks) in backend/src/api/tasks.py"
Task: "Implement list tasks endpoint (GET /api/{user_id}/tasks) in backend/src/api/tasks.py"
Task: "Implement get single task endpoint (GET /api/{user_id}/tasks/{id}) in backend/src/api/tasks.py"

# Launch frontend components in parallel:
Task: "Create main task list page in frontend/src/app/tasks/page.tsx"
Task: "Create TaskList component in frontend/src/components/TaskList.tsx"
Task: "Create TaskItem component in frontend/src/components/TaskItem.tsx"
Task: "Create TaskForm component in frontend/src/components/TaskForm.tsx"
```

---

## Implementation Strategy

### MVP First (Minimum Viable Product)

**Goal**: Get a working todo application as quickly as possible

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T022) ← CRITICAL
3. Complete Phase 3: US1 Authentication (T023-T038) ← CRITICAL
4. Complete Phase 4: US2 Create/View Tasks (T039-T055)
5. Complete Phase 5: US3 Mark Complete (T056-T062)
6. Complete Phase 6: US6 Data Isolation (T063-T071) ← SECURITY
7. **STOP and VALIDATE**: You now have a functional multi-user todo app!
   - Users can register and sign in
   - Users can create, view, and complete tasks
   - Data is properly isolated between users
8. Deploy/Demo MVP if ready

**MVP Scope**: Phases 1-6 (72 tasks) = Functional multi-user todo application

### Incremental Delivery (Full Feature Set)

After MVP is validated:

9. Add Phase 7: US4 Update Tasks (T072-T081)
10. Add Phase 8: US5 Delete Tasks (T082-T088)
11. Add Phase 9: US7 Responsive UI (T089-T095)
12. Add Phase 10: Polish (T096-T110)
13. Final validation and deployment

**Full Delivery**: All 10 phases (110 tasks) = Production-ready application

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

- **Developer A**: Focus on US1 (Authentication) - MUST complete first
- After US1 completes:
  - **Developer A**: US2 (Create/View) + US6 (Data Isolation)
  - **Developer B**: US3 (Mark Complete)
  - **Developer C**: US7 (Responsive UI)
- After core features:
  - **Developer A**: US4 (Update)
  - **Developer B**: US5 (Delete)
  - **Developer C**: Polish tasks

---

## Notes

- **[P]** tasks = different files, no dependencies, can run in parallel
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Authentication (US1) MUST complete before other stories can function
- Data Isolation (US6) is CRITICAL for security and should be prioritized
- Stop at any checkpoint to validate story independently
- Commit after each task or logical group
- Follow acceptance scenarios from spec.md for validation

## Task Summary

- **Total Tasks**: 110
- **Setup**: 9 tasks
- **Foundational**: 13 tasks (CRITICAL BLOCKER)
- **US1 (Auth)**: 16 tasks (CRITICAL - MUST COMPLETE FIRST)
- **US2 (Create/View)**: 17 tasks
- **US3 (Complete)**: 7 tasks
- **US6 (Security)**: 9 tasks (CRITICAL)
- **US4 (Update)**: 10 tasks
- **US5 (Delete)**: 7 tasks
- **US7 (Responsive)**: 7 tasks
- **Polish**: 15 tasks

**MVP Scope**: 72 tasks (Phases 1-6)
**Full Delivery**: 110 tasks (All phases)

**Suggested MVP**: Complete through Phase 6 for a functional, secure, multi-user todo application ready for user testing.
