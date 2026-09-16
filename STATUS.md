# Status

Stage: v0.1 offline command-line prototype.

Verified: 12 tests pass; default synthetic demo runs.

Current: Persists structured claims and retractions in SQLite, detects conflicting active values, expires old claims and answers time-specific queries with evidence. Database triggers prevent ordinary updates/deletes of audit events.

Next: Add source-wide retraction, pagination and a last-write-wins comparison on adversarial temporal sequences.

Repository target: https://github.com/Ppetip/memory-court
Budget: local/free; no paid APIs or model downloads used.
