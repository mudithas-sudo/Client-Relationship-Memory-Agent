# Client Relationship Memory Agent — ADK Week 4

A pre-sales assistant with **institutional memory per client**: documents live
in artifact storage, relationship facts live in long-term memory, and both are
sealed to one explicit `client_id` — shared by everyone on the account team,
invisible to every other client.

## Tier mapping (Step 8)

| Tier | What lives there here | Scope |
|---|---|---|
| Events | the live meeting conversation | one session |
| State | `client_id` (set by calling code, never inferred), `person` | one session |
| Artifacts | client documents (`FileArtifactService`, on disk, versioned), compact refs only in context | per **client** (`user_id=client_id`, `session_id=None`) |
| Memory | relationship facts from past meetings (`recall_client_memory` search, `memorize_meeting` consolidation - both client-scoped explicitly) | per **client**, across sessions and people |

Key design (from the brief): sessions are created with `user_id = client_id`
and the human's name kept in state — so memory and artifacts belong to the
*account*, not the individual. Alice's meeting notes surface for Bob; nothing
surfaces for another client.

## Run (local mode — no cloud, no billing)

```bash
cd Client-Relationship-Memory-Agent-main
set -a; source ../test_agent/.env; set +a          # any Gemini API key
PY=../venv/bin/python                              # google-adk 2.8 venv
$PY run_step2.py            # artifacts: upload, grounded Q&A, no-client refusal
$PY run_step4_memory.py     # memory across sessions AND people + combined with artifacts
$PY run_step5_isolation.py  # cross-client leakage checks; exits non-zero on a leak
```

`services.py` picks the backend: with `GOOGLE_GENAI_USE_ENTERPRISE=true` and a
`.agent_engine_id` present it uses Vertex Agent Engine (Sessions + Memory Bank,
Step 3); otherwise it falls back to local in-memory services and says so. The
agent and tools are identical in both modes — the swap is configuration.

## Run (production mode — real Vertex Agent Engine, ADC auth)

```bash
./run_vertex.sh check_connectivity.py     # sessions + Memory Bank reachable
./run_vertex.sh run_step4_memory.py       # REAL Memory Bank: async consolidation,
                                          # cross-person recall of extracted facts
./run_vertex.sh run_step5_isolation.py    # isolation against the live service
```

Auth is Application Default Credentials (`gcloud application-default login`);
no API key is used. Note the two locations: models are served on the `global`
endpoint for this project, the Agent Engine lives in `us-central1` — see
`run_vertex.sh`. With Memory Bank, recall returns LLM-extracted facts, not raw
transcript, and consolidation is asynchronous (the demo polls until ready).

## Demo flow (tomorrow)

1. **Refusal first** (run_step2 tail): a session without `client_id` is refused
   by `before_agent_callback` — scope is set by code, never guessed by the model.
2. **Grounded answers**: licence fee + early-signing discount quoted verbatim
   from the fetched artifact; show prompt-token counts — the document is not
   pasted into every turn.
3. **The memory moment** (run_step4): Alice records CTO/hosting/November facts;
   **Bob, new session**, gets them recalled automatically; then a question that
   needs memory *and* the proposal together ("when to close Phase 2, what
   discount") — answer: November cycle + 6%/90-day clause.
4. **Isolation** (run_step5): three-level check — memory search, artifact
   listing, and a live agent answer under the other client — all clean, script
   exits 0.

## Status vs handover

- Steps 4, 5, 6, 7, 8: **done** (this commit) — memory wiring with local
  fallback, isolation test with assertions, multi-person sharing, combined
  memory+artifact test, this README.
- Step 3 (Vertex express mode): still blocked on the 403 key; everything is
  wired so that fixing the key + `setup_agent_engine.py` flips production on
  with zero code changes.
