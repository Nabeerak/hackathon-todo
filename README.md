# Full-Stack Todo Application

Phase 2 implementation of the hackathon todo application with multi-user authentication and persistent storage.

## Tech Stack

- **Backend**: Python 3.13+, FastAPI, SQLModel, Neon PostgreSQL
- **Frontend**: Next.js 16+, React 19+, TypeScript, Tailwind CSS 4+
- **Authentication**: Better Auth with JWT tokens
- **Package Management**: UV (backend), npm/pnpm (frontend)

## Project Structure

```
.
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── api/            # API route handlers
│   │   ├── auth/           # Authentication utilities
│   │   ├── db/             # Database configuration
│   │   ├── lib/            # Business logic libraries
│   │   ├── models.py       # SQLModel database models
│   │   ├── config.py       # Environment configuration
│   │   └── main.py         # FastAPI application entry
│   ├── pyproject.toml      # Python dependencies
│   └── README.md
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utility libraries
│   │   └── types/         # TypeScript type definitions
│   ├── package.json       # Node.js dependencies
│   ├── tsconfig.json      # TypeScript configuration
│   └── README.md
│
├── .env.example           # Environment variable template
└── README.md              # This file
```

## Setup Instructions

### Prerequisites

- Python 3.13+
- Node.js 18+
- UV package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Neon PostgreSQL account (or local PostgreSQL)

### Backend Setup

```bash
cd backend

# Install dependencies with UV
uv sync

# Copy environment variables
cp ../.env.example .env
# Edit .env and set your DATABASE_URL and JWT_SECRET_KEY

# Run database migrations
uv run python -m src.db.init_db

# Start the development server
uv run uvicorn src.main:app --reload --port 8000
```

Backend API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Copy environment variables (if needed)
# Edit any frontend-specific env vars

# Start the development server
npm run dev
# or
pnpm dev
```

Frontend will be available at `http://localhost:3000`

## Features

- **User Authentication**: Secure registration and login with JWT tokens
- **Task Management**: Create, read, update, delete, and complete tasks
- **Multi-User Isolation**: Each user sees only their own tasks
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Session Persistence**: Stay logged in for 7 days

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Sign in with credentials
- `POST /api/auth/signout` - Sign out (client-side token removal)

### Tasks
- `GET /api/{user_id}/tasks` - List all user's tasks
- `POST /api/{user_id}/tasks` - Create a new task
- `GET /api/{user_id}/tasks/{id}` - Get specific task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion status

## Development

This project follows spec-driven development using SpecKit Plus workflow:
1. `/sp.specify` - Create feature specification
2. `/sp.plan` - Generate implementation plan
3. `/sp.tasks` - Break down into executable tasks
4. `/sp.implement` - Execute implementation

See `specs/002-fullstack-web/` for detailed specifications and plans.

## Testing

```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

- **Frontend**: Deploy to Vercel (recommended)
- **Backend**: Deploy to any platform supporting Python ASGI (e.g., Railway, Render, Fly.io)
- **Database**: Use Neon serverless PostgreSQL

## License

MIT
