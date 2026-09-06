from pydantic import BaseModel, Field
from typing import Optional

class AgentRequest(BaseModel):
    message: str = Field(min_length=1)
    thread_id: Optional[str] = None

class GoalCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"
    deadline: str = ""
    areas: str = ""

class ActivityCreate(BaseModel):
    name: str
    category: str = "other"
    duration: float = Field(gt=0)
    notes: str = ""

class MemoryCreate(BaseModel):
    content: str
    memory_type: str = "fact"
    importance: int = Field(default=3, ge=1, le=5)

class CalendarEventCreate(BaseModel):
    title: str
    start_time: str
    end_time: str = ""
    notes: str = ""
