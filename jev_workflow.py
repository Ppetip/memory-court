# SPDX-License-Identifier: GPL-3.0-only
import argparse
import json
from pathlib import Path
from jev_client import Client, JevError, MODEL, choice, selected
import app

def request_data():
    return {"entity": "fictional-customer", "attribute": "shipping_city", "left": "Boston", "right": "Portland", "same_time": True}, choice(
        "Review two active claims about one customer's single shipping city at the same time. Do they conflict? Do not choose a winner or infer which source is true.",
        {"conflict": "Incompatible values", "equivalent": "Same value expressed differently", "review": "Unclear without more evidence"})

def run(client):
    state, questions = request_data()
    response = client.evaluate(state, questions)
    before = app.run(app.demo())
    return {"semantic_review": selected(response, "review"),
            "structured_conflict": before["queries"][1], "mutates_memory": False,
            "usage": [response["usage"]],
            "limitation": "Advisory synthetic review; the structured court remains authoritative. No source revocation, claim resolution or production-memory upload."}

def main():
    parser = argparse.ArgumentParser(description="Preview the synthetic Jev request; --live explicitly opts into paid calls.")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if not args.live:
        state, questions = request_data()
        print(json.dumps({"mode": "dry-run-no-network", "model": MODEL, "state": state, "questions": questions}, indent=2))
        return
    if args.env_file is None:
        parser.error("--live requires --env-file with the shared budget ledger")
    try:
        client = Client(args.env_file)
        result = run(client)
        print(json.dumps({"mode": "live-model-on-synthetic-data", "model": MODEL, **result, "budget": client.budget.summary()}, indent=2))
    except JevError as exc:
        parser.exit(1, str(exc) + "\n")

if __name__ == "__main__":
    main()
