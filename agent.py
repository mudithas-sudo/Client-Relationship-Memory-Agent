"""Client Relationship Memory Agent (Step 2: artifacts only).

NEW ADK CONCEPTS
  * LlmAgent: model + instruction + tools. ADK runs the loop
    model -> tool call -> tool result -> model ... until a final answer.
  * Function tools: plain Python functions; ADK builds the schema from the
    signature + docstring, so docstrings are the model's "manual".
  * InstructionProvider: `instruction` may be a function of the context, letting
    us inject the (explicit) client_id from session state into the prompt.
  * before_agent_callback: runs before the agent; returning Content short-circuits
    the turn. We use it to refuse to run without a client_id.
"""
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.genai import types

from artifact_store import require_client_id
from memory_tools import memorize_meeting, recall_client_memory
from tools import fetch_artifact, list_client_artifacts, upload_artifact

MODEL = "gemini-3.8-flash"


def _instruction(ctx: ReadonlyContext) -> str:
  client_id = ctx.state.get("client_id")
  return f"""You are a pre-sales assistant for ONE client: {client_id}.
You never work with any other client.

Client documents are stored as artifacts and are NOT in this conversation.
- Use list_client_artifacts to see what exists (ids + one-line summaries).
- When a question needs a specific detail from a document, call fetch_artifact
  for that document, then answer from the fetched text. Do not guess details.
- Use upload_artifact only when the user asks you to store a file.
Quote figures exactly as they appear in the document and name the document.

Relationship memory (Step 4):
- Before briefing anyone, or advising on strategy or timing, call
  recall_client_memory - it holds institutional knowledge from past meetings,
  recorded by the whole account team. Cite it as "from our account history".
- When the user asks you to remember something, or to wrap up a meeting whose
  facts matter, restate the key facts in your reply and call memorize_meeting.
- Do only what the user asked for in the current message."""


def _require_client(callback_context):
  try:
    require_client_id(callback_context.state.get("client_id"))
  except ValueError as e:
    return types.Content(role="model", parts=[types.Part(text=f"Session refused: {e}")])
  return None


root_agent = LlmAgent(
    name="client_relationship_agent",
    model=MODEL,
    instruction=_instruction,
    tools=[upload_artifact, fetch_artifact, list_client_artifacts,
           recall_client_memory, memorize_meeting],
    before_agent_callback=_require_client,
)
