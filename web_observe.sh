#!/usr/bin/env bash
# Observability UI: serve the agent in adk web with the REAL Vertex services.
# Usage: ./web_observe.sh [client_id]     (default client_ab_bank; port 8002)
#
# Location split, web edition: the server env is us-central1 so the
# agentengine:// URIs resolve; the wrapper package pins the MODEL's own client
# to the "global" endpoint (see ../client_memory_agent/agent.py).
# WEB_CLIENT_ID pins the session's client scope per launch - set by this
# launch command, never typed into the chat.
set -e
cd "$(dirname "$0")/.."
ENGINE="agentengine://6480054791425753088"
exec env -u GOOGLE_API_KEY -u GEMINI_API_KEY \
  PYTHONWARNINGS="ignore::FutureWarning,ignore::UserWarning" \
  GOOGLE_CLOUD_PROJECT=project-team-1-507409 \
  GOOGLE_CLOUD_LOCATION=us-central1 \
  GOOGLE_GENAI_USE_VERTEXAI=true \
  WEB_CLIENT_ID="${1:-client_ab_bank}" \
  ./venv/bin/adk web --port 8002 \
    --session_service_uri "$ENGINE" \
    --memory_service_uri  "$ENGINE" \
    --artifact_service_uri "file://$(pwd)/Client-Relationship-Memory-Agent-main/artifact_store_data"
