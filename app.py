"""Append-only temporal claims and evidence-linked retrieval for agent memory."""
import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def stamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be ISO 8601 text")
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("timezone required")
    return t.astimezone(timezone.utc).isoformat(timespec="microseconds")


class Court:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, kind TEXT NOT NULL, recorded_at TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS immutable_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'events are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS immutable_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'events are immutable'); END;
        """)

    def close(self):
        self.db.close()

    def events(self):
        return [{"sequence": seq, "kind": kind, "recorded_at": at, "payload": json.loads(p)}
                for seq, kind, at, p in self.db.execute("SELECT seq,kind,recorded_at,payload FROM events ORDER BY seq")]

    def _append(self, kind, recorded_at, payload):
        at = stamp(recorded_at)
        # Serialize validation and insertion across writers to the same database.
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            events = self.events()
            if events and at < events[-1]["recorded_at"]:
                raise ValueError("recorded timestamps must be nondecreasing")
            known = {e["payload"]["id"] for e in events if e["kind"] == "claim"}
            revoked_sources = {e["payload"]["source"] for e in events if e["kind"] == "revoke_source"}
            if kind == "claim" and payload["source"] in revoked_sources:
                raise ValueError("source has been revoked; use a new source version")
            if kind == "revoke_source" and payload["source"] not in {e["payload"]["source"] for e in events if e["kind"] == "claim"}:
                raise ValueError("unknown source")
            if kind == "claim" and payload["id"] in known:
                raise ValueError("claim ID already exists")
            if kind == "retract" and payload["id"] not in known:
                raise ValueError("unknown claim")
            self.db.execute("INSERT INTO events(kind,recorded_at,payload) VALUES(?,?,?)", (kind, at, json.dumps(payload, sort_keys=True)))

    def claim(self, id, entity, attribute, value, source, recorded_at, valid_from, valid_until=None):
        if not all(isinstance(f, str) and f.strip() for f in (id, entity, attribute, value, source)):
            raise ValueError("nonempty string claim fields required")
        start = stamp(valid_from)
        end = stamp(valid_until) if valid_until is not None else None
        if end and end <= start:
            raise ValueError("valid_until must be later than valid_from")
        self._append("claim", recorded_at, {"id": id, "entity": entity, "attribute": attribute,
                     "value": value, "source": source, "valid_from": start, "valid_until": end})

    def retract(self, id, recorded_at, reason):
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("retraction reason required")
        self._append("retract", recorded_at, {"id": id, "reason": reason})

    def revoke_source(self, source, recorded_at, reason):
        """Revoke all claims from a source from this recorded time onward."""
        if not all(isinstance(v, str) and v.strip() for v in (source, reason)):
            raise ValueError("nonempty source and reason required")
        self._append("revoke_source", recorded_at, {"source": source, "reason": reason})

    def query(self, entity, attribute, as_of):
        at = stamp(as_of)
        claims, retracted, revoked_sources = {}, set(), set()
        for event in self.events():
            if event["recorded_at"] > at:
                continue
            p = event["payload"]
            if event["kind"] == "claim":
                claims[p["id"]] = p
            elif event["kind"] == "retract":
                retracted.add(p["id"])
            elif event["kind"] == "revoke_source":
                revoked_sources.add(p["source"])
        active = [p for id, p in claims.items() if id not in retracted and p["source"] not in revoked_sources and p["entity"] == entity
                  and p["attribute"] == attribute and p["valid_from"] <= at
                  and (p["valid_until"] is None or at < p["valid_until"])]
        values = sorted({p["value"] for p in active})
        return {"entity": entity, "attribute": attribute, "as_of": at,
                "status": "unknown" if not values else "supported" if len(values) == 1 else "conflict",
                "answer": values[0] if len(values) == 1 else None, "evidence": active}


def run(operations, path=":memory:"):
    court, results = Court(path), []
    try:
        for op in operations:
            item = dict(op)
            kind = item.pop("operation")
            if kind == "claim":
                court.claim(**item)
            elif kind == "retract":
                court.retract(**item)
            elif kind == "revoke_source":
                court.revoke_source(**item)
            elif kind == "query":
                results.append(court.query(**item))
            else:
                raise ValueError("unknown operation")
        return {"queries": results, "events": court.events(),
                "limitation": "Structured claims only. Provenance does not prove truth. Retraction hides claims from current answers but retains audit history; it is not physical deletion."}
    finally:
        court.close()


def demo():
    def claim(id, value, day):
        at = f"2026-01-{day:02}T00:00:00Z"
        return {"operation": "claim", "id": id, "entity": "fictional-customer", "attribute": "shipping_city",
                "value": value, "source": "synthetic-form-" + id, "recorded_at": at, "valid_from": at}
    def query(day):
        return {"operation": "query", "entity": "fictional-customer", "attribute": "shipping_city", "as_of": f"2026-01-{day:02}T12:00:00Z"}
    return [claim("old", "Boston", 1), query(1), claim("new", "Portland", 2), query(2),
            {"operation": "retract", "id": "old", "recorded_at": "2026-01-03T00:00:00Z", "reason": "Superseded by verified update"}, query(3)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, help="JSON array of claim/retract/query operations")
    p.add_argument("--db", default=":memory:")
    a = p.parse_args()
    print(json.dumps(run(json.loads(a.input.read_text(encoding="utf-8")) if a.input else demo(), a.db), indent=2))


if __name__ == "__main__":
    main()
