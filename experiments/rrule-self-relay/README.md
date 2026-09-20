# Experiment: RRULE Self-Relay

## Objective

Verify that one recurring ChatGPT automation can preserve its canonical ID and recurring RRULE while rotating `BYMINUTE` to produce an effective 15-minute relay, with GitHub as durable state and high useful-work utilization.

For a fresh-session step-by-step reproduction procedure, see [REPRO_CHECKLIST.md](REPRO_CHECKLIST.md).

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
7. Policy was corrected: predecessor continues useful work until successor execution is actually observed; scheduled-time arrival, checkpoint creation, document completion, and milestone completion are not yield conditions.
8. Work continued after the correction: AGENTS/POLICY/ARCHITECTURE/relay guide hardened; schemas, operator runbook, event ledger, utilization metric, and expanded CI checks added.

### Scheduled successor observation — 2026-09-20 19:44:39 KST

Directly observed:

1. The scheduled automation execution actually began under the same canonical automation ID.
2. NEXT WAKE FIRST succeeded: the same recurring automation rotated `:45 -> :00` with next due `20:00 KST`.
3. The successor then read `AGENTS.md`, `control/POLICY.md`, `state/CURRENT.json`, machine relay policy, handoff state, and reproduction guide from GitHub.
4. It reconstructed `CP-BOOTSTRAP-004` without relying on predecessor chat memory.
5. It immediately continued substantive non-duplicative work by adding the durable execution model plus fenced-lease/checkpoint/effect-receipt schemas and expanding CI requirements.
6. Durable state advanced to `CP-BOOTSTRAP-005`, authority epoch 2, with the next scheduled phase at `:00`.

This is direct evidence for **scheduled successor -> GitHub reconstruction -> substantive continuation**.

### Third phase continuation — 2026-09-20 20:02 KST

Directly observed:

1. A subsequent scheduled execution began and NEXT WAKE FIRST rotated the same canonical recurring automation `:00 -> :15`.
2. Canonical automation ID remained `6aaf8a993eb08191b8d0ab1d9662e4b2`; the automation remained enabled, recurring, and `exact_schedule`.
3. The run reconstructed authority from `AGENTS.md`, `control/POLICY.md`, `control/relay-policy.v1.json`, and `state/CURRENT.json` before substantive writes.
4. The latest GitHub Actions validation run for the control plane, run `35506033120`, completed `success` against commit `85315fb98b4d2b06b8ed15e8e138d7230b9c39c0`.
5. This supplies an additional live continuation cycle after the first scheduled cold continuation, reducing the risk that the observed relay was a one-cycle artifact.

### Overlap / serialization finding

Scheduled successor execution and durable cold continuation are proven. Exact predecessor/successor concurrency semantics must be classified only from durable or directly observable evidence; correctness does not depend on concurrency. If executions serialize, GitHub reconstruction remains the correctness path. If overlap is observed, authority fencing and active-unit ownership still prevent duplicate substantive work.

## Checklist

- [x] Public-safe durable repo exists.
- [x] Bootstrap and relay reproduction guide persisted.
- [x] Same canonical automation re-enabled as recurring RRULE.
- [x] First RRuleR-era recurring phase transition recorded (`:30 -> :45`).
- [x] Continuous-work/no-voluntary-idle policy made authoritative.
- [x] Machine-readable current-state and relay-event schemas exist.
- [x] CI validates required control-plane files and durable-state invariants.
- [x] Second RRuleR-era phase transition recorded by scheduled successor (`:45 -> :00`).
- [x] Scheduled successor reads durable GitHub state and continues substantive work.
- [x] Third phase transition recorded by later scheduled continuation (`:00 -> :15`).
- [x] At least one additional continuation cycle confirms continuation survives beyond the first cold handoff.
- [ ] Successor/predecessor overlap-or-serialization semantics observed sufficiently to classify platform behavior.
- [ ] Handoff idle gap / successor wait is measured where observable.

## Correctness boundary

Queued or concurrent predecessor/successor execution is not required for correctness.

The relay must remain correct under serialized execution because durable GitHub state is authoritative. However, serialized execution is not a reason to voluntarily stop early. The predecessor keeps working until successor observation, a terminal condition, a proven external blocker, or platform-enforced termination.

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
