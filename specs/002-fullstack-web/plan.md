# Implementation Plan: Full-Stack Web Application

**Branch**: `002-fullstack-web` | **Date**: 2025-12-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fullstack-web/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Transform the Phase 1 console todo application into a full-stack web application with multi-user authentication, persistent database storage, and a responsive web interface. The system will provide RESTful APIs for task management (create, read, update, delete, complete) with JWT-based authentication ensuring each user can only access their own tasks. Frontend built with Next.js 16+ and Better Auth; backend with FastAPI and SQLModel connecting to Neon PostgreSQL.

**Technical Approach**:
- Reuse Phase 1 task management logic as a library layer
- Implement Better Auth with JWT tokens for authentication
- Create FastAPI backend with JWT validation middleware
- Build Next.js frontend with Better Auth integration
- Deploy frontend to Vercel, backend to compatible platform
- Use Neon PostgreSQL for persistent, multi-user data storage

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend), Node.js 18+
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, python-jose (JWT), passlib (password hashing), psycopg2 (PostgreSQL driver)
- Frontend: Next.js 16+, Better Auth, React 19+, Tailwind CSS 4+

**Storage**: Neon Serverless PostgreSQL (production), SQLite (local development)
**Testing**: pytest (backend), Jest + React Testing Library (frontend), Playwright (E2E)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge), deployed on Vercel (frontend) + compatible backend hosting
**Project Type**: Web application (frontend + backend monorepo)
**Performance Goals**:
- API latency < 200ms p95
- Frontend initial load < 3 seconds
- Support 100+ concurrent users
- Database queries < 50ms p95

**Constraints**:
- Must use specified tech stack (hackathon requirement)
- No manual code writing (spec-driven only)
- JWT tokens expire after 7 days
- Character limits: title 200 chars, description 1000 chars
- Must deploy by December 14, 2025

**Scale/Scope**:
- Expected users: 100-1000 during hackathon
- Task volume: ~10-50 tasks per user
- Database size: < 100MB for hackathon phase
- 7 user stories, 32 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ **I. Incremental Evolution**
**Status**: PASS
**Validation**: Phase 2 builds on Phase 1 console app by:
- Reusing task management logic as library (principle III)
- Adding authentication layer without changing core task operations
- Extending data model with user entity and user_id foreign keys
- Maintaining backward compatibility: Phase 1 console app still functional

### ✅ **II. Spec-Driven Development**
**Status**: PASS
**Validation**:
- Comprehensive specification created via `/sp.specify` (346 lines, all sections complete)
- This plan generated via `/sp.plan`
- Tasks will be generated via `/sp.tasks`
- Implementation via `/sp.implement`
- No manual code writing permitted

### ✅ **III. Library-First Architecture**
**Status**: PASS
**Validation**:
- Phase 1 task operations (add, update, delete, complete, list) will be extracted to `backend/src/lib/task_operations.py`
- Backend API routes will import and call library functions
- Frontend will call API endpoints (not directly manipulate data)
- Library functions testable without FastAPI or Next.js dependencies

### ✅ **IV. User Isolation by Design**
**Status**: PASS
**Validation**:
- All database queries filter by `user_id` (SQLModel filters)
- API endpoints require JWT authentication
- JWT middleware extracts user_id from token
- API routes validate user_id in URL matches authenticated user
- No shared state between users (stateless API design)

### ✅ **V. Testing Strategy**
**Status**: PASS
**Planned Tests**:
- **Contract Tests**: Validate API endpoints match OpenAPI spec (7 endpoints × 2-3 scenarios = ~20 tests)
- **Integration Tests**: End-to-end user journeys (7 user stories = 7 test suites)
- **Unit Tests**: Task operations library, validation logic, JWT utilities (~30 tests)
- **Total**: ~60 automated tests minimum

### ✅ **VI. Technology Standards**
**Status**: PASS
**Compliance**:
- ✅ Python 3.13+ (backend)
- ✅ TypeScript strict mode (frontend)
- ✅ UV package manager (backend)
- ✅ npm/pnpm (frontend)
- ✅ FastAPI with SQLModel ORM
- ✅ Next.js 16+ with App Router
- ✅ Neon PostgreSQL (serverless)
- ✅ Better Auth with JWT tokens
- No deviations; no ADR required

### ✅ **VII. Performance Budgets**
**Status**: PASS
**Budgets**:
- ✅ REST API latency < 200ms (p95) - specified in Success Criteria SC-009 as < 500ms (more lenient, still compliant)
- ✅ Frontend initial load < 3 seconds - aligned with modern web standards
- ✅ Monitoring: Will implement OpenTelemetry or structured logging in Phase 4/5
- Performance testing included in acceptance criteria

**Overall Gate Status**: ✅ **PASS** - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-web/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already created)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-endpoints.yml   # OpenAPI 3.1 spec for REST API
│   └── database-schema.sql # SQL DDL for reference
├── checklists/          # Quality validation
│   └── requirements.md  # Spec validation checklist (already created)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py          # FastAPI application entry point
│   ├── models.py        # SQLModel database models (User, Task)
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py       # JWT token generation and validation
│   │   └── middleware.py # Authentication middleware
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py      # Auth endpoints (signup, signin, signout)
│   │   └── tasks.py     # Task endpoints (CRUD + complete)
│   ├── lib/
│   │   ├── __init__.py
│   │   └── task_operations.py  # Core task logic (reused from Phase 1)
│   ├── db/
│   │   ├── __init__.py
│   │   └── connection.py # Database connection and session management
│   └── config.py        # Environment variables and settings
├── tests/
│   ├── contract/        # API contract tests (OpenAPI validation)
│   ├── integration/     # End-to-end API tests
│   └── unit/            # Library and utility tests
├── pyproject.toml       # UV project configuration
└── README.md

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx   # Root layout with Better Auth provider
│   │   ├── page.tsx     # Home/landing page
│   │   ├── auth/
│   │   │   ├── signin/page.tsx
│   │   │   └── signup/page.tsx
│   │   └── tasks/
│   │       └── page.tsx # Main task list page
│   ├── components/
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx # Create/Edit task form
│   │   └── ui/          # Reusable UI components (Button, Input, etc.)
│   ├── lib/
│   │   ├── auth.ts      # Better Auth client configuration
│   │   └── api.ts       # API client with JWT token handling
│   └── types/
│       └── task.ts      # TypeScript types for Task and User
├── tests/
│   ├── components/      # Component unit tests
│   └── e2e/             # Playwright end-to-end tests
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── README.md

.env.example             # Environment variable template
docker-compose.yml       # Local development environment (optional)
README.md                # Project overview and monorepo setup
```

**Structure Decision**: Selected **Option 2: Web application** with `backend/` and `frontend/` directories in a monorepo. This structure:
- Separates concerns between API and UI
- Allows independent deployment (Vercel for frontend, flexible for backend)
- Shares common documentation and configuration at root level
- Maintains clear boundaries for testing (backend tests separate from frontend tests)
- Facilitates spec-driven development with clear artifact locations

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - All constitution principles satisfied. Complexity is appropriate for a multi-user web application with authentication.
