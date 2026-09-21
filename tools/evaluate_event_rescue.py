#!/usr/bin/env python3
"""Evaluate whether the guarded event-wake rescue producer may emit."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def evaluate(current: dict[str, Any], activity: dict[str, Any], ledger: dict[str, Any],
             startup: dict[str, Any], as_of: datetime) -> dict[str, Any]:
    result = {"emit": False, "reason": "NOT_ELIGIBLE", "event_reason": None}
    if current.get("program_status") not in {"CONTINUE", "DEGRADED_CONTINUATION"}:
        return result | {"reason": "PROGRAM_TERMINAL"}
    if ledger.get("status") != "ACTIVE":
        return result | {"reason": "LEDGER_INACTIVE"}
    if ledger.get("consumer_status") != "VERIFIED":
        return result | {"reason": "EVENT_CONSUMER_UNVERIFIED"}
    if ledger.get("outstanding_generation") not in (None, 0):
        return result | {"reason": "OUTSTANDING_GENERATION"}

    sample = startup.get("next_sample") or {}
    observed = sample.get("successor_observed_at")
    boot = sample.get("boot_started_at")
    if observed and not boot:
        age = max(0, int((as_of - _ts(observed)).total_seconds()))
        if age >= 120:
            return {
                "emit": True,
                "reason": "ELIGIBLE",
                "event_reason": "STARTUP_ACK_MISSING",
                "age_seconds": age,
                "sample_id": sample.get("sample_id"),
            }

    progress = activity.get("last_progress_at")
    if progress:
        age = max(0, int((as_of - _ts(progress)).total_seconds()))
        if age >= 180:
            return {
                "emit": True,
                "reason": "ELIGIBLE",
                "event_reason": "STALE_ACTIVE_OWNER",
                "age_seconds": age,
                "sample_id": sample.get("sample_id"),
            }
    return result | {"reason": "HEALTHY_OR_WITHIN_GRACE"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("current", type=Path)
    parser.add_argument("activity", type=Path)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("startup", type=Path)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args()
    docs = [json.loads(path.read_text()) for path in (args.current, args.activity, args.ledger, args.startup)]
    print(json.dumps(evaluate(*docs, _ts(args.as_of)), sort_keys=True))


if __name__ == "__main__":
    main()
