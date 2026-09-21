# AGENTS.md — Disposable Session Bootstrap Contract

## Prime directive

A ChatGPT session is disposable. Fresh durable GitHub state is authoritative.

## Mandatory startup

Read `state/NOW.json` first. If execution_status is PAUSED, do not start substantive work or rearm; preserve a safe checkpoint and report PAUSED. Recheck this flag before each write batch and scheduler mutation.


1. Read `control/ACTIVE_CONTROLS.json`, then all artifacts it marks mandatory on wake.
2. Read `planning/PROGRAM.md` and `state/NOW.json`. Follow NOW's project and work-spec references and reconstruct the full PROGRAM -> PROJECT -> WORK SPEC chain.
3. Read `state/CURRENT.json`, `state/ACTIVITY.json`, `state/HANDOFF.json`, and `state/TURN_PLAN.json`.
4. Resolve north-star goal, active project, active work spec, program status, owner/authority epoch, latest checkpoint, exact next action, current activity evidence, and durable expected next due.
5. Apply `control/scheduler-fence.v1.json` before substantive side effects. A timing/generation mismatch is recovery work when a newer valid same-canonical continuation exists; reconcile forward and never roll schedule generation or authority backward.
6. Before substantive work, establish and verify a valid successor/continuation path for THIS SAME canonical according to the active rolling lifecycle. Never create a replacement canonical merely to continue this actor.
7. Persist WORKING activity before or with the first substantive durable change after authority is obtained.
8. Persist one primary turn objective in `state/TURN_PLAN.json` before substantive execution. The turn objective MUST implement the active work spec; it must not silently invent a different project or strategy.
9. Read only task-specific files needed for the current objective.
10. Continue from durable state; never restart completed work merely because local chat context is missing.

## Planning spine and anti-local-optimization

The canonical planning hierarchy is:

```text
planning/PROGRAM.md
 -> planning/projects/<project>.md
 -> planning/work-specs/<work-spec>.md
 -> state/NOW.json
 -> state/TURN_PLAN.json
```

- `PROGRAM` defines the north-star goal and ordered project roadmap.
- A `PROJECT` is an outcome-oriented phase with explicit exit criteria.
- A `WORK SPEC` is the implementable unit with scope and acceptance checklist.
- `NOW` is a pointer to the active chain and exact resume target.
- `TURN_PLAN` is only the bounded execution plan for the current turn.

Before starting a substantive unit, be able to state which work-spec acceptance item it advances. Do not execute work merely because it is nearby, technically interesting, or already open in context.

Rules, controls, tests, workflows, and process are instruments. Add, strengthen, modify, consolidate, or retire them according to expected net contribution to the active project and program goals. Fewer rules are not inherently better; more rules are not inherently safer.

When progress changes, update the work-spec acceptance/evidence first, then project/program roll-up if needed, then `state/NOW.json`, and only then the next turn plan.

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
- A CONTINUE turn has a **short-turn diagnostic threshold of 8 elapsed minutes** unless a real stop condition applies. Finishing one experiment setup, scheduler mutation, measurement capture, CI check, or bounded substep before 8 minutes is not permission to end.
- If the current substep becomes wait-bound, immediately switch to another safe authorized runnable item from the same work spec/project rather than ending the turn. Waiting for a future observation is not a blocker while other useful work exists.
- A short CONTINUE turn (<8 minutes) is an exception that MUST record a concrete `short_turn_reason` and the exhausted alternatives. Acceptable reasons are limited to: actual platform-enforced termination, explicit operator intervention, authority/fencing failure closed, or no safe runnable work anywhere in the active work spec/project after an explicit scan.

### Forward useful-work evidence capture

`state/WORK_EVIDENCE.json` is a strict acceptance ledger, not an automatic activity feed. A worker that creates qualifying substantive artifacts must keep the ledger current instead of assuming another process will discover the work later.

At a natural observed boundary after materially new substantive work:

1. identify the actual observed start and end boundaries; never infer missing time;
2. identify the materially new artifact/commit/test/design evidence produced in that interval;
3. append a non-overlapping `SUBSTANTIVE_ACCEPTED` record using `tools/append_work_evidence.py` semantics (or an equivalent validated write when direct execution is unavailable);
4. validate the resulting ledger with `tools/validate_work_evidence.py` semantics;
5. if either boundary is unknown, do not manufacture a record—leave the interval unknown and durably classify the measurement gap instead.

Scheduler mutation, heartbeat-only state, waiting, timestamp-only changes, and evidence bookkeeping alone do not qualify as useful work. Evidence capture must follow useful work; it must never create work merely to improve the metric.

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

A non-terminal owner MUST continue until the single decision procedure in control/run-continuation-gate.v1.json authorizes bounded close or a documented exception.

`CONTINUE`, `WORKING`, `DEGRADED_CONTINUATION`, checkpoint completion, CI success, document completion, root completion, plan completion, "nothing immediately obvious", or waiting for a future cold-rescue wake are not permission to end.

