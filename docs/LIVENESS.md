# Durable Liveness and Operator Visibility

## Purpose

RRuleR needs a liveness signal that survives disposable ChatGPT sessions and does not depend on inference from the composer UI.

The authoritative activity projection is `state/ACTIVITY.json`; the machine-readable classification policy is `control/liveness-policy.v1.json`.

## Signals

A healthy active run has all of the following:

- the program is non-terminal;
- `ACTIVITY.status` is `WORKING`;
- `active_run_id` is present;
- `ACTIVITY.authority_epoch` equals `CURRENT.authority_epoch`;
- `last_progress_at` is fresh;
- a continuation wake is recorded.

The foreground ChatGPT stop/send button is useful operator evidence, but it is not durable authority. A send button proves the foreground turn ended; it does not prove a scheduled run is absent. Conversely, a stale durable WORKING record must not be treated as proof that useful work is still happening.

## Freshness classes

The initial policy uses conservative operational thresholds:

- target refresh: 5 minutes after meaningful progress when practical;
- `SUSPECT`: no fresh progress for 10 minutes while claiming WORKING;
- `OVERDUE`: no fresh progress for 20 minutes while claiming WORKING.

These are detection thresholds, not work-duration quotas. Long substantive units should still checkpoint or refresh durable activity when practical.

## Utilization gap

Classify `UTILIZATION_GAP` when the program is non-terminal, no fresh fenced WORKING evidence exists, and no durable successor observation explains the transition.

Idle foreground UI plus stale durable activity is therefore actionable evidence. Idle UI plus fresh successor WORKING evidence is not a gap.

## Recovery

On `SUSPECT`, reconcile owner, authority epoch, current unit, and recurrence before replaying work.

On `OVERDUE`, persist the gap and restore a valid continuation path. Never use liveness recovery as permission for blind duplicate substantive execution.

## Why epoch fencing matters

A stale predecessor can remain alive after a successor acquires authority. Without an epoch on the activity heartbeat, the predecessor could refresh a misleading WORKING record after it has lost authority. `ACTIVITY.authority_epoch == CURRENT.authority_epoch` makes that condition mechanically detectable.
