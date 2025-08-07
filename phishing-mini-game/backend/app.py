# app.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlmodel import select

from database import create_db_and_tables, get_session
from models import EmailTemplate, AcademyResult

app = FastAPI()

# CORS for your local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/academy/emails", response_model=List[EmailTemplate])
def get_emails(level: str = "easy", session=Depends(get_session)):
    statement = select(EmailTemplate).where(EmailTemplate.level == level)
    results = session.exec(statement).all()
    if not results:
        raise HTTPException(404, "No templates for this level")
    return results

@app.post("/academy/results", response_model=AcademyResult)
def post_result(result: AcademyResult, session=Depends(get_session)):
    session.add(result)
    session.commit()
    session.refresh(result)
    return result
