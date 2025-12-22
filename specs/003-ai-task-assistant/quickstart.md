# Quickstart Guide: AI-Powered Task Assistant

**Feature**: `003-ai-task-assistant`
**Date**: 2025-12-19
**Phase**: Phase 1 Design (from `/sp.plan`)

## Overview

This guide provides step-by-step instructions to set up and run the Phase 3 AI-powered task assistant locally. It assumes Phase 2 (full-stack web application) is already working.

**Prerequisites**:
- Phase 2 application fully functional (backend + frontend)
- OpenAI API key with GPT-4 access
- Node.js 18+, Python 3.13+, UV package manager
- Neon PostgreSQL database (from Phase 2)

**Estimated Setup Time**: 20-30 minutes

---

## Step 1: Environment Configuration

### 1.1 Update `.env` File

Add OpenAI API configuration to the existing `.env` file at the repo root:

```bash
# Existing Phase 2 variables
DATABASE_URL=postgresql://user:pass@neon.tech/db
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# NEW: Phase 3 AI Configuration
OPENAI_API_KEY=sk-proj-...your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3

# NEW: Rate Limiting
AI_RATE_LIMIT_PER_DAY=100
AI_RATE_LIMIT_PER_HOUR=20

# NEW: Feature Flags
AI_FEATURES_ENABLED=true
```

### 1.2 Get OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Create new secret key
3. Copy and paste into `.env` as `OPENAI_API_KEY`
4. **Important**: Add `.env` to `.gitignore` (should already be there from Phase 2)

---

## Step 2: Database Migration

### 2.1 Run Phase 3 Migration

Phase 3 adds 5 new tables to the existing database:

```bash
cd backend

# Review migration SQL (optional)
cat src/db/migrations/003_add_ai_tables.sql

# Run migration
uv run python -m src.db.init_db

# Expected output:
# ✓ Created table: chat_sessions
# ✓ Created table: chat_messages
# ✓ Created table: task_actions
# ✓ Created table: user_preferences
# ✓ Created table: ai_contexts
# Migration complete!
```

### 2.2 Verify Tables

```bash
# Connect to database
psql $DATABASE_URL

# List all tables
\dt

# Expected output should include:
#   users               (Phase 2)
#   tasks               (Phase 2)
#   chat_sessions       (Phase 3 - NEW)
#   chat_messages       (Phase 3 - NEW)
#   task_actions        (Phase 3 - NEW)
#   user_preferences    (Phase 3 - NEW)
#   ai_contexts         (Phase 3 - NEW)

\q  # Exit psql
```

---

## Step 3: Backend Setup

### 3.1 Install New Dependencies

```bash
cd backend

# Add OpenAI SDK
uv add openai

# Add SSE support (already included in FastAPI)
# No additional packages needed!

# Verify dependencies
uv pip list | grep openai
# Expected: openai  1.x.x
```

### 3.2 Start Backend Server

```bash
# From backend/ directory
uv run uvicorn src.main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
# INFO:     OpenAI API key loaded
# INFO:     AI features enabled
```

### 3.3 Test Backend Health

Open a new terminal:

```bash
curl http://localhost:8000/api/v1/ai/health

# Expected response:
# {
#   "status": "healthy",
#   "openai_api_status": "available",
#   "response_time_ms": 150,
#   "features": {
#     "chat": true,
#     "task_extraction": true,
#     "real_time_sync": true
#   },
#   "checked_at": "2025-12-19T10:30:00Z"
# }
```

---

## Step 4: Frontend Setup

### 4.1 Install New Dependencies

```bash
cd frontend

# Add AI SDK and SSE client
pnpm add ai openai @microsoft/fetch-event-source

# Verify installation
pnpm list | grep -E '(ai|openai|fetch-event-source)'
# Expected:
#   ai  3.x.x
#   openai  4.x.x
#   @microsoft/fetch-event-source  2.x.x
```

### 4.2 Start Frontend Server

```bash
# From frontend/ directory
pnpm run dev

# Expected output:
# ▲ Next.js 16.x.x
# - Local:        http://localhost:3000
# - Environments: .env.local
#
# ✓ Ready in 2.5s
```

### 4.3 Verify Frontend

1. Open http://localhost:3000
2. Sign in with existing Phase 2 account (or create new one)
3. Navigate to `/tasks`
4. **Look for**: New chat widget in bottom-right corner (collapsed by default)

---

## Step 5: Test AI Features

