from langchain.tools import tool
from app.database import SessionLocal
from app.models import Activity
from app.config import APP_USER_ID

@tool
def log_activity(name: str, category: str = "other", duration: float = 1, notes: str = ""):
    """Log a user activity. Duration is in minutes."""
    db = SessionLocal()
    try:
        a = Activity(
            user_id=APP_USER_ID,
            name=name,
            category=category,
            duration=duration,
            notes=notes,
        )
        db.add(a)
        db.commit()
        db.refresh(a)
        return {
            "success": True,
            "activity_id": a.id,
            "message": f"Logged {name} for {duration} minutes."
        }
    finally:
        db.close()

@tool
def get_recent_activities(limit: int = 30):
    """Retrieve recent activities for the current user."""
    db = SessionLocal()
    try:
        activities = (
            db.query(Activity)
            .filter(Activity.user_id == APP_USER_ID)
            .order_by(Activity.created_at.desc())
            .limit(min(limit, 100))
            .all()
        )
        return [
            {
                "id": a.id, "name": a.name, "category": a.category,
                "duration": a.duration, "notes": a.notes,
                "created_at": str(a.created_at)
            } for a in activities
        ]
    finally:
        db.close()
