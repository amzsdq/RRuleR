# AGENTS.md — Disposable Session Bootstrap Contract

## Prime directive

A ChatGPT session is disposable. Durable GitHub state is authoritative.

## Mandatory startup

1. Read `control/POLICY.md`.
2. Read `state/CURRENT.json`.
3. Resolve root goal, status, owner/authority epoch, latest checkpoint, and exact next action.
4. On a relay wake, establish/verify the next wake before substantive work.
5. Read only the task-specific files needed for the current work unit.
6. Continue from durable state; never restart completed work merely because local chat context is missing.

## Utilization rule

Useful-work utilization is a first-class objective.

- After the next wake is secured, start substantive work immediately.
- While the root is non-terminal and useful admissible work exists, do not voluntarily idle.
- A completed document, checkpoint, milestone, phase, or scheduled quarter boundary is not a yield condition.
- When one bounded work unit finishes, immediately select the next useful non-duplicative unit.
- Keep work units small enough that a successor-triggered handoff can finish the current unit safely.
- Checkpointing preserves state; checkpointing alone does not authorize stopping.

## Successor-triggered handoff

A predecessor keeps working until a successor wake is actually observed.

1. Scheduled time arrival alone does not trigger handoff.
2. If the scheduled time passes with no successor evidence, continue useful work.
3. Once successor execution is actually observed, stop starting new substantive units.
4. Finish the current smallest safe unit.
5. Persist checkpoint, evidence, duration/progress, side-effect ambiguity, and exact next action.
6. Emit a concise handoff status and end.
7. Successor treats predecessor as active until the durable handoff is visible and must not duplicate its active unit.

If the platform does not allow same-canonical overlap/queue, do not manufacture an idle gap. Continue predecessor work until platform-enforced termination; successor then reconstructs from GitHub.

## Execution discipline

- Continue useful work while the root remains non-terminal.
- Before handoff, finish the current smallest safe checkpointable work unit.
- Persist the checkpoint before relinquishing authority.
- Record side effects that may already have happened.
- Reconcile ambiguous irreversible side effects before replay.
- Chat prose is not completion evidence.
- Do not create duplicate workers or wakes when a valid continuation already exists.

## Exit states

- `CONTINUE` — work remains and continuation is established.
- `COMPLETE` — root acceptance is proven; relay is disabled.
- `BLOCKED_EXTERNAL` — a real external dependency is proven and internal alternatives are exhausted.
- `DEGRADED_CONTINUATION` — fast continuation failed but a verified slower fallback remains.

Tool/runtime/browser failure is an incident, not root completion.

## Public repository rule

Never write secrets or private source material here. Store only public-safe state or references.
