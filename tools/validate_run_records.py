#!/usr/bin/env python3
"""Validate newly closed turns; retain legacy observations without rewriting them."""
import json
import sys
from datetime import datetime
from pathlib import Path

ENFORCE_FROM = datetime.fromisoformat('2026-09-21T09:35:00+00:00')
EXCEPTIONS = {'PLATFORM_ENFORCED_TERMINATION', 'EXPLICIT_OPERATOR_INTERVENTION', 'AUTHORITY_OR_FENCING_FAIL_CLOSED', 'NO_SAFE_RUNNABLE_WORK_AFTER_EXPLICIT_SCAN'}

def timestamp(value):
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError('timestamp must include timezone')
    return dt

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
    if record['close_decision'] not in {'TIME_BOUNDARY', 'BUDGET_EXHAUSTED', 'EXCEPTION', 'HANDOFF', 'TERMINAL'}:
        raise ValueError('invalid close_decision')
    if outcome == 'CONTINUE':
        if record['end_reason'] not in {'VERIFIED_SAME_CANONICAL_CONTINUATION', 'COMMITTED_SUCCESSOR_HANDOFF', 'PLATFORM_ENFORCED_TERMINATION'}:
            raise ValueError('CONTINUE lacks valid end reason')
        alternatives = record.get('alternatives_checked')
        if duration < 600 and (not isinstance(alternatives, list) or not alternatives or not all(isinstance(x,str) and x.strip() for x in alternatives)):
            raise ValueError('early close lacks concrete alternatives')
        if duration < 480:
            if record.get('short_turn_reason') not in EXCEPTIONS or record['close_decision'] != 'EXCEPTION':
                raise ValueError('short CONTINUE lacks allowlisted exception')
        elif duration < 600 and record['close_decision'] not in {'BUDGET_EXHAUSTED', 'EXCEPTION', 'HANDOFF'}:
            raise ValueError('target boundary not reached')
        if record['close_decision'] == 'BUDGET_EXHAUSTED':
            reserve = record.get('close_reserve_seconds')
            if type(reserve) not in (int, float) or not 0 <= reserve <= 600:
                raise ValueError('invalid close reserve')
        if record['end_reason'] == 'COMMITTED_SUCCESSOR_HANDOFF':
            timestamp(record['successor_observed_at'])
    if outcome == 'COMPLETE' and record['program_status_at_end'] != 'PROGRAM_COMPLETE':
        raise ValueError('local completion is not program completion')
    useful = record.get('productive_substantive_seconds')
    if useful is not None and (type(useful) is not int or not 0 <= useful <= duration):
        raise ValueError('invalid useful duration')

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
