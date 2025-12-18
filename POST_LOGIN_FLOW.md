# Post-Login Flow Documentation

Complete guide to what happens after successful authentication in the Todo application.

---

## 📋 Complete User Journey

### 1. Landing Page (`/`)

**For Unauthenticated Users**:
- Shows welcome page with app description
- Two buttons:
  - "Sign In" → `/auth/signin`
  - "Create Account" → `/auth/signup`
- Lists key features

**For Authenticated Users**:
- ✅ **Automatically redirected to `/tasks`**
- No need to click anything
- Seamless experience

**File**: `frontend/src/app/page.tsx`

---

### 2. Sign Up Journey (`/auth/signup`)

**Step 1: Access Signup Page**
- User fills in:
  - Display Name (required, 1-100 chars)
  - Email (validated, unique)
  - Password (8-72 chars)

**Step 2: Client-Side Validation**
- Email format checked
- Password length checked
- Immediate feedback if invalid

**Step 3: Submit to Backend**
- POST request to `/api/auth/signup`
- Backend validates:
  - Email uniqueness
  - Email format (RFC 5321)
  - Password constraints
  - XSS prevention

**Step 4: Success Response**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "display_name": "John Doe",
    "created_at": "2025-12-16T10:30:00"
  }
}
```

**Step 5: Auto-Login**
- ✅ JWT token saved to localStorage
- ✅ User ID extracted from token
- ✅ **Automatic redirect to `/tasks`**

**Edge Case - Already Logged In**:
- If user somehow accesses signup page while logged in
- ✅ **Automatically redirected to `/tasks`** (prevents confusion)

**File**: `frontend/src/app/auth/signup/page.tsx`

---

### 3. Sign In Journey (`/auth/signin`)

**Step 1: Access Signin Page**
- User enters:
  - Email
  - Password

**Step 2: Client-Side Validation**
- Email format checked
- Immediate feedback if invalid

**Step 3: Submit to Backend**
- POST request to `/api/auth/signin`
- Backend verifies:
  - Email exists in database
  - Password matches bcrypt hash

**Step 4: Success Response**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "display_name": "John Doe",
    "created_at": "2025-12-16T10:30:00"
  }
}
```

**Step 5: Auto-Login**
- ✅ JWT token saved to localStorage
- ✅ User ID extracted from token
- ✅ **Automatic redirect to `/tasks`**

**Edge Case - Already Logged In**:
- If user somehow accesses signin page while logged in
- ✅ **Automatically redirected to `/tasks`** (prevents confusion)

**File**: `frontend/src/app/auth/signin/page.tsx`

---

### 4. Tasks Page (`/tasks`) - Main Application

**Authentication Check**:
```typescript
useEffect(() => {
  // Check authentication
  if (!AuthClient.isAuthenticated()) {
    router.push("/auth/signin");
    return;
  }
  // Load tasks
  loadTasks();
}, [router]);
```

**What Happens on Page Load**:

1. **Authentication Verification**
   - Checks if JWT token exists in localStorage
   - If NO token → Redirect to `/auth/signin`
   - If token exists → Proceed

2. **Extract User ID from Token**
   ```typescript
   const userId = AuthClient.getUserId();
   // Decodes JWT: payload.sub or payload.user_id
   ```

3. **Load User's Tasks**
   - GET request to `/api/${userId}/tasks`
   - Authorization header: `Bearer ${token}`
   - Backend validates:
     - Token is valid
     - Token not expired
     - User ID in URL matches token

4. **Display UI Components**
   ```
   ┌─────────────────────────────────────┐
   │  Header (with Sign Out button)      │
   ├─────────────────────────────────────┤
   │                                     │
   │  TaskForm (Create new task)         │
   │  ┌───────────────────────────────┐ │
   │  │ Title: [input]                │ │
   │  │ Description: [textarea]       │ │
   │  │ [Add Task] button             │ │
   │  └───────────────────────────────┘ │
   │                                     │
   │  TaskList (All user's tasks)        │
   │  ┌───────────────────────────────┐ │
   │  │ ☐ Task 1 [Edit] [Delete]     │ │
   │  │ ☑ Task 2 [Edit] [Delete]     │ │
   │  │ ☐ Task 3 [Edit] [Delete]     │ │
   │  └───────────────────────────────┘ │
   │                                     │
   └─────────────────────────────────────┘
   ```

**File**: `frontend/src/app/tasks/page.tsx`

---

## 🔐 JWT Token Details

### Token Structure

