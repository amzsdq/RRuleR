#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from audit_startup_boundaries import audit


def test_flags_last_useful_after_predecessor_end():
    runs = ['{"observation_id":"P","run_started_at":"2026-09-21T10:00:00+00:00","run_ended_at":"2026-09-21T10:10:00+00:00"}']
    startup = {"samples":[{
        "sample_id":"S",
        "predecessor_run_id":"P",
        "predecessor_last_useful_at":"2026-09-21T10:10:01+00:00",
        "scheduled_due_at":"2026-09-21T10:09:00+00:00",
        "successor_observed_at":"2026-09-21T10:10:30+00:00",
    }]}
    out = audit(startup, runs)
    assert out["valid"] is False
    assert out["results"][0]["errors"] == ["PREDECESSOR_LAST_USEFUL_AFTER_RECORDED_END"]
    assert out["results"][0]["scheduler_comparison_eligible"] is False


def test_maintenance_sample_is_preserved_but_excluded():
    sample = {
        "sample_id":"M",
        "predecessor_run_id":"P",
        "predecessor_last_useful_at":"2026-09-21T10:09:00+00:00",
        "scheduled_due_at":"2026-09-21T10:10:00+00:00",
        "successor_observed_at":"2026-09-21T10:11:00+00:00",
        "exclusion_reason":"OPERATOR_MAINTENANCE_INTERRUPTION",
    }
    runs = ['{"observation_id":"P","run_started_at":"2026-09-21T10:00:00+00:00","run_ended_at":"2026-09-21T10:10:00+00:00"}']
    out = audit({"samples":[sample]}, runs)
    result = out["results"][0]
    assert result["raw_sample"] == sample
    assert result["scheduler_comparison_eligible"] is False
    assert result["scheduler_comparison_exclusion"] == "OPERATOR_MAINTENANCE_INTERRUPTION"


def test_complete_consistent_sample_is_eligible():
    runs = ['{"observation_id":"P","run_started_at":"2026-09-21T10:00:00+00:00","run_ended_at":"2026-09-21T10:10:00+00:00"}']
    startup = {"samples":[{
        "sample_id":"OK",
        "predecessor_run_id":"P",
        "predecessor_last_useful_at":"2026-09-21T10:09:30+00:00",
        "scheduled_due_at":"2026-09-21T10:09:00+00:00",
        "successor_observed_at":"2026-09-21T10:10:30+00:00",
    }]}
    out = audit(startup, runs)
    assert out["valid"] is True
    assert out["scheduler_comparison_eligible_count"] == 1


def test_matches_observation_prefix_to_predecessor_run_id():
    runs = ['{"observation_id":"OBS-RUN-UTIL-1","run_started_at":"2026-09-21T10:00:00+00:00","run_ended_at":"2026-09-21T10:10:00+00:00"}']
    startup = {"samples":[{
        "sample_id":"PREFIX",
        "predecessor_run_id":"RUN-UTIL-1",
        "predecessor_last_useful_at":"2026-09-21T10:10:01+00:00",
        "scheduled_due_at":"2026-09-21T10:09:00+00:00",
        "successor_observed_at":"2026-09-21T10:10:30+00:00",
    }]}
    result = audit(startup, runs)["results"][0]
    assert result["predecessor_run_found"] is True
    assert result["errors"] == ["PREDECESSOR_LAST_USEFUL_AFTER_RECORDED_END"]


def test_acknowledged_boundary_inconsistency_stays_flagged_but_does_not_fail_audit():
    runs = ['{"observation_id":"OBS-RUN-UTIL-2","run_started_at":"2026-09-21T10:00:00+00:00","run_ended_at":"2026-09-21T10:10:00+00:00"}']
    startup = {"samples":[{
        "sample_id":"ACK",
        "predecessor_run_id":"RUN-UTIL-2",
        "predecessor_last_useful_at":"2026-09-21T10:10:01+00:00",
        "scheduled_due_at":"2026-09-21T10:09:00+00:00",
        "successor_observed_at":"2026-09-21T10:10:30+00:00",
        "validity":"INVALID",
        "exclusion_reason":"BOUNDARY_INCONSISTENCY",
    }]}
    out = audit(startup, runs)
    assert out["valid"] is True
    result = out["results"][0]
    assert result["errors"] == ["PREDECESSOR_LAST_USEFUL_AFTER_RECORDED_END"]
    assert result["acknowledged_invalid"] is True
    assert result["scheduler_comparison_eligible"] is False
