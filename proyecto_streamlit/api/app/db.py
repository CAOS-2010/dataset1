from sqlalchemy import create_engine
from pathlib import Path

DB_FILE = Path(__file__).resolve().parents[2] / "data" / "students.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