**JWT Token**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOjEsInVzZXJfaWQiOjEsImV4cCI6MTczNDQxMjgwMH0.
signature
```

**Decoded Payload**:
```json
{
  "sub": 1,           // Subject (user ID)
  "user_id": 1,       // User ID (duplicate for compatibility)
  "exp": 1734412800   // Expiration timestamp (7 days)
}
```

### Token Storage

**Location**: Browser localStorage
**Key**: `"auth_token"`

**Operations**:
- `AuthClient.setToken(token)` - Save after login
- `AuthClient.getToken()` - Retrieve for API calls
- `AuthClient.clearToken()` - Remove on signout
- `AuthClient.isAuthenticated()` - Check if token exists
- `AuthClient.getUserId()` - Extract user ID from token

**File**: `frontend/src/lib/auth.ts`

---

## 🔄 Session Management

### Token Lifecycle

1. **Creation**: When user signs up or signs in
2. **Storage**: Saved to localStorage immediately
3. **Usage**: Sent with every API request
4. **Validation**: Backend checks on every request
5. **Expiration**: 7 days from creation
6. **Renewal**: Not automatic - user must sign in again

### Auto-Authentication on Page Reload

**Scenario**: User refreshes page or closes/reopens browser

**What Happens**:
1. Page loads → Check localStorage for token
2. If token exists:
   - ✅ User stays on `/tasks` page
   - ✅ Tasks are loaded automatically
   - ✅ No need to sign in again
3. If no token or expired:
   - ❌ Redirected to `/auth/signin`

### Signout Process

**When User Clicks "Sign Out"**:

1. **Frontend Actions** (`Header.tsx`):
   ```typescript
   const handleSignout = async () => {
     // 1. Call backend signout (optional, logs the event)
     await APIClient.post("/api/auth/signout", {});
     
     // 2. Clear token from localStorage
     AuthClient.clearToken();
     
     // 3. Redirect to signin page
     router.push("/auth/signin");
   };
   ```

2. **Backend Actions** (`auth.py`):
   - Logs: "User signed out (client-side token cleared)"
   - Returns success message
   - Note: JWT is stateless, so backend doesn't invalidate it
   - Token becomes useless once frontend deletes it

3. **Result**:
   - User is on signin page
   - All subsequent requests fail (no token)
   - User must sign in to access tasks

**File**: `frontend/src/components/Header.tsx`

---

## 🛡️ Security Features

### 1. Protected Routes

**Tasks page is protected**:
- Checks authentication before rendering
- Redirects to signin if not authenticated
- Prevents unauthorized access

### 2. Automatic Token Injection

**Every API request includes token**:
```typescript
const headers: HeadersInit = {
  "Content-Type": "application/json",
  "Authorization": `Bearer ${token}`, // Auto-added
};
```

### 3. Error Handling

**401 Unauthorized or 403 Forbidden**:
```typescript
if (response.status === 401 || response.status === 403) {
  AuthClient.clearToken();
  window.location.href = "/auth/signin"; // Auto-redirect
  throw new APIError(...);
}
```

**Result**: Invalid token = Automatic signout

**File**: `frontend/src/lib/api.ts`

### 4. User Data Isolation

**Backend validates every request**:
```python
# Extract user ID from JWT token
current_user_id = Depends(get_current_user_id)

# Verify URL user_id matches token
validate_user_id_match(user_id, current_user_id)

# If mismatch → 403 Forbidden
```

**Result**: Users can only access their own data

**File**: `backend/src/auth/middleware.py`

---

## 📱 User Interface After Login

### Header Component

**Features**:
- Shows "My Tasks" title
- Sign out button (responsive)
  - Desktop: "Sign Out" text
  - Mobile: Icon only
- Sticky positioning (stays at top on scroll)

**File**: `frontend/src/components/Header.tsx`

### TaskForm Component

**Features**:
- Title input (required, max 200 chars)
- Description textarea (optional, max 1000 chars)
- "Add Task" button
- Loading state during submission
- Error messages
- Responsive design (mobile-friendly)

**File**: `frontend/src/components/TaskForm.tsx`

### TaskList Component

**Features**:
- Shows all tasks in reverse chronological order
- Empty state: "No tasks yet"
- Responsive grid layout
- Task count display

**File**: `frontend/src/components/TaskList.tsx`

### TaskItem Component

**Features**:
- Checkbox to toggle completion
- Task title and description
- Edit button (inline editing)
- Delete button (with confirmation)
- Timestamp
- Touch-friendly on mobile (44px min buttons)
- Visual feedback (strikethrough for completed)

**File**: `frontend/src/components/TaskItem.tsx`

---

## 🎯 Complete Flow Diagram

```
┌─────────────────┐
│   Landing (/)   │
│                 │
│ Not logged in:  │
│ - Show welcome  │
│                 │
│ Already logged: │
│ → Redirect to   │
│   /tasks        │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼────┐  ┌─▼──────┐
│ Signup │  │ Signin │
│        │  │        │
│ Already│  │Already │
│ logged:│  │logged: │
│→/tasks │  │→/tasks │
└───┬────┘  └────┬───┘
    │            │
    │  ┌─────────┘
    │  │ Submit credentials
    │  │ 
    │  ▼
    │ Backend validates
    │  │
    │  ▼
    │ ✅ Success
    │  │
    │  ▼
    │ Return JWT token
    │  │
    └──┴──────────┐
                  │
                  ▼
         ┌────────────────┐
         │ Save to        │
         │ localStorage   │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │ Redirect to    │
         │ /tasks         │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────────────┐
         │  Tasks Page (/tasks)   │
         │                        │
         │ 1. Check auth          │
         │ 2. Extract user ID     │
         │ 3. Load tasks          │
         │ 4. Show UI:            │
         │    - Header            │
         │    - Task Form         │
         │    - Task List         │
         │                        │
         │ User can:              │
         │ ✓ Create tasks         │
         │ ✓ Edit tasks           │
         │ ✓ Delete tasks         │
         │ ✓ Toggle complete      │
         │ ✓ Sign out             │
         └────────────────────────┘
```

---

## ⚡ Quick Reference

| Action | Result |
|--------|--------|
| Visit `/` while logged in | → Redirect to `/tasks` |
| Visit `/auth/signin` while logged in | → Redirect to `/tasks` |
| Visit `/auth/signup` while logged in | → Redirect to `/tasks` |
| Visit `/tasks` not logged in | → Redirect to `/auth/signin` |
| Successful signup | → Save token → Redirect to `/tasks` |
| Successful signin | → Save token → Redirect to `/tasks` |
| Click "Sign Out" | → Clear token → Redirect to `/auth/signin` |
| Page refresh on `/tasks` | → Check token → Stay on page (if valid) |
| Token expired | → 401 error → Clear token → Redirect to `/auth/signin` |

---

**Last Updated**: 2025-12-16
**Status**: ✅ Fully Implemented
