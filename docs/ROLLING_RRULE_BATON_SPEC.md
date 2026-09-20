# Rolling RRULE Baton Specification

Status: proposed canonical runtime lifecycle  
Date: 2026-09-21

## 1. Goal

Use one recurring wake identity as both:

1. a bounded cold-rescue deadline while the current invocation is alive; and
2. a fast completion-relative continuation after normal work completes.

The schedule must not define the work duration. Work completion determines the next fast wake.

## 2. Core lifecycle

```text
WAKE
  -> read minimum durable fence/current state
  -> validate wake/authority
  -> read predecessor-planned NEXT PACKET
  -> establish provisional continuation for packet target + safety margin
  -> verify continuation
  -> restore checkpoint
  -> execute useful packet continuously
  -> checkpoint
  -> plan the successor packet
  -> persist successor packet durably
  -> mirror only a small packet capsule into the reservation text
  -> establish completion-relative continuation (default close + 60s)
  -> verify
  -> return
```

Default operating envelope:

- target useful work: 600 seconds;
- normal packet range: roughly 420-660 seconds when the work shape justifies it;
- provisional safety margin: 180 seconds by default;
- normal fast continuation: completion + 60 seconds;
- all timing values are tunables, not architectural constants.

Example: a predecessor estimates the next packet at 9 minutes. It may leave a 9-minute target and a 12-minute provisional rescue horizon. The successor secures that rescue horizon first, performs the packet, then moves the next normal wake to one minute after actual completion.

## 3. Successor baton

The predecessor is responsible for reducing the next worker's startup tax.

Before normal close it writes a small durable work packet containing:

- packet id;
- program/root identity;
- authority epoch that planned it;
- checkpoint reference;
- one concrete objective;
- target work duration;
- provisional safety margin;
- acceptance criteria;
- exact first action;
- fallback action if the packet is stale or invalid.

The reservation text may cache a small subset such as packet id, checkpoint reference, target work time and provisional offset. That cache is never authoritative.

### Correctness rule

GitHub durable state wins over the reservation capsule.

A successor must refresh rather than blindly execute the cached packet when program/root/authority/checkpoint lineage has changed.

## 4. Why predecessor planning matters

Without a baton, every wake pays:

```text
restore -> inspect -> choose work -> decompose -> begin
```

With a baton, the fast path becomes:

```text
minimum validation -> provisional continuation -> restore referenced checkpoint -> begin
```

This shifts planning cost into the predecessor's already-warm context and increases useful-work duty cycle.

## 5. Safety invariants

- Durable state remains authoritative.
- A cached reservation packet is a fast-start hint, not a second source of truth.
- Stale wakes may not roll schedule generation or authority backward.
- A packet target is a planning horizon, not a forced stop timer.
- Busywork to consume the target window is forbidden.
- Ambiguous irreversible effects must be reconciled before replay.
- The current invocation checkpoints before publishing the successor packet.
- The successor packet is invalidated by incompatible root, authority, checkpoint or terminal-state changes.

## 6. Failure behavior

### Invocation dies after provisional continuation

The provisional occurrence is the cold-rescue path. A fresh invocation reconstructs from the latest durable checkpoint.

### Invocation dies before provisional continuation is verified

No substantive side effect should have started yet. The prior verified continuation remains the fallback when available.

### Normal close continuation mutation fails

Preserve the newest already-verified future occurrence, record degraded continuation, and never claim a secured fast handoff without evidence.

### Cached baton is stale

Refresh from fresh durable state and continue. Staleness is recovery work, not program completion.

## 7. Utilization model

With 10 minutes useful work and a one-minute normal gap, theoretical duty cycle is:

```text
600 / (600 + 60) = 90.9%
```

Measured production duty cycle must use evidenced useful intervals and observed scheduler/runtime overhead, not the theoretical ratio.

The cold-rescue margin is not a normal idle interval. It is paid only when the active invocation fails before normal close.

## 8. Acceptance tests

The lifecycle is production-accepted only when all are demonstrated:

1. same wake identity can move its future occurrence and remain active;
2. two consecutive automatic wakes follow the moved due time;
3. stale occurrence cannot restore an older schedule or authority;
4. abrupt-loss fault injection resumes from the last checkpoint;
5. normal close produces a completion-relative wake without a fixed quarter-hour wait;
6. successor can start from a predecessor-planned packet without trusting chat context;
7. invalid packet refreshes safely from durable state;
8. no duplicate irreversible side effect occurs during recovery;
9. utilization and recovery latency are recorded separately.

## 9. Relationship to schedulers

Rolling RRULE is an adapter, not the architecture.

A future event-trigger, queue worker, cloud scheduler, or another wake provider may replace it if the same durable contracts survive:

- fenced authority;
- checkpoint continuation;
- successor packet;
- idempotent/reconciled side effects;
- independent completion evidence;
- bounded recovery;
- operator control.

## 10. Superseded operating assumption

The fixed 00/15/30/45 quarter-cycle is no longer the target architecture. It may remain in historical experiment evidence, but it must not be treated as an active instruction once the rolling lifecycle is accepted.
