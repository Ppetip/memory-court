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
