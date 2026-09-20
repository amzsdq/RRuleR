#!/usr/bin/env python3
"""Deterministically validate RRuleR forward-only useful-work evidence."""
from __future__ import annotations
import json, sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
WINDOW_SECONDS=900; TARGET_USEFUL_SECONDS=840; MAX_GAP_SECONDS=120; ACCEPTED="SUBSTANTIVE_ACCEPTED"
def ts(value:str)->datetime:
    dt=datetime.fromisoformat(value)
    if dt.tzinfo is None: raise ValueError("timestamp must include timezone")
    return dt
def validate_record(record:dict)->list[str]:
    errors=[]
    for key in ("record_id","start_at","end_at","kind","artifact","qualification","basis"):
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
def _record_intersects_window(record:dict,start:datetime,end:datetime)->bool|None:
    """True/False when boundaries are parseable; None means scope is unknowable and must fail closed."""
    try:
        a,b=ts(record["start_at"]),ts(record["end_at"])
    except (KeyError,TypeError,ValueError):
        return None
    return b>start and a<end
def _merge_intervals(intervals:list[tuple[datetime,datetime,int]])->list[tuple[datetime,datetime]]:
    """Return the union of already-clipped intervals; overlap remains separately auditable/rejectable."""
    merged=[]
    for a,b,_ in sorted(intervals):
        if not merged or a>merged[-1][1]:
            merged.append([a,b])
        elif b>merged[-1][1]:
            merged[-1][1]=b
    return [(a,b) for a,b in merged]
def audit(data:dict,window_start:str|None=None,observed_through:str|None=None)->dict:
    records=data.get("records",[]); ids=Counter(r.get("record_id") for r in records if r.get("record_id")); duplicate_ids=sorted(k for k,v in ids.items() if v>1)
    record_results=[]; intervals=[]
    for i,record in enumerate(records):
        errors=validate_record(record)
        if record.get("record_id") in duplicate_ids: errors.append("DUPLICATE_RECORD_ID")
        record_results.append({"index":i,"errors":errors})
        if not errors: intervals.append((ts(record["start_at"]),ts(record["end_at"]),i))
    intervals.sort(); overlap_errors=[]
    for left,right in zip(intervals,intervals[1:]):
        if right[0]<left[1]: overlap_errors.append({"left":left[2],"right":right[2],"reason":"OVERLAPPING_INTERVALS"})
    result={"record_results":record_results,"duplicate_record_ids":duplicate_ids,"overlap_errors":overlap_errors,"window":None,"promotion":"INCOMPLETE"}
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
    union=_merge_intervals(clipped)
    useful=sum((b-a).total_seconds() for a,b in union); gaps=[]; cursor=start
    for a,b in union:
        if a>cursor: gaps.append((cursor,a))
        cursor=max(cursor,b)
    if cursor<end: gaps.append((cursor,end))
    max_gap=max(((b-a).total_seconds() for a,b in gaps),default=0); reasons=[]
    invalid_in_window=any(
        rr["errors"] and _record_intersects_window(record,start,end) is not False
        for rr,record in zip(record_results,records)
    )
    overlap_in_window=any(
        _record_intersects_window(records[e["left"]],start,end) is not False or
        _record_intersects_window(records[e["right"]],start,end) is not False
        for e in overlap_errors
    )
    if invalid_in_window: reasons.append("INVALID_RECORD_PRESENT")
    if overlap_in_window: reasons.append("OVERLAPPING_INTERVALS")
    if max_gap>MAX_GAP_SECONDS: reasons.append("UNEXPLAINED_GAP_GT_120_SECONDS")
    if useful<TARGET_USEFUL_SECONDS: reasons.append("USEFUL_SECONDS_LT_840")
    result["window"]={"start_at":start.isoformat(),"end_at":end.isoformat(),"observed_through":horizon.isoformat(),"useful_seconds":useful,"maximum_unexplained_gap_seconds":max_gap,"interval_count":len(clipped),"union_interval_count":len(union),"reasons":reasons}
    result["promotion"]="VALID_ACCEPTED" if not reasons else "REJECTED"; return result
def main()->int:
    if len(sys.argv) not in (2,3,4):
        print("usage: validate_work_evidence.py STATE_JSON [WINDOW_START_ISO] [OBSERVED_THROUGH_ISO]",file=sys.stderr); return 2
    data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")); result=audit(data,sys.argv[2] if len(sys.argv)>=3 else None,sys.argv[3] if len(sys.argv)==4 else None)
    print(json.dumps(result,indent=2,sort_keys=True)); return 0 if result["promotion"]!="REJECTED" else 1
if __name__=="__main__": raise SystemExit(main())
