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
11. **Useful-work utilization is a first-class operating objective.**
12. **Scheduled time is not a voluntary stop signal.**

## Authority

`state/CURRENT.json` identifies current owner and monotonic `authority_epoch`.

A stale run may read state but must not perform authoritative substantive writes after observing a newer epoch.

## Continuous work

After the next wake is verified:

- begin substantive work immediately;
- keep selecting useful admissible bounded work units while the root is non-terminal;
- do not stop at document, checkpoint, milestone, phase, or quarter boundaries;
- checkpoint frequently enough for recovery without treating checkpoint creation as a yield;
- only successor observation, terminal completion, or a proven external blocker authorizes normal relinquishment.

## Handoff

Preferred handoff:

```text
successor wake already armed
        ↓
predecessor continues useful work
        ↓
successor ACTUALLY observed
        ↓
predecessor stops starting new units
        ↓
finish current smallest safe work unit
        ↓
persist checkpoint + duration + evidence + exact next action
        ↓
handoff status / predecessor end
        ↓
successor reconstructs from GitHub and resumes
```

Scheduled quarter arrival without successor evidence is not a handoff trigger.

If same-canonical overlap is unsupported, correctness falls back to durable reconstruction, but the predecessor must not voluntarily introduce an idle period before platform-enforced termination.

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
