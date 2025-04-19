from src.agents import root_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

APP_NAME = "Code Assistance Agent"
USER_ID = "user_1"
SESSION_ID = "session_1"

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

runner = Runner(
    app_name=APP_NAME,
    session_service=session_service,
    agent=root_agent,
)

# Export these variables for use in main.py
__all__ = ["runner", "USER_ID", "SESSION_ID", "APP_NAME"]
