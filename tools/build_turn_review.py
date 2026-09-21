#!/usr/bin/env python3
"""Build validity-aware turn review rows without inferring unknown time."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _run_id(observation_id: str | None) -> str | None:
    return observation_id[4:] if observation_id and observation_id.startswith("OBS-") else observation_id


def _progress_status(sample: dict | None) -> str:
    if not sample or not sample.get("successor_observed_at"):
        return "SUCCESSOR_NOT_OBSERVED"
    if not sample.get("authority_claim_at"):
        return "MISSING_AUTHORITY_CLAIM"
    if not sample.get("first_durable_useful_at"):
        return "MISSING_FIRST_USEFUL"
    return "COMPLETE"


def build_rows(run_lines: list[str], work_evidence: dict, startup: dict) -> list[dict]:
    evidence_by_run: dict[str, list[dict]] = {}
    for record in work_evidence.get("records", []):
        if record.get("qualification") == "SUBSTANTIVE_ACCEPTED":
            evidence_by_run.setdefault(record.get("run_id"), []).append(record)
    startup_by_predecessor = {
        sample.get("predecessor_run_id"): sample
        for sample in startup.get("samples", [])
        if sample.get("predecessor_run_id")
    }
    rows = []
    for run in (json.loads(line) for line in run_lines if line.strip()):
        if not run.get("run_ended_at"):
            continue
        run_id = _run_id(run.get("observation_id"))
        evidence = evidence_by_run.get(run_id, [])
        useful = sum(item["observed_seconds"] for item in evidence) if evidence else None
        sample = startup_by_predecessor.get(run_id)
        gap = None
        gap_exclusion = "NO_MATCHED_SUCCESSOR_SAMPLE"
        if sample:
            if sample.get("validity") == "INVALID" or sample.get("exclusion_reason"):
                gap_exclusion = sample.get("exclusion_reason") or "INVALID"
            elif sample.get("predecessor_last_useful_at") and sample.get("first_durable_useful_at"):
                gap = int((_ts(sample["first_durable_useful_at"]) - _ts(sample["predecessor_last_useful_at"])).total_seconds())
                gap_exclusion = None
            else:
                gap_exclusion = "MISSING_OBSERVED_BOUNDARY"
        excluded = run.get("turn_outcome") == "PAUSED" or run.get("end_reason") == "PLATFORM_ENFORCED_TERMINATION"
        rows.append({
            "observation_id": run.get("observation_id"),
            "observed_start": run.get("run_started_at"),
            "observed_end": run.get("run_ended_at"),
            "elapsed_seconds": run.get("duration_seconds"),
            "accepted_useful_seconds": useful,
            "useful_time_known": useful is not None,
            "observed_control_close_seconds": run.get("checkpoint_seconds"),
            "successor_delivery_seconds": sample.get("due_to_observation_seconds") if sample else None,
            "successor_progress_status": _progress_status(sample),
            "successor_gap_seconds": gap,
            "successor_gap_exclusion": gap_exclusion,
            "close_decision": run.get("close_decision"),
            "end_reason": run.get("end_reason"),
            "alternatives_checked": run.get("alternatives_checked"),
            "eligible_live_turn": not excluded,
            "turn_exclusion": "OPERATOR_PAUSE" if run.get("turn_outcome") == "PAUSED" else "PLATFORM_TERMINATION" if run.get("end_reason") == "PLATFORM_ENFORCED_TERMINATION" else None,
            "evidence_record_ids": [item.get("record_id") for item in evidence],
        })
    return rows


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: build_turn_review.py RUNS_JSONL WORK_EVIDENCE_JSON SUCCESSOR_STARTUP_JSON", file=sys.stderr)
        return 2
    rows = build_rows(
        Path(sys.argv[1]).read_text(encoding="utf-8").splitlines(),
        json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")),
        json.loads(Path(sys.argv[3]).read_text(encoding="utf-8")),
    )
    print(json.dumps({"rows": rows, "unknown_policy": "NULL_IS_UNKNOWN_NEVER_ZERO"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
