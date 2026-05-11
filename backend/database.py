# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a local db file
SQLALCHEMY_DATABASE_URL = "sqlite:///./bpa_platform.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This function helps to inject the db session in the routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()