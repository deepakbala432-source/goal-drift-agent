from langchain.tools import tool
from app.database import SessionLocal
from app.models import Goal, Activity
from app.config import APP_USER_ID

@tool
def create_recovery_plan(goal_id: int, daily_minutes: int = 60):
    """Create a simple recovery plan from a stored goal and recent activity."""
    db = SessionLocal()
    try:
        goal = db.query(Goal).filter(
            Goal.id == goal_id, Goal.user_id == APP_USER_ID
        ).first()
        if not goal:
            return {"error": "Goal not found."}

        areas = [x.strip() for x in (goal.areas or "").split(",") if x.strip()]
        if not areas:
            areas = [goal.title]

        per_area = max(15, daily_minutes // min(len(areas), 3))
        plan = [
            {
                "focus": area,
                "minutes": per_area,
                "reason": "Prioritize a clearly relevant goal area."
            }
            for area in areas[:3]
        ]

        return {
            "goal": goal.title,
            "deadline": goal.deadline,
            "daily_minutes": daily_minutes,
            "plan": plan,
            "note": "Start small and adjust based on real progress."
        }
    finally:
        db.close()
