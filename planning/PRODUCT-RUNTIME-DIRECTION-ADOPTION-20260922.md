# Product Runtime Direction Adoption — 2026-09-22

Status: ACTIVE DECISION RECORD

## Purpose

Record which product/runtime direction principles are adopted now, deferred, or rejected for the current RRuleR self-development program without copying private source material into the public repository.

## Operator-locked P0

Current top priority is limited to two runtime outcomes:

1. P0-A — turn worktime / sustained useful work
   - A normal nonterminal CONTINUE turn should sustain at least 10 minutes (600 observed elapsed seconds) unless a truthful early-exit exception applies.
   - Elapsed time is not automatically useful work; artifact-backed evidence remains required.

2. P0-B — exact schedule rearm / continuation latency
   - Normal close must mutate the SAME enabled recurring MAIN to ACTUAL END + exactly 1 minute (60 seconds).
   - Re-read live metadata and verify the exact DTSTART.
   - Persist the same due across durable state projections.
   - Provider delivery/startup delay is measured separately from local schedule arithmetic.
   - Unitless human-readable timing arithmetic is forbidden.

Until both are stably proven and retained as regression gates, unrelated product expansion is secondary.

## Adopt now

### Goal over mechanism

Rules, checkpoints, schedulers, and logs are instruments. Keep, strengthen, simplify, or remove them according to measured contribution to P0-A/P0-B and required safety/correctness.

### Evidence-grounded recursive development

Use this loop:

OBSERVE
-> CLASSIFY BOTTLENECK
-> CHECK PRIOR ART / EXISTING MECHANISMS
-> GENERATE REVERSIBLE CANDIDATE
-> ESTIMATE BENEFIT / COST / RISK
-> EXPERIMENT
-> VERIFY AGAINST FIXED EVIDENCE
-> ADOPT / REVISE / ROLLBACK / REJECT / DO_NOTHING

Do not change the success criterion merely to make a candidate pass.

### Stable vs experimental

Experimental runtime changes must be reversible where practical and must not silently redefine stable invariants. Keep rollback points for material scheduler/runtime experiments.

### Prior art before invention

Prefer established patterns such as retry/backoff, idempotency, fencing, checkpointing, durable execution, observability, and structured recovery when they fit the measured failure.

### Natural-language distribution reporting

Final distribution UX should keep exact internal telemetry but render each turn concisely in natural language:
- observed work period / duration;
- what was completed;
- current status;
- what happens next.

This is a product-layer renderer. During active runtime canaries, evidence-bound technical traces may remain visible. Prose must never replace machine evidence.

## Deferred until P0-A/P0-B are stable

- Personal/Library/Drive distribution adapters
- broader adapter abstraction work
- generalized intake/planner UX
- plan-preview/revision UX
- broader BLOCKED UX productization
- delegation/orchestration expansion not directly needed for the active P0
- general onboarding/product packaging

These may be revisited after the two current runtime blockers are resolved.

## Decision rule

A proposed change that does not materially improve P0-A, P0-B, or a required safety/correctness invariant should normally be deferred or rejected during the current phase.
