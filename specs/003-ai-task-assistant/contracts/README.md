# API Contracts - Phase 3 AI Task Assistant

**Feature**: `003-ai-task-assistant`
**Date**: 2025-12-19

## Overview

This directory contains API contract specifications for Phase 3 AI-powered task assistant endpoints. All contracts are defined using OpenAPI 3.1.0 specification.

## Files

- **`openapi-ai-endpoints.yaml`**: Complete OpenAPI specification for all 12 REST endpoints + SSE stream
  - Chat endpoints (message send/receive, session management)
  - AI action confirmation/rejection
  - Rate limiting and quota
  - User preferences
  - Health check

## Contract Summary

### Authentication

All endpoints (except `/health`) require JWT Bearer token from Phase 2 authentication system:

```http
Authorization: Bearer <jwt_token>
```

### Endpoint Count

- **12 REST endpoints**: Chat, sessions, actions, preferences, quota, health
- **1 SSE endpoint**: Real-time AI response streaming
- **Total**: 13 endpoints

### Base URL

- Local development: `http://localhost:8000`
- Production: `https://api.example.com` (TBD)

### API Versioning

All endpoints prefixed with `/api/v1` for future compatibility.

## Using the Contracts

### Viewing in Swagger UI

```bash
# Install swagger-ui (if not already installed)
npm install -g swagger-ui-watcher

# Serve the OpenAPI spec
swagger-ui-watcher openapi-ai-endpoints.yaml
```

Open http://localhost:8000 to view interactive API documentation.

### Code Generation

**Backend (Python/FastAPI)**:
```bash
# Generate FastAPI stubs
openapi-generator generate \
  -i openapi-ai-endpoints.yaml \
  -g python-fastapi \
  -o ../../../backend/src/api/generated
```

**Frontend (TypeScript)**:
```bash
# Generate TypeScript API client
openapi-generator generate \
  -i openapi-ai-endpoints.yaml \
  -g typescript-fetch \
  -o ../../../frontend/src/lib/api/generated
```

### Contract Testing

Contract tests validate that implementations match the OpenAPI specification.

**Backend** (pytest):
```python
# backend/tests/contract/test_ai_api_contract.py
from schemathesis import from_uri

schema = from_uri("specs/003-ai-task-assistant/contracts/openapi-ai-endpoints.yaml")

@schema.parametrize()
def test_api_contract(case):
    response = case.call_asgi(app)
    case.validate_response(response)
```

**Frontend** (Jest):
```typescript
// frontend/tests/contract/api-contract.test.ts
import { validateAgainstSchema } from 'openapi-validator';
import spec from '@/specs/003-ai-task-assistant/contracts/openapi-ai-endpoints.yaml';

describe('AI API Contract', () => {
  it('should match OpenAPI schema', async () => {
    const response = await chatClient.sendMessage("test");
    expect(validateAgainstSchema(response, spec, '/api/v1/chat/messages')).toBe(true);
  });
});
```

## Key Endpoints

### Chat

- `POST /api/v1/chat/messages` - Send user message, receive AI response
- `GET /api/v1/chat/stream` - SSE stream for real-time responses
- `GET /api/v1/chat/sessions/{session_id}/messages` - Retrieve chat history

### Sessions

- `POST /api/v1/chat/sessions` - Create new session
- `GET /api/v1/chat/sessions` - List active sessions
- `DELETE /api/v1/chat/sessions/{session_id}` - End session

### AI Actions

- `POST /api/v1/ai/actions/{action_id}/confirm` - Confirm AI-proposed task action
- `POST /api/v1/ai/actions/{action_id}/reject` - Reject AI-proposed action
- `GET /api/v1/ai/actions/pending` - List pending actions awaiting confirmation

### Quota & Preferences

- `GET /api/v1/ai/quota` - Check remaining AI requests (rate limiting)
- `GET /api/v1/ai/preferences` - Get user AI settings
- `PATCH /api/v1/ai/preferences` - Update user AI settings

### Health

- `GET /api/v1/ai/health` - Check AI service availability

## Error Handling

All endpoints return consistent error format:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Human-readable error message",
    "details": {},
    "timestamp": "2025-12-19T10:30:00Z"
  }
}
```

**Standard Error Codes**:
- `UNAUTHORIZED` (401): Invalid/missing JWT
- `FORBIDDEN` (403): Access denied (wrong user)
- `NOT_FOUND` (404): Resource doesn't exist
- `BAD_REQUEST` (400): Invalid parameters
- `RATE_LIMIT_EXCEEDED` (429): Quota exceeded
- `SERVICE_UNAVAILABLE` (503): OpenAI API down

## Security

1. **Authentication**: All endpoints (except `/health`) require JWT Bearer token
2. **User Isolation**: All operations filtered by `user_id` from JWT claims
3. **Rate Limiting**: 100 requests/user/day enforced at `/quota` endpoint
4. **Input Validation**: All request bodies validated against JSON schemas
5. **CORS**: Configured for frontend origin only (Vercel deployment)

## Testing Checklist

Before implementation, ensure:

- [ ] All endpoint paths match specification
- [ ] All required fields in request/response bodies present
- [ ] HTTP status codes match specification
- [ ] Error responses follow standard format
- [ ] JWT authentication required on all protected endpoints
- [ ] Rate limiting enforced (100 requests/user/day)
- [ ] OpenAI API failure returns 503 with fallback message
- [ ] SSE stream uses `text/event-stream` content type
- [ ] All timestamps in ISO 8601 format
- [ ] UUIDs validated as RFC 4122 format

## References

- **OpenAPI Specification**: https://spec.openapis.org/oas/v3.1.0
- **Phase 3 Spec**: `../spec.md`
- **Phase 3 Plan**: `../plan.md`
- **Data Model**: `../data-model.md`
- **Research Findings**: `../research.md`

## Changelog

- **2025-12-19**: Initial contract creation for Phase 3 (v3.0.0)
  - 12 REST endpoints + 1 SSE endpoint
  - JWT authentication
  - Rate limiting support
  - OpenAI integration patterns
