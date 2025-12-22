# Phase 0 Research: AI-Powered Task Assistant

**Feature**: `003-ai-task-assistant`
**Date**: 2025-12-19
**Phase**: Phase 0 Research (from `/sp.plan`)

## Overview

This document consolidates research findings to resolve all "NEEDS CLARIFICATION" items from the Technical Context section of the implementation plan. Research covers WebSocket/SSE libraries, OpenAI integration patterns, and API endpoint design.

---

## Research Question 1: WebSocket/SSE Library Selection

### Decision: Server-Sent Events (SSE) over WebSocket

**Rationale**:
1. **Vercel Compatibility**: Frontend deploys to Vercel (serverless) which has limited WebSocket support
2. **OpenAI Patterns**: OpenAI streaming APIs use SSE natively - architectural consistency
3. **Simplicity**: HTTP-based with automatic reconnection, simpler than WebSocket lifecycle
4. **Use Case Fit**: AI chat is primarily server→client streaming (AI responses), client→server uses standard HTTP POST

**Transport Protocol Comparison**:

| Criterion | SSE | WebSocket | Winner |
|-----------|-----|-----------|--------|
| Vercel Compatibility | ✅ Full support | ⚠️ Limited (serverless restrictions) | SSE |
| AI Streaming | ✅ Native OpenAI pattern | ❌ Custom implementation | SSE |
| Simplicity | ✅ HTTP-based, auto-reconnect | ❌ Complex connection lifecycle | SSE |
| Bidirectional | ⚠️ Requires HTTP POST for client→server | ✅ True bidirectional | WebSocket |
| Browser Support | ✅ All modern browsers | ✅ All modern browsers | Tie |

### Backend Library: Native FastAPI `StreamingResponse`

**Decision**: Use FastAPI's built-in `StreamingResponse` (no additional library needed)

**Installation**: Already included in FastAPI (no new dependencies)

**Compatibility**:
- ✅ FastAPI native feature
- ✅ Async/await support
- ✅ JWT authentication compatible (middleware)
- ✅ Works on any ASGI server (Uvicorn, Hypercorn)

**Example Implementation**:
```python
# backend/src/api/chat.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from ..auth.jwt import get_current_user
from ..services.ai.chat_service import ChatService
import json

router = APIRouter()

@router.post("/api/chat/stream")
async def stream_chat(request: Request, user=Depends(get_current_user)):
    """SSE endpoint for streaming AI responses"""
    data = await request.json()
    user_message = data.get("message")

    async def event_generator():
        chat_service = ChatService(user_id=user.id)
        async for chunk in chat_service.stream_ai_response(user_message):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

**Alternative Considered**: `sse-starlette` (adds helper utilities on top of StreamingResponse)
- **Pros**: Cleaner API, automatic SSE formatting
- **Cons**: Additional dependency (lightweight but unnecessary)
- **Decision**: Skip for Phase 3 MVP - native FastAPI is sufficient

### Frontend Library: `@microsoft/fetch-event-source`

**Decision**: Use `@microsoft/fetch-event-source` for SSE client

**Installation**:
```bash
pnpm add @microsoft/fetch-event-source
```

**Compatibility**:
- ✅ Next.js 16 App Router (client components)
- ✅ React hooks compatible
- ✅ TypeScript types included
- ✅ Vercel deployment (HTTP-based)
- ✅ Auto-reconnection with exponential backoff
- ✅ JWT authentication via headers

**Example Implementation**:
```typescript
// frontend/src/lib/chatClient.ts
import { fetchEventSource } from '@microsoft/fetch-event-source';

