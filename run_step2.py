"""Step 2 demo: upload a doc, ask a detail question, show the tool calls and
prompt-token counts per model call (proof the doc is not pasted into every turn)."""
import asyncio, os, sys
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent
from artifact_store import APP_NAME, artifact_service

CLIENT = "client_ab_bank"

async def ask(runner, session_id, text):
  print(f"\nUSER: {text}")
  async for ev in runner.run_async(
      user_id="alice", session_id=session_id,
      new_message=types.Content(role="user", parts=[types.Part(text=text)])):
    u = ev.usage_metadata
    if u: print(f"   [model call: prompt_tokens={u.prompt_token_count}]")
    for c in ev.get_function_calls():
      print(f"   TOOL CALL: {c.name}({dict(c.args)})")
    for r in ev.get_function_responses():
      s = str(r.response); print(f"   TOOL RESULT: {s[:110]}{'...' if len(s)>110 else ''}")
    if ev.is_final_response() and ev.content and ev.content.parts:
      print("AGENT:", ev.content.parts[0].text)

async def main():
  sessions = InMemorySessionService()
  runner = Runner(app_name=APP_NAME, agent=root_agent,
                  session_service=sessions, artifact_service=artifact_service)
  # Explicit client scope, set by CALLING CODE at session creation.
  s = await sessions.create_session(app_name=APP_NAME, user_id="alice",
                                    state={"client_id": CLIENT})
  await ask(runner, s.id, "Please store sample_docs/ab_bank_sdp_proposal.txt (it's the SDP module proposal).")
  await ask(runner, s.id, "What is the annual SDP licence fee, and what discount applies for signing Phase 2 early?")

  print("\n--- no client_id: must be refused ---")
  s2 = await sessions.create_session(app_name=APP_NAME, user_id="alice")
  await ask(runner, s2.id, "What documents do we have?")

asyncio.run(main())
