# Runtime continuity prior art

Purpose: preserve external design evidence so failed RRuleR interventions are not retried in isolation.

## AWS Step Functions callback/activity pattern

AWS Step Functions separates three concepts that RRuleR should also keep separate:

1. **Task completion** — an explicit success/failure callback advances workflow state.
2. **Heartbeat/liveness** — periodic heartbeat signals show that a worker still owns a live task; missing heartbeats cause timeout/failure.
3. **Maximum task duration** — task timeout remains a separate upper bound; heartbeats do not make an invocation immortal.

Official references consulted 2026-09-21:
- https://docs.aws.amazon.com/step-functions/latest/dg/state-task.html
- https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html
- https://docs.aws.amazon.com/step-functions/latest/apireference/API_SendTaskHeartbeat.html

## RRuleR implications

- Keep `ACTIVITY.last_progress_at` as liveness/ownership evidence, not automatic useful-work credit.
- Keep useful-work evidence in `WORK_INTERVALS` and validate internal evidence gaps separately.
- Treat missing liveness as a recovery trigger, not as proof that the substantive task itself failed or should be blindly replayed.
- Preserve an invocation/runtime upper-bound assumption even when heartbeats are fresh; a disposable ChatGPT generation can still be platform-ended.
- Continuation tokens/events should behave like fenced callback tokens: one outstanding generation, monotonic authority, duplicate delivery allowed but duplicate substantive side effects forbidden.

This supports the current layered architecture: hard continuation authority controls voluntary yield; liveness detects disappearance; event/scheduled wakes create a replacement worker; durable authority fencing decides who may continue the task.
