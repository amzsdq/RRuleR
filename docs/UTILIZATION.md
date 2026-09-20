# Relay Utilization Measurement

## Goal
RRuleR optimizes useful-work utilization subject to correctness invariants. A correct relay that voluntarily ends a runnable nonterminal turn is operationally defective.

## Primary metric
`useful_work_utilization = productive_substantive_seconds / eligible_active_window_seconds`

Eligible time excludes explicit operator pause, proven external blocking, and platform-wide unavailability. It includes voluntary early stop, avoidable handoff/scheduler gaps, and successor delay caused by stale durable state.

## Wake cadence versus execution
The 15-minute RRULE is a wake cadence, not a work-duration quota. A run does not gain permission to end because a work unit, checkpoint, document, root, or CI check completed.

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
3. claim a newer authority epoch before authoritative work;
4. classify the predecessor end only from evidence, never from assumption;
5. measure predecessor productive-end to successor productive-start when both boundaries are known;
6. leave the metric unknown rather than fabricate a duration when a boundary is missing;
7. continue substantive work in the same turn after recording the observation.

## Classification
Productive work includes reasoning, research, implementation, validation, reconciliation, and durable documentation that advances the active root. Necessary overhead includes authority, checkpoint, wake verification, and bounded handoff work. Relay-caused idle is runnable time with no executor because of relay design or voluntary early stop. Platform unavailability is tracked separately.

## Correctness constraints
Utilization optimization never overrides authority fencing, duplicate-execution prevention, idempotency/reconciliation, public-safety rules, or terminal acceptance gates.

## Active acceptance gate
The utilization root cannot pass merely because the no-self-termination policy exists. It requires live successor-cycle evidence that run termination is classified with the measurable end contract and that any gap/overlap is reported from durable timestamps. Until then, utilization handoff measurement remains blocking and program status remains `CONTINUE`.
