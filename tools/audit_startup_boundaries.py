#!/usr/bin/env python3
"""Audit observed successor-startup boundaries without altering raw evidence."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

MAINTENANCE_EXCLUSIONS = {"OPERATOR_MAINTENANCE_INTERRUPTION", "MAINTENANCE_PAUSE"}


def _ts(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed


def audit(startup: dict, run_lines: list[str]) -> dict:
    runs = {
        run.get("observation_id"): run
        for run in (json.loads(line) for line in run_lines if line.strip())
        if run.get("observation_id")
    }
    results = []
    for sample in startup.get("samples", []):
        errors = []
        predecessor_id = sample.get("predecessor_run_id")
        run = find_run(predecessor_id)
        predecessor_end = run.get("run_ended_at") if run else None
        last_useful = sample.get("predecessor_last_useful_at")
        if predecessor_end and last_useful and _ts(last_useful) > _ts(predecessor_end):
            errors.append("PREDECESSOR_LAST_USEFUL_AFTER_RECORDED_END")
        exclusion = sample.get("exclusion_reason")
        maintenance_interrupted = (
            sample.get("maintenance_interrupted") is True
            or exclusion in MAINTENANCE_EXCLUSIONS
        )
        comparison_ready = bool(sample.get("scheduled_due_at") and sample.get("successor_observed_at"))
        results.append({
            "sample_id": sample.get("sample_id"),
            "raw_sample": sample,
            "predecessor_run_found": run is not None,
            "predecessor_recorded_end": predecessor_end,
            "errors": errors,
            "scheduler_comparison_eligible": comparison_ready and not maintenance_interrupted and not errors,
            "scheduler_comparison_exclusion": (
                "OPERATOR_MAINTENANCE_INTERRUPTION" if maintenance_interrupted
                else "MISSING_OBSERVED_BOUNDARY" if not comparison_ready
                else "BOUNDARY_INCONSISTENCY" if errors
                else None
            ),
        })
    return {
        "sample_count": len(results),
        "valid": not any(item["errors"] for item in results),
        "scheduler_comparison_eligible_count": sum(item["scheduler_comparison_eligible"] for item in results),
        "results": results,
        "raw_evidence_policy": "PRESERVED_WITH_EXCLUSION_NOT_DELETED_OR_REWRITTEN",
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: audit_startup_boundaries.py SUCCESSOR_STARTUP_JSON RUNS_JSONL", file=sys.stderr)
        return 2
    startup = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    runs = Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()
    result = audit(startup, runs)
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(not result["valid"])


if __name__ == "__main__":
    raise SystemExit(main())
