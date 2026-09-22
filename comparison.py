# SPDX-License-Identifier: GPL-3.0-only
"""Synthetic temporal retrieval versus last recorded claim, ignoring withdrawals."""
import json
from app import run, stamp

def latest_value(events, query):
    known = stamp(query.get("known_at") or query["as_of"])
    candidates = [e for e in events if e["kind"] == "claim" and e["recorded_at"] <= known
                  and e["payload"]["entity"] == query["entity"] and e["payload"]["attribute"] == query["attribute"]]
    return {"status":"supported" if candidates else "unknown",
            "answer":max(candidates,key=lambda e:e["sequence"])["payload"]["value"] if candidates else None}

def fixtures():
    def at(day): return f"2026-01-{day:02}T00:00:00Z"
    def query(day): return {"operation":"query","entity":"fictional","attribute":"city","as_of":at(day)}
    old = {"operation":"claim","id":"old","entity":"fictional","attribute":"city","value":"Boston",
           "source":"synthetic-old","recorded_at":at(1),"valid_from":at(1),"valid_until":at(4)}
    new = dict(old,id="new",value="Portland",source="synthetic-new",recorded_at=at(2),valid_from=at(2))
    operations = [old,query(1),new,query(2),{"operation":"retract","id":"new","recorded_at":at(3),"reason":"Synthetic correction"},query(3),query(4)]
    # Authored expectations are separate from either retrieval implementation.
    expected = [{"status":"supported","answer":"Boston"},{"status":"conflict","answer":None},
                {"status":"supported","answer":"Boston"},{"status":"unknown","answer":None}]
    return operations, expected

def demo():
    operations, expected = fixtures()
    result = run(operations)
    queries = [op for op in operations if op["operation"] == "query"]
    baseline = [latest_value(result["events"],q) for q in queries]
    comparisons = []
    for name,answers in (("temporal-court",result["queries"]),("latest-recorded-value",baseline)):
        trials = [{"query_index":i,"expected":gold,"actual":{k:actual[k] for k in ("status","answer")},
                   "matched":all(actual[k]==gold[k] for k in gold)} for i,(actual,gold) in enumerate(zip(answers,expected))]
        comparisons.append({"policy":name,"matched":sum(t["matched"] for t in trials),"queries":len(trials),"trials":trials})
    return {"data":"four-author-labeled-synthetic-temporal-queries","comparisons":comparisons,
            "limitation":"Small specification example chosen to exercise conflict, retraction and expiry. Baseline uses the latest recorded claim known at the query cutoff and ignores validity and withdrawals. Not a representative accuracy estimate or proof of source truth."}

if __name__ == "__main__":
    print(json.dumps(demo(),indent=2))
