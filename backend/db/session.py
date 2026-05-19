from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from backend.core.config import settings
import sys

if settings.APP_ENV == "production" and "sqlite" in settings.DATABASE_URL:
    print("FATAL: Cannot use SQLite in production APP_ENV. Set a PostgreSQL DATABASE_URL.", file=sys.stderr)
    sys.exit(1)

connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
