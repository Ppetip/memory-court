# Memory Court

Agent memory that can explain, dispute, expire and retract what it believes.

**v0.1 development prototype Ãƒâ€šÃ‚Â· Python 3.11+ Ãƒâ€šÃ‚Â· GPL-3.0-only**

## What works

Persists structured claims and retractions in SQLite, detects conflicting active values, expires old claims and answers time-specific queries with evidence. Database triggers prevent ordinary updates/deletes of audit events.

## Run

No third-party Python dependencies. Clone this repository and run from its root:

```sh
python app.py
python app.py --input examples/operations.json --db runs/memory.db
```

For commands using a file under `runs/`, create that directory first (`mkdir runs`). Generated files are ignored by Git. The default demo is offline and uses invented data.

## Test

```sh
python -m unittest discover -s tests -v
```

41 tests pass on Windows and Linux with Python 3.11 and 3.13 (GitHub Actions).

## Architecture

Claim and retraction writes serialize validation and insertion with `BEGIN IMMEDIATE`. Recorded timestamps are normalized to UTC and nondecreasing. Queries replay only events known at the requested time and apply half-open validity intervals. Conflicting active values produce no answer.

## Reproduced example

The invented shipping-city scenario moves through supported, conflict and supported states. Retracting the old claim resolves the conflict while historical queries still see what was known earlier.

See [the captured output](examples/demo-output.json). Rerun `python app.py` to reproduce it.

## Limits

The core court stores structured string claims; no natural-language extraction or embeddings. Optional Jev semantic review is advisory and cannot resolve claims. Evidence does not establish truth. Retractions preserve audit history and are not physical deletion. SQLite administrators can change schema: triggers are an application invariant, not tamper-proof storage. Operations in a file are committed individually, not as one batch.

## Next experiment

Add source-wide retraction, pagination and a last-write-wins comparison on adversarial temporal sequences.

The [design brief](docs/DESIGN.md) describes the larger goal, including unimplemented milestones.

## Contribute

Provide invented examples of facts that change or conflict in a workflow you understand. Use invented or openly licensed examples. Include expected outcomes, edge cases and data provenance.

## License

Copyright (c) 2026 Ppetip. Original code is licensed under GNU GPL version 3 only; see [LICENSE](LICENSE).

## Latest development pass

Temporal source-wide revocation with historical query preservation.

Use JSON operation `revoke_source` with `source`, `recorded_at`, and `reason`. Later claims from that source are rejected. Audit history is retained.

## Optional Jev workflow

Run `python jev_workflow.py` to preview the synthetic request without network access.
To opt into live calls, create a local `.env` using `.env.example`, set your TypeSafe key,
and point `JEV_BUDGET_DB` at one absolute SQLite path shared by all five projects.
Then run `python jev_workflow.py --live --env-file /absolute/path/to/.env`.
Do not commit the real configuration. No packages or model downloads are required.

The adapter pins `jev-1.13.0` and sends only the built-in synthetic fixture in this CLI.
Agent Black Box makes four replay calls; each other workflow makes one. The reusable
`Client.evaluate(state, questions)` interface supports bounded Choice questions.
Treat low-confidence decisions as abstentions; its 0.8 cutoff is a heuristic, not calibrated certainty.

The shared ledger allows at most $3 in cumulative reservations: one cent is permanently
reserved **before each attempt**, including timeouts and failed requests. It never retries
automatically. Concurrent processes share an atomic SQLite reservation. Never reset,
delete, replace or split the ledger to regain budget. This guard covers this client,
not unrelated account use. Provider billing remains authoritative.

[Official TypeSafe pricing](https://docs.typesafe.ai/models) checked 2026-09-21 lists
$0.042 per million input tokens and free output. One cent exceeds a full 65,536-input-token
request at that rate; the client also limits serialized input to 16KB. Estimates use
reported input tokens and exclude unknown failed-request usage. Calls fail closed on
2026-09-28 until pricing and the reservation bound are reviewed. Never extend the review
date without checking the provider's current terms.

[The HTTP API](https://docs.typesafe.ai/api) uses the fixed official TypeSafe endpoint.
Redirects are refused, responses are schema-checked, and error bodies/credentials are
not logged. Tests mock the provider and do not spend money.

`examples/jev-live-smoke.json` records a real 2026-09-21 model response on synthetic input.
It is a connectivity and workflow smoke check, not a quality benchmark or evidence of
training, generalization, speed or production reliability. Re-running it may change results.

Jev flags a synthetic conflict without overriding the temporal court or writing claims.

## Continuous verification

[Offline checks](https://github.com/Ppetip/memory-court/actions/workflows/offline.yml) run tests and JSON CLI smoke checks on Windows/Linux with Python 3.11/3.13 for pushes and pull requests. Run `python verify_demos.py` locally. Actions are pinned to immutable commits, use read-only permissions, and receive no provider secrets. Jev tests use mocks; the CLI check uses its default dry run. The workflow does not run live inference.

### First-time budget setup and recovery

For a genuinely new allowance only, run `python jev_client.py --init-budget /absolute/path/to/jev-budget.sqlite3` once, then use that exact path in `JEV_BUDGET_DB` for every app. Initialization refuses existing files, including empty files. Do not initialize a new ledger to replace lost spending history. Existing users keep their existing ledger and skip setup.

Live clients now open existing ledgers only, including at reservation time. A missing, mistyped, or empty ledger stops calls instead of silently recreating a zero balance. Restore missing history from a trusted backup; do not reset it. This prevents accidental recreation, not deliberate administrator modification or substitution of a different valid database.

## Latest reliability improvement

Use `court.events_page(after_sequence=0, limit=100)` to read up to 1,000 events and receive `next_cursor`. Continue with that cursor; empty pages retain it. Events appended later can appear on subsequent pages, so pagination is not a frozen snapshot. Existing full-history retrieval is unchanged.

See [Reading results](docs/RESULTS.md) for outcome fields, denominators, abstentions and the limits of command success.

## New evaluation path

Call `court.query(..., explain=True)` or set `explain: true` on a JSON query operation. `excluded` lists matching known claim IDs and all applicable reasons: retracted, source_revoked, expired, not_yet_valid. Claims not yet recorded at the knowledge cutoff remain hidden (by default, the query time). Answers and evidence remain unchanged. Try `python app.py --input examples/explained-operations.json`.

## Evaluation reliability

Query operations now accept optional `known_at`. `as_of` selects the effective validity time; `known_at` selects which recorded claims, retractions and source revocations are known. Omit it to preserve the original behavior where both times equal `as_of`. Later knowledge can correct an earlier view without rewriting its original answer. A known future-effective claim can also be queried, but that is a view of stored assertions, not a prediction. Run `python app.py --input examples/knowledge-time.json` for a synthetic late-arriving claim: original view unknown, hindsight view Boston, corrected hindsight unknown after retraction.
