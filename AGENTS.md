# AGENTS.md — Disposable Session Bootstrap Contract

## Prime directive

A ChatGPT session is disposable. Durable GitHub state is authoritative.

## Mandatory startup

1. Read `control/POLICY.md`.
2. On a relay run, read `control/relay-policy.v1.json` as the machine-readable relay contract.
3. Read `state/CURRENT.json` and `state/ACTIVITY.json`.
4. Resolve root goal, program status, owner/authority epoch, latest checkpoint, exact next action, and current activity evidence.
5. On a relay wake, establish/verify the next recurring wake before substantive work.
6. Persist `state/ACTIVITY.json` as WORKING before or with the first substantive durable change.
7. Read only the task-specific files needed for the current work unit.
8. Continue from durable state; never restart completed work merely because local chat context is missing.

## Utilization rule

Useful-work utilization is a first-class objective.

- After the next wake is secured, start substantive work immediately.
- While the program is non-terminal and useful admissible work exists, do not voluntarily idle.
- A completed document, checkpoint, milestone, phase, root job, or schedule boundary is not by itself a yield condition.
- When one bounded work unit finishes, immediately select the next useful non-duplicative unit.
- When one root completes, persist its terminal evidence and immediately chain a materially useful next root if one exists.
- Never invent busywork merely to keep the relay alive.
- Keep work units small enough that a successor-triggered handoff can finish the current unit safely.
- Refresh durable activity evidence after meaningful work units; checkpointing preserves state but does not authorize stopping.

## Successor-triggered handoff

A predecessor keeps working until a successor wake is actually observed.

1. Scheduled time arrival alone does not trigger handoff.
2. If the scheduled time passes with no successor evidence, continue useful work.
3. Once successor execution is actually observed, stop starting new substantive units.
4. Finish the current smallest safe unit.
5. Persist checkpoint, activity/handoff evidence, duration/progress, side-effect ambiguity, and exact next action.
6. Emit a concise handoff status and end.
7. Successor treats predecessor as active until the durable handoff is visible and must not duplicate its active unit.

If the platform does not allow same-canonical overlap/queue, do not manufacture an idle gap. Continue predecessor work until platform-enforced termination; successor then reconstructs from GitHub.

## Operator-visible activity

The ChatGPT composer/stop-button UI is an operator-visible hint, not the durable source of truth.

- A foreground stop button generally means that foreground turn is still generating.
- A send button or idle composer means that foreground turn has ended; it does not prove that no separate scheduled run is active.
- Because the operator uses this UI as a practical liveness signal, an active predecessor must not voluntarily emit its normal final response before successor-triggered handoff, program terminal state, or platform-enforced termination.
- If the operator sees idle UI and `state/ACTIVITY.json` is also stale with no successor evidence, treat that as a utilization gap requiring recovery, not as healthy idle.

## Execution discipline

- Continue useful work while the program remains non-terminal.
- Before handoff, finish the current smallest safe checkpointable work unit.
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

A root-level `COMPLETE` is not automatically a program exit state.
Tool/runtime/browser failure is an incident, not program completion.

## Public repository rule

Never write secrets or private source material here. Store only public-safe state or references.

## Hard no-self-termination invariant

A non-terminal owner MUST NOT voluntarily end its turn.

- If program state is not `PROGRAM_COMPLETE` or `BLOCKED_EXTERNAL`, emitting a normal final response is forbidden unless a successor has actually been observed and the durable handoff has been committed.
- `CONTINUE`, `WORKING`, `DEGRADED_CONTINUATION`, checkpoint completion, CI pending/success, document completion, root completion, or "nothing immediately obvious" are NOT permission to end.
- After every bounded unit, re-read durable state, select the next useful admissible unit, and execute it in the SAME turn.
- If no next unit is obvious, the next unit is to inspect durable state/evidence for the highest-value unresolved invariant or validation gap; this is not a reason to idle.
- Only `PROGRAM_COMPLETE`, proven `BLOCKED_EXTERNAL`, committed successor handoff, explicit operator stop, or platform-enforced termination may end an active turn.
