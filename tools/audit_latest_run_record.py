#!/usr/bin/env python3
import json, sys
from pathlib import Path
CLOSED_STATES={"CHECKPOINTED","HANDOFF_COMMITTED"}
def load_runs(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
def matches_owner(record,run_id):
    return record.get("run_id")==run_id or record.get("observation_id") in {run_id,"OBS-"+run_id}
def audit(current,runs):
    errors=[]
    if current.get("run_state") not in CLOSED_STATES: return errors
    run_id=current.get("current_owner"); matches=[r for r in runs if matches_owner(r,run_id)]
    if not matches: return [f"closed current owner {run_id} has no RUNS record"]
    if not any(r.get("run_ended_at") is not None for r in matches): errors.append(f"closed current owner {run_id} lacks closed RUNS record")
    return errors
def main(current_path='state/CURRENT.json',runs_path='state/RUNS.jsonl'):
    current=json.loads(Path(current_path).read_text(encoding='utf-8')); errors=audit(current,load_runs(runs_path)); print(json.dumps({'valid':not errors,'errors':errors})); return int(bool(errors))
if __name__=='__main__': raise SystemExit(main(*(sys.argv[1:3])))
