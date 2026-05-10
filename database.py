from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# here, create a local db file
SQLALQUEMY_DATABASE_URL = "sqlite:///./bpa_plataforma.db"

engine = create_engine(SQLALQUEMY_DATABASE_URL, connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# this function helps to inject the db session in the routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close