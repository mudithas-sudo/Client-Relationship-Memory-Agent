# Handover: Client Relationship Memory Agent (ADK Week 4)

Python 3.14, venv in `.venv` (not shared). Setup:
    python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
(pip may warn about opentelemetry version pins between google-adk and google-api-core; harmless so far.)

## Status
- Step 1 DONE  local artifacts (artifact_store.py, upload_artifact.py, fetch_artifact.py, test_step1.py)
- Step 2 DONE  agent + tools (agent.py, tools.py, run_step2.py). Tested live on Gemini API, model gemini-3.8-flash
- Step 3 IN PROGRESS  code written (memory_config.py, setup_agent_engine.py, check_connectivity.py), NOT yet run successfully.
  Blocker: the API key so far returns 403 API_KEY_SERVICE_BLOCKED for aiplatform.googleapis.com.
  Need a key from Vertex AI *express mode* sign-up (console.cloud.google.com/vertex-ai/studio). No paid GCP project / billing.
- Steps 4-8 not started (memory wiring, isolation test, multi-person test, combined test, README tier mapping).

## Non-negotiables from the brief
- client_id is ALWAYS explicit at session start, never inferred; used as user_id for memory/session services (shared across people).
- Express mode only; stop and flag if anything needs billing.
- Fictional data only.

## Env vars (never commit keys)
    GOOGLE_API_KEY=<express-mode key>
    GOOGLE_GENAI_USE_ENTERPRISE=true      # older name GOOGLE_GENAI_USE_VERTEXAI
Then: python setup_agent_engine.py (once) ; python check_connectivity.py
