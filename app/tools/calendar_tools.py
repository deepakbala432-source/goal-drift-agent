from langchain.tools import tool
from app.database import SessionLocal
from app.models import CalendarEvent
from app.config import APP_USER_ID

@tool
def add_calendar_event(title: str, start_time: str, end_time: str = "", notes: str = ""):
    """Store a simple calendar event using user-provided date/time text."""
    db = SessionLocal()
    try:
        e = CalendarEvent(
            user_id=APP_USER_ID,
            title=title,
            start_time=start_time,
            end_time=end_time,
            notes=notes,
        )
        db.add(e)
        db.commit()
        db.refresh(e)
        return {"success": True, "event_id": e.id, "message": f"Added event: {title}"}
    finally:
        db.close()

@tool
def get_calendar_events():
    """Retrieve stored calendar events for the current user."""
    db = SessionLocal()
    try:
        events = (
            db.query(CalendarEvent)
            .filter(CalendarEvent.user_id == APP_USER_ID)
            .order_by(CalendarEvent.start_time.asc())
            .all()
        )
        return [
            {
                "id": e.id, "title": e.title, "start_time": e.start_time,
                "end_time": e.end_time, "notes": e.notes
            } for e in events
        ]
    finally:
        db.close()
