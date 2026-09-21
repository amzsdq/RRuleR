#!/usr/bin/env python3
"""Validate durable observation-horizon state against authoritative GitHub provenance."""
import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path


def instant(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("observation horizon timestamp lacks timezone")
    return dt.timestamp()


def validate(horizon, policy, source, previous=None, previous_states=None):
    kind = horizon.get("provenance_kind")
    ref = str(horizon.get("provenance_ref", ""))
    trusted = horizon.get("trusted_observed_through")
    if kind not in policy.get("accepted_provenance_kinds", []):
        raise ValueError("unsupported observation horizon provenance kind")
    if not ref or not trusted:
        raise ValueError("observation horizon provenance incomplete")
    trusted_instant = instant(trusted)
    predecessors = list(previous_states or [])
    if previous is not None:
        predecessors.append(previous)
    for predecessor in predecessors:
        previous_trusted = predecessor.get("trusted_observed_through")
        if not previous_trusted:
            raise ValueError("previous observation horizon incomplete")
        if trusted_instant < instant(previous_trusted):
            raise ValueError("observation horizon rollback is forbidden")
    if kind == "GITHUB_ACTIONS_OBSERVED_TIMESTAMP":
        if not ref.isdigit():
            raise ValueError("GitHub Actions provenance ref must be a run id")
        if source.get("status") != "completed" or source.get("conclusion") != "success":
            raise ValueError("observation horizon Actions provenance is not successful/completed")
        authoritative = source.get("updated_at")
    elif kind == "GITHUB_COMMIT_COMMITTER_TIMESTAMP":
        authoritative = source.get("commit", {}).get("committer", {}).get("date")
    else:
        raise ValueError("accepted provenance kind has no verifier")
    if not authoritative or trusted_instant != instant(authoritative):
        raise ValueError("trusted_observed_through does not match authoritative provenance timestamp")
    return True


def api(repo, token, path):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/{path}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
    )
    with urllib.request.urlopen(req) as response:
        return json.load(response)


def load_predecessor_states(previous_paths):
    states = []
    for path in previous_paths:
        if not path.exists():
            raise ValueError(f"explicit predecessor observation horizon file missing: {path}")
        states.append(json.loads(path.read_text()))
    return states


def main():
    horizon_path = Path(sys.argv[1] if len(sys.argv) > 1 else "state/OBSERVATION_HORIZON.json")
    policy_path = Path(sys.argv[2] if len(sys.argv) > 2 else "control/observation-horizon.v1.json")
    previous_paths = [Path(p) for p in sys.argv[3:]]
    horizon = json.loads(horizon_path.read_text())
    policy = json.loads(policy_path.read_text())
    previous_states = load_predecessor_states(previous_paths)
    kind = horizon.get("provenance_kind")
    ref = str(horizon.get("provenance_ref", ""))
    repo = os.environ["REPO"]
    token = os.environ["GH_TOKEN"]
    path = f"actions/runs/{ref}" if kind == "GITHUB_ACTIONS_OBSERVED_TIMESTAMP" else f"commits/{ref}"
    validate(horizon, policy, api(repo, token, path), previous_states=previous_states)
    print(f"observation horizon provenance valid: {kind}:{ref}; predecessors={len(previous_states)}")


if __name__ == "__main__":
    main()
