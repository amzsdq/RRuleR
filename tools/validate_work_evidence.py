#!/usr/bin/env python3
"""Deterministically validate RRuleR forward-only useful-work evidence."""
from __future__ import annotations
import json, sys
from datetime import datetime, timedelta
from pathlib import Path
WINDOW_SECONDS=900; TARGET_USEFUL_SECONDS=840; MAX_GAP_SECONDS=120; ACCEPTED="SUBSTANTIVE_ACCEPTED"
def ts(value:str)->datetime:
    dt=datetime.fromisoformat(value)
    if dt.tzinfo is None: raise ValueError("timestamp must include timezone")
    return dt
def validate_record(record:dict)->list[str]:
    errors=[]
    for key in ("start_at","end_at","kind","artifact","qualification","basis"):
        if not record.get(key): errors.append(f"MISSING_{key.upper()}")
    if errors: return errors
    if record["qualification"]!=ACCEPTED: errors.append("NOT_SUBSTANTIVE_ACCEPTED")
    if record.get("start_boundary")!="OBSERVED" or record.get("end_boundary")!="OBSERVED": errors.append("BOUNDARY_NOT_OBSERVED")
    try:
        start,end=ts(record["start_at"]),ts(record["end_at"]); duration=(end-start).total_seconds()
        if duration<=0: errors.append("NON_POSITIVE_INTERVAL")
        declared=record.get("observed_seconds")
        if declared is not None and (not isinstance(declared,(int,float)) or isinstance(declared,bool) or abs(float(declared)-duration)>1e-9): errors.append("OBSERVED_SECONDS_MISMATCH")
    except (TypeError,ValueError): errors.append("INVALID_TIMESTAMP")
    return errors
def audit(data:dict,window_start:str|None=None,observed_through:str|None=None)->dict:
    record_results=[]; intervals=[]
    for i,record in enumerate(data.get("records",[])):
        errors=validate_record(record); record_results.append({"index":i,"errors":errors})
        if not errors: intervals.append((ts(record["start_at"]),ts(record["end_at"]),i))
    intervals.sort(); overlap_errors=[]
    for left,right in zip(intervals,intervals[1:]):
        if right[0]<left[1]: overlap_errors.append({"left":left[2],"right":right[2],"reason":"OVERLAPPING_INTERVALS"})
    result={"record_results":record_results,"overlap_errors":overlap_errors,"window":None,"promotion":"INCOMPLETE"}
    if window_start is None: return result
    start=ts(window_start); end=start+timedelta(seconds=WINDOW_SECONDS)
    horizon=ts(observed_through) if observed_through else max((b for _,b,_ in intervals),default=None)
    if horizon is None or horizon<end:
        result["window"]={"start_at":start.isoformat(),"end_at":end.isoformat(),"observed_through":horizon.isoformat() if horizon else None,"reasons":["WINDOW_NOT_YET_COMPLETE"]}
        return result
    clipped=[]
    for a,b,idx in intervals:
        x,y=max(a,start),min(b,end,horizon)
        if y>x: clipped.append((x,y,idx))
    useful=sum((b-a).total_seconds() for a,b,_ in clipped); gaps=[]; cursor=start
    for a,b,idx in clipped:
        if a>cursor: gaps.append((cursor,a))
        cursor=max(cursor,b)
    if cursor<end: gaps.append((cursor,end))
    max_gap=max(((b-a).total_seconds() for a,b in gaps),default=0); reasons=[]
    if any(r["errors"] for r in record_results): reasons.append("INVALID_RECORD_PRESENT")
    if overlap_errors: reasons.append("OVERLAPPING_INTERVALS")
    if max_gap>MAX_GAP_SECONDS: reasons.append("UNEXPLAINED_GAP_GT_120_SECONDS")
    if useful<TARGET_USEFUL_SECONDS: reasons.append("USEFUL_SECONDS_LT_840")
    result["window"]={"start_at":start.isoformat(),"end_at":end.isoformat(),"observed_through":horizon.isoformat(),"useful_seconds":useful,"maximum_unexplained_gap_seconds":max_gap,"interval_count":len(clipped),"reasons":reasons}
    result["promotion"]="VALID_ACCEPTED" if not reasons else "REJECTED"; return result
def main()->int:
    if len(sys.argv) not in (2,3,4):
        print("usage: validate_work_evidence.py STATE_JSON [WINDOW_START_ISO] [OBSERVED_THROUGH_ISO]",file=sys.stderr); return 2
    data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")); result=audit(data,sys.argv[2] if len(sys.argv)>=3 else None,sys.argv[3] if len(sys.argv)==4 else None)
    print(json.dumps(result,indent=2,sort_keys=True)); return 0 if result["promotion"]!="REJECTED" else 1
if __name__=="__main__": raise SystemExit(main())
