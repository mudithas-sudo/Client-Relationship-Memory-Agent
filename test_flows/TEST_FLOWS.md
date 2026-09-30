# Test Flows — three clients, six people

Fresh, realistic exercise scripts for the Client Relationship Memory Agent.
Each client has its own folder under `sample_docs/` and its own cast. Run each
line in `chat.py` as the named person:

```bash
./run_vertex.sh chat.py <client_id> <person>      # real Memory Bank
```

Every fact below exists in the documents, so every expected answer is checkable.
Remember: after a "remember ...", Memory Bank consolidation is asynchronous —
give it ~15–30 seconds before the recall session.

---

## Client 1 — `client_lanka_pay` (payment switch operator)

**Cast:** `dilini` (account manager), `kasun` (support engineer)
**Docs:** `sample_docs/lanka_pay/sla_addendum.txt`, `sample_docs/lanka_pay/incident_credit_memo.txt`

### Flow 1A — Dilini, first session (store + grounded Q&A)
1. `Store sample_docs/lanka_pay/sla_addendum.txt — it's the current SLA addendum v2.`
2. `Store sample_docs/lanka_pay/incident_credit_memo.txt — credit memo for incident INC-0842.`
3. `What service credit applies if monthly availability is 99.6%?`
   → **expect:** 10% of monthly fee, from Addendum s.4 (99.50–99.79% band) — and it should cite the document.
4. `What did September's incident actually cost us, and was the credit claimed in time?`
   → **expect:** USD 980 (10% of USD 9,800), claimed 2026-09-18 within the 60-day window.
5. `Remember: their head of switching operations is Nadeesha Silva, she is furious about the HSM failover incident, and they want a quarterly failover drill discussed at the November account review.`

### Flow 1B — Kasun, NEW session (cross-person recall + combined)
1. `I'm covering this account while Dilini is on leave. Brief me.`
   → **expect:** Nadeesha Silva, the incident anger, the November drill topic — *none of which Kasun ever typed*.
2. `If we agree to the quarterly failover drill, which SLA sections would it interact with?`
   → **expect:** fetches the addendum; maintenance windows (s.1) and incident response (s.3) are the sensible citations.
3. `Draft talking points for the November review that acknowledge the incident without reopening the credit discussion.`
   → **expect:** uses memo facts (credit already applied) + memory (Nadeesha's mood, drill request).

### Flow 1C — Version update (artifact versioning)
1. Edit `sla_addendum.txt` locally (e.g. change p95 latency 350 → 320 ms), then:
   `Store sample_docs/lanka_pay/sla_addendum.txt again — we renegotiated the latency clause.`
   → **expect:** same filename, **new version** (`@v1`).
2. `What p95 latency are we committed to now?` → **expect:** the new figure from the latest version.

---

## Client 2 — `client_golden_lotus_hotels` (hotel chain, guest messaging)

**Cast:** `ruwanthi` (presales), `mohamed` (integration engineer)
**Docs:** `sample_docs/golden_lotus/cpaas_quote.txt`, `sample_docs/golden_lotus/integration_scope.txt`

### Flow 2A — Ruwanthi, commercial session
1. `Store sample_docs/golden_lotus/cpaas_quote.txt — quote GLH-Q-118 for guest messaging.`
2. `Store sample_docs/golden_lotus/integration_scope.txt — notes from the technical workshop.`
3. `At their estimated volume, roughly what does a month of WhatsApp template messages cost if 40% of the 210,000 messages are templates?`
   → **expect:** it must fetch the quote (LKR 5.60 × 84,000 = LKR 470,400) and show the arithmetic from cited figures.
4. `What do they have to do to earn the platform-fee discount?`
   → **expect:** all 11 properties live within 60 days of signature → 8% off LKR 145,000.
5. `Remember: the owner's daughter Shanika Weerasinghe is the real decision maker, the GM cares only about review scores, and the quote expires 15 November — they tend to go silent, so chase two weeks before.`

### Flow 2B — Mohamed, NEW session, technical
1. `I'm doing the Opera integration. What was decided about where booking confirmations trigger from?`
   → **expect:** head-office sync, not per property; up to 15 min latency accepted (scope note, decision 1).
2. `Any data constraints I should know before we route WhatsApp traffic?`
   → **expect:** guest phone numbers must remain in Sri Lanka; BSP routing must be confirmed pre-contract (open item).
3. `Who should I actually be convincing on the client side?`
   → **expect:** Shanika Weerasinghe from memory — Ruwanthi's note, never told to Mohamed.

### Flow 2C — Deadline pressure (memory + artifact date logic)
1. As either person: `It's the first week of November. What should we be doing on this account right now?`
   → **expect:** quote expires 15 Nov + "they go silent, chase two weeks before" → chase now; discount clock (60-day go-live) worth mentioning.

---

## Client 3 — `client_ruhuna_insurance` (insurer, RFP bid)

**Cast:** `tharindu` (bid manager), `farah` (solutions architect)
**Docs:** `sample_docs/ruhuna_insurance/claims_rfp_excerpt.txt`, `sample_docs/ruhuna_insurance/bid_strategy_note.txt`

### Flow 3A — Tharindu, bid kickoff
1. `Store sample_docs/ruhuna_insurance/claims_rfp_excerpt.txt — the RFP excerpt, ref RGI/ICT/2026/31.`
2. `Store sample_docs/ruhuna_insurance/bid_strategy_note.txt — our internal bid strategy.`
3. `List the mandatory criteria and confirm which we satisfy.`
   → **expect:** M1–M4 from the RFP + the strategy note's claim that all four are covered.
4. `What's our pricing floor and why?`
   → **expect:** LKR 2.40 — below that, margin under 30% at monsoon peak.
5. `Remember: deadline is 24 October at 2pm, the CIO is the elasticity buyer, and legal will not sign without capping the liquidated damages at 20% monthly.`

### Flow 3B — Farah, NEW session, orals prep
1. `I'm presenting the technical orals. What should I emphasise and what evidence should I bring?`
   → **expect:** monsoon elasticity (T3, CIO's concern) + the 2025 flood-season throughput report; Tamil voice weakness of the incumbent for T2.
2. `How many scored points ride on the criteria I'm covering?`
   → **expect:** fetches the RFP — T1+T2+T3 = 30 of 60 technical points (model should show its reading).
3. `Anything that could kill the deal after we win it?`
   → **expect:** the uncapped liquidated damages clause → must be capped at 20% (memory + strategy note agree).

---

## Cross-client checks (run after seeding at least two clients)

1. **Isolation probe** — in a `client_golden_lotus_hotels` session:
   `Do we have any SLA credits pending with this client?`
   → **expect:** no knowledge of LankaPay's USD 980 credit. Any mention = leakage bug.
2. **Automated isolation** — `./run_vertex.sh run_step5_isolation.py` (exit 0).
3. **Refusal** — `run_step2.py`'s last scenario, or any session created without
   `client_id`: must answer "Session refused...".
4. **Wrong-folder upload** — ask any client to store `test_flows/TEST_FLOWS.md`:
   → **expect:** refused ("Only files inside sample_docs/ can be uploaded").

## Cast summary

| client_id | people | flavour |
|---|---|---|
| `client_lanka_pay` | dilini, kasun | SLA + incident credits |
| `client_golden_lotus_hotels` | ruwanthi, mohamed | cPaaS quote + integration |
| `client_ruhuna_insurance` | tharindu, farah | RFP bid strategy |
| `client_ab_bank` (original) | alice, bob | SDP proposal |
| `client_ceylon_micro` (original) | carol | isolation counterpart |
