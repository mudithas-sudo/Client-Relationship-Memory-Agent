import asyncio, json
from upload_artifact import upload_artifact
from fetch_artifact import fetch_artifact
from artifact_store import require_client_id

async def main():
  ref = await upload_artifact("client_ab_bank", "sample_docs/ab_bank_sdp_proposal.txt")
  print("== UPLOAD RETURNS (compact reference) ==")
  print(json.dumps(ref, indent=2))
  print(f"reference is {len(json.dumps(ref))} chars vs document {ref['size_bytes']} bytes\n")

  full = await fetch_artifact("client_ab_bank", ref["artifact_id"])
  print("== EXPLICIT FETCH RETURNS (full content) ==")
  print(full["content"][:200] + "\n...[%d chars total]\n" % len(full["content"]))

  print("== ISOLATION: same ref under a different client ==")
  print(await fetch_artifact("client_brac_bank", ref["artifact_id"]), "\n")

  print("== GUARD: missing / malformed client_id ==")
  for bad in (None, "AB Bank", ""):
    try: require_client_id(bad)
    except ValueError as e: print("rejected:", repr(bad))

asyncio.run(main())
