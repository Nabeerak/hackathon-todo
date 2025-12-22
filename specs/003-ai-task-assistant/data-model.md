# Data Model: AI-Powered Task Assistant

**Feature**: `003-ai-task-assistant`
**Date**: 2025-12-19
**Phase**: Phase 1 Design (from `/sp.plan`)

## Overview

Phase 3 extends the Phase 2 database schema with five new entities to support conversational AI task management. All entities maintain user-level isolation through `user_id` foreign keys and JWT authentication.

**Design Principle**: New entities are additive only - no modifications to existing Phase 2 tables (User, Task).

## Entity Relationship Diagram

```
User (Phase 2)
  ├─── Task (Phase 2) [1:Many]
  ├─── ChatSession (Phase 3) [1:Many]
  ├─── UserPreferences (Phase 3) [1:1]
  └─── AIContext (Phase 3) [1:1]

ChatSession (Phase 3)
  ├─── ChatMessage (Phase 3) [1:Many]
  └─── TaskAction (Phase 3) [1:Many]

ChatMessage (Phase 3)
  └─── TaskAction (Phase 3) [1:1 optional]

TaskAction (Phase 3)
  ├─── ChatMessage (Phase 3) [1:1]
  └─── Task (Phase 2) [Many:1 optional] (for query/update/delete actions)
```

## Entities

### 1. ChatMessage (New - Phase 3)

Represents a single message in the conversational AI interface.

**Attributes**:
- `id` (UUID, Primary Key): Unique message identifier
- `user_id` (UUID, Foreign Key → User): Owner of the message (for isolation)
- `session_id` (UUID, Foreign Key → ChatSession): Conversation session this message belongs to
- `content` (Text, Required): Message text (user input or AI response)
- `message_type` (Enum, Required): One of: `user_message`, `ai_response`, `system_notification`
- `created_at` (Timestamp, Auto): When message was created
- `metadata` (JSONB, Optional): Additional data (e.g., AI confidence score, token count)

**Relationships**:
- Belongs to one `ChatSession`
- Belongs to one `User` (for access control)
- May have one `TaskAction` (if message triggers/confirms an action)

**Indexes**:
- `(session_id, created_at)` - Fast retrieval of session history in chronological order
- `(user_id, created_at)` - User-level message queries

**Validation Rules**:
- `content` must not be empty
- `message_type` must be valid enum value
- `user_id` must match session's user_id (enforced at service layer)

**Storage Notes**:
- Messages stored in-memory during active session (24 hours)
- Older messages may be archived or deleted (retention policy TBD)
- Max 50 messages per session kept in active context

---

### 2. ChatSession (New - Phase 3)

Represents a conversation session between user and AI assistant.

**Attributes**:
- `id` (UUID, Primary Key): Unique session identifier
- `user_id` (UUID, Foreign Key → User): Session owner
- `started_at` (Timestamp, Auto): When session was created
- `last_activity_at` (Timestamp, Auto-update): Last message timestamp
- `is_active` (Boolean, Default: True): Whether session is still ongoing
- `context_summary` (Text, Optional): Compressed conversation context for long sessions
- `message_count` (Integer, Default: 0): Total messages in session

**Relationships**:
- Belongs to one `User`
- Has many `ChatMessage` (conversation history)
- Has many `TaskAction` (actions performed in this session)

**Indexes**:
- `(user_id, last_activity_at)` - Find user's recent sessions
- `(is_active, last_activity_at)` - Clean up stale sessions

**Validation Rules**:
- Session expires after 24 hours of inactivity (`last_activity_at` + 24h)
- Only one active session per user at a time (soft limit, not enforced)

**Lifecycle**:
1. Created when user sends first chat message (if no active session)
2. Updated on every new message (`last_activity_at` refreshed)
3. Marked inactive after 24 hours or explicit user close
4. Context summarized when message_count > 50 (to save memory)

---

### 3. TaskAction (New - Phase 3)

Represents an AI-interpreted action on a task, pending confirmation or executed.

