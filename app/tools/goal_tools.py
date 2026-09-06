from langchain.tools import tool
from app.database import SessionLocal
from app.models import Goal
from app.config import APP_USER_ID

@tool
def create_goal(title: str, description: str = "", priority: str = "medium",
                deadline: str = "", areas: str = ""):
    """Create a long-term goal for the current user."""
    db = SessionLocal()
    try:
        g = Goal(
            user_id=APP_USER_ID,
            title=title,
            description=description,
            priority=priority,
            deadline=deadline,
            areas=areas,
        )
        db.add(g)
        db.commit()
        db.refresh(g)
        return {"success": True, "goal_id": g.id, "message": f"Created goal: {title}"}
    finally:
        db.close()

@tool
def get_goals(include_archived: bool = False):
    """Retrieve the current user's goals."""
    db = SessionLocal()
    try:
        q = db.query(Goal).filter(Goal.user_id == APP_USER_ID)
        if not include_archived:
            q = q.filter(Goal.status == "active")
        goals = q.order_by(Goal.created_at.desc()).all()
        return [
            {
                "id": g.id, "title": g.title, "description": g.description,
                "priority": g.priority, "deadline": g.deadline,
                "areas": g.areas, "status": g.status
            } for g in goals
        ]
    finally:
        db.close()

@tool
def archive_goal(goal_id: int):
    """Archive a goal when the user explicitly wants to stop pursuing it."""
    db = SessionLocal()
    try:
        g = db.query(Goal).filter(
            Goal.id == goal_id, Goal.user_id == APP_USER_ID
        ).first()
        if not g:
            return {"success": False, "message": "Goal not found."}
        g.status = "archived"
        db.commit()
        return {"success": True, "message": f"Archived goal: {g.title}"}
    finally:
        db.close()
