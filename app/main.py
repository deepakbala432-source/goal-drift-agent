from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import Goal, Activity, Memory, CalendarEvent
from app.schemas import AgentRequest, GoalCreate, ActivityCreate, MemoryCreate, CalendarEventCreate
from app.agent import run_agent
from app.config import APP_USER_ID
from app.memory import search_memories, save_memory

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Goal Drift Agent",
    version="1.0.0",
    description="A memory-enabled goal alignment agent.",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", include_in_schema=False)
def home():
    return FileResponse("static/index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "user_id": APP_USER_ID}

@app.post("/agent")
def agent_endpoint(request: AgentRequest):
    return run_agent(request.message, request.thread_id)

@app.get("/api/goals")
def goals(db: Session = Depends(get_db)):
    rows = db.query(Goal).filter(
        Goal.user_id == APP_USER_ID
    ).order_by(Goal.created_at.desc()).all()
    return [
        {
            "id": g.id, "title": g.title, "description": g.description,
            "priority": g.priority, "deadline": g.deadline,
            "areas": g.areas, "status": g.status
        } for g in rows
    ]

@app.post("/api/goals")
def add_goal(data: GoalCreate, db: Session = Depends(get_db)):
    g = Goal(user_id=APP_USER_ID, **data.model_dump())
    db.add(g)
    db.commit()
    db.refresh(g)
    return {"id": g.id, "message": "Goal created"}

@app.get("/api/activities")
def activities(db: Session = Depends(get_db)):
    rows = db.query(Activity).filter(
        Activity.user_id == APP_USER_ID
    ).order_by(Activity.created_at.desc()).limit(100).all()
    return [
        {
            "id": a.id, "name": a.name, "category": a.category,
            "duration": a.duration, "notes": a.notes,
            "created_at": str(a.created_at)
        } for a in rows
    ]

@app.post("/api/activities")
def add_activity(data: ActivityCreate, db: Session = Depends(get_db)):
    a = Activity(user_id=APP_USER_ID, **data.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"id": a.id, "message": "Activity logged"}

@app.get("/api/memories")
def memories(db: Session = Depends(get_db)):
    rows = db.query(Memory).filter(
        Memory.user_id == APP_USER_ID,
        Memory.active == True
    ).order_by(Memory.created_at.desc()).limit(100).all()
    return [
        {
            "id": m.id, "content": m.content, "memory_type": m.memory_type,
            "importance": m.importance, "created_at": str(m.created_at)
        } for m in rows
    ]

@app.post("/api/memories")
def add_memory(data: MemoryCreate):
    return save_memory(
        APP_USER_ID, data.content, data.memory_type, data.importance
    )

@app.get("/api/memory/search")
def memory_search(q: str, top_k: int = 5):
    return search_memories(APP_USER_ID, q, top_k)

@app.get("/api/calendar")
def calendar(db: Session = Depends(get_db)):
    rows = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == APP_USER_ID
    ).order_by(CalendarEvent.start_time.asc()).all()
    return [
        {
            "id": e.id, "title": e.title, "start_time": e.start_time,
            "end_time": e.end_time, "notes": e.notes
        } for e in rows
    ]

@app.post("/api/calendar")
def add_calendar(data: CalendarEventCreate, db: Session = Depends(get_db)):
    e = CalendarEvent(user_id=APP_USER_ID, **data.model_dump())
    db.add(e)
    db.commit()
    db.refresh(e)
    return {"id": e.id, "message": "Calendar event added"}
