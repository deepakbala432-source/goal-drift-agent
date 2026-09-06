from uuid import uuid4

from langchain_openrouter import ChatOpenRouter
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL, MAX_TOKENS
from app.prompts import SYSTEM_PROMPT
from app.tools.goal_tools import create_goal, get_goals, archive_goal
from app.tools.activity_tools import log_activity, get_recent_activities
from app.tools.memory_tools import remember, recall, forget_memory
from app.tools.calendar_tools import add_calendar_event, get_calendar_events
from app.tools.drift_tools import analyze_goal_drift
from app.tools.planner_tools import create_recovery_plan

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is missing. Create .env from .env.example."
    )

model = ChatOpenRouter(
    model=OPENROUTER_MODEL,
    temperature=0,
    max_tokens=MAX_TOKENS,
    max_retries=2,
)

tools = [
    create_goal,
    get_goals,
    archive_goal,
    log_activity,
    get_recent_activities,
    remember,
    recall,
    forget_memory,
    add_calendar_event,
    get_calendar_events,
    analyze_goal_drift,
    create_recovery_plan,
]

checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)

def run_agent(user_message: str, thread_id: str | None = None):
    thread_id = thread_id or str(uuid4())

    print("\n================ GOAL DRIFT AGENT ================")
    print("USER:", user_message)

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        config={"configurable": {"thread_id": thread_id}},
    )

    print("\nAGENT TRACE:")
    for message in result.get("messages", []):
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            for call in tool_calls:
                print("TOOL CALLED:", call.get("name"))
                print("ARGUMENTS:", call.get("args"))
        if getattr(message, "type", None) == "tool":
            print("TOOL RESULT:", message.content)
    print("===================================================\n")

    return {
        "thread_id": thread_id,
        "response": result["messages"][-1].content,
    }
