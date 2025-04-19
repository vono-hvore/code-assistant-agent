from ui.cli_ui import app
from dotenv import load_dotenv
import logging
import warnings
import asyncio
from core.runner import runner


async def main():
    app.run()

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
                app.send_markdown(final_response_text)


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.ERROR)
    load_dotenv()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
