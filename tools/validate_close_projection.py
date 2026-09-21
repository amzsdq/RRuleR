#!/usr/bin/env python3
"""Validate mutually consistent CURRENT/ACTIVITY/HANDOFF ownership projections."""
from __future__ import annotations
import json, sys
from pathlib import Path

def validate_projection(current: dict, activity: dict, handoff: dict) -> dict:
    errors=[]; run_state=current.get('run_state'); owner=current.get('current_owner'); epoch=current.get('authority_epoch'); next_due=current.get('continuation',{}).get('next_due_at')
    if activity.get('authority_epoch') != epoch: errors.append('ACTIVITY_AUTHORITY_EPOCH_MISMATCH')
    if run_state == 'WORKING':
        if activity.get('status') != 'WORKING': errors.append('WORKING_CURRENT_REQUIRES_WORKING_ACTIVITY')
        if activity.get('active_run_id') != owner: errors.append('WORKING_ACTIVITY_OWNER_MISMATCH')
        if activity.get('handoff_ready') is not False: errors.append('WORKING_ACTIVITY_CANNOT_BE_HANDOFF_READY')
        if handoff.get('successor_run_id') != owner: errors.append('WORKING_HANDOFF_SUCCESSOR_MISMATCH')
        if activity.get('next_wake_due_at') != next_due: errors.append('WORKING_ACTIVITY_NEXT_DUE_MISMATCH')
        if handoff.get('handoff_state') not in {'SUCCESSOR_WORKING','WORKING'}: errors.append('WORKING_HANDOFF_STATE_MISMATCH')
    elif run_state == 'HANDOFF_COMMITTED':
        if activity.get('status') != 'HANDOFF_READY': errors.append('CLOSED_CURRENT_REQUIRES_HANDOFF_READY_ACTIVITY')
        if activity.get('active_run_id') is not None: errors.append('CLOSED_ACTIVITY_MUST_CLEAR_ACTIVE_RUN_ID')
        if activity.get('handoff_ready') is not True: errors.append('CLOSED_ACTIVITY_MUST_BE_HANDOFF_READY')
        if handoff.get('handoff_state') != 'COMMITTED': errors.append('CLOSED_CURRENT_REQUIRES_COMMITTED_HANDOFF')
        if handoff.get('predecessor_run_id') != owner: errors.append('CLOSED_HANDOFF_PREDECESSOR_MISMATCH')
        if handoff.get('predecessor_authority_epoch') != epoch: errors.append('CLOSED_HANDOFF_AUTHORITY_EPOCH_MISMATCH')
        if activity.get('next_wake_due_at') != next_due: errors.append('CLOSED_ACTIVITY_NEXT_DUE_MISMATCH')
        if handoff.get('successor_expected_at') != next_due: errors.append('CLOSED_HANDOFF_NEXT_DUE_MISMATCH')
    return {'valid':not errors,'run_state':run_state,'owner':owner,'authority_epoch':epoch,'errors':errors}

def main():
    if len(sys.argv)!=4: print('usage: validate_close_projection.py CURRENT_JSON ACTIVITY_JSON HANDOFF_JSON',file=sys.stderr); return 2
    result=validate_projection(*[json.loads(Path(p).read_text(encoding='utf-8')) for p in sys.argv[1:4]])
    print(json.dumps(result,indent=2,sort_keys=True)); return int(not result['valid'])
if __name__=='__main__': raise SystemExit(main())
