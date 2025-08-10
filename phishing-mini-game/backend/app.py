from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import random

# ---------------- LEADERBOARDS (kept minimal) ----------------
LEADERBOARDS = {"easy": [], "medium": [], "hard": []}

# ---------------- MODELS ----------------
class Email(BaseModel):
    id: str
    sender: str
    subject: str
    snippet: str
    body: str
    isPhish: bool
    clue: Optional[str] = None  # present only for legit "safe" clue emails

class ProgressUpdate(BaseModel):
    gain: int = 0
    clues: Dict[str, str] = {}
    dayCleared: Optional[int] = None

class ProgressResponse(BaseModel):
    clues: Dict[str, str]
    score: int
    daysCleared: List[int]

# ---------------- STORY DATA (10 DAYS, REALISTIC) ----------------
# Company: Northbridge Labs (northbridgelabs.com)
# Attacker rotates aliases & lookalike domains: northbridqelabs.com, northbr1dgelabs.com
# Recurrent tells in phish: “Sent from MetroLink Wi-Fi.”
# Drop/C2 host across days: vault-sync.app
story_days: List[List[Dict[str, Any]]] = [
    # Day 1 — normal onboarding (all legit)
    [
        dict(
            id="d1e1",
            sender="HR Onboarding <hr@northbridgelabs.com>",
            subject="Welcome to Northbridge Labs",
            snippet="Orientation, desk, and credentials for week one.",
            body="Welcome to Northbridge, Sam Rivers.\nOrientation: Tue 09:00, Floor 4 R-2.\nPlease complete your profile by EOD.\n— HR",
            isPhish=False,
            clue="Legal name on file: Samuel D. Rivers",
        ),
        dict(
            id="d1e2",
            sender="IT Helpdesk <helpdesk@northbridgelabs.com>",
            subject="Your account is ready",
            snippet="Username, SSO, and MFA policy.",
            body="Your username is srivers.\nMFA is required—enroll in the official portal from the office network.\nOpen a ticket for device registration.",
            isPhish=False,
            clue="Username: srivers",
        ),
        dict(
            id="d1e3",
            sender="Facilities <facilities@northbridgelabs.com>",
            subject="Desk & badge pickup",
            snippet="Badge today until 5pm. Desk: 4F—Pod C, seat C-7.",
            body="Badge pickup (Floor 1, Lobby) until 17:00.\nDesk: 4F, Pod C, seat C-7.\nEmergency exit behind the copy room.",
            isPhish=False,
            clue="Desk: 4F C-7",
        ),
        dict(
            id="d1e4",
            sender="Harper Reid <harper.reid@northbridgelabs.com>",
            subject="First-week plan",
            snippet="Welcome to Risk & UX—your first tasks and who to meet.",
            body="Welcome! You’ll sit with Risk & UX.\nDay 2: quick copy audit.\nJoin Slack: #risk-ux and #onboarding.",
            isPhish=False,
            clue="Team: Risk & UX",
        ),
    ],

    # Day 2 — first ominous note (attacker; one sentence; mentions home address)
    [
        dict(
            id="d2e1",
            sender="Security Announcements <sec-announce@northbridgelabs.com>",
            subject="Heads up: lookalike domains active",
            snippet="Watch for northbridqelabs.com and other homographs.",
            body="Threat intel notes homographs targeting staff. Seen: northbridqelabs.com (q-for-g), northbr1dgelabs.com (1-for-i).\nHover links before clicking.",
            isPhish=False,
            clue="Homograph seen: northbridqelabs.com",
        ),
        dict(
            id="d2e2",
            sender="Payroll <payroll@northbridgelabs.com>",
            subject="Direct deposit confirmation",
            snippet="Verify bank ending ••27; reply only if wrong.",
            body="We show bank ending in ••27 for direct deposit. If this is wrong, open a Helpdesk ticket—do not email account numbers.",
            isPhish=False,
            clue="Policy: never email account numbers",
        ),
        dict(
            id="d2e3",
            sender="Customer Desk <support@northbridqelabs.com>",
            subject="Address confirmation",
            snippet="712 Winding Creek Rd, Abilene, TX—correct?",
            body="712 Winding Creek Rd, Abilene, TX—correct?",
            isPhish=True,
        ),
        dict(
            id="d2e4",
            sender="Benefits <benefits@northbridge-support.com>",
            subject="Re-submit insurance forms",
            snippet="Upload via secure link to complete enrollment.",
            body="We need your insurance forms. Upload to our secure portal:\nhttps://vault-sync.app/upload?id=ben-2941",
            isPhish=True,
        ),
    ],

    # Day 3 — escalation; attacker changes name again
    [
        dict(
            id="d3e1",
            sender="Facilities <facilities@northbridgelabs.com>",
            subject="Wi-Fi guest codes",
            snippet="MetroLink vouchers refresh weekly.",
            body="Hosting visitors? Request MetroLink Wi-Fi vouchers from Facilities. Vouchers refresh Mondays at 08:00.",
            isPhish=False,
            clue="Recurring phish footer string: “Sent from MetroLink Wi-Fi.”",
        ),
        dict(
            id="d3e2",
            sender="Alex <alex@northbr1dgelabs.com>",
            subject="Late-night check-in",
            snippet="Nice porch light. Flickers at 2am.",
            body="Nice porch light. Flickers at 2am.",
            isPhish=True,
        ),
        dict(
            id="d3e3",
            sender="IT Threat Intel <intel@northbridgelabs.com>",
            subject="Indicator observed in recent phish",
            snippet="Outbound links are landing on an external drop.",
            body="We’re seeing links eventually land on vault-sync.app. If you see that host, report immediately.",
            isPhish=False,
            clue="C2/drop host: vault-sync.app",
        ),
        dict(
            id="d3e4",
            sender="Drive Share <noreply@drive-share.cloud>",
            subject="Finance-private folder",
            snippet="You were added—open to view invoices.",
            body="Open your shared folder:\nhttps://vault-sync.app/s/finance-private",
            isPhish=True,
        ),
    ],

    # Day 4 — new alias, more pressure
    [
        dict(
            id="d4e1",
            sender="Mia <mia@northbridqelabs.com>",
            subject="Quick confirm",
            snippet="Do you still park behind Building C?",
            body="Do you still park behind Building C?",
            isPhish=True,
        ),
        dict(
            id="d4e2",
            sender="PeopleOps <people@northbridgelabs.com>",
            subject="Directory & profile photo",
            snippet="Preferred name and org visibility updated.",
            body="Preferred name set to Sam; org photo visible.\nIf you didn’t request this, notify PeopleOps.",
            isPhish=False,
            clue="Preferred name: Sam",
        ),
        dict(
            id="d4e3",
            sender="Training <training@northbridgelabs.com>",
            subject="Security onboarding—module 2",
            snippet="Homographs, reply-chain hijack, tracking pixels.",
            body="Module 2 covers homographs, reply-chain theft, and 1×1 tracking pixels.\nComplete by Friday.",
            isPhish=False,
            clue="Topic: reply-chain theft & tracking pixels",
        ),
        dict(
            id="d4e4",
            sender="Box Share <no-reply@box-share.co>",
            subject="CEO shared quarterly financials",
            snippet="Access the folder here.",
            body="Access shared files:\nhttps://vault-sync.app/login/box",
            isPhish=True,
        ),
    ],

    # Day 5 — attacker keeps rotating names
    [
        dict(
            id="d5e1",
            sender="Rowan <rowan@northbridqelabs.com>",
            subject="Standup notes?",
            snippet="Attach them here—need before 9:30.",
            body="Attach them here—need before 9:30:\nhttps://vault-sync.app/upload/notes",
            isPhish=True,
        ),
        dict(
            id="d5e2",
            sender="Calendar <calendar@northbridgelabs.com>",
            subject="Daily standups & Friday retro",
            snippet="Standup 09:30; retro Fridays at 16:00.",
            body="Standup 09:30 daily; sprint retro Friday 16:00.\nInvite added to your calendar.",
            isPhish=False,
            clue="Rituals: Standup 09:30, Retro Fri 16:00",
        ),
        dict(
            id="d5e3",
            sender="Design Systems <design@northbridgelabs.com>",
            subject="Brand reference",
            snippet="Use NB Purple #6B46C1 on banners.",
            body="Use NB Purple #6B46C1 on banners and buttons.\nSee the brand kit on the intranet.",
            isPhish=False,
            clue="Brand color: #6B46C1",
        ),
        dict(
            id="d5e4",
            sender="“Harper R.” <harper.reid@northbridge-alerts.com>",
            subject="Use my backup email",
            snippet="IT systems are down. Send your VPN.",
            body="IT is down. Send your VPN so I can test.",
            isPhish=True,
        ),
    ],

    # Day 6 — personal details; same tell appears
    [
        dict(
            id="d6e1",
            sender="Seth <seth@northbr1dgelabs.com>",
            subject="Door code?",
            snippet="The side entrance keypad near the bike rack.",
            body="What’s the door code by the bike rack?",
            isPhish=True,
        ),
        dict(
            id="d6e2",
            sender="Mentor <lindsay.m@northbridgelabs.com>",
            subject="Copy review partners",
            snippet="You and Taylor handle round one.",
            body="You and Taylor own copy round one.\nShare a draft by Wednesday.",
            isPhish=False,
            clue="Partner: Taylor",
        ),
        dict(
            id="d6e3",
            sender="Helpdesk <helpdesk@northbridgelabs.com>",
            subject="MFA token resynced",
            snippet="You should be able to approve prompts again.",
            body="We resynced your MFA token at 14:14.\nOpen a ticket if prompts fail.",
            isPhish=False,
            clue="MFA token resynced 14:14",
        ),
        dict(
            id="d6e4",
            sender="Printer Queue <print@northbridgelabs.com>",
            subject="Scan-to-mail from MFP-4C",
            snippet="ZIP attachment requires “Enable Content”.",
            body="Scanned ZIP from MFP-4C attached.\nOpen and Enable Content to view.",
            isPhish=True,
        ),
    ],

    # Day 7 — reply-chain theft teased
    [
        dict(
            id="d7e1",
            sender="Lila <lila@northbridqelabs.com>",
            subject="re: payroll export",
            snippet="Quick turn needed before lunch.",
            body="Can you export payroll before lunch?\nSent from MetroLink Wi-Fi.",
            isPhish=True,
        ),
        dict(
            id="d7e2",
            sender="Harper Reid <harper.reid@northbridgelabs.com>",
            subject="Heads up on display-name spoofing",
            snippet="Trust headers, not display names.",
            body="We’re seeing display-name spoofs that look like me.\nCheck domains and headers; don’t send credentials.",
            isPhish=False,
            clue="Tell: display-name spoofing active",
        ),
        dict(
            id="d7e3",
            sender="Benefits <benefits@northbridgelabs.com>",
            subject="Open enrollment reminder",
            snippet="Window closes next week.",
            body="Open enrollment closes next week.\nUse the intranet to enroll; never email SSNs.",
            isPhish=False,
            clue="Policy: never email SSNs",
        ),
        dict(
            id="d7e4",
            sender="“Taylor” <taylor@northbr1dgelabs.com>",
            subject="Need your 2FA code",
            snippet="Locked out right now—send your current code.",
            body="Send your current 2FA code real quick.",
            isPhish=True,
        ),
    ],

    # Day 8 — thread hijack attempt + timing clue
    [
        dict(
            id="d8e1",
            sender="RE: Standup notes <harper.reid@northbridgelabs.com>",
            subject="RE: Standup notes",
            snippet="Attaching… can you confirm your VPN too?",
            body="Attaching notes shortly—also send your VPN to confirm the connection?",
            isPhish=True,
        ),
        dict(
            id="d8e2",
            sender="Security Training <sec-training@northbridgelabs.com>",
            subject="Module 2 passed",
            snippet="Certificate attached.",
            body="Congrats—Module 2 passed.\nBadge: Phish Rookie.",
            isPhish=False,
            clue="Badge earned: Phish Rookie",
        ),
        dict(
            id="d8e3",
            sender="Threat Intel <intel@northbridgelabs.com>",
            subject="Timing pattern in attacker sends",
            snippet="Most messages land between 02:00–03:00 CT.",
            body="We see a consistent window: 02:00–03:00 CT for attacker outbound.\nFlag late-night mail with domain anomalies.",
            isPhish=False,
            clue="Timing: 02:00–03:00 CT",
        ),
        dict(
            id="d8e4",
            sender="Zoom Team <no-reply@zoom-team.cloud>",
            subject="CEO AMA recording",
            snippet="Watch now—SSO required.",
            body="Recording available:\nhttps://vault-sync.app/zoom/recording",
            isPhish=True,
        ),
    ],

    # Day 9 — final pre-boss tells
    [
        dict(
            id="d9e1",
            sender="Nora <nora@northbridqelabs.com>",
            subject="re: reenter credentials",
            snippet="Just use the short link. It’s easier.",
            body="Just reenter your credentials here:\nhttps://vault-sync.app/r/srivers",
            isPhish=True,
        ),
        dict(
            id="d9e2",
            sender="QA <qa@northbridgelabs.com>",
            subject="Copy test score",
            snippet="Anti-phishing copy scored 92%.",
            body="Great work—anti-phishing copy scored 92%.\nWe publish the landing tomorrow.",
            isPhish=False,
            clue="Score: 92%",
        ),
        dict(
            id="d9e3",
            sender="Mentor <lindsay.m@northbridgelabs.com>",
            subject="Final tip before tomorrow",
            snippet="Expect subtle reply-chain + homograph.",
            body="Expect subtlety—reply-chain theft plus a homograph domain is likely.\nCheck Message-ID and return-path.",
            isPhish=False,
            clue="Check Message-ID & return-path",
        ),
        dict(
            id="d9e4",
            sender="HR Forms <forms@northbridge-forms.com>",
            subject="Tax update needed",
            snippet="W-4 correction required; sign today.",
            body="Fix your W-4 here:\nhttps://vault-sync.app/w4/update",
            isPhish=True,
        ),
    ],

    # Day 10 — last day; attacker still hiding behind a new name
    [
        dict(
            id="d10e1",
            sender="Omar <omar@northbridqelabs.com>",
            subject="You won’t piece it together.",
            snippet="Last chance to prove it.",
            body="You won’t piece it together.\nSent from MetroLink Wi-Fi.",
            isPhish=True,
        ),
        dict(
            id="d10e2",
            sender="Helpdesk <helpdesk@northbridgelabs.com>",
            subject="Final tip for headers",
            snippet="Hover links; check DMARC & DKIM alignment.",
            body="Before you report, peek at headers: DMARC alignment failures are decisive.\nHover links to catch homographs.",
            isPhish=False,
            clue="DMARC alignment is decisive",
        ),
        dict(
            id="d10e3",
            sender="Team Ops <ops@northbridgelabs.com>",
            subject="Wrap-up today",
            snippet="Boss evaluation tomorrow.",
            body="Wrap today’s reviews. Boss evaluation tomorrow.\nBring your instincts.",
            isPhish=False,
            clue="Boss eval tomorrow",
        ),
        dict(
            id="d10e4",
            sender="Drive Share <noreply@drive-share.cloud>",
            subject="Private folder",
            snippet="Open now.",
            body="Open the private folder:\nhttps://vault-sync.app/private",
            isPhish=True,
        ),
    ],
]

