# Relay Failure and Recovery Semantics

## Purpose

Define what counts as degraded continuation, relay death, and safe recovery for the RRULE self-update relay.

## Normal fast path

```text
wake
 -> update same recurring automation to next quarter
 -> verify update
 -> reconstruct durable state
 -> work continuously
 -> successor-triggered handoff
```

## Self-update failure with previous RRULE intact

Example:

```text
current schedule: FREQ=HOURLY;BYMINUTE=15
18:15 run attempts move to :30
update fails
old :15 hourly RRULE remains enabled and valid
```

Classification: `DEGRADED_CONTINUATION`.

Meaning:

- the fast 15-minute continuation path failed;
- the relay is not yet proven dead;
- the old hourly recurrence may wake again at 19:15;
- that future wake is a recovery opportunity, not proof of recovery until it actually runs.

Persist:

- failed attempted phase;
- previous verified RRULE;
- expected slower fallback wake;
- durable checkpoint;
- exact next action.

## Relay continuation failure

Do not claim self-rescue when any of these hold:

- automation is disabled;
- automation is deleted or missing;
- no valid future recurrence remains;
- schedule state is ambiguous and cannot be verified;
- durable continuation state is corrupt or insufficient;
- platform cannot execute automations.

Classification should explicitly require external/operator recovery.

## Runtime termination

Unexpected run termination is not root failure if:

- durable checkpoint is sufficient;
- a valid future wake exists.

The successor resumes from the last verified durable checkpoint.

## Duplicate wake/execution

At-least-once wake delivery is tolerable only if duplicate substantive execution is prevented.

A successor must not replay an active predecessor unit merely because it woke.

Use durable handoff/current authority state to decide whether to wait/recheck, resume, reconcile, or no-op.

## Ambiguous external side effect

If a side effect may have happened but confirmation is absent:

1. record ambiguity durably;
2. inspect idempotent/durable evidence;
3. reconcile before retry;
4. never blind replay an irreversible effect.

## Recovery priority

Prefer recovery that preserves existing durable work:

1. valid same-canonical scheduled continuation;
2. slower surviving recurring fallback;
3. explicit bounded external/operator recovery;
4. replacement actor only when the existing continuation identity is genuinely unusable and replacement semantics are defined.

## Completion

Recovery machinery stops when the root is proven COMPLETE.

Completion requires:

- terminal durable state;
- final acceptance evidence;
- same canonical automation disabled;
- no successor wake.
