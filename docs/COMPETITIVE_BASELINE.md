# Commercial Agent Runtime Competitive Baseline

Status: living evidence baseline, not a parity claim.  
Updated: 2026-09-21.

## Objective

RRuleR is not trying to beat a hosted product by feature count or by assuming a weaker/stronger model.

The comparison target is **runtime/control-plane structure**: if model quality were held comparable, the system should not be materially behind production agent platforms on persistence, scheduling, recovery, orchestration, operator control, side-effect safety, observability, governance, and reproducibility.

Model/provider quality is treated separately as an adapter choice.

## Current external reference points

Observed product/runtime capabilities in current vendor documentation:

- **Temporal**: durable workflows persist running state, resume after failures, expose retries/task queues/timers/signals, and support long-running and human-in-the-loop workflows.
- **LangGraph**: checkpoint-backed durable execution, node retry policies, interrupts that can pause indefinitely and resume from saved state.
- **Gumloop**: scheduled/event-triggered agent tasks, subagents and parallel clones, per-tool approval controls, guardrails, shared-agent visibility, analytics and spend controls.
- **Relevance AI**: scheduled work, wake mode, task queues with in-progress/upcoming/failed/processed/cancelled status, multi-agent workforces, approval/escalation modes, workload pacing and broad integrations.
- **Lindy**: monitoring triggers/actions for task completion/status/history and enable/disable controls, plus large integration surface.

Representative public references:
- https://docs.temporal.io/
- https://docs.langchain.com/oss/javascript/langgraph/thinking-in-langgraph
- https://www.gumloop.com/blog/introducing-agent-tasks
- https://www.gumloop.com/blog/subagents-launch
- https://www.gumloop.com/blog/human-in-the-loop
- https://relevanceai.com/docs/agent/give-your-agent-tasks/task-queue
- https://relevanceai.com/schedule-work
- https://relevanceai.com/approvals-escalations
- https://www.lindy.ai/changelog

## Structural parity dimensions

Canonical gate definitions live in `docs/SAAS_PARITY_ARCHITECTURE.md`.

1. Durable resume
2. Scheduling/wake adapters
3. Side-effect safety
4. Recovery
5. Delegation
6. Queue/backpressure
7. Human approval/escalation
8. Observability
9. Governance
10. Version/replay safety
11. Reproducibility

## Current RRuleR assessment

### Strong or structurally promising

- GitHub durable state independent of disposable reasoning context.
- Explicit owner/authority epoch and stale-worker fences.
- Checkpoint-first continuation design.
- Ambiguous irreversible-effect reconciliation and idempotency direction.
- Independent completion evidence rather than worker prose.
- Public-safe durable boundary.
- Replaceable wake-adapter architecture.
- Same-canonical rolling continuation with provisional rescue and completion-relative fast re-entry.

### Still proving

- production recovery latency distribution;
- rolling scheduler reliability across many cycles;
- independent event-wake adapter;
- multi-agent delegation/convergence;
- unified operator observability;
- negative governance/permission tests.

### Clear structural gaps

- canonical prioritized runnable queue with backpressure/admission control;
- durable human approval interrupt/resume;
- version/replay compatibility for in-flight jobs;
- end-to-end cold bootstrap acceptance;
- unified resource/tool/cost + queue + approval scorecard.

## Rolling baton as utilization architecture

The prior fixed quarter-hour scheduler made useful-work capacity depend on arbitrary wall-clock phase and scheduler jitter.

The rolling design changes the relationship:

```text
predecessor plans next packet
  -> successor validates packet
  -> provisional rescue occurrence is secured
  -> useful work executes
  -> durable checkpoint
  -> predecessor plans next packet
  -> normal next occurrence = actual completion + short delay
```

With a nominal 600-second packet and 60-second normal continuation delay, the theoretical duty cycle is about 90.9%. Production scoring must use observed evidence, not this theoretical number.

The longer provisional rescue horizon is not normal idle time; it exists for abrupt-loss recovery.

## Acceptance discipline

A capability is not competitive because a document says it exists.

A parity gate requires the strongest evidence appropriate to the claim:

- deterministic regression test;
- live fault injection;
- live scheduler/trigger proof;
- negative permission test;
- reproducible bootstrap;
- durable operator-visible evidence.

## Priority

1. Make rolling continuation + successor baton internally consistent and regression-tested.
2. Prove production utilization and recovery behavior.
3. Add queue/backpressure.
4. Add durable human approval/interrupt.
5. Prove delegation fan-out and convergence.
6. Add version/replay migration safety.
7. Consolidate operator observability.
8. Prove a second trigger adapter and cold bootstrap reproducibility.

This order is chosen for structural leverage, not marketing visibility.
