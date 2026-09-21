# P001 — Sustained Utilization & Continuous Execution

Status: **ACTIVE**  
Parent: [RRuleR Program](../PROGRAM.md)  
Primary dimension: **Useful-work utilization (P0)**

## Outcome

Turn RRuleR from a relay that reliably wakes into a runtime that uses most eligible wall-clock time for substantive progress, while preserving correctness and cold-rescue safety.

## Why this project exists

Continuation survival is much stronger than actual useful-work occupancy. The project therefore optimizes measured useful wall-clock coverage, not mere scheduler survival.

## Exit criteria

All must be satisfied:

- [ ] Three consecutive valid fixed 900-second windows each meet the active evidenced-useful-work target.
- [ ] Rolling mean meets the active P0 threshold.
- [ ] No accepted window relies on inferred/unknown time.
- [ ] Work-evidence capture remains current rather than lagging many authority epochs behind.
- [x] A low-utilization/structurally impossible sample produces a durable cause classification and a concrete next correction.
- [ ] P0 becomes a regression SLO so later projects cannot silently destroy utilization.

## Work specs

| Work spec | Status | Acceptance progress | Purpose |
|---|---|---:|---|
| [WS-P001-001 — Strategic Planning Spine](../work-specs/WS-P001-001-STRATEGIC-PLANNING-SPINE.md) | **DONE** | 5 / 5 | Prevent local optimization by binding work to program/project/spec/NOW |
| [WS-P001-002 — Sustained Turn Utilization](../work-specs/WS-P001-002-SUSTAINED-TURN-UTILIZATION.md) | **ACTIVE** | 4 / 6 | Raise real useful-work occupancy and repair evidence freshness |
| WS-P001-003 — P0 Acceptance & Regression SLO | BACKLOG | 0 / TBD | Prove sustained P0 and preserve it while advancing the roadmap |

Project progress: **1 / 3 committed work specs DONE**; active spec **4 / 6 acceptance items satisfied**.

## Current measured bottleneck

In-turn execution now sustains bounded work, but `STARTUP-006` exposed the dominant availability hole: the exact END+60 schedule invoked 73 seconds after due yet produced no durable bootstrap acknowledgement, provisional rearm, authority claim, useful work, or next self-rearm. The next hourly occurrence recovered the relay. Normal scheduling and pre-bootstrap recovery are therefore separate problems.

## Current decision

Keep 10-12 minute work-unit chaining and exact END+60 normal continuation. Add forward-only `BOOT_STARTED` and `REARM_VERIFIED` boundaries and classify `STARTUP_ACK_MISSING` without inferring process death. Detection is not recovery: the fast-path candidate remains a guarded GitHub PR event consumer, but it must stay inactive until the consumer is provisioned, its write probe passes, and one outstanding generation can be claimed safely. Hourly same-canonical RRULE remains the actual fallback meanwhile.
