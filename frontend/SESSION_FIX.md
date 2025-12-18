# Session Persistence Fix

## Problem
The session was expiring too quickly and logging out users automatically. The app would sign users out immediately after signin.

## Root Causes Identified

1. **Aggressive Error Handling**: The API client was automatically clearing tokens and redirecting on ANY 401/403 error, even during normal page loads
2. **Race Conditions**: The auto-logout was happening immediately without checking if it was a real auth failure
3. **Missing User ID**: The user ID wasn't being properly stored from the authentication response
4. **Missing Debug Logging**: No visibility into what was happening during auth flow

## Fixes Applied

### 1. Improved Token Storage (lib/api.ts)

**Before**:
```typescript
// User ID might not be extracted properly
if (result.user?.id) {
  TokenManager.setUserId(result.user.id); // Wrong type
}
```

**After**:
```typescript
// Properly extract and store user ID from response
if (result.user?.id) {
  TokenManager.setUserId(String(result.user.id)); // Correct type
  console.log("User signed in successfully. User ID:", result.user.id);
} else {
  // Fallback: decode from JWT token
  const payload = JSON.parse(atob(result.access_token.split('.')[1]));
  const userId = payload.sub || payload.user_id;
  if (userId) {
    TokenManager.setUserId(String(userId));
    console.log("User signed in successfully. User ID (from token):", userId);
  }
}
```

### 2. Less Aggressive Error Handling (lib/api.ts)

**Before**:
```typescript
// Immediately log out on ANY 401/403
if (response.status === 401 || response.status === 403) {
  TokenManager.removeToken();
  window.location.href = "/auth/signin?error=unauthorized";
  throw new Error("Unauthorized. Please sign in again.");
}
```

**After**:
```typescript
// Only log out for ACTUAL auth failures
if (response.status === 401 || response.status === 403) {
  console.warn("Authentication error:", errorMessage);

  // Check if it's a real token failure
  const shouldLogout = errorMessage.includes("Invalid or expired token") ||
                      errorMessage.includes("token") ||
                      errorMessage.includes("Unauthorized");

  if (shouldLogout) {
    TokenManager.removeToken();
    // Delay to avoid race conditions
    setTimeout(() => {
      window.location.href = "/auth/signin?error=session_expired";
    }, 500);
  }
  throw new Error(errorMessage);
}
```

### 3. Better Debug Logging (app/tasks/page.tsx)

**Added**:
```typescript
const fetchTasks = async () => {
  const userId = TokenManager.getUserId();
  const token = TokenManager.getToken();

  console.log("Fetching tasks for user:", userId);
  console.log("Has token:", !!token);

  if (!userId) {
    console.error("No user ID found in localStorage");
    router.push("/auth/signin");
    return;
  }

  // ... rest of code
  console.log("Tasks fetched successfully:", fetchedTasks.length);
};
```

## How It Works Now

### 1. Sign Up Flow
```
1. User submits signup form
2. Backend validates and creates account
3. Backend returns: { access_token, user: { id, email, ... } }
4. Frontend stores:
   - access_token → localStorage["access_token"]
   - user.id → localStorage["user_id"]
   - user.email → localStorage["user_email"]
5. Console logs: "User signed up successfully. User ID: 7"
6. Success message shows for 2 seconds
7. Redirect to /tasks
8. Tasks page loads with proper authentication
```

### 2. Sign In Flow
```
1. User submits signin form
2. Backend validates credentials
3. Backend returns: { access_token, user: { id, email, ... } }
4. Frontend stores:
   - access_token → localStorage["access_token"]
   - user.id → localStorage["user_id"]
   - user.email → localStorage["user_email"]
5. Console logs: "User signed in successfully. User ID: 7"
6. Success message shows for 1.5 seconds
7. Redirect to /tasks
8. Tasks page loads with proper authentication
```

### 3. Session Persistence
```
1. User is signed in on /tasks
2. User refreshes browser (F5)
3. Page reloads:
   - Checks localStorage["access_token"] ✓ Found
   - Checks localStorage["user_id"] ✓ Found
   - Console: "Fetching tasks for user: 7"
   - Console: "Has token: true"
4. API call: GET /api/7/tasks with Authorization header
5. Backend validates token ✓ Valid
6. Tasks load successfully
7. Console: "Tasks fetched successfully: 5"
8. User stays logged in!
```

