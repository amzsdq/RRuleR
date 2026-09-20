# RRuleR Control Policy

## Authority surfaces

- `control/POLICY.md` — human-readable architectural policy.
- `control/relay-policy.v1.json` — machine-readable relay policy for scheduler/utilization/handoff behavior.
- `state/CURRENT.json` — current program/root projection and exact continuation state.
- `state/ACTIVITY.json` — current observable run/activity heartbeat.

If prose and machine-readable relay fields disagree, fail closed and reconcile them before relying on the disputed behavior.

## Architectural axioms

1. **Persistence belongs to GitHub.**
2. **Intelligence belongs to disposable ChatGPT sessions.**
3. **No session is authoritative; durable state is.**
4. **Automation is a wake mechanism, not a state store.**
5. **Delivery is not work completion.**
6. **Checkpoint before authoritative advancement.**
7. **At-least-once delivery is acceptable; duplicate substantive execution is not.**
8. **Ambiguous irreversible side effects reconcile before replay.**
9. **Authority must be explicit and fenced.**
10. **Completion requires evidence, not worker prose.**
11. **Useful-work utilization is a first-class operating objective.**
12. **Scheduled time is not a voluntary stop signal.**
13. **Root completion is not automatically program completion.**
14. **An active program must not voluntarily create an idle gap when useful admissible work exists.**

## Authority

`state/CURRENT.json` identifies current owner and monotonic `authority_epoch`.

A stale run may not roll authority backward or replay conflicting side effects. Scheduler-time mismatch alone is not a stop condition: if the live canonical continuation is verifiable, reconcile scheduler/owner/handoff metadata forward to the newest valid continuation and resume under a fresh authority claim.

## Continuous work

After the next wake is verified:

- mark durable activity WORKING;
- begin substantive work immediately;
- keep selecting useful admissible bounded work units while the program is non-terminal;
- do not stop at document, checkpoint, milestone, phase, root, or schedule boundaries;
- checkpoint frequently enough for recovery without treating checkpoint creation as a yield;
- on root completion, persist root terminal evidence, select the next materially useful root if one exists, persist it, and continue;
- never generate busywork solely to satisfy utilization;
- only successor observation, verified program completion, explicit operator stop, a proven external blocker with internal alternatives exhausted, or platform-enforced termination authorizes normal relinquishment.

## Handoff

Preferred handoff:

```text
successor wake already armed
        ↓
predecessor continues useful work
        ↓
successor ACTUALLY observed
        ↓
predecessor stops starting new units
        ↓
finish current smallest safe work unit
        ↓
persist checkpoint + activity + duration + evidence + exact next action
        ↓
handoff status / predecessor end
        ↓
successor reconstructs from GitHub and resumes
```

Scheduled recurrence arrival without successor evidence is not a handoff trigger.

If same-canonical overlap is unsupported, correctness falls back to durable reconstruction, but the predecessor must not voluntarily introduce an idle period before platform-enforced termination.

## Scheduler policy

The scheduler is a replaceable wake adapter. The active scheduling design is the completion-relative rolling lifecycle described in `docs/ROLLING_RRULE_BATON_SPEC.md` and `control/rolling-rrule-lifecycle.v1.json`.

Operational semantics:

- validate the minimum durable fence before relying on a wake;
- establish and verify a provisional future continuation before full restore/substantive work;
- perform sustained checkpointable work;
- checkpoint and prepare the next bounded successor packet;
- on normal close, move the same recurring continuation to a short completion-relative delay and verify it;
- fixed quarter-hour slots are historical compatibility evidence, not the active target.

Architectural invariant:

> A live non-terminal program that requires continuation must have a verified recoverable continuation path, and normal successful work should not intentionally wait for a fixed wall-clock phase.

## Activity evidence and UI

The ChatGPT composer/stop-button state is not authoritative durable state, but it is a useful operator-facing liveness signal.

