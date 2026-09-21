# RRuleR Architecture

## Responsibility boundary

| Layer | Responsibility | Authoritative? |
|---|---|---|
| GitHub repository | durable state, checkpoints, policy, evidence, work history | Yes |
| ChatGPT scheduled session | reasoning and substantive work | No |
| ChatGPT MAIN automation | primary wake/continuation trigger | No |
| ChatGPT Startup Watchdog | independent pre-bootstrap liveness/rearm trigger; no substantive authority | No |
| GitHub Actions | deterministic checks/reconciliation | Only for facts they verify |
| Chat STATUS output | human-visible handoff receipt | No |

## Cold-start requirement

A fresh successor must be able to answer from GitHub alone:

- What is the root goal?
- What is the current status?
- Who owns authority?
- What checkpoint is verified?
- What has already been attempted?
- Which side effects may already have occurred?
- What is the exact next action?
- What continuation mechanism should wake the next run?

If not, the previous run did not checkpoint enough state.

## Terms

- **TURN** — one logical ownership interval.
- **RUN** — one actual ChatGPT execution.
- **WORK UNIT** — smallest meaningful safely checkpointable unit.
- **CHECKPOINT** — durable continuation state.
- **SUCCESSOR OBSERVED** — evidence that the next scheduled execution has actually begun; mere clock arrival is insufficient.

Task phases do not need to align with TURN boundaries.

## Continuous-work principle

Workers do not stop merely because research ended, writing began, a milestone was crossed, a checkpoint was written, or a schedule boundary arrived.

The normal control loop is:

```text
secure next wake
 -> work unit
 -> checkpoint if useful
 -> immediately continue another admissible unit
 -> ...
 -> successor actually observed
 -> finish current smallest unit
 -> durable handoff
 -> predecessor end
```

This is deliberately optimized for high useful-work utilization.

## Runtime handoff

At successor-triggered handoff:

1. successor execution is actually observed;
2. predecessor stops starting new substantive units;
3. predecessor finishes the current smallest safe unit;
4. predecessor persists checkpoint, duration/progress, evidence, ambiguous side effects, and exact next action;
5. predecessor emits concise STATUS and ends;
6. successor waits for durable handoff if needed, then reconstructs and continues.

If same-canonical overlap/queue is unsupported, the system must not depend on it for correctness. Durable GitHub state remains sufficient for continuation. However, the predecessor still must not voluntarily stop early merely to create a gap.

## Utilization metric

For an observation window:

```text
useful_work_utilization =
  useful substantive work time
  / wall-clock time in which the root job is intended to be active
```

Classify separately:

- productive work;
- checkpoint/handoff overhead;
- scheduler/runtime idle gap;
- external blocked time;
- platform outage time.

Platform-wide outages and explicit external blocks should not be conflated with relay scheduling overhead.

## Correctness before optimization

High utilization never authorizes:

- duplicate substantive execution;
- stale-authority writes;
- replay of ambiguous irreversible side effects;
- skipping durable checkpoint requirements;
- unsafe overlap.

The target is **high utilization subject to correctness invariants**, not activity for its own sake.

## Two-stage continuation protection

RRuleR separates failures by whether MAIN has already protected itself:

```text
MAIN expected due
  -> independent one-shot Startup Watchdog protects pre-bootstrap gap
  -> BOOT_STARTED
  -> MAIN provisional rearm verified
  -> REARM_VERIFIED
  -> existing provisional continuation protects in-turn failure
  -> normal close: MAIN END+60 and Watchdog MAIN_due+3m
```

The Watchdog is intentionally not a Worker/Foreman. It reads fresh durable state, detects missing startup/rearm receipts, and can only rearm the same MAIN canonical when fresh fencing permits. It never performs program work and never creates a replacement actor.

Reservation prompts embed only the stable survival kernel. `control/startup-watchdog.v1.json` is authoritative; MAIN and Watchdog prompts must resynchronize their embedded kernel when GitHub changes materially.
