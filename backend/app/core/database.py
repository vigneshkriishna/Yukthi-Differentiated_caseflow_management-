"""
Database configuration and setup
"""
from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings


# Create database engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite specific settings
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL settings
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO
    )


def create_db_and_tables():
    """Create database and tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
