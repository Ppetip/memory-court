# Memory Court

Agent memory that can explain, dispute, expire and retract what it believes.

**v0.1 development prototype · Python 3.11+ · GPL-3.0-only**

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

12 tests passed locally on Python 3.13. Other Python versions have not yet been exercised.

## Architecture

Claim and retraction writes serialize validation and insertion with `BEGIN IMMEDIATE`. Recorded timestamps are normalized to UTC and nondecreasing. Queries replay only events known at the requested time and apply half-open validity intervals. Conflicting active values produce no answer.

## Reproduced example

The invented shipping-city scenario moves through supported, conflict and supported states. Retracting the old claim resolves the conflict while historical queries still see what was known earlier.

See [the captured output](examples/demo-output.json). Rerun `python app.py` to reproduce it.

## Limits

Structured string claims only; no natural-language extraction, embeddings or semantic conflict detection. Evidence does not establish truth. Retractions preserve audit history and are not physical deletion. SQLite administrators can change schema: triggers are an application invariant, not tamper-proof storage. Operations in a file are committed individually, not as one batch.

## Next experiment

Add source-wide retraction, pagination and a last-write-wins comparison on adversarial temporal sequences.

The [design brief](docs/DESIGN.md) describes the larger goal, including unimplemented milestones.

## Contribute

Provide invented examples of facts that change or conflict in a workflow you understand. Use invented or openly licensed examples. Include expected outcomes, edge cases and data provenance.

## License

Copyright (c) 2026 Ppetip. Original code is licensed under GNU GPL version 3 only; see [LICENSE](LICENSE).
