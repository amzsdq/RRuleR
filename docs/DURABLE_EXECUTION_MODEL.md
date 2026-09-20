# Durable Execution Model

Status: **bootstrap normative design**

This document defines the minimum durable semantics required beyond the wake relay itself. The scheduler only creates execution opportunities; correctness lives in GitHub state.

## 1. Root state machine

```text
NEW
 -> READY
 -> ACTIVE
 -> VERIFYING
 -> COMPLETE

ACTIVE -> RECOVERING -> ACTIVE
ACTIVE -> BLOCKED_EXTERNAL
VERIFYING -> ACTIVE          (acceptance failed / more work)
BLOCKED_EXTERNAL -> READY    (dependency cleared)
```

`COMPLETE` is terminal and requires durable acceptance evidence.

## 2. Work-unit state machine

```text
QUEUED
 -> CLAIMED
 -> WORKING
 -> CHECKPOINTED
 -> VERIFYING
 -> ACCEPTED

CLAIMED|WORKING|CHECKPOINTED -> SUSPECT_LIVENESS -> RECOVERABLE
RECOVERABLE -> CLAIMED       (new fenced authority)
VERIFYING -> WORKING         (revision required)
```

A work unit is not accepted merely because a session says it finished.

## 3. Authority / lease model

Every authoritative work claim carries:

- `root_job_id`
- `work_unit_id`
- `owner_id`
- monotonic `authority_epoch`
- `lease_acquired_at`
- `lease_expires_at`
- optional `heartbeat_at`
- `checkpoint_id`

A writer must re-read durable authority before a substantive authoritative write. If it observes a higher epoch or a different valid owner, it is stale and must not advance the work unit.

Lease expiry does **not** prove the old worker is dead. It only permits recovery to create a newer fenced authority. The monotonic epoch makes late stale writes rejectable.

## 4. Checkpoint contract

A resumable checkpoint records enough information for a cold session to continue without chat history:

```json
{
  "checkpoint_id": "CP-...",
  "root_job_id": "...",
  "work_unit_id": "...",
  "authority_epoch": 7,
  "completed": ["durable facts / outputs"],
  "in_progress": "smallest active unit",
  "next_action": "exact executable next action",
  "evidence": ["commit/run/issue/reference ids"],
  "side_effects": [
    {
      "effect_id": "...",
      "status": "NOT_STARTED|CONFIRMED|AMBIGUOUS",
      "receipt": null
    }
  ]
}
```

A checkpoint is recovery state, not a yield signal.

## 5. Idempotent side effects

Before an externally visible or irreversible effect, derive a stable `effect_id` from the logical operation, not from the current session.

Protocol:

1. read the durable effect record;
2. if `CONFIRMED`, do not replay;
3. if `AMBIGUOUS`, reconcile the target system first;
4. if absent/`NOT_STARTED`, perform the effect once;
5. capture a receipt or target-state proof;
6. persist `CONFIRMED` with the receipt.

At-least-once wake delivery is allowed. At-least-once irreversible side effects are not.

## 6. Completion verification

Separate **execution** from **acceptance**.

A work unit reaches `VERIFYING` when implementation appears done. A verifier then checks explicit acceptance criteria and durable evidence. Only verified criteria permit `ACCEPTED`.

The root reaches `COMPLETE` only when:

- all required work units are accepted or explicitly waived by policy;
- required tests/checks pass;
- no unresolved ambiguous side effect remains;
- durable current state and evidence agree;
- no required continuation remains.

## 7. Liveness and recovery

Liveness detection uses durable evidence, not absence of chat prose alone. Signals may include:

- expired lease;
- overdue heartbeat/checkpoint;
- missing expected continuation;
- repeated unchanged checkpoint beyond policy threshold;
- known failed execution receipt.

Recovery flow:

```text
suspect liveness
 -> inspect durable checkpoint + side effects
 -> reconcile ambiguous effects
 -> fence old authority with epoch+1
 -> claim same logical work unit
 -> cold-start from checkpoint
 -> continue
```

Do not create a new logical job merely because the executor changed.

## 8. Scheduler decoupling

The durable model must not depend on RRULE phase rotation. Any wake source is admissible if it can start a session that reconstructs the same durable state and respects authority/fencing.

Current RRULE self-update is therefore an adapter, not the runtime's source of truth.

## 9. Public-safe boundary

Because this repository is public, durable records may contain identifiers, hashes, public references, state classifications, and sanitized evidence, but never credentials, session material, private source text, or personal data.

## 10. Minimum implementation order

1. Durable current/root state.
2. Checkpoint schema.
3. Authority/lease + monotonic fencing.
4. Side-effect ledger/idempotency keys.
5. Verification/acceptance evidence.
6. Liveness classification and recovery transition.
7. Replaceable scheduler adapters.
8. Delegation/parallel work only after the above invariants are enforceable.
