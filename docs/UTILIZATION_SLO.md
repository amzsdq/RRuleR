# RRuleR useful-work utilization SLO

Status: ACTIVE MEASUREMENT DEFINITION
Date: 2026-09-21

## Why the metric must be continuous-time

The real product goal is high **actual useful-work duty cycle**, not compliance with arbitrary quarter-hour boundaries.

`>=840 useful seconds per 900 seconds` corresponds to **>=93.33% useful-work coverage**. A fixed per-turn test is useful for diagnosis, but it can misattribute scheduler delay when predecessor/successor work overlaps a boundary. Conversely, endpoint span can falsely claim utilization across dead gaps.

Therefore RRuleR should optimize a continuous-time coverage SLO and keep per-turn 840/900 as a diagnostic acceptance proxy.

## Primary SLO

Over an observation horizon with trustworthy interval evidence:

`useful_work_coverage / observation_horizon >= 0.9333`

Additional guard:

- unexplained no-progress / no-worker gap should not exceed 120 seconds in a passing high-utilization interval.

Recommended horizons:

- development gate: rolling 15 minutes;
- stability gate: rolling 60 minutes;
- production evidence: multi-hour and overnight windows.

## What counts

Count only intervals supported by substantive execution evidence. Do not count:

- scheduler wait;
- unexplained silence between sparse timestamps;
- heartbeat-only writes;
- duplicate/replayed work;
- blocked approval time;
- coordination that produces no material progress unless coordination itself is the necessary work product.

Useful overlap by two workers counts once for wall-clock utilization, although parallel throughput may be tracked separately.

## Relationship to 840/900

`840 / 900 = 0.9333...`

The old target remains valuable because three consecutive 840-second-equivalent windows are an easy local proof. It is not the ultimate definition of utilization.

Example: if a successor wakes 70 seconds late but the predecessor continues useful work across that boundary, the system may still have ~100% wall-clock useful coverage. A fixed boundary-start metric would incorrectly penalize the scheduler despite no actual idle time.

Conversely, if the predecessor died before the boundary, that same 70-second delivery delay is real dead time and must reduce coverage.

## Engineering consequence

The control plane must reconstruct a union of evidenced useful-work intervals across owners and generations. The next measurement upgrade should therefore persist interval boundaries, not only `started_at` / `last_progress_at` endpoints.

The wake architecture should be judged by reduction in uncovered wall-clock time:

1. worker event chain — fastest potential handoff;
2. independent 5-minute Actions pulse — rescue path;
3. quarter-shift schedule — slow independent fallback.

This aligns the metric with the user's actual goal: a competitive agent runtime that spends nearly all available wall-clock time doing useful work.
