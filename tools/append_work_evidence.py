#!/usr/bin/env python3
"""Append one strictly observed useful-work interval to WORK_EVIDENCE.json.

This helper intentionally does not discover or infer work time. The caller must supply
both observed boundaries and a materially-new artifact reference. It computes duration,
rejects overlap/duplicates/backward epochs, and validates the complete ledger before writing.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from validate_work_evidence import audit, validate_record


def ts(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return dt


def build_record(args: argparse.Namespace) -> dict:
    start, end = ts(args.start_at), ts(args.end_at)
    seconds = int((end - start).total_seconds())
    if seconds <= 0:
        raise ValueError("end_at must be after start_at")
    return {
        "record_id": args.record_id,
        "authority_epoch": args.authority_epoch,
        "run_id": args.run_id,
        "start_at": args.start_at,
        "end_at": args.end_at,
        "start_boundary": "OBSERVED",
        "end_boundary": "OBSERVED",
        "kind": args.kind,
        "artifact": args.artifact,
        "qualification": "SUBSTANTIVE_ACCEPTED",
        "basis": args.basis,
        "observed_seconds": seconds,
    }


def append_record(data: dict, record: dict) -> dict:
    errors = validate_record(record)
    if errors:
        raise ValueError("invalid record: " + ",".join(errors))
    records = data.setdefault("records", [])
    if any(r.get("record_id") == record["record_id"] for r in records):
        raise ValueError("duplicate record_id")
    prior_epochs = [r.get("authority_epoch") for r in records if isinstance(r.get("authority_epoch"), int)]
    if prior_epochs and record.get("authority_epoch", -1) < max(prior_epochs):
        raise ValueError("authority_epoch would move evidence backward")
    start, end = ts(record["start_at"]), ts(record["end_at"])
    for existing in records:
        try:
            a, b = ts(existing["start_at"]), ts(existing["end_at"])
        except (KeyError, TypeError, ValueError):
            continue
        if start < b and end > a:
            raise ValueError(f"interval overlaps {existing.get('record_id','unknown')}")
    records.append(record)
    result = audit(data)
    if result["duplicate_record_ids"] or result["overlap_errors"] or any(x["errors"] for x in result["record_results"]):
        raise ValueError("resulting ledger fails strict audit")
    collection = data.setdefault("collection", {})
    collection["latest_observed_record"] = record["record_id"]
    return data


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("state_json")
    p.add_argument("--record-id", required=True)
    p.add_argument("--authority-epoch", required=True, type=int)
    p.add_argument("--run-id", required=True)
    p.add_argument("--start-at", required=True)
    p.add_argument("--end-at", required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--artifact", required=True)
    p.add_argument("--basis", required=True)
    args = p.parse_args()
    path = Path(args.state_json)
    data = json.loads(path.read_text(encoding="utf-8"))
    updated = append_record(data, build_record(args))
    path.write_text(json.dumps(updated, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
