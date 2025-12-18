"""Database initialization script."""
from .connection import create_db_and_tables


def main():
    """Initialize database and create all tables."""
    print("Creating database tables...")
    create_db_and_tables()
    print("✓ Database tables created successfully!")


if __name__ == "__main__":
    main()
