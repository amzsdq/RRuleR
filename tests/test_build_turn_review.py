#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_turn_review import build_rows


def test_unknown_useful_stays_null_and_valid_gap_is_observed():
    runs = ['{"observation_id":"OBS-RUN-1","run_started_at":"2026-09-21T10:00:00+00:00","run_ended_at":"2026-09-21T10:09:14+00:00","duration_seconds":554,"turn_outcome":"CONTINUE","end_reason":"VERIFIED_SAME_CANONICAL_CONTINUATION","close_decision":"BUDGET_EXHAUSTED"}']
    startup = {"samples":[{"predecessor_run_id":"RUN-1","predecessor_last_useful_at":"2026-09-21T10:08:00+00:00","first_durable_useful_at":"2026-09-21T10:14:27+00:00","validity":"VALID"}]}
    row = build_rows(runs, {"records":[]}, startup)[0]
    assert row["accepted_useful_seconds"] is None
    assert row["useful_time_known"] is False
    assert row["successor_gap_seconds"] == 387
    assert row["eligible_live_turn"] is True


def test_invalid_startup_gap_is_excluded_not_printed():
    runs = ['{"observation_id":"OBS-RUN-2","run_started_at":"2026-09-21T10:00:00+00:00","run_ended_at":"2026-09-21T10:09:00+00:00","duration_seconds":540,"turn_outcome":"CONTINUE"}']
    startup = {"samples":[{"predecessor_run_id":"RUN-2","predecessor_last_useful_at":"2026-09-21T10:08:00+00:00","first_durable_useful_at":"2026-09-21T10:09:00+00:00","validity":"INVALID","exclusion_reason":"BOUNDARY_INCONSISTENCY"}]}
    row = build_rows(runs, {"records":[]}, startup)[0]
    assert row["successor_gap_seconds"] is None
    assert row["successor_gap_exclusion"] == "BOUNDARY_INCONSISTENCY"


def test_accepted_evidence_is_summed_by_normalized_run_id():
    runs = ['{"observation_id":"OBS-RUN-3","run_started_at":"2026-09-21T10:00:00+00:00","run_ended_at":"2026-09-21T10:10:00+00:00","duration_seconds":600,"turn_outcome":"CONTINUE"}']
    evidence = {"records":[
        {"record_id":"A","run_id":"RUN-3","qualification":"SUBSTANTIVE_ACCEPTED","observed_seconds":16},
        {"record_id":"B","run_id":"RUN-3","qualification":"SUBSTANTIVE_ACCEPTED","observed_seconds":126},
    ]}
    row = build_rows(runs, evidence, {"samples":[]})[0]
    assert row["accepted_useful_seconds"] == 142
    assert row["evidence_record_ids"] == ["A","B"]
