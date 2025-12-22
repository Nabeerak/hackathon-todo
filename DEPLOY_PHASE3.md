# Phase 3 Deployment Guide

## Quick Deploy Checklist

### Prerequisites
- [ ] GitHub account with code pushed
- [ ] Railway account (free tier): https://railway.app
- [ ] Vercel account (free tier): https://vercel.com
- [ ] OpenAI API key: https://platform.openai.com/api-keys

---

## Step 1: Deploy Backend to Railway (10 mins)

### 1.1 Create Railway Project
```bash
# Push code to GitHub first
git add .
git commit -m "Phase 3 ready for deployment"
git push origin 003-ai-task-assistant
```

1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `hackathon-todo` repository
5. Railway auto-detects the backend

### 1.2 Add PostgreSQL Database
1. Click "+ New" in your project
2. Select "Database" → "PostgreSQL"
3. Railway automatically creates `DATABASE_URL` variable

### 1.3 Configure Environment Variables

In Railway dashboard, add these variables:

```bash
# Auto-configured by Railway
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Generate new JWT secret
JWT_SECRET_KEY=<run: openssl rand -hex 32>
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=production

# Will be updated after frontend deployment
ALLOWED_ORIGINS=http://localhost:3000
FRONTEND_URL=http://localhost:3000
BACKEND_URL=https://your-app.railway.app

# Phase 3: AI Configuration
OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=200
OPENAI_TEMPERATURE=0.3

# Phase 3: Rate Limiting
AI_RATE_LIMIT_PER_DAY=15
AI_RATE_LIMIT_PER_HOUR=5

# Phase 3: Feature Flags
AI_FEATURES_ENABLED=true
```

### 1.4 Configure Build Settings

Railway should auto-detect, but verify:
- **Root Directory**: `backend`
- **Build Command**: `uv sync`
- **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### 1.5 Deploy
1. Click "Deploy"
2. Wait for build to complete (~2-3 minutes)
3. Copy your Railway URL: `https://your-app.railway.app`
4. Test: Visit `https://your-app.railway.app/health`

---

## Step 2: Deploy Frontend to Vercel (5 mins)

### 2.1 Create Vercel Project
1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`

### 2.2 Add Environment Variable

```bash
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```

### 2.3 Deploy
1. Click "Deploy"
2. Wait for build (~2-3 minutes)
3. Copy your Vercel URL: `https://your-app.vercel.app`

---

## Step 3: Update CORS Settings

### 3.1 Update Railway Backend

Go back to Railway and update:
```bash
ALLOWED_ORIGINS=https://your-app.vercel.app
FRONTEND_URL=https://your-app.vercel.app
```

### 3.2 Redeploy Backend
Railway will auto-redeploy with new environment variables

---

## Step 4: Test Production Deployment

### 4.1 Backend Health Check
```bash
curl https://your-app.railway.app/health
# Should return: {"status":"healthy","database":"connected","environment":"production"}
```

### 4.2 Frontend Test
1. Visit `https://your-app.vercel.app`
2. Sign up with a new account
3. Create a task via form (traditional way)
4. Open chat widget (bottom right)
5. Type: "add buy groceries tomorrow"
6. Verify task is created

### 4.3 AI Chat Test
```bash
# Test chat endpoint
curl -X POST https://your-app.railway.app/api/v1/chat/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "what are my tasks?"}'
```

---

## Alternative: Deploy to Render

### Backend (Render)
1. Go to https://render.com
2. New "Web Service"
3. Connect GitHub repo
4. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install uv && uv sync && uv pip compile pyproject.toml -o requirements.txt && pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.13

### Database (Neon)
1. Go to https://neon.tech
2. Create new project
3. Copy `DATABASE_URL`
4. Add to Render environment variables

---

## Cost Estimates (Free Tiers)

- **Railway**: $5/month free credit (enough for 1 backend + database)
- **Vercel**: Unlimited free deployments for hobby projects
- **OpenAI**: ~$0.12/user/month (15 messages/day @ GPT-4o-mini)

**Total**: **~$0.12/user/month** (only AI costs)

---

## Troubleshooting

### CORS Errors
- Verify `ALLOWED_ORIGINS` includes your Vercel URL
- Check Railway logs: `railway logs`

### Database Connection Failed
- Ensure `DATABASE_URL` has `?sslmode=require` suffix
- Check Railway database is running

### OpenAI API Errors
- Verify `OPENAI_API_KEY` is valid
- Check API quota at https://platform.openai.com/usage
- Ensure rate limits aren't exceeded

### Build Failures
- Check Railway logs for Python/UV errors
- Verify `pyproject.toml` has all dependencies
- Test locally: `cd backend && uv sync`

---

## Next Steps: Phase 4 & 5

After Phase 3 is deployed:
1. **Phase 4**: Advanced AI features (voice input, task templates, smart scheduling)
2. **Phase 5**: Collaboration & sharing (team tasks, real-time collaboration, notifications)

Ready to deploy? Start with Step 1! 🚀
