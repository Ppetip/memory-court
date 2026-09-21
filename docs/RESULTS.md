# Reading memory results

A successful command means the supplied operations ran. It does not mean all queried facts are supported.

- Each `queries[]` entry has a `status`: supported, conflict, or unknown. Conflict and unknown produce no answer.
- Counts across `queries` describe queries at their individual times. A historical conflict may have been resolved before the final query; do not present the count as the current memory state.
- `events` is the append-only audit history, including claims and retractions.
- The synthetic demo has three queries: two supported and one conflict, with three audit events.

Provenance records where a claim came from; it does not prove truth. Retractions hide claims from later answers while preserving historical evidence. Use the query timestamp and evidence to understand an answer, and use `events_page` for bounded history browsing.
