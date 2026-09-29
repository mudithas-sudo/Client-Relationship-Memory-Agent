"""Shared artifact-service setup + client scoping guard.

NEW ADK CONCEPT: BaseArtifactService
------------------------------------
ADK separates *where big blobs live* from *what the model sees*. An artifact
service stores named, versioned files (types.Part). Implementations:
InMemoryArtifactService (tests), FileArtifactService (local disk - used here),
GcsArtifactService (cloud). They share one interface, so swapping backends later
does not change our tools.

Scoping: ADK addresses artifacts by (app_name, user_id, session_id, filename).
  * session_id=None  -> artifact belongs to the *user_id* and outlives sessions.
We deliberately pass client_id as user_id and session_id=None, so a document
uploaded for client_ab_bank is visible to every later session for that client
(and to no other client). The same client-not-person choice is applied to
Memory Bank in Step 4.
"""
import re
from pathlib import Path

from google.adk.artifacts import FileArtifactService

APP_NAME = "client_relationship_agent"
STORE_DIR = Path(__file__).parent / "artifact_store_data"

artifact_service = FileArtifactService(root_dir=STORE_DIR)

_CLIENT_ID_RE = re.compile(r"^client_[a-z0-9_]{2,60}$")


def require_client_id(client_id: str | None) -> str:
  """Client scoping is ALWAYS explicit: reject missing/malformed ids, never guess."""
  if not client_id or not _CLIENT_ID_RE.match(client_id):
    raise ValueError(
        "A valid explicit client_id is required (e.g. 'client_ab_bank'); "
        f"got {client_id!r}. Client scope is never inferred."
    )
  return client_id