Only an allowlisted condition in `control/run-continuation-gate.v1.json` may authorize run end. Canonical disable requires durable program terminal state or explicit operator STOP.

## Mandatory turn status

Every execution turn must leave a compact, directly observable status record.

At actual substantive turn start, capture the real start timestamp. At turn close, capture the real end timestamp and derive duration from the two observed timestamps.

Normal user-visible footer:

```text
[TURN STATUS]
START=<YYYY-MM-DD HH:MM:SS KST>
END=<YYYY-MM-DD HH:MM:SS KST>
DURATION=<Xm Ys or Xs>
STATUS=<CONTINUE|COMPLETE|BLOCKED|PAUSED>
```

Short-turn guard:
- `STATUS=CONTINUE` with `DURATION<8m` is presumptively a utilization failure.
- Before closing such a turn, scan the active work spec/project for the next safe runnable unit and continue working if one exists.
- If a short turn is unavoidable, persist `short_turn_reason` and `alternatives_checked` in the durable run record; do not use vague reasons such as "experiment armed", "waiting for next wake", "CI pending", or "nothing obvious".

Semantics:
- `CONTINUE` — useful authorized work remains; durable resume target/continuation is preserved.
- `COMPLETE` — the active program is durably terminal; do not use merely because a packet, CI run, work spec, project, or local objective finished.
- `BLOCKED` — a genuine blocker prevents safe useful continuation and internal alternatives are exhausted.
- `PAUSED` — explicit operator pause/stop governs execution.

Use actual observed timestamps only; never backfill or fabricate time to improve utilization.

Persist equivalent durable evidence in `state/RUNS.jsonl` for every new bounded turn when repository write authority is available. New records should include `run_started_at`, `run_ended_at`, derived `duration_seconds`, and `turn_outcome`, plus existing detailed classification/evidence fields as applicable.

The compact footer is for operator readability. Detailed machine evidence remains in GitHub.

## Pre-final authorization gate

Immediately before emitting ANY normal user-visible final response, freshly read:

- `state/CURRENT.json`;
- `state/HANDOFF.json`;
- `control/run-continuation-gate.v1.json`.

Apply `turn_decision` in `control/run-continuation-gate.v1.json` as the single close decision. Verified continuation permits final only after its bounded-close requirements are satisfied. An operator pause in `state/NOW.json` overrides continuation: checkpoint, do not rearm, and report PAUSED. A stale earlier check cannot authorize final after additional work or state mutation.

## Public repository rule

Never write secrets or private source material here. Store only public-safe state or references.

## Runnable selection and measured close (v4)

Use the existing TURN_PLAN, not another planning system. Before work, identify a primary item, a dependency-independent fallback, and a small residual-budget item within the active work spec/project. Each item must name its target artifact, acceptance result, dependencies, authority/conflict domain, estimated duration, and safe checkpoint. Mark a future observation WAITING; never select it as a currently runnable item. If a queue item is already complete, skip it and choose the next acceptance item.

After every useful unit, select the next runnable item immediately. Refresh mutable authority/pause state before writes; immutable policy need not be reloaded after every tiny step when its version is unchanged. A completed packet or a secured next wake is not a close decision.

Observe wake/start/end separately. START-to-END is elapsed duration including control and close overhead, never automatically productive_substantive_seconds. Keep unknown useful time null. Start closing in time to respect the 10-minute work envelope and the existing platform safety limit; never reset the safety clock after slow bootstrap.

For every newly closed run, supply observed start/end, derived duration_seconds, turn_outcome, end_reason, program_status_at_end, and close_decision. Run `python tools/validate_run_records.py state/RUNS.jsonl` before normal close. This checks records written after the v4 migration boundary; historical invalid records remain unchanged and visible. A validator failure is a repair task, not permission to fabricate time or exception evidence.

## Continuous measured relay (operator directive)

Run ongoing authorized work with no fixed turn/sample-count limit. Three eligible turns are an initial descriptive review only, never an automatic stop or proof of efficacy. Continue selecting the next authorized work-spec/project item after local completion, while preserving the existing bounded-turn safety and ownership rules. Explicit operator pause/STOP takes precedence; actual platform constraints and genuine blockers must be reported honestly, never bypassed or disguised with fabricated activity.

The existing RRuleR actor performs routine recording, review, bottleneck diagnosis and correction. Do not create a separate reviewer for routine measurement. Keep per-turn raw records and artifact-backed useful intervals; maintain latest-ten eligible-turn and lifetime summaries plus unknown/invalid counts. Normal turns require only incremental review.

Follow the single detailed continuous review procedure in `planning/evidence/TURN-CLOSE-V4-RETEST.md`, section “Continuous relay directive”. Trigger targeted diagnosis for unexcused short closes, invalid/missing records, conflicting timestamps, duplicate effects or missing continuation; investigate sustained performance degradation only with comparable valid observations. Then correct one evidenced cause and compare subsequent samples. Preserve exclusions and unknown time.

A completed initial review, successful repair, CI pass or accumulated sample count does not make the ongoing program terminal.