### 5.1 Basic Chat Test

1. Click chat widget to expand
2. Type: **"Add buy groceries tomorrow"**
3. Press Enter

**Expected Behavior**:
- AI responds: "I'll create that task for you. Task: Buy groceries, Due: [tomorrow's date]. Proceed?"
- Confirmation dialog appears
- Click "Confirm"
- Task appears in task list with due date set

### 5.2 Multi-Task Test

1. In chat: **"Add call dentist by Friday and schedule team meeting next Monday at 2pm"**
2. AI should propose 2 actions
3. Confirm both
4. Verify 2 new tasks in list

### 5.3 Query Test

1. In chat: **"What tasks are due this week?"**
2. AI should list pending tasks with due dates in current week
3. No confirmation needed (read-only query)

### 5.4 Update Test

1. In chat: **"Change the dentist task to 'Schedule annual dental checkup'"**
2. AI proposes update action
3. Confirm
4. Verify task title updated in list

### 5.5 Complete Test

1. In chat: **"Mark groceries as done"**
2. AI proposes completion action
3. Confirm
4. Verify task marked complete (strikethrough in UI)

### 5.6 Graceful Degradation Test

1. Stop backend server (Ctrl+C)
2. Refresh frontend
3. Try to send chat message
4. **Expected**: Error message: "AI service temporarily unavailable. Please use the traditional form to create tasks."
5. Verify traditional task form still works
6. Restart backend

---

## Step 6: Verify Real-Time Sync

### 6.1 Test UI → Chat Sync

1. Expand chat widget
2. Use traditional form to create task: "Test task from form"
3. **Expected**: Chat displays notification: "I see you created 'Test task from form' using the form."

### 6.2 Test Chat → UI Sync

1. In chat: "Add another test task"
2. Confirm action
3. **Expected**: Task appears in list WITHOUT page refresh (real-time update via SSE)

---

## Step 7: Verify Rate Limiting

### 7.1 Check Quota

```bash
# Get JWT token from browser localStorage (F12 → Console → localStorage.getItem('jwt_token'))
TOKEN="your-jwt-token-here"

curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/ai/quota

# Expected response:
# {
#   "user_id": "...",
#   "period": "day",
#   "limit": 100,
#   "remaining": 97,
#   "resets_at": "2025-12-20T00:00:00Z",
#   "cost_to_date": 0.003
# }
```

### 7.2 Test Rate Limit Enforcement

1. Send 100 chat messages rapidly (use browser console loop):
   ```javascript
   for (let i = 0; i < 100; i++) {
     await chatClient.sendMessage(`Test message ${i}`);
   }
   ```

2. Send 101st message
3. **Expected**: Error: "Rate limit exceeded. You have reached your daily limit of 100 AI requests. Resets at [timestamp]."

---

## Step 8: API Documentation

### 8.1 View OpenAPI Docs

Visit http://localhost:8000/docs (FastAPI auto-generated)

**Expected sections**:
- **Chat**: `/api/v1/chat/messages`, `/api/v1/chat/stream`, `/api/v1/chat/sessions`
- **AI Actions**: `/api/v1/ai/actions/{id}/confirm`, `/api/v1/ai/actions/{id}/reject`
- **Preferences**: `/api/v1/ai/preferences`
- **Quota**: `/api/v1/ai/quota`
- **Health**: `/api/v1/ai/health`

### 8.2 Test via Swagger UI

1. Click "Authorize" button (top-right)
2. Paste JWT token
3. Click "Authorize" again
4. Try `POST /api/v1/chat/messages`:
   - Request body: `{"message": "Add test task"}`
   - Click "Execute"
   - Verify 200 response with AI reply

---

## Troubleshooting

This section covers common errors when setting up and using the AI-powered task assistant.

### Common Error 1: "OpenAI API key invalid"

**Symptoms:**
- Chat messages fail with 401 error
- Backend logs show "OpenAI API authentication failed"
- AI health check endpoint returns `"openai_api_status": "unavailable"`

**Root Causes:**
1. API key not set in `.env` file
2. API key format incorrect (should start with `sk-proj-` or `sk-`)
3. API key expired or revoked
4. API key lacks necessary permissions

**How to Fix:**

