"""Store a client document as an artifact; return a COMPACT reference only.

The point of the tiered-context pattern: the caller (and later the LLM) gets
back  {artifact_id, summary, size}  - not the document body.
"""
import mimetypes
from pathlib import Path

from google.genai import types

from artifact_store import APP_NAME, artifact_service, require_client_id

_SUMMARY_MAX = 140


def _one_line_summary(text: str, filename: str) -> str:
  # Step 1 heuristic: first non-empty line. (Step 2: the agent can supply a better one.)
  for line in text.splitlines():
    line = line.strip().lstrip("#").strip()
    if line:
      return line[:_SUMMARY_MAX]
  return f"(empty file) {filename}"


async def upload_artifact(
    client_id: str, file_path: str, summary: str | None = None
) -> dict:
  """Upload a local text/CSV file as an artifact for a client.

  Args:
    client_id: Explicit client scope, e.g. 'client_ab_bank'.
    file_path: Path to a plain text or CSV file.
    summary: Optional one-line description; auto-derived if omitted.

  Returns:
    Compact reference: {artifact_id, filename, version, summary, size_bytes}.
  """
  client_id = require_client_id(client_id)
  path = Path(file_path)
  data = path.read_bytes()
  text = data.decode("utf-8", errors="replace")
  summary = (summary or _one_line_summary(text, path.name))[:_SUMMARY_MAX]
  mime = mimetypes.guess_type(path.name)[0] or "text/plain"

  version = await artifact_service.save_artifact(
      app_name=APP_NAME,
      user_id=client_id,          # client, not person
      session_id=None,            # client-level: survives across sessions
      filename=path.name,
      artifact=types.Part.from_bytes(data=data, mime_type=mime),
      custom_metadata={"summary": summary, "size_bytes": len(data)},
  )
  return {
      "artifact_id": f"{path.name}@v{version}",
      "filename": path.name,
      "version": version,
      "summary": summary,
      "size_bytes": len(data),
  }
