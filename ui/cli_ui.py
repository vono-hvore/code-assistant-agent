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
            self.send_message(message)
        event.input.value = ""

    def send_message(self, message: str):
        conversation_box = self.query_one("#conversation_box")
        conversation_box.mount(Static(f"{message}", classes="message user"))
        conversation_box.scroll_end(animate=False)

    def send_markdown(self, content: str):
        markdown = Markdown(f"{content}", classes="message agent")
        markdown.code_dark_theme = "textual-dark"
        markdown.code_light_theme = "textual-dark"
        conversation_box = self.query_one("#conversation_box")
        conversation_box.mount(markdown)
        conversation_box.scroll_to_widget(markdown, top=True)

    def loader_start(self):
        conversation_box = self.query_one("#conversation_box")
        conversation_box.mount(self.loader)

    async def loader_stop(self):
        await self.loader.remove()


app = MainApp()
