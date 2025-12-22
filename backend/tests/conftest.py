"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from src.main import app
from src.db import get_db_session
from src.models import User


@pytest.fixture(name="db_session")
def db_session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    """Create a test client with database override."""
    def get_db_session_override():
        return db_session
    app.dependency_overrides[get_db_session] = get_db_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(db_session: Session):
    """Create a test user."""
    from src.auth.jwt import hash_password
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        display_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(name="auth_token")
def auth_token_fixture(test_user: User):
    """Create authentication token for test user."""
    from src.auth.jwt import create_access_token
    return create_access_token(user_id=test_user.id)


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str):
    """Create authentication headers."""
    return {"Authorization": f"Bearer {auth_token}"}
