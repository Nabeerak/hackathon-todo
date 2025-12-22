# Todo Backend API

FastAPI backend for the full-stack todo application with JWT authentication and PostgreSQL storage.

## Features

- **JWT Authentication**: Secure user authentication with 7-day token expiry
- **RESTful API**: Full CRUD operations for tasks
- **Multi-User Support**: Complete data isolation between users
- **AI-Powered Task Assistant** (Phase 3): Natural language task creation and management
- **Real-Time Updates**: Server-Sent Events (SSE) for live task synchronization
- **AI Personalization**: Learn user patterns and preferences over time
- **Rate Limiting**: Prevent API cost overruns (100 requests/user/day default)
- **SQLModel ORM**: Type-safe database operations
- **Input Validation**: Pydantic models for request/response validation
- **Connection Pooling**: Efficient database connection management

## Tech Stack

- Python 3.13+
- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- PostgreSQL (Neon Serverless or local)
- python-jose (JWT)
- passlib (password hashing with bcrypt)
- OpenAI Python SDK (GPT-4o-mini for AI features)
- UV package manager

## Setup

### Prerequisites

- Python 3.13+
- UV package manager
- PostgreSQL database (Neon or local)

### Installation

```bash
# Install dependencies
uv sync

# Copy environment variables
cp ../.env.example ../.env
# Edit ../.env with your DATABASE_URL and JWT_SECRET_KEY
```

### Environment Variables

Create a `.env` file at the repository root with:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# JWT
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7

# URLs & CORS
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000
ENVIRONMENT=development

# Phase 3: AI Configuration (REQUIRED for AI features)
OPENAI_API_KEY=sk-proj-your-openai-key-here  # Get from https://platform.openai.com/api-keys
OPENAI_MODEL=gpt-4o-mini  # Cost-effective model (~$0.15/1M input tokens)
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3
AI_RATE_LIMIT_PER_DAY=100  # Prevent cost overruns
AI_RATE_LIMIT_PER_HOUR=20
AI_FEATURES_ENABLED=true  # Master toggle for AI functionality
```

### Database Initialization

```bash
# Create tables
uv run python -m src.db.init_db
```

## Running

```bash
# Development server with auto-reload
uv run uvicorn src.main:app --reload --port 8000

# Production
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

#### POST `/api/auth/signup`
Register a new user.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure123",
  "display_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "display_name": "John Doe",
    "created_at": "2025-12-16T10:30:00"
  }
}
```

**Errors**:
- 409 Conflict: Email already registered
- 422 Validation Error: Invalid email or password too short

---

#### POST `/api/auth/signin`
Sign in an existing user.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "display_name": "John Doe",
    "created_at": "2025-12-16T10:30:00"
  }
}
```

**Errors**:
- 401 Unauthorized: Invalid email or password

---

#### POST `/api/auth/signout`
Sign out (client-side token clearing).

**Response** (200 OK):
```json
{
  "message": "Signed out successfully"
}
```

---

### Tasks

All task endpoints require JWT authentication via `Authorization: Bearer <token>` header.

#### GET `/api/{user_id}/tasks`
List all tasks for authenticated user with pagination.

**Query Parameters**:
- `skip` (optional, default: 0): Number of tasks to skip
- `limit` (optional, default: 100, max: 1000): Maximum tasks to return

**Example**: `GET /api/1/tasks?skip=0&limit=10`

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "is_completed": false,
    "created_at": "2025-12-16T10:30:00",
    "updated_at": "2025-12-16T10:30:00"
  },
  {
    "id": 2,
    "user_id": 1,
    "title": "Finish report",
    "description": null,
    "is_completed": true,
    "created_at": "2025-12-15T14:20:00",
    "updated_at": "2025-12-16T09:00:00"
  }
]
```

**Errors**:
- 403 Forbidden: user_id doesn't match authenticated user

---

#### POST `/api/{user_id}/tasks`
Create a new task.

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, bread, eggs"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "is_completed": false,
  "created_at": "2025-12-16T10:30:00",
  "updated_at": "2025-12-16T10:30:00"
}
```

**Validations**:
- Title: required, 1-200 characters
- Description: optional, max 1000 characters
- Input is HTML-escaped for XSS protection

