#!/usr/bin/env python3
"""Summarize strict work-evidence freshness and bounded-turn utilization without inference."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from validate_work_evidence import audit


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


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


def summarize_runs(run_lines: list[str], minimum_continue_seconds: int = 480) -> dict:
    """Classify bounded run records without inventing missing durations."""
    parsed = [json.loads(line) for line in run_lines if line.strip()]
    completed = [r for r in parsed if r.get("run_ended_at") is not None]
    short_continue = []
    durations = []
    for run in completed:
        duration = run.get("duration_seconds")
        if duration is None:
            try:
                duration = int((_ts(run["run_ended_at"]) - _ts(run["run_started_at"])).total_seconds())
            except (KeyError, TypeError, ValueError):
                duration = None
        if isinstance(duration, int):
            durations.append(duration)
            if run.get("turn_outcome") == "CONTINUE" and duration < minimum_continue_seconds:
                short_continue.append({
                    "observation_id": run.get("observation_id"),
                    "duration_seconds": duration,
                    "short_turn_reason": run.get("short_turn_reason"),
                    "alternatives_checked": run.get("alternatives_checked"),
                    "guard_compliant": bool(run.get("short_turn_reason")) and bool(run.get("alternatives_checked")),
                })
    return {
        "completed_run_count": len(completed),
        "completed_duration_seconds_total": sum(durations),
        "average_completed_duration_seconds": (sum(durations) / len(durations)) if durations else None,
        "minimum_continue_seconds": minimum_continue_seconds,
        "short_continue_count": len(short_continue),
        "short_continue_runs": short_continue,
        "short_turn_guard_pass": all(x["guard_compliant"] for x in short_continue),
    }


def main() -> int:
    if len(sys.argv) not in (2, 3, 4):
        print("usage: summarize_work_evidence.py STATE_JSON [CURRENT_EPOCH] [RUNS_JSONL]", file=sys.stderr)
        return 2
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    epoch = int(sys.argv[2]) if len(sys.argv) >= 3 else None
    out = summarize(data, epoch)
    if len(sys.argv) == 4:
        out["run_utilization"] = summarize_runs(Path(sys.argv[3]).read_text(encoding="utf-8").splitlines())
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
