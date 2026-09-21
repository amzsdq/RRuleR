# Relay Utilization Measurement

## Goal

RRuleR optimizes evidenced useful-work coverage subject to correctness invariants. A correct relay that voluntarily ends a runnable normal nonterminal `CONTINUE` turn before the current minimum is operationally defective.

Two time scales must remain separate:

- **bounded execution turn:** normal nonterminal `CONTINUE` has a 600-second voluntary hard floor and ~720-second soft ceiling;
- **P0 acceptance window:** 900 seconds with >=840 seconds of evidenced useful coverage, evaluated independently of the bounded-turn duration.

The 600-second turn is not the 840/900 acceptance threshold.

## Primary measurement

Useful time is accepted only from observed artifact-backed boundaries. Elapsed START-to-END is not automatically useful work.

`useful_work_utilization = evidenced_productive_seconds / eligible_active_window_seconds`

Eligible time excludes explicit operator pause, proven external blocking, and platform-wide unavailability. It includes voluntary early stop, avoidable continuation gaps, and scheduler/startup loss caused by the relay design.

Missing boundaries remain unknown. Do not infer hidden work from commits, schedule times, or silence.

## Current continuation topology

The authoritative normal scheduler is the current clean SAME MAIN recurring hourly RRULE. The current MAIN self-shifts its DTSTART to exact observed END+60 for the fast continuation path while preserving recurrence. The same recurring RRULE is the built-in cold fallback if a shifted wake is lost. Watchdog is disabled break-glass standby and is not part of normal continuation.

Retired custom-recurring and prior MAIN canonicals are historical only and must not be reactivated.

Expected due time and actual invocation/BOOT_STARTED must be recorded separately. Scheduler/provider delivery latency is not worker useful time and must not be hidden inside turn-duration claims.

## Fresh-policy synchronization

Every wake reads fresh `control/ACTIVE_CONTROLS.json` and the artifacts it currently marks mandatory before substantive work. Prior-wake cached policy cannot override fresh durable controls. Reservation/bootstrap text is a survival kernel; dynamic policy belongs in fresh GitHub durable state except explicit operator and canonical-safety invariants.

## 600-second normal CONTINUE hard floor

For a normal nonterminal `CONTINUE` turn:

1. 600 observed elapsed seconds is the minimum voluntary turn duration, not merely a target.
2. Before 600 seconds, when a bounded unit completes, immediately select the next clear low-risk checkpointable authorized unit.
3. If the obvious unit is too large, decompose it and execute a smaller safe slice.
4. If the primary unit is waiting on CI or external evidence, select an independent fallback/residual authorized unit.
5. CI pending, packet/substep/checkpoint completion, secured continuation, or `nothing obvious` do not authorize voluntary pre-600 close.
6. Earlier end is reserved for explicit operator STOP/PAUSE, durable program terminal state, a genuine BLOCKED/fail-closed authority or safety condition with no safe authorized work, or platform-enforced termination. Record the corresponding status/reason rather than disguising it as a normal CONTINUE close.
7. At or after 600 seconds, stop starting new large units and finish only the smallest safe in-flight unit. ~720 seconds is the normal soft ceiling.
8. Never pad, sleep, fabricate timestamps, or invent busywork to manufacture duration.

Historical runs recorded before adoption of this hard floor remain historical evidence and are not retroactively rewritten.

## Normal close contract

A normal `STATUS=CONTINUE` close requires:

1. latest useful checkpoint persisted;
2. actual END observed;
3. THIS SAME MAIN mutated to exact `END+60s` while preserving recurring schedule and `is_enabled=true`;
4. live metadata re-read proving same canonical, enabled state, recurrence, and exact DTSTART;
5. the same verified fast due persisted coherently to CURRENT/ACTIVITY/HANDOFF;
6. non-WORKING close projection validated;
7. turn status/evidence persisted from actual observed boundaries.

A long provisional crash-insurance due cannot satisfy normal close. If exact fast rearm fails, retry once when safe. Preserve an older verified recurring fallback if available and classify degraded continuation; do not create a replacement MAIN merely to continue.

## P0 acceptance measurement

P0 is evaluated on fixed 900-second windows. A valid accepted window requires >=840 seconds of evidenced useful coverage and no unexplained internal progress gap above the active threshold. Current pass logic requires at least three valid completed windows and the rolling mean of selected valid windows to meet the 840-second target.

This target is intentionally stricter than the bounded-turn minimum. With 600-second turns, cross-turn scheduler/startup/close losses must be measured explicitly rather than hidden by treating elapsed time as productive.

## Useful-work evidence

Productive evidence may include materially new implementation, validation, reconciliation, research, design, or durable documentation that advances the active work spec. Scheduler mutation, heartbeat-only state, waiting, timestamp-only changes, duplicate checkpoint prose, and CI polling without a new result do not independently prove useful work.

Evidence rules:

- observed boundaries only;
- forward-only capture;
- unknown time is not useful time;
- materially new artifact/test/design evidence is required for accepted useful-work records;
- known waiting/idle intervals are not counted as productive coverage;
- no authority rollback or conflicting duplicate execution may contaminate the interval.

## Scheduler and startup measurement

For each continuation generation, preserve distinct observations where available:

- scheduled due;
- actual invocation observation;
- `BOOT_STARTED`;
- provisional `REARM_VERIFIED`;
- authority claim;
- first durable useful mutation;
- predecessor last useful boundary;
- actual END;
- verified next fast due.

Provider delivery delay and post-invocation startup delay are different failure classes and must not be merged.

## Under-target diagnosis

When a valid sample/window misses the target, classify the dominant measured cause before changing policy. Typical classes include:

- early voluntary end;
- packet too small;
- scheduler/provider delivery gap;
- startup/authority delay;
- handoff/close delay;
- waiting on tool or CI;
- recovery/fencing overhead;
- unknown evidence gap.

Choose the next corrective experiment from observed evidence. Repeating a failed intervention without new evidence is forbidden.

## Correctness constraints

Utilization optimization never overrides authority fencing, duplicate-execution prevention, idempotency/reconciliation, public-repository safety, explicit operator STOP/PAUSE, or program terminal acceptance. Scheduler bookkeeping drift is repaired forward; stale wakes may not roll DTSTART, canonical lineage, authority, or checkpoint state backward.

## Current acceptance gate

The utilization program does not pass because a 600-second hard floor exists or because a single long turn succeeds. It passes only from the active machine-readable P0 policy and valid prospective evidence. Until those thresholds are durably met, program status remains nonterminal and the relay continues through the current SAME MAIN continuation mechanism.
