# models.py
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class EmailTemplate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    level: str                  # "easy", "medium", "hard"
    sender: str
    subject: str
    snippet: str
    is_phish: bool

class AcademyResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    level: str
    score: int
    total: int
    answered: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
