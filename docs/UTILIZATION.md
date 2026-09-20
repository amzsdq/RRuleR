# Relay Utilization Measurement

## Goal
RRuleR optimizes useful-work utilization subject to correctness invariants. A correct relay that voluntarily ends a runnable nonterminal turn is operationally defective.

The active performance target is a **rolling mean observed useful-work span >= 840 seconds across at least 3 valid completed turns**, with continuous progress evidence inside every counted span. The intended operating shape is approximately 14 minutes of useful work inside each 15-minute wake interval, with roughly one minute of runtime/handoff safety margin.

## Primary metric
`useful_work_utilization = productive_substantive_seconds / eligible_active_window_seconds`

Eligible time excludes explicit operator pause, proven external blocking, and platform-wide unavailability. It includes voluntary early stop, avoidable handoff/scheduler gaps, and successor delay caused by stale durable state.

For the current experiment, the reconstructable proxy is:

`observed_useful_span_seconds = last_meaningful_progress_at - substantive_work_started_at`

A span alone is **not** proof that every second was useful work. Two commits 14 minutes apart with a long idle gap must not pass. A turn counts only when meaningful durable progress evidence covers the span with no unexplained internal gap greater than 120 seconds and no known waiting/idle interval masquerading as work.

## Wake cadence versus execution
The 15-minute RRULE is a wake cadence, not a work-duration quota. A run does not gain permission to end because a work unit, checkpoint, document, root, or CI check completed.

The same canonical automation remains an hourly RRULE whose BYMINUTE phase rotates `00 -> 15 -> 30 -> 45 -> 00`. Each expected wake secures and verifies the following quarter before substantive work.

OpenAI's current Scheduled Tasks documentation describes eligible paid recurring tasks as running up to once per hour. RRuleR's effective quarter-hour fast path is therefore an experimental same-task schedule-mutation technique, not a documented native 15-minute recurrence. Expected due time and actual successor observation must be stored separately.

## Live 14+1 measurement protocol
A turn that is intended to count toward the 840-second gate must follow this sequence:

1. **Wake boundary** — record the actual worker wake time; do not substitute the nominal scheduled time.
2. **Rearm first** — move the same canonical RRULE to the next quarter and verify success.
3. **Authority claim** — advance to a fresh authority epoch and mark `state/ACTIVITY.json` as `WORKING`.
4. **Substantive start** — persist `substantive_work_started_at` at the first real useful-work boundary.
5. **Progress evidence** — after meaningful bounded units, refresh `last_progress_at` and describe the current unit. A turn intended for acceptance must not contain an unexplained internal progress-evidence gap >120 seconds.
6. **12-minute admission cutoff** — after roughly 720 seconds, stop starting work that cannot be checkpointed quickly.
7. **14-minute handoff-ready point** — at roughly 840 seconds, set `handoff_ready=true`; continue only tiny safe units while waiting for actual successor evidence. Do not idle merely because 840 seconds was reached.
8. **Successor evidence** — the successor first secures its own next quarter, then durably requests handoff. Scheduled clock arrival alone is not successor evidence.
9. **Drain** — predecessor stops admitting new substantive units, closes the smallest safe unit, persists the final meaningful progress boundary and exact next action, then commits handoff.
10. **Finalize** — only after the end boundary is known, update `state/RUNS.jsonl` and `state/UTILIZATION.json`. Missing timestamps make the measurement invalid; they are never inferred.

## Valid-turn contract
A turn may enter `state/UTILIZATION.json#/valid_completed_turns` only when all of the following are positively evidenced:

- one root/run identity and one authority epoch cover the measurement;
- `substantive_work_started_at` is durable;
- final meaningful progress time is durable and is not earlier than substantive start;
- ordered meaningful progress evidence spans the interval with no unexplained internal gap >120 seconds;
- known waiting or idle intervals are not counted as productive coverage;
- run end/handoff boundary is durable;
- end reason is in the allowed end-reason set;
- `COMMITTED_SUCCESSOR_HANDOFF` includes durable successor observation;
- no authority rollback or conflicting duplicate execution invalidated the interval;
- `observed_useful_span_seconds` is computed from recorded timestamps, never from schedule assumptions.

A turn can be operationally useful yet measurement-invalid. Invalid evidence is retained for diagnosis but does not count toward the three-turn gate.

## Measurable end contract
Every durably observed run end must record:
- `run_ended_at`;
- `end_reason`;
- `program_status_at_end`;
- `successor_observed_at` when the reason is committed successor handoff.

Allowed end reasons are exactly:
- `PROGRAM_COMPLETE`;
- `BLOCKED_EXTERNAL`;
- `COMMITTED_SUCCESSOR_HANDOFF`;
- `EXPLICIT_OPERATOR_STOP`;
- `PLATFORM_ENFORCED_TERMINATION`.

An ended run with no allowed reason is a validation failure, not healthy idle. A handoff end without durable successor observation is also invalid.

## Successor measurement
At each cold successor wake:
1. secure the next wake first;
2. read predecessor activity and run evidence;
3. persist successor observation/handoff request before takeover when a predecessor is still fresh;
4. claim a newer authority epoch only after normal handoff or eligible stale-predecessor recovery;
5. classify the predecessor end only from evidence, never from assumption;
6. measure predecessor productive-end to successor productive-start when both boundaries are known;
7. leave the metric unknown rather than fabricate a duration when a boundary is missing;
8. continue substantive work in the same turn after recording the observation.

If the predecessor was already stale for at least the configured recovery grace before the handoff request, recovery policy v2 permits a fast takeover after an immediate re-read proves no newer predecessor progress. This avoids paying the same 120-second freshness grace twice while still forbidding takeover from a fresh predecessor.

## Under-target diagnosis
Every valid completed turn below 840 seconds must select one dominant cause:

- `PACKET_TOO_SMALL`
- `EARLY_VOLUNTARY_END`
- `WAITING_ON_TOOL_OR_CI`
- `SCHEDULER_GAP`
- `HANDOFF_DELAY`
- `AUTHORITY_RECOVERY`
- `UNKNOWN_EVIDENCE_GAP`

Then persist exactly one concrete corrective experiment for the next worker. The next worker applies it before choosing its work packet. Repeating a failed intervention without new evidence is forbidden.

## Classification
Productive work includes reasoning, research, implementation, validation, reconciliation, and durable documentation that advances the active root. Necessary overhead includes authority, checkpoint, wake verification, and bounded handoff work. Relay-caused idle is runnable time with no executor because of relay design or voluntary early stop. Platform unavailability is tracked separately.

## Correctness constraints
Utilization optimization never overrides authority fencing, duplicate-execution prevention, idempotency/reconciliation, public-safety rules, or terminal acceptance gates. Scheduler bookkeeping drift is repaired forward rather than used as a reason to idle, but authority must never be rolled backward.

## Active acceptance gate
The utilization root cannot pass merely because the no-self-termination policy exists. It requires live successor-cycle evidence that run termination is classified with the measurable end contract, progress evidence is sufficiently dense to reject sparse-span false positives, and any gap/overlap is reported from durable timestamps.

PASS requires at least 3 valid completed turns and a rolling mean of their last three `observed_useful_span_seconds` values >= 840. Each counted turn must also satisfy the continuous-progress evidence rule. Until then, utilization handoff measurement remains blocking and program status remains `CONTINUE`.
