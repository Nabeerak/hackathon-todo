# Deployment Guide - Full-Stack Todo Application

This guide covers deploying both the frontend (Next.js) and backend (FastAPI) to production.

---

## Table of Contents

1. [Overview](#overview)
2. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
3. [Backend Deployment (Railway/Render)](#backend-deployment-railwayrender)
4. [Database Setup (Neon)](#database-setup-neon)
5. [Environment Variables](#environment-variables)
6. [Post-Deployment](#post-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Overview

**Architecture:**
- **Frontend**: Next.js 16 → Deploy to Vercel (recommended)
- **Backend**: FastAPI + PostgreSQL → Deploy to Railway or Render
- **Database**: PostgreSQL → Use Neon, Supabase, or Railway built-in DB

**Estimated Time**: 30-45 minutes

---

## Frontend Deployment (Vercel)

### Prerequisites

- GitHub repository with your code
- Vercel account (free tier works)

### Step 1: Prepare Frontend

\`\`\`bash
cd frontend
npm run build
npm start
# Verify at http://localhost:3000
\`\`\`

### Step 2: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework**: Next.js
   - **Root Directory**: \`frontend\`
5. Add environment variable:
   \`\`\`
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   \`\`\`
6. Click "Deploy"

---

## Backend Deployment (Railway)

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Create new project from GitHub
3. Select \`backend\` directory

### Step 2: Add PostgreSQL

1. Click "+ New" → "Database" → "PostgreSQL"
2. Copy DATABASE_URL

### Step 3: Set Environment Variables

\`\`\`bash
DATABASE_URL=\${{Postgres.DATABASE_URL}}
JWT_SECRET_KEY=<openssl rand -hex 32>
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend.vercel.app
\`\`\`

### Step 4: Configure Start Command

\`\`\`bash
uvicorn src.main:app --host 0.0.0.0 --port \$PORT
\`\`\`

---

## Environment Variables

### Backend

| Variable | Example |
|----------|---------|
| DATABASE_URL | \`postgresql://user:pass@host/db\` |
| JWT_SECRET_KEY | Generate with \`openssl rand -hex 32\` |
| ALLOWED_ORIGINS | \`https://app.vercel.app\` |

### Frontend

| Variable | Example |
|----------|---------|
| NEXT_PUBLIC_API_URL | \`https://api.railway.app\` |

---

## Post-Deployment

1. Visit \`https://your-backend.railway.app/health\`
2. Test API at \`https://your-backend.railway.app/docs\`
3. Visit frontend and test full flow

---

## Troubleshooting

**CORS Errors**: Verify ALLOWED_ORIGINS includes frontend URL
**Database Connection**: Check DATABASE_URL format includes \`?sslmode=require\`
**Build Fails**: Test locally with \`npm run build\`

---

**Last Updated**: 2025-12-16
