"""Unit tests for chat service."""
import pytest
from sqlmodel import Session
from uuid import uuid4

from src.services.ai.chat_service import ChatService
from src.models import User, ChatSession, ChatMessage, MessageType


class TestChatService:
    """Test suite for ChatService class."""

    @pytest.fixture
    def chat_service(self, db_session: Session, test_user: User):
        """Create a ChatService instance."""
        return ChatService(user_id=test_user.id, db_session=db_session)

    def test_get_or_create_session_creates_new(self, chat_service: ChatService, db_session: Session):
        """Test creating a new chat session."""
        session = chat_service.get_or_create_session()

        assert session is not None
        assert session.user_id == chat_service.user_id
        assert session.active is True
        assert session.message_count == 0

    def test_get_or_create_session_reuses_active(self, chat_service: ChatService, db_session: Session):
        """Test reusing an active chat session."""
        session1 = chat_service.get_or_create_session()
        session2 = chat_service.get_or_create_session()

        assert session1.session_id == session2.session_id

    def test_save_message_user_type(self, chat_service: ChatService, db_session: Session):
        """Test saving a user message."""
        session = chat_service.get_or_create_session()
        content = "Add buy groceries task"

        message = chat_service.save_message(
            session_id=session.session_id,
            message_type=MessageType.USER_MESSAGE,
            content=content
        )

        assert message.content == content
        assert message.type == MessageType.USER_MESSAGE
        assert message.session_id == session.session_id

    def test_save_message_ai_type(self, chat_service: ChatService, db_session: Session):
        """Test saving an AI response message."""
        session = chat_service.get_or_create_session()
        content = "I'll create that task for you."

        message = chat_service.save_message(
            session_id=session.session_id,
            message_type=MessageType.AI_RESPONSE,
            content=content
        )

        assert message.content == content
        assert message.type == MessageType.AI_RESPONSE

    def test_save_message_increments_count(self, chat_service: ChatService, db_session: Session):
        """Test that saving messages increments session message count."""
        session = chat_service.get_or_create_session()
        initial_count = session.message_count

        chat_service.save_message(
            session_id=session.session_id,
            message_type=MessageType.USER_MESSAGE,
            content="Test message"
        )

        db_session.refresh(session)
        assert session.message_count == initial_count + 1

    def test_get_session_messages(self, chat_service: ChatService, db_session: Session):
        """Test retrieving messages for a session."""
        session = chat_service.get_or_create_session()

        # Add multiple messages
        chat_service.save_message(session.session_id, MessageType.USER_MESSAGE, "Message 1")
        chat_service.save_message(session.session_id, MessageType.AI_RESPONSE, "Response 1")
        chat_service.save_message(session.session_id, MessageType.USER_MESSAGE, "Message 2")

        messages = chat_service.get_session_messages(session.session_id, limit=10)

        assert len(messages) == 3
        assert messages[0].content == "Message 1"  # Chronological order
        assert messages[1].content == "Response 1"
        assert messages[2].content == "Message 2"

    def test_get_session_messages_pagination(self, chat_service: ChatService, db_session: Session):
        """Test message pagination."""
        session = chat_service.get_or_create_session()

        # Add 5 messages
        for i in range(5):
            chat_service.save_message(
                session.session_id,
                MessageType.USER_MESSAGE,
                f"Message {i}"
            )

        # Get first 3
        messages_page1 = chat_service.get_session_messages(session.session_id, limit=3, offset=0)
        # Get next 2
        messages_page2 = chat_service.get_session_messages(session.session_id, limit=3, offset=3)

        assert len(messages_page1) == 3
        assert len(messages_page2) == 2
        assert messages_page1[0].content == "Message 0"
        assert messages_page2[0].content == "Message 3"

    def test_user_isolation(self, db_session: Session, test_user: User):
        """Test that sessions are isolated per user."""
        user1_service = ChatService(user_id=test_user.id, db_session=db_session)

        # Create another user
        user2 = User(
            email="user2@example.com",
            hashed_password="hashed",
            display_name="User 2"
        )
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user2)

        user2_service = ChatService(user_id=user2.id, db_session=db_session)

        session1 = user1_service.get_or_create_session()
        session2 = user2_service.get_or_create_session()

        assert session1.user_id != session2.user_id
        assert session1.session_id != session2.session_id