**Errors**:
- 403 Forbidden: user_id doesn't match authenticated user
- 422 Validation Error: Invalid input

---

#### GET `/api/{user_id}/tasks/{task_id}`
Get a specific task by ID.

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "is_completed": false,
  "created_at": "2025-12-16T10:30:00",
  "updated_at": "2025-12-16T10:30:00"
}
```

**Errors**:
- 404 Not Found: Task doesn't exist or doesn't belong to user

---

#### PUT `/api/{user_id}/tasks/{task_id}`
Update a task's title and/or description.

**Request Body**:
```json
{
  "title": "Buy groceries and supplies",
  "description": "Milk, bread, eggs, paper towels"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Buy groceries and supplies",
  "description": "Milk, bread, eggs, paper towels",
  "is_completed": false,
  "created_at": "2025-12-16T10:30:00",
  "updated_at": "2025-12-16T11:45:00"
}
```

**Errors**:
- 404 Not Found: Task doesn't exist or doesn't belong to user

---

#### PATCH `/api/{user_id}/tasks/{task_id}/complete`
Toggle task completion status.

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "is_completed": true,
  "created_at": "2025-12-16T10:30:00",
  "updated_at": "2025-12-16T12:00:00"
}
```

---

#### DELETE `/api/{user_id}/tasks/{task_id}`
Delete a task.

**Response**: 204 No Content

**Errors**:
- 404 Not Found: Task doesn't exist or doesn't belong to user

---

### AI Endpoints (Phase 3)

#### POST `/api/v1/chat/messages`
Send natural language message to AI assistant.

**Request**:
```json
{
  "content": "Add buy groceries tomorrow at 3pm"
}
```

**Response**: Returns AI response with proposed task action.

#### GET `/api/v1/chat/stream`
Server-Sent Events (SSE) endpoint for real-time task updates.

#### POST `/api/v1/ai/actions/{id}/confirm`
Confirm AI-proposed task action.

#### POST `/api/v1/ai/actions/{id}/reject`
Reject AI-proposed task action.

#### GET `/api/v1/ai/preferences`
Get user AI preferences (tone, language, proactive suggestions).

#### PATCH `/api/v1/ai/preferences`
Update user AI preferences.

#### GET `/api/v1/ai/quota`
Get AI usage quota (remaining requests, resets_at).

#### GET `/api/v1/ai/health`
Check OpenAI API connectivity and service health.

For complete AI API documentation, see: http://localhost:8000/docs after running the server.

---

## Authentication

All task endpoints require JWT authentication via `Authorization: Bearer <token>` header.

The backend validates:
1. Token is valid and not expired
2. `user_id` in URL matches the authenticated user from token
3. Returns `401 Unauthorized` for invalid tokens
4. Returns `403 Forbidden` for user_id mismatch

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── models.py            # SQLModel database models
│   ├── api/
│   │   ├── auth.py          # Authentication endpoints
│   │   └── tasks.py         # Task CRUD endpoints
│   ├── auth/
│   │   ├── jwt.py           # JWT utilities
│   │   └── middleware.py    # Auth middleware
│   └── db/
│       ├── connection.py    # Database connection
│       └── init_db.py       # DB initialization script
├── pyproject.toml           # Dependencies
└── README.md                # This file
```

## Security

- Passwords are hashed with bcrypt (never stored in plaintext)
- JWT tokens use HS256 algorithm
- All user input is validated with Pydantic
- Database queries use parameterized statements (SQL injection protection)
- CORS configured to allow only specified origins
- User data is isolated (queries filter by user_id)

## Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src
```

## Deployment

### Environment Variables

Ensure all environment variables are set in production:
- `DATABASE_URL`: Your production PostgreSQL connection string
- `JWT_SECRET_KEY`: Strong random secret (generate with `openssl rand -hex 32`)
- `ALLOWED_ORIGINS`: Your frontend URL(s)
- `ENVIRONMENT`: Set to `production`

### Platforms

Compatible with:
- Railway
- Render
- Fly.io
- Heroku
- Any platform supporting Python ASGI apps

### Example: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

## License

MIT
