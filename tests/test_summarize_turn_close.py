#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from summarize_turn_close import summarize


def test_summary_keeps_unknown_useful_and_successor_boundaries_unknown():
    runs = [
        '{"observation_id":"A","run_started_at":"2026-09-21T09:36:00+00:00","run_ended_at":"2026-09-21T09:46:00+00:00","duration_seconds":600,"turn_outcome":"CONTINUE","productive_substantive_seconds":557}',
        '{"observation_id":"B","run_started_at":"2026-09-21T09:50:00+00:00","run_ended_at":"2026-09-21T10:00:00+00:00","duration_seconds":600,"turn_outcome":"CONTINUE","productive_substantive_seconds":null}',
    ]
    startup = {"samples": [{
        "sample_id": "PARTIAL", "scheduled_due_at": "2026-09-21T10:01:00+00:00",
        "successor_observed_at": None, "authority_claim_at": None,
        "first_durable_useful_at": None, "predecessor_last_useful_at": "2026-09-21T10:00:00+00:00",
    }]}
    out = summarize(runs, startup)
    assert out["known_useful_seconds_total"] == 557
    assert out["known_useful_turn_count"] == 1
    assert out["unknown_useful_turn_count"] == 1
    gap = out["successor_gap_samples"][0]
    assert gap["due_to_observation_seconds"] is None
    assert gap["predecessor_to_first_useful_seconds"] is None
    assert gap["complete_boundary_set"] is False


def test_summary_reports_unexcused_short_continue_and_observed_segments():
    runs = [
        '{"observation_id":"SHORT","run_started_at":"2026-09-21T10:00:00+00:00","run_ended_at":"2026-09-21T10:02:00+00:00","duration_seconds":120,"turn_outcome":"CONTINUE","productive_substantive_seconds":null}',
        '{"observation_id":"OLD","run_started_at":"2026-09-21T09:00:00+00:00","run_ended_at":"2026-09-21T09:01:00+00:00","duration_seconds":60,"turn_outcome":"CONTINUE"}',
    ]
    startup = {"samples": [{
        "sample_id": "COMPLETE", "scheduled_due_at": "2026-09-21T10:00:00+00:00",
        "successor_observed_at": "2026-09-21T10:02:35+00:00", "authority_claim_at": "2026-09-21T10:02:56+00:00",
        "first_durable_useful_at": "2026-09-21T10:02:56+00:00", "predecessor_last_useful_at": "2026-09-21T10:01:06+00:00",
    }]}
    out = summarize(runs, startup)
    assert out["v4_closed_turn_count"] == 1
    assert out["v4_unexcused_short_close_count"] == 1
    gap = out["successor_gap_samples"][0]
    assert gap["due_to_observation_seconds"] == 155
    assert gap["observation_to_claim_seconds"] == 21
    assert gap["claim_to_first_useful_seconds"] == 0
    assert gap["predecessor_to_first_useful_seconds"] == 110
    assert gap["complete_boundary_set"] is True


def test_summary_accepts_allowlisted_short_exception():
    runs = ['{"observation_id":"E","run_started_at":"2026-09-21T10:00:00+00:00","run_ended_at":"2026-09-21T10:02:00+00:00","duration_seconds":120,"turn_outcome":"CONTINUE","productive_substantive_seconds":null,"short_turn_reason":"PLATFORM_ENFORCED_TERMINATION","alternatives_checked":["primary","fallback"],"close_decision":"EXCEPTION"}']
    out = summarize(runs, {"samples":[]})
    assert out["v4_unexcused_short_close_count"] == 0
    assert out["unknown_useful_turn_count"] == 1


def test_invalid_complete_sample_is_visible_but_not_comparison_eligible():
    startup = {"samples":[{
        "sample_id":"INVALID", "scheduled_due_at":"2026-09-21T10:00:00+00:00",
        "successor_observed_at":"2026-09-21T10:01:00+00:00", "authority_claim_at":"2026-09-21T10:01:10+00:00",
        "first_durable_useful_at":"2026-09-21T10:01:10+00:00", "predecessor_last_useful_at":"2026-09-21T10:00:30+00:00",
        "validity":"INVALID", "exclusion_reason":"BOUNDARY_INCONSISTENCY",
    }]}
    gap = summarize([], startup)["successor_gap_samples"][0]
    assert gap["complete_boundary_set"] is True
    assert gap["evidence_valid"] is False
    assert gap["comparison_eligible"] is False
    assert gap["exclusion_reason"] == "BOUNDARY_INCONSISTENCY"


def test_complete_watchdog_recovery_is_segmented_and_excluded_from_normal_comparison():
    startup = {"samples":[{
        "sample_id":"RECOVERY", "recovery_of_sample_id":"FAILED", "scheduled_due_at":"2026-09-21T10:00:00+00:00",
        "successor_observed_at":"2026-09-21T10:00:40+00:00", "boot_started_at":"2026-09-21T10:01:00+00:00",
        "rearm_verified_at":"2026-09-21T10:01:30+00:00", "authority_claim_at":"2026-09-21T10:02:00+00:00",
        "first_durable_useful_at":"2026-09-21T10:02:20+00:00", "validity":"VALID",
    }]}
    out = summarize([], startup)
    gap = out["recovery_gap_samples"][0]
    assert gap["generation_kind"] == "WATCHDOG_RECOVERY"
    assert gap["observation_to_boot_seconds"] == 20
    assert gap["boot_to_rearm_verified_seconds"] == 30
    assert gap["rearm_verified_to_claim_seconds"] == 30
    assert gap["due_to_first_useful_seconds"] == 140
    assert gap["complete_recovery_boundary_set"] is True
    assert gap["comparison_eligible"] is False
    assert out["normal_scheduler_comparison_samples"] == []


def test_incomplete_watchdog_recovery_preserves_unknown_segments():
    startup = {"samples":[{
        "sample_id":"RECOVERY-PARTIAL", "recovery_of_sample_id":"FAILED",
        "scheduled_due_at":"2026-09-21T10:00:00+00:00", "successor_observed_at":"2026-09-21T10:00:40+00:00",
        "boot_started_at":"2026-09-21T10:01:00+00:00", "rearm_verified_at":None,
        "authority_claim_at":None, "first_durable_useful_at":None, "validity":"INCOMPLETE",
        "exclusion_reason":"BOOTSTRAP_REARM_MISSING",
    }]}
    gap = summarize([], startup)["recovery_gap_samples"][0]
    assert gap["observation_to_boot_seconds"] == 20
    assert gap["boot_to_rearm_verified_seconds"] is None
    assert gap["rearm_verified_to_claim_seconds"] is None
    assert gap["due_to_first_useful_seconds"] is None
    assert gap["complete_recovery_boundary_set"] is False
    assert gap["evidence_valid"] is False
