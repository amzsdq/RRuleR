# Durable State

## Files

- `CURRENT.json` — compact machine-readable projection of the current program/root job.
- `HANDOFF.json` — explicit predecessor/successor coordination state for the current handoff.
- `ACTIVITY.json` — durable operator-facing liveness heartbeat: armed/working/handoff/terminal state, active run identity, last progress, current unit, and next wake.
- `WORK_EVIDENCE.json` — strict forward-only accepted useful-work intervals; unknown time is never inferred.
- `PREDICTIVE_PREARM_CANARY.json` — active UTIL-EXP-018 canary state and measured cross-turn latency samples.
- `RELAY_VALIDATION.json` — machine-readable acceptance ledger for the reproduced RRULE self-relay.
- `EVENTS.jsonl` — append-oriented public-safe relay event ledger.
- `RUNS.jsonl` — run/handoff/utilization observation ledger.

Detailed history also remains available in Git commits, experiment records, task/spec documents, and Actions evidence.

## CURRENT.json requirements

It must remain public-safe; sufficient for cold-start reconstruction; explicit about program status, owner/authority epoch, checkpoint, exact next action, continuation mode, and program-vs-root completion; and free of secrets/private source material.

## ACTIVITY.json

`WORKING` requires an `active_run_id`. Refresh after meaningful work units when practical. `ARMED` means continuation exists but no active executor is claimed. Schedule existence alone never proves useful work.

Schema: `schemas/activity.schema.json`.

## WORK_EVIDENCE.json

This is the strict useful-work acceptance ledger used for P0 measurement. It does not infer work from commits, schedules, or heartbeats.

Prospective capture rules:

- both interval boundaries are actually observed and timezone-aware;
- a materially new substantive artifact supports the interval;
- intervals do not overlap and record IDs are unique;
- evidence authority epochs do not move backward;
- scheduler-only, heartbeat-only, waiting, timestamp-only, and evidence-bookkeeping-only activity is not useful work;
- missing historical time remains unknown.

`tools/append_work_evidence.py` provides guarded append semantics. `tools/validate_work_evidence.py` audits the ledger/promotion windows. `tools/summarize_work_evidence.py` reports freshness/totals without converting unknown time.

When the available connector surface cannot safely append the monolithic one-line ledger without rewriting unrelated history, an observed candidate may be persisted under `state/evidence-pending/`. Pending evidence is **not** P0-accepted evidence and must be ignored by promotion until validated and canonically appended. This preserves observed boundaries without falsely claiming acceptance.

## PREDICTIVE_PREARM_CANARY.json

This is the durable measurement surface for `UTIL-EXP-018`.

Purpose: determine whether arming the same canonical successor before predecessor close can hide scheduler delivery latency under still-useful predecessor work while preserving one substantive authority owner.

Required sample evidence includes predictive due, actual successor observation, predecessor last useful boundary, successor first useful boundary, derived post-close gap, overlap/fence result, duplicate-side-effect result, and schedule-rollback result.

An early successor may fence/read/observe but cannot claim conflicting substantive authority while the predecessor is fresh. Promotion requires the documented safe-sample threshold and then a valid fixed 900-second utilization window. Schema: `schemas/predictive-prearm-canary.schema.json`.

## RELAY_VALIDATION.json

Machine-readable acceptance surface for the live relay experiment. Preserve canonical identity, never infer timing/overlap from missing evidence, and promote only when the documented pass rule is satisfied.

Schema: `schemas/relay-validation.schema.json`.

## EVENTS.jsonl

Each non-empty line follows `schemas/relay-event.schema.json`. Do not rewrite history merely to improve presentation; correct later with a new event when necessary.

## RUNS.jsonl

Each non-empty line follows `schemas/run-observation.schema.json`.

Every bounded execution turn should durably record actual `run_started_at`, actual `run_ended_at`, derived `duration_seconds`, and `turn_outcome: CONTINUE | COMPLETE | BLOCKED | PAUSED`, plus detailed classification/evidence fields as applicable.

`COMPLETE` is reserved for durable program terminal state. Missing timing values remain null rather than fabricated.
