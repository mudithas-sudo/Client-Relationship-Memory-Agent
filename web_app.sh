#!/usr/bin/env bash
# Northbook console on http://localhost:8010 - real Vertex services, ADC auth.
set -e
cd "$(dirname "$0")"
exec env -u GOOGLE_API_KEY -u GEMINI_API_KEY \
  PYTHONWARNINGS="ignore::FutureWarning,ignore::UserWarning" \
  GOOGLE_CLOUD_PROJECT=project-team-1-507409 \
  GOOGLE_CLOUD_LOCATION=global \
  AGENT_ENGINE_LOCATION=us-central1 \
  GOOGLE_GENAI_USE_VERTEXAI=true \
  ../venv/bin/uvicorn crm_app:app --host 127.0.0.1 --port 8010
