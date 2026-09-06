from datetime import datetime, timedelta
from langchain.tools import tool
from app.database import SessionLocal
from app.models import Goal, Activity
from app.config import APP_USER_ID

def tokens(text):
    return {
        x.strip(".,:;!?()[]{}").lower()
        for x in text.split() if len(x) > 2
    }

def score_goal(goal, activities):
    goal_words = tokens(" ".join([
        goal.title, goal.description or "", goal.areas or ""
    ]))
    related = 0.0
    total = 0.0
    evidence = []

    for a in activities:
        total += a.duration
        words = tokens(f"{a.name} {a.category} {a.notes or ''}")
        overlap = goal_words.intersection(words)
        if overlap:
            related += a.duration
            evidence.append(
                f"{a.name}: {a.duration} min; matched {', '.join(sorted(overlap))}"
            )

    score = (related / total * 100) if total else 0
    return score, related, total, evidence

@tool
def analyze_goal_drift(goal_id: int):
    """Analyze goal alignment, recent trend, and evidence for a stored goal."""
    db = SessionLocal()
    try:
        goal = db.query(Goal).filter(
            Goal.id == goal_id, Goal.user_id == APP_USER_ID
        ).first()
        if not goal:
            return {"error": "Goal not found."}

        now = datetime.utcnow()
        recent_cutoff = now - timedelta(days=7)
        previous_cutoff = now - timedelta(days=14)

        recent = db.query(Activity).filter(
            Activity.user_id == APP_USER_ID,
            Activity.created_at >= recent_cutoff
        ).all()

        previous = db.query(Activity).filter(
            Activity.user_id == APP_USER_ID,
            Activity.created_at >= previous_cutoff,
            Activity.created_at < recent_cutoff
        ).all()

        score, related, total, evidence = score_goal(goal, recent)
        previous_score, _, _, _ = score_goal(goal, previous)
        change = round(score - previous_score, 2)

        if not recent:
            drift = "unknown"
        elif score >= 70 and change >= -10:
            drift = "low"
        elif score >= 40:
            drift = "moderate"
        else:
            drift = "high"

        trend = "improving" if change > 5 else "declining" if change < -5 else "stable"

        return {
            "goal": goal.title,
            "goal_id": goal.id,
            "alignment_score": round(score, 2),
            "previous_week_score": round(previous_score, 2),
            "trend": trend,
            "score_change": change,
            "drift_level": drift,
            "related_minutes": round(related, 2),
            "total_minutes": round(total, 2),
            "evidence": evidence[:10],
            "deadline": goal.deadline,
        }
    finally:
        db.close()
