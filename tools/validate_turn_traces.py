#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

ALLOWED={"TRACE_DURABLY_RECORDED","TRACE_INTERMEDIATE_DELIVERED","TRACE_FINAL_FLUSH_DELIVERED"}
QUALIFYING={"BOUNDED_SUBSTANTIVE_UNIT"}

def parse_ts(value):
    try: return datetime.fromisoformat(value)
    except Exception: return None

def validate(doc):
    errors=[]; rules=doc.get("rules",{})
    if doc.get("schema_version")!="1.0": errors.append("unsupported schema_version")
    if not doc.get("active_run_id") or not isinstance(doc.get("authority_epoch"),int): errors.append("active run identity required")
    if set(doc.get("delivery_states",[])) != ALLOWED: errors.append("delivery_states declaration drift")
    if rules.get("durable_before_delivery") is not True: errors.append("durable_before_delivery must be true")
    if rules.get("trace_is_never_close_authority") is not True: errors.append("trace_is_never_close_authority must be true")
    if rules.get("unit_trace_requires_artifact_backed_work_evidence") is not True: errors.append("unit trace evidence rule must be true")
    if rules.get("delivery_must_not_be_inferred") is not True: errors.append("delivery_must_not_be_inferred must be true")
    if rules.get("final_flush_required_for_undelivered_traces") is not True: errors.append("final flush rule must be true")
    seen=set(); previous=None; final_flush_seen=False
    for i,t in enumerate(doc.get("traces",[])):
        p=f"traces[{i}]"; tid=t.get("trace_id")
        if not tid or tid in seen: errors.append(f"{p}: missing/duplicate trace_id")
        seen.add(tid); state=t.get("delivery_state")
        if state not in ALLOWED: errors.append(f"{p}: invalid delivery_state")
        ts=parse_ts(t.get("created_at"))
        if ts is None: errors.append(f"{p}: valid created_at required")
        elif previous is not None and ts < previous: errors.append(f"{p}: traces must be chronological")
        if ts is not None: previous=ts
        if not t.get("message"): errors.append(f"{p}: message required")
        evidence=t.get("evidence")
        if not isinstance(evidence,list) or not evidence: errors.append(f"{p}: durable evidence required")
        if t.get("kind") in QUALIFYING and not str(t.get("message","")).startswith("완료:"): errors.append(f"{p}: substantive unit trace must start with 완료:")
        if state=="TRACE_FINAL_FLUSH_DELIVERED": final_flush_seen=True
        elif final_flush_seen: errors.append(f"{p}: undelivered/intermediate trace cannot follow final-flush-delivered trace")
    return errors

def main(path):
    doc=json.loads(Path(path).read_text(encoding="utf-8")); errors=validate(doc)
    if errors:
        print("TURN_TRACE_INVALID"); [print(e) for e in errors]; return 1
    print(f"TURN_TRACE_VALID count={len(doc.get('traces',[]))}"); return 0

if __name__=="__main__": raise SystemExit(main(sys.argv[1] if len(sys.argv)>1 else "state/TURN_TRACES.json"))
