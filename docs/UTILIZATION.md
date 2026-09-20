# Relay Utilization Measurement

## Goal

RRuleR optimizes **useful-work utilization subject to correctness invariants**.

A relay that is correct but spends large portions of its intended active window idle is operationally poor. A relay that is busy but duplicates work or performs stale-authority writes is also poor.

## Primary metric

For a root job observation window:

```text
useful_work_utilization =
  productive_substantive_seconds
  / eligible_active_window_seconds
```

Where `eligible_active_window_seconds` excludes:

- explicit user-requested pause;
- proven external blocking time;
- platform-wide outage time when no execution path is available.

It includes relay-caused idle time such as:

- voluntary predecessor early stop;
- avoidable handoff gap;
- avoidable scheduler gap;
- successor waiting caused by stale or insufficient checkpoint state.

## Secondary metrics

Record where observable:

- `run_wall_seconds`
- `productive_substantive_seconds`
- `checkpoint_seconds`
- `handoff_seconds`
- `relay_idle_gap_seconds`
- `successor_wait_seconds`
- `external_blocked_seconds`
- `platform_unavailable_seconds`
- `duplicate_work_seconds` — target is zero
- `recovery_seconds`
- `useful_work_utilization`

## Classification

### Productive

Reasoning, research, implementation, validation, reconciliation, or durable documentation that advances the active root goal.

### Necessary overhead

Checkpointing, authority verification, next-wake verification, and bounded handoff work required for correctness.

### Relay-caused idle

The root is runnable but no executor performs useful work because of relay design or voluntary early stop.

### External blocked

No admissible useful work can proceed because a proven dependency outside the relay is unavailable.

### Platform unavailable

Execution is impossible due to platform-level unavailability. Track separately; do not attribute it to relay design.

## Operating rule

The relay must not reduce utilization merely to create aesthetically clean 15-minute turns.

The quarter-hour schedule is a **wake cadence**, not a work-duration quota.

If the predecessor is still active when the scheduled successor boundary arrives:

- predecessor keeps working until successor execution is actually observed;
- scheduled-time arrival alone does not trigger voluntary stop;
- once successor is observed, predecessor finishes the current smallest safe unit and hands off;
- if overlap is unsupported, record the platform behavior and minimize the resulting idle gap without relying on unsafe concurrency.

## Correctness constraints

Utilization optimization may never override:

- current authority/fencing;
- duplicate-execution prevention;
- idempotency/reconciliation requirements;
- public-safety rules;
- terminal acceptance gates.

## Current target

During bootstrap, collect enough live observations to establish an empirical normal-range estimate. Do not invent a target percentage before measurements exist.

The first useful baseline is the distribution of:

`predecessor productive end -> successor productive start`

across multiple handoffs.
