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


def audit_startup_ack(ack: dict, expected_main_canonical_id: str) -> dict:
    errors = []
    if ack.get("main_canonical_id") != expected_main_canonical_id:
        errors.append("STARTUP_ACK_MAIN_CANONICAL_ID_MISMATCH")
    due = ack.get("current_expected_due_at")
    generation_key = ack.get("generation_key")
    if due and generation_key and generation_key != f"DUE:{due}":
        errors.append("STARTUP_ACK_GENERATION_KEY_DUE_MISMATCH")
    return {
        "valid": not errors,
        "errors": errors,
        "observed_main_canonical_id": ack.get("main_canonical_id"),
        "expected_main_canonical_id": expected_main_canonical_id,
    }


def audit(
    startup: dict,
    run_lines: list[str],
    startup_ack: dict | None = None,
    expected_main_canonical_id: str | None = None,
) -> dict:
    runs = {
        run.get("observation_id"): run
        for run in (json.loads(line) for line in run_lines if line.strip())
        if run.get("observation_id")
    }
    samples = list(startup.get("samples", []))
    next_sample = startup.get("next_sample")
    if isinstance(next_sample, dict):
        samples.append(next_sample)
    samples_by_id = {sample.get("sample_id"): sample for sample in samples}

    def find_run(predecessor_id: str | None) -> dict | None:
        if not predecessor_id:
            return None
        return runs.get(predecessor_id) or runs.get(f"OBS-{predecessor_id}")

    results = []
    for sample in samples:
        errors = []
        predecessor_id = sample.get("predecessor_run_id")
        run = find_run(predecessor_id)
        predecessor_end = run.get("run_ended_at") if run else None
        last_useful = sample.get("predecessor_last_useful_at")
        if predecessor_end and last_useful and _ts(last_useful) > _ts(predecessor_end):
            errors.append("PREDECESSOR_LAST_USEFUL_AFTER_RECORDED_END")

        ordered = [
            ("SUCCESSOR_AFTER_DUE", sample.get("scheduled_due_at"), sample.get("successor_observed_at")),
            ("BOOT_BEFORE_SUCCESSOR_OBSERVATION", sample.get("successor_observed_at"), sample.get("boot_started_at")),
            ("REARM_BEFORE_BOOT", sample.get("boot_started_at"), sample.get("rearm_verified_at")),
            ("AUTHORITY_BEFORE_REARM", sample.get("rearm_verified_at"), sample.get("authority_claim_at")),
            ("FIRST_USEFUL_BEFORE_AUTHORITY", sample.get("authority_claim_at"), sample.get("first_durable_useful_at")),
        ]
        for code, earlier, later in ordered[1:]:
            if earlier and later and _ts(later) < _ts(earlier):
                errors.append(code)

        due = sample.get("scheduled_due_at")
        generation_key = sample.get("generation_key")
        if due and generation_key and generation_key != f"DUE:{due}":
            errors.append("GENERATION_KEY_DUE_MISMATCH")

        recovery_of = sample.get("recovery_of_sample_id")
        recovery_source = samples_by_id.get(recovery_of) if recovery_of else None
        recovery_generation = recovery_of is not None
        recovery_kind = sample.get("recovery_kind")
        if recovery_generation and recovery_kind is None and recovery_source:
            if recovery_source.get("exclusion_reason") == "STARTUP_ACK_MISSING":
                recovery_kind = "FIXED_WATCHDOG_PREBOOTSTRAP"
            elif recovery_source.get("exclusion_reason") == "MISSING_DURABLE_FIRST_USEFUL_AFTER_VERIFIED_BOOTSTRAP":
                recovery_kind = "PROVISIONAL_COLD_RESCUE"
        recovery_lineage_valid = None
        if recovery_generation:
            expected_source_exclusion = {
                "FIXED_WATCHDOG_PREBOOTSTRAP": "STARTUP_ACK_MISSING",
                "PROVISIONAL_COLD_RESCUE": "MISSING_DURABLE_FIRST_USEFUL_AFTER_VERIFIED_BOOTSTRAP",
            }.get(recovery_kind)
            recovery_lineage_valid = bool(
                recovery_source
                and expected_source_exclusion
                and recovery_source.get("exclusion_reason") == expected_source_exclusion
            )
            if not recovery_source:
                errors.append("RECOVERY_SOURCE_SAMPLE_MISSING")
            elif expected_source_exclusion is None:
                errors.append("RECOVERY_KIND_UNKNOWN")
            elif recovery_source.get("exclusion_reason") != expected_source_exclusion:
                errors.append("RECOVERY_SOURCE_CLASS_MISMATCH")

        exclusion = sample.get("exclusion_reason")
        maintenance_interrupted = (
            sample.get("maintenance_interrupted") is True
            or exclusion in MAINTENANCE_EXCLUSIONS
        )
        comparison_ready = bool(due and sample.get("successor_observed_at"))
        acknowledged_invalid = (
            sample.get("validity") == "INVALID"
            and exclusion == "BOUNDARY_INCONSISTENCY"
        )
        unacknowledged_errors = [] if acknowledged_invalid else list(errors)

        if maintenance_interrupted:
            comparison_exclusion = "OPERATOR_MAINTENANCE_INTERRUPTION"
        elif recovery_generation:
            comparison_exclusion = f"{recovery_kind or 'UNKNOWN'}_GENERATION"
        elif not comparison_ready:
            comparison_exclusion = "MISSING_OBSERVED_BOUNDARY"
        elif errors:
            comparison_exclusion = "BOUNDARY_INCONSISTENCY"
        else:
            comparison_exclusion = None

        results.append({
            "sample_id": sample.get("sample_id"),
            "raw_sample": sample,
            "predecessor_run_found": run is not None,
            "predecessor_recorded_end": predecessor_end,
            "errors": errors,
            "unacknowledged_errors": unacknowledged_errors,
            "acknowledged_invalid": acknowledged_invalid,
            "startup_receipt_complete": bool(sample.get("boot_started_at") and sample.get("rearm_verified_at")),
            "recovery_generation": recovery_generation,
            "recovery_kind": recovery_kind,
            "recovery_lineage_valid": recovery_lineage_valid,
            "scheduler_comparison_eligible": (
                comparison_ready and not maintenance_interrupted and not recovery_generation and not errors
            ),
            "scheduler_comparison_exclusion": comparison_exclusion,
        })
    ack_audit = None
    if startup_ack is not None and expected_main_canonical_id is not None:
        ack_audit = audit_startup_ack(startup_ack, expected_main_canonical_id)
    return {
        "sample_count": len(results),
        "valid": (
            not any(item["unacknowledged_errors"] for item in results)
            and (ack_audit is None or ack_audit["valid"])
        ),
        "startup_ack_audit": ack_audit,
        "scheduler_comparison_eligible_count": sum(item["scheduler_comparison_eligible"] for item in results),
        "watchdog_recovery_generation_count": sum(item["recovery_generation"] for item in results),
        "results": results,
        "raw_evidence_policy": "PRESERVED_WITH_EXCLUSION_NOT_DELETED_OR_REWRITTEN",
    }


def main() -> int:
    if len(sys.argv) not in {3, 5}:
        print(
            "usage: audit_startup_boundaries.py SUCCESSOR_STARTUP_JSON RUNS_JSONL "
            "[STARTUP_ACK_JSON EXPECTED_MAIN_CANONICAL_ID]",
            file=sys.stderr,
        )
        return 2
    startup = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    runs = Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()
    startup_ack = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8")) if len(sys.argv) == 5 else None
    expected_main = sys.argv[4] if len(sys.argv) == 5 else None
    result = audit(startup, runs, startup_ack, expected_main)
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(not result["valid"])


if __name__ == "__main__":
    raise SystemExit(main())
