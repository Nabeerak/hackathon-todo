# Deploy Backend to Render - Step by Step Guide

**Platform**: Render.com
**Time**: 15-20 minutes
**Cost**: Free tier available

---

## Prerequisites

- [ ] GitHub account with code pushed
- [ ] Render account (sign up at https://render.com)
- [ ] OpenAI API key (get from https://platform.openai.com/api-keys)

---

## Step 1: Prepare Your Code (5 mins)

### 1.1 Commit and Push to GitHub

```bash
# Make sure you're on the correct branch
cd /home/nabeera/hackathon-todo
git status

# Add all changes
git add .
git commit -m "Phase 3: Ready for Render deployment"
git push origin 003-ai-task-assistant
```

### 1.2 Create requirements.txt for Render

Render needs a `requirements.txt` file. Create it:

```bash
cd backend
uv pip compile pyproject.toml -o requirements.txt
git add requirements.txt
git commit -m "Add requirements.txt for Render"
git push
```

---

## Step 2: Create PostgreSQL Database on Render (5 mins)

### 2.1 Create Database

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `hackathon-todo-db`
   - **Database**: `todo_db`
   - **User**: `todo_user` (auto-generated)
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: 16
   - **Plan**: **Free** (Expires after 90 days, can upgrade)
4. Click **"Create Database"**
5. Wait 2-3 minutes for database to provision

### 2.2 Copy Database URL

1. Once created, go to database dashboard
2. Scroll down to **"Connections"**
3. Copy **"Internal Database URL"** (starts with `postgresql://`)
4. Save it somewhere - you'll need it next

**Example**:
```
postgresql://todo_user:password123@dpg-xyz.render.com/todo_db
```

---

## Step 3: Deploy Backend Web Service (10 mins)

### 3.1 Create Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Choose **"Build and deploy from a Git repository"**
4. Click **"Connect"** next to GitHub
5. Find your `hackathon-todo` repository
6. Click **"Connect"**

### 3.2 Configure Service

Fill in the following:

**Basic Settings**:
- **Name**: `hackathon-todo-api`
- **Region**: Same as your database
- **Branch**: `003-ai-task-assistant` (or `main`)
- **Root Directory**: `backend`
- **Runtime**: **Python 3**

**Build & Deploy**:
- **Build Command**:
  ```bash
  pip install uv && uv pip compile pyproject.toml -o requirements.txt && pip install -r requirements.txt
  ```

- **Start Command**:
  ```bash
  uvicorn src.main:app --host 0.0.0.0 --port $PORT
  ```

**Plan**:
- Select **"Free"** (0.1 CPU, 512 MB RAM - enough for Phase 3)

### 3.3 Add Environment Variables

Scroll down to **"Environment Variables"** section and add these:

**Click "Add Environment Variable" for each:**

1. **DATABASE_URL**
   ```
   <paste your Internal Database URL from Step 2.2>
   ```

2. **JWT_SECRET_KEY**
   ```bash
   # Generate a secure key:
   # Run: openssl rand -hex 32
   # Or use: https://generate-secret.now.sh/64
   ```
   Example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6`

3. **JWT_ALGORITHM**
   ```
   HS256
   ```

4. **JWT_EXPIRE_DAYS**
   ```
   7
   ```

5. **ENVIRONMENT**
   ```
   production
   ```

6. **ALLOWED_ORIGINS**
   ```
   http://localhost:3000
   ```
   *(We'll update this after frontend deployment)*

7. **FRONTEND_URL**
   ```
   http://localhost:3000
   ```
   *(We'll update this after frontend deployment)*

8. **BACKEND_URL**
   ```
   https://hackathon-todo-api.onrender.com
   ```
   *(Replace with your actual Render URL - check after creation)*

9. **OPENAI_API_KEY**
   ```
   sk-proj-YOUR-KEY-HERE
   ```
   *(Get from https://platform.openai.com/api-keys)*

10. **OPENAI_MODEL**
    ```
    gpt-4o-mini
    ```

11. **OPENAI_MAX_TOKENS**
    ```
    200
    ```

12. **OPENAI_TEMPERATURE**
    ```
    0.3
    ```

13. **AI_RATE_LIMIT_PER_DAY**
    ```
    15
    ```

14. **AI_RATE_LIMIT_PER_HOUR**
    ```
    5
    ```

15. **AI_FEATURES_ENABLED**
    ```
    true
    ```

### 3.4 Deploy

1. Click **"Create Web Service"**
2. Render will start building (takes 3-5 minutes)
3. Watch the logs for any errors
4. Once you see: `Application startup complete.`
5. Your backend is live! 🎉

### 3.5 Get Your Backend URL

1. On the service dashboard, you'll see the URL at the top
2. Example: `https://hackathon-todo-api.onrender.com`
3. Copy this URL - you'll need it for frontend

---

## Step 4: Test Your Backend (2 mins)

### 4.1 Health Check

Open your browser or use curl:

```bash
curl https://hackathon-todo-api.onrender.com/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "production"
}
```

### 4.2 API Documentation

Visit in browser:
```
https://hackathon-todo-api.onrender.com/docs
```

You should see the FastAPI interactive documentation.

### 4.3 Test Signup

```bash
curl -X POST https://hackathon-todo-api.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test12345",
    "display_name": "Test User"
  }'
```

**Expected**: You should get back a JWT token!

---

## Step 5: Update CORS Settings (1 min)

After you deploy the frontend (next step), come back here:

1. Go to your Render service dashboard
2. Click **"Environment"** tab
3. Update these variables:
   - **ALLOWED_ORIGINS**: `https://your-app.vercel.app`
   - **FRONTEND_URL**: `https://your-app.vercel.app`
4. Click **"Save Changes"**
5. Render will auto-redeploy (~1 min)

---

## Troubleshooting

### Build Failed

**Error**: `uv: command not found`
**Fix**: Update build command to:
```bash
pip install uv && uv pip compile pyproject.toml -o requirements.txt && pip install -r requirements.txt
```

**Error**: `Module 'src' not found`
**Fix**: Verify **Root Directory** is set to `backend`

**Error**: `requirements.txt not found`
**Fix**: Run Step 1.2 to generate requirements.txt and push to GitHub

### Database Connection Failed

**Error**: `FATAL: no pg_hba.conf entry`
**Fix**:
1. Go to database dashboard
2. Use **"Internal Database URL"** not "External"
3. Ensure URL has `?sslmode=require` at the end

### Application Won't Start

**Error**: `Address already in use`
**Fix**: Ensure start command uses `$PORT` variable:
```bash
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

**Error**: `Application startup failed`
**Fix**: Check logs in Render dashboard for specific Python errors

### CORS Errors (After Frontend Deployed)

**Error**: `No 'Access-Control-Allow-Origin' header`
**Fix**:
1. Update `ALLOWED_ORIGINS` environment variable
2. Must include your Vercel frontend URL
3. Multiple origins: `https://app1.vercel.app,https://app2.vercel.app`

### OpenAI API Errors

**Error**: `Invalid API key`
**Fix**:
1. Get new key from https://platform.openai.com/api-keys
2. Update `OPENAI_API_KEY` environment variable
3. Ensure no extra spaces in the key

**Error**: `Rate limit exceeded`
**Fix**:
1. Check usage at https://platform.openai.com/usage
2. Add payment method to OpenAI account
3. Increase `AI_RATE_LIMIT_PER_DAY` if needed

---

## Free Tier Limitations

Render Free Tier:
- ✅ 750 hours/month (enough for 24/7 uptime)
- ⚠️ Spins down after 15 minutes of inactivity (cold start ~30 seconds)
- ⚠️ Database expires after 90 days (upgrade to $7/month for persistent)
- ✅ Automatic HTTPS with SSL certificate
- ✅ Unlimited deployments

**Upgrade Options**:
- **Starter Plan**: $7/month (always on, no cold starts)
- **PostgreSQL**: $7/month (persistent database)

---

## Next Steps

1. ✅ Backend deployed to Render
2. ⏭️ Deploy frontend to Vercel (see DEPLOY_PHASE3.md Step 2)
3. ⏭️ Update CORS settings (Step 5 above)
4. ⏭️ Test full application end-to-end

---

## Your Backend URL

Once deployed, save this info:

```
Backend URL: https://hackathon-todo-api.onrender.com
Database: hackathon-todo-db (Render PostgreSQL)
Status: https://dashboard.render.com
```

Ready to deploy frontend? Continue to Vercel deployment! 🚀