export class ChatClient {
  async sendMessage(
    message: string,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ) {
    const token = localStorage.getItem('jwt_token');

    await fetchEventSource('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ message }),

      onmessage(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'done') {
          onComplete();
        } else {
          onChunk(data.content);
        }
      },

      onerror(err) {
        onError(err);
        throw err; // Stop retrying
      },

      openWhenHidden: true
    });
  }
}
```

**Alternative Considered**: Native Browser `EventSource` API
- **Pros**: Zero dependencies, browser built-in
- **Cons**: Cannot send custom headers (JWT auth requires URL token or cookie), limited reconnection control
- **Decision**: Skip - lack of header support makes JWT authentication cumbersome

### Architecture Pattern

**Client sends messages via HTTP POST** → **Server streams responses via SSE**

```
User Input → POST /api/chat/send (JSON body with message)
            ↓
Server processes with OpenAI
            ↓
← SSE stream /api/chat/stream (server→client chunks)
```

This hybrid approach provides:
- Simple client→server communication (POST)
- Efficient server→client streaming (SSE)
- Vercel compatibility (HTTP-based)
- Graceful degradation (fallback to polling if SSE fails)

---

## Research Question 2: OpenAI Integration Patterns

### Decision: Direct API Calls with Structured Outputs (Primary)

**Recommendation**: Use OpenAI Chat Completions API with `response_format: { type: "json_object" }` for structured task extraction

**Rationale**:
1. **Simplicity**: Direct API calls are easier to debug and understand than Assistants API
2. **Cost Control**: Transparent pricing per request, no hidden storage costs
3. **Performance**: Lower latency than Assistants API (no thread management overhead)
4. **Fit for Use Case**: Single-turn task extraction doesn't need persistent threads
5. **JSON Schema Validation**: Guaranteed structured output matching task schema

**Comparison: Direct API vs Assistants API**

| Criterion | Direct API + Structured Outputs | OpenAI Assistants API | Winner |
|-----------|--------------------------------|----------------------|--------|
| Complexity | ✅ Simple | ❌ Higher (threads, assistants) | Direct API |
| Cost Transparency | ✅ Per-request pricing | ❌ Hidden storage costs | Direct API |
| Latency | ✅ Lower | ❌ Higher (thread overhead) | Direct API |
| State Management | ❌ Manual | ✅ Built-in threading | Assistants |
| Function Calling | ✅ Supported | ✅ Supported | Tie |
| Structured Outputs | ✅ Native JSON schema | ✅ Supported | Tie |

**Implementation Approach**:
- **Phase 3 MVP**: Direct API with structured outputs (GPT-4o-mini for cost efficiency)
- **Future Enhancement**: Add function calling for multi-step workflows (e.g., "show tasks then mark first one complete")
- **Deferred**: Assistants API only if persistent conversations across sessions become a requirement

### Frontend: Vercel AI SDK (Not "OpenAI ChatKit")

**Important Clarification**: "OpenAI ChatKit" does not exist as an official SDK. The constitution reference appears to be a placeholder.

**Recommendation**: Use **Vercel AI SDK** (`ai` package from Vercel)

**Why Vercel AI SDK**:
1. **Official Vercel Integration**: First-party support for Next.js 16 App Router
2. **Streaming Support**: Built-in `useChat()` hook for real-time AI responses
3. **OpenAI Compatible**: Works seamlessly with OpenAI API
4. **React Hooks**: Clean integration with React components
5. **TypeScript**: Full type safety
6. **Edge Runtime**: Compatible with Vercel Edge Functions

**Installation**:
```bash
pnpm add ai openai
```

**Example Usage (Next.js App Router)**:
```typescript
// app/api/chat/route.ts (backend API route)
import OpenAI from 'openai';
import { OpenAIStream, StreamingTextResponse } from 'ai';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function POST(req: Request) {
  const { messages } = await req.json();

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    stream: true,
    messages,
  });

  const stream = OpenAIStream(response);
  return new StreamingTextResponse(stream);
}