- Stop button: usually means the foreground turn is still generating.
- Send button / idle composer: means that foreground turn ended, but does not rule out a separate scheduled run.
- To align behavior with the operator's practical observation, an active predecessor does not voluntarily send its normal final response while it still owns work and no successor has been observed.
- `state/ACTIVITY.json` is the durable corroborating signal. Idle UI plus stale activity and no successor evidence is a utilization incident.

## Failure semantics

- Recurrence phase-update failure while a prior valid RRULE remains alive is `DEGRADED_CONTINUATION`, not immediate death.
- A surviving recurrence may provide a slower recovery opportunity.
- Disabled/deleted/missing automation is not rescued by that fallback.
- Repeated blind retry without a new hypothesis or reconciliation evidence is forbidden.

## Public-safe persistence

RRuleR must remain safe to expose publicly. Never persist credentials, cookies, private files, private message content, private-repository material, or personal data.

## Hard no-self-termination invariant

A non-terminal owner MUST NOT voluntarily end its turn.

- If program state is not `PROGRAM_COMPLETE` or `BLOCKED_EXTERNAL`, emitting a normal final response is forbidden unless a successor has actually been observed and the durable handoff has been committed.
- `CONTINUE`, `WORKING`, `DEGRADED_CONTINUATION`, checkpoint completion, CI pending/success, document completion, root completion, or "nothing immediately obvious" are NOT permission to end.
- After every bounded unit, re-read durable state, select the next useful admissible unit, and execute it in the SAME turn.
- If no next unit is obvious, the next unit is to inspect durable state/evidence for the highest-value unresolved invariant or validation gap; this is not a reason to idle.
- Only `PROGRAM_COMPLETE`, proven `BLOCKED_EXTERNAL`, committed successor handoff, explicit operator stop, or platform-enforced termination may end an active turn.


## Rolling work-packet protocol

Each valid wake executes a predecessor/successor baton lifecycle.

- A predecessor leaves a bounded next packet linked to the latest durable checkpoint.
- A successor validates that packet against fresh durable state before using it.
- The packet normally targets about 10 minutes of useful work, but the duration is a planning horizon rather than a stop timer.
- The successor establishes its provisional recovery continuation before full restore/work.
- Finishing the packet early is not a reason to idle; continue useful related work or prepare the next packet.
- Normal close checkpoints first, plans/persists the next packet, then establishes the short completion-relative continuation.
- If the active invocation dies, the provisional continuation is the cold-rescue path.
- The reservation's packet capsule is a cache only; GitHub durable state remains authoritative.

Canonical order:

```text
WAKE
  -> MINIMUM FENCE + PACKET VALIDATION
  -> PROVISIONAL CONTINUATION + VERIFY
  -> RESTORE
  -> WORK
  -> CHECKPOINT
  -> PLAN + PERSIST NEXT PACKET
  -> COMPLETION-RELATIVE CONTINUATION + VERIFY
  -> RETURN
```

## Utilization measurement and improvement

The active optimization target is sustained evidenced useful-work coverage with minimal normal continuation gaps. The current packet target is approximately 10 minutes followed by a short completion-relative continuation, while recovery latency is measured separately.

A completed run must persist enough timestamps to distinguish work from dead time. The minimum derived fields are:
- observed_useful_span_seconds: last meaningful durable progress minus substantive_work_started_at;
- dead_tail_seconds: successor/handoff boundary minus last meaningful durable progress, when both timestamps are known;
- scheduler_or_handoff_overhead_seconds: known non-substantive startup/handoff overhead;
- measurement_valid: false when required boundaries are missing rather than inventing values.

Every completed valid observation window is an experiment:
1. measure useful coverage, normal continuation gap, startup overhead, and recovery latency separately;
2. classify the dominant loss source;
3. choose one concrete correction;
4. persist it for the next worker;
5. retest without inventing missing timestamps.

One good window does not complete the optimization program. Sustained evidence across multiple windows is required.


### Runtime-safe rolling cadence

The operational target is approximately 10 minutes of useful work plus a short normal continuation delay, protected by a longer provisional rescue horizon.

