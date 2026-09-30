"""Northbook - dedicated web console for the Client Relationship Memory Agent.

The production pattern in miniature: THIS backend is the "CRM" - it decides
the client scope when it creates a session (user_id = client_id, person in
state). The browser never sends anything the model could use to switch
clients mid-session.

Run:  ./web_app.sh          (port 8010, real Vertex services)
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from google.genai import types
from google.adk.runners import Runner

from agent import root_agent
from artifact_store import APP_NAME, artifact_service, require_client_id
from services import get_services

CLIENTS = [
    {"id": "client_ab_bank", "name": "AB Bank", "industry": "Banking", "initials": "AB"},
    {"id": "client_lanka_pay", "name": "LankaPay", "industry": "Payments", "initials": "LP"},
    {"id": "client_golden_lotus_hotels", "name": "Golden Lotus Hotels", "industry": "Hospitality", "initials": "GL"},
    {"id": "client_ruhuna_insurance", "name": "Ruhuna General Insurance", "industry": "Insurance", "initials": "RG"},
    {"id": "client_ceylon_micro", "name": "Ceylon Microfinance", "industry": "Microfinance", "initials": "CM"},
]
PEOPLE = ["alice", "bob", "dilini", "kasun", "ruwanthi", "mohamed", "tharindu", "farah"]

app = FastAPI(title="Northbook")

_sessions, _memory, MODE = get_services()
runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=_sessions,
                artifact_service=artifact_service, memory_service=_memory)

STATIC = Path(__file__).parent / "webapp"


@app.get("/")
async def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/meta")
async def meta():
    return {"clients": CLIENTS, "people": PEOPLE, "mode": MODE}


class NewSession(BaseModel):
    client_id: str
    person: str


@app.post("/api/sessions")
async def new_session(body: NewSession):
    client_id = require_client_id(body.client_id)
    s = await _sessions.create_session(
        app_name=APP_NAME, user_id=client_id,
        state={"client_id": client_id, "person": body.person})
    return {"session_id": s.id}


class ChatIn(BaseModel):
    client_id: str
    session_id: str
    message: str


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj)}\n\n"


@app.post("/api/chat")
async def chat(body: ChatIn):
    client_id = require_client_id(body.client_id)
    msg = types.Content(role="user", parts=[types.Part(text=body.message)])

    async def stream():
        try:
            async for ev in runner.run_async(user_id=client_id,
                                             session_id=body.session_id,
                                             new_message=msg):
                for c in ev.get_function_calls():
                    yield _sse({"type": "tool_call", "name": c.name,
                                "args": {k: str(v)[:120] for k, v in (c.args or {}).items()}})
                for r in ev.get_function_responses():
                    yield _sse({"type": "tool_result", "name": r.name,
                                "result": str(r.response)[:400]})
                if ev.is_final_response() and ev.content and ev.content.parts:
                    text = "".join(p.text or "" for p in ev.content.parts)
                    if text.strip():
                        yield _sse({"type": "text", "content": text})
        except Exception as exc:  # surface, don't hang the stream
            yield _sse({"type": "error", "message": str(exc)[:300]})
        yield _sse({"type": "done"})

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/artifacts/{client_id}")
async def artifacts(client_id: str):
    client_id = require_client_id(client_id)
    names = await artifact_service.list_artifact_keys(
        app_name=APP_NAME, user_id=client_id, session_id=None)
    items = []
    for name in sorted(names):
        v = await artifact_service.get_artifact_version(
            app_name=APP_NAME, user_id=client_id, session_id=None, filename=name)
        meta_ = (v.custom_metadata if v else {}) or {}
        items.append({"id": f"{name}@v{v.version}" if v else name,
                      "name": name,
                      "summary": meta_.get("summary", ""),
                      "size": meta_.get("size_bytes")})
    return {"artifacts": items}
