# Successor-Triggered Handoff Protocol

## Objective

Transfer logical work ownership with minimal idle time while preventing duplicate substantive execution.

The protocol does not assume that the scheduler supports concurrent runs of the same canonical automation.

## States

### PREDECESSOR_ACTIVE

- predecessor owns current substantive work;
- next wake is already armed and verified;
- predecessor continuously selects useful bounded work units.

### SUCCESSOR_DUE

The scheduled clock boundary has arrived, but successor execution is not yet observed.

This state **does not** change work ownership. Predecessor continues working.

### SUCCESSOR_OBSERVED

There is positive evidence that the successor run actually began.

This is the normal handoff trigger.

### HANDOFF_DRAIN

Predecessor:

- starts no new substantive unit;
- finishes only its current smallest safe unit;
- persists final predecessor checkpoint and evidence.

Successor:

- performs no duplicate substantive unit;
- reads durable state;
- waits/rechecks if the predecessor handoff is not yet durable.

### HANDOFF_COMMITTED

Durable state contains the predecessor's safe resume point and exact next action.

### SUCCESSOR_ACTIVE

Successor resumes substantive work from the committed checkpoint.

## State flow

```text
PREDECESSOR_ACTIVE
       |
       | scheduled time arrives
       v
SUCCESSOR_DUE --------------------+
       |                          |
       | no successor observed    |
       +------ predecessor works -+
       |
       | successor actually observed
       v
SUCCESSOR_OBSERVED
       |
       v
HANDOFF_DRAIN
       |
       v
HANDOFF_COMMITTED
       |
       v
SUCCESSOR_ACTIVE
```

If the platform serializes same-canonical runs, `SUCCESSOR_OBSERVED` may occur only after the predecessor is ended by the platform. In that case the successor reconstructs from the latest durable checkpoint. Correctness must not depend on overlap.

## Positive successor evidence

Use the strongest available evidence. Examples include:

- automation metadata showing a new `last_run_time` corresponding to the scheduled successor;
- a successor-authored durable event/checkpoint;
- direct current-run evidence exposed by the automation platform.

Mere wall-clock arrival is not positive evidence.

## Invariants

1. One substantive work unit has at most one active executor.
2. Scheduled-time arrival alone does not transfer ownership.
3. Predecessor voluntarily idling before successor observation is forbidden while useful work remains.
4. Successor does not duplicate the predecessor's active unit.
5. Handoff is durable before successor relies on predecessor-local context.
6. Stale authority cannot perform authoritative substantive writes.
7. Utilization optimization never weakens reconciliation/idempotency rules.

## Timeout/runtime protection

Work units should be bounded, but bounded does not mean short for its own sake.

Prefer a stream of small useful units so that, when successor evidence arrives, the predecessor can reach a safe handoff boundary quickly.

If the platform ends the run before explicit handoff:

- latest durable checkpoint is the recovery boundary;
- successor records `PLATFORM_ENDED` where observable;
- successor resumes rather than restarting the root.

## Measurement

At each handoff, record when observable:

- predecessor last productive timestamp;
- successor observed timestamp;
- handoff committed timestamp;
- successor first productive timestamp.

Derived metrics:

- handoff drain time;
- successor wait time;
- relay-caused idle gap.

See `docs/UTILIZATION.md`.
