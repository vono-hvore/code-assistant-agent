from ui.cli_ui import MainApp
from dotenv import load_dotenv
import logging
import warnings
from src.runner import runner, USER_ID, SESSION_ID
from google.genai import types


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


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.ERROR)
    load_dotenv()

    app = MainApp()
    app.input_handler = process_message
    app.run()