**Attributes**:
- `id` (UUID, Primary Key): Unique action identifier
- `session_id` (UUID, Foreign Key → ChatSession): Session where action was proposed
- `message_id` (UUID, Foreign Key → ChatMessage): Message that triggered this action
- `user_id` (UUID, Foreign Key → User): Action owner (for isolation)
- `action_type` (Enum, Required): One of: `create`, `update`, `delete`, `complete`, `query`
- `extracted_params` (JSONB, Required): Structured parameters (e.g., `{title, description, due_date}`)
- `confidence_score` (Float, 0.0-1.0): AI's confidence in interpretation
- `confirmation_status` (Enum, Default: `pending`): One of: `pending`, `confirmed`, `rejected`
- `executed_status` (Enum, Default: `not_executed`): One of: `not_executed`, `executing`, `success`, `failed`
- `task_id` (UUID, Foreign Key → Task, Optional): Related task (for update/delete/complete/query)
- `error_message` (Text, Optional): Error details if execution failed
- `created_at` (Timestamp, Auto): When action was proposed
- `confirmed_at` (Timestamp, Optional): When user confirmed
- `executed_at` (Timestamp, Optional): When action was executed

**Relationships**:
- Belongs to one `ChatSession`
- Belongs to one `ChatMessage` (the AI response that proposed the action)
- Belongs to one `User` (for access control)
- May reference one `Task` (for update/delete/complete actions)

**Indexes**:
- `(user_id, created_at)` - User's action history
- `(session_id, confirmation_status)` - Find pending actions in session
- `(task_id)` - Find actions related to specific task

**Validation Rules**:
- `action_type` determines required fields in `extracted_params`:
  - `create`: requires `{title, description?}`
  - `update`: requires `{task_id, title?, description?}`
  - `delete`: requires `{task_id}`
  - `complete`: requires `{task_id, completed}`
  - `query`: requires `{filters?}` (e.g., `{completed: false}`)
- Cannot execute if `confirmation_status != confirmed` (except low-risk queries)
- `user_id` must match task's user_id for update/delete/complete

**Execution Flow**:
1. AI proposes action → `confirmation_status = pending`
2. User confirms → `confirmation_status = confirmed`, `executed_status = executing`
3. Backend executes → `executed_status = success` or `failed`
4. If failed, `error_message` populated

---

### 4. UserPreferences (New - Phase 3)

Stores AI personalization settings and learned user patterns.

**Attributes**:
- `id` (UUID, Primary Key): Unique preference record identifier
- `user_id` (UUID, Foreign Key → User, Unique): One preference record per user
- `preferred_language` (String, Default: "en"): AI response language
- `ai_tone` (Enum, Default: "professional"): One of: `professional`, `casual`, `concise`
- `enable_proactive_suggestions` (Boolean, Default: False): AI suggests actions without prompting
- `learned_shortcuts` (JSONB, Default: {}): User-specific shortcuts (e.g., `{"usual": {title: "Weekly review"}}`)
- `rate_limit_override` (Integer, Optional): Custom rate limit for premium users (requests/day)
- `ai_features_enabled` (Boolean, Default: True): Master toggle for all AI features
- `created_at` (Timestamp, Auto): When preferences created
- `updated_at` (Timestamp, Auto-update): Last preference change

**Relationships**:
- Belongs to one `User` (1:1 relationship)

**Indexes**:
- `(user_id)` - Unique index for fast lookup

**Validation Rules**:
- One record per user (enforced by unique constraint on `user_id`)
- `preferred_language` must be valid ISO 639-1 code (Phase 3: only "en")
- `rate_limit_override` must be positive integer if set

**Defaults**:
- Created on first AI interaction if doesn't exist
- Populated with system defaults

---

### 5. AIContext (New - Phase 3)

Maintains persistent context for AI interactions across sessions.

**Attributes**:
- `id` (UUID, Primary Key): Unique context record identifier
- `user_id` (UUID, Foreign Key → User, Unique): One context record per user
- `conversation_summary` (Text, Optional): Key information from past sessions
- `user_patterns` (JSONB, Default: {}): Observed patterns (e.g., `{frequent_tasks: ["meeting prep"], peak_hours: [9, 14]}`)
- `total_messages` (Integer, Default: 0): Lifetime message count
- `total_sessions` (Integer, Default: 0): Lifetime session count
- `average_session_length` (Float, Default: 0.0): Avg messages per session
- `last_updated_at` (Timestamp, Auto-update): Last context update
- `created_at` (Timestamp, Auto): When context created

**Relationships**:
- Belongs to one `User` (1:1 relationship)