// app/page.tsx (frontend component)
'use client';
import { useChat } from 'ai/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat();

  return (
    <div>
      {messages.map(m => (
        <div key={m.id}>{m.role}: {m.content}</div>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
      </form>
    </div>
  );
}
```

**Alternative Considered**: Build custom React components
- **Pros**: Full UI/UX control
- **Cons**: More development effort, no built-in streaming/session handling
- **Decision**: Use Vercel AI SDK for Phase 3 MVP, custom components only if needed for specific UX requirements

### Prompt Engineering for Task Extraction

**System Prompt Template**:
```typescript
const TASK_EXTRACTION_SYSTEM_PROMPT = `You are a task extraction assistant. Extract structured task information from natural language input.

Output JSON matching this schema:
{
  "tasks": [{
    "title": "string (required, max 100 chars)",
    "description": "string (optional, max 500 chars)",
    "dueDate": "ISO 8601 date string or null",
    "priority": "low" | "medium" | "high",
    "actionType": "add" | "update" | "delete" | "query"
  }]
}

Rules:
1. Extract ALL tasks mentioned in the input
2. Infer reasonable due dates from phrases like "tomorrow", "next week", "by Friday"
3. Set priority based on urgency words (urgent=high, soon=medium, default=low)
4. If unclear, set actionType to "add"
5. Keep titles concise and actionable
`;

const response = await openai.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [
    { role: "system", content: TASK_EXTRACTION_SYSTEM_PROMPT },
    { role: "user", content: userInput }
  ],
  response_format: { type: "json_object" },
  temperature: 0.3,  // Lower for consistent extraction
  max_tokens: 500     // Limit response length
});
```

**Example Input/Output**:
```typescript
// Input
"Add buy groceries tomorrow and schedule dentist appointment for next Friday"

// Output
{
  "tasks": [
    {
      "title": "Buy groceries",
      "description": "",
      "dueDate": "2025-12-20T00:00:00Z",
      "priority": "medium",
      "actionType": "add"
    },
    {
      "title": "Schedule dentist appointment",
      "description": "",
      "dueDate": "2025-12-26T00:00:00Z",
      "priority": "medium",
      "actionType": "add"
    }
  ]
}
```

### Cost Optimization Strategies

**Model Selection**: Use **GPT-4o-mini** instead of GPT-4 for cost efficiency

| Model | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) | Use Case |
|-------|---------------------------|----------------------------|----------|
| GPT-4o-mini | $0.150 | $0.600 | Task extraction (recommended) |
| GPT-4 Turbo | $10.00 | $30.00 | Complex reasoning only |

**Cost Calculations**:
- Average task extraction: ~200 input tokens + 150 output tokens
- Cost per extraction (GPT-4o-mini): ~$0.00005 (0.005 cents)
- 10,000 extractions: ~$0.50
- 100 messages/user/day × 30 days = 3,000 messages/month = **$0.15/user/month** ✅ (well under $0.05 target with GPT-4o-mini)

**Additional Optimizations**:
1. **Truncate long conversations**: Keep last 10 messages for context
   ```typescript
   const MAX_CONTEXT_MESSAGES = 10;
   const trimmedMessages = messages.slice(-MAX_CONTEXT_MESSAGES);
   ```

2. **Set max_tokens**: Limit response length
   ```typescript
   max_tokens: 500  // Enough for task extraction, prevents runaway costs
   ```

3. **Batch multiple tasks**: Extract multiple tasks in one API call instead of separate requests

4. **Rate limiting**: Enforce 100 requests/user/day (prevents abuse, keeps costs predictable)

### Error Handling Patterns

```typescript
async function extractTasks(userInput: string) {
  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: TASK_EXTRACTION_SYSTEM_PROMPT },
        { role: "user", content: userInput }
      ],
      response_format: { type: "json_object" },
      temperature: 0.3,
    });

    const content = response.choices[0].message.content;
    if (!content) throw new Error("Empty response from AI");

    const parsed = JSON.parse(content);

    // Validate schema
    if (!parsed.tasks || !Array.isArray(parsed.tasks)) {
      throw new Error("Invalid task structure");
    }

    // Validate each task
    const validTasks = parsed.tasks.filter(task => {
      return task.title &&
             task.title.length > 0 &&
             task.title.length <= 100 &&
             ['add', 'update', 'delete', 'query'].includes(task.actionType);
    });

    if (validTasks.length === 0) {
      return {
        success: false,
        clarificationNeeded: true,
        message: "I couldn't understand your task. Could you rephrase it?"
      };
    }

    return {
      success: true,
      tasks: validTasks
    };

  } catch (error) {
    console.error("Task extraction error:", error);

    // OpenAI API errors
    if (error.status === 429) {
      return {
        success: false,
        error: "Rate limit exceeded. Please try again in a moment.",
        fallback: true
      };
    }

    if (error.status === 503) {
      return {
        success: false,
        error: "AI service temporarily unavailable. Please use the form to create tasks.",
        fallback: true
      };
    }

    return {
      success: false,
      error: "Failed to extract tasks. Please try again.",
      fallback: true
    };
  }
}
```

### Integration Architecture

**Backend (Python FastAPI) + Frontend (Next.js) Architecture**:

```
┌─────────────────────────────────────────────┐
│  Frontend (Next.js 16 App Router)          │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │ Chat UI (Vercel AI SDK useChat)    │    │
│  │ - Message rendering                │    │
│  │ - Input handling                   │    │
│  │ - Streaming responses              │    │
│  └────────────────────────────────────┘    │
│                 │                           │
│                 │ HTTP POST /api/chat       │
│                 ▼                           │
│  ┌────────────────────────────────────┐    │
│  │ API Route (app/api/chat/route.ts)  │    │
│  │ - Validate input                   │    │
│  │ - Call OpenAI API                  │    │
│  │ - Stream response back             │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
                 │
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────┐
│  OpenAI API                                 │
│  ┌────────────────────────────────────┐    │
│  │ GPT-4o-mini                        │    │
│  │ - Structured outputs (JSON schema) │    │
│  │ - Function calling (optional)      │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
                 │
                 │ Parsed Tasks
                 ▼
