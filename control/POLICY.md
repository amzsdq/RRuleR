# RRuleR Control Policy

## Authority surfaces

- `control/POLICY.md` — human-readable architectural policy.
- `control/relay-policy.v1.json` — machine-readable relay policy.
- `control/scheduler-fence.v1.json` — scheduler generation/fencing policy.
- `control/rolling-rrule-lifecycle.v1.json` — active rolling same-canonical lifecycle.
- `state/CURRENT.json` — current program/root projection and exact continuation state.
- `state/ACTIVITY.json` — current observable run/activity heartbeat.

Machine-readable active controls and fresh durable state govern execution. If prose disagrees, fail closed only for the disputed side effect, reconcile forward, and continue safe useful work.

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

## Authority and continuous work

`state/CURRENT.json` identifies the current owner and monotonic `authority_epoch`. A stale run may not roll authority or schedule generation backward. Scheduler mismatch is recovery work when a newer valid same-canonical continuation exists.

After continuation is verified, obtain/confirm authority, persist WORKING activity, and execute useful admissible bounded work continuously. Document, checkpoint, CI, milestone, root, or schedule boundaries do not authorize voluntary termination. Checkpoint frequently enough for cold recovery without manufacturing heartbeat-only evidence.

## Active scheduler policy

The active mechanism is `RRULE_HOURLY_ROLLING_COMPLETION_RELATIVE` on one same canonical automation.

Startup order:

```text
FRESH DURABLE STATE
 -> STALE-WAKE / GENERATION FENCE
 -> PRESERVE NEWEST VERIFIED SAME-CANONICAL CONTINUATION
 -> PROVISIONAL ARM + VERIFY
 -> AUTHORITY / ACTIVITY RECONCILIATION
 -> USEFUL WORK
```

Normal close order:

```text
LATEST CHECKPOINT
 -> FINAL REARM SAME CANONICAL TO COMPLETION-RELATIVE FAST CONTINUATION
 -> VERIFY ENABLED + FUTURE DUE
 -> PERSIST VERIFIED DUE
```

The provisional rescue horizon and final close offset are tunables declared by active machine controls; they are not utilization acceptance thresholds. Never create a replacement canonical merely to continue this actor and never convert the canonical to one-shot for normal continuation.

Fixed quarter-hour BYMINUTE rotation and predecessor/successor quarter-cycle choreography are retired scheduler semantics. Historical evidence produced under that mechanism remains history, not an active instruction.

## Handoff and recovery

The rolling cold successor reconstructs from GitHub. A future wake existing by itself does not authorize a healthy current owner to stop. Normal run end requires an allowlisted condition from `control/run-continuation-gate.v1.json`, including committed successor handoff, explicit operator stop, or platform-enforced termination. Program end additionally requires durable terminal evidence such as `PROGRAM_COMPLETE` or proven `BLOCKED_EXTERNAL`.

If a wake is stale relative to the newest verified schedule generation, recover forward. Do not restore an older DTSTART, prompt, title, authority epoch, or checkpoint. Ambiguous irreversible side effects must reconcile before replay.

## Primary turn objective

After rearm verification and authority acquisition, persist one coherent primary objective sized for useful sustained work. Required fields are maintained in `state/TURN_PLAN.json`: objective id, expected useful duration, acceptance criteria, checkpointable substeps, current substep, safe handoff boundary, and early-finish fallback.

Prefer meaningful medium-sized work over unrelated microtasks. If the objective finishes early and useful work remains, execute the declared fallback or form a related continuation objective. Do not pad with filler solely to manufacture duration.

## Utilization evidence and P0 acceptance

P0 is sustained evidenced useful-work coverage. The current acceptance target is:

- intended evaluation window: 900 seconds;
- evidenced useful-work target: at least 840 seconds;
- no unexplained internal durable-progress gap greater than 120 seconds;
- at least 3 valid completed windows with rolling mean at least 840 seconds.

The active rolling scheduler may use a shorter provisional rescue planning horizon. That horizon is operational safety, not permission to redefine the 840/900 acceptance gate.

Substantive evidence follows `control/evidence-policy.v1.json`. Heartbeat-only, timestamp-only, waiting, scheduler mutation alone, CI polling without a new result, reformatting, and duplicate checkpoint prose do not independently prove useful work. Missing timestamps or unexplained intervals must remain unknown rather than inferred.

Each valid completed sample follows:

```text
MEASURE -> CLASSIFY -> CORRECT ONE DOMINANT CAUSE -> RETEST
```

Do not repeat a failed intervention without new evidence.

## Runtime-safe continuity

Keep work checkpointable. As runtime exposure grows, prefer smaller safe units rather than voluntarily idling. A cold-rescue wake is a safety mechanism, not authority for a healthy owner to terminate. If the future wake becomes too near while useful authorized work remains and active lifecycle policy permits, refresh it before collision.

## Program goals and autonomous R&D authority

The program goal is to evolve RRuleR into a production-oriented autonomous agent runtime/control plane competitive with commercial agent SaaS for long-running work, including utilization, durable continuation, disposable-session recovery, delegation, tool reach, observability, completion verification, security/governance, and reproducibility.

Within `amzsdq/RRuleR`, workers may autonomously inspect, create, edit, refactor, and remove reversible relevant repository artifacts; build tests, schemas, policies, experiments, docs, workflows, checkpoints, and measurement infrastructure; research prior art when needed; replace falsified interventions; and select the next bounded objective by expected effect on program goals.

This authority does not waive platform/security constraints, public-repository secret rules, irreversible-side-effect reconciliation, or approval requirements for consequential actions outside RRuleR.

## Public-safe persistence

RRuleR is public-safe durable state. Never persist credentials, cookies, private files, private message content, private-repository material, or personal data.

## Pre-final authorization gate

Immediately before any normal user-visible final response, freshly read `state/CURRENT.json`, `state/HANDOFF.json`, and `control/run-continuation-gate.v1.json`. If the program is non-terminal and no allowlisted run-end condition exists, final response and voluntary run end are forbidden; select and execute the next useful admissible unit instead.
