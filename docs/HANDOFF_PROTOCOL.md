# Successor-Triggered Handoff Protocol

## Objective

Transfer logical work ownership with minimal idle time while preventing duplicate substantive execution.

The protocol does not assume that the scheduler supports concurrent runs of the same canonical automation. The operational target is a 14+1 rhythm: predecessor stays useful for roughly 14 minutes, then remains immediately checkpointable for the successor-triggered baton pass.

## States

### PREDECESSOR_ACTIVE

- predecessor owns current substantive work;
- next wake is already armed and verified;
- predecessor continuously selects useful bounded work units;
- after roughly 12 minutes, predecessor avoids admitting units that are expensive to checkpoint;
- near 14 minutes, predecessor remains productive but `HANDOFF_READY` on tiny safe units.

### SUCCESSOR_DUE

The scheduled clock boundary has arrived, but successor execution is not yet observed.

This state **does not** change work ownership. Predecessor continues working.

### SUCCESSOR_OBSERVED

There is positive evidence that the successor run actually began **and the successor has already secured its following quarter wake**.

This is the normal handoff trigger. Observation alone does not let the successor duplicate the predecessor's active unit.

### HANDOFF_DRAIN

Predecessor:

- starts no new substantive unit;
- finishes only its current smallest safe unit;
- persists final meaningful progress timestamp, checkpoint, evidence, and exact next action;
- commits the measurable predecessor end boundary when it is actually known.

Successor:

- performs no duplicate substantive unit;
- reads durable state;
- waits/rechecks if the predecessor handoff is not yet durable;
- may perform only non-conflicting read-only preparation before takeover.

### HANDOFF_COMMITTED

Durable state contains the predecessor's safe resume point, exact next action, and the known handoff/end evidence required for measurement.

### SUCCESSOR_ACTIVE

Successor advances authority and resumes substantive work from the committed checkpoint.

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
       | AND successor next wake secured
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

If the platform serializes same-canonical runs, `SUCCESSOR_OBSERVED` may occur only after the predecessor is ended by the platform. In that case the successor reconstructs from the latest durable checkpoint. Correctness must not depend on overlap, and the predecessor's exact end time must remain unknown unless positively observed.

## Positive successor evidence

Use the strongest available evidence. Mere wall-clock arrival is never enough.

Preferred evidence, strongest first:

1. **Successor-authored durable evidence** — the successor writes a handoff request/checkpoint carrying its run identity after verifying the next canonical quarter. This proves a new executor is alive and has completed the required rearm-first step.
2. **Direct current-run platform evidence** — an execution/run identifier or equivalent current-run evidence exposed by the automation platform.
3. **Automation metadata transition** — metadata such as `last_run_time` advances to the expected successor occurrence, provided the value is fresh and unambiguously belongs to the canonical automation.

A scheduled timestamp by itself, or an unchanged automation object merely showing the future RRULE, is not successor evidence.

When overlap exists, successor-authored durable evidence is preferred because it gives the predecessor a concrete request to observe. When same-canonical execution is serialized, the successor must not fabricate a predecessor handoff; it records the latest durable predecessor boundary and classifies unknown end/gap fields as unknown.

## Baton request contract

A normal successor request should establish all of these facts before predecessor drains:

- canonical automation identity matches;
- successor's following quarter wake is already verified;
- program/root identity matches fresh durable state;
- predecessor run identity and authority epoch observed by successor are named;
- successor run identity is named;
- request timestamp is durable;
- predecessor active unit is not claimed by successor.

The current `state/HANDOFF.json` is the compact control surface; `state/RUNS.jsonl` retains run-level measurement evidence. Do not use chat prose as the only request/acknowledgement record.

## Invariants

1. One substantive work unit has at most one active executor.
2. Scheduled-time arrival alone does not transfer ownership.
3. Predecessor voluntarily idling before successor observation is forbidden while useful work remains.
4. Successor does not duplicate the predecessor's active unit.
5. Handoff is durable before successor relies on predecessor-local context.
6. Stale authority cannot perform authoritative substantive writes.
7. Utilization optimization never weakens reconciliation/idempotency rules.
8. Successor rearm precedes handoff request.
9. Authority moves forward only; scheduler recovery never rolls an epoch backward.
10. Missing runtime boundaries remain unknown rather than being inferred from the 15-minute cadence.

## Timeout/runtime protection

Work units should be bounded, but bounded does not mean short for its own sake.

Prefer a stream of small useful units so that, when successor evidence arrives, the predecessor can reach a safe handoff boundary quickly. Near the 14-minute target, use tiny checkpointable units rather than idling.

If the platform ends the run before explicit handoff:

- latest durable checkpoint is the recovery boundary;
- successor records `PLATFORM_ENFORCED_TERMINATION` only when the platform end is positively evidenced;
- otherwise exact predecessor end remains unknown;
- successor resumes rather than restarting the root.

## Measurement

At each handoff, record when observable:

- predecessor substantive-work start timestamp;
- predecessor last meaningful progress timestamp;
- successor observed/request timestamp;
- handoff committed/run-ended timestamp;
- successor first productive timestamp.

Derived metrics:

- observed useful-work span;
- handoff drain time;
- successor wait time;
- relay-caused idle gap.

A valid 840-second utilization turn requires durable boundaries as defined in `docs/UTILIZATION.md`; schedule arithmetic is not a substitute for evidence.
