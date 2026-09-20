# AGENTS.md — Disposable Session Bootstrap Contract

## Prime directive

A ChatGPT session is disposable. Durable GitHub state is authoritative.

## Mandatory startup

1. Read `control/POLICY.md`.
2. On a relay run, read `control/relay-policy.v1.json` as the machine-readable relay contract.
3. Read `state/CURRENT.json`, `state/ACTIVITY.json`, `state/HANDOFF.json`, `control/handoff-recovery.v1.json`, and `control/scheduler-fence.v1.json`.
4. Resolve root goal, program status, owner/authority epoch, latest checkpoint, exact next action, current activity evidence, and durable expected next due.
5. BEFORE substantive work, compare this wake against durable expected due under `control/scheduler-fence.v1.json`. Scheduler mismatch is a RECOVERY condition, not a yield condition: preserve the live canonical schedule, reconcile durable expected-due/owner/handoff state to the newest verified continuation, then continue. A stale occurrence must not restore an older prompt/title or roll authority backward.
6. For an expected wake, validate the predecessor-planned successor packet and establish/verify the provisional future continuation before full restore or substantive work. The fixed quarter-hour cycle is retired as an active instruction.
7. If a predecessor is active, persist a durable handoff request only after the successor's own next wake is secured.
8. Persist `state/ACTIVITY.json` as WORKING before or with the first substantive durable change after authority is obtained.
9. Read only the task-specific files needed for the current work unit.
10. Continue from durable state; never restart completed work merely because local chat context is missing.

## Utilization rule

Useful-work utilization is a first-class objective.

- After the next wake is secured and authority is obtained, start substantive work immediately.
- While the program is non-terminal and useful admissible work exists, do not voluntarily idle.
- A completed document, checkpoint, milestone, phase, root job, or schedule boundary is not by itself a yield condition.
- When one bounded work unit finishes, check for pending handoff; if ownership remains, immediately select the next useful non-duplicative unit.
- Never invent busywork merely to keep the relay alive.
- Keep work units small enough that a successor-triggered handoff can finish the current unit safely.
- Refresh durable activity evidence after meaningful work units.

## Successor-triggered handoff

A predecessor keeps working until a successor wake is actually observed.

1. Scheduled time arrival alone does not trigger handoff.
2. If the scheduled time passes with no successor evidence, continue useful work.
3. Once a durable successor handoff request is observed, stop starting new substantive units.
4. Finish the current smallest safe unit.
5. Persist checkpoint, activity/handoff evidence, duration/progress, side-effect ambiguity, and exact next action.
6. Commit handoff and relinquish authority promptly.
7. Successor treats predecessor as active until durable handoff is visible, unless `control/handoff-recovery.v1.json` becomes eligible.

## Successor packet planning

After provisional continuation and authority validation, use the durable successor packet when valid. If it is stale, refresh it from fresh durable state.

The packet should normally:
- target about 10 minutes of useful work, adjusted to the work shape;
- contain one coherent objective with explicit acceptance criteria;
- reference the checkpoint it continues from;
- define checkpointable substeps and a first action;
- carry a provisional safety margin;
- remain a planning horizon, never a forced stop timer.

Before a normal return, checkpoint current work and plan/persist the next successor packet so the next cold worker pays minimal startup/planning overhead.

## Rolling worker lifecycle

Each valid wake is a disposable worker generation in a rolling baton pipeline.

1. Reconstruct the minimum fresh fence/current/packet state.
2. Validate that the wake and successor packet are current; refresh stale packet state rather than trusting cached reservation text.
3. Establish and verify a provisional future continuation using the packet work target plus safety margin.
4. Restore the bound checkpoint and execute the packet continuously.
5. Persist durable progress after meaningful units.
6. On normal close, checkpoint, plan/persist the next successor packet, then establish/verify a short completion-relative continuation.
7. If the invocation dies, the provisional occurrence is the cold-rescue path.
8. Never convert a packet target or schedule boundary into a voluntary stop condition.

Successor ordering: MINIMUM_FENCE+PACKET -> PROVISIONAL_CONTINUATION -> RESTORE -> WORK -> CHECKPOINT -> NEXT_PACKET -> FAST_CONTINUATION -> RETURN


## Operator-visible activity

The ChatGPT composer/stop-button UI is an operator-visible hint, not the durable source of truth. Idle UI plus stale durable activity is a utilization-gap signal, not healthy idle.

## Execution discipline

