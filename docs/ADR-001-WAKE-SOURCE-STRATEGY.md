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

### 3. GitHub event-triggered ChatGPT Work continuation chain

**Highest-value next feasibility experiment.** Official OpenAI documentation states event-triggered tasks can run up to 30/hour. GitHub triggers may include PR open/ready/close and, depending on trigger, PR reviews, comments, **commit updates**, or completed merges.

That makes a stronger design possible than passive failure recovery: use a dedicated long-lived PR branch as an event lane. A current worker performs a meaningful checkpoint, then intentionally emits exactly one next-generation commit-update event before the historically observed early-runtime boundary. The triggered successor resumes the same durable 10-14 minute objective. The objective remains long-lived; the disposable reasoning invocations become short micro-generations.

This is controlled chaining, not uncontrolled recursion.

Safety rules:
- exactly one outstanding continuation generation;
- unique event ID and monotonically advancing generation;
- only the current authority owner may emit the next continuation event;
- merely acknowledging an event cannot emit another event;
- emit only after meaningful useful work/checkpoint, never heartbeat-only traffic;
- successor deduplicates event ID before substantive work;
- authority epoch cannot roll backward;
- quarter-shift scheduler stays enabled as fallback during the experiment;
- any unbounded event storm disables event emission immediately.

Why target roughly 60-110 seconds before emission: epoch 16 produced 145 seconds of evidenced span before disappearing. If that pattern repeats, emitting a successor event before ~110 seconds may establish the next worker before the predecessor vanishes. The value must be measured, not assumed.

Required proof design:
1. Dedicated public-safe test PR/event lane.
2. Provision a Work event trigger for PR commit updates if the account exposes that supported trigger.
3. Run at least three generations under one durable objective.
4. Measure source event -> worker observation -> first substantive progress and overlap.
5. Prove duplicate delivery is harmless and max generation-ahead remains one.
6. Abort promotion on storm, authority rollback, duplicate substantive execution, or latency that fails to beat the quarter baseline.

### 4. ChatGPT Work background execution

**Research in parallel.** Official documentation confirms cloud-browser Work tasks can continue after the user leaves. If RRuleR can reliably enter that substrate, it may solve worker lifetime directly rather than increasing wake frequency. Current evidence does not prove scheduled RRuleR runs automatically receive that lifetime.

### 5. Paid API background mode / external durable executor

**Architecturally strong but outside the preferred cost envelope.** Keep as a reference implementation and fallback, not the current target.

## Decision

Keep the quarter-shift canonical scheduler as recovery baseline. Promote the controlled `WORK_GITHUB_EVENT_TRIGGER` continuation chain to the highest-priority wake-source feasibility experiment once event-trigger provisioning is available. Keep Work background execution as a parallel capability test.

Do not weaken durable checkpointing, lease/fencing, idempotency, or measurement when swapping wake sources.

## Promotion gate

An alternate wake adapter may replace the baseline only after a bounded test proves:
- median event-to-first-work latency materially below quarter-wake recovery latency;
- duplicate deliveries are harmless;
- no unbounded trigger storm;
- authority never rolls backward;
- no secret/private payload enters the public repository;
- at least three continuation generations complete with measurable useful-work coverage improvement.

## Sources checked

- OpenAI Scheduled Tasks: https://help.openai.com/en/articles/10291617-chatgpt-tasks
- OpenAI GitHub connection/event triggers: https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt
- OpenAI Cloud Browser / Work: https://help.openai.com/en/articles/20001280-using-cloud-browser-in-chatgpt
- Temporal durable execution: https://temporal.io/
- LangGraph production runtime: https://www.langchain.com/blog/runtime-behind-production-deep-agents
