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

Scheduler mechanism is replaceable. The active mechanism is one same-canonical hourly RRULE. Each valid wake rotates only BYMINUTE through the fixed quarter-hour cycle:

```text
:00 -> :15 -> :30 -> :45 -> :00 of the next hour
```

The successor MUST rearm and verify this same canonical before substantive work or handoff request. Do not create four separate quarter-hour automations and do not convert the canonical to one-shot.

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


## Fifteen-minute rolling worker protocol

The active relay is a rolling predecessor/successor pipeline.

- Each wake first re-arms the same canonical hourly RRULE to the next fixed quarter-hour slot and verifies it.
- Each worker then plans a substantive packet sized for approximately one 15-minute window.
- A newly awakened successor MUST secure its own following wake before requesting handoff from the predecessor.
- Handoff is request-driven, not clock-driven.
- After a durable handoff request, the predecessor stops admitting new substantive units, closes its current smallest safe unit, saves exact continuation state/evidence, and relinquishes authority promptly.
- The successor may not perform conflicting substantive work until the predecessor's durable handoff is committed; read-only reconstruction/preparation is allowed.
- After handoff, the successor claims the next authority epoch, plans its own 15-minute packet, and works.
- Finishing the planned packet early is not a reason to idle: pull another useful bounded unit if one exists.
- Missing/delayed successor means the predecessor continues useful work; the nominal 15-minute boundary does not terminate the predecessor.

Canonical order:

```text
WAKE
  -> REARM SAME RRULE FOR +15m AND VERIFY
  -> if predecessor active: HANDOFF_REQUEST
  -> predecessor: finish smallest safe unit + SAVE + RELEASE
  -> successor: CLAIM NEXT EPOCH
  -> PLAN ~15m USEFUL WORK PACKET
  -> WORK
  -> next successor wake repeats the cycle
```


## Utilization measurement and improvement

The active optimization target is an average observed useful-work span of at least 14 minutes per 15-minute turn.

A completed run must persist enough timestamps to distinguish work from dead time. The minimum derived fields are:
- observed_useful_span_seconds: last meaningful durable progress minus substantive_work_started_at;
- dead_tail_seconds: successor/handoff boundary minus last meaningful durable progress, when both timestamps are known;
- scheduler_or_handoff_overhead_seconds: known non-substantive startup/handoff overhead;
- measurement_valid: false when required boundaries are missing rather than inventing values.

Every completed valid turn is an experiment:
1. measure;
2. compare against 840 seconds;
3. classify the dominant under-utilization cause;
4. choose one concrete policy/process correction;
5. persist it for the next worker;
6. next worker applies it and retests.

The optimization target is reached only after at least 3 valid completed turns whose rolling mean observed_useful_span_seconds is >= 840. Until then the program remains CONTINUE unless a true BLOCKED_EXTERNAL condition is proven. A single good turn does not complete the experiment.


### Runtime-safe 14+1 cadence

The operational target is not to terminate at minute 14. It is to keep each worker productive for about 14 of the 15 minutes, reserving roughly the last minute as a runtime/handoff safety margin.

- 0-12m: normal substantive bounded units.
- 12-14m: do not begin units that are expensive to checkpoint; prefer short bounded units.
- ~14m onward: HANDOFF_READY. Keep working on tiny safe units and keep checkpoint state current.
- At successor handoff request: stop admitting work, close the smallest safe unit, persist exact next action/evidence, release authority immediately.
- If no successor request arrives, continue useful small units rather than idling.
- A worker must not intentionally run a monolithic 15-minute operation that cannot checkpoint; this is the runtime-timeout avoidance mechanism.
