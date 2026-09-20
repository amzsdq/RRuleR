# AGENTS.md — Disposable Session Bootstrap Contract

## Prime directive

A ChatGPT session is disposable. Durable GitHub state is authoritative.

## Mandatory startup

1. Read `control/POLICY.md`.
2. On a relay run, read `control/relay-policy.v1.json` as the machine-readable relay contract.
3. Read `state/CURRENT.json`, `state/ACTIVITY.json`, `state/HANDOFF.json`, `control/handoff-recovery.v1.json`, and `control/scheduler-fence.v1.json`.
4. Resolve root goal, program status, owner/authority epoch, latest checkpoint, exact next action, current activity evidence, and durable expected next due.
5. BEFORE substantive work, compare this wake against durable expected due under `control/scheduler-fence.v1.json`. Scheduler mismatch is a RECOVERY condition, not a yield condition: preserve the live canonical schedule, reconcile durable expected-due/owner/handoff state to the newest verified continuation, then continue. A stale occurrence must not restore an older prompt/title or roll authority backward.
6. For an expected wake, establish/verify the next recurring wake before substantive work. Keep the schedule as one hourly RRULE and rotate only the minute slot in the fixed quarter cycle: 00 -> 15 -> 30 -> 45 -> 00(next hour).
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

## Fourteen-minute primary objective planning

After REARM+VERIFY and authority acquisition, DO NOT begin with miscellaneous small work.

Before the first substantive action, persist one PRIMARY TURN OBJECTIVE designed to consume up to about 14 minutes of useful work.

The plan must contain:
- one concrete primary objective;
- expected useful-work duration, normally 10-14 minutes and never intentionally above 14 minutes;
- explicit acceptance criteria that can be checked at handoff;
- 2-5 checkpointable substeps that advance the same objective;
- the smallest safe handoff boundary for each substep;
- a fallback continuation unit only if the primary objective finishes materially early.

Planning discipline:
- Prefer one coherent medium-sized objective over many unrelated microtasks.
- Do not choose an objective expected to finish in only a few minutes when a larger useful objective can safely be formed.
- Do not pad with busywork merely to reach 14 minutes.
- If no single useful objective can honestly fill most of the window, bundle tightly related substeps under one outcome-level objective.
- Persist the plan BEFORE substantive execution so a successor can distinguish planned work from opportunistic drift.
- Execute the planned objective continuously. Do not re-plan merely because an intermediate substep completed.
- At ~12 minutes, stop admitting any substep that is expensive to checkpoint.
- On actual successor handoff request, finish only the current smallest safe boundary, persist achieved acceptance criteria and exact remaining substep, then hand off.

## Fifteen-minute worker cycle

Each scheduled wake is a worker generation in a rolling handoff pipeline. The 15-minute interval is the work-packet design horizon, not a voluntary stop timer.

1. Reconstruct fresh durable state and run scheduler reconciliation. A mismatch must be repaired in-place when a valid live continuation exists; it must not cause a non-terminal no-op.
2. REARM+VERIFY the same canonical hourly RRULE by moving its minute slot exactly one quarter: 00->15, 15->30, 30->45, 45->00(next hour).
3. If predecessor exists, persist HANDOFF_REQUEST only after rearm verification.
4. While predecessor is fresh, wait for its durable handoff commit and do only non-conflicting preparation.
5. If predecessor is SUSPECT or OVERDUE and remains unchanged through the recovery grace, execute `control/handoff-recovery.v1.json`.
6. After authority is obtained, persist a PRIMARY TURN OBJECTIVE with an expected 10-14 minute useful-work duration, acceptance criteria, and 2-5 checkpointable substeps; then execute that objective continuously.
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


## Utilization optimization loop

Current optimization target: average observed useful-work span >= 840 seconds per 15-minute turn.

At every valid wake:
1. Record wake/start and rearm verification timestamps.
2. Read the previous completed-turn utilization result before planning.
3. Plan enough useful, non-duplicative work to occupy the upcoming quarter-hour window; prefer several checkpointable units over one tiny unit.
4. Start substantive work immediately after authority is obtained.
5. Refresh durable activity at least after every meaningful unit and, when practical, do not allow more than 120 seconds without durable progress evidence while actively working.
6. On successor handoff, close the smallest safe unit, persist the exact continuation, then finalize the run measurement.
7. Compute at minimum: observed_useful_span_seconds, dead_tail_seconds, scheduler_or_handoff_overhead_seconds, and end_reason. Never infer missing timestamps.
8. If the completed turn is under 840 seconds, classify the dominant cause and persist exactly one concrete corrective experiment for the next turn. Valid cause classes include PACKET_TOO_SMALL, EARLY_VOLUNTARY_END, WAITING_ON_TOOL_OR_CI, SCHEDULER_GAP, HANDOFF_DELAY, AUTHORITY_RECOVERY, and UNKNOWN_EVIDENCE_GAP.
9. The next worker MUST read and apply the latest corrective experiment before selecting its work packet.
10. Do not declare the utilization goal reached from one good turn. Goal PASS requires at least 3 valid completed turns with a rolling mean observed useful-work span >= 840 seconds/.
11. Until PASS, utilization optimization remains the active root and each turn must measure -> diagnose -> change -> retest. Do not repeat the same failed intervention without new evidence.


## Runtime-safe baton timing

The intended rhythm is ~14 minutes of useful work inside each 15-minute wake interval, followed by a fast successor-triggered baton pass.

- Treat 840 seconds as the useful-work target and ~60 seconds as handoff/runtime safety margin.
- Do not spend that final margin idling. Continue useful bounded work, but after ~12 minutes avoid starting a unit that cannot be checkpointed quickly.
- Around ~14 minutes, enter HANDOFF_READY mode: keep durable state current, prefer tiny checkpointable/read-only units, and be able to stop within the smallest safe boundary when the successor request appears.
- The successor wakes on the quarter-hour, rearms its own next quarter first, then requests handoff.
- The predecessor immediately stops admitting new substantive units, closes the smallest safe unit, saves exact continuation/evidence, commits handoff, and ends.
- If the successor is late, the predecessor keeps doing useful small units; there is no voluntary idle tail.
- This cadence is specifically intended to avoid long single-turn runtime exposure while maintaining near-continuous utilization.


## Priority override — utilization continuity

For the active RRULER-UTILIZATION program, continuity and measured useful-work utilization are the highest operational priority below platform/security constraints.

- Internal stale-wake, scheduler-fence, handoff-freshness, CI-pending, or bookkeeping inconsistencies are recovery work, not reasons to stop.
- If the canonical automation is enabled and a future quarter wake can be verified, reconcile durable state to that continuation and keep the program moving.
- Never intentionally no-op a non-terminal expected/recoverable wake merely because durable timing metadata is stale.
- Do not bypass actual platform/security controls, irreversible-side-effect reconciliation, or public-repository secret protections.
