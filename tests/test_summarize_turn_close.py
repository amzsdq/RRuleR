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

def test_consecutive_p0_a_and_local_p0_b_require_observed_duration_and_explicit_due():
    runs=[
      '{"observation_id":"R1","run_started_at":"2026-09-21T17:00:00+00:00","run_ended_at":"2026-09-21T17:10:00+00:00","duration_seconds":600,"turn_outcome":"CONTINUE","end_reason":"VERIFIED_SAME_CANONICAL_CONTINUATION","verified_next_fast_due_at":"2026-09-21T17:11:00+00:00"}',
      '{"observation_id":"R2","run_started_at":"2026-09-21T17:20:00+00:00","run_ended_at":"2026-09-21T17:30:01+00:00","duration_seconds":601,"turn_outcome":"CONTINUE","end_reason":"VERIFIED_SAME_CANONICAL_CONTINUATION","verified_next_fast_due_at":"2026-09-21T17:31:01+00:00"}',
      '{"observation_id":"R3","run_started_at":"2026-09-21T17:40:00+00:00","run_ended_at":"2026-09-21T17:50:02+00:00","duration_seconds":602,"turn_outcome":"CONTINUE","end_reason":"VERIFIED_SAME_CANONICAL_CONTINUATION","verified_next_fast_due_at":"2026-09-21T17:51:02+00:00"}'
    ]
    out=summarize(runs,{"samples":[]})
    assert out["p0_a_consecutive_normal_turns_gte_10_minutes_600_seconds"]==3
    assert out["p0_b_consecutive_local_closes_exactly_1_minute_60_seconds"]==3
    assert out["p0_b_consecutive_normal_closes_exactly_1_minute_60_seconds_with_observed_fast_bootstrap"]==0

def test_p0_b_does_not_infer_exact_close_from_end_reason_or_hourly_recurrence():
    runs=[
      '{"observation_id":"GOOD","run_started_at":"2026-09-21T17:00:00+00:00","run_ended_at":"2026-09-21T17:10:00+00:00","duration_seconds":600,"turn_outcome":"CONTINUE","end_reason":"VERIFIED_SAME_CANONICAL_CONTINUATION","verified_next_fast_due_at":"2026-09-21T17:11:00+00:00"}',
      '{"observation_id":"MISSING-DUE","run_started_at":"2026-09-21T17:20:00+00:00","run_ended_at":"2026-09-21T17:30:00+00:00","duration_seconds":600,"turn_outcome":"CONTINUE","end_reason":"VERIFIED_SAME_CANONICAL_CONTINUATION"}'
    ]
    out=summarize(runs,{"samples":[]})
    assert out["p0_a_consecutive_normal_turns_gte_10_minutes_600_seconds"]==2
    assert out["p0_b_consecutive_local_closes_exactly_1_minute_60_seconds"]==0

def test_sixty_minutes_is_not_accepted_as_one_minute():
    runs=['{"observation_id":"BAD-HOUR","run_started_at":"2026-09-21T17:00:00+00:00","run_ended_at":"2026-09-21T17:10:00+00:00","duration_seconds":600,"turn_outcome":"CONTINUE","end_reason":"VERIFIED_SAME_CANONICAL_CONTINUATION","verified_next_fast_due_at":"2026-09-21T18:10:00+00:00"}']
    out=summarize(runs,{"samples":[]}); assert out["p0_b_consecutive_local_closes_exactly_1_minute_60_seconds"]==0

def test_p0_b_delivery_pass_requires_matching_normal_fast_bootstrap():
    runs=['{"observation_id":"OBS-RUN-1","run_started_at":"2026-09-21T17:00:00+00:00","run_ended_at":"2026-09-21T17:10:00+00:00","duration_seconds":600,"turn_outcome":"CONTINUE","end_reason":"VERIFIED_SAME_CANONICAL_CONTINUATION","verified_next_fast_due_at":"2026-09-21T17:11:00+00:00"}']
    normal={"sample_id":"FAST","predecessor_run_id":"RUN-1","scheduled_due_at":"2026-09-21T17:11:00+00:00","successor_observed_at":"2026-09-21T17:11:20+00:00","boot_started_at":"2026-09-21T17:11:25+00:00"}
    out=summarize(runs,{"samples":[normal]})
    assert out["p0_b_consecutive_local_closes_exactly_1_minute_60_seconds"]==1
    assert out["p0_b_consecutive_normal_closes_exactly_1_minute_60_seconds_with_observed_fast_bootstrap"]==1


def test_cold_fallback_does_not_satisfy_p0_b_delivered_fast_successor():
    runs=['{"observation_id":"OBS-RUN-1","run_started_at":"2026-09-21T17:00:00+00:00","run_ended_at":"2026-09-21T17:10:00+00:00","duration_seconds":600,"turn_outcome":"CONTINUE","end_reason":"VERIFIED_SAME_CANONICAL_CONTINUATION","verified_next_fast_due_at":"2026-09-21T17:11:00+00:00"}']
    cold={"sample_id":"COLD","predecessor_run_id":"RUN-1","scheduled_due_at":"2026-09-21T17:11:00+00:00","successor_observed_at":"2026-09-21T18:09:10+00:00","boot_started_at":"2026-09-21T18:09:10+00:00","generation_class":"SAME_MAIN_NATURAL_HOURLY_COLD_FALLBACK_AFTER_MISSED_FAST_SHIFT"}
    out=summarize(runs,{"samples":[cold]})
    assert out["p0_b_consecutive_local_closes_exactly_1_minute_60_seconds"]==1
    assert out["p0_b_consecutive_normal_closes_exactly_1_minute_60_seconds_with_observed_fast_bootstrap"]==0
    assert out["recovery_gap_samples"][0]["generation_kind"]=="HOURLY_FALLBACK_RECOVERY"

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
