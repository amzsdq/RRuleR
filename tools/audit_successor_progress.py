#!/usr/bin/env python3
"""Report successor invocations that lack durable startup progress."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def audit(payload: dict[str, Any], as_of: datetime, threshold_seconds: int) -> dict[str, Any]:
    samples = list(payload.get("samples", []))
    if payload.get("next_sample"):
        samples.append(payload["next_sample"])

    findings: list[dict[str, Any]] = []
    for sample in samples:
        observed = sample.get("successor_observed_at")
        if not observed:
            continue
        claim = sample.get("authority_claim_at")
        useful = sample.get("first_durable_useful_at")
        boundary = claim or observed
        age = max(0, int((as_of - parse_time(boundary)).total_seconds()))

        code = None
        if not claim:
            code = "MISSING_AUTHORITY_CLAIM_AFTER_INVOCATION"
        elif not useful:
            code = "MISSING_FIRST_USEFUL_AFTER_CLAIM"
        if code and age >= threshold_seconds:
            findings.append(
                {
                    "sample_id": sample.get("sample_id"),
                    "code": code,
                    "age_seconds": age,
                    "threshold_seconds": threshold_seconds,
                    "validity": sample.get("validity"),
                    "exclusion_reason": sample.get("exclusion_reason"),
                    "promotion_eligible": False,
                }
            )

    return {
        "schema_version": "1.0",
        "as_of": as_of.isoformat(),
        "threshold_seconds": threshold_seconds,
        "finding_count": len(findings),
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("startup_path", type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--threshold-seconds", type=int, default=120)
    args = parser.parse_args()
    if args.threshold_seconds < 0:
        raise SystemExit("threshold must be non-negative")
    payload = json.loads(args.startup_path.read_text())
    print(json.dumps(audit(payload, parse_time(args.as_of), args.threshold_seconds), indent=2))


if __name__ == "__main__":
    main()
