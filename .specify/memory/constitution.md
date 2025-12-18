<!--
SYNC IMPACT REPORT:
Version Change: Initial → 1.0.0
Modified Principles: N/A (initial creation)
Added Sections:
  - Core Principles (7 principles defined)
  - Technology Standards
  - Development Workflow
  - Governance
Removed Sections: N/A
Templates Status:
  ✅ plan-template.md - Constitution Check section already supports custom gates
  ✅ spec-template.md - Mandatory sections align with principles
  ✅ tasks-template.md - Testing and independent story structure align with principles
Follow-up TODOs: None
-->

# Hackathon Todo Evolution Constitution

## Core Principles

### I. Incremental Evolution

Each phase builds on the previous phase without breaking existing functionality.
Phase N must be fully working and validated before Phase N+1 begins. Regression
tests from previous phases must continue to pass. New phases may extend data models
and add capabilities, but must maintain backward compatibility where feasible.

**Rationale**: Progressive development reduces risk and ensures working software
at every milestone.

### II. Spec-Driven Development (NON-NEGOTIABLE)

NO manual code writing is permitted. All code must be generated through the
SpecKitPlus workflow: `/sp.specify` → `/sp.plan` → `/sp.tasks` → `/sp.implement`.
If generated code fails or has defects, the specification or plan must be refined
and regenerated. Manual code edits are prohibited.

**Rationale**: Ensures reproducibility, traceability, and validates that
specifications are sufficiently detailed to drive correct implementation.

### III. Library-First Architecture

Core business logic must be independent of delivery mechanisms (CLI, API, UI).
Domain logic resides in standalone libraries/modules that can be imported and
reused across different interfaces. Libraries must be self-contained,
independently testable, and documented.

**Rationale**: Enables code reuse across phases (console → web → AI chatbot)
and facilitates testing without infrastructure dependencies.

### IV. User Isolation by Design

Starting from Phase II (multi-user web application), all data access must enforce
user-level isolation. Database queries MUST filter by user_id. APIs MUST validate
authentication tokens and reject unauthorized access. No shared state between users.

**Rationale**: Security and privacy are foundational, not retrofitted. Multi-tenancy
must be architected from the start.

### V. Testing Strategy

Three testing layers are required:
- **Contract Tests**: Validate API/CLI interfaces match documented contracts
- **Integration Tests**: Verify end-to-end user journeys work as specified
- **Unit Tests**: Test individual functions and business logic in isolation

Test-Driven Development (TDD) is strongly encouraged but not mandatory. Tests must
be written before or alongside implementation, not as an afterthought.

**Rationale**: Comprehensive testing prevents regressions and validates that
specifications translate to working software.

### VI. Technology Standards

The following technology stack is mandated for consistency across all phases:

- **Languages**: Python 3.13+ (backend/scripts), TypeScript strict mode (frontend)
- **Package Management**: UV (Python), npm/pnpm (Node.js)
- **Backend Framework**: FastAPI with SQLModel ORM
- **Frontend Framework**: Next.js 16+ with App Router
- **Database**: Neon PostgreSQL (serverless)
- **Authentication**: Better Auth with JWT tokens
- **AI/ML**: OpenAI ChatKit (frontend), OpenAI Agents SDK (backend), Official MCP SDK
- **Container Orchestration**: Docker, Kubernetes (Minikube local, DOKS/GKE/AKS cloud)
- **Event Streaming**: Kafka (Redpanda Cloud), Dapr for distributed runtime

Deviations require explicit justification in an ADR.

**Rationale**: Standardization reduces cognitive load, enables code reuse, and
ensures compatibility across phases.

### VII. Performance Budgets

Measurable performance targets enforce quality:

- **Console App** (Phase I): Command execution < 100ms (p95)
- **REST API** (Phase II-V): Endpoint latency < 200ms (p95)
- **Frontend** (Phase II-V): Initial page load < 3 seconds
- **Event Processing** (Phase V): End-to-end event latency < 500ms (p95)

Performance regressions are considered defects. Monitoring and observability
(OpenTelemetry traces, metrics, logs) are required from Phase II onward.

**Rationale**: Performance is a feature. Budgets prevent degradation and ensure
user experience standards are maintained.

## Technology Standards

All phases must use the specified technology stack (see Principle VI). Technology
choices are locked to ensure:
- Compatibility and integration across phases
- Consistent development practices
- Reusable skills and patterns
- Simplified tooling and CI/CD pipelines

New technology introductions require:
1. Explicit user request or clear blocking need
2. ADR documenting decision rationale
3. Compatibility validation with existing stack
4. Update to this constitution

## Development Workflow

### Specification Process

1. **Constitution First**: Establish project principles before any feature work
2. **Feature Specification** (`/sp.specify`): Capture user requirements in natural language
3. **Clarification** (`/sp.clarify`): Resolve ambiguities before design
4. **Implementation Plan** (`/sp.plan`): Architecture, data models, contracts, quickstart
5. **ADRs** (`/sp.adr`): Document significant architectural decisions
6. **Task Generation** (`/sp.tasks`): Break plan into testable, dependency-ordered tasks
7. **Implementation** (`/sp.implement`): Execute tasks and generate code
8. **Validation**: Run tests, verify acceptance criteria, manual smoke test
9. **Commit & PR**: Version control with semantic commit messages

### Iterative Refinement

If `/sp.implement` fails or produces incorrect code:
1. Analyze the error or defect
2. Refine the specification (`spec.md`) with more detail/examples
3. Update the plan (`plan.md`) with clearer architecture guidance
4. Update task descriptions (`tasks.md`) if needed
5. Re-run `/sp.implement`
6. Iterate 2-3 times until success

**Critical**: Never manually edit generated code. Fix the specs instead.

### Quality Gates

Before proceeding to the next phase:
- [ ] All tests passing (contract, integration, unit)
- [ ] Performance budgets met
- [ ] Security requirements validated (authentication, authorization, no hardcoded secrets)
- [ ] User acceptance criteria satisfied
- [ ] Documentation complete (README, quickstart, API docs)
- [ ] Code committed with proper PHR and ADR references

## Governance

### Amendment Process

This constitution may be amended when:
- A principle proves impractical or harmful
- New requirements emerge that need constitutional guidance
- Technology standards require updates

Amendment requires:
1. Proposal with rationale
2. Impact analysis on existing phases
3. Version bump (semantic versioning):
   - **MAJOR**: Backward-incompatible changes (e.g., removing a principle)
   - **MINOR**: New principles or sections added
   - **PATCH**: Clarifications, wording improvements
4. Update to all dependent templates and documentation
5. Commit with message: `docs: amend constitution to vX.Y.Z (reason)`

### Compliance

All implementations, code reviews, and pull requests must verify compliance with
this constitution. Violations require either:
- Correction to bring code into compliance, OR
- ADR justifying the exception with mitigation plan

### Complexity Justification

Introduced complexity (additional abstractions, patterns, dependencies) must be
justified against simpler alternatives. The burden of proof is on complexity.

**Version**: 1.0.0 | **Ratified**: 2025-12-08 | **Last Amended**: 2025-12-08
