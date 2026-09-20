# ADR-002 — Sliding cold-rescue horizon

Status: CANDIDATE; NOT ACTIVE
Date: 2026-09-21

## Problem

The long-run owner model prevents artificial quarter-boundary handoffs, but the current same-canonical cold rescue remains parked at the next 15-minute phase. Epoch 18 stopped producing meaningful durable progress at 01:25:08 and epoch 19 first resumed meaningful work at 01:33:11, producing a measured 483-second recovery gap. The recovery SLO is <=120 seconds at p95, so the quarter fallback is correct but insufficient.

## Candidate

Replace the fixed 15-minute cold-rescue horizon with a shorter *sliding deadline* while a healthy owner is alive. The current owner continually keeps one same-canonical wake a bounded horizon H in the future. If the owner disappears, the already-armed wake becomes the recovery opportunity. If the owner remains alive, it moves the deadline forward before it becomes due and continues useful work.

This is not a higher-frequency recurring automation and does not create extra automations. It reuses the same canonical automation and changes only its next effective due phase.

## Why not activate immediately

A shorter horizon creates a new failure mode: if the active owner fails to roll the deadline before it becomes due, same-canonical overlap is not known to occur. The due occurrence may be missed while the current invocation is still alive, potentially degrading to a much longer recurrence gap. Therefore a shorter horizon can improve crash recovery while making deadline-maintenance failure more dangerous.

The candidate must not be promoted merely because 483 seconds is bad.

## Experiment matrix

Test H = 10m, 5m, then 3m only if the prior stage is safe. For each horizon measure:

- owner-side scheduler mutations per useful minute;
- mutation/verification overhead;
- whether a due occurrence while the owner is alive is queued, skipped, or otherwise observable;
- recovery gap after a deliberately stale owner;
- missed-deadline failure severity;
- duplicate worker/substantive execution count;
- authority rollback count.

## Promotion rule

Promote a shorter horizon only if all are true:

1. no duplicate substantive execution;
2. no authority rollback;
3. deadline maintenance is reliable enough that expected recovery improves rather than merely shifting failure modes;
4. measured recovery latency materially beats the 483-second epoch18 baseline;
5. scheduler-mutation overhead does not materially reduce useful-work coverage;
6. independent event wake remains preferred for the <=120-second product SLO.

## Decision

Do not replace the quarter fallback yet. Treat a shorter sliding horizon as an empirical fallback-improvement experiment, not as a substitute for the independent event wake. The event-driven consumer remains the only current candidate that can plausibly satisfy <=120-second recovery without requiring the reasoning worker to continuously babysit its own deadline.
