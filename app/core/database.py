import os
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

# BASE_DIR is now the project root (two levels up from app/core/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "db"
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "np_case_trainer.db"
sqlite_url = f"sqlite:///{DB_FILE}"

# Connect args needed for SQLite
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)

def init_db():
    # Import models here to ensure they are registered with SQLModel metadata
    from app.models.case_study import CaseStudy
    from app.models.case_session import CaseStudySession

    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session