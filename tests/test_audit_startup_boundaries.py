#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from audit_startup_boundaries import audit, audit_startup_ack


def _run(obs="OBS-RUN-UTIL-1", end="2026-09-21T10:10:00+00:00"):
    return [f'{{"observation_id":"{obs}","run_started_at":"2026-09-21T10:00:00+00:00","run_ended_at":"{end}"}}']


def test_flags_last_useful_after_predecessor_end():
    startup = {"samples":[{"sample_id":"S","predecessor_run_id":"RUN-UTIL-1","predecessor_last_useful_at":"2026-09-21T10:10:01+00:00","scheduled_due_at":"2026-09-21T10:09:00+00:00","successor_observed_at":"2026-09-21T10:10:30+00:00"}]}
    out = audit(startup, _run())
    assert out["valid"] is False
    assert out["results"][0]["errors"] == ["PREDECESSOR_LAST_USEFUL_AFTER_RECORDED_END"]
    assert out["results"][0]["scheduler_comparison_eligible"] is False


def test_maintenance_sample_is_preserved_but_excluded():
    sample = {"sample_id":"M","predecessor_run_id":"RUN-UTIL-1","predecessor_last_useful_at":"2026-09-21T10:09:00+00:00","scheduled_due_at":"2026-09-21T10:10:00+00:00","successor_observed_at":"2026-09-21T10:11:00+00:00","exclusion_reason":"OPERATOR_MAINTENANCE_INTERRUPTION"}
    result = audit({"samples":[sample]}, _run())["results"][0]
    assert result["raw_sample"] == sample
    assert result["scheduler_comparison_eligible"] is False
    assert result["scheduler_comparison_exclusion"] == "OPERATOR_MAINTENANCE_INTERRUPTION"


def test_complete_consistent_sample_is_eligible():
    startup = {"samples":[{"sample_id":"OK","predecessor_run_id":"RUN-UTIL-1","predecessor_last_useful_at":"2026-09-21T10:09:30+00:00","scheduled_due_at":"2026-09-21T10:09:00+00:00","successor_observed_at":"2026-09-21T10:10:30+00:00"}]}
    out = audit(startup, _run())
    assert out["valid"] is True
    assert out["scheduler_comparison_eligible_count"] == 1


def test_acknowledged_boundary_inconsistency_does_not_fail_audit():
    startup = {"samples":[{"sample_id":"ACK","predecessor_run_id":"RUN-UTIL-1","predecessor_last_useful_at":"2026-09-21T10:10:01+00:00","scheduled_due_at":"2026-09-21T10:09:00+00:00","successor_observed_at":"2026-09-21T10:10:30+00:00","validity":"INVALID","exclusion_reason":"BOUNDARY_INCONSISTENCY"}]}
    out = audit(startup, _run())
    assert out["valid"] is True
    assert out["results"][0]["acknowledged_invalid"] is True


def test_valid_watchdog_recovery_lineage_is_not_normal_scheduler_sample():
    failed = {"sample_id":"S0","scheduled_due_at":"2026-09-21T10:00:00+00:00","successor_observed_at":"2026-09-21T10:01:00+00:00","exclusion_reason":"STARTUP_ACK_MISSING","validity":"INCOMPLETE"}
    recovered = {"sample_id":"S1","recovery_of_sample_id":"S0","scheduled_due_at":"2026-09-21T10:05:00+00:00","generation_key":"DUE:2026-09-21T10:05:00+00:00","successor_observed_at":"2026-09-21T10:05:20+00:00","boot_started_at":"2026-09-21T10:05:30+00:00","rearm_verified_at":"2026-09-21T10:05:40+00:00","authority_claim_at":"2026-09-21T10:05:50+00:00"}
    out = audit({"samples":[failed,recovered]}, [])
    result = out["results"][1]
    assert out["valid"] is True
    assert out["watchdog_recovery_generation_count"] == 1
    assert result["startup_receipt_complete"] is True
    assert result["recovery_lineage_valid"] is True
    assert result["scheduler_comparison_eligible"] is False
    assert result["recovery_kind"] == "FIXED_WATCHDOG_PREBOOTSTRAP"
    assert result["scheduler_comparison_exclusion"] == "FIXED_WATCHDOG_PREBOOTSTRAP_GENERATION"


def test_valid_provisional_cold_rescue_lineage_is_separate():
    stalled = {"sample_id":"S0","exclusion_reason":"MISSING_DURABLE_FIRST_USEFUL_AFTER_VERIFIED_BOOTSTRAP","validity":"INCOMPLETE"}
    recovered = {"sample_id":"S1","recovery_of_sample_id":"S0","recovery_kind":"PROVISIONAL_COLD_RESCUE","scheduled_due_at":"2026-09-21T10:05:00+00:00","generation_key":"DUE:2026-09-21T10:05:00+00:00","successor_observed_at":"2026-09-21T10:05:20+00:00","boot_started_at":"2026-09-21T10:05:30+00:00","rearm_verified_at":"2026-09-21T10:05:40+00:00","authority_claim_at":"2026-09-21T10:05:50+00:00","first_durable_useful_at":"2026-09-21T10:06:00+00:00"}
    result = audit({"samples":[stalled,recovered]}, [])["results"][1]
    assert result["recovery_lineage_valid"] is True
    assert result["recovery_kind"] == "PROVISIONAL_COLD_RESCUE"
    assert result["scheduler_comparison_exclusion"] == "PROVISIONAL_COLD_RESCUE_GENERATION"


