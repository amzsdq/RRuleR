# P0 runtime focus — epoch 82 — 2026-09-22

Run: `RUN-UTIL-20260922-030015`  
Authority epoch: 82  
Observed wake reference: 2026-09-22 03:00:15 KST

## Operator priority

The immediate program priority is now explicitly two-part:

1. P0-A: normal nonterminal turns sustain at least **10 minutes (600 observed elapsed seconds)** of real chained authorized work unless a truthful non-CONTINUE exception applies.
2. P0-B: normal close mutates the **SAME enabled recurring MAIN** to **ACTUAL END + exactly 1 minute (60 seconds)**, live-verifies exact `DTSTART`, and persists the same due. Provider delivery/startup latency is measured separately.

## Product Runtime Direction review

The operator-supplied `RRuleR_Product_Runtime_Direction.md` was reviewed before this run. The following ideas are adopted because they directly improve the two P0 outcomes without expanding feature breadth:

- rules/mechanisms are instruments, not goals;
- recursive development must be evidence-grounded and compare before/after against stable objectives;
- experimental changes stay separate from stable runtime until a promotion gate passes;
- prior art / proven mechanisms are preferred over unnecessary invention;
- internal telemetry remains structured and exact while final distribution may render concise natural-language turn reports.

Deferred until P0-A/P0-B are proven: broad planner, profile, storage-adapter, onboarding, and general product-UX expansion.

## Durable changes in this unit

- `state/CURRENT.json`: epoch 82 ownership and explicit two-part P0.
- `state/ACTIVITY.json`: epoch 82 WORKING projection.
- `state/TURN_PLAN.json`: bounded objective constrained to P0-A/P0-B.
- `planning/work-specs/WS-P001-002-SUSTAINED-TURN-UTILIZATION.md`: explicit unit-safe P0 decision procedure and final-distribution reporting note.

## Timing evidence

This bounded unit began at the first substantive durable change at approximately 03:01:05 KST and completed at the final work-spec commit boundary at approximately 03:04:20 KST. Exact useful-work promotion remains subject to the repository evidence validator; this document does not convert elapsed time into accepted useful time by prose alone.
