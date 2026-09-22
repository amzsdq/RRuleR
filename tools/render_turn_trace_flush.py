#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from tools.validate_turn_traces import validate

def pending_messages(doc):
    errors=validate(doc)
    if errors: raise ValueError("; ".join(errors))
    return [t["message"] for t in doc.get("traces",[]) if t.get("delivery_state")=="TRACE_DURABLY_RECORDED"]

def main(path):
    doc=json.loads(Path(path).read_text(encoding="utf-8"))
    for message in pending_messages(doc): print(message)
    return 0

if __name__=="__main__": raise SystemExit(main(sys.argv[1] if len(sys.argv)>1 else "state/TURN_TRACES.json"))
