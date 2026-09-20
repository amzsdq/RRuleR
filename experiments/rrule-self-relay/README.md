# Experiment: RRULE Self-Relay

## Objective

Verify that one recurring ChatGPT automation can preserve its canonical ID and recurring RRULE while rotating `BYMINUTE` to produce an effective 15-minute relay, with GitHub as durable state and high useful-work utilization.

## Canonical automation

`6aaf8a993eb08191b8d0ab1d9662e4b2`

## RRuleR live validation ledger

### Bootstrap / predecessor run — 2026-09-20 KST

Observed sequence:

1. Same canonical re-enabled as recurring `RRULE:FREQ=HOURLY;BYMINUTE=30;BYSECOND=0`.
2. Substantive RRuleR bootstrap work began immediately.
3. Bootstrap/control/state/architecture/relay documents and CI validation were created.
4. Same canonical was updated `:30 -> :45` while preserving recurring RRULE semantics.
5. Next due was verified as `2026-09-20T19:45:00+09:00`.
6. A premature clean-stop policy was identified as inconsistent with the utilization objective.
7. Policy was corrected: predecessor now continues useful work until successor execution is **actually observed**; scheduled-time arrival, checkpoint creation, document completion, and milestone completion are not yield conditions.
8. Work continued after the correction: AGENTS/POLICY/ARCHITECTURE/relay guide hardened; schemas, operator runbook, event ledger, utilization metric, and expanded CI checks added.

### Current expected successor behavior

At the actual scheduled successor wake:

1. successor performs NEXT WAKE FIRST and rotates `:45 -> :00`;
2. successor reads `state/CURRENT.json`;
3. successor detects whether a predecessor handoff is already durable;
4. if predecessor is still active and overlap is possible, successor must not duplicate the active unit;
5. predecessor, once successor is actually observed, finishes its smallest safe current unit and persists handoff;
6. successor resumes from that handoff;
7. if same-canonical overlap is serialized by the platform, record the actual gap and resume from latest durable state rather than assuming overlap.

## Checklist

- [x] Public-safe durable repo exists.
- [x] Bootstrap and relay reproduction guide persisted.
- [x] Same canonical automation re-enabled as recurring RRULE.
- [x] First RRuleR-era recurring phase transition recorded (`:30 -> :45`).
- [x] Continuous-work/no-voluntary-idle policy made authoritative.
- [x] Machine-readable current-state and relay-event schemas exist.
- [x] CI validates required control-plane files and durable-state invariants.
- [ ] Second RRuleR-era phase transition recorded by scheduled successor (`:45 -> :00`).
- [ ] Scheduled successor reads `state/CURRENT.json` and continues substantive work.
- [ ] Successor/predecessor overlap-or-serialization semantics observed and recorded.
- [ ] At least one handoff continuation cycle completes without runtime-timeout loss.
- [ ] Handoff idle gap / successor wait is measured where observable.

## Correctness boundary

Queued or concurrent predecessor/successor execution is not required for correctness.

The relay must remain correct under serialized execution because durable GitHub state is authoritative. However, **serialized execution is not a reason to voluntarily stop early**. The predecessor keeps working until successor observation, a terminal condition, a proven external blocker, or platform-enforced termination.

## Failure classification

If phase self-update fails but the previous hourly RRULE is verified intact, record `DEGRADED_CONTINUATION` and the expected fallback wake. If no valid wake remains, record a continuation failure requiring external recovery.

## Utilization evidence

See `docs/UTILIZATION.md`.

Primary relay overhead to measure:

```text
predecessor last productive work
 -> predecessor handoff completion
 -> successor productive resume
```

Do not treat platform-wide outages or proven external blocking time as relay-caused idle.