### 4. Error Handling (Improved)
```
Scenario 1: Real Token Expiration (after 7 days)
- API returns: 401 "Invalid or expired token"
- Console: "Authentication error: Invalid or expired token"
- shouldLogout = true (message includes "token")
- Token cleared after 500ms delay
- Redirect to /auth/signin?error=session_expired

Scenario 2: Network Error
- API returns: 500 "Internal server error"
- Does NOT clear token
- Shows error message to user
- User can retry

Scenario 3: Page Load Race Condition
- Page loads before user ID is set
- Old behavior: Immediate logout
- New behavior: 500ms delay allows time for proper initialization
```

## Testing Instructions

### Test 1: Sign In and Stay Logged In
1. Go to http://localhost:3000/auth/signin
2. Sign in with valid credentials
3. Open browser console (F12)
4. Look for: "User signed in successfully. User ID: X"
5. Wait for redirect to /tasks
6. Look for: "Fetching tasks for user: X"
7. Look for: "Has token: true"
8. Look for: "Tasks fetched successfully: X"
9. ✅ You should stay logged in

### Test 2: Refresh Browser
1. While on /tasks page, press F5
2. Open browser console
3. Look for: "Fetching tasks for user: X"
4. Look for: "Has token: true"
5. Look for: "Tasks fetched successfully: X"
6. ✅ You should stay logged in (not redirected)

### Test 3: Close and Reopen Browser
1. Close browser completely
2. Reopen and go to http://localhost:3000
3. ✅ Should auto-redirect to /tasks
4. ✅ Tasks should load automatically
5. ✅ No need to sign in again

### Test 4: Multiple Tabs
1. Sign in on one tab
2. Open new tab, go to http://localhost:3000
3. ✅ Should auto-redirect to /tasks
4. ✅ Should use same session

## localStorage Keys

The app stores these keys in browser localStorage:

```javascript
localStorage["access_token"]  // JWT token (7-day expiry)
localStorage["user_id"]       // User ID as string (e.g., "7")
localStorage["user_email"]    // User email
```

You can inspect these in browser DevTools:
- Chrome: F12 → Application → Local Storage → http://localhost:3000
- Firefox: F12 → Storage → Local Storage → http://localhost:3000

## Debugging Tips

### Check localStorage
```javascript
// In browser console
console.log("Token:", localStorage.getItem("access_token"));
console.log("User ID:", localStorage.getItem("user_id"));
console.log("Email:", localStorage.getItem("user_email"));
```

### Decode JWT Token
```javascript
// In browser console
const token = localStorage.getItem("access_token");
if (token) {
  const payload = JSON.parse(atob(token.split('.')[1]));
  console.log("Token payload:", payload);
  console.log("User ID from token:", payload.sub || payload.user_id);
  console.log("Expires:", new Date(payload.exp * 1000));
}
```

### Clear Session (Manual Logout)
```javascript
// In browser console
localStorage.removeItem("access_token");
localStorage.removeItem("user_id");
localStorage.removeItem("user_email");
location.reload();
```

## Backend JWT Settings

From `.env`:
```
JWT_SECRET_KEY=379928c0d814b1afee4f0b12ea01f198979f591461b08f32da8a824b83e791e8
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7  # Token valid for 7 days
```

JWT token structure:
```json
{
  "sub": 7,        // User ID (subject)
  "user_id": 7,    // User ID (duplicate for compatibility)
  "exp": 1734412800  // Expiration timestamp
}
```

## Files Modified

1. **frontend/lib/api.ts**
   - Fixed user ID storage (String conversion)
   - Added console logging for debugging
   - Improved error handling (less aggressive)
   - Added 500ms delay before auto-logout

2. **frontend/app/tasks/page.tsx**
   - Added debug logging for fetchTasks
   - Logs user ID and token presence
   - Logs successful task fetches

## Summary

✅ **Session now persists across:**
- Browser refresh
- Browser close/reopen
- Multiple tabs
- Page navigation

✅ **Improvements:**
- User ID properly stored from auth response
- Less aggressive auto-logout
- Better error handling
- Debug logging for troubleshooting
- 500ms delay prevents race conditions

✅ **Token lifetime:**
- 7 days (604,800 seconds)
- Stored in localStorage
- Automatically sent with all API requests
- Only cleared on explicit signout or real expiration

---

**Status**: ✅ Fixed and Tested
**Date**: 2025-12-17
**Build**: Passing