# (Keep a small finale set if your UI still calls /api/story/finale)
finale_set: List[Dict[str, Any]] = [
    dict(
        id="b1",
        sender="‘Colleague’ <helen.r@northbridqelabs.com>",
        subject="You’ll never piece it together.",
        snippet="Last chance",
        body="Display-name spoof + homograph + odd URL. Report it.",
        isPhish=True,
    ),
    dict(
        id="b2",
        sender="Helpdesk <helpdesk@northbridgelabs.com>",
        subject="Final onboarding tips",
        snippet="Finish strong",
        body="Legit internal note. Finish strong.",
        isPhish=False,
        clue="You did it.",
    ),
]

# ---------------- PROGRESS (in-memory) ----------------
PROGRESS: Dict[str, Any] = {"clues": {}, "score": 0, "daysCleared": []}

# ---------------- APP BOOTSTRAP ----------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- STORY MODE ----------------
@app.get("/api/story/day/{n}", response_model=List[Email])
def get_story_day(n: int):
    if n < 1 or n > len(story_days):
        raise HTTPException(status_code=404, detail="Day not found")
    return story_days[n - 1]

@app.get("/api/story/finale", response_model=List[Email])
def get_finale():
    return finale_set

@app.get("/api/story/progress", response_model=ProgressResponse)
def get_progress():
    return ProgressResponse(
        clues=PROGRESS["clues"], score=PROGRESS["score"], daysCleared=PROGRESS["daysCleared"]
    )

