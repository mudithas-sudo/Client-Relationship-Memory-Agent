"""Step 5: client isolation test, with hard assertions.

AB Bank's memories and artifacts must be invisible from a Ceylon Microfinance
session. Two checks:
  1. service-level: search AB Bank facts under the other client's scope -> empty;
     artifact listing under the other client -> no AB Bank documents.
  2. agent-level: ask the other client's session who the CTO is -> the answer
     must not contain the AB Bank facts.

Exits non-zero on any leak, so this doubles as a CI check.
"""
import asyncio
import sys

from google.adk.runners import Runner
from google.genai import types

from agent import root_agent
from artifact_store import APP_NAME, artifact_service
from services import get_services

AB, CEY = "client_ab_bank", "client_ceylon_micro"
SECRETS = ("Ruwan", "November", "on-premise")  # facts that belong to AB Bank only


async def final_text(runner, session_id, user_id, text):
  out = ""
  async for ev in runner.run_async(
      user_id=user_id, session_id=session_id,
      new_message=types.Content(role="user", parts=[types.Part(text=text)])):
    if ev.is_final_response() and ev.content and ev.content.parts:
      out = ev.content.parts[0].text or ""
  return out


async def main():
  sessions, memory, mode = get_services()
  print(f"[mode: {mode}]")
  runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=sessions,
                  artifact_service=artifact_service, memory_service=memory)
  failures = []

  # --- seed AB Bank memory ---
  s_ab = await sessions.create_session(app_name=APP_NAME, user_id=AB,
                                       state={"client_id": AB, "person": "alice"})
  await final_text(runner, s_ab.id, AB,
                   "Remember: AB Bank's CTO is Ruwan Jayasuriya, on-premise only, "
                   "budget approvals happen in November.")

  # --- 1. service-level checks ---
  hits = await memory.search_memory(app_name=APP_NAME, user_id=CEY,
                                    query="Who is the CTO? budget approval month")
  if hits.memories:
    failures.append(f"memory leak: {len(hits.memories)} AB Bank memories visible to {CEY}")
  print(f"memory search under {CEY}: {len(hits.memories)} hits (want 0)")

  names = await artifact_service.list_artifact_keys(
      app_name=APP_NAME, user_id=CEY, session_id=None)
  leaked = [n for n in names if "ab_bank" in n]
  if leaked:
    failures.append(f"artifact leak: {leaked} visible to {CEY}")
  print(f"AB Bank artifacts listed under {CEY}: {leaked} (want [])")

  # --- 2. agent-level check ---
  s_cey = await sessions.create_session(app_name=APP_NAME, user_id=CEY,
                                        state={"client_id": CEY, "person": "carol"})
  answer = await final_text(runner, s_cey.id, CEY,
                            "Who is this client's CTO and when do they approve budgets?")
  print(f"\n{CEY} agent answer: {answer[:250]}")
  found = [w for w in SECRETS if w.lower() in answer.lower()]
  if found:
    failures.append(f"agent leaked AB Bank facts to {CEY}: {found}")

  print("\n" + ("ISOLATION FAILED: " + "; ".join(failures) if failures
                else "ISOLATION OK: no cross-client leakage."))
  sys.exit(1 if failures else 0)


asyncio.run(main())
