import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4.1-mini")
APP_USER_ID = os.getenv("APP_USER_ID", "demo-user")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
