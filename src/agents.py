from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool

from src.tools import (
    delete_file,
    edit_file,
    external_approval_tool,
    read_file,
    read_folder,
    search_files,
)


LLM_MODEL = "claude-3-5-sonnet-20241022"

approval_tool = FunctionTool(func=external_approval_tool)

request_approval = LlmAgent(
    name="RequestHumanApproval",
    instruction="Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].",
    tools=[approval_tool],
    output_key="human_decision",
)

prepare_request = LlmAgent(
    name="PrepareApproval",
    instruction="Prepare the approval request details based on user input. Store amount and reason in state.",
)

process_decision = LlmAgent(
    name="ProcessDecision",
    instruction="Check state key 'human_decision'. If 'approved', proceed. If 'rejected', inform user.",
)

root_agent = LlmAgent(
    name="code_assistance",
    model=LiteLlm(model="claude-3-5-sonnet-20241022"),
    description=("An agent that helps refactor code with provided codebase."),
    instruction=(
        "You are a professional code assistant."
        "You can read folder structure and load it to your memmory"
        "You can reaactor codes"
        "You can edit files"
        "You can read files"
        "You can delete files"
        "Before Delete or Edit ask it aprove that type of action"
    ),
    tools=[
        read_folder,
        edit_file,
        read_file,
        delete_file,
        search_files,
    ],
    sub_agents=[request_approval, prepare_request, process_decision],
)
