#!/usr/bin/env python3
"""Validate newly closed turns and v5.5 durable unit chat-trace evidence."""
import json
import sys
from datetime import datetime
from pathlib import Path

ENFORCE_FROM = datetime.fromisoformat('2026-09-21T16:10:25+00:00')
PRE600_CONTINUE_EXCEPTIONS = {'PLATFORM_ENFORCED_TERMINATION'}
VALID_CONTINUE_END_REASONS = {
    'VERIFIED_SAME_CANONICAL_CONTINUATION',
    'VERIFIED_SAME_CANONICAL_EXACT_ONE_SHOT_CONTINUATION',
    'VERIFIED_SAME_CANONICAL_CUSTOM_RECURRING_CONTINUATION',
    'COMMITTED_SUCCESSOR_HANDOFF',
    'PLATFORM_ENFORCED_TERMINATION',
}
FORBIDDEN_TRACE_SOURCES = {
    'MERE_READ', 'PLAN_ONLY', 'WAIT', 'RETRY_WITHOUT_COMPLETION',
    'UNPERSISTED_PARTIAL_WORK', 'SCHEDULER_MUTATION_ALONE',
}

def timestamp(value):
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError('timestamp must include timezone')
    return dt

def validate_unit_traces(record):
    traces = record.get('unit_completion_traces', [])
    if not isinstance(traces, list):
        raise ValueError('unit_completion_traces must be a list')
    seen = set()
    for trace in traces:
        if not isinstance(trace, dict):
            raise ValueError('unit completion trace must be an object')
        for key in ('unit_id', 'start_at', 'end_at', 'duration_seconds', 'artifact', 'work_evidence_ref', 'message'):
            if not trace.get(key):
                raise ValueError('unit completion trace missing ' + key)
        if trace['unit_id'] in seen:
            raise ValueError('duplicate unit completion trace')
        seen.add(trace['unit_id'])
        start = timestamp(trace['start_at'])
        end = timestamp(trace['end_at'])
        duration = trace['duration_seconds']
        actual = (end - start).total_seconds()
        if type(duration) is not int or duration <= 0 or abs(duration - actual) >= 1:
            raise ValueError('unit trace duration does not match observed boundaries')
        if trace.get('source_kind') in FORBIDDEN_TRACE_SOURCES:
            raise ValueError('forbidden source emitted completion trace')
        if not trace['message'].startswith('완료: '):
            raise ValueError('unit completion trace message must use completion form')
        if trace.get('durably_persisted') is not True:
            raise ValueError('unit completion trace lacks durable persistence proof')
        if trace.get('continued_same_wake') is not True and record.get('duration_seconds', 0) < 600:
            raise ValueError('pre-600 unit trace did not continue same wake')

def validate(record):
    start = timestamp(record['run_started_at'])
    if start < ENFORCE_FROM or record.get('run_ended_at') is None:
        return
    for key in ('duration_seconds', 'turn_outcome', 'end_reason', 'program_status_at_end', 'close_decision'):
        if record.get(key) is None:
            raise ValueError('missing ' + key)
    duration = record['duration_seconds']
    actual = (timestamp(record['run_ended_at']) - start).total_seconds()
    if type(duration) is not int or duration < 0 or abs(duration - actual) >= 1:
        raise ValueError('duration does not match observed boundaries')
    outcome = record['turn_outcome']
    if outcome not in {'CONTINUE', 'COMPLETE', 'BLOCKED', 'PAUSED'}:
        raise ValueError('invalid turn_outcome')
    if record['close_decision'] not in {'TIME_BOUNDARY', 'TARGET_REACHED_SAFE_BOUNDARY', 'BUDGET_EXHAUSTED', 'EXCEPTION', 'HANDOFF', 'TERMINAL'}:
        raise ValueError('invalid close_decision')
    if outcome == 'CONTINUE':
        if record['end_reason'] not in VALID_CONTINUE_END_REASONS:
            raise ValueError('CONTINUE lacks valid end reason')
        if duration < 600:
            if record.get('short_turn_reason') not in PRE600_CONTINUE_EXCEPTIONS or record['close_decision'] != 'EXCEPTION' or record['end_reason'] != 'PLATFORM_ENFORCED_TERMINATION':
                raise ValueError('voluntary normal CONTINUE before 600s is forbidden')
        if record['close_decision'] == 'BUDGET_EXHAUSTED' and duration < 600:
            raise ValueError('budget exhaustion cannot authorize normal close before 600s')
        if record['end_reason'] == 'COMMITTED_SUCCESSOR_HANDOFF':
            timestamp(record['successor_observed_at'])
    if outcome == 'COMPLETE' and record['program_status_at_end'] != 'PROGRAM_COMPLETE':
        raise ValueError('local completion is not program completion')
    useful = record.get('productive_substantive_seconds')
    if useful is not None and (type(useful) is not int or not 0 <= useful <= duration):
        raise ValueError('invalid useful duration')
    if record.get('chat_trace_policy') == 'DURABLE_UNIT_CHAT_TRACE_CANARY_V5_5':
        if record.get('schedule_trace_verified') is not True:
            raise ValueError('v5.5 run lacks verified schedule trace')
        validate_unit_traces(record)
        if outcome == 'CONTINUE' and record.get('final_due_trace_verified') is not True:
            raise ValueError('v5.5 CONTINUE lacks verified final due trace')

def main():
    errors = []
    for index, line in enumerate(Path(sys.argv[1]).read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            validate(json.loads(line))
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'line {index}: {exc}')
    print(json.dumps({'valid': not errors, 'errors': errors}))
    return int(bool(errors))

if __name__ == '__main__':
    raise SystemExit(main())
