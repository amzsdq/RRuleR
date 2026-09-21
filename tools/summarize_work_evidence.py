#!/usr/bin/env python3
"""Summarize strict work-evidence freshness without inferring missing time."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from validate_work_evidence import audit


def summarize(data: dict, current_epoch: int | None = None) -> dict:
    checked = audit(data)
    invalid = [x for x in checked["record_results"] if x["errors"]]
    if invalid or checked["duplicate_record_ids"] or checked["overlap_errors"]:
        raise ValueError("work evidence ledger is not strictly valid")
    records = data.get("records", [])
    by_run: dict[str, int] = defaultdict(int)
    epochs = []
    durations = []
    for record in records:
        seconds = int(record.get("observed_seconds", 0))
        by_run[str(record.get("run_id", "UNKNOWN"))] += seconds
        durations.append(seconds)
        if isinstance(record.get("authority_epoch"), int):
            epochs.append(record["authority_epoch"])
    latest_epoch = max(epochs) if epochs else None
    lag = None if current_epoch is None or latest_epoch is None else max(0, current_epoch - latest_epoch)
    return {
        "record_count": len(records),
        "observed_useful_seconds_total": sum(durations),
        "latest_evidence_epoch": latest_epoch,
        "current_authority_epoch": current_epoch,
        "evidence_epoch_lag": lag,
        "fresh_for_current_epoch": lag == 0 if lag is not None else None,
        "observed_useful_seconds_by_run": dict(sorted(by_run.items())),
        "shortest_observed_interval_seconds": min(durations) if durations else None,
        "longest_observed_interval_seconds": max(durations) if durations else None,
        "unknown_time_policy": "NOT_INFERRED_NOT_COUNTED",
    }


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: summarize_work_evidence.py STATE_JSON [CURRENT_EPOCH]", file=sys.stderr)
        return 2
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    epoch = int(sys.argv[2]) if len(sys.argv) == 3 else None
    print(json.dumps(summarize(data, epoch), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
