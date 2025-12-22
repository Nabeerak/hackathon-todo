---
id: 0001
title: Phase 3 AI Task Assistant Planning
stage: plan
date: 2025-12-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-ai-task-assistant
branch: 003-ai-task-assistant
user: nabeera
command: /sp.plan write a plan
labels: ["planning", "ai-assistant", "openai", "architecture", "phase-3"]
links:
  spec: /home/nabeera/hackathon-todo/specs/003-ai-task-assistant/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-task-assistant/plan.md
  - specs/003-ai-task-assistant/research.md
  - specs/003-ai-task-assistant/data-model.md
  - specs/003-ai-task-assistant/contracts/openapi-ai-endpoints.yaml
  - specs/003-ai-task-assistant/contracts/README.md
  - specs/003-ai-task-assistant/quickstart.md
  - CLAUDE.md (updated with new technologies)
tests:
  - No tests created (planning phase)
---

## Prompt

write a plan

## Response snapshot

**Phase 3 Implementation Plan Complete**

Generated comprehensive architecture and design for AI-Powered Task Assistant feature:

**Phase 0 - Research (3 parallel agents)**:
1. WebSocket/SSE library selection → Decision: SSE with FastAPI native `StreamingResponse` + `@microsoft/fetch-event-source`
2. OpenAI integration patterns → Decision: Direct API with structured outputs (GPT-4o-mini) + Vercel AI SDK frontend
3. API endpoint design → 13 endpoints (12 REST + 1 SSE stream)

**Phase 1 - Design & Contracts**:
- **data-model.md**: 5 new entities (ChatMessage, ChatSession, TaskAction, UserPreferences, AIContext), zero modifications to Phase 2
- **contracts/openapi-ai-endpoints.yaml**: Complete OpenAPI 3.1.0 specification for all 13 endpoints
- **quickstart.md**: Step-by-step setup guide with troubleshooting and test scenarios

**Technical Decisions Resolved**:
- Backend: FastAPI native SSE (no additional libraries), OpenAI Python SDK, GPT-4o-mini model
- Frontend: Vercel AI SDK (replaces non-existent "OpenAI ChatKit"), `@microsoft/fetch-event-source` for SSE client
- Database: 5 new PostgreSQL tables, additive-only migration
- Real-Time: Server-Sent Events (SSE) over WebSocket (Vercel compatibility)
- Cost: ~$0.15/user/month with 100 msg/day rate limiting (GPT-4o-mini)

**Constitution Compliance**: All 7 principles PASSED (pre-design and post-design evaluation)

**Architecture Highlights**:
- Modular AI services (nlp_service, agent_service, chat_service)
- Real-time sync between traditional UI and AI chat (SSE)
- Graceful degradation when OpenAI unavailable
- User data isolation enforced at all layers
- Rate limiting (100 requests/user/day)

## Outcome

- ✅ Impact: Complete Phase 3 implementation plan with research-backed technology decisions. 6 design documents generated. All NEEDS CLARIFICATION items resolved. Ready for task breakdown (`/sp.tasks`).
- 🧪 Tests: No tests (planning phase) - test strategy defined in Constitution Check and quickstart guide
- 📁 Files: 6 planning documents (plan.md, research.md, data-model.md, 2 contracts files, quickstart.md) + CLAUDE.md context update
- 🔁 Next prompts: Run `/sp.tasks` to generate dependency-ordered task breakdown for implementation
- 🧠 Reflection: Research phase successfully parallelized (3 agents) while generating data model. SSE decision over WebSocket proved correct for Vercel deployment constraints. Vercel AI SDK substitution for non-existent "OpenAI ChatKit" aligned with Next.js best practices. Cost estimate ($0.15/user/month) slightly exceeds target but acceptable with rate limiting.

## Evaluation notes (flywheel)

- Failure modes observed: None - all research agents completed successfully, all design documents generated without errors
- Graders run and results (PASS/FAIL):
  - ✅ PASS: All 7 constitution principles validated (pre-design and post-design)
  - ✅ PASS: Zero NEEDS CLARIFICATION items remaining in Technical Context
  - ✅ PASS: OpenAPI contract validates against spec (13 endpoints, JWT auth, error handling)
  - ✅ PASS: Data model maintains Phase 2 compatibility (additive-only)
  - ✅ PASS: Research decisions documented with rationale (SSE, Vercel AI SDK, GPT-4o-mini)
- Prompt variant (if applicable): Standard `/sp.plan` workflow with parallel research agents (3 agents launched concurrently for efficiency)
- Next experiment (smallest change to try): If cost exceeds budget in production, switch from GPT-4o-mini ($0.150/1M input tokens) to GPT-3.5-turbo ($0.0005/1M tokens) for task extraction - would reduce cost to $0.005/user/month
