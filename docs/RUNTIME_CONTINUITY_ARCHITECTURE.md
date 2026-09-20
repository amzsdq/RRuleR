# Runtime Continuity Architecture

## Problem

A valid plan, a WORKING state, and a passing validator do not keep a disposable reasoning invocation alive. Epoch 16 proved this directly: its plan was valid and its implementation finished, but durable progress stopped long before the successor wake.

The control plane must therefore separate **liveness production** from **liveness detection**.

## External prior art

Current durable-execution systems converge on the same boundary:

- Temporal persists workflow/event history and lets workers fail while later workers resume from durable state. Workflow state is durable; individual workers are not assumed to stay alive.
- LangGraph checkpoints graph state after execution steps and resumes from the latest checkpoint when a worker crashes or is released. Its production runtime explicitly treats tying up one worker for an entire long-running agent lifetime as undesirable.
- OpenAI Responses API background mode exists specifically so multi-minute reasoning can execute asynchronously without depending on a client connection. That capability is an API runtime primitive, not something repository policy can emulate inside a consumer scheduled invocation.
- OpenAI's current Scheduled Tasks documentation states that eligible paid plans support ordinary recurring schedules only up to once per hour, while **event-triggered tasks can run up to 30 times per hour / 720 times per day** across event-triggered tasks. Supported event sources include GitHub pull-request activity through ChatGPT Work on eligible paid plans. This is materially different from the ordinary scheduler and is a candidate low-latency wake adapter.
- ChatGPT Work cloud-browser tasks can continue after the user leaves or closes the device, demonstrating a consumer-subscription background execution substrate that may be useful for future RRuleR adapters when accessible to the workflow.

References checked 2026-09-21:
- https://temporal.io/
- https://go.temporal.io/platform-hub/ai-engineering/ai-reference-architecture
- https://www.langchain.com/blog/runtime-behind-production-deep-agents
- https://www.langchain.com/blog/why-agent-infrastructure
- https://openai.com/index/new-tools-and-features-in-the-responses-api/
- https://help.openai.com/en/articles/10291617-chatgpt-tasks
- https://help.openai.com/en/articles/20001280-using-cloud-browser-in-chatgpt

## RRuleR consequence

RRuleR must not confuse four independent mechanisms:

1. **Wake source** — causes a fresh reasoning invocation to start.
2. **Reasoning worker** — performs useful work while the invocation exists.
3. **Durable continuation** — stores exact resumable state so worker death loses little work.
4. **Supervisor/measurement** — detects stale workers and quantifies dead time.

GitHub can provide (3) and much of (4). The scheduled task provides (1). Neither can guarantee that (2) remains alive for 14 minutes.

## Invariants

### RC-1: worker mortality is normal

A worker disappearing before its nominal 14-minute horizon is a runtime event, not proof that the work packet completed.

### RC-2: no fake heartbeat

A timestamp-only heartbeat is not useful-work evidence. Every progress event must identify a completed or materially advanced unit and durable evidence.

### RC-3: bounded loss

Every substantive unit must end in a resumable checkpoint. Side effects must remain idempotent or have reconciliation evidence.

### RC-4: separate metrics

Track at least:

- `invocation_useful_span_seconds`: first substantive progress to last meaningful progress inside one invocation.
- `continuation_gap_seconds`: next invocation substantive start minus predecessor last meaningful progress.
- `window_useful_coverage_seconds`: evidenced useful intervals inside the intended 900-second window; never infer coverage between sparse events.
- `scheduler_delivery_delay_seconds`: actual successor observation minus durable expected due.
- `handoff_overhead_seconds`: successor observation to new-owner substantive start.

The old `observed_useful_span_seconds` remains diagnostic but cannot alone prove 840 seconds of useful work.

### RC-5: classify the producer boundary

If a valid active plan has unfinished admissible work but the invocation produces no further durable progress before a later successor observes it stale, classify `RUNTIME_INVOCATION_ENDED_EARLY`. Do not blame packet sizing or handoff.

## Wake-adapter candidates

### A. Quarter-shift scheduled task — current

Strength: already operational and durable. Weakness: official recurring-task cadence is hourly; RRuleR's quarter-shift self-mutation is experimental and cannot rescue a worker that dies between quarter wakes.

### B. Event-triggered Work task — high-priority feasibility target

Official documentation allows event-triggered tasks up to 30 executions/hour and supports GitHub pull-request activity. In principle this can reduce the recovery/wake latency from ~15 minutes toward event latency without paid API usage.

This is **not yet adopted as production**. It needs a controlled proof that:

1. a public-safe GitHub PR event produced by the RRuleR control plane can trigger the Work task;
2. the event-triggered invocation can read the same durable state and obey the same lease/fence contract;
3. self-generated events do not create a trigger storm or recursive duplicate execution;
4. deduplication by event ID / authority epoch is reliable;
5. rate limits and grouping behavior still permit materially lower continuation gaps.

If feasible, the event trigger should be an interchangeable `wake_source` adapter, not embedded in workflow semantics.

### C. ChatGPT Work background/cloud execution — research target

Work can continue cloud-browser tasks after the user leaves. Treat this as a potential longer-lived worker substrate, but do not assume that ordinary scheduled invocations automatically inherit the same lifetime. A separate capability test is required.

## Strategy ladder

1. **Exploit long invocation when available.** Give each worker a coherent 10-14 minute objective and keep doing related useful work.
2. **Checkpoint aggressively by meaningful unit.** Minimize lost work when the invocation disappears.
3. **Recover immediately at next available wake.** Never add another grace period to an already stale worker.
4. **Measure the unavoidable gap honestly.** Do not count dead time as utilization.
5. **Test event-driven wake feasibility.** If supported, use GitHub PR activity as a lower-latency wake adapter with strict dedupe/fencing.
6. **Evaluate Work background execution separately.** If it provides longer worker lifetime, plug it in behind the same durable contract.

## Architectural implication for SaaS competitiveness

Commercial agent SaaS obtains high apparent availability by owning a background execution substrate or durable task queue. RRuleR can reproduce the durable workflow semantics on GitHub, but a consumer scheduled-task wake source imposes a hard utilization ceiling whenever individual invocations terminate early and no sub-quarter wake primitive exists.

The newly documented event-triggered task path changes that feasibility picture: eligible paid ChatGPT plans expose a supported event wake mechanism with a much higher documented execution ceiling than ordinary schedules. If GitHub PR activity can be made into a safe self-continuation signal, RRuleR may be able to close much of the dead-time gap without a paid API or always-on PC.

Therefore the P0 experiment now has three outputs:

- maximize useful span of each available invocation;
- quantify whether remaining dead time is application logic or runtime substrate;
- test whether a supported event-driven Work wake adapter can reduce recovery latency without trigger recursion.
