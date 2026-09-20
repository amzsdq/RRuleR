# AGENTS.md — Disposable Session Bootstrap Contract

## Prime directive

A ChatGPT session is disposable. Durable GitHub state is authoritative.

## Mandatory startup

1. Read `control/POLICY.md`.
2. On a relay run, read `control/relay-policy.v1.json` as the machine-readable relay contract.
3. Read `state/CURRENT.json`, `state/ACTIVITY.json`, `state/HANDOFF.json`, `control/handoff-recovery.v1.json`, and `control/scheduler-fence.v1.json`.
4. Resolve root goal, program status, owner/authority epoch, latest checkpoint, exact next action, current activity evidence, and durable expected next due.
5. BEFORE any automation mutation, compare this wake against the durable expected due under `control/scheduler-fence.v1.json`. A stale queued occurrence may record an incident but MUST NOT update/disable the canonical, restore an old prompt/title, or claim authority.
6. For an expected wake, establish/verify the next recurring wake before substantive work. Compute it from actual wake/start: target_due = next whole minute at least 15 minutes after actual wake/start.
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

## Fifteen-minute worker cycle

Each scheduled wake is a worker generation in a rolling handoff pipeline. The 15-minute interval is the work-packet design horizon, not a voluntary stop timer.

1. Reconstruct fresh durable state and pass the scheduler-fence check.
2. REARM+VERIFY the same canonical RRULE for the next whole minute at least 15 minutes after actual wake.
3. If predecessor exists, persist HANDOFF_REQUEST only after rearm verification.
4. While predecessor is fresh, wait for its durable handoff commit and do only non-conflicting preparation.
5. If predecessor is SUSPECT or OVERDUE and remains unchanged through the recovery grace, execute `control/handoff-recovery.v1.json`.
6. After authority is obtained, select a useful work packet sized for roughly the next 15-minute window and execute it.
7. If the packet finishes early and useful work remains, pull another bounded unit rather than idle.
8. A predecessor checks for pending handoff after every bounded unit; on request it closes the smallest safe unit and hands off promptly.

Successor ordering: FRESH_STATE+SCHEDULER_FENCE -> REARM+VERIFY -> HANDOFF_REQUEST -> WAIT_OR_RECOVER -> CLAIM_AUTHORITY -> PLAN_15M_PACKET -> WORK.

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
