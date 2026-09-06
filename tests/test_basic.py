from app.memory import save_memory, search_memories
from app.config import APP_USER_ID

def test_memory_roundtrip():
    saved = save_memory(
        APP_USER_ID,
        "I prefer short 45 minute study sessions.",
        "preference",
        4,
    )
    assert saved["id"] > 0

    results = search_memories(APP_USER_ID, "study session preference")
    assert results
    assert "45 minute" in results[0]["content"]