**Indexes**:
- `(user_id)` - Unique index for fast lookup

**Validation Rules**:
- One record per user (enforced by unique constraint on `user_id`)
- Metrics updated asynchronously (not real-time)

**Update Strategy**:
- Created on first AI interaction
- Updated after each session ends (async job)
- `conversation_summary` regenerated when total_messages crosses thresholds (100, 500, 1000)
- `user_patterns` extracted via background ML/heuristic analysis

---

## Existing Entities (Phase 2 - No Changes)

### User (Phase 2 - Unchanged)

**Attributes**:
- `id`, `email`, `hashed_password`, `display_name`, `created_at`

**New Relationships**:
- Has many `ChatSession` (Phase 3)
- Has many `ChatMessage` (Phase 3)
- Has many `TaskAction` (Phase 3)
- Has one `UserPreferences` (Phase 3)
- Has one `AIContext` (Phase 3)

### Task (Phase 2 - Unchanged)

**Attributes**:
- `id`, `user_id`, `title`, `description`, `is_completed`, `created_at`, `updated_at`

**New Relationships**:
- Referenced by `TaskAction` (Phase 3) for update/delete/complete actions

---

## Database Migration Strategy

**Phase 3 Migration** (additive only):

1. Create new tables:
   - `chat_sessions`
   - `chat_messages`
   - `task_actions`
   - `user_preferences`
   - `ai_contexts`

2. Add foreign key constraints:
   - All `user_id` foreign keys → `users.id` (ON DELETE CASCADE)
   - `chat_messages.session_id` → `chat_sessions.id` (ON DELETE CASCADE)
   - `task_actions.session_id` → `chat_sessions.id` (ON DELETE SET NULL)
   - `task_actions.message_id` → `chat_messages.id` (ON DELETE SET NULL)
   - `task_actions.task_id` → `tasks.id` (ON DELETE SET NULL)

3. Create indexes (listed above for each entity)

4. Seed default records:
   - For existing users: create `user_preferences` and `ai_contexts` with defaults

5. No data migration needed (all Phase 2 data unchanged)

**Rollback Strategy**:
- Drop new tables in reverse order (no impact on Phase 2 data)
- Phase 2 app continues working unchanged

---

## Data Retention Policy

**ChatMessage**:
- Active sessions: Keep all messages in-memory (max 50 per session)
- Inactive sessions (>24h): Archive or delete (Phase 3: delete)
- Future: May persist for training/analytics (with user consent)

**ChatSession**:
- Keep metadata indefinitely (for analytics)
- Messages cleaned up per ChatMessage policy

**TaskAction**:
- Keep all executed actions for audit trail (30 days minimum)
- Pending/rejected actions cleaned up after 7 days

**UserPreferences & AIContext**:
- Persist indefinitely (user-specific settings)
- Deleted on user account deletion (CASCADE)

---

## Performance Considerations

**In-Memory Chat Sessions**:
- Active sessions stored in application memory (not database)
- Redis/memory cache for fast access (<10ms)
- Database writes async (eventual consistency acceptable)

**Query Optimization**:
- Composite indexes for common queries
- JSONB indexes for `extracted_params` and `user_patterns` if needed
- Partition `chat_messages` by `created_at` if volume grows large

**Scalability**:
- Horizontal scaling via user_id sharding (if needed)
- Session data partitioned by user for isolation
- Background jobs for context summarization and pattern extraction

---

## Security Notes

**User Isolation**:
- All entities have `user_id` for access control
- Service layer enforces: `JWT.user_id == entity.user_id`
- No cross-user data leakage via AI responses

**Data Sanitization**:
- All user input in `ChatMessage.content` sanitized before AI processing
- Prevent prompt injection via input validation and system prompt isolation

**Sensitive Data**:
- No plaintext passwords (inherited from Phase 2)
- OpenAI API key stored in environment variables (not database)
- Rate limits prevent abuse and cost overruns

---

## Summary

- **5 new entities**: ChatMessage, ChatSession, TaskAction, UserPreferences, AIContext
- **0 modified entities**: User and Task remain unchanged
- **Schema extension**: Additive only, maintains Phase 2 compatibility
- **Data isolation**: All entities filtered by `user_id` for multi-tenancy
- **Performance**: In-memory sessions, optimized indexes, async context updates
