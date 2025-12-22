"""Seed default UserPreferences and AIContext for existing users."""
from sqlmodel import Session, select
from ..models import User, UserPreferences, AIContext
from .connection import engine


def seed_ai_defaults() -> None:
    """
    Create default UserPreferences and AIContext records for all existing users.

    This script should be run after the Phase 3 migration to ensure all users
    have the necessary AI-related records.
    """
    with Session(engine) as session:
        # Get all existing users
        users = session.exec(select(User)).all()

        created_preferences = 0
        created_contexts = 0

        for user in users:
            # Check if user already has preferences
            existing_prefs = session.exec(
                select(UserPreferences).where(UserPreferences.user_id == user.id)
            ).first()

            if not existing_prefs:
                # Create default preferences
                user_prefs = UserPreferences(
                    user_id=user.id,
                    preferred_language="en",
                    ai_tone="professional",
                    enable_proactive_suggestions=False,
                    learned_shortcuts={},
                    ai_features_enabled=True
                )
                session.add(user_prefs)
                created_preferences += 1

            # Check if user already has AI context
            existing_context = session.exec(
                select(AIContext).where(AIContext.user_id == user.id)
            ).first()

            if not existing_context:
                # Create default AI context
                ai_context = AIContext(
                    user_id=user.id,
                    conversation_summary=None,
                    user_patterns={},
                    total_messages=0,
                    total_sessions=0,
                    average_session_length=0.0
                )
                session.add(ai_context)
                created_contexts += 1

        # Commit all changes
        session.commit()

        print(f"✓ Created {created_preferences} UserPreferences records")
        print(f"✓ Created {created_contexts} AIContext records")
        print(f"✓ Seed completed for {len(users)} total users")


if __name__ == "__main__":
    print("Seeding default AI records for existing users...")
    seed_ai_defaults()
    print("Done!")
