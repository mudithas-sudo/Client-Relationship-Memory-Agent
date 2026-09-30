"""Interactive console for the Client Relationship Memory Agent.

Usage:
    ./run_vertex.sh chat.py client_ab_bank alice     # real Vertex Memory Bank
    ../venv/bin/python chat.py client_ab_bank alice  # local mode (needs GOOGLE_API_KEY)

The calling code - here, this script; in production, your CRM - sets WHO the
client is. The agent never chooses. Type freely; /quit ends the meeting.
"""
import asyncio
import sys

from google.genai import types
from google.adk.runners import Runner

from agent import root_agent
from artifact_store import APP_NAME, artifact_service, require_client_id
from services import get_services


async def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("usage: chat.py <client_id> <your_name>   e.g. chat.py client_ab_bank alice")
    client_id = require_client_id(sys.argv[1])
    person = sys.argv[2]

    sessions, memory, mode = get_services()
    runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=sessions,
                    artifact_service=artifact_service, memory_service=memory)
    s = await sessions.create_session(app_name=APP_NAME, user_id=client_id,
                                      state={"client_id": client_id, "person": person})
    print(f"[{mode}] Meeting started: client={client_id}, you={person}. /quit to end.\n"
          f"Tip: say 'remember ...' to store facts; 'brief me on this client' to recall.")

    while True:
        try:
            text = (await asyncio.to_thread(input, f"\n{person}> ")).strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if text.lower() in ("/quit", "/exit", "q"):
            break
        msg = types.Content(role="user", parts=[types.Part(text=text)])
        async for ev in runner.run_async(user_id=client_id, session_id=s.id, new_message=msg):
            for c in ev.get_function_calls():
                print(f"   .. {c.name}")
            if ev.is_final_response() and ev.content and ev.content.parts and ev.content.parts[0].text:
                print(f"\nagent> {ev.content.parts[0].text.strip()}")

    print("\nMeeting ended. (Facts you asked the agent to remember are in the "
          "client's long-term memory for the next person.)")


asyncio.run(main())
