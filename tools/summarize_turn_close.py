#!/usr/bin/env python3
"""Summarize bounded-turn and startup evidence without imputing unknown time."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ENFORCE_FROM = datetime.fromisoformat("2026-09-21T16:10:25+00:00")
SHORT_SECONDS = 600  # 10 minutes (600 seconds)
NORMAL_CLOSE_OFFSET_SECONDS = 60  # 1 minute (60 seconds)
ALLOWED_SHORT_REASONS = {"PLATFORM_ENFORCED_TERMINATION"}


def _ts(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed


def _seconds(start: str | None, end: str | None) -> int | None:
    if not start or not end:
        return None
    return int((_ts(end) - _ts(start)).total_seconds())


def _generation_kind(sample: dict) -> str:
    if sample.get("schedule_mode") == "EXACT_ONE_SHOT_SELF_UPDATE_CANARY" or sample.get("validity") == "EXCLUDED_SCHEDULE_CATEGORY_CANARY" or sample.get("exclusion_reason") in {"SCHEDULE_CATEGORY_CANARY_REJECTED", "ONE_SHOT_CANARY_FAILURE"}:
        return "REJECTED_ONE_SHOT_CANARY"
    if sample.get("operator_rescheduled") is True or sample.get("validity") in {"EXCLUDED_OPERATOR_RESCHEDULED", "EXCLUDED_OPERATOR_MAINTENANCE_RECOVERY"} or sample.get("exclusion_reason") in {"OPERATOR_RESCHEDULED_GENERATION", "EXPLICIT_OPERATOR_RESCHEDULE", "OPERATOR_SCHEDULE_RESET"}:
        return "OPERATOR_RESCHEDULED"
    if sample.get("recovery_kind"):
        return sample["recovery_kind"]
    if sample.get("recovery_of_sample_id"):
        return "WATCHDOG_RECOVERY"
    validity = str(sample.get("validity", "")); classification = str(sample.get("classification", ""))
    if "HOURLY_FALLBACK" in validity or "HOURLY_FALLBACK" in classification:
        return "HOURLY_FALLBACK_RECOVERY"
    return "NORMAL_SCHEDULER"


def _startup_gap(sample: dict) -> dict:
    scheduled=sample.get("scheduled_due_at"); observed=sample.get("successor_observed_at"); boot=sample.get("boot_started_at"); rearm=sample.get("rearm_verified_at"); claim=sample.get("authority_claim_at"); first=sample.get("first_durable_useful_at"); predecessor=sample.get("predecessor_last_useful_at")
    kind=_generation_kind(sample); validity=sample.get("validity")
    evidence_valid=validity not in {"INVALID","INCOMPLETE","EXCLUDED_OPERATOR_RESCHEDULED","EXCLUDED_HOURLY_FALLBACK_RECOVERY","EXCLUDED_SCHEDULE_CATEGORY_CANARY"}
    complete=all((scheduled,observed,claim,first,predecessor)); recovery_complete=all((scheduled,observed,boot,rearm,claim,first))
    return {"sample_id":sample.get("sample_id"),"generation_kind":kind,"recovery_of_sample_id":sample.get("recovery_of_sample_id"),"due_to_observation_seconds":_seconds(scheduled,observed),"observation_to_boot_seconds":_seconds(observed,boot),"boot_to_rearm_verified_seconds":_seconds(boot,rearm),"rearm_verified_to_claim_seconds":_seconds(rearm,claim),"observation_to_claim_seconds":_seconds(observed,claim),"claim_to_first_useful_seconds":_seconds(claim,first),"due_to_first_useful_seconds":_seconds(scheduled,first),"predecessor_to_first_useful_seconds":_seconds(predecessor,first),"complete_boundary_set":complete,"complete_recovery_boundary_set":recovery_complete,"evidence_valid":evidence_valid,"comparison_eligible":kind=="NORMAL_SCHEDULER" and evidence_valid and complete,"exclusion_reason":sample.get("exclusion_reason")}


def _normal_close_offset_seconds(run: dict) -> int | None:
    ended = run.get("run_ended_at")
    due = run.get("verified_next_fast_due_at") or run.get("next_due_at")
    return _seconds(ended, due)


def _tail_consecutive(rows: list[dict], predicate) -> list[dict]:
    tail=[]
    for row in reversed(rows):
        if not predicate(row):
            break
        tail.append(row)
    return list(reversed(tail))


def summarize(run_lines: list[str], startup: dict) -> dict:
    runs=[json.loads(line) for line in run_lines if line.strip()]; closed=[]
    for run in runs:
        try: start=_ts(run["run_started_at"])
        except (KeyError,TypeError,ValueError): continue
        if start >= ENFORCE_FROM and run.get("run_ended_at"): closed.append(run)
    known_useful=[run["productive_substantive_seconds"] for run in closed if type(run.get("productive_substantive_seconds")) is int]
    unexcused=[]
    for run in closed:
        duration=run.get("duration_seconds")
        if type(duration) is not int: duration=_seconds(run.get("run_started_at"),run.get("run_ended_at"))
        if run.get("turn_outcome")!="CONTINUE" or duration is None or duration>=SHORT_SECONDS: continue
        excused=(run.get("short_turn_reason") in ALLOWED_SHORT_REASONS and run.get("close_decision")=="EXCEPTION" and run.get("end_reason")=="PLATFORM_ENFORCED_TERMINATION")
        if not excused: unexcused.append({"observation_id":run.get("observation_id"),"duration_seconds":duration,"short_turn_reason":run.get("short_turn_reason"),"alternatives_checked":run.get("alternatives_checked")})
    normal_continue=[r for r in closed if r.get("turn_outcome")=="CONTINUE" and r.get("end_reason")=="VERIFIED_SAME_CANONICAL_CONTINUATION"]
    p0a_tail=_tail_consecutive(normal_continue, lambda r: (r.get("duration_seconds") if type(r.get("duration_seconds")) is int else _seconds(r.get("run_started_at"),r.get("run_ended_at"))) >= SHORT_SECONDS)
    p0b_tail=_tail_consecutive(normal_continue, lambda r: _normal_close_offset_seconds(r)==NORMAL_CLOSE_OFFSET_SECONDS)
    raw_samples=list(startup.get("samples",[]))
    if isinstance(startup.get("next_sample"),dict): raw_samples.append(startup["next_sample"])
    gaps=[_startup_gap(sample) for sample in raw_samples]
    normal=[gap for gap in gaps if gap["generation_kind"]=="NORMAL_SCHEDULER"]
    operator=[gap for gap in gaps if gap["generation_kind"]=="OPERATOR_RESCHEDULED"]
    one_shot=[gap for gap in gaps if gap["generation_kind"]=="REJECTED_ONE_SHOT_CANARY"]
    recovery=[gap for gap in gaps if gap["generation_kind"] not in {"NORMAL_SCHEDULER","OPERATOR_RESCHEDULED","REJECTED_ONE_SHOT_CANARY"}]
    return {"v4_closed_turn_count":len(closed),"v4_unexcused_short_close_count":len(unexcused),"v4_unexcused_short_closes":unexcused,"known_useful_seconds_total":sum(known_useful),"known_useful_turn_count":len(known_useful),"unknown_useful_turn_count":len(closed)-len(known_useful),"p0_a_consecutive_normal_turns_gte_10_minutes_600_seconds":len(p0a_tail),"p0_a_tail_observation_ids":[r.get("observation_id") for r in p0a_tail],"p0_b_consecutive_normal_closes_exactly_1_minute_60_seconds":len(p0b_tail),"p0_b_tail_observation_ids":[r.get("observation_id") for r in p0b_tail],"p0_b_requires_explicit_verified_due_timestamp":True,"successor_gap_samples":gaps,"normal_scheduler_gap_samples":normal,"normal_scheduler_comparison_samples":[gap for gap in normal if gap["comparison_eligible"]],"operator_rescheduled_gap_samples":operator,"rejected_one_shot_canary_gap_samples":one_shot,"recovery_gap_samples":recovery,"unknown_policy":"MISSING_USEFUL_OR_BOUNDARY_VALUES_REMAIN_NULL_NOT_ZERO"}


def main() -> int:
    if len(sys.argv)!=3:
        print("usage: summarize_turn_close.py RUNS_JSONL SUCCESSOR_STARTUP_JSON",file=sys.stderr); return 2
    runs=Path(sys.argv[1]).read_text(encoding="utf-8").splitlines(); startup=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    print(json.dumps(summarize(runs,startup),indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
