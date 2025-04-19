from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool

from core.tools import (
    delete_file,
    edit_file,
    external_approval_tool,
    read_file,
    read_folder,
    search_files,
)


LLM_MODEL = "claude-3-5-sonnet-20241022"

approval_tool = FunctionTool(func=external_approval_tool)

request_approval_agent = LlmAgent(
    name="RequestHumanApproval",
    instruction="""
        Use the external_approval_tool with amount from state['approva_amount'] and rease from state['approval_reason'].
        """,
    tools=[approval_tool],
    output_key="human_decision",
)

prepare_request_agent = LlmAgent(
    name="PrepareApproval",
    instruction="""
        Prepare the approval request details based on user input.
        Store amount and reason in state
        """,
)

process_decision = LlmAgent(
    name="ProcessDecision",
    instruction="""
        Check state key 'human_decision'. If approved, proceed.
        If 'rejected', inform user.
        """,
)

root_agent = LlmAgent(
    name="CodeAssistance",
    model=LiteLlm(model=LLM_MODEL),
    description="An agent that helps refactor code base on provided codebase",
    instruction="""
    Analyze codebase, architecture, of project.
    Read folder structure and load it to your memmory.
    Refactor code.
    Edit file.
    Read file.
    Print file content.
    Delete file.
    Before Delete or Edit actions ask user approval.
    """,
    tools=[read_folder, edit_file, read_file, delete_file, search_files],
    sub_agents=[request_approval_agent, prepare_request_agent, process_decision],
)
