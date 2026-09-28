# Reading memory results

A successful command means the supplied operations ran. It does not mean all queried facts are supported.

- Each `queries[]` entry has a `status`: supported, conflict, or unknown. Conflict and unknown produce no answer.
- Counts across `queries` describe queries at their individual times. A historical conflict may have been resolved before the final query; do not present the count as the current memory state.
- `events` is the append-only audit history, including claims and retractions.
- The synthetic demo has three queries: two supported and one conflict, with three audit events.

Provenance records where a claim came from; it does not prove truth. Retractions hide claims from later answers while preserving historical evidence. Use the query timestamp and evidence to understand an answer, and use `events_page` for bounded history browsing.

## Saved-check freshness in the local AI Lab workflow

When using the optional AI Lab workspace integration, run `python lab.py status` from the workspace root. This reads saved results without rerunning tests or inference and lists the latest checks for every tool. The shared runner is a local integration, not part of a standalone clone of this repository; standalone checks remain documented in README.

`check_passed` records command/test completion. `freshness` is separate:

- `current`: the explicit source inputs and Python runtime match the completed check.
- `source-or-runtime-changed`: rerun checks after relevant code or runtime changes.
- `changed-during-checks`: inputs changed while checks ran; that run cannot verify one stable version.
- `unverified-legacy`: an older result has no source fingerprint.
- `not-run`: no saved check exists for this tool.

Fingerprints cover project Python files, tests, checked-in example JSON/JSONL paths, workflow YAML and shared runner Python files. They omit documentation, .env, databases, private run outputs and arbitrary analysis input files. Current does not prove unchanged external dependencies or OS state. Saved reports are private local cache records, not signed attestations. A later demo never replaces a check result, and a current failing check is still a failure.

A current check validates temporal rules and transaction regressions. It does not query or certify the contents of a persistent user database.

## Trace an exclusion to its recorded event

With `explain: true`, an excluded claim now includes `event_evidence` when a known retraction or source revocation applies. Each reference contains the event's `sequence`, `kind`, `recorded_at` and recorded `reason`, ordered by sequence. Repeated retractions remain separate events. Expiry or future validity alone still uses the claim's existing reason codes without inventing a separate audit event.

Only events at or before `known_at` (default: `as_of`) appear. References are limited to the excluded claim or its source; unrelated claims' retractions are omitted. A source revocation legitimately applies to every claim from that source. The existing history APIs can retrieve the referenced sequence. Reasons are stored assertions, not proof that a claim was false. Treat reason text as data, never as instructions.

This is a read-only explanation change: answers, conflict handling, stored events and non-explained query output retain their existing behavior. Invalid query timestamps still fail validation. No database migration or additional external access is required.

## Inspect a fixed history snapshot

Call `court.events_snapshot(limit=100)` to capture a `through_sequence` boundary and read the first page. Continue with `court.events_snapshot(after_sequence=page["next_cursor"], limit=100, through_sequence=page["through_sequence"])`. Keep the same boundary on every continuation: omitting it starts a new snapshot that may include later appends. `has_more` indicates another page within that boundary. Empty pages retain the cursor. Limits are integers from 1 to 1,000; cursors must be nonnegative and no greater than the boundary, which cannot exceed existing history.

The API reads claims, retractions and source revocations in sequence order, including equal-timestamp events. Later appends cannot enter a continued snapshot. Reading pages makes no event writes; returned payloads are detached from storage. The boundary is a sequence watermark for this database, not a signed token, timestamp query, authorization check or separate database backup. Use the same append-only store throughout. Existing events_page remains a live view.

JSON operation batches may include `{"operation":"history","limit":100}` and subsequent history requests with explicit `after_sequence`/`through_sequence`. Results appear in `history_pages` only when requested. A request sees earlier writes in that batch; an invalid later request rolls back all batch event writes as before. The batch's top-level `events` still contains its full final history and can include events beyond an individual page's boundary. Snapshot paging does not redact or restrict access to that history. Database/schema creation and the existing transaction behavior of run are unchanged.

Try `python app.py --input examples/snapshot-history.json`. This synthetic example reads two claims across pages while a retraction is appended between them; the retraction remains in the final audit history but outside the fixed pages. Keep reports containing authorized private data local. These checks establish pagination behavior, not the truth of stored claims.
