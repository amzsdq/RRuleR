# RRuleR Control Policy

## Authority surfaces

- `control/POLICY.md` — human-readable architectural policy.
- `control/relay-policy.v1.json` — machine-readable relay policy.
- `control/scheduler-fence.v1.json` — scheduler generation/fencing policy.
- `control/rolling-rrule-lifecycle.v1.json` — active rolling same-canonical lifecycle.
- `state/CURRENT.json` — current program/root projection and exact continuation state.
- `state/ACTIVITY.json` — current observable run/activity heartbeat.

Machine-readable active controls and fresh durable state govern execution. If prose disagrees, fail closed only for the disputed side effect, reconcile forward, and continue safe useful work.

Every wake must perform a fresh policy sync from `control/ACTIVE_CONTROLS.json` and its currently mandatory artifacts before substantive work. Automation/bootstrap text is a survival kernel and pointer, not a cached substitute for fresh dynamic policy. For a normal nonterminal `CONTINUE` turn, 600 observed elapsed seconds is the minimum voluntary duration. Before 600 seconds, chain or decompose authorized work; CI pending, local completion, checkpointing, or a secured next wake do not authorize early close. Earlier termination must be represented truthfully as STOP/PAUSE, program terminal, genuine BLOCKED/fail-closed state, or platform-enforced termination.

## Architectural axioms

1. Persistence belongs to GitHub.
2. Intelligence belongs to disposable ChatGPT sessions.
3. No session is authoritative; durable state is.
4. Automation is a wake mechanism, not a state store.
5. Delivery is not work completion.
6. Checkpoint before authoritative advancement.
7. At-least-once delivery is acceptable; duplicate substantive execution is not.
8. Ambiguous irreversible side effects reconcile before replay.
9. Authority must be explicit and fenced.
10. Completion requires evidence, not worker prose.
11. Useful-work utilization is a first-class operating objective.
12. Scheduled time is not a voluntary stop signal.
13. Root completion is not automatically program completion.
14. A non-terminal program must retain a verified recoverable continuation path.
15. Predictive wake overlap never grants dual substantive authority.

## Authority and continuous work

`state/CURRENT.json` identifies the current owner and monotonic `authority_epoch`. A stale run may not roll authority or schedule generation backward. Scheduler mismatch is recovery work when a newer valid same-canonical continuation exists.

After continuation is verified, obtain/confirm authority, persist WORKING activity, and execute useful admissible bounded work continuously. Document, checkpoint, CI, milestone, root, or schedule boundaries do not authorize voluntary termination. Checkpoint frequently enough for cold recovery without manufacturing heartbeat-only evidence.

## Active scheduler policy

The active mechanism is one same-canonical hourly RRULE under the rolling lifecycle. For a normal ~600-second nonterminal turn, arm the SAME MAIN once at observed wake/arm reference +660 seconds, normally leave it untouched during work, and replace it at normal close with exact observed END+60. Extend the SAME MAIN once before collision only when useful authorized work or required close handling clearly threatens the verified provisional due. The natural hourly recurrence is the built-in cold fallback. Repeated +2-minute rolling refresh and the former +780-second provisional are retired normal strategies. `UTIL-EXP-018` predictive prearm is rolled back and is historical evidence, not active authority.

Startup order:

```text
FRESH DURABLE STATE
 -> STALE-WAKE / GENERATION FENCE
 -> PERSIST GENERATION-MATCHED BOOT_STARTED
 -> PROVISIONAL SAME MAIN +660s ARM + LIVE VERIFY
 -> PERSIST REARM_VERIFIED
 -> AUTHORITY / ACTIVITY RECONCILIATION
 -> USEFUL WORK
```

Normal close:

```text
LATEST CHECKPOINT
 -> OBSERVE ACTUAL END
 -> SHIFT SAME MAIN RECURRING DTSTART TO END+60 EXACTLY
 -> LIVE VERIFY SAME CANONICAL + ENABLED + RECURRENCE + EXACT DTSTART
 -> PERSIST IDENTICAL FAST DUE TO CURRENT / ACTIVITY / HANDOFF
 -> VALIDATE NON-WORKING CLOSE PROJECTION
```

Historical predictive-prearm and short-rolling canaries remain evidence only. They may not restore retired scheduler values or dual substantive authority.

The provisional rescue horizon and final-close offset are operational safety parameters, not utilization acceptance thresholds. Never create a replacement canonical merely to continue this actor and never convert the canonical to one-shot for normal continuation.

Fixed quarter-hour BYMINUTE rotation and predecessor/successor quarter-cycle choreography are retired scheduler semantics. Historical evidence remains history, not active instruction.

## Handoff and recovery

A future wake existing by itself does not authorize a healthy current owner to stop. If a wake is stale relative to the newest verified schedule generation, recover forward. Do not restore an older DTSTART, prompt, title, authority epoch, or checkpoint. Ambiguous irreversible side effects must reconcile before replay.

## Primary turn objective

After rearm verification and authority acquisition, persist one coherent primary objective sized for useful sustained work. Required fields are maintained in `state/TURN_PLAN.json`: objective id, expected useful duration, acceptance criteria, checkpointable substeps, current substep, safe handoff boundary, and early-finish fallback.

Prefer meaningful medium-sized work over unrelated microtasks. If the objective finishes early and useful work remains, execute the declared fallback or form a related continuation objective. Do not pad with filler solely to manufacture duration.

## Utilization evidence and P0 acceptance

P0 is sustained evidenced useful-work coverage:

- fixed evaluation window: 900 seconds;
- evidenced useful-work target: at least 840 seconds;
- no unexplained internal durable-progress gap greater than 120 seconds;
- at least 3 consecutive valid completed windows with selected rolling mean at least 840 seconds.

The bounded turn and provisional rescue horizons are operational safety/execution parameters, not permission to redefine the 840/900 acceptance gate.

Substantive evidence follows `control/evidence-policy.v1.json`. Heartbeat-only, timestamp-only, waiting, scheduler mutation alone, CI polling without a new result, reformatting, and duplicate checkpoint prose do not independently prove useful work. Missing timestamps or unexplained intervals remain unknown rather than inferred.

Each valid completed sample follows:

```text
MEASURE -> CLASSIFY -> CORRECT ONE DOMINANT CAUSE -> RETEST
```

Do not repeat a failed intervention without new evidence.

## Runtime-safe continuity

Keep work checkpointable. As runtime exposure grows, prefer smaller safe units rather than voluntarily idling. A cold-rescue wake is a safety mechanism, not authority for a healthy owner to terminate. Watchdog remains disabled break-glass standby and is not a normal correctness dependency.

## Program goals and autonomous R&D authority

The program goal is to evolve RRuleR into a production-oriented autonomous agent runtime/control plane competitive with commercial agent SaaS for long-running work, including utilization, durable continuation, disposable-session recovery, delegation, tool reach, observability, completion verification, security/governance, and reproducibility.

Within `amzsdq/RRuleR`, workers may autonomously inspect, create, edit, refactor, and remove reversible relevant repository artifacts; build tests, schemas, policies, experiments, docs, workflows, checkpoints, and measurement infrastructure; research prior art when needed; replace falsified interventions; and select the next bounded objective by expected effect on program goals.

This authority does not waive platform/security constraints, public-repository secret rules, irreversible-side-effect reconciliation, or approval requirements for consequential actions outside RRuleR.

## Public-safe persistence

RRuleR is public-safe durable state. Never persist credentials, cookies, private files, private message content, private-repository material, or personal data.

## Pre-final authorization gate

Immediately before any normal user-visible final response, freshly read `state/CURRENT.json`, `state/HANDOFF.json`, and `control/run-continuation-gate.v1.json`. If the program is non-terminal and no allowlisted run-end condition exists, final response and voluntary run end are forbidden; select and execute the next useful admissible unit instead.

## Durable unit chat trace canary

V5.5 adds direct operator-visible observability without changing close authority. After the SAME MAIN provisional schedule is live-verified and durably recorded, emit one compact schedule trace showing the verified due. Each bounded substantive unit may emit exactly one compact completion trace only after its observed START/END/DURATION and artifact-backed work evidence are durably persisted. The trace is evidence of a persisted unit boundary, not a task boundary, handoff, or permission to stop. While a normal nonterminal CONTINUE turn is below 600 observed elapsed seconds, immediately select and execute the next safe authorized unit after each trace. Mere reads, plans, waits, retries without completion, scheduler mutation alone, and unpersisted partial work must not produce completion traces. After normal close is live-verified on the SAME MAIN at exact observed END+60 and the durable close projection agrees, emit one compact final next-due trace.
