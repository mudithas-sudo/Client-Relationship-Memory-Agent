"""One-time: create the Agent Engine that hosts our sessions + Memory Bank.

Works in both auth modes (see memory_config.py): ADC (project + location) or
express-mode key.
"""
import os, vertexai
from memory_config import ENGINE_ID_FILE, auth_mode, check_env

check_env()
if ENGINE_ID_FILE.exists():
  raise SystemExit(f"Already created: {ENGINE_ID_FILE.read_text().strip()} (delete {ENGINE_ID_FILE.name} to recreate)")
if auth_mode() == "adc":
  client = vertexai.Client(
      project=os.environ["GOOGLE_CLOUD_PROJECT"],
      location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
  )
else:
  client = vertexai.Client(api_key=os.environ["GOOGLE_API_KEY"])   # no project/location
engine = client.agent_engines.create()   # empty engine: sessions + memory only, NO runtime deployment
engine_id = engine.api_resource.name.split("/")[-1]
ENGINE_ID_FILE.write_text(engine_id)
print("Created Agent Engine:", engine.api_resource.name)
