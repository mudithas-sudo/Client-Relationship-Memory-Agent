"""Retrieve the FULL content of an artifact from its compact reference."""
from artifact_store import APP_NAME, artifact_service, require_client_id


def parse_artifact_id(artifact_id: str) -> tuple[str, int | None]:
  name, sep, ver = artifact_id.rpartition("@v")
  if sep and ver.isdigit():
    return name, int(ver)
  return artifact_id, None  # bare filename -> latest version


async def fetch_artifact(client_id: str, artifact_id: str) -> dict:
  """Fetch full content for an artifact reference (e.g. 'proposal.txt@v0').

  The client_id must be given explicitly; a reference only resolves inside the
  client it was uploaded to.
  """
  client_id = require_client_id(client_id)
  filename, version = parse_artifact_id(artifact_id)
  part = await artifact_service.load_artifact(
      app_name=APP_NAME, user_id=client_id, session_id=None,
      filename=filename, version=version,
  )
  if part is None:
    return {"error": f"No artifact {artifact_id!r} for {client_id}."}
  if part.inline_data is not None:
    content = part.inline_data.data.decode("utf-8", errors="replace")
  else:
    content = part.text or ""
  return {"artifact_id": artifact_id, "content": content}
