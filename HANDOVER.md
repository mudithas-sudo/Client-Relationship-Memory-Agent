# Handover: Client Relationship Memory Agent (ADK Week 4)

Python 3.14, venv in `.venv` (not shared). Setup:
    python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
(pip may warn about opentelemetry version pins between google-adk and google-api-core; harmless so far.)

## Status
- Step 1 DONE  local artifacts (artifact_store.py, upload_artifact.py, fetch_artifact.py, test_step1.py)
- Step 2 DONE  agent + tools (agent.py, tools.py, run_step2.py). Tested live on Gemini API, model gemini-3.8-flash
- Step 3 DONE (2026-09-29) via ADC instead of the express key (which stayed 403-blocked).
  Auth: `gcloud application-default login` -> ADC file + quota project project-team-1-507409.
  memory_config.py now supports both modes; setup_agent_engine.py created engine
  6480054791425753088 (us-central1). Gotcha: this project serves Gemini models ONLY on the
  `global` endpoint while the Agent Engine needs a real region -> GOOGLE_CLOUD_LOCATION=global
  for models, AGENT_ENGINE_LOCATION=us-central1 for services. Use ./run_vertex.sh <script>.
  Real Memory Bank verified: consolidation is async (run_step4 polls until searchable);
  run_step5 isolation passes against the live service.
- Steps 4-8 DONE (2026-09-29, second half of the pair):
  * services.py - session+memory services with local InMemory fallback while the express key is blocked; Vertex path untouched.
  * memory_tools.py + agent.py - preload_memory (auto recall) + memorize_meeting (ToolContext.add_session_to_memory).
  * run_step4_memory.py - memory across sessions AND people (alice -> bob) + combined memory+artifact question.
  * run_step5_isolation.py - 3-level leakage check (memory search, artifact listing, live agent answer), exits non-zero on leak. Passing.
  * README.md - tier mapping + demo flow.
  * Scoping decision implemented per brief: sessions use user_id=client_id, person kept in state.
  * Verified on linux venv (google-adk 2.8.0, python 3.11) with a plain Gemini key, model gemini-3.8-flash.

## Non-negotiables from the brief
- client_id is ALWAYS explicit at session start, never inferred; used as user_id for memory/session services (shared across people).
- Express mode only; stop and flag if anything needs billing.
- Fictional data only.

## Env vars (never commit keys)
    GOOGLE_API_KEY=<express-mode key>
    GOOGLE_GENAI_USE_ENTERPRISE=true      # older name GOOGLE_GENAI_USE_VERTEXAI
Then: python setup_agent_engine.py (once) ; python check_connectivity.py

## Revision 2026-09-29 (evening)
- Memory tools re-scoped: built-in preload_memory / add_session_to_memory key by the
  SESSION user, which broke recall in adk web (sessions there belong to 'user').
  memory_tools.py now calls the memory service with user_id=state['client_id']
  explicitly (recall_client_memory + memorize_meeting) - same drawer from CLI,
  chat.py and the web UI. Recall is now a visible tool call in the Events panel.
- Observability: ./web_observe.sh [client_id] serves the agent in adk web (port 8002)
  against the real Agent Engine; wrapper package ../client_memory_agent pins the
  model to the global endpoint and seeds client_id from WEB_CLIENT_ID.
