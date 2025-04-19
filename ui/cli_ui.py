from textual.app import App, ComposeResult
from textual.widgets import (
    LoadingIndicator,
    Static,
    Input,
    Markdown,
)
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive
from textual.message import Message
from resources.skynet_logo import skynet_logo


class ChatMessage(Message):
    def __init__(self, content: str):
        self.content = content
        super().__init__()


class MainApp(App):
    CSS_PATH = "../resources/styles.css"
    loader = LoadingIndicator(id="loading")
    chat_log = reactive("")

    @property
    def input_handler(self):
        return self._input_handler

    @input_handler.setter
    def input_handler(self, handler):
        self._input_handler = handler

    def on_mount(self) -> None:
        self.theme = "textual-ansi"

    def compose(self) -> ComposeResult:
        with Container(id="ascii-art-container"):
            yield Static(skynet_logo, id="ascii-art")
        with Container(id="conversation_box_centered"):
            yield VerticalScroll(id="conversation_box")
        with Container(id="input_box"):
            yield Input(
                placeholder="Type a message and press Enter...", id="message_input"
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        if message:
            self.run_worker(self.input_handler(message), exclusive=True)
        event.input.value = ""

    def send_message(self, message: str, mode: str = "user"):
        conversation_box = self.query_one("#conversation_box")
        conversation_box.mount(Static(f"{message}", classes=f"message {mode}"))
        conversation_box.scroll_end(animate=False)

    def send_markdown(self, content: str, mode: str = "agent"):
        markdown = Markdown(f"{content}", classes=f"message {mode}")
        markdown.code_dark_theme = "textual-dark"
        markdown.code_light_theme = "textual-dark"
        conversation_box = self.query_one("#conversation_box")
        conversation_box.mount(markdown)
        conversation_box.scroll_to_widget(markdown)

    def loader_start(self):
        conversation_box = self.query_one("#conversation_box")
        conversation_box.mount(self.loader)

    async def loader_stop(self):
        await self.loader.remove()
