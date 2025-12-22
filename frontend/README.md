This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Overview

This is the frontend application for a full-stack Todo application with AI-powered task assistance. The application includes:

- Phase 2: Traditional task management UI (forms, lists, authentication)
- Phase 3: AI-powered conversational task assistant with natural language processing

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm package manager
- Backend API running on http://localhost:8000 (see `../backend/README.md`)
- OpenAI API key (for Phase 3 AI features)

### Installation

First, install dependencies:

```bash
pnpm install
```

### Environment Variables

The frontend requires the backend API URL. This is configured in the Next.js environment:

```bash
# Optional: Create .env.local if you need to override the default API URL
# Default: http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

The OpenAI API key is configured in the backend (root `.env` file), not in the frontend.

### Run Development Server

Start the development server:

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Phase 3: AI Features

### AI Chat Widget

The application includes an AI-powered chat widget that allows users to manage tasks using natural language. The chat widget is available on the `/tasks` page.

**Key Features:**
- Natural language task creation ("Add buy groceries tomorrow at 3pm")
- Conversational task queries ("What tasks are due this week?")
- Task updates via chat ("Change meeting to 'Team standup'")
- Task completion commands ("Mark groceries as done")
- Real-time sync between traditional UI and AI chat
- Proactive suggestions for overdue tasks

**How to Use:**
1. Navigate to the tasks page (`/tasks`)
2. Click the chat widget icon in the bottom-right corner
3. Type natural language commands like:
   - "Add call dentist by Friday"
   - "What tasks are pending?"
   - "Mark groceries as complete"
   - "Help me plan the quarterly report task"
4. Confirm proposed actions in the dialog
5. Tasks sync automatically with the traditional UI

### New Dependencies (Phase 3)

The following packages were added for AI functionality:

```json
{
  "dependencies": {
    "@microsoft/fetch-event-source": "^2.0.1",  // Server-Sent Events for real-time sync
    "ai": "^5.0.115",                           // Vercel AI SDK
    "openai": "^6.15.0"                         // OpenAI client (used by AI SDK)
  }
}
```

**Dependency Details:**
- **@microsoft/fetch-event-source**: Robust SSE client for real-time task updates between UI and chat
- **ai**: Vercel AI SDK for streaming AI responses and structured outputs
- **openai**: OpenAI client library for GPT-4o-mini integration

### AI Feature Configuration

AI features are controlled by the backend. To enable/disable:

1. Set `AI_FEATURES_ENABLED=true` in the root `.env` file
2. Ensure `OPENAI_API_KEY` is configured in the root `.env` file
3. Restart the backend server

When AI features are disabled:
- Chat widget will display an error message
- Users can still use traditional task forms
- Application degrades gracefully

### Environment Variables (AI-Related)

All AI-related environment variables are configured in the **backend** (root `.env` file):

```bash
# Required for AI features to work
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3

# Rate limiting
AI_RATE_LIMIT_PER_DAY=100
AI_RATE_LIMIT_PER_HOUR=20

# Feature flag
AI_FEATURES_ENABLED=true
```

The frontend does NOT require these variables - it communicates with the backend API which handles all OpenAI integration.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
