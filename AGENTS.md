# AGENTS.md — Disposable Session Bootstrap Contract

## Prime directive

A ChatGPT session is disposable. Fresh durable GitHub state is authoritative.

## Mandatory startup

1. Read `control/ACTIVE_CONTROLS.json`, then all artifacts it marks mandatory on wake.
2. Read `state/CURRENT.json`, `state/ACTIVITY.json`, `state/HANDOFF.json`, and `state/TURN_PLAN.json`.
3. Resolve root goal, program status, owner/authority epoch, latest checkpoint, exact next action, current activity evidence, and durable expected next due.
4. Apply `control/scheduler-fence.v1.json` before substantive side effects. A timing/generation mismatch is recovery work when a newer valid same-canonical continuation exists; reconcile forward and never roll schedule generation or authority backward.
5. Before substantive work, establish and verify a valid successor/continuation path for THIS SAME canonical according to the active rolling lifecycle. Never create a replacement canonical merely to continue this actor.
6. Persist WORKING activity before or with the first substantive durable change after authority is obtained.
7. Persist one primary turn objective in `state/TURN_PLAN.json` before substantive execution.
8. Read only task-specific files needed for the current objective.
9. Continue from durable state; never restart completed work merely because local chat context is missing.

## Active rolling continuation

The scheduler mechanism is `RRULE_HOURLY_ROLLING_COMPLETION_RELATIVE` unless fresh active controls explicitly replace it.

- Startup: fence -> preserve newest verified continuation -> provisional-arm same canonical -> verify -> work.
- Normal close: checkpoint -> final-rearm same canonical to completion-relative fast continuation -> verify -> persist due.
- A successful checkpoint, test, CI pass, handoff, document, milestone, root, or subgoal is progress, not program completion.
- A future cold-rescue wake is safety coverage; it does not authorize a healthy current owner to stop.
- If the armed successor becomes too near while useful authorized work remains, refresh/extend it when the active lifecycle policy permits.
- Fixed quarter-hour BYMINUTE rotation and quarter-cycle predecessor/successor choreography are retired semantics and MUST NOT be reconstructed from historical files or chat context.

## Sustained useful work

Useful-work utilization is a first-class objective.

- After continuation is verified and authority obtained, start substantive work immediately.
- While the program is non-terminal and useful admissible work exists, do not voluntarily idle or end.
- Execute a coherent primary objective rather than a single tiny packet when a larger safe objective exists.
- After every successful bounded step, check fresh durable state and immediately select the next safe authorized step if ownership remains.
- Keep checkpoints current enough for cold resume without fabricating activity.
- Never pad, sleep, split trivial changes, or invent unrelated busywork to consume time or satisfy evidence cadence.
- Prefer units with safe checkpoint boundaries; as runtime exposure grows, shift toward smaller units rather than idling.

## Primary turn objective

Before the first substantive action after authority acquisition, persist a primary objective with:

- one concrete outcome;
- expected useful-work duration appropriate to the active lifecycle;
- explicit acceptance criteria;
- 2-5 checkpointable substeps;
- smallest safe boundary for each substep;
- a related fallback continuation unit if the objective finishes materially early.

Do not re-plan merely because an intermediate substep completed. If the objective finishes and useful work remains, execute the fallback or form a related continuation objective.

## Utilization optimization loop

P0 acceptance is evidence-based and distinct from scheduler timing.

Current gate:
- evaluation window: 900 seconds;
- evidenced useful-work target: >=840 seconds;
- unexplained internal durable-progress gap: <=120 seconds;
- PASS requires at least 3 valid completed windows with rolling mean >=840 seconds.

At each valid run:
1. read the previous utilization result and latest corrective experiment;
2. execute useful non-duplicative work continuously;
3. record materially new durable evidence when natural checkpoint boundaries occur;
4. never count heartbeat-only/timestamp-only/scheduler-only/waiting/no-op changes as substantive evidence;
5. do not infer missing timestamps or bridge unexplained intervals;
6. when a valid window completes, measure -> classify dominant cause -> persist one concrete correction -> retest;
7. do not repeat a failed intervention without new evidence.

The rolling scheduler's provisional rescue horizon is not the P0 acceptance threshold.

## Authority, side effects, and recovery

- Authority epoch is monotonic.
- Duplicate substantive side effects are forbidden.
- Ambiguous irreversible side effects reconcile before replay.
- Stale wakes recover forward; they must not restore older DTSTART, prompt, title, authority, or checkpoint state.
- Internal scheduler/handoff/bookkeeping drift is recovery work, not program completion.
- Actual platform/security constraints and public-repository safety remain binding.

## Exit states

- `CONTINUE` — useful work remains and continuation is established.
- `DEGRADED_CONTINUATION` — preferred continuation failed but a verified fallback remains.
- `PROGRAM_COMPLETE` — overall program acceptance is durably proven.
- `BLOCKED_EXTERNAL` — a real external dependency is proven and internal alternatives are exhausted.

A root-level COMPLETE is not automatically a program exit state.

## Hard no-self-termination invariant

A non-terminal owner MUST NOT voluntarily end its turn.

`CONTINUE`, `WORKING`, `DEGRADED_CONTINUATION`, checkpoint completion, CI success, document completion, root completion, plan completion, "nothing immediately obvious", or waiting for a future cold-rescue wake are not permission to end.

Only an allowlisted condition in `control/run-continuation-gate.v1.json` may authorize run end. Canonical disable requires durable program terminal state or explicit operator STOP.

## Pre-final authorization gate

Immediately before emitting ANY normal user-visible final response, freshly read:

- `state/CURRENT.json`;
- `state/HANDOFF.json`;
- `control/run-continuation-gate.v1.json`.

If the program is `CONTINUE` or `DEGRADED_CONTINUATION` and no committed successor handoff, explicit operator stop, or actual platform-enforced termination exists, FINAL IS FORBIDDEN. Immediately execute the next useful admissible unit instead. A stale earlier check cannot authorize final after additional work or state mutation.

## Public repository rule

Never write secrets or private source material here. Store only public-safe state or references.
