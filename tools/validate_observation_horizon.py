#!/usr/bin/env python3
"""Validate durable observation-horizon state against authoritative GitHub provenance."""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TRUSTED_ACTION_WORKFLOWS = {".github/workflows/validate-control-plane.yml", ".github/workflows/validate-observation-horizon.yml"}

def parsed_instant(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None: raise ValueError("observation horizon timestamp lacks timezone")
    return dt

def instant(value):
    return parsed_instant(value).timestamp()

def canonical_timestamp(value):
    return parsed_instant(value).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def provenance_identity(state):
    return (state.get("provenance_kind"), str(state.get("provenance_ref", "")), state.get("provenance_attempt"))

def provenance_record(state):
    return {"provenance_kind": state.get("provenance_kind"), "provenance_ref": str(state.get("provenance_ref", "")), "provenance_attempt": state.get("provenance_attempt"), "trusted_observed_through": state.get("trusted_observed_through")}

def provenance_history(state):
    history = state.get("provenance_history", [])
    if not isinstance(history, list): raise ValueError("observation provenance history must be a list")
    return history

def record_key(record):
    timestamp = record.get("trusted_observed_through")
    return (record.get("provenance_kind"), str(record.get("provenance_ref", "")), record.get("provenance_attempt"), canonical_timestamp(timestamp) if timestamp else None)

def validate_history_merge(horizon, predecessors):
    """Treat retirement history as an immutable semantic set ledger and reconcile all merge parents."""
    current_history = provenance_history(horizon)
    current_keys = [record_key(record) for record in current_history]
    if len(current_keys) != len(set(current_keys)):
        raise ValueError("observation provenance history contains duplicate retirement records")
    required = set()
    current_identity = provenance_identity(horizon)
    for predecessor in predecessors:
        previous_history = provenance_history(predecessor)
        previous_keys = [record_key(record) for record in previous_history]
        if len(previous_keys) != len(set(previous_keys)):
            raise ValueError("predecessor observation provenance history contains duplicate retirement records")
        required.update(previous_keys)
        if provenance_identity(predecessor) != current_identity:
            required.add(record_key(provenance_record(predecessor)))
    if set(current_keys) != required:
        missing = required - set(current_keys)
        extra = set(current_keys) - required
        if missing: raise ValueError("append-only observation provenance history lost required merge-parent retirement records")
        if extra: raise ValueError("observation provenance history contains unexplained retirement records")
    if current_keys != sorted(current_keys, key=lambda key: tuple("" if v is None else str(v) for v in key)):
        raise ValueError("observation provenance history is not in deterministic canonical order")
    for record in current_history:
        if provenance_identity(record) == current_identity:
            raise ValueError("retired observation provenance identity cannot be reused")

def validate(horizon, policy, source, previous=None, previous_states=None):
    kind = horizon.get("provenance_kind"); ref = str(horizon.get("provenance_ref", "")); trusted = horizon.get("trusted_observed_through")
    if kind not in policy.get("accepted_provenance_kinds", []): raise ValueError("unsupported observation horizon provenance kind")
    if not ref or not trusted: raise ValueError("observation horizon provenance incomplete")
    trusted_instant = instant(trusted)
    predecessors = list(previous_states or [])
    if previous is not None: predecessors.append(previous)
    current_identity = provenance_identity(horizon)
    for predecessor in predecessors:
        previous_trusted = predecessor.get("trusted_observed_through")
        if not previous_trusted: raise ValueError("previous observation horizon incomplete")
        if trusted_instant < instant(previous_trusted): raise ValueError("observation horizon rollback is forbidden")
    for predecessor in predecessors:
        previous_trusted = predecessor.get("trusted_observed_through")
        if provenance_identity(predecessor) == current_identity and instant(previous_trusted) != trusted_instant:
            raise ValueError("same observation provenance identity cannot be repinned to a different timestamp; replace provenance explicitly")
    if predecessors:
        validate_history_merge(horizon, predecessors)
    if kind == "GITHUB_ACTIONS_OBSERVED_TIMESTAMP":
        if not ref.isdigit(): raise ValueError("GitHub Actions provenance ref must be a run id")
        expected_attempt = horizon.get("provenance_attempt")
        if expected_attempt is not None:
            if not isinstance(expected_attempt, int) or expected_attempt < 1: raise ValueError("GitHub Actions provenance attempt is invalid")
            if source.get("run_attempt") != expected_attempt: raise ValueError("observation horizon Actions provenance attempt mismatch")
        if source.get("status") != "completed" or source.get("conclusion") != "success": raise ValueError("observation horizon Actions provenance is not successful/completed")
        authoritative = source.get("updated_at")
    else:
        raise ValueError("accepted provenance kind has no verifier")
    if not authoritative: raise ValueError("authoritative provenance timestamp missing")
    if trusted_instant != instant(authoritative):
        raise ValueError("trusted_observed_through drifted from pinned authoritative provenance timestamp")
    return True

def validate_actions_causality(source, compare_result, current_sha):
    if source.get("event") != "push" or source.get("head_branch") != "main": raise ValueError("observation horizon Actions provenance is not a trusted main push")
    if source.get("path") not in TRUSTED_ACTION_WORKFLOWS: raise ValueError("observation horizon Actions provenance workflow is not trusted")
    source_sha = source.get("head_sha")
    if not source_sha or not current_sha: raise ValueError("observation horizon Actions provenance lacks commit causality")
    status = compare_result.get("status")
    if status not in {"identical", "ahead"}: raise ValueError("observation horizon Actions provenance commit is not an ancestor of current commit")
    base = compare_result.get("base_commit", {}).get("sha"); merge_base = compare_result.get("merge_base_commit", {}).get("sha")
    if status == "identical" and source_sha != current_sha: raise ValueError("observation horizon Actions provenance identical comparison is inconsistent")
    if status == "ahead" and base != source_sha and merge_base != source_sha: raise ValueError("observation horizon Actions provenance ancestry is inconsistent")
    return True

def api(repo, token, path):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/{path}", headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req) as response: return json.load(response)

def load_predecessor_states(previous_paths):
    states=[]
    for path in previous_paths:
        if not path.exists(): raise ValueError(f"explicit predecessor observation horizon file missing: {path}")
        states.append(json.loads(path.read_text()))
    return states

def main():
    horizon_path=Path(sys.argv[1] if len(sys.argv)>1 else "state/OBSERVATION_HORIZON.json"); policy_path=Path(sys.argv[2] if len(sys.argv)>2 else "control/observation-horizon.v1.json"); previous_paths=[Path(p) for p in sys.argv[3:]]
    horizon=json.loads(horizon_path.read_text()); policy=json.loads(policy_path.read_text()); previous_states=load_predecessor_states(previous_paths)
    kind=horizon.get("provenance_kind"); ref=str(horizon.get("provenance_ref", "")); repo=os.environ["REPO"]; token=os.environ["GH_TOKEN"]
    if kind != "GITHUB_ACTIONS_OBSERVED_TIMESTAMP": raise ValueError("accepted provenance kind has no verifier")
    attempt=horizon.get("provenance_attempt")
    if not isinstance(attempt, int) or attempt < 1: raise ValueError("GitHub Actions provenance must bind a specific run attempt")
    source=api(repo, token, f"actions/runs/{ref}/attempts/{attempt}")
    validate(horizon, policy, source, previous_states=previous_states)
    current_sha=os.environ.get("GITHUB_SHA")
    if not current_sha: raise ValueError("GITHUB_SHA is required for Actions provenance causality")
    source_sha=source.get("head_sha", ""); compare_path="compare/"+urllib.parse.quote(source_sha,safe="")+"..."+urllib.parse.quote(current_sha,safe="")
    validate_actions_causality(source, api(repo,token,compare_path), current_sha)
    print(f"observation horizon provenance valid: {kind}:{ref}:attempt:{attempt}; predecessors={len(previous_states)}")

if __name__ == "__main__": main()
