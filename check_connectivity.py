"""Step 3 minimal connectivity check (agent NOT involved yet).
create session -> read it back -> ask Memory Bank to search (empty result is fine)."""
import asyncio
from memory_config import make_services

APP = "client_relationship_agent"
CLIENT = "client_ab_bank"

async def main():
  sessions, memory = make_services()
  s = await sessions.create_session(app_name=APP, user_id=CLIENT, state={"client_id": CLIENT})
  print("1. VertexAiSessionService.create_session OK  id =", s.id)
  got = await sessions.get_session(app_name=APP, user_id=CLIENT, session_id=s.id)
  print("2. get_session OK  state =", got.state)
  r = await memory.search_memory(app_name=APP, user_id=CLIENT, query="anything")
  print("3. VertexAiMemoryBankService.search_memory OK  memories found =", len(r.memories))

asyncio.run(main())
