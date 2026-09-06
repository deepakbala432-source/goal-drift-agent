from app.database import Base, engine
from app.memory import save_memory, search_memories
from app.config import APP_USER_ID


def test_memory_roundtrip():
    Base.metadata.create_all(bind=engine)

    saved = save_memory(
        APP_USER_ID,
        "I prefer short 45 minute study sessions.",
        "preference",
        4,
    )

    results = search_memories(
        APP_USER_ID,
        "study session preference",
    )

    assert saved["id"] > 0
    assert saved["content"] == "I prefer short 45 minute study sessions."
    assert saved["memory_type"] == "preference"
    assert results
    assert "45 minute" in results[0]["content"]