# AGENTS.md — Disposable Session Bootstrap Contract

## Prime directive

A ChatGPT session is disposable. Fresh durable GitHub state is authoritative.

## Mandatory startup

Read `state/NOW.json` first. If execution_status is PAUSED, do not start substantive work or rearm; preserve a safe checkpoint and report PAUSED. Recheck this flag before each write batch and scheduler mutation.

1. Read fresh `control/ACTIVE_CONTROLS.json`, then every artifact it currently marks mandatory on wake. Do not reuse a prior wake's policy merely because it was already loaded. This bootstrap document and the reservation prompt are survival/kernel pointers; fresh active machine controls are the dynamic policy authority, except explicit operator instructions and canonical/retired-canonical safety invariants.
2. Read `planning/PROGRAM.md` and fresh `state/NOW.json`. Follow NOW's project and work-spec references and reconstruct the full PROGRAM -> PROJECT -> WORK SPEC chain.
3. Read fresh `state/CURRENT.json`, `state/ACTIVITY.json`, `state/HANDOFF.json`, and `state/TURN_PLAN.json`.
4. Resolve north-star goal, active project, active work spec, program status, owner/authority epoch, latest checkpoint, exact next action, current activity evidence, and durable expected next due.
5. Apply `control/scheduler-fence.v1.json` before substantive side effects. A timing/generation mismatch is recovery work when a newer valid same-canonical continuation exists; reconcile forward and never roll schedule generation or authority backward.
6. Immediately after minimum fresh NOW/CURRENT/canonical/fence validation, persist a generation-matched `BOOT_STARTED` receipt in `state/STARTUP_ACK.json`. Do this before provisional arm, full restore, or substantive work; never infer the receipt from clock arrival or automation metadata alone.
7. Establish and verify a valid provisional successor/continuation path for THIS SAME canonical according to the active rolling lifecycle. Never create a replacement canonical merely to continue this actor.
8. Immediately after provisional continuation verification, persist generation-matched `REARM_VERIFIED` in `state/STARTUP_ACK.json`, including the verified provisional due. Only then continue full restore/authority/work.
9. If mandatory artifacts conflict, fail closed only for the disputed side effect, reconcile forward durably, and continue other safe authorized work. Never restore stale checkpoint/prompt policy over fresher durable policy.
10. Persist WORKING activity before or with the first substantive durable change after authority is obtained.
11. Persist one primary turn objective in `state/TURN_PLAN.json` before substantive execution. The turn objective MUST implement the active work spec; it must not silently invent a different project or strategy.
12. Read only task-specific files needed for the current objective and continue from durable state; never restart completed work merely because local chat context is missing.

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

- Startup: fence -> preserve newest verified continuation -> persist BOOT_STARTED -> arm the same canonical once at observed wake + exactly 11 minutes (660 seconds) for the normal 10-minute (600-second) envelope -> verify -> work. Do not restore the retired 13-minute (780-second) horizon, and do not use repeated 2-minute (120-second) rolling refresh as the normal strategy.
- Normal `CONTINUE` close: checkpoint -> set THIS SAME canonical's next due to the **ACTUAL END + exactly 1 minute (60 seconds)** (preserve seconds; no minute rounding) -> verify -> persist observed due. **Do not arm or synchronize Watchdog during normal close.** The same MAIN's recurring RRULE is its built-in cold fallback if a shifted wake is lost before bootstrap. A different MAIN delay requires fresh durable evidence/constraint plus an explicit exception reason; scheduler delivery jitter is measured separately.
- **Normal path invariant:** normal relay is `MAIN -> SAME MAIN at ACTUAL END + exactly 1 minute (60 seconds) -> MAIN`. During the active turn, arm provisional crash insurance once at observed WAKE + exactly 11 minutes (660 seconds) for the normal 10-minute (600-second) envelope. Normally do not mutate it mid-turn; extend the SAME canonical only if useful work or required close handling clearly threatens to cross that due. Prior live A/B evidence rejects repeated 2-minute (120-second) rolling refresh as the default because it produced overlap; the former 13-minute (780-second) horizon is also retired as unnecessarily long. If a shifted fast wake is lost, the SAME MAIN's natural recurring RRULE occurrence is the cold fallback. Startup Watchdog is disabled break-glass standby and is not required for correctness.
- **Hard close gate:** before a normal `STATUS=CONTINUE` final, re-read live MAIN metadata and prove same canonical, `is_enabled=true`, recurring RRULE, and DTSTART exactly equal to ACTUAL END + 1 minute (60 seconds). Persist that exact fast due consistently in CURRENT/ACTIVITY/HANDOFF and validate the non-WORKING close projection. If the live MAIN still points at the provisional due, normal final is forbidden; retry the fast rearm once, otherwise record degraded continuation instead of claiming a normal close.
- After the SAME MAIN fast continuation is verified, publish one consistent non-WORKING close projection: `CURRENT.run_state=HANDOFF_COMMITTED`; `ACTIVITY.status=HANDOFF_READY`, `active_run_id=null`, `handoff_ready=true`; and `HANDOFF.handoff_state=COMMITTED`. CURRENT, ACTIVITY, and HANDOFF must carry the same next due and predecessor epoch/owner.
- A successful checkpoint, test, CI pass, handoff, document, milestone, root, or subgoal is progress, not program completion.
- A future cold-rescue wake is safety coverage; it does not authorize a healthy current owner to stop.
- Fixed quarter-hour BYMINUTE rotation and quarter-cycle predecessor/successor choreography are retired semantics and MUST NOT be reconstructed from historical files or chat context.

## Sustained useful work

Useful-work utilization is a first-class objective.

- After continuation is verified and authority obtained, start substantive work immediately.
- While the program is non-terminal and useful admissible work exists, do not voluntarily idle or end.
- Execute a coherent primary objective rather than a single tiny packet when a larger safe objective exists.
- After every successful bounded step, check fresh mutable durable state and immediately select the next safe authorized step if ownership remains.
- Keep checkpoints current enough for cold resume without fabricating activity.
- Never pad, sleep, split trivial changes, or invent unrelated busywork to consume time or satisfy evidence cadence.
- Prefer units with safe checkpoint boundaries; as runtime exposure grows, shift toward smaller units rather than idling.
- **Normal nonterminal `CONTINUE` has a 600-second voluntary hard floor.** Before 600 observed elapsed seconds, immediately start the next clear low-risk checkpointable authorized unit. If the obvious unit is too large, decompose it. If it is wait-bound on CI/external evidence, choose an independent fallback/residual authorized unit.
- CI pending, packet/substep/checkpoint completion, secured continuation, or `nothing obvious` never authorize a voluntary pre-10-minute (pre-600-second) normal `CONTINUE` close.
- Earlier end is only STOP/PAUSE, durable program terminal, genuine BLOCKED/fail-closed authority/safety state with no safe authorized work, or platform-enforced termination; use the corresponding status/reason rather than a normal CONTINUE close.
- At >=600 elapsed seconds, do not start a new large unit. Finish only the smallest safe in-flight unit, checkpoint, hand off, and close. Treat ~720 seconds as a soft upper bound for normal operation; crossing it requires an actual in-flight safety/atomicity reason.

### Forward useful-work evidence capture

`state/WORK_EVIDENCE.json` is a strict acceptance ledger, not an automatic activity feed. A worker that creates qualifying substantive artifacts must keep the ledger current instead of assuming another process will discover the work later. Record actual observed boundaries and materially new artifact/test/design evidence; never infer missing time. Scheduler mutation, heartbeat-only state, waiting, timestamp-only changes, and evidence bookkeeping alone do not qualify as useful work.

## Primary turn objective

Before the first substantive action after authority acquisition, persist a primary objective with one concrete outcome, explicit acceptance criteria, checkpointable substeps, safe boundaries, and a related fallback continuation unit. Do not re-plan merely because an intermediate substep completed. Before 600 elapsed seconds, pull the next safe authorized unit; at/after 600 seconds, stop starting new large units and close after the smallest safe in-flight boundary.

## Utilization optimization loop

P0 acceptance is evidence-based and distinct from scheduler timing. Current gate: evaluation window 900 seconds; evidenced useful-work target >=840 seconds; unexplained internal durable-progress gap <=120 seconds; PASS requires at least 3 valid completed windows with rolling mean >=840 seconds. Do not infer missing timestamps or bridge unexplained intervals, and do not repeat a failed intervention without new evidence.

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

A non-terminal owner MUST continue until the single decision procedure in `control/run-continuation-gate.v1.json` authorizes bounded close. `CONTINUE`, `WORKING`, `DEGRADED_CONTINUATION`, checkpoint completion, CI success, document completion, root completion, plan completion, `nothing immediately obvious`, or waiting for a future cold-rescue wake are not permission to end. Canonical disable requires durable program terminal state or explicit operator STOP.

## Mandatory turn status

Every execution turn must leave a compact directly observable status record:

```text
[TURN STATUS]
START=<YYYY-MM-DD HH:MM:SS KST>
END=<YYYY-MM-DD HH:MM:SS KST>
DURATION=<Xm Ys or Xs>
STATUS=<CONTINUE|COMPLETE|BLOCKED|PAUSED>
```

Turn-duration guard:
- Normal `STATUS=CONTINUE` voluntary close with `DURATION<10m` is forbidden.
- An earlier end must be STOP/PAUSE, durable terminal, genuine BLOCKED/fail-closed authority/safety state with no safe authorized work, or platform-enforced termination, with corresponding durable evidence/status.
- At `DURATION>=10m`, do not start a new large unit. Finish only the smallest safe in-flight unit and close; ~12m is the normal soft ceiling.
- Use actual observed timestamps only; never backfill or fabricate time to improve utilization.

Semantics:
- `CONTINUE` — useful authorized work remains; durable resume target/continuation is preserved.
- `COMPLETE` — the active program is durably terminal; do not use merely because a packet, CI run, work spec, project, or local objective finished.
- `BLOCKED` — a genuine blocker prevents safe useful continuation and internal alternatives are exhausted.
- `PAUSED` — explicit operator pause/stop governs execution.

Persist equivalent durable evidence in `state/RUNS.jsonl` for every new bounded turn when repository write authority is available.

## Pre-final authorization gate

Immediately before emitting ANY normal user-visible final response, freshly read `state/CURRENT.json`, `state/HANDOFF.json`, `control/run-continuation-gate.v1.json`, and `state/NOW.json`. Apply `turn_decision` as the single close decision. A stale earlier check cannot authorize final after additional work or state mutation.

## Public repository rule

Never write secrets or private source material here. Store only public-safe state or references.

## Runnable selection and measured close

Use the existing TURN_PLAN, not another planning system. Before work, identify a primary item, a dependency-independent fallback, and a small residual-budget item within the active work spec/project. Mark a future observation WAITING; never select it as a currently runnable item. After every useful unit, select the next runnable item immediately. Refresh mutable authority/pause state before writes. A completed packet or secured next wake is not a close decision.

Observe wake/start/end separately. START-to-END is elapsed duration including control and close overhead, never automatically productive_substantive_seconds. Keep unknown useful time null. For every newly closed run, supply observed start/end, derived duration_seconds, turn_outcome, end_reason, program_status_at_end, and close_decision; validate against `tools/validate_run_records.py` semantics before normal close.

## Continuous measured relay

Run ongoing authorized work with no fixed turn/sample-count limit. Three eligible turns are an initial descriptive review only, never an automatic stop or proof of efficacy. Continue selecting the next authorized work-spec/project item after local completion while preserving bounded-turn safety and ownership rules. Explicit operator pause/STOP takes precedence; actual platform constraints and genuine blockers must be reported honestly, never bypassed or disguised with fabricated activity.

## Startup Watchdog

The startup Watchdog is disabled-by-default break-glass standby governed by `control/startup-watchdog.v1.json`. Normal continuity MUST work without it. MAIN writes BOOT_STARTED and REARM_VERIFIED for observability, but normal close does not arm or synchronize Watchdog. Nominal continuation is SAME MAIN at ACTUAL END + exactly 1 minute (60 seconds), meaning sixty seconds after observed END and never 60 minutes. Never reactivate retired MAIN canonicals.

## V5.5 durable unit chat trace

During the v5.5 canary, operator-visible progress messages are mandatory observability events, not turn boundaries.

- After provisional SAME MAIN rearm is live-verified and durably recorded, emit one compact schedule message naming the verified due.
- For each bounded substantive unit, record observed unit START, END, derived DURATION, and artifact-backed work evidence first. Only then emit one compact `완료: ... (duration ...)` message.
- Do not emit a completion message for a mere read, plan, wait, retry without completion, scheduler mutation alone, or unpersisted partial work.
- After emitting a unit trace, immediately continue same-wake work selection while normal nonterminal CONTINUE elapsed is below 600 seconds. The message does not authorize final response or voluntary close.
- After SAME MAIN ACTUAL END + exactly 1 minute (60 seconds) live verification and consistent durable close projection, emit one final compact next-due message, then the normal TURN STATUS footer.


## Time-unit safety

Never use bare numeric timing deltas in human-readable control text. Write `1 minute (60 seconds)`, not `+60`; `3 minutes (180 seconds)`, not `NOW+180`; `10 minutes (600 seconds)`, not `600 floor`; and `11 minutes (660 seconds)`, not `+660`. Machine fields ending in `_seconds` are seconds by schema. `RRULE:FREQ=HOURLY` describes recurrence only and must never be used to reinterpret an explicit second offset.
