# Week 4 demo script — Northbook (≈5 minutes)

## Before the demo (5 min prior)

```bash
cd Client-Relationship-Memory-Agent-main
./web_app.sh          # Northbook on http://localhost:8010
```

- Open http://localhost:8010, confirm sidebar shows the 5 accounts and
  `memory: vertex-adc` bottom-left.
- Keep `docs/week4-slides.html` open in another tab (arrow keys to navigate).
- LankaPay already has the SLA + incident docs stored and Dilini's meeting
  facts in Memory Bank from rehearsal — that's the point: it remembers.

## The demo (4 beats)

**Beat 1 — The brief (90s).**
Sign in as **dilini** → select **LankaPay** → type:

> Brief me on this client before my call.

While it streams, say: *"Nobody pasted anything. It's pulling the account's
memory and its documents."* When the reply lands, point at the two sources in
the answer: Nadeesha Silva / November drill (memory) and the USD 980 credit
(document).

**Beat 2 — Open the hood (45s).**
Click the **"… tool calls — view run"** chip under the reply.

> *"Every step is recorded: it searched the client's memory, listed the
> documents, fetched one. The model never touches storage — these tools do,
> and each one checks the client scope first."*

Close the drawer (Esc). *"And it's optional — this is a product, not a debug
screen."*

**Beat 3 — Memory travels (90s).**
Still as dilini, type:

> Remember: their CFO will join the next call — bring the Q3 uptime report.

Point out the `memorize_meeting` confirmation. Then: switch **Signed in as →
kasun**, click **New meeting** (fresh session, empty thread), and type:

> Anything I should know before the LankaPay call?

*(Consolidation is async — if the CFO fact hasn't surfaced yet, narrate it:
"Memory Bank extracts facts in the background, takes a few seconds" and ask
again.)* Land the line: *"Dilini told it once. Kasun — new person, new
session — inherits it. When someone leaves the company, the account memory
doesn't."*

**Beat 4 — The wall between clients (45s).**
Select **Golden Lotus Hotels** → type:

> Do we have any SLA credits pending with this client?

It knows nothing about LankaPay's credit. *"Same agent, different account —
scope is set by the app when the session is created, and every tool enforces
it. We also have an automated leak test that fails the build on any
cross-client answer."*

**Close (15s).**
*"Documents in the filing cabinet, facts in the notebook, one client at a
time — that's tiered context, artifacts, and Memory Bank, running on the real
Agent Engine."*

## If something breaks

| Symptom | Say / do |
|---|---|
| "model not found" | location env — restart via `./web_app.sh` (sets global + us-central1) |
| memory empty in Beat 3 | wait ~20s, ask again — async extraction |
| network dies | `../venv/bin/python chat.py client_lanka_pay dilini` — same agent, local fallback, keep talking |
