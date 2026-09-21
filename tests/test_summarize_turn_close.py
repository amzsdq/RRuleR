#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from summarize_turn_close import summarize

def test_summary_keeps_unknown_useful_and_successor_boundaries_unknown():
    runs=['{"observation_id":"A","run_started_at":"2026-09-21T17:00:00+00:00","run_ended_at":"2026-09-21T17:10:00+00:00","duration_seconds":600,"turn_outcome":"CONTINUE","productive_substantive_seconds":557}','{"observation_id":"B","run_started_at":"2026-09-21T17:20:00+00:00","run_ended_at":"2026-09-21T17:30:00+00:00","duration_seconds":600,"turn_outcome":"CONTINUE","productive_substantive_seconds":null}']
    startup={"samples":[{"sample_id":"PARTIAL","scheduled_due_at":"2026-09-21T17:31:00+00:00","successor_observed_at":None,"authority_claim_at":None,"first_durable_useful_at":None,"predecessor_last_useful_at":"2026-09-21T17:30:00+00:00"}]}
    out=summarize(runs,startup); assert out["known_useful_seconds_total"]==557; assert out["known_useful_turn_count"]==1; assert out["unknown_useful_turn_count"]==1; gap=out["successor_gap_samples"][0]; assert gap["due_to_observation_seconds"] is None; assert gap["predecessor_to_first_useful_seconds"] is None; assert gap["complete_boundary_set"] is False

def test_599_second_continue_is_unexcused():
    runs=['{"observation_id":"SHORT","run_started_at":"2026-09-21T17:00:00+00:00","run_ended_at":"2026-09-21T17:09:59+00:00","duration_seconds":599,"turn_outcome":"CONTINUE","productive_substantive_seconds":null}']
    out=summarize(runs,{"samples":[]}); assert out["v4_unexcused_short_close_count"]==1

def test_platform_enforced_pre600_continue_is_excused():
    runs=['{"observation_id":"E","run_started_at":"2026-09-21T17:00:00+00:00","run_ended_at":"2026-09-21T17:02:00+00:00","duration_seconds":120,"turn_outcome":"CONTINUE","productive_substantive_seconds":null,"short_turn_reason":"PLATFORM_ENFORCED_TERMINATION","end_reason":"PLATFORM_ENFORCED_TERMINATION","close_decision":"EXCEPTION"}']
    out=summarize(runs,{"samples":[]}); assert out["v4_unexcused_short_close_count"]==0; assert out["unknown_useful_turn_count"]==1

def test_old_no_safe_work_exception_is_not_excused_anymore():
    runs=['{"observation_id":"OLD-EX","run_started_at":"2026-09-21T17:00:00+00:00","run_ended_at":"2026-09-21T17:02:00+00:00","duration_seconds":120,"turn_outcome":"CONTINUE","productive_substantive_seconds":null,"short_turn_reason":"NO_SAFE_RUNNABLE_WORK_AFTER_EXPLICIT_SCAN","alternatives_checked":["primary","fallback"],"close_decision":"EXCEPTION"}']
    assert summarize(runs,{"samples":[]})["v4_unexcused_short_close_count"]==1

def test_invalid_complete_sample_is_visible_but_not_comparison_eligible():
    startup={"samples":[{"sample_id":"INVALID","scheduled_due_at":"2026-09-21T10:00:00+00:00","successor_observed_at":"2026-09-21T10:01:00+00:00","authority_claim_at":"2026-09-21T10:01:10+00:00","first_durable_useful_at":"2026-09-21T10:01:10+00:00","predecessor_last_useful_at":"2026-09-21T10:00:30+00:00","validity":"INVALID","exclusion_reason":"BOUNDARY_INCONSISTENCY"}]}
    gap=summarize([],startup)["successor_gap_samples"][0]; assert gap["complete_boundary_set"] is True; assert gap["evidence_valid"] is False; assert gap["comparison_eligible"] is False

def test_complete_watchdog_recovery_is_segmented_and_excluded_from_normal_comparison():
    startup={"samples":[{"sample_id":"RECOVERY","recovery_of_sample_id":"FAILED","scheduled_due_at":"2026-09-21T10:00:00+00:00","successor_observed_at":"2026-09-21T10:00:40+00:00","boot_started_at":"2026-09-21T10:01:00+00:00","rearm_verified_at":"2026-09-21T10:01:30+00:00","authority_claim_at":"2026-09-21T10:02:00+00:00","first_durable_useful_at":"2026-09-21T10:02:20+00:00","validity":"VALID"}]}
    out=summarize([],startup); gap=out["recovery_gap_samples"][0]; assert gap["generation_kind"]=="WATCHDOG_RECOVERY"; assert gap["observation_to_boot_seconds"]==20; assert gap["boot_to_rearm_verified_seconds"]==30; assert gap["rearm_verified_to_claim_seconds"]==30; assert gap["due_to_first_useful_seconds"]==140; assert gap["complete_recovery_boundary_set"] is True; assert gap["comparison_eligible"] is False

def test_operator_rescheduled_sample_has_own_bucket():
    startup={"samples":[{"sample_id":"OP","validity":"EXCLUDED_OPERATOR_RESCHEDULED","scheduled_due_at":"2026-09-22T00:13:08+09:00","successor_observed_at":"2026-09-22T00:14:46+09:00"}]}
    out=summarize([],startup); assert out["operator_rescheduled_gap_samples"][0]["generation_kind"]=="OPERATOR_RESCHEDULED"; assert out["normal_scheduler_gap_samples"]==[]

def test_rejected_one_shot_canary_has_own_bucket():
    startup={"samples":[{"sample_id":"ONE","schedule_mode":"EXACT_ONE_SHOT_SELF_UPDATE_CANARY","scheduled_due_at":"2026-09-22T00:25:53+09:00","successor_observed_at":"2026-09-22T00:27:31+09:00","validity":"EXCLUDED_SCHEDULE_CATEGORY_CANARY","exclusion_reason":"SCHEDULE_CATEGORY_CANARY_REJECTED"}]}
    out=summarize([],startup); assert out["rejected_one_shot_canary_gap_samples"][0]["generation_kind"]=="REJECTED_ONE_SHOT_CANARY"; assert out["normal_scheduler_gap_samples"]==[]
