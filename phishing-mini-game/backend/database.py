# database.py
import os
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel, Session

load_dotenv()  # reads DATABASE_URL from .env

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
