# Durable State

## Files

- `CURRENT.json` — compact machine-readable projection of the current root job.
- `HANDOFF.json` — explicit predecessor/successor coordination state for the current handoff.
- `RELAY_VALIDATION.json` — machine-readable acceptance ledger for the reproduced RRULE self-relay.
- `EVENTS.jsonl` — append-oriented public-safe relay event ledger.
- `RUNS.jsonl` — run/handoff/utilization observation ledger.

Detailed history also remains available in Git commits, experiment records, task/spec documents, and Actions evidence.

## CURRENT.json requirements

It must remain:

- public-safe;
- sufficient for cold-start reconstruction;
- explicit about owner/authority epoch;
- explicit about latest checkpoint;
- explicit about exact next action;
- explicit about continuation mode;
- explicit that voluntary idle before successor observation is forbidden for this relay;
- free of secrets and private source material.

Chat output may summarize this state but cannot override it.

## RELAY_VALIDATION.json

This is the machine-readable acceptance surface for the live relay experiment. It separates proven criteria from pending observations so a fresh session does not have to infer PASS from prose.

Rules:

- preserve the canonical automation ID;
- mark each criterion `PASS`, `PASS_WITH_SCOPE`, `PENDING`, or `FAIL`;
- never infer overlap/serialization or timing values from missing evidence;
- link concrete run/commit/schedule evidence in the criterion or current checkpoint;
- only promote overall `status` to `PASS` when the documented pass rule is satisfied.

Schema: `schemas/relay-validation.schema.json`.

## EVENTS.jsonl

Each non-empty line is one JSON object following `schemas/relay-event.schema.json`.

Use stable unique `event_id` values. Relevant event classes include wake update, work start, checkpoint, successor observation, handoff, degraded continuation, completion, and external block.

Do not rewrite history merely to improve presentation. Correct later with a new event when necessary.

## RUNS.jsonl

Each non-empty line is a run observation following `schemas/run-observation.schema.json`.

Use it to measure:

- run start/end;
- successor observation;
- productive work;
- checkpoint/handoff overhead;
- relay-caused idle gap;
- successor wait;
- classification.

Do not invent timing values that were not observed. Null is preferable to fabricated precision.
