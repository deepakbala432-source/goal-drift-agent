from langchain.tools import tool
from app.memory import save_memory, search_memories, delete_memory
from app.config import APP_USER_ID

@tool
def remember(content: str, memory_type: str = "fact", importance: int = 3):
    """Save a durable user fact, preference, decision, reason, pattern, or goal context."""
    return save_memory(APP_USER_ID, content, memory_type, importance)

@tool
def recall(query: str, top_k: int = 5):
    """Search the user's persistent memories using local TF-IDF similarity."""
    return search_memories(APP_USER_ID, query, top_k)

@tool
def forget_memory(memory_id: int):
    """Deactivate a stored memory when the user asks to forget it."""
    return {"success": delete_memory(APP_USER_ID, memory_id), "memory_id": memory_id}
