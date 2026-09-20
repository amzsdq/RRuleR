# Disposable Actor Delegation Model

Status: **bootstrap design; activation deferred until core fencing is enforced**

RRuleR separates logical roles from ChatGPT sessions. A session is an executor instance, not an identity that must survive.

## Roles

### Coordinator

Owns decomposition, dependency ordering, acceptance criteria, and recovery decisions for a root job. It does not own durable truth; GitHub does.

### Worker

Claims one bounded work unit under a fenced lease, performs substantive work, checkpoints, and submits evidence for verification.

### Verifier

Checks explicit acceptance criteria and evidence. It may return revision without taking over the worker's unfinished implementation.

### Supervisor

Evaluates liveness evidence and continuation health. It does not blindly replay ambiguous work.

A single session may temporarily perform more than one role only when policy explicitly permits it and authority remains unambiguous.

## Actor identity

Distinguish:

- `role_id` — logical role, e.g. `COORDINATOR`;
- `actor_id` — logical actor lineage;
- `session_id` — disposable execution instance;
- `authority_epoch` — fencing generation.

Never use chat title or conversational memory as authority.

## Delegation envelope

A work assignment should contain at least:

```json
{
  "root_job_id": "ROOT-...",
  "work_unit_id": "WU-...",
  "parent_work_unit_id": null,
  "assigned_role": "WORKER",
  "objective": "bounded outcome",
  "acceptance": ["machine- or evidence-checkable criterion"],
  "dependencies": [],
  "allowed_surfaces": ["repo:path"],
  "forbidden_effects": [],
  "checkpoint_ref": "CP-...",
  "authority_epoch": 12
}
```

## Worker lifecycle

```text
PROVISIONED
 -> READY
 -> CLAIMED
 -> WORKING
 -> SUBMITTED
 -> VERIFYING
 -> ACCEPTED

WORKING -> CHECKPOINTED -> WORKING
WORKING -> SUSPECT_LIVENESS -> RECOVERABLE
VERIFYING -> REVISION -> WORKING
```

Provisioning/READY proves reachability, not substantive completion.

## Fresh versus reused worker

Default to a fresh disposable session when the work unit is separable and its state can be reconstructed cheaply from GitHub. Reuse a live session only when continuity has material value and reuse does not create authority ambiguity or context contamination.

The optimization criterion is expected progress/effectiveness subject to correctness, not preserving sessions for its own sake.

## Parallelism gate

Parallel workers are allowed only when all are true:

1. work units have explicit non-overlapping ownership or conflict-safe write rules;
2. each unit has its own lease/fence;
3. dependencies are durable;
4. side effects have stable effect IDs;
5. acceptance can be verified independently;
6. merge/reconciliation ownership is explicit.

Otherwise serialize.

## Recovery

If a worker becomes suspect:

1. inspect its latest durable checkpoint;
2. inspect/reconcile ambiguous effects;
3. expire/revoke old claim according to policy;
4. increment authority epoch;
5. assign the same logical work unit to a replacement session;
6. replacement cold-starts from GitHub and continues.

Do not create a new logical work unit merely to hide a failed executor.

## Completion

Worker `SUBMITTED` is not root completion. A verifier must record acceptance evidence. Coordinator/root state advances only from accepted durable results.

## Activation rule

Do not build elaborate actor orchestration before fenced leases, resumable checkpoints, effect receipts, and acceptance evidence are working. Delegation multiplies race conditions; it should be layered on top of those invariants, not used to compensate for their absence.
