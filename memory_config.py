"""Express-mode wiring for Vertex AI Session + Memory Bank services.

NEW ADK CONCEPTS
  * BaseSessionService: stores a conversation's events. VertexAiSessionService
    keeps them in Vertex "Agent Engine Sessions" (cloud) instead of RAM.
  * BaseMemoryService: long-term, cross-session memory. VertexAiMemoryBankService
    sends finished sessions to Memory Bank, which uses an LLM to extract durable
    facts, and later serves semantic search over them.
  * Both are bound to an *Agent Engine* resource (`agent_engine_id`) - the
    container that holds sessions and memories. Create it once (setup_agent_engine.py).

EXPRESS MODE PATTERN: pass NO project/location. Authentication is the express-mode
API key (GOOGLE_API_KEY) and GOOGLE_GENAI_USE_ENTERPRISE=true (older name:
GOOGLE_GENAI_USE_VERTEXAI=true). ADK raises if you pass both project/location and a key.
"""
import os
from pathlib import Path

from google.adk.memory import VertexAiMemoryBankService
from google.adk.sessions import VertexAiSessionService

ENGINE_ID_FILE = Path(__file__).parent / ".agent_engine_id"


def check_env() -> None:
  key = os.environ.get("GOOGLE_API_KEY")
  flag = os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE") or os.environ.get("GOOGLE_GENAI_USE_VERTEXAI")
  if not key:
    raise SystemExit("GOOGLE_API_KEY is not set (use your Vertex express-mode key).")
  if (flag or "").lower() not in ("true", "1"):
    raise SystemExit("Set GOOGLE_GENAI_USE_ENTERPRISE=true (or GOOGLE_GENAI_USE_VERTEXAI=true).")


def get_engine_id() -> str:
  if not ENGINE_ID_FILE.exists():
    raise SystemExit("No Agent Engine yet - run setup_agent_engine.py first.")
  return ENGINE_ID_FILE.read_text().strip()


def make_services():
  check_env()
  engine = get_engine_id()
  return (
      VertexAiSessionService(agent_engine_id=engine),
      VertexAiMemoryBankService(agent_engine_id=engine),
  )