- The work target is not a hard cutoff.
- Prefer checkpointable units as the provisional deadline approaches.
- If useful work safely overruns the initial target, extend the provisional future occurrence before collision.
- Normal close computes the next due from actual completion, not from a fixed quarter boundary.
- Abrupt-loss recovery latency is measured independently from the normal completion-relative delay.

## Utilization continuity precedence

For RRULER-UTILIZATION, the operator's priority order is:

1. preserve a verified future continuation;
2. keep useful work running;
3. checkpoint and leave a high-quality successor packet;
4. minimize the normal completion-relative gap;
5. repair internal scheduler/baton bookkeeping without yielding when safe.

Never restore an older schedule generation or authority epoch.


## Primary work packet

A worker should not begin by greedily selecting the first microtask. After provisional continuation and authority validation, it should use the fresh successor packet or commit one coherent packet sized for the available work envelope.

Required planning fields are defined by `docs/ROLLING_RRULE_BATON_SPEC.md`. The normal target is about 600 useful seconds; duration is tunable and must follow the work shape rather than force filler.

Execution rule:
- follow the packet until acceptance, invalidation, genuine blocker, or platform boundary;
- checkpoint meaningful progress;
- if the packet finishes early and useful work remains, continue related bounded work and prepare the successor packet;
- before normal close, persist the exact next packet for the next cold worker.

## Program goals and autonomous R&D authority

The operator has established two durable goals for RRuleR.

### Program goal — commercial-agent-SaaS competitiveness

Evolve RRuleR into a production-oriented autonomous agent runtime/control plane that can credibly compete with commercial agent SaaS on the dimensions that matter for long-running autonomous work:

- sustained useful-work utilization;
- durable continuation and background operation;
- recovery from disposable-session failure;
- delegation / multi-agent orchestration;
- tool and environment reach;
- observability, auditability, and operator control;
- predictable completion verification;
- security / governance appropriate to a public-safe control plane;
- low-friction setup and reproducibility.

Competitive parity is evidence-based. Marketing claims or architecture presence alone do not count.

### P0 goal — sustained utilization

Until the utilization acceptance gate passes, sustained useful work is P0.

Acceptance target:
- intended turn window: 900 seconds;
- evidenced useful-work target: >=840 seconds;
- no unexplained internal durable-progress gap >120 seconds;
- fast successor-triggered baton handoff;
- minimum 3 valid completed turns with rolling mean >=840 seconds;
- after initial PASS, utilization becomes a regression SLO and must remain protected while other capabilities advance.

### Autonomous R&D authority inside RRuleR

Within `amzsdq/RRuleR`, workers may autonomously:
- inspect, create, edit, refactor, and remove repo files when reversible and relevant;
- create/update tests, schemas, policies, experiments, docs, workflows, checkpoints, and measurement infrastructure;
- perform web research and compare external prior art when the current intervention fails or architecture is uncertain;
- replace a failed intervention with a materially different hypothesis without waiting for operator approval;
- select the next bounded objective by highest expected effect on the program goals;
- use negative results as durable evidence and revise architecture rather than protecting prior ideas.

This authority does not waive platform/security constraints, public-repository secret rules, or approval requirements for consequential actions outside RRuleR.

### Failure-driven improvement loop

A failed turn or failed intervention MUST trigger:

```text
MEASURE FAILURE
 -> LOCALIZE ROOT CAUSE
 -> CHECK WHETHER CURRENT HYPOTHESIS WAS FALSIFIED
 -> SEARCH INTERNAL EVIDENCE
 -> IF NEEDED SEARCH EXTERNAL PRIOR ART / COMPETITOR PRACTICE
 -> GENERATE >=2 PLAUSIBLE CORRECTIONS WHEN UNCERTAIN
 -> SELECT HIGHEST EXPECTED-EFFECT CORRECTION
 -> IMPLEMENT
 -> VALIDATE
 -> RETEST UNDER LIVE RELAY
```

Repeating the same failed intervention without new evidence is forbidden.
