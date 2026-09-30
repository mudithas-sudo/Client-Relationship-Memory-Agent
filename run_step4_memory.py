"""Steps 4+6+7 demo: relationship memory across sessions AND people, combined
with artifact fetches.

Meeting 1: Alice (account manager) records relationship facts -> memorized.
Meeting 2: Bob (solutions engineer), NEW session, same client: recall alone.
Meeting 3: Bob asks a question needing BOTH memory and the stored proposal.

Sessions are created with user_id = CLIENT (not the person): memory and
artifacts are institutional - owned by the account, shared by its team.
"""
import asyncio
import time

from google.adk.runners import Runner
from google.genai import types

from agent import root_agent
from artifact_store import APP_NAME, artifact_service
from services import get_services

CLIENT = "client_ab_bank"


async def ask(runner, session_id, person, text):
  print(f"\n{person.upper()}: {text}")
  async for ev in runner.run_async(
      user_id=CLIENT, session_id=session_id,
      new_message=types.Content(role="user", parts=[types.Part(text=text)])):
    for c in ev.get_function_calls():
      print(f"   TOOL CALL: {c.name}({str(dict(c.args))[:90]})")
    if ev.is_final_response() and ev.content and ev.content.parts:
      print("AGENT:", ev.content.parts[0].text.strip()[:600])


async def main():
  sessions, memory, mode = get_services()
  print(f"[mode: {mode}]")
  runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=sessions,
                  artifact_service=artifact_service, memory_service=memory)

  print("\n===== Meeting 1: Alice =====")
  s1 = await sessions.create_session(
      app_name=APP_NAME, user_id=CLIENT,
      state={"client_id": CLIENT, "person": "alice"})
  await ask(runner, s1.id, "alice",
            "Notes from today's AB Bank meeting, please remember: their CTO is "
            "Ruwan Jayasuriya, they are strict about on-premise hosting only, and "
            "their budget committee only approves purchases in November.")

  if mode != "local":
    # Memory Bank extracts facts asynchronously; wait until they are searchable.
    print("\n[waiting for Memory Bank consolidation", end="", flush=True)
    deadline = time.time() + 180
    while time.time() < deadline:
      r = await memory.search_memory(app_name=APP_NAME, user_id=CLIENT,
                                     query="CTO hosting budget approval")
      if r.memories:
        print(f" - {len(r.memories)} memories ready]")
        break
      print(".", end="", flush=True)
      await asyncio.sleep(10)
    else:
      print(" - timed out after 180s; recall may be empty]")

  print("\n===== Meeting 2: Bob, new session, memory only =====")
  s2 = await sessions.create_session(
      app_name=APP_NAME, user_id=CLIENT,
      state={"client_id": CLIENT, "person": "bob"})
  await ask(runner, s2.id, "bob",
            "I'm new on this account. Who is the technical decision maker and "
            "what constraints should I keep in mind?")

  print("\n===== Meeting 3: Bob, memory + artifact combined =====")
  await ask(runner, s2.id, "bob",
            "Given what we know about their buying constraints, when should we "
            "push to close Phase 2 of the SDP proposal, and what discount can I "
            "offer? Check the stored proposal for the exact terms.")


asyncio.run(main())