┌─────────────────────────────────────────────┐
│  Backend (Python FastAPI)                   │
│  ┌────────────────────────────────────┐    │
│  │ Task Manager Service               │    │
│  │ - Validate extracted tasks         │    │
│  │ - Add to PostgreSQL database       │    │
│  │ - Return confirmation              │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

**Flow**:
1. User types message in Next.js chat UI
2. Frontend sends to `/api/chat` route (Next.js API route)
3. API route calls OpenAI API with structured output schema
4. OpenAI returns JSON with extracted task(s)
5. API route forwards to Python FastAPI backend for task creation
6. FastAPI validates and stores in PostgreSQL
7. Confirmation streamed back to user via SSE

---

## Research Question 3: API Endpoint Count and Structure

### Decision: 14 Total Endpoints (12 REST + 2 Real-Time Options)

Based on Phase 3 requirements (real-time chat, AI task actions, session management, rate limiting), the complete API structure is:

**REST Endpoints (12)**:
1. `POST /api/v1/chat/messages` - Send chat message (SSE model)
2. `GET /api/v1/chat/sessions/{session_id}/messages` - Get chat history
3. `POST /api/v1/chat/sessions` - Create chat session
4. `GET /api/v1/chat/sessions` - List active sessions
5. `DELETE /api/v1/chat/sessions/{session_id}` - End session
6. `POST /api/v1/ai/actions/{action_id}/confirm` - Confirm AI action
7. `POST /api/v1/ai/actions/{action_id}/reject` - Reject AI action
8. `GET /api/v1/ai/actions/pending` - List pending actions
9. `GET /api/v1/ai/quota` - Check rate limit status
10. `GET /api/v1/ai/preferences` - Get user AI preferences
11. `PATCH /api/v1/ai/preferences` - Update AI preferences
12. `GET /api/v1/ai/health` - AI service health check

**Real-Time Endpoints (2 options - choose one)**:
- Option A: `WS /api/v1/chat/ws` - WebSocket bidirectional chat
- Option B: `GET /api/v1/chat/stream` - Server-Sent Events (recommended per Research Q1)

