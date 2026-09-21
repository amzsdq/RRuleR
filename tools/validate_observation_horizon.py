#!/usr/bin/env python3
"""Validate durable observation-horizon state against authoritative GitHub provenance."""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


TRUSTED_ACTION_WORKFLOWS = {
    ".github/workflows/validate-control-plane.yml",
    ".github/workflows/validate-observation-horizon.yml",
}


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


def validate_actions_causality(source, compare_result, current_sha):
    """Require Actions provenance to come from a trusted push workflow on current ancestry."""
    if source.get("event") != "push" or source.get("head_branch") != "main":
        raise ValueError("observation horizon Actions provenance is not a trusted main push")
    if source.get("path") not in TRUSTED_ACTION_WORKFLOWS:
        raise ValueError("observation horizon Actions provenance workflow is not trusted")
    source_sha = source.get("head_sha")
    if not source_sha or not current_sha:
        raise ValueError("observation horizon Actions provenance lacks commit causality")
    status = compare_result.get("status")
    if status not in {"identical", "ahead"}:
        raise ValueError("observation horizon Actions provenance commit is not an ancestor of current commit")
    base = compare_result.get("base_commit", {}).get("sha")
    merge_base = compare_result.get("merge_base_commit", {}).get("sha")
    if status == "identical" and source_sha != current_sha:
        raise ValueError("observation horizon Actions provenance identical comparison is inconsistent")
    if status == "ahead" and base != source_sha and merge_base != source_sha:
        raise ValueError("observation horizon Actions provenance ancestry is inconsistent")
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
    source = api(repo, token, path)
    validate(horizon, policy, source, previous_states=previous_states)
    if kind == "GITHUB_ACTIONS_OBSERVED_TIMESTAMP":
        current_sha = os.environ.get("GITHUB_SHA")
        if not current_sha:
            raise ValueError("GITHUB_SHA is required for Actions provenance causality")
        source_sha = source.get("head_sha", "")
        compare_path = "compare/" + urllib.parse.quote(source_sha, safe="") + "..." + urllib.parse.quote(current_sha, safe="")
        validate_actions_causality(source, api(repo, token, compare_path), current_sha)
    print(f"observation horizon provenance valid: {kind}:{ref}; predecessors={len(previous_states)}")


if __name__ == "__main__":
    main()