```bash
# Step 1: Verify .env file has OPENAI_API_KEY
cat .env | grep OPENAI_API_KEY

# Step 2: Test the key directly with OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"

# Expected: 200 response with list of models
# If 401: Key is invalid, get a new one from https://platform.openai.com/api-keys

# Step 3: Get a new API key
# 1. Visit https://platform.openai.com/api-keys
# 2. Click "Create new secret key"
# 3. Copy the key (starts with sk-proj- or sk-)
# 4. Update .env file:
echo "OPENAI_API_KEY=sk-proj-your-new-key-here" >> .env

# Step 4: Restart the backend
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

**Verification:**
```bash
# Check AI health endpoint
curl http://localhost:8000/api/v1/ai/health

# Expected response:
# {
#   "status": "healthy",
#   "openai_api_status": "available",
#   ...
# }
```

**Related Links:**
- Health check endpoint: `GET /api/v1/ai/health`
- OpenAI API keys dashboard: https://platform.openai.com/api-keys
- OpenAI status page: https://status.openai.com

---

### Common Error 2: "Rate limit exceeded"

**Symptoms:**
- Error message: "Rate limit exceeded. You have reached your daily limit of 100 AI requests."
- HTTP 429 status code
- Chat widget shows quota warning

**Root Causes:**
1. User exceeded daily quota (default: 100 requests/day)
2. User exceeded hourly quota (default: 20 requests/hour)
3. OpenAI API rate limits (separate from app limits)

**Explanation:**
The application enforces two levels of rate limiting:
- **Application-level**: Prevents API cost abuse (configurable via `.env`)
- **OpenAI-level**: OpenAI's own rate limits based on your account tier

**Resolution:**

**For Development (Increase Limit):**
```bash
# Option 1: Increase global limit in .env (affects all users)
echo "AI_RATE_LIMIT_PER_DAY=1000" >> .env
echo "AI_RATE_LIMIT_PER_HOUR=100" >> .env

# Restart backend
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

**For Production (Per-User Override):**
```bash
# Option 2: Override limit for specific user (database update)
# First, get user ID from JWT token or database
psql $DATABASE_URL -c "SELECT id, email FROM users;"

# Then set custom limit for that user
psql $DATABASE_URL -c "UPDATE user_preferences SET rate_limit_override=500 WHERE user_id='USER_ID_HERE';"
```

**Check Current Quota:**
```bash
# Get JWT token from browser localStorage (F12 → Console)
# localStorage.getItem('jwt_token')
TOKEN="your-jwt-token-here"

curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/ai/quota

# Response shows remaining requests and reset time
```

**OpenAI Rate Limits:**
If you're hitting OpenAI's limits (not application limits):
1. Check your OpenAI account tier: https://platform.openai.com/account/limits
2. Upgrade to higher tier for increased limits
3. Implement request batching in code (future enhancement)

**Related Links:**
- Quota check endpoint: `GET /api/v1/ai/quota`
- OpenAI rate limits documentation: https://platform.openai.com/docs/guides/rate-limits

---

### Common Error 3: "SSE connection fails"

**Symptoms:**
- Tasks created in traditional UI don't appear in chat
- Tasks created in chat don't update UI without refresh
- Browser console shows "EventSource failed"
- Network tab shows `/api/v1/chat/stream` connection closes immediately