@app.post("/api/story/progress", response_model=ProgressResponse)
def post_progress(update: ProgressUpdate):
    PROGRESS["score"] += update.gain
    for k, v in update.clues.items():
        PROGRESS["clues"][k] = v
    if update.dayCleared and update.dayCleared not in PROGRESS["daysCleared"]:
        PROGRESS["daysCleared"].append(update.dayCleared)
    return ProgressResponse(
        clues=PROGRESS["clues"], score=PROGRESS["score"], daysCleared=PROGRESS["daysCleared"]
    )

# ---------------- QUICK MODE (ACADEMY) ----------------
def _flatten_days(start_inclusive: int, end_inclusive: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for d in range(start_inclusive, end_inclusive + 1):
        out.extend(story_days[d - 1])
    return out

LEVEL_CFG = {
    "easy":   {"days": (1, 3),  "count": 5},   # early days only
    "medium": {"days": (4, 7),  "count": 8},   # mid-arc
    "hard":   {"days": (8, 10), "count": 12},  # late game only
}

def _pick_quick(level: str) -> List[Dict[str, Any]]:
    cfg = LEVEL_CFG.get(level.lower(), LEVEL_CFG["easy"])
    pool = _flatten_days(*cfg["days"])[:]
    random.shuffle(pool)
    # ensure snippets exist
    for e in pool:
        if not e.get("snippet"):
            e["snippet"] = (e.get("body", "")[:120].replace("\n", " ") + "...") if e.get("body") else ""
    return pool[:cfg["count"]]

@app.get("/academy/emails", response_model=List[Email])
def academy_emails(level: str = Query("easy")):
    return _pick_quick(level)

@app.post("/academy/result")
def academy_result(payload: Dict[str, Any]):
    gain = int(payload.get("score", 0))
    PROGRESS["score"] += gain
    return {"ok": True, "score": PROGRESS["score"]}

@app.get("/academy/leaderboard")
def academy_leaderboard(level: str = Query("easy")):
    level = level.lower()
    if level not in LEADERBOARDS:
        raise HTTPException(status_code=400, detail="Invalid level. Use easy, medium, or hard.")
    top = sorted(LEADERBOARDS[level], key=lambda x: x.get("score", 0), reverse=True)[:10]
    return {"level": level, "top": top}

# ---------------- BOSS: SUSPECTS & TASKS (aligned to clues) ----------------
SUSPECTS = [
    {"id": "S1", "name": "Maya Chen",  "title": "Finance Analyst", "dept": "Finance",  "motiveHint": "Invoice access"},
    {"id": "S2", "name": "Elias Kade", "title": "Contractor",      "dept": "IT Ops",   "motiveHint": "Rotating aliases"},
    {"id": "S3", "name": "Taylor Kim", "title": "QA Engineer",     "dept": "Product",  "motiveHint": "Test data"},
    {"id": "S4", "name": "Noah Trent", "title": "Former Employee", "dept": "—",        "motiveHint": "Left last quarter"},
]
TRUE_ATTACKER_ID = "S2"  # Contractor rotating aliases (matches story clues)

BOSS_TASKS_NORMAL = [
    {
        "id": "T1",
        "type": "domain",
        "prompt": "Which is the homograph of northbridgelabs.com used by the attacker?",
        "options": ["northbridqelabs.com", "northbridgelabs.com", "northbridgelabz.com", "north-bridgelabs.com"],
        "ans": 0,
        "why": "q-for-g swap was cited in threat intel.",
    },
    {
        "id": "T2",
        "type": "headers",
        "prompt": "Which header outcome confirms spoofed mail?",
        "options": ["Authentication-Results: dmarc=fail", "Received-SPF: pass", "DKIM-Signature: v=1", "Return-Path matches From"],
        "ans": 0,
        "why": "DMARC fail = spoofed or misaligned sending.",
    },
    {
        "id": "T3",
        "type": "c2",
        "prompt": "Block the attacker’s drop host:",
        "options": ["vault-sync.app", "box-share.co", "zoom-team.cloud", "drive-share.cloud"],
        "ans": 0,
        "why": "Referenced by Threat Intel; used across phish.",
    },
]

BOSS_TASKS_HARD = BOSS_TASKS_NORMAL + [
    {
        "id": "T4",
        "type": "replychain",
        "prompt": "Which is the strongest reply-chain hijack signal?",
        "options": ["Subject starts with 'RE:'", "From matches only display name", "Message-ID domain mismatch", "To contains your name"],
        "ans": 2,
        "why": "Message-ID domain mismatch strongly indicates thread theft.",
    }
]

BOSS_STATE = {"accused": None, "difficulty": "normal", "passed": False}

@app.get("/api/story/suspects")
def get_suspects():
    return [
        {"id": s["id"], "name": s["name"], "title": s["title"], "dept": s["dept"], "motiveHint": s["motiveHint"]}
        for s in SUSPECTS
    ]

@app.post("/api/story/accuse")
def post_accuse(payload: Dict[str, Any]):
    sid = payload.get("suspectId")
    correct = (sid == TRUE_ATTACKER_ID)
    BOSS_STATE["accused"] = sid
    BOSS_STATE["difficulty"] = "normal" if correct else "hard"
    PROGRESS["score"] += (30 if correct else -15)
    return {"correct": correct, "difficulty": BOSS_STATE["difficulty"], "score": PROGRESS["score"]}

@app.get("/api/story/boss/tasks")
def get_boss_tasks():
    diff = BOSS_STATE.get("difficulty", "normal")
    tasks = BOSS_TASKS_NORMAL if diff == "normal" else BOSS_TASKS_HARD
    sanitized = [{"id": t["id"], "type": t["type"], "prompt": t["prompt"], "options": t["options"]} for t in tasks]
    return {"difficulty": diff, "tasks": sanitized}

@app.post("/api/story/boss/submit")
def post_boss_submit(payload: Dict[str, Any]):
    diff = BOSS_STATE.get("difficulty", "normal")
    tasks = BOSS_TASKS_NORMAL if diff == "normal" else BOSS_TASKS_HARD
    answers: List[int] = payload.get("answers", [])
    correct = 0
    feedback = []
    for i, t in enumerate(tasks):
        ok = (i < len(answers) and answers[i] == t["ans"])
        correct += (1 if ok else 0)
        feedback.append({"id": t["id"], "ok": ok, "why": t["why"]})
    need = len(tasks) if diff == "normal" else (len(tasks) - 1)
    passed = (correct >= need)
    BOSS_STATE["passed"] = passed
    PROGRESS["score"] += (50 if passed else 0)
    return {"passed": passed, "correct": correct, "total": len(tasks), "feedback": feedback, "score": PROGRESS["score"]}
