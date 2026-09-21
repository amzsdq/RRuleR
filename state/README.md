# Durable State

## Files

- `CURRENT.json` — compact machine-readable projection of the current program/root job.
- `HANDOFF.json` — explicit predecessor/successor coordination state for the current handoff.
- `ACTIVITY.json` — durable operator-facing liveness heartbeat: armed/working/handoff/terminal state, active run identity, last progress, current unit, and next wake.
- `WORK_EVIDENCE.json` — strict forward-only accepted useful-work intervals; unknown time is never inferred.
- `SUCCESSOR_STARTUP.json` — prospective scheduler-due, invocation-observation, authority-claim, and first-useful boundaries for startup-loss attribution.
- `PREDICTIVE_PREARM_CANARY.json` — historical UTIL-EXP-018 canary result; do not mistake its failed sample for the active UTIL-EXP-019 startup experiment.
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

`tools/append_work_evidence.py` provides guarded append semantics. `tools/validate_work_evidence.py` audits the ledger/promotion windows. `tools/summarize_work_evidence.py` reports freshness/totals and bounded-run short-turn diagnostics without converting unknown time.

When the available connector surface cannot safely append the monolithic one-line ledger without rewriting unrelated history, an observed candidate may be persisted under `state/evidence-pending/`. Pending evidence is **not** P0-accepted evidence and must be ignored by promotion until validated and canonically appended. This preserves observed boundaries without falsely claiming acceptance.

## SUCCESSOR_STARTUP.json

This is the active prospective measurement surface for `UTIL-EXP-019`. Keep four boundaries separate: scheduled due, actual successor observation, nonconflicting authority claim, and first durable useful mutation. Missing boundaries remain unknown. Optimize the largest measured avoidable segment rather than attributing all cross-turn loss to scheduler timing or all loss to worker startup.

## PREDICTIVE_PREARM_CANARY.json

This preserves the `UTIL-EXP-018` result. Its first canary failed because predecessor-last-useful to successor-first-useful was 3514 seconds. It remains historical evidence and a rollback constraint, not the current experiment state. Any later guarded timing retry must be justified by new evidence such as `SUCCESSOR_STARTUP.json` and must preserve single substantive authority.

## RELAY_VALIDATION.json

Machine-readable acceptance surface for the live relay experiment. Preserve canonical identity, never infer timing/overlap from missing evidence, and promote only when the documented pass rule is satisfied.

Schema: `schemas/relay-validation.schema.json`.

## EVENTS.jsonl

Each non-empty line follows `schemas/relay-event.schema.json`. Do not rewrite history merely to improve presentation; correct later with a new event when necessary.

## RUNS.jsonl

Each non-empty line follows `schemas/run-observation.schema.json`.

Every bounded execution turn should durably record actual `run_started_at`, actual `run_ended_at`, derived `duration_seconds`, and `turn_outcome: CONTINUE | COMPLETE | BLOCKED | PAUSED`, plus detailed classification/evidence fields as applicable.

A normal `CONTINUE` turn has an 8-minute minimum floor. A `CONTINUE` run below 480 seconds is an exception and must include an allowlisted `short_turn_reason` plus non-empty `alternatives_checked`; otherwise it is a utilization-policy failure. `tools/summarize_work_evidence.py ... state/RUNS.jsonl` exposes this diagnostically, and the run-observation schema enforces the fields for new records.

`COMPLETE` is reserved for durable program terminal state. Missing timing values remain null rather than fabricated.
