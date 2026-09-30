"""Step 4: pluggable session + memory services with a local fallback.

Express mode (Step 3) is still blocked on the 403 key, so the demo must not
depend on it. This module returns:
  * Vertex services (memory_config.make_services) when the express-mode env is
    set AND an Agent Engine id exists - the production path, unchanged;
  * otherwise local services (InMemorySessionService + InMemoryMemoryService)
    with a clear banner. Same interfaces, so nothing downstream changes.

That swap-is-config property is the whole point of BaseSessionService /
BaseMemoryService, and it is the line to say in the demo when someone asks
"but is this the real Memory Bank?": locally it is a keyword-matching stand-in;
with the express key it becomes LLM-extracted, deduplicated facts - and not
one line of agent or tool code changes.
"""
import os

from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService

from memory_config import ENGINE_ID_FILE, make_services


def get_services():
  """(session_service, memory_service, mode) - Vertex when configured, else local."""
  flag = os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE") or os.environ.get(
      "GOOGLE_GENAI_USE_VERTEXAI"
  )
  if (flag or "").lower() in ("true", "1") and ENGINE_ID_FILE.exists():
    from memory_config import auth_mode
    session_service, memory_service = make_services()
    return session_service, memory_service, f"vertex-{auth_mode()}"
  print("[services] LOCAL MODE: InMemory session+memory services "
        "(express-mode key not configured; memories die with the process).")
  return InMemorySessionService(), InMemoryMemoryService(), "local"
