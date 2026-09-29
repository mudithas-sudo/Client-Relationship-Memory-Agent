"""ADK tool wrappers around the Step 1 functions.

NEW ADK CONCEPT: ToolContext + session state
--------------------------------------------
Any tool function may declare a `tool_context: ToolContext` parameter; ADK
injects it (and hides it from the model's tool schema). tool_context.state is the
session's key/value state. We read `client_id` from there, so the LLM is NEVER
asked to (or able to) choose which client's data it touches: the calling code
sets the client at session creation, and tools trust only that.
"""
from pathlib import Path

from google.adk.tools import ToolContext

import fetch_artifact as _fetch
import upload_artifact as _upload
from artifact_store import APP_NAME, artifact_service, require_client_id

# Training-exercise safety: the agent may only ingest files from sample_docs/.
_ALLOWED_DIR = (Path(__file__).parent / "sample_docs").resolve()


def _client(tool_context: ToolContext) -> str:
  return require_client_id(tool_context.state.get("client_id"))


async def upload_artifact(
    file_path: str, summary: str, tool_context: ToolContext
) -> dict:
  """Store a client document (text/CSV) and return a compact reference.

  Args:
    file_path: Path of the file inside sample_docs/, e.g. 'sample_docs/x.txt'.
    summary: One-line description of what the document is.
  """
  path = Path(file_path).resolve()
  if _ALLOWED_DIR not in path.parents:
    return {"error": "Only files inside sample_docs/ can be uploaded."}
  return await _upload.upload_artifact(_client(tool_context), str(path), summary)


async def fetch_artifact(artifact_id: str, tool_context: ToolContext) -> dict:
  """Fetch the FULL text of a stored document by its artifact_id.

  Only call this when you need a specific detail from the document.

  Args:
    artifact_id: Reference from list_client_artifacts/upload_artifact,
      e.g. 'proposal.txt@v0'.
  """
  return await _fetch.fetch_artifact(_client(tool_context), artifact_id)


async def list_client_artifacts(tool_context: ToolContext) -> dict:
  """List this client's stored documents: id + one-line summary only (no content)."""
  client_id = _client(tool_context)
  names = await artifact_service.list_artifact_keys(
      app_name=APP_NAME, user_id=client_id, session_id=None
  )
  items = []
  for name in sorted(names):
    v = await artifact_service.get_artifact_version(
        app_name=APP_NAME, user_id=client_id, session_id=None, filename=name
    )
    meta = (v.custom_metadata if v else {}) or {}
    items.append({
        "artifact_id": f"{name}@v{v.version}" if v else name,
        "summary": meta.get("summary", ""),
        "size_bytes": meta.get("size_bytes"),
    })
  return {"client_id": client_id, "artifacts": items}
