# seed.py
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import EmailTemplate

SAMPLES = [
    # EASY (5)
    ("easy","admin@bank.com","Verify your account","Click here to update…",True),
    ("easy","newsletter@shop.com","Your weekly deals","Check out our latest offers",False),
    ("easy","security@service.com","Password reset","We detected a login…",True),
    ("easy","friend@example.com","Lunch tomorrow?","Hey, want to grab…",False),
    ("easy","alerts@store.com","Order shipped!","Your package is on the way",False),
    # MEDIUM (5)
    ("medium","support@micros0ft.com","Unusual sign-in activity","Review the IP address immediately",True),
    ("medium","hr@company.com","Updated handbook","Please acknowledge receipt",False),
    ("medium","it-helpdesk@corp.com","Urgent: MFA reset","Use the attachment to re-enroll",True),
    ("medium","events@meetup.com","Tonight’s event reminder","Starts at 6pm—see you there!",False),
    ("medium","payroll@corp.com","Direct deposit failed","Confirm account within 24h",True),
    # HARD (5)
    ("hard","ceo@company.com","Quick favor","Are you at your desk right now?",True),
    ("hard","noreply@github.com","Security alert for your account","Token used from new location",False),
    ("hard","vendor@invoices.io","Invoice 8471 due","PO attached—please process",True),
    ("hard","ops@cloudprovider.com","Maintenance window notice","No action required",False),
    ("hard","legal@corp.com","Policy acknowledgement overdue","Sign by EOD to remain compliant",True),
]

def seed():
    create_db_and_tables()
    with Session(engine) as session:
        # If already seeded, bail out
        already = session.exec(select(EmailTemplate)).first()
        if already:
            print("✅ Templates already present; skipping.")
            return
        session.add_all([
            EmailTemplate(level=l,sender=s,subject=sub,snippet=snip,is_phish=ph)
            for (l,s,sub,snip,ph) in SAMPLES
        ])
        session.commit()
        print("✅ Seeded 15 email templates (5 per level).")

if __name__ == "__main__":
    seed()
