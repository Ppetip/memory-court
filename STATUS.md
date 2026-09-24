# Status

Stage: command-line prototype with optional live Jev integration.
Verified: 52 tests and five offline CLI paths pass locally; all four hosted checks pass. Jev smoke results remain historical; no new live calls.

Latest: Explained exclusions link to visible retraction and source-revocation events.

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

2026-09-22 22:50 UTC: Run `python comparison.py` (Codex route `comparison`). Four authored query expectations cover a supported fact, conflict, retraction and expiry. Temporal Court matches 4/4; the latest-recorded-value baseline matches 1/4. The baseline respects the knowledge cutoff but deliberately ignores validity, retractions and source revocation. This small specification example is chosen to show those differences and is not a representative accuracy estimate. See `examples/extended-evaluation.json`. Common-runner checks pass. Published and verified: all four hosted Windows/Linux Python 3.11/3.13 jobs pass. No new Jev calls.

Extended evaluation verification: https://github.com/Ppetip/memory-court/actions/runs/35795070942

2026-09-23 06:53 UTC: A run of operations now shares one SQLite write transaction. If any later operation fails, all earlier writes from that batch roll back; existing events remain intact. Queries within a successful batch see its pending claims, and the whole batch commits on success. Direct claim/retract calls still own individual transactions. Database/schema creation can occur before batch validation; rollback covers event writes, not file creation. A successful batch replayed again is not silently deduplicated: existing claim IDs still reject duplicates. Checks pass; run ID 3a10bc0eebe149bfa6d5f7d629a944bd. No live calls. Hosted verification passed on all four OS/Python combinations.

2026-09-23 10:54 UTC verification follow-up: Published code and all four hosted jobs verified after the earlier approval-review usage-limit interruption. Existing check suites were not rerun solely to create history. Run: https://github.com/Ppetip/memory-court/actions/runs/35829397926

2026-09-23 14:55 UTC: Added guidance for interpreting saved-check freshness in the optional local Codex runner. A current check validates temporal rules and transaction regressions. It does not query or certify the contents of a persistent user database. The shared runner now records check-source fingerprints and provides read-only status. All five current app checks passed (234 tests total), along with 24 local runner regressions. Run ID: 811900b822db42e390b5e1714afbbe25. App implementation unchanged; this documentation update skips redundant hosted CI. No live calls or new performance claim.

2026-09-24 15:00 UTC: Explained exclusions now include ordered audit-event references and reasons, limited by claim/source and knowledge cutoff. Answers and stored events remain unchanged. Local check a95d89877d0f4655bdb2ebd5593690d7 passed. All four hosted Windows/Linux Python 3.11/3.13 jobs pass. No user databases or live providers accessed.

Exclusion-evidence verification: https://github.com/Ppetip/memory-court/actions/runs/36017422071
