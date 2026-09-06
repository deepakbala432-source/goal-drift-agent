# Project Guide

## Core use case

The agent answers:

> Am I spending my time in a way that supports my long-term goals?

## Tools

1. create_goal
2. get_goals
3. archive_goal
4. log_activity
5. get_recent_activities
6. remember
7. recall
8. forget_memory
9. add_calendar_event
10. get_calendar_events
11. analyze_goal_drift
12. create_recovery_plan

## Memory

Structured persistence:
- goals
- activities
- memories
- calendar events
- agent thread state during a running process

Semantic-ish memory:
- local TF-IDF vectors
- cosine similarity
- top-k retrieval

For production, replace the TF-IDF layer with a real embedding model/vector database.

## Demo flow

1. Create a goal.
2. Log several goal-related and unrelated activities.
3. Save a preference.
4. Ask the agent to analyze drift.
5. Ask what it remembers.
6. Ask for a recovery plan.

## Interview explanation

The LLM is the reasoning layer. LangChain exposes Python functions as tools. LangGraph manages the agent loop and conversation state. OpenRouter supplies the model. SQLite stores persistent application data. The memory layer retrieves relevant past user information. The drift tool calculates an alignment/trend signal. The LLM converts those structured results into a personalized explanation.
