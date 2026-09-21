# Runtime Continuity Architecture

## Problem

A valid plan, WORKING state, and passing validator do not keep a disposable reasoning invocation alive. Durable workflow continuity and live reasoning-worker lifetime are separate concerns.

RRuleR therefore separates:

1. **Wake source** — starts a fresh reasoning invocation.
2. **Reasoning worker** — performs useful work while the invocation exists.
3. **Durable continuation** — stores exact resumable state.
4. **Supervisor/measurement** — detects stale workers and quantifies dead time without inference.

GitHub provides durable state and much of measurement. The ChatGPT scheduler provides the current wake source. Neither alone proves useful work occurred.

## Current production substrate

The active durable workflow uses one same-canonical hourly RRULE whose DTSTART is mutated. Fixed quarter-hour rotation is retired.

Two scheduler horizons must remain distinct:

- **cold rescue:** provisional same-canonical due around +780 seconds, retained so abrupt worker death has a bounded future wake opportunity;
- **normal continuation:** optimized separately so a healthy bounded turn does not pay the full cold-rescue delay.

The verified normal fallback is completion-relative rearm. A production sample observed the next invocation about 64 seconds after the durable due boundary.

## P0 constraint exposed by epoch 59/60

P0 requires at least 840 useful seconds in a fixed 900-second window: 93.33% coverage.

Epoch 59 improved in-turn execution to 557 strict useful seconds over 626 wall seconds. That exposed the next bottleneck: with a 600-second useful turn, the average non-useful cross-turn gap must stay at or below about 42.9 seconds. A nominal 60-second post-close due already exceeds that budget before scheduler jitter/startup overhead.

Therefore the verified completion-relative fallback is a safety mechanism but cannot reliably satisfy P0 as the optimized normal path.

## UTIL-EXP-018 — predictive same-canonical prearm

The current canary attempts to hide scheduler delivery latency under predecessor useful work:

```text
wake
 -> fence / provisional +780s cold-rescue arm
 -> useful work + checkpoints
 -> before target close, move SAME canonical due to predictive boundary
 -> predecessor keeps doing useful work
 -> successor may arrive
      -> if predecessor fresh+conflicting: fence/read/observe only
      -> no conflicting substantive authority
 -> predecessor durable close/transfer
 -> successor claims fresh epoch
 -> measure predecessor-last-useful -> successor-first-useful gap
```

The first candidate uses a predictive due 30 seconds before target close. If the prior ~64-second scheduler delay repeats, successor observation would occur about 34 seconds after close, inside the ~42.9-second P0 gap budget. This is a hypothesis only; actual observed timestamps decide the result.

### Safety invariants

- one canonical automation;
- one substantive authority owner at a time;
- predictive wake alone never advances authority;
- early successor cannot replay or duplicate predecessor side effects;
- authority epoch remains monotonic;
- newest verified schedule generation wins;
- +780s cold-rescue semantics remain intact until predictive arm replaces that occurrence intentionally;
- unsafe overlap, duplicate side effect, schedule rollback, or missed successor rolls normal continuation back to the verified completion-relative fallback.

### Promotion gate

Predictive prearm is not production-promoted from one apparent success. Require:

1. at least two safe same-canonical canary handoffs;
2. no duplicate substantive side effect;
3. no schedule rollback;
4. observed predecessor-last-useful to successor-first-useful gap <=42 seconds in each promoted sample;
5. then at least one valid fixed 900-second utilization window before broader adoption.

P0 itself still requires three consecutive valid accepted fixed windows and the configured rolling mean threshold.

## Evidence discipline

Track at least:

- `invocation_useful_span_seconds`;
- `continuation_gap_seconds`;
- `window_useful_coverage_seconds`;
- `scheduler_delivery_delay_seconds`;
- `predictive_due_to_successor_observation_seconds`;
- `predecessor_last_useful_to_successor_first_useful_seconds`;
- overlap/fence outcome;
- duplicate-side-effect and schedule-rollback outcome.

Missing timestamps remain unknown. Scheduler-only mutation, heartbeat-only state, waiting, and evidence bookkeeping alone are not useful-work evidence.

## Worker mortality and recovery

Worker mortality is normal. If an invocation disappears without committed close/transfer, classify abrupt owner loss and recover under `control/handoff-recovery.v1.json`; do not pretend predictive prearm or a future schedule proves the predecessor stayed alive.

Predictive prearm optimizes the **healthy normal handoff path**. It does not replace abrupt-loss recovery and does not weaken cold-rescue safety.

## Longer-term wake adapters

A genuinely independent event-driven wake remains architecturally attractive because it can reduce both normal and abrupt-loss latency without depending on predictive timing. GitHub PR-triggered ChatGPT Work and other supported consumer-subscription wake surfaces should remain interchangeable adapters behind the same durable authority/fence contract, not embedded into workflow semantics.

## SaaS competitiveness implication

Commercial agent SaaS controls a background execution substrate or durable task queue. RRuleR already approximates durable workflow semantics on GitHub; the remaining P0 question is whether the consumer wake substrate can deliver sufficiently small useful-work gaps.

The immediate strategy is therefore evidence-driven:

`maximize in-turn work -> hide measurable normal scheduler latency safely -> prove fixed-window utilization -> only then broaden architecture`.
