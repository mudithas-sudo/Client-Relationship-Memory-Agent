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

# AUTH MODES (2026-09-29 update): express-mode keys turned out to be blocked for
# aiplatform.googleapis.com on our accounts, so the formal path is Application
# Default Credentials (gcloud application-default login) + an explicit project.
#   ADC mode:     GOOGLE_CLOUD_PROJECT + GOOGLE_CLOUD_LOCATION set -> project auth
#   Express mode: GOOGLE_API_KEY only (partner's original path, kept working)
# Either way GOOGLE_GENAI_USE_VERTEXAI/ENTERPRISE=true routes model calls to Vertex.


def auth_mode() -> str:
  if os.environ.get("GOOGLE_CLOUD_PROJECT"):
    return "adc"
  if os.environ.get("GOOGLE_API_KEY"):
    return "express"
  raise SystemExit(
      "Set GOOGLE_CLOUD_PROJECT (+ GOOGLE_CLOUD_LOCATION, ADC mode) or "
      "GOOGLE_API_KEY (express mode)."
  )


def check_env() -> None:
  auth_mode()
  flag = os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE") or os.environ.get("GOOGLE_GENAI_USE_VERTEXAI")
  if (flag or "").lower() not in ("true", "1"):
    raise SystemExit("Set GOOGLE_GENAI_USE_ENTERPRISE=true (or GOOGLE_GENAI_USE_VERTEXAI=true).")


def get_engine_id() -> str:
  if not ENGINE_ID_FILE.exists():
    raise SystemExit("No Agent Engine yet - run setup_agent_engine.py first.")
  return ENGINE_ID_FILE.read_text().strip()


def make_services():
  check_env()
  engine = get_engine_id()
  if auth_mode() == "adc":
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    # NOTE: this project serves Gemini models only on the "global" endpoint,
    # but Agent Engine (sessions + Memory Bank) lives in a real region. So the
    # engine's region is its own setting; GOOGLE_CLOUD_LOCATION stays "global"
    # for model calls.
    location = os.environ.get("AGENT_ENGINE_LOCATION", "us-central1")
    return (
        VertexAiSessionService(project=project, location=location, agent_engine_id=engine),
        VertexAiMemoryBankService(project=project, location=location, agent_engine_id=engine),
    )
  return (
      VertexAiSessionService(agent_engine_id=engine),
      VertexAiMemoryBankService(agent_engine_id=engine),
  )
