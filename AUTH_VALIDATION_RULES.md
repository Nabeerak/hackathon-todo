# Authentication Validation Rules

Complete documentation of all sign up and sign in validation rules implemented in the application.

---

## Sign Up Validation

### Email Validation

**Rules**:
1. ✅ Must be a valid email format (e.g., user@example.com)
2. ✅ Must start with alphanumeric character
3. ✅ Must contain exactly one @ symbol
4. ✅ Must have a domain with TLD (.com, .org, etc.)
5. ✅ Minimum length: 3 characters
6. ✅ Maximum length: 254 characters (RFC 5321)
7. ✅ Local part (before @) max: 64 characters
8. ✅ Cannot contain consecutive dots (..)
9. ✅ Cannot start or end with a dot
10. ✅ Domain must be at least 4 characters (e.g., a.co)
11. ✅ **Email uniqueness**: Cannot create account with existing email

**Valid Examples**:
- user@example.com
- john.doe@company.co.uk
- test123@mail.io

**Invalid Examples**:
- user@example (no TLD)
- user..name@example.com (consecutive dots)
- .user@example.com (starts with dot)
- @example.com (no local part)

**Error Messages**:
- "Invalid email format. Please enter a valid email address (e.g., user@example.com)"
- "Email is too short"
- "Email is too long (max 254 characters)"
- "An account with this email already exists. Please sign in or use a different email address."

### Password Validation

**Rules**:
1. ✅ Minimum length: 8 characters
2. ✅ Maximum length: 72 characters (bcrypt limit)
3. ✅ Byte-level validation for UTF-8 characters
4. ✅ Password is hashed with bcrypt before storage

**Valid Examples**:
- password123
- MySecureP@ss123
- long-secure-password

**Invalid Examples**:
- pass (too short)
- [72+ character password] (exceeds bcrypt limit)

**Error Messages**:
- "Password must be at least 8 characters"
- "Password cannot exceed 72 bytes"

### Display Name Validation

**Rules**:
1. ✅ Required field
2. ✅ Minimum length: 1 character
3. ✅ Maximum length: 100 characters
4. ✅ HTML-escaped to prevent XSS attacks

**Error Messages**:
- "Display name is required"
- "Display name is too long (max 100 characters)"

### Signup Error Scenarios

| Scenario | HTTP Status | Frontend Message | Action |
|----------|-------------|------------------|--------|
| Email already exists | 409 Conflict | "An account with this email already exists. Please sign in instead or use a different email." | Shows link to sign in page |
| Invalid email format | 422 Validation Error | "Invalid email format. Please enter a valid email address (e.g., user@example.com)" | User corrects email |
| Password too short | 422 Validation Error | "Password must be at least 8 characters" | User lengthens password |
| Missing required field | 422 Validation Error | "All fields are required" | User fills missing fields |
| Server error | 500 Internal Error | "Signup failed. Please try again." | User retries |

---

## Sign In Validation

### Email Validation

**Rules**:
1. ✅ Same email format validation as signup
2. ✅ Must match an existing account

**Error Messages**:
- "Invalid email format. Please check your email address."
- "Incorrect email or password. Please check your credentials and try again."

### Password Validation

**Rules**:
1. ✅ Must match the password for the given email
2. ✅ Checked against bcrypt hash

**Security Note**: 
For security reasons, the error message doesn't reveal whether the email exists or the password is wrong. It shows a generic "Incorrect email or password" to prevent email enumeration attacks.

**Error Messages**:
- "Incorrect email or password. Please check your credentials and try again."

### Signin Error Scenarios

| Scenario | HTTP Status | Frontend Message | Action |
|----------|-------------|------------------|--------|
| Wrong email/password | 401 Unauthorized | "Incorrect email or password. Please check your credentials and try again." | User corrects credentials |
| Invalid email format | 422 Validation Error | "Invalid email format. Please check your email address." | User corrects email format |
| Account not found | 404 Not Found | "Account not found. Please check your email or sign up for a new account." | Shows link to signup page |
| Server error | 500 Internal Error | "Sign in failed. Please try again." | User retries |

---

## User Experience Enhancements

### Helpful Navigation

1. **Signup page - Email exists**:
   - Shows error: "An account with this email already exists..."
   - Displays link: "Go to Sign In →"
   - User clicks and goes to signin page

2. **Signin page - Account not found**:
   - Shows error: "Account not found..."
   - Displays link: "Create a new account →"
   - User clicks and goes to signup page

### Real-time Validation

**Frontend (Client-side)**:
- Email format checked before submission
- Password length checked before submission
- Immediate feedback to user

**Backend (Server-side)**:
- Final validation with detailed error messages
- Database constraints enforced
- Security checks applied

### Error Message Guidelines

All error messages follow these principles:
1. **Clear**: Tell user exactly what's wrong
2. **Actionable**: Explain how to fix it
3. **Helpful**: Provide examples or links
4. **Secure**: Don't reveal sensitive information

---

## Implementation Files

### Backend
- `backend/src/api/auth.py` - Authentication endpoints and validation
- `backend/src/auth/jwt.py` - Password hashing and JWT tokens
- `backend/src/models.py` - User model with email uniqueness constraint

### Frontend
- `frontend/src/app/auth/signup/page.tsx` - Signup page with validation
- `frontend/src/app/auth/signin/page.tsx` - Signin page with validation
- `frontend/src/lib/api.ts` - API client with error handling

---

## Testing Scenarios

### Test Case 1: Signup with New Email
```
Input: email=new@example.com, password=password123, name=John
Expected: ✅ Success - Account created, user redirected to tasks
```

### Test Case 2: Signup with Existing Email
```
Input: email=existing@example.com, password=password123, name=John
Expected: ❌ 409 Error - "An account with this email already exists..."
```

### Test Case 3: Signup with Invalid Email
```
Input: email=invalid@example, password=password123, name=John
Expected: ❌ 422 Error - "Invalid email format..."
```

### Test Case 4: Signup with Short Password
```
Input: email=test@example.com, password=short, name=John
Expected: ❌ 422 Error - "Password must be at least 8 characters"
```

### Test Case 5: Signin with Correct Credentials
```
Input: email=user@example.com, password=correctpassword
Expected: ✅ Success - User signed in, redirected to tasks
```

### Test Case 6: Signin with Wrong Password
```
Input: email=user@example.com, password=wrongpassword
Expected: ❌ 401 Error - "Incorrect email or password..."
```

### Test Case 7: Signin with Non-existent Email
```
Input: email=nobody@example.com, password=anypassword
Expected: ❌ 401 Error - "Incorrect email or password..."
```

---

## Security Considerations

### Password Security
- ✅ Passwords hashed with bcrypt (cost factor: default)
- ✅ Never stored in plaintext
- ✅ Never returned in API responses
- ✅ 72-byte limit enforced (bcrypt constraint)

### Email Privacy
- ✅ Email enumeration prevented (signin doesn't reveal if email exists)
- ✅ Emails normalized (lowercase, trimmed)
- ✅ HTML-escaped to prevent XSS

### Session Security
- ✅ JWT tokens with 7-day expiry
- ✅ Tokens stored in localStorage (client-side)
- ✅ Automatic token injection in API calls
- ✅ Auto-redirect on 401/403 errors

---

**Last Updated**: 2025-12-16
**Status**: ✅ Fully Implemented and Tested
