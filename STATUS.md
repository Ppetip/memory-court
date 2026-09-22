# Status

Stage: command-line prototype with optional live Jev integration.
Verified: 44 offline tests pass; dry run and live synthetic Jev workflow pass.

Latest: Run `python comparison.py` (Codex route `comparison`).

Next: Expand independently reviewed temporal scenarios, including source revocation and late-arriving evidence.

Repository: https://github.com/Ppetip/memory-court
Budget: one shared $3 cumulative Jev allowance across the portfolio, never per project or cycle.
No other paid compute authorized. Eight initial calls across all projects used 3,303 input tokens;
estimated total $0.000138726, with $0.08 conservatively reserved. See README for limits.
Live smoke responses are not production benchmarks. No model training performed.

2026-09-21 CI pass: added pinned, read-only Windows/Linux Python 3.11/3.13 checks for unit tests and offline CLI contracts. Local checks and all four hosted Windows/Linux Python 3.11/3.13 jobs pass. No additional Jev calls.

Hosted verification: https://github.com/Ppetip/memory-court/actions/runs/35590283432

2026-09-21 14:42 UTC budget fix: live clients require an existing ledger; explicit initialization refuses overwrite. Added four regression cases for missing/deleted/empty ledgers and preserved spending. All local tests, CLI checks, and four hosted Windows/Linux Python 3.11/3.13 jobs pass. No additional Jev calls.

Budget-fix hosted verification: https://github.com/Ppetip/memory-court/actions/runs/35614390873

2026-09-21 18:44 UTC: Event history supports bounded keyset pagination with stable sequence cursors. Local tests, offline CLI checks, and all four hosted matrix jobs pass. No additional Jev calls.

Feature-pass verification: https://github.com/Ppetip/memory-court/actions/runs/35640902098

2026-09-21 22:45 UTC: documented how to interpret this tool's outcomes separately from command success. The local Codex runner now shows a concise outcome summary for this project. Verified through common-runner checks and synthetic demo output; histories stay local.

2026-09-22 02:46 UTC: Optional query explanations identify retracted, revoked, expired and not-yet-valid claims. Common-runner checks, new route and all four hosted jobs pass. No new Jev calls.

Evaluation-path verification: https://github.com/Ppetip/memory-court/actions/runs/35681202238

2026-09-22 10:48 UTC: Query operations now accept optional `known_at`. `as_of` selects the effective validity time; `known_at` selects which recorded claims, retractions and source revocations are known. Omit it to preserve the original behavior where both times equal `as_of`. Later knowledge can correct an earlier view without rewriting its original answer. A known future-effective claim can also be queried, but that is a view of stored assertions, not a prediction. Run `python app.py --input examples/knowledge-time.json` for a synthetic late-arriving claim: original view unknown, hindsight view Boston, corrected hindsight unknown after retraction. Published and verified: local checks and all four hosted matrix jobs pass. No new Jev calls.

Reliability verification: https://github.com/Ppetip/memory-court/actions/runs/35718650769

2026-09-22 22:50 UTC: Run `python comparison.py` (Codex route `comparison`). Four authored query expectations cover a supported fact, conflict, retraction and expiry. Temporal Court matches 4/4; the latest-recorded-value baseline matches 1/4. The baseline respects the knowledge cutoff but deliberately ignores validity, retractions and source revocation. This small specification example is chosen to show those differences and is not a representative accuracy estimate. See `examples/extended-evaluation.json`. Common-runner checks pass. Publication and hosted verification pending. No new Jev calls.
