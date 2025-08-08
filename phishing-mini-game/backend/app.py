from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from sqlmodel import select, Session

from database import create_db_and_tables, get_session, engine
from models import EmailTemplate, AcademyResult

app = FastAPI()

# CORS: localhost + Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000","http://localhost:3001",
        "http://127.0.0.1:3000","http://127.0.0.1:3001",
        "https://*.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

# -------- sample data + seed helpers ----------
_SAMPLES = [
    ("easy","admin@bank.com","Verify your account","Click here to update…",True),
    ("easy","newsletter@shop.com","Your weekly deals","Check out our latest offers",False),
    ("easy","security@service.com","Password reset","We detected a login…",True),
    ("easy","friend@example.com","Lunch tomorrow?","Hey, want to grab…",False),
    ("easy","alerts@store.com","Order shipped!","Your package is on the way",False),
    ("medium","support@micros0ft.com","Unusual sign-in activity","Review the IP address immediately",True),
    ("medium","hr@company.com","Updated handbook","Please acknowledge receipt",False),
    ("medium","it-helpdesk@corp.com","Urgent: MFA reset","Use the attachment to re-enroll",True),
    ("medium","events@meetup.com","Tonight’s event reminder","Starts at 6pm—see you there!",False),
    ("medium","payroll@corp.com","Direct deposit failed","Confirm account within 24h",True),
    ("hard","ceo@company.com","Quick favor","Are you at your desk right now?",True),
    ("hard","noreply@github.com","Security alert for your account","Token used from new location",False),
    ("hard","vendor@invoices.io","Invoice 8471 due","PO attached—please process",True),
    ("hard","ops@cloudprovider.com","Maintenance window notice","No action required",False),
    ("hard","legal@corp.com","Policy acknowledgement overdue","Sign by EOD to remain compliant",True),
]

def seed_if_empty() -> Dict[str, int]:
    """Insert sample templates if table is empty; return per-level counts."""
    with Session(engine) as session:
        exists = session.exec(select(EmailTemplate)).first()
        if not exists:
            session.add_all([
                EmailTemplate(level=l, sender=s, subject=sub, snippet=snip, is_phish=ph)
                for (l, s, sub, snip, ph) in _SAMPLES
            ])
            session.commit()
        # return counts
        out = {}
        for lvl in ("easy", "medium", "hard"):
            out[lvl] = session.exec(
                select(EmailTemplate).where(EmailTemplate.level == lvl)
            ).count()
        return out
# ---------------------------------------------

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_if_empty()

# debug helpers
@app.get("/debug/counts")
def debug_counts():
    return seed_if_empty()

@app.post("/debug/seed")
def debug_seed():
    return seed_if_empty()

@app.get("/academy/emails", response_model=List[EmailTemplate])
def get_emails(level: str = "easy", session=Depends(get_session)):
    results = session.exec(
        select(EmailTemplate).where(EmailTemplate.level == level)
    ).all()
    if not results:
        raise HTTPException(404, "No templates for this level")
    return results

@app.post("/academy/results", response_model=AcademyResult)
def post_result(result: AcademyResult, session=Depends(get_session)):
    session.add(result)
    session.commit()
    session.refresh(result)
    return result
