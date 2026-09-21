#!/usr/bin/env python3
"""Summarize post-v4 bounded-turn close evidence without converting unknowns to zero."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ENFORCE_FROM = datetime.fromisoformat("2026-09-21T09:35:00+00:00")
SHORT_SECONDS = 480
ALLOWED_SHORT_REASONS = {
    "PLATFORM_ENFORCED_TERMINATION",
    "EXPLICIT_OPERATOR_INTERVENTION",
    "AUTHORITY_OR_FENCING_FAIL_CLOSED",
    "NO_SAFE_RUNNABLE_WORK_AFTER_EXPLICIT_SCAN",
}


def _ts(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed


def _seconds(start: str | None, end: str | None) -> int | None:
    if not start or not end:
        return None
    return int((_ts(end) - _ts(start)).total_seconds())


def summarize(run_lines: list[str], startup: dict) -> dict:
    runs = [json.loads(line) for line in run_lines if line.strip()]
    closed = []
    for run in runs:
        try:
            start = _ts(run["run_started_at"])
        except (KeyError, TypeError, ValueError):
            continue
        if start >= ENFORCE_FROM and run.get("run_ended_at"):
            closed.append(run)

    known_useful = [
        run["productive_substantive_seconds"]
        for run in closed
        if type(run.get("productive_substantive_seconds")) is int
    ]
    unexcused = []
    for run in closed:
        duration = run.get("duration_seconds")
        if type(duration) is not int:
            duration = _seconds(run.get("run_started_at"), run.get("run_ended_at"))
        if run.get("turn_outcome") != "CONTINUE" or duration is None or duration >= SHORT_SECONDS:
            continue
        alternatives = run.get("alternatives_checked")
        excused = (
            run.get("short_turn_reason") in ALLOWED_SHORT_REASONS
            and isinstance(alternatives, list)
            and bool(alternatives)
            and all(isinstance(item, str) and item.strip() for item in alternatives)
            and run.get("close_decision") == "EXCEPTION"
        )
        if not excused:
            unexcused.append({
                "observation_id": run.get("observation_id"),
                "duration_seconds": duration,
                "short_turn_reason": run.get("short_turn_reason"),
                "alternatives_checked": alternatives,
            })

    gaps = []
    for sample in startup.get("samples", []):
        scheduled = sample.get("scheduled_due_at")
        observed = sample.get("successor_observed_at")
        claim = sample.get("authority_claim_at")
        first = sample.get("first_durable_useful_at")
        predecessor = sample.get("predecessor_last_useful_at")
        gaps.append({
            "sample_id": sample.get("sample_id"),
            "due_to_observation_seconds": _seconds(scheduled, observed),
            "observation_to_claim_seconds": _seconds(observed, claim),
            "claim_to_first_useful_seconds": _seconds(claim, first),
            "predecessor_to_first_useful_seconds": _seconds(predecessor, first),
            "complete_boundary_set": all((scheduled, observed, claim, first, predecessor)),
        })

    return {
        "v4_closed_turn_count": len(closed),
        "v4_unexcused_short_close_count": len(unexcused),
        "v4_unexcused_short_closes": unexcused,
        "known_useful_seconds_total": sum(known_useful),
        "known_useful_turn_count": len(known_useful),
        "unknown_useful_turn_count": len(closed) - len(known_useful),
        "successor_gap_samples": gaps,
        "unknown_policy": "MISSING_USEFUL_OR_BOUNDARY_VALUES_REMAIN_NULL_NOT_ZERO",
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: summarize_turn_close.py RUNS_JSONL SUCCESSOR_STARTUP_JSON", file=sys.stderr)
        return 2
    runs = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    startup = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    print(json.dumps(summarize(runs, startup), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
