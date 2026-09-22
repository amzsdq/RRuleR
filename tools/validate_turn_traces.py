#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ALLOWED={"TRACE_DURABLY_RECORDED","TRACE_INTERMEDIATE_DELIVERED","TRACE_FINAL_FLUSH_DELIVERED"}
QUALIFYING={"BOUNDED_SUBSTANTIVE_UNIT"}

def validate(doc):
    errors=[]
    if doc.get("schema_version")!="1.0": errors.append("unsupported schema_version")
    if doc.get("rules",{}).get("durable_before_delivery") is not True: errors.append("durable_before_delivery must be true")
    seen=set()
    for i,t in enumerate(doc.get("traces",[])):
        p=f"traces[{i}]"
        tid=t.get("trace_id")
        if not tid or tid in seen: errors.append(f"{p}: missing/duplicate trace_id")
        seen.add(tid)
        state=t.get("delivery_state")
        if state not in ALLOWED: errors.append(f"{p}: invalid delivery_state")
        if not t.get("created_at") or not t.get("message"): errors.append(f"{p}: created_at/message required")
        evidence=t.get("evidence")
        if not isinstance(evidence,list) or not evidence: errors.append(f"{p}: durable evidence required")
        if t.get("kind") in QUALIFYING and not str(t.get("message","")).startswith("완료:"):
            errors.append(f"{p}: substantive unit trace must start with 완료:")
    return errors

def main(path):
    doc=json.loads(Path(path).read_text(encoding="utf-8"))
    errors=validate(doc)
    if errors:
        print("TURN_TRACE_INVALID")
        for e in errors: print(e)
        return 1
    print(f"TURN_TRACE_VALID count={len(doc.get('traces',[]))}")
    return 0

if __name__=="__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv)>1 else "state/TURN_TRACES.json"))
