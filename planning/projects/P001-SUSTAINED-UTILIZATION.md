# P001 — Sustained Utilization & Continuous Execution

Status: **ACTIVE**  
Parent: [RRuleR Program](../PROGRAM.md)  
Primary dimensions: **P0-A turn worktime / sustained useful work** + **P0-B exact schedule rearm / continuation latency**

## Outcome

Turn RRuleR from a relay that merely wakes into a runtime that (A) keeps a normal nonterminal turn working for at least 10 minutes (600 observed elapsed seconds) unless a truthful early-exit exception applies and (B) closes by rearming the SAME enabled recurring MAIN to ACTUAL END + exactly 1 minute (60 seconds), with exact live verification and separately measured provider delay.

## Why this project exists

Two defects dominate the current project: premature/underfilled work inside a wake, and next-wake timing/rearm ambiguity after close. The project therefore optimizes measured useful wall-clock coverage **and** exact completion-relative continuation, not mere scheduler survival.

## Exit criteria

All must be satisfied:

- [ ] Three consecutive valid fixed 900-second windows each meet the active evidenced-useful-work target.
- [ ] Rolling mean meets the active P0 threshold.
- [ ] No accepted window relies on inferred/unknown time.
- [ ] Work-evidence capture remains current rather than lagging many authority epochs behind.
- [x] A low-utilization/structurally impossible sample produces a durable cause classification and a concrete next correction.
- [ ] P0-A becomes a regression gate so later projects cannot silently destroy sustained turn worktime/useful coverage.
- [ ] P0-B proves at least three consecutive normal closes with SAME MAIN live-verified at ACTUAL END + exactly 1 minute (60 seconds), consistent durable due projection, and separately measured provider delivery/startup delay; retain it as a regression gate.

## Work specs

| Work spec | Status | Acceptance progress | Purpose |
|---|---|---:|---|
| [WS-P001-001 — Strategic Planning Spine](../work-specs/WS-P001-001-STRATEGIC-PLANNING-SPINE.md) | **DONE** | 5 / 5 | Prevent local optimization by binding work to program/project/spec/NOW |
| [WS-P001-002 — Sustained Turn Utilization](../work-specs/WS-P001-002-SUSTAINED-TURN-UTILIZATION.md) | **ACTIVE** | 4 / 6 | Raise real useful-work occupancy and repair evidence freshness |
| WS-P001-003 — P0 Acceptance & Regression SLO | BACKLOG | 0 / TBD | Prove sustained P0 and preserve it while advancing the roadmap |

Project progress: **1 / 3 committed work specs DONE**; active spec **4 / 6 acceptance items satisfied**.

## Current measured bottleneck

In-turn execution has improved, but the two current top-priority questions are now explicit: **P0-A:** does each normal nonterminal wake actually sustain at least 10 minutes (600 observed elapsed seconds) of chained authorized work with artifact-backed evidence? **P0-B:** does each normal close actually mutate and live-verify the SAME recurring MAIN at ACTUAL END + exactly 1 minute (60 seconds), rather than leaving a provisional or natural hourly occurrence? `STARTUP-006` also showed that provider invocation/bootstrap latency must be measured separately from the local rearm offset.

## Current decision

Keep a normal work envelope of 10 to about 12 minutes (600 to about 720 observed elapsed seconds) and require exact ACTUAL END + 1 minute (60 seconds) normal continuation on the SAME recurring MAIN. Preserve forward-only `BOOT_STARTED` and `REARM_VERIFIED` boundaries; classify missing startup evidence without inventing process death. Do not widen product scope until P0-A and P0-B are stably demonstrated. The natural hourly recurrence is cold fallback only, never the intended normal next wake.

## Operator-locked active focus

Until both gates pass, select work by expected impact on these two outcomes only:

- **P0-A:** eliminate premature turn closure and raise artifact-backed useful work within each normal wake.
- **P0-B:** eliminate schedule-unit ambiguity, stale provisional close, and incorrect next-wake timing; prove exact SAME MAIN ACTUAL END + 1 minute (60 seconds) rearm and distinguish provider delivery/startup delay from local schedule calculation.

Broader planner, adapter, orchestration, onboarding, and product-UX work is deferred unless it directly removes a measured blocker for P0-A/P0-B or preserves a required invariant.
