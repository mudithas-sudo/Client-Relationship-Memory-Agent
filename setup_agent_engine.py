"""One-time: create the Agent Engine that hosts our sessions + Memory Bank (express mode)."""
import os, vertexai
from memory_config import ENGINE_ID_FILE, check_env

check_env()
if ENGINE_ID_FILE.exists():
  raise SystemExit(f"Already created: {ENGINE_ID_FILE.read_text().strip()} (delete {ENGINE_ID_FILE.name} to recreate)")
client = vertexai.Client(api_key=os.environ["GOOGLE_API_KEY"])   # no project/location
engine = client.agent_engines.create()   # empty engine: sessions + memory only, NO runtime deployment
engine_id = engine.api_resource.name.split("/")[-1]
ENGINE_ID_FILE.write_text(engine_id)
print("Created Agent Engine:", engine.api_resource.name)
