from ui.cli_ui import MainApp, ChatMessage
from src.tools import approval_handler, log_handler
import src.tools as tools
from dotenv import load_dotenv
import logging
import warnings
from src.runner import runner, USER_ID, SESSION_ID
from google.genai import types
import asyncio


async def process_message(message: str):
    app.send_message(f"You: {message}")
    app.loader_start()
    try:
        content = types.Content(role="user", parts=[types.Part(text=message)])
        final_response_text = "No response received."
        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                app.send_markdown(f"T-800: {final_response_text}")
                await app.loader_stop()
    except Exception as e:
        app.send_message(f"Error: {str(e)}", mode="error")
        raise e
    finally:
        await app.loader_stop()


async def get_approval():
    approval_future = asyncio.Future()

    def handle_approval_response(message):
        response = message.strip().lower()
        approval_future.set_result(response)

    original_handler = app.input_handler

    app.input_handler = handle_approval_response
    app.send_message(
        "⚠️ APPROVAL REQUIRED: Type 'yes' to approve or anything else to reject",
        mode="agent",
    )
    try:
        response = await approval_future
        return response
    finally:
        app.input_handler = original_handler


def process_log(message: str):
    app.send_message(message, mode="log")


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.ERROR)
    load_dotenv()

    app = MainApp()
    app.input_handler = process_message
    tools.approval_handler = get_approval
    tools.log_handler = process_log
    app.run()
