#!/usr/bin/env bash
# Run any script in this project against the REAL Vertex Agent Engine (ADC auth).
# Usage: ./run_vertex.sh run_step4_memory.py
# Prereq: gcloud application-default login already done (ADC file exists).
set -e
cd "$(dirname "$0")"
exec env -u GOOGLE_API_KEY -u GEMINI_API_KEY \
  PYTHONWARNINGS="ignore::FutureWarning,ignore::UserWarning" \
  GOOGLE_CLOUD_PROJECT=project-team-1-507409 \
  GOOGLE_CLOUD_LOCATION=global \
  AGENT_ENGINE_LOCATION=us-central1 \
  GOOGLE_GENAI_USE_VERTEXAI=true \
  ../venv/bin/python "$@"
