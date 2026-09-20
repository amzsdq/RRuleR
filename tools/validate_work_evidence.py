#!/usr/bin/env python3
"""Deterministically validate RRuleR forward-only useful-work evidence."""
from __future__ import annotations
import json, sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
WINDOW_SECONDS=900; TARGET_USEFUL_SECONDS=840; MAX_GAP_SECONDS=120; ACCEPTED="SUBSTANTIVE_ACCEPTED"
def ts(value:str)->datetime:
    dt=datetime.fromisoformat(value)
    if dt.tzinfo is None: raise ValueError("timestamp must include timezone")
    return dt
def fixed_window_start(value:str|datetime)->datetime:
    dt=ts(value) if isinstance(value,str) else value
    if dt.tzinfo is None: raise ValueError("timestamp must include timezone")
    epoch_seconds=int(dt.timestamp()); bucket=epoch_seconds-(epoch_seconds%WINDOW_SECONDS)
    return datetime.fromtimestamp(bucket,tz=timezone.utc)
def enumerate_completed_fixed_windows(first_observed:str,last_observed:str)->list[str]:
    first,last=ts(first_observed),ts(last_observed)
    if last<first: raise ValueError("last_observed precedes first_observed")
    start=fixed_window_start(first); first_utc=first.astimezone(timezone.utc); last_utc=last.astimezone(timezone.utc)
    if first_utc>start: start+=timedelta(seconds=WINDOW_SECONDS)
    out=[]
    while start+timedelta(seconds=WINDOW_SECONDS)<=last_utc:
        out.append(start.isoformat()); start+=timedelta(seconds=WINDOW_SECONDS)
    return out
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
    try: a,b=ts(record["start_at"]),ts(record["end_at"])
    except (KeyError,TypeError,ValueError): return None
    return b>start and a<end
def _merge_intervals(intervals:list[tuple[datetime,datetime,int]])->list[tuple[datetime,datetime]]:
    merged=[]
    for a,b,_ in sorted(intervals):
        if not merged or a>merged[-1][1]: merged.append([a,b])
        elif b>merged[-1][1]: merged[-1][1]=b
    return [(a,b) for a,b in merged]
def audit(data:dict,window_start:str|None=None,observed_through:str|None=None,trusted_observed_through:str|None=None)->dict:
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
    try:
        requested=ts(observed_through) if observed_through else max((b for _,b,_ in intervals),default=None)
        trusted=ts(trusted_observed_through) if trusted_observed_through else None
    except (TypeError,ValueError):
        result["window"]={"start_at":start.isoformat(),"end_at":end.isoformat(),"observed_through":observed_through,"reasons":["INVALID_OBSERVATION_HORIZON"]}; result["promotion"]="REJECTED"; return result
    if requested is not None and trusted is not None and requested>trusted:
        result["window"]={"start_at":start.isoformat(),"end_at":end.isoformat(),"observed_through":requested.isoformat(),"trusted_observed_through":trusted.isoformat(),"reasons":["UNTRUSTED_OBSERVATION_HORIZON"]}; result["promotion"]="REJECTED"; return result
    horizon=requested
    if horizon is None or horizon<end:
        result["window"]={"start_at":start.isoformat(),"end_at":end.isoformat(),"observed_through":horizon.isoformat() if horizon else None,"reasons":["WINDOW_NOT_YET_COMPLETE"]}; return result
    clipped=[]
    for a,b,idx in intervals:
        x,y=max(a,start),min(b,end,horizon)
        if y>x: clipped.append((x,y,idx))
    union=_merge_intervals(clipped); useful=sum((b-a).total_seconds() for a,b in union); gaps=[]; cursor=start
    for a,b in union:
        if a>cursor: gaps.append((cursor,a))
        cursor=max(cursor,b)
    if cursor<end: gaps.append((cursor,end))
    max_gap=max(((b-a).total_seconds() for a,b in gaps),default=0); reasons=[]
    if start.astimezone(timezone.utc)!=fixed_window_start(start): reasons.append("NON_FIXED_WINDOW_BOUNDARY")
    invalid_in_window=any(rr["errors"] and _record_intersects_window(record,start,end) is not False for rr,record in zip(record_results,records))
    overlap_in_window=any(_record_intersects_window(records[e["left"]],start,end) is not False or _record_intersects_window(records[e["right"]],start,end) is not False for e in overlap_errors)
    if invalid_in_window: reasons.append("INVALID_RECORD_PRESENT")
    if overlap_in_window: reasons.append("OVERLAPPING_INTERVALS")
    if max_gap>MAX_GAP_SECONDS: reasons.append("UNEXPLAINED_GAP_GT_120_SECONDS")
    if useful<TARGET_USEFUL_SECONDS: reasons.append("USEFUL_SECONDS_LT_840")
    result["window"]={"start_at":start.isoformat(),"end_at":end.isoformat(),"observed_through":horizon.isoformat(),"trusted_observed_through":trusted.isoformat() if trusted else None,"useful_seconds":useful,"maximum_unexplained_gap_seconds":max_gap,"interval_count":len(clipped),"union_interval_count":len(union),"reasons":reasons}
    result["promotion"]="VALID_ACCEPTED" if not reasons else "REJECTED"; return result
