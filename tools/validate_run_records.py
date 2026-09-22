#!/usr/bin/env python3
"""Validate newly closed turns and durable unit trace evidence."""
import json, sys
from datetime import datetime
from pathlib import Path
ENFORCE_FROM=datetime.fromisoformat('2026-09-21T16:10:25+00:00')
PRE600_CONTINUE_EXCEPTIONS={'PLATFORM_ENFORCED_TERMINATION'}
NORMAL_CLOSE_OFFSET_SECONDS=60
VALID_CONTINUE_END_REASONS={'VERIFIED_SAME_CANONICAL_CONTINUATION','VERIFIED_SAME_CANONICAL_EXACT_ONE_SHOT_CONTINUATION','VERIFIED_SAME_CANONICAL_CUSTOM_RECURRING_CONTINUATION','COMMITTED_SUCCESSOR_HANDOFF','PLATFORM_ENFORCED_TERMINATION'}
FORBIDDEN_TRACE_SOURCES={'MERE_READ','PLAN_ONLY','WAIT','RETRY_WITHOUT_COMPLETION','UNPERSISTED_PARTIAL_WORK','SCHEDULER_MUTATION_ALONE'}
TRACE_DELIVERY_STATES={'TRACE_DURABLY_RECORDED','TRACE_INTERMEDIATE_DELIVERED','TRACE_FINAL_FLUSH_DELIVERED'}

def timestamp(value):
    dt=datetime.fromisoformat(value)
    if dt.tzinfo is None: raise ValueError('timestamp must include timezone')
    return dt

def validate_unit_traces(record, require_delivery_state=False):
    traces=record.get('unit_completion_traces',[])
    if not isinstance(traces,list): raise ValueError('unit_completion_traces must be a list')
    seen=set()
    for trace in traces:
        if not isinstance(trace,dict): raise ValueError('unit completion trace must be an object')
        for key in ('unit_id','start_at','end_at','duration_seconds','artifact','work_evidence_ref','message'):
            if not trace.get(key): raise ValueError('unit completion trace missing '+key)
        if trace['unit_id'] in seen: raise ValueError('duplicate unit completion trace')
        seen.add(trace['unit_id']); start=timestamp(trace['start_at']); end=timestamp(trace['end_at']); duration=trace['duration_seconds']; actual=(end-start).total_seconds()
        if type(duration) is not int or duration<=0 or abs(duration-actual)>=1: raise ValueError('unit trace duration does not match observed boundaries')
        if trace.get('source_kind') in FORBIDDEN_TRACE_SOURCES: raise ValueError('forbidden source emitted completion trace')
        if not trace['message'].startswith('완료: '): raise ValueError('unit completion trace message must use completion form')
        if trace.get('durably_persisted') is not True: raise ValueError('unit completion trace lacks durable persistence proof')
        if require_delivery_state and trace.get('delivery_state') not in TRACE_DELIVERY_STATES: raise ValueError('unit trace lacks explicit delivery state')
        if trace.get('continued_same_wake') is not True and record.get('duration_seconds',0)<600: raise ValueError('pre-600 unit trace did not continue same wake')

def validate(record):
    start=timestamp(record['run_started_at'])
    if start<ENFORCE_FROM or record.get('run_ended_at') is None: return
    for key in ('duration_seconds','turn_outcome','end_reason','program_status_at_end','close_decision'):
        if record.get(key) is None: raise ValueError('missing '+key)
    duration=record['duration_seconds']; ended=timestamp(record['run_ended_at']); actual=(ended-start).total_seconds()
    if type(duration) is not int or duration<0 or abs(duration-actual)>=1: raise ValueError('duration does not match observed boundaries')
    outcome=record['turn_outcome']
    if outcome not in {'CONTINUE','COMPLETE','BLOCKED','PAUSED'}: raise ValueError('invalid turn_outcome')
    if record['close_decision'] not in {'TIME_BOUNDARY','TARGET_REACHED_SAFE_BOUNDARY','BUDGET_EXHAUSTED','EXCEPTION','HANDOFF','TERMINAL'}: raise ValueError('invalid close_decision')
    if outcome=='CONTINUE':
        if record['end_reason'] not in VALID_CONTINUE_END_REASONS: raise ValueError('CONTINUE lacks valid end reason')
        if duration<600 and (record.get('short_turn_reason') not in PRE600_CONTINUE_EXCEPTIONS or record['close_decision']!='EXCEPTION' or record['end_reason']!='PLATFORM_ENFORCED_TERMINATION'): raise ValueError('voluntary normal CONTINUE before 10 minutes (600 seconds) is forbidden')
        if record['close_decision']=='BUDGET_EXHAUSTED' and duration<600: raise ValueError('budget exhaustion cannot authorize normal close before 10 minutes (600 seconds)')
        if record['end_reason']=='COMMITTED_SUCCESSOR_HANDOFF': timestamp(record['successor_observed_at'])
        if record['end_reason']=='VERIFIED_SAME_CANONICAL_CONTINUATION':
            due=timestamp(record['verified_next_fast_due_at']); offset=record.get('normal_close_offset_seconds')
            if type(offset) is not int or offset!=NORMAL_CLOSE_OFFSET_SECONDS: raise ValueError('normal close offset must be exactly 1 minute (60 seconds)')
            if int((due-ended).total_seconds())!=NORMAL_CLOSE_OFFSET_SECONDS: raise ValueError('verified fast due must equal ACTUAL END + exactly 1 minute (60 seconds)')
    if outcome=='COMPLETE' and record['program_status_at_end']!='PROGRAM_COMPLETE': raise ValueError('local completion is not program completion')
    useful=record.get('productive_substantive_seconds')
    if useful is not None and (type(useful) is not int or not 0<=useful<=duration): raise ValueError('invalid useful duration')
    policy=record.get('chat_trace_policy')
    if policy=='DURABLE_UNIT_CHAT_TRACE_CANARY_V5_5':
        if record.get('schedule_trace_verified') is not True: raise ValueError('v5.5 run lacks verified schedule trace')
        validate_unit_traces(record)
        if outcome=='CONTINUE' and record.get('final_due_trace_verified') is not True: raise ValueError('v5.5 CONTINUE lacks verified final due trace')
    if policy=='DURABLE_FIRST_FINAL_FLUSH_V5_6':
        if record.get('trace_ledger_ref') is None: raise ValueError('v5.6 run lacks durable trace ledger ref')
        if record.get('schedule_trace_durably_recorded') is not True: raise ValueError('v5.6 run lacks durable schedule trace')
        validate_unit_traces(record,require_delivery_state=True)
        if outcome=='CONTINUE' and record.get('final_due_trace_durably_recorded') is not True: raise ValueError('v5.6 CONTINUE lacks durable final due trace')
        if record.get('intermediate_delivery_required_for_execution_success') is not False: raise ValueError('v5.6 must separate intermediate UI delivery from execution success')

def main():
    errors=[]
    for index,line in enumerate(Path(sys.argv[1]).read_text().splitlines(),1):
        if not line.strip(): continue
        try: validate(json.loads(line))
        except (ValueError,KeyError,TypeError) as exc: errors.append(f'line {index}: {exc}')
    print(json.dumps({'valid':not errors,'errors':errors})); return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
