from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from src.config.config import DATABASE_URL

DATABASE_URL =  DATABASE_URL

engine = create_engine(DATABASE_URL)  # ✅ Sync engine
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
