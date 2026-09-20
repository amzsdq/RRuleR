# RRuleR Control Policy

## Architectural axioms

1. **Persistence belongs to GitHub.**
2. **Intelligence belongs to disposable ChatGPT sessions.**
3. **No session is authoritative; durable state is.**
4. **Automation is a wake mechanism, not a state store.**
5. **Delivery is not work completion.**
6. **Checkpoint before authoritative advancement.**
7. **At-least-once delivery is acceptable; duplicate substantive execution is not.**
8. **Ambiguous irreversible side effects reconcile before replay.**
9. **Authority must be explicit and fenced.**
10. **Completion requires evidence, not worker prose.**

## Authority

`state/CURRENT.json` identifies current owner and monotonic `authority_epoch`.

A stale run may read state but must not perform authoritative substantive writes after observing a newer epoch.

## Handoff

Preferred handoff:

```text
successor wake already armed
        ↓
predecessor continues useful work
        ↓
handoff boundary
        ↓
finish current smallest safe work unit
        ↓
persist checkpoint + duration + exact next action
        ↓
clean stop / concise STATUS
        ↓
successor reconstructs from GitHub
```

Do not force a phase or milestone to end merely because a relay turn boundary was reached.

## Scheduler policy

Scheduler mechanism is replaceable. The currently reproduced mechanism is `docs/RELAY_RRULE_SELF_UPDATE.md`.

Architectural invariant:

> A live non-terminal job that requires continuation must have a valid recoverable continuation path.

## Failure semantics

- Fast self-update failure while the prior recurring RRULE remains verified alive is `DEGRADED_CONTINUATION`, not immediate death.
- The surviving hourly recurrence may provide a low-frequency self-rescue opportunity.
- Disabled/deleted/missing automation is not rescued by that fallback.
- Repeated blind retry without a new hypothesis or reconciliation evidence is forbidden.

## Public-safe persistence

RRuleR must remain safe to expose publicly. Never persist credentials, cookies, private files, private message content, or private-repository material.
