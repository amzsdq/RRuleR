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

## Execution discipline

- Continue useful work while the root remains non-terminal.
- A milestone, phase, or document boundary is not an automatic yield point.
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
