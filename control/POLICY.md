# RRuleR Control Policy

## Authority surfaces

- `control/POLICY.md` — human-readable architectural policy.
- `control/relay-policy.v1.json` — machine-readable relay policy for scheduler/utilization/handoff behavior.
- `state/CURRENT.json` — current program/root projection and exact continuation state.
- `state/ACTIVITY.json` — current observable run/activity heartbeat.

If prose and machine-readable relay fields disagree, fail closed and reconcile them before relying on the disputed behavior.

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
13. **Root completion is not automatically program completion.**
14. **An active program must not voluntarily create an idle gap when useful admissible work exists.**

## Authority

`state/CURRENT.json` identifies current owner and monotonic `authority_epoch`.

A stale run may read state but must not perform authoritative substantive writes after observing a newer epoch.

## Continuous work

After the next wake is verified:

- mark durable activity WORKING;
- begin substantive work immediately;
- keep selecting useful admissible bounded work units while the program is non-terminal;
- do not stop at document, checkpoint, milestone, phase, root, or schedule boundaries;
- checkpoint frequently enough for recovery without treating checkpoint creation as a yield;
- on root completion, persist root terminal evidence, select the next materially useful root if one exists, persist it, and continue;
- never generate busywork solely to satisfy utilization;
- only successor observation, verified program completion, explicit operator stop, a proven external blocker with internal alternatives exhausted, or platform-enforced termination authorizes normal relinquishment.

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
persist checkpoint + activity + duration + evidence + exact next action
        ↓
handoff status / predecessor end
        ↓
successor reconstructs from GitHub and resumes
```

Scheduled recurrence arrival without successor evidence is not a handoff trigger.

If same-canonical overlap is unsupported, correctness falls back to durable reconstruction, but the predecessor must not voluntarily introduce an idle period before platform-enforced termination.

## Scheduler policy

Scheduler mechanism is replaceable. The active mechanism is a same-canonical hourly RRULE whose BYMINUTE is self-shifted on every wake. The shift MUST be computed from the actual wake/start time, not from the stale prior phase. Set target_due to the next whole-minute boundary at least 15 minutes after actual wake/start, then set DTSTART=target_due and RRULE:FREQ=HOURLY;BYMINUTE=target_due.minute;BYSECOND=0. This avoids the failure mode where a delayed wake re-arms only seconds before the nominal next phase, misses that occurrence, and then sleeps for nearly an hour.

Architectural invariant:

> A live non-terminal program that requires continuation must have a valid recoverable continuation path.

## Activity evidence and UI

The ChatGPT composer/stop-button state is not authoritative durable state, but it is a useful operator-facing liveness signal.

- Stop button: usually means the foreground turn is still generating.
- Send button / idle composer: means that foreground turn ended, but does not rule out a separate scheduled run.
- To align behavior with the operator's practical observation, an active predecessor does not voluntarily send its normal final response while it still owns work and no successor has been observed.
- `state/ACTIVITY.json` is the durable corroborating signal. Idle UI plus stale activity and no successor evidence is a utilization incident.

## Failure semantics

- Recurrence phase-update failure while a prior valid RRULE remains alive is `DEGRADED_CONTINUATION`, not immediate death.
- A surviving recurrence may provide a slower recovery opportunity.
- Disabled/deleted/missing automation is not rescued by that fallback.
- Repeated blind retry without a new hypothesis or reconciliation evidence is forbidden.

## Public-safe persistence

RRuleR must remain safe to expose publicly. Never persist credentials, cookies, private files, private message content, private-repository material, or personal data.

## Hard no-self-termination invariant

A non-terminal owner MUST NOT voluntarily end its turn.

- If program state is not `PROGRAM_COMPLETE` or `BLOCKED_EXTERNAL`, emitting a normal final response is forbidden unless a successor has actually been observed and the durable handoff has been committed.
- `CONTINUE`, `WORKING`, `DEGRADED_CONTINUATION`, checkpoint completion, CI pending/success, document completion, root completion, or "nothing immediately obvious" are NOT permission to end.
- After every bounded unit, re-read durable state, select the next useful admissible unit, and execute it in the SAME turn.
- If no next unit is obvious, the next unit is to inspect durable state/evidence for the highest-value unresolved invariant or validation gap; this is not a reason to idle.
- Only `PROGRAM_COMPLETE`, proven `BLOCKED_EXTERNAL`, committed successor handoff, explicit operator stop, or platform-enforced termination may end an active turn.
