"""Authentication API endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlmodel import Session, select
import html
import logging
import re

from ..models import User
from ..db import get_db_session
from ..auth.jwt import hash_password, verify_password, create_access_token

# Configure logging
logger = logging.getLogger(__name__)

# Strict email validation pattern
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$'
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class SignupRequest(BaseModel):
    """Signup request model."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    display_name: str = Field(min_length=1, max_length=100)

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format with strict rules."""
        email_str = str(v).strip().lower()

        # Check for empty or whitespace-only email
        if not email_str:
            raise ValueError("Email cannot be empty")

        # Check minimum length
        if len(email_str) < 3:
            raise ValueError("Email is too short")

        # Check maximum length (RFC 5321)
        if len(email_str) > 254:
            raise ValueError("Email is too long (max 254 characters)")

        # Validate with regex
        if not EMAIL_REGEX.match(email_str):
            raise ValueError("Invalid email format. Please enter a valid email address (e.g., user@example.com)")

        # Additional checks
        if '..' in email_str:
            raise ValueError("Email cannot contain consecutive dots")

        if email_str.startswith('.') or email_str.endswith('.'):
            raise ValueError("Email cannot start or end with a dot")

        local_part, domain = email_str.rsplit('@', 1)

        # Validate local part (before @)
        if len(local_part) > 64:
            raise ValueError("Email local part is too long (max 64 characters)")

        # Validate domain
        if len(domain) < 4:  # Minimum: a.co
            raise ValueError("Email domain is too short")

        if not '.' in domain:
            raise ValueError("Email domain must contain a dot (e.g., example.com)")

        return email_str

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength and bcrypt limit."""
        # Check byte limit first
        if len(v.encode('utf-8')) > 72:
            raise ValueError("Password cannot exceed 72 bytes")

        # Check minimum length
        if len(v) < 8:
            raise ValueError("Password too weak. Must have 8+ characters, uppercase, lowercase, and number")

        # Check for required character types
        has_uppercase = any(c.isupper() for c in v)
        has_lowercase = any(c.islower() for c in v)
        has_number = any(c.isdigit() for c in v)

        if not (has_uppercase and has_lowercase and has_number):
            raise ValueError("Password too weak. Must have 8+ characters, uppercase, lowercase, and number")

        return v

    @field_validator('display_name')
    @classmethod
    def sanitize_display_name(cls, v: str) -> str:
        """Sanitize display name to prevent XSS attacks."""
        return html.escape(v.strip())


class SigninRequest(BaseModel):
    """Signin request model."""
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format with strict rules."""
        email_str = str(v).strip().lower()

        # Check for empty or whitespace-only email
        if not email_str:
            raise ValueError("Email cannot be empty")

        # Validate with regex
        if not EMAIL_REGEX.match(email_str):
            raise ValueError("Invalid email format. Please enter a valid email address")

        return email_str


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    session: Session = Depends(get_db_session)
):
    """
    Register a new user.

    - Validates email uniqueness
    - Validates password strength (min 8 characters)
    - Hashes password before storage
    - Returns JWT token
    """
    # Check if email already exists
    statement = select(User).where(User.email == request.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        logger.warning(f"Signup attempt with existing email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists. Please sign in or use a different email address."
        )

    # Password validation is handled by Pydantic Field(min_length=8)

    # Create new user
    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        display_name=request.display_name,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    logger.info(f"New user registered: {user.email} (ID: {user.id})")

    # Create access token (convert user.id to string for JWT spec compliance)
    access_token = create_access_token(data={"sub": str(user.id), "user_id": user.id})

    return AuthResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "created_at": user.created_at.isoformat(),
        }
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(
    request: SigninRequest,
    session: Session = Depends(get_db_session)
):
    """
    Sign in an existing user.

    - Validates email and password
    - Returns JWT token on success
    """
    # Find user by email
    statement = select(User).where(User.email == request.email)
    user = session.exec(statement).first()

    # Check if user exists
    if not user:
        logger.warning(f"Failed signin attempt - user not found: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account does not exist. Create a new account now."
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        logger.warning(f"Failed signin attempt - wrong password: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password, please try again"
        )

    logger.info(f"User signed in: {user.email} (ID: {user.id})")

    # Create access token (convert user.id to string for JWT spec compliance)
    access_token = create_access_token(data={"sub": str(user.id), "user_id": user.id})

    return AuthResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "created_at": user.created_at.isoformat(),
        }
    )


@router.post("/signout")
async def signout():
    """
    Sign out (stateless - client discards token).

    Returns success message.
    """
    logger.info("User signed out (client-side token cleared)")
    return {"message": "Signed out successfully"}