- Continue useful work while the program remains non-terminal and this run owns authority.
- Persist the checkpoint before relinquishing authority.
- Record side effects that may already have happened.
- Reconcile ambiguous irreversible side effects before replay.
- Chat prose is not completion evidence.
- Do not create duplicate workers or wakes when a valid continuation already exists.

## Exit states

- `CONTINUE` — useful work remains and continuation is established.
- `PROGRAM_COMPLETE` — the overall program acceptance is proven; relay may be disabled.
- `BLOCKED_EXTERNAL` — a real external dependency is proven and internal alternatives are exhausted.
- `DEGRADED_CONTINUATION` — fast continuation failed but a verified slower fallback remains.

A root-level `COMPLETE` is not automatically a program exit state. Tool/runtime/browser failure is an incident, not program completion.

## Public repository rule

Never write secrets or private source material here. Store only public-safe state or references.

## Hard no-self-termination invariant

A non-terminal owner MUST NOT voluntarily end its turn.

- `CONTINUE`, `WORKING`, `DEGRADED_CONTINUATION`, checkpoint completion, CI success, document completion, root completion, or "nothing immediately obvious" are not permission to end.
- After every bounded unit, re-read durable state, check for pending handoff, then execute the next useful unit if ownership remains.
- If no next unit is obvious, inspect durable state/evidence for the highest-value unresolved invariant or validation gap.
- Only `PROGRAM_COMPLETE`, proven `BLOCKED_EXTERNAL`, committed successor handoff, explicit operator stop, platform-enforced termination, or validated loss of authority under stale-predecessor recovery may end an active turn.


## Utilization optimization loop

Current optimization target: sustained evidenced useful-work coverage with short normal continuation gaps and separately measured recovery latency.

At every valid wake:
1. record wake/start and continuation verification timestamps;
2. use or refresh the successor packet;
3. start substantive work immediately after authority/provisional continuation are secured;
4. refresh durable evidence after meaningful work, keeping unexplained evidence gaps <=120 seconds when practical;
5. on normal close, checkpoint and prepare the next packet before scheduling the fast completion-relative continuation;
6. measure useful coverage, startup overhead, normal continuation gap, and abrupt-loss recovery gap separately;
7. classify the dominant loss cause and leave one concrete corrective experiment when targets are missed;
8. do not declare success from one good window.

## Runtime-safe rolling timing

The intended rhythm is approximately 10 minutes of useful work, protected by a longer provisional rescue horizon, followed by a short completion-relative continuation.

- Ten minutes is a target, not a hard cutoff.
- The default provisional horizon is target work plus a tunable safety margin.
- Continue useful checkpointable work if the target is reached early or safely overrun.
- If the provisional deadline approaches while useful work remains, move the future continuation forward before collision and verify it.
- On normal close, checkpoint and set the next due from actual completion rather than a fixed wall-clock slot.
- Recovery timing and normal continuation timing are different metrics and must not be conflated.


## Priority override — utilization continuity

For the active RRULER-UTILIZATION program, continuity and measured useful-work utilization are the highest operational priority below platform/security constraints.

- Internal stale-wake, packet-staleness, scheduler-fence, checkpoint, CI-pending, or bookkeeping inconsistencies are recovery work, not reasons to stop.
- Preserve the newest verified future continuation and reconcile durable state forward.
- A stale cached reservation capsule may not roll durable packet/checkpoint/authority backward.
- Do not bypass actual platform/security controls or irreversible-side-effect reconciliation.


## Pre-final authorization gate

A user-visible final response is an authoritative run-ending side effect for an active owner.

Immediately before emitting ANY normal final response, the current owner MUST perform a fresh pre-final authorization check against:
- `state/CURRENT.json`;
- `state/HANDOFF.json`;
- `control/run-continuation-gate.v1.json`.

Rules:
- If program status is `CONTINUE` or `DEGRADED_CONTINUATION`, and no committed successor handoff, explicit operator stop, or actual platform-enforced termination exists, FINAL IS FORBIDDEN.
- A future cold-rescue wake being armed does NOT authorize the current healthy owner to stop.
- Reporting that work remains, that a checkpoint succeeded, or that the next wake is scheduled does NOT authorize final.
- If the pre-final gate denies final, do not emit a terminal/status reply. Immediately select and execute the next useful admissible unit in the same invocation.
- The check must be fresh and immediately precede any final. A stale earlier check cannot authorize final after more work/state changes.