**Root Causes:**
1. CORS misconfiguration (backend doesn't allow frontend origin)
2. JWT token invalid or expired
3. Browser or network blocks SSE connections
4. Backend SSE endpoint not running

**Debugging Steps:**

**Step 1: Check SSE Connection in Browser**
```javascript
// Open browser console (F12 → Console)
// Check for active EventSource connection
// Go to Network tab → Filter: "stream" or "eventsource"
// Should see persistent connection to /api/v1/chat/stream
```

**Step 2: Test SSE Endpoint Directly**
```bash
# Get JWT token from browser localStorage
TOKEN="your-jwt-token-here"

# Test SSE connection with curl
curl -N \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: text/event-stream" \
  http://localhost:8000/api/v1/chat/stream

# Expected: Connection stays open, receives events when tasks change
# If 401: Token invalid, login again
# If 403: CORS issue, check backend ALLOWED_ORIGINS
# If 404: Endpoint not implemented, check backend version
```

**Step 3: Verify CORS Configuration**
```bash
# Check .env file for ALLOWED_ORIGINS
cat .env | grep ALLOWED_ORIGINS

# Should include frontend URL:
# ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# If missing, add it:
echo "ALLOWED_ORIGINS=http://localhost:3000" >> .env

# Restart backend
```

**Step 4: Check JWT Token**
```javascript
// In browser console (F12 → Console)
const token = localStorage.getItem('jwt_token');
console.log('Token:', token);

// If null or expired, login again
// Go to /login page and sign in
```

**Step 5: Disable Browser Extensions**
Some ad-blockers and privacy extensions block SSE connections:
1. Temporarily disable ad-blocker (uBlock Origin, AdBlock Plus)
2. Try in incognito/private mode
3. Whitelist `localhost:8000` in extension settings

**Verification:**
```bash
# After fixes, test real-time sync:
# 1. Open chat widget
# 2. Create task via traditional form
# 3. Chat should show: "I see you created 'Task Name' using the form"
# 4. If message appears, SSE is working
```

**Related Links:**
- SSE endpoint: `GET /api/v1/chat/stream`
- CORS configuration: See `backend/src/config.py`

---

### Common Error 4: "AI features unavailable"

**Symptoms:**
- Chat widget shows "AI features are currently disabled"
- All AI endpoints return 503 error
- Health check shows `"features": { "chat": false }`

**Root Causes:**
1. `AI_FEATURES_ENABLED=false` in `.env` file
2. OpenAI API key not configured
3. Backend AI services failed to initialize

**How to Fix:**

**Step 1: Check Feature Flag**
```bash
# Verify AI_FEATURES_ENABLED is true
cat .env | grep AI_FEATURES_ENABLED

# If false or missing, enable it:
echo "AI_FEATURES_ENABLED=true" >> .env
```

**Step 2: Verify OpenAI Configuration**
```bash
# Check all required AI environment variables
cat .env | grep -E '(OPENAI|AI_)'

# Required variables:
# OPENAI_API_KEY=sk-proj-...
# OPENAI_MODEL=gpt-4o-mini
# AI_FEATURES_ENABLED=true

# If any are missing, add them from .env.example:
cp .env.example .env
# Edit .env and fill in your OpenAI API key
```

**Step 3: Test AI Health**
```bash
# Check AI health endpoint
curl http://localhost:8000/api/v1/ai/health

# Expected response when working:
# {
#   "status": "healthy",
#   "openai_api_status": "available",
#   "features": {
#     "chat": true,
#     "task_extraction": true,
#     "real_time_sync": true
#   }
# }

# If "status": "unhealthy", check backend logs:
tail -f backend/logs/app.log | grep "AI"
```

**Step 4: Restart Backend**
```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000

# Watch startup logs for AI initialization:
# INFO: OpenAI API key loaded
# INFO: AI features enabled
# INFO: AI services initialized successfully
```

**Graceful Degradation:**
When AI features are unavailable, the application should:
- Display clear error message in chat widget
- Allow users to continue using traditional task forms
- Show "AI temporarily unavailable" banner

**Related Links:**
- Health check endpoint: `GET /api/v1/ai/health`
- Feature flag configuration: See `.env.example`
- Backend logs: `backend/logs/app.log`

---

### Additional Troubleshooting Tips

**Issue: "OpenAI API key not found"**

**Solution**:
```bash
# Verify .env file has OPENAI_API_KEY
cat .env | grep OPENAI_API_KEY

# If missing, add it:
echo "OPENAI_API_KEY=sk-proj-your-key-here" >> .env

# Restart backend
```

---

**Issue: "AI service unavailable" (503 error)**

**Causes**:
1. OpenAI API key invalid/expired
2. OpenAI API down (check https://status.openai.com)
3. Network connectivity issue

**Solution**:
```bash
# Test OpenAI API directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# If 401: Key invalid, get new one
# If timeout: Network issue, check firewall/proxy
# If 200: Backend integration issue, check logs
```

---

**Issue: Chat widget not appearing**

**Solution**:
```bash
# Verify frontend dependencies
cd frontend
pnpm list | grep -E '(ai|openai|fetch-event-source)'

# If missing, reinstall:
pnpm add ai openai @microsoft/fetch-event-source

# Clear Next.js cache
rm -rf .next
pnpm run dev
```

---

**Issue: Tasks not syncing in real-time**

**Solution**:
```bash
# Check SSE connection in browser console (F12 → Network → filter: stream)
# Should see active EventSource connection to /api/v1/chat/stream

# If connection fails:
# 1. Check CORS headers in backend (should allow frontend origin)
# 2. Verify JWT token valid
# 3. Check browser blocks SSE (some ad-blockers do)
```

---

### Getting More Help

If you're still experiencing issues after trying these solutions:

1. **Check Backend Logs:**
   ```bash
   tail -f backend/logs/app.log | grep -E "(ERROR|AI|OpenAI)"
   ```

2. **Check Frontend Console:**
   - Open browser DevTools (F12)
   - Look for errors in Console tab
   - Check Network tab for failed requests

3. **Verify Database State:**
   ```bash
   psql $DATABASE_URL
   \dt  # List tables (should include chat_sessions, chat_messages, etc.)
   SELECT * FROM user_preferences LIMIT 1;  # Check AI preferences initialized
   ```

4. **Review Documentation:**
   - Backend setup: `../../backend/README.md`
   - API contracts: `contracts/openapi-ai-endpoints.yaml`
   - Phase 3 spec: `spec.md`

5. **Check OpenAI Status:**
   - API status: https://status.openai.com
   - Usage dashboard: https://platform.openai.com/usage
   - Rate limits: https://platform.openai.com/account/limits

---

## Development Workflow

### Running Tests

**Backend**:
```bash
cd backend
uv run pytest tests/unit/test_nlp_service.py -v
uv run pytest tests/integration/test_chat_workflows.py -v
uv run pytest tests/contract/test_ai_api_contract.py -v
```

**Frontend**:
```bash
cd frontend
pnpm test                              # Unit tests
pnpm test:e2e                          # Playwright E2E
pnpm test tests/components/chat/ -v   # Chat component tests
```

### Debugging

**Backend logs**:
```bash
# Tail backend logs
tail -f backend/logs/app.log

# Filter for AI-related logs
tail -f backend/logs/app.log | grep "AI"
```

**Frontend logs**:
```bash
# Browser console (F12)
# Look for [ChatClient], [AI], [SSE] prefixes

# Enable debug mode
localStorage.setItem('debug', 'chat:*');
# Refresh page
```

### Hot Reload

- **Backend**: Uvicorn auto-reloads on file changes (if `--reload` flag used)
- **Frontend**: Next.js auto-reloads on file changes (dev server)

---

## Next Steps

After quickstart works:

1. **Customize AI Prompts**: Edit `backend/src/services/ai/prompt_templates.py`
2. **Add New AI Capabilities**: Extend task extraction to handle priorities, tags, attachments
3. **Improve UI**: Customize chat widget styling in `frontend/src/components/chat/ChatWidget.tsx`
4. **Monitor Costs**: Set up OpenAI API usage alerts at https://platform.openai.com/account/billing/limits
5. **Deploy**: Follow deployment guides:
   - Frontend: `frontend/README.md` (Vercel deployment)
   - Backend: `backend/README.md` (Railway/Render deployment)

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Set `AI_FEATURES_ENABLED=true` in production `.env`
- [ ] Use production OpenAI API key (not development key)
- [ ] Enable rate limiting (100 requests/user/day)
- [ ] Set up monitoring for OpenAI API costs
- [ ] Configure CORS for production frontend URL
- [ ] Enable HTTPS for all API endpoints
- [ ] Set up database backups (chat history, preferences)
- [ ] Test graceful degradation (OpenAI API outage)
- [ ] Review logs for prompt injection attempts
- [ ] Set up alerts for 429 errors (rate limiting)

---

## Resources

- **Phase 3 Spec**: `spec.md` - Full requirements and user stories
- **Phase 3 Plan**: `plan.md` - Architecture and design decisions
- **Data Model**: `data-model.md` - Database schema and entities
- **API Contracts**: `contracts/openapi-ai-endpoints.yaml` - API specifications
- **Research**: `research.md` - Technology decisions and best practices
- **Backend README**: `../../backend/README.md` - Phase 2 backend setup
- **Frontend README**: `../../frontend/README.md` - Phase 2 frontend setup

---

## Support

**Issues**:
- Backend errors: Check `backend/logs/app.log`
- Frontend errors: Check browser console (F12)
- Database issues: Check Neon dashboard

**Cost Monitoring**:
- OpenAI usage: https://platform.openai.com/usage
- Estimated cost: ~$0.15/user/month (100 messages/day with GPT-4o-mini)

**Getting Help**:
- Review `research.md` for implementation patterns
- Check `data-model.md` for entity relationships
- Refer to `contracts/README.md` for API usage examples

---

**Status**: Phase 3 quickstart guide complete. Ready for implementation via `/sp.tasks`.
