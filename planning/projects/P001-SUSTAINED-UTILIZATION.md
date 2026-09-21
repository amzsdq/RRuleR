# P001 — Sustained Utilization & Continuous Execution

Status: **ACTIVE**  
Parent: [RRuleR Program](../PROGRAM.md)  
Primary dimension: **Useful-work utilization (P0)**

## Outcome

Turn RRuleR from a relay that reliably wakes into a runtime that uses most eligible wall-clock time for substantive progress, while preserving correctness and cold-rescue safety.

## Why this project exists

Current evidence shows continuation survival is much stronger than actual wake utilization. The system can remain alive while doing too little useful work per wake. That makes local control-plane hardening insufficient as a primary strategy.

## Exit criteria

All must be satisfied:

- [ ] Three consecutive valid fixed 900-second windows each meet the active evidenced-useful-work target.
- [ ] Rolling mean meets the active P0 threshold.
- [ ] No accepted window relies on inferred/unknown time.
- [ ] Work-evidence capture remains current rather than lagging many authority epochs behind.
- [ ] A low-utilization turn produces a durable cause classification and a concrete next correction.
- [ ] P0 becomes a regression SLO so later projects cannot silently destroy utilization.

## Work specs

| Work spec | Status | Acceptance progress | Purpose |
|---|---|---:|---|
| [WS-P001-001 — Strategic Planning Spine](../work-specs/WS-P001-001-STRATEGIC-PLANNING-SPINE.md) | **DONE** | 5 / 5 | Prevent local optimization by binding work to program/project/spec/NOW |
| [WS-P001-002 — Sustained Turn Utilization](../work-specs/WS-P001-002-SUSTAINED-TURN-UTILIZATION.md) | **ACTIVE** | 1 / 6 | Raise real useful-work occupancy and repair evidence freshness |
| WS-P001-003 — P0 Acceptance & Regression SLO | BACKLOG | 0 / TBD | Prove sustained P0 and preserve it while advancing the roadmap |

Project progress: **1 / 3 committed work specs DONE**; active spec **1 / 6 acceptance items satisfied**.

## Current decision

Do not continue control-plane simplification merely because it is nearby. It is subordinate work and should be resumed only when it has higher expected effect on P001 than direct utilization/evidence work.

The active work spec is **WS-P001-002**. Evidence freshness has been repaired for the resumed epoch; next priority is a trustworthy current baseline and measured cause ranking.
