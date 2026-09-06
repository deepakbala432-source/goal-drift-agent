from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .database import SessionLocal
from .models import Memory

def save_memory(user_id, content, memory_type="fact", importance=3):
    db = SessionLocal()
    try:
        m = Memory(
            user_id=user_id,
            content=content.strip(),
            memory_type=memory_type,
            importance=importance,
        )
        db.add(m)
        db.commit()
        db.refresh(m)
        return {
            "id": m.id,
            "content": m.content,
            "memory_type": m.memory_type,
            "importance": m.importance,
        }
    finally:
        db.close()

def search_memories(user_id, query, top_k=5):
    db = SessionLocal()
    try:
        memories = (
            db.query(Memory)
            .filter(Memory.user_id == user_id, Memory.active == True)
            .order_by(Memory.importance.desc(), Memory.created_at.desc())
            .all()
        )
        if not memories:
            return []

        corpus = [query] + [m.content for m in memories]
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(corpus)
        scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

        ranked = sorted(
            zip(memories, scores),
            key=lambda x: (x[1], x[0].importance),
            reverse=True,
        )[:top_k]

        return [
            {
                "id": m.id,
                "content": m.content,
                "memory_type": m.memory_type,
                "importance": m.importance,
                "similarity": round(float(score), 3),
            }
            for m, score in ranked if score > 0
        ]
    finally:
        db.close()

def delete_memory(user_id, memory_id):
    db = SessionLocal()
    try:
        m = db.query(Memory).filter(
            Memory.id == memory_id,
            Memory.user_id == user_id
        ).first()
        if not m:
            return False
        m.active = False
        db.commit()
        return True
    finally:
        db.close()