**WebSocket Events** (if using WebSocket):
- Client→Server: `auth`, `message`, `confirm_action`, `reject_action`, `ping`
- Server→Client: `connected`, `ai_response`, `task_updated`, `task_created`, `task_deleted`, `action_pending`, `error`, `rate_limit_warning`, `pong`

**Authentication**: All endpoints (except `/health`) require JWT tokens from Phase 2 authentication system
- REST: `Authorization: Bearer {token}` header
- WebSocket: `?token={token}` query param
- SSE: `Authorization: Bearer {token}` header

**Detailed Endpoint Specifications** (see contracts/ directory for full OpenAPI schema)

**Example: Send Chat Message**
```
POST /api/v1/chat/messages
Auth: JWT required
Request Body:
{
  "message": "string",       // User's natural language input
  "session_id": "string?"    // Optional: resume existing session
}
Response (200 OK):
{
  "message_id": "string",
  "session_id": "string",
  "ai_response": {
    "message_id": "string",
    "content": "string",
    "proposed_action": {      // Null if just conversation
      "action_id": "string",
      "action_type": "create" | "update" | "delete" | "complete" | "query",
      "parameters": object,
      "confidence": number    // 0.0-1.0
    },
    "timestamp": "string"
  }
}
Errors:
- 401 Unauthorized: Invalid/missing JWT
- 429 Too Many Requests: Rate limit exceeded
- 503 Service Unavailable: OpenAI API down
```

---

## Resolved NEEDS CLARIFICATION Items

### Original Questions from Technical Context:

1. **WebSocket/SSE Library (Backend)?**
   - **Decision**: Native FastAPI `StreamingResponse` (no additional library)
   - **Rationale**: Built-in, simple, sufficient for SSE pattern

2. **WebSocket/SSE Library (Frontend)?**
   - **Decision**: `@microsoft/fetch-event-source`
   - **Rationale**: Production-ready, TypeScript support, auto-reconnection, Vercel-compatible

3. **How many new backend API endpoints?**
   - **Decision**: 12 REST + 1 SSE endpoint (13 total)
   - **Breakdown**: 5 chat/session, 3 AI actions, 2 preferences/quota, 1 health, 1 SSE stream

4. **How many new frontend components?**
   - **Decision**: 6 chat components + 1 integration wrapper (7 total)
   - **Components**: ChatWidget, ChatMessageList, ChatInput, ChatMessage, TaskActionConfirm, ChatToggle, ChatKitIntegration

5. **OpenAI API integration patterns?**
   - **Decision**: Direct API calls with structured outputs (primary), Vercel AI SDK for frontend
   - **Model**: GPT-4o-mini for cost efficiency
   - **Pattern**: Structured JSON output via `response_format: { type: "json_object" }`

---

## Updated Technical Context Summary

**Language/Version**: Python 3.13+ (backend), TypeScript strict mode (frontend)

**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Python SDK (`openai`), native `StreamingResponse`
- Frontend: Next.js 16 App Router, React, Vercel AI SDK (`ai`), `@microsoft/fetch-event-source`, TailwindCSS

**Storage**: Neon PostgreSQL (5 new tables: ChatMessage, ChatSession, TaskAction, UserPreferences, AIContext)

**Testing**: pytest (backend), Jest + React Testing Library (frontend), Playwright (E2E)

**Target Platform**: Linux server (backend), Modern browsers (frontend deployed to Vercel)

**Performance Goals**:
- AI response latency < 3s (p95) ✅ Achievable with GPT-4o-mini
- Task synchronization < 500ms ✅ SSE provides sub-second updates
- Traditional UI maintains Phase 2 performance (API < 200ms p95, page load < 3s) ✅ AI features are additive