def test_recovery_generation_fails_closed_on_wrong_source_or_generation():
    source = {"sample_id":"S0","exclusion_reason":"MISSING_DURABLE_SUCCESSOR_PROGRESS"}
    recovered = {"sample_id":"S1","recovery_of_sample_id":"S0","scheduled_due_at":"2026-09-21T10:05:00+00:00","generation_key":"DUE:2026-09-21T10:06:00+00:00","successor_observed_at":"2026-09-21T10:05:20+00:00"}
    out = audit({"samples":[source,recovered]}, [])
    assert out["valid"] is False
    assert out["results"][1]["errors"] == ["GENERATION_KEY_DUE_MISMATCH", "RECOVERY_KIND_UNKNOWN"]


def test_startup_ack_fails_closed_on_mixed_main_canonical_id():
    expected = "6aaf8a993eb08191b8d0ab1d9662e4b2"
    ack = {
        "main_canonical_id": "6aaf8a993eb08191b68dcec5e3fed081",
        "current_expected_due_at": "2026-09-21T21:54:52+09:00",
        "generation_key": "DUE:2026-09-21T21:54:52+09:00",
    }
    result = audit_startup_ack(ack, expected)
    assert result["valid"] is False
    assert result["errors"] == ["STARTUP_ACK_MAIN_CANONICAL_ID_MISMATCH"]


def test_startup_ack_accepts_matching_canonical_and_generation():
    expected = "6aaf8a993eb08191b8d0ab1d9662e4b2"
    ack = {
        "main_canonical_id": expected,
        "current_expected_due_at": "2026-09-21T21:54:52+09:00",
        "generation_key": "DUE:2026-09-21T21:54:52+09:00",
    }
    result = audit({"samples": []}, [], ack, expected)
    assert result["valid"] is True
    assert result["startup_ack_audit"]["valid"] is True


def test_audit_includes_next_sample_and_validates_recovery_lineage():
    failed = {"sample_id":"S0","scheduled_due_at":"2026-09-21T10:00:00+00:00","successor_observed_at":"2026-09-21T10:01:00+00:00","exclusion_reason":"STARTUP_ACK_MISSING","validity":"INCOMPLETE"}
    recovered = {"sample_id":"S1","recovery_of_sample_id":"S0","recovery_kind":"FIXED_WATCHDOG_PREBOOTSTRAP","scheduled_due_at":"2026-09-21T10:05:00+00:00","generation_key":"DUE:2026-09-21T10:05:00+00:00","successor_observed_at":"2026-09-21T10:05:20+00:00","boot_started_at":"2026-09-21T10:05:30+00:00","rearm_verified_at":"2026-09-21T10:05:40+00:00","authority_claim_at":"2026-09-21T10:05:50+00:00","first_durable_useful_at":"2026-09-21T10:06:00+00:00"}
    out = audit({"samples":[failed],"next_sample":recovered}, [])
    assert out["valid"] is True
    assert out["sample_count"] == 2
    assert out["watchdog_recovery_generation_count"] == 1
    result = out["results"][1]
    assert result["sample_id"] == "S1"
    assert result["recovery_lineage_valid"] is True
    assert result["scheduler_comparison_eligible"] is False


def test_next_sample_generation_error_fails_audit():
    next_sample = {"sample_id":"NEXT","scheduled_due_at":"2026-09-21T10:05:00+00:00","generation_key":"DUE:2026-09-21T10:06:00+00:00","successor_observed_at":"2026-09-21T10:05:20+00:00"}
    out = audit({"samples":[],"next_sample":next_sample}, [])
    assert out["valid"] is False
    assert out["sample_count"] == 1
    assert out["results"][0]["errors"] == ["GENERATION_KEY_DUE_MISMATCH"]


def test_operator_rescheduled_generation_is_preserved_but_excluded():
    sample = {
        "sample_id": "OP",
        "operator_rescheduled": True,
        "scheduled_due_at": "2026-09-22T00:13:08+09:00",
        "successor_observed_at": "2026-09-22T00:14:46+09:00",
        "boot_started_at": "2026-09-22T00:14:46+09:00",
        "rearm_verified_at": "2026-09-22T00:17:48+09:00",
        "authority_claim_at": "2026-09-22T00:18:31+09:00",
        "first_durable_useful_at": "2026-09-22T00:18:31+09:00",
    }
    out = audit({"samples": [sample]}, [])
    result = out["results"][0]
    assert out["valid"] is True
    assert out["operator_rescheduled_generation_count"] == 1
    assert result["raw_sample"] == sample
    assert result["startup_receipt_complete"] is True
    assert result["scheduler_comparison_eligible"] is False
    assert result["scheduler_comparison_exclusion"] == "OPERATOR_RESCHEDULED_GENERATION"


def test_legacy_operator_reset_marker_is_classified_as_operator_rescheduled():
    sample = {
        "sample_id": "LEGACY-OP",
        "validity": "EXCLUDED_OPERATOR_MAINTENANCE_RECOVERY",
        "exclusion_reason": "OPERATOR_SCHEDULE_RESET",
        "scheduled_due_at": "2026-09-21T23:52:00+09:00",
        "successor_observed_at": "2026-09-21T23:50:45+09:00",
    }
    result = audit({"samples": [sample]}, [])["results"][0]
    assert result["operator_rescheduled_generation"] is True
    assert result["scheduler_comparison_exclusion"] == "OPERATOR_RESCHEDULED_GENERATION"
