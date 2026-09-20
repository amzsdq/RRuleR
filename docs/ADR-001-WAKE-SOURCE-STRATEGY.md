# ADR-001 — Wake-source strategy for high utilization

Status: EXPERIMENTAL DECISION
Date: 2026-09-21

## Context

RRuleR's P0 target is >=840 seconds of evidenced useful work per intended 900-second window. Epoch 16 demonstrated that a correct plan and durable state cannot guarantee that one consumer reasoning invocation remains alive. The current quarter-shift scheduler can recover only at the next quarter wake.

## Options

### 1. Keep adding policy/heartbeat rules

**Reject as primary fix.** It improves detection but not liveness production. Epoch 16 falsified the assumption that stronger plan policy alone extends worker lifetime.

### 2. Rely only on the quarter-shift scheduled task

**Retain as baseline/fallback.** It is already working and gives a bounded recovery opportunity, but ordinary paid scheduled tasks are officially documented at up to hourly recurrence and the quarter-shift mutation cannot rescue an invocation inside the current quarter.

### 3. GitHub event-triggered ChatGPT Work wake

**Highest-value next feasibility experiment.** Official Scheduled Tasks documentation states event-triggered tasks can run up to 30/hour and supports GitHub pull-request activity on eligible paid plans. This is the only currently identified supported consumer-subscription primitive with documented sub-hour event capacity and no paid API requirement.

Risks:
- trigger recursion if the worker's own PR mutation emits another wake;
- event grouping/delivery latency may reduce effective frequency;
- supported GitHub event types may not include the exact self-signal needed;
- Work/event-trigger provisioning may require operator-visible authorization;
- concurrent deliveries require strict dedupe and authority fencing.

Required proof design:
1. Use a dedicated public-safe test PR/event lane.
2. Event envelope carries a stable event/correlation ID but no secrets.
3. Triggered worker first reads CURRENT + event ledger; duplicate event IDs become no-op observations.
4. Worker must not emit the same trigger event as a side effect of merely acknowledging it.
5. Separate `wake_requested` from `work_committed`; only the latter can advance workflow state.
6. Measure event timestamp -> invocation observation -> first substantive progress.
7. Abort promotion if recursion, grouping, or latency makes the path less reliable than quarter wakes.

### 4. ChatGPT Work background execution

**Research in parallel, not yet selected.** Official documentation confirms cloud-browser Work tasks can continue after the user leaves. If the RRuleR workflow can reliably enter that substrate, it may solve worker lifetime directly rather than increasing wake frequency. Current evidence does not prove scheduled RRuleR runs automatically receive that lifetime.

### 5. Paid API background mode / external durable executor

**Architecturally strong but outside the preferred cost envelope.** Keep as a reference implementation and fallback, not the current target.

## Decision

Keep the quarter-shift canonical scheduler as the recovery baseline. Promote `WORK_GITHUB_EVENT_TRIGGER` to the highest-priority wake-source feasibility experiment once the required event-trigger provisioning path is available. Keep Work background execution as a parallel capability test.

Do not weaken durable checkpointing, lease/fencing, idempotency, or measurement when swapping wake sources.

## Promotion gate

An alternate wake adapter may replace the baseline only after a bounded test proves:

- median event-to-first-work latency materially below quarter-wake recovery latency;
- duplicate deliveries are harmless;
- no recursive trigger storm;
- authority never rolls backward;
- no secret/private payload enters the public repository;
- at least three continuation cycles complete with measurable useful-work coverage improvement.

## Sources checked

- OpenAI Scheduled Tasks: https://help.openai.com/en/articles/10291617-chatgpt-tasks
- OpenAI Cloud Browser / Work: https://help.openai.com/en/articles/20001280-using-cloud-browser-in-chatgpt
- Temporal durable execution: https://temporal.io/
- LangGraph production runtime: https://www.langchain.com/blog/runtime-behind-production-deep-agents
