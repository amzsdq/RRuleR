#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from summarize_work_evidence import summarize, summarize_runs


def record(record_id, epoch, run_id, start, end, seconds):
    return {
        "record_id": record_id,
        "authority_epoch": epoch,
        "run_id": run_id,
        "start_at": start,
        "end_at": end,
        "start_boundary": "OBSERVED",
        "end_boundary": "OBSERVED",
        "kind": "implementation",
        "artifact": f"artifact@{record_id}",
        "qualification": "SUBSTANTIVE_ACCEPTED",
        "basis": "Observed test evidence.",
        "observed_seconds": seconds,
    }


def test_summary_reports_fresh_epoch_without_inference():
    data = {"records": [
        record("A", 58, "R1", "2026-09-21T15:40:00+09:00", "2026-09-21T15:41:00+09:00", 60),
        record("B", 59, "R2", "2026-09-21T15:50:00+09:00", "2026-09-21T15:52:00+09:00", 120),
    ]}
    out = summarize(data, 59)
    assert out["observed_useful_seconds_total"] == 180
    assert out["evidence_epoch_lag"] == 0
    assert out["fresh_for_current_epoch"] is True
    assert out["unknown_time_policy"] == "NOT_INFERRED_NOT_COUNTED"


def test_summary_exposes_epoch_lag():
    data = {"records": [record("A", 43, "R1", "2026-09-21T06:00:00+09:00", "2026-09-21T06:01:00+09:00", 60)]}
    out = summarize(data, 58)
    assert out["latest_evidence_epoch"] == 43
    assert out["evidence_epoch_lag"] == 15
    assert out["fresh_for_current_epoch"] is False


def test_run_summary_flags_short_continue_without_required_reason():
    lines = ['{"observation_id":"A","run_started_at":"2026-09-21T18:00:00+09:00","run_ended_at":"2026-09-21T18:02:56+09:00","duration_seconds":176,"turn_outcome":"CONTINUE"}']
    out = summarize_runs(lines)
    assert out["short_continue_count"] == 1
    assert out["short_turn_guard_pass"] is False
    assert out["short_continue_runs"][0]["guard_compliant"] is False


def test_run_summary_accepts_documented_exception_and_normal_continue():
    lines = [
        '{"observation_id":"A","run_started_at":"2026-09-21T18:00:00+09:00","run_ended_at":"2026-09-21T18:02:00+09:00","duration_seconds":120,"turn_outcome":"CONTINUE","short_turn_reason":"PLATFORM_ENFORCED_TERMINATION","alternatives_checked":["same_work_spec"]}',
        '{"observation_id":"B","run_started_at":"2026-09-21T18:10:00+09:00","run_ended_at":"2026-09-21T18:19:00+09:00","duration_seconds":540,"turn_outcome":"CONTINUE"}'
    ]
    out = summarize_runs(lines)
    assert out["short_continue_count"] == 1
    assert out["short_turn_guard_pass"] is True
    assert out["average_completed_duration_seconds"] == 330
