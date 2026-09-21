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

Epoch 59 demonstrated materially improved in-turn execution: 557 strict useful seconds over 626 wall seconds. Epoch 60 then exposed a higher-level constraint: a 600-second work turn followed by a nominal 60-second post-close continuation gap has an idealized steady-state ceiling of 90.91%, below the P0 requirement of 93.33% even before scheduler jitter/startup overhead.

A prior production sample observed about 64 seconds of scheduler delivery delay after the due boundary. Merely shortening a post-close offset cannot reliably fit the <=42.9-second average non-useful budget for a 600-second turn.

## Current decision

The highest-effect next correction is `UTIL-EXP-018`, a guarded **predictive same-canonical successor prearm** canary. It attempts to overlap scheduler delivery latency with the predecessor's final useful-work period while preserving exactly one substantive authority owner.

Do not broaden into generic control cleanup. Do not weaken the P0 target to make the current cadence pass. Preserve the 780-second cold-rescue horizon; measure the normal handoff path independently.
