import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./slopeguard.db")

# SQLite needs check_same_thread=False for use with FastAPI (multiple requests)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Helper to know if we're running on Postgres (full spatial support) vs SQLite
IS_POSTGRES = DATABASE_URL.startswith("postgresql")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()