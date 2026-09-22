#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from tools.validate_turn_traces import validate

def append_trace(doc, trace):
    candidate=json.loads(json.dumps(doc))
    candidate.setdefault("traces",[]).append(trace)
    errors=validate(candidate)
    if errors: raise ValueError("; ".join(errors))
    return candidate

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ledger",default="state/TURN_TRACES.json")
    p.add_argument("--trace-json",required=True)
    args=p.parse_args()
    path=Path(args.ledger)
    doc=json.loads(path.read_text(encoding="utf-8"))
    trace=json.loads(args.trace_json)
    updated=append_trace(doc,trace)
    path.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(trace["trace_id"])

if __name__=="__main__": main()