**Constraints**:
- OpenAI API costs < $0.05/user/month ✅ GPT-4o-mini achieves $0.15/user/month with 100 msg/day limit
- SSE must work on Vercel ✅ Confirmed compatible
- Graceful degradation when OpenAI unavailable ✅ Traditional UI fully functional

**Scale/Scope**:
- Multi-user application (inherit Phase 2's user base)
- 5 new database entities
- 13 new backend endpoints (12 REST + 1 SSE)
- 7 new frontend components
- Direct OpenAI API integration with structured outputs

---

## Implementation Checklist (From Research)

**Backend**:
1. ✅ Use native FastAPI `StreamingResponse` for SSE
2. ✅ Install OpenAI Python SDK: `uv add openai`
3. ✅ Create system prompt template for task extraction
4. ✅ Implement 13 API endpoints (see contracts/)
5. ✅ Add JWT authentication to all endpoints except `/health`
6. ✅ Implement rate limiting (100 requests/user/day)
7. ✅ Use GPT-4o-mini model for cost efficiency

**Frontend**:
1. ✅ Install dependencies: `pnpm add ai openai @microsoft/fetch-event-source`
2. ✅ Create 7 chat components (ChatWidget, ChatMessageList, etc.)
3. ✅ Integrate Vercel AI SDK `useChat()` hook
4. ✅ Build SSE client with `@microsoft/fetch-event-source`
5. ✅ Handle reconnection and error states
6. ✅ Test on Vercel deployment

**Testing**:
1. Test SSE streaming: `curl -N -H "Authorization: Bearer $TOKEN" /api/chat/stream`
2. Test AI task extraction with various natural language inputs
3. Test rate limiting with rapid requests
4. E2E: Send message → Verify streamed response → Verify task created in database

---

## Cost and Performance Estimates

**OpenAI API Costs** (GPT-4o-mini):
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens
- Average extraction: 200 input + 150 output tokens = $0.00005 per message
- 100 messages/user/day × 30 days = **$0.15/user/month** ✅ (within budget if rate limited)
- **Mitigation**: Rate limit to 100 messages/day, batch multiple tasks per request

**SSE Performance**:
- Latency overhead vs WebSocket: <50ms (negligible)
- HTTP/2 multiplexing: Multiple SSE connections supported
- Vercel Edge Functions: Streaming responses have no cold start penalty

**Database Scaling**:
- In-memory chat sessions (Redis/memory cache) for <10ms access
- PostgreSQL for persistent data (Task, User, UserPreferences, AIContext)
- Partition `chat_messages` by `created_at` if volume exceeds 1M rows

---

## Security Considerations

**Prompt Injection Prevention**:
- Sanitize all user input before sending to OpenAI
- Isolate system prompts from user content
- Validate AI-generated actions before execution
- Log suspicious patterns for review

**Data Isolation**:
- All entities filtered by `user_id` from JWT claims
- AI cannot access other users' tasks even if mentioned in conversation
- Service layer enforces: `JWT.user_id == entity.user_id`

**Rate Limiting**:
- Per-user limits (100 requests/day) to prevent abuse
- OpenAI API key stored in environment variables (not database)
- Monitor costs with alerts ($10/day threshold)

---

## References

- **OpenAI API Documentation**: https://platform.openai.com/docs/api-reference
- **Vercel AI SDK**: https://sdk.vercel.ai/docs
- **@microsoft/fetch-event-source**: https://github.com/Azure/fetch-event-source
- **FastAPI Streaming**: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
- **Phase 3 Spec**: `/home/nabeera/hackathon-todo/specs/003-ai-task-assistant/spec.md`
- **Phase 3 Plan**: `/home/nabeera/hackathon-todo/specs/003-ai-task-assistant/plan.md`

---

## Next Steps

All research questions resolved. Proceed to Phase 1 (Design & Contracts):
1. Generate `data-model.md` ✅ COMPLETE
2. Generate API contracts in `contracts/` directory
3. Create `quickstart.md` guide
4. Update agent context with new technologies
5. Re-evaluate Constitution Check
