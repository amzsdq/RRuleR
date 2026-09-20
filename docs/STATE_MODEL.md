# Durable State Model

## Design goal

A cold ChatGPT session must reconstruct active work without relying on prior conversational memory.

RRuleR therefore separates three kinds of durable information.

## 1. Current projection — `state/CURRENT.json`

This is the compact control-plane read model.

It answers:

- what root job is active;
- current terminal/non-terminal status;
- current logical owner;
- authority epoch;
- canonical wake automation;
- latest checkpoint;
- exact next action;
- continuation mechanism;
- public-safety constraints.

It is optimized for fast cold-start reads, not for full historical audit.

## 2. Event history — `state/EVENTS.jsonl`

This records meaningful control-plane events as JSON Lines.

Events document facts such as:

- next wake verified;
- work started;
- checkpoint persisted;
- successor observed;
- handoff completed;
- degraded continuation;
- terminal completion.

The event ledger is evidence/history. It does not automatically override the current projection.

## 3. Run observations — `state/RUNS.jsonl`

This records runtime and utilization observations.

It is deliberately separate from business/control events because measurement may be partial.

Unknown durations stay null. Do not infer precision.

## Authority epoch

`authority_epoch` is monotonic logical fencing metadata.

Minimum rule:

> A run that observes a newer authority epoch than the one it loaded must not perform authoritative substantive writes under the stale epoch.

The current bootstrap uses a single logical relay owner, so epoch changes are rare. The field exists now so future multi-worker or recovery mechanisms do not need to retrofit the concept.

## Checkpoint semantics

A checkpoint is a durable safe-resume boundary.

A checkpoint must contain enough information to continue the active root without guessing:

- completed work;
- evidence;
- unresolved risk/ambiguity where relevant;
- exact next action.

A checkpoint is **not** a yield instruction. Under continuous-work mode the current run checkpoints and continues until successor-triggered handoff or a terminal condition.

## Projection consistency

Normal write order for a meaningful unit:

```text
perform bounded work
 -> collect evidence
 -> update CURRENT projection
 -> optionally append EVENT / RUN observation
 -> deterministic validation
 -> continue next work unit
```

For future irreversible external effects, introduce an explicit intent/effect reconciliation model before relying on this simple order.

## Concurrent writers

Current bootstrap assumes effectively one authoritative control-plane writer.

Before enabling multiple concurrent writers, RRuleR must add and verify:

- lease/claim identity;
- monotonic fencing token or epoch discipline;
- stale-writer rejection;
- deterministic conflict resolution;
- idempotent/reconcilable external effects.

Do not treat GitHub file writes as a distributed compare-and-swap service without proving the required semantics.

## Terminal state

On terminal `COMPLETE`:

- final evidence is durable;
- `CURRENT.json` becomes terminal;
- canonical automation is disabled;
- no successor wake is scheduled;
- terminal event/run observation is appended where observable.
