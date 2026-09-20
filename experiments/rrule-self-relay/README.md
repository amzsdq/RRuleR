# Experiment: RRULE Self-Relay

## Objective

Verify that one recurring ChatGPT automation can preserve its canonical ID and recurring RRULE while rotating `BYMINUTE` to produce an effective 15-minute relay, with GitHub as durable state and high useful-work utilization.

For a fresh-session step-by-step reproduction procedure, see [REPRO_CHECKLIST.md](REPRO_CHECKLIST.md).

## Canonical automation

`6aaf8a993eb08191b8d0ab1d9662e4b2`

## Result

**PASS — reproduction bootstrap complete.**

The same canonical recurring automation successfully rotated RRULE phases across multiple scheduled executions, later executions reconstructed authoritative state from GitHub, substantive work continued from that durable state, and the control-plane validator remained coherent. `state/RELAY_VALIDATION.json` is the machine-readable acceptance record.

Exact predecessor/successor concurrency classification and precise handoff idle-gap measurement remain intentionally unclaimed because available durable evidence is insufficient to distinguish them without inference. They are performance-characterization follow-ups, not blocking reproduction criteria.

## Live validation ledger

### Bootstrap / predecessor run — 2026-09-20 KST

Observed sequence:

1. Same canonical re-enabled as recurring `RRULE:FREQ=HOURLY;BYMINUTE=30;BYSECOND=0`.
2. Substantive RRuleR bootstrap work began immediately.
3. Bootstrap/control/state/architecture/relay documents and CI validation were created.
4. Same canonical was updated `:30 -> :45` while preserving recurring RRULE semantics.
5. Next due was verified.
6. A premature clean-stop policy was identified as inconsistent with the utilization objective.
7. Policy was corrected: predecessor continues useful work until successor execution is actually observed; scheduled-time arrival, checkpoint creation, document completion, and milestone completion are not yield conditions.
8. Work continued after the correction: AGENTS/POLICY/ARCHITECTURE/relay guide hardened; schemas, operator runbook, event ledger, utilization metric, and expanded CI checks added.

### Scheduled successor observation — 2026-09-20 19:44 KST

Directly observed:

1. A scheduled automation execution began under the same canonical automation ID.
2. NEXT WAKE FIRST succeeded: the same recurring automation rotated `:45 -> :00`.
3. The successor read durable bootstrap/control/current-state material from GitHub.
4. It reconstructed the durable checkpoint without relying on predecessor chat memory.
5. It immediately continued substantive non-duplicative work by adding the durable execution model plus fenced-lease/checkpoint/effect-receipt schemas and expanding CI requirements.
6. Durable state advanced with a newer authority epoch and continuation phase.

This is direct evidence for **scheduled successor -> GitHub reconstruction -> substantive continuation**.

### Additional continuation — 2026-09-20 KST

Directly observed:

1. Subsequent scheduled executions rotated the same canonical recurring automation through additional quarter phases.
2. Canonical automation ID remained unchanged; the automation remained recurring and `exact_schedule` until terminal completion.
3. Runs reconstructed authority from durable GitHub state before substantive writes.
4. GitHub Actions control-plane validation continued to complete successfully; run `35506916073` succeeded on commit `ee83a1ae1839a5325541eb6f25dbd8df01303608` before terminal promotion.
5. This demonstrates continuation beyond a single cold handoff.

## Acceptance checklist

- [x] Public-safe durable repo exists.
- [x] Bootstrap and relay reproduction guide persisted.
- [x] Same canonical automation preserved.
- [x] Multiple recurring RRULE phase transitions observed.
- [x] Continuous-work/no-voluntary-idle policy made authoritative.
- [x] Machine-readable current-state and relay-event schemas exist.
- [x] CI validates required control-plane files and durable-state invariants.
- [x] Scheduled successor reads durable GitHub state and continues substantive work.
- [x] Additional continuation cycle confirms continuation survives beyond the first cold handoff.
- [x] All blocking `state/RELAY_VALIDATION.json` criteria are PASS or PASS_WITH_SCOPE.
- [ ] Overlap-or-serialization semantics precisely classified — non-blocking future characterization.
- [ ] Handoff idle gap precisely measured — non-blocking future characterization.

## Correctness boundary

Queued or concurrent predecessor/successor execution is not required for correctness. Durable GitHub reconstruction is the correctness path. Serialized execution is not a reason to voluntarily stop early: a predecessor keeps useful work moving until successor observation, a terminal condition, a proven external blocker, or platform-enforced termination.

## Failure classification

If phase self-update fails but the previous hourly RRULE is verified intact, record `DEGRADED_CONTINUATION` and the expected fallback wake. If no valid wake remains, record a continuation failure requiring external recovery.

## Utilization evidence

See `docs/UTILIZATION.md`. Precise utilization values must come from positive durable/platform evidence; unknown values remain unknown.