def evaluate_consecutive_windows(data:dict,first_observed:str,last_observed:str,required:int=3,trusted_observed_through:str|None=None)->dict:
    if required<=0: raise ValueError("required must be positive")
    try: starts=enumerate_completed_fixed_windows(first_observed,last_observed)
    except (TypeError,ValueError) as exc:
        return {"required_consecutive_windows":required,"completed_window_count":0,"windows":[],"longest_consecutive_accepted":0,"selection_policy":"FRESHEST_LONGEST_STREAK_THEN_FRESHEST_REQUIRED_WINDOWS","selected_windows":[],"rolling_mean_useful_seconds":None,"p0_acceptance":"NOT_YET","observation_boundary_error":str(exc)}
    windows=[]
    for start in starts:
        result=audit(data,start,last_observed,trusted_observed_through); window=result["window"] or {}
        windows.append({"start_at":start,"promotion":result["promotion"],"useful_seconds":window.get("useful_seconds"),"maximum_unexplained_gap_seconds":window.get("maximum_unexplained_gap_seconds"),"reasons":window.get("reasons",[])})
    streak=[]; best=[]
    for window in windows:
        if window["promotion"]=="VALID_ACCEPTED":
            streak.append(window)
            if len(streak)>=len(best): best=list(streak)
        else: streak=[]
    selected=best[-required:] if len(best)>=required else []
    mean=(sum(float(w["useful_seconds"]) for w in selected)/required) if selected else None
    accepted=bool(selected) and mean>=TARGET_USEFUL_SECONDS
    return {"required_consecutive_windows":required,"completed_window_count":len(windows),"windows":windows,"longest_consecutive_accepted":len(best),"selection_policy":"FRESHEST_LONGEST_STREAK_THEN_FRESHEST_REQUIRED_WINDOWS","selected_windows":[w["start_at"] for w in selected],"rolling_mean_useful_seconds":mean,"p0_acceptance":"PASS" if accepted else "NOT_YET","observation_boundary_error":None}
def _load_trusted_horizon(state_path:Path)->str|None:
    path=state_path.parent/"OBSERVATION_HORIZON.json"
    if not path.exists(): return None
    return json.loads(path.read_text(encoding="utf-8")).get("trusted_observed_through")
def main()->int:
    if len(sys.argv) not in (2,3,4): print("usage: validate_work_evidence.py STATE_JSON [WINDOW_START_ISO] [OBSERVED_THROUGH_ISO]",file=sys.stderr); return 2
    state_path=Path(sys.argv[1]); data=json.loads(state_path.read_text(encoding="utf-8")); trusted=_load_trusted_horizon(state_path)
    result=audit(data,sys.argv[2] if len(sys.argv)>=3 else None,sys.argv[3] if len(sys.argv)==4 else None,trusted)
    print(json.dumps(result,indent=2,sort_keys=True)); return 0 if result["promotion"]!="REJECTED" else 1
if __name__=="__main__": raise SystemExit(main())
