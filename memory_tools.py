"""Step 4 (revised): CLIENT-SCOPED memory tools.

Lesson learned in the web UI: ADK's built-in preload_memory and
ToolContext.add_session_to_memory() scope memory by the SESSION's user_id.
Our CLI creates sessions with user_id=client_id, so that worked - but the
web UI creates sessions under its own user ("user"), and memories landed in
(or were searched from) the wrong drawer.

Fix: like the artifact tools, these tools scope by state["client_id"]
EXPLICITLY, calling the memory service with user_id=client_id no matter who
owns the session. Same behavior in the CLI, chat.py, and adk web.

Trade-off made on purpose: recall is now a deliberate tool call
(recall_client_memory) instead of automatic injection - which also makes it
VISIBLE in the adk web Events panel.
"""
from google.adk.tools import ToolContext

from artifact_store import APP_NAME, require_client_id


async def memorize_meeting(summary: str, tool_context: ToolContext) -> dict:
  """Consolidate this session into the client's long-term relationship memory.

  Call when the user says to remember something, or asks to close/wrap up a
  meeting whose facts should persist.

  Args:
    summary: One or two sentences naming what should be remembered.
  """
  client_id = require_client_id(tool_context.state.get("client_id"))
  ic = tool_context.get_invocation_context()
  if ic.memory_service is None:
    return {"status": "error", "error_message": "No memory service configured."}
  # Consolidate under the CLIENT's scope even if the session belongs to a
  # person or a UI user: hand the service a copy re-keyed to the client.
  session = ic.session.model_copy(update={"user_id": client_id})
  await ic.memory_service.add_session_to_memory(session)
  return {"status": "success", "client_id": client_id, "remembered": summary}


async def recall_client_memory(query: str, tool_context: ToolContext) -> dict:
  """Search the client's long-term relationship memory (facts from past
  meetings, recorded by anyone on the account team).

  Call this before briefing, advising on strategy, or whenever knowledge
  from previous meetings could matter.

  Args:
    query: What to look for, e.g. "decision makers, constraints, deadlines".
  """
  client_id = require_client_id(tool_context.state.get("client_id"))
  ic = tool_context.get_invocation_context()
  if ic.memory_service is None:
    return {"status": "error", "error_message": "No memory service configured."}
  resp = await ic.memory_service.search_memory(
      app_name=APP_NAME, user_id=client_id, query=query)
  memories = []
  for m in resp.memories:
    text = ""
    if m.content and m.content.parts:
      text = " ".join(p.text for p in m.content.parts if p.text)
    memories.append({"fact": text, "author": m.author})
  return {"status": "success", "client_id": client_id, "memories": memories}
