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
    future = asyncio.Future()

    async def handle_approval_response(message):
        response = message.strip().lower()
        if not future.done():  # Check if future is not already done
            future.set_result(response)

    prev_handler = app.input_handler
    app.input_handler = handle_approval_response
    result = await future
    return result


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
