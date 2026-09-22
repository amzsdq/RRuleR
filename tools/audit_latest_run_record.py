#!/usr/bin/env python3
import json, sys
from pathlib import Path

CLOSED_STATES={"CHECKPOINTED","HANDOFF_COMMITTED"}

def load_runs(path):
    out=[]
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip(): out.append(json.loads(line))
    return out

def audit(current,runs):
    errors=[]
    if current.get("run_state") not in CLOSED_STATES: return errors
    run_id=current.get("current_owner")
    matches=[r for r in runs if r.get("run_id")==run_id or r.get("observation_id")==run_id]
    if not matches:
        errors.append(f"closed current owner {run_id} has no RUNS record")
        return errors
    closed=[r for r in matches if r.get("run_ended_at") is not None]
    if not closed: errors.append(f"closed current owner {run_id} lacks closed RUNS record")
    return errors

def main(current_path='state/CURRENT.json',runs_path='state/RUNS.jsonl'):
    current=json.loads(Path(current_path).read_text(encoding='utf-8')); errors=audit(current,load_runs(runs_path))
    print(json.dumps({'valid':not errors,'errors':errors})); return int(bool(errors))
if __name__=='__main__': raise SystemExit(main(*(sys.argv[1:3])))
