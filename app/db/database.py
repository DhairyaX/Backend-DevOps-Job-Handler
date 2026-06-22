from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# engine is the core interface to the database. It handles the actual connection.
engine = create_engine(settings.DATABASE_URL)

# SessionLocal class will be a database session factory.
# When we create an instance of this, it represents a single connection session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models to inherit from.
# All our models will be subclasses of this Base.
Base = declarative_base()

# Dependency to get the database session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
