# Scheduled-task platform boundary for the quarter relay

## Status

Evidence note for the active RRuleR utilization experiment. This is not a claim that ChatGPT natively supports a 15-minute recurring schedule.

## Official product boundary observed 2026-09-20

OpenAI's current Scheduled Tasks help documentation states that eligible paid plans support recurring scheduled tasks **up to once per hour** and exact delivery times. It separately states that event-triggered tasks can run more frequently. Source: OpenAI Help Center, `Scheduled tasks in ChatGPT` (`https://help.openai.com/en/articles/10291617-chatgpt-tasks`).

Therefore the RRuleR mechanism must be described precisely:

- the canonical task remains an **hourly RRULE**;
- each execution mutates the same task's hourly `BYMINUTE` phase to the next quarter slot;
- the observed effective quarter-hour continuation is an experimental consequence of repeated schedule mutation, not a documented native `FREQ=MINUTELY;INTERVAL=15` capability;
- no correctness or availability guarantee should assume that a newly edited schedule will always trigger again 15 minutes later;
- durable GitHub state and a surviving hourly recurrence remain the recovery basis when the fast path fails.

## Implication for utilization measurement

A 14-minute useful-work target can only be credited from observed run boundaries. The nominal quarter slot is not evidence that a successor actually ran. Early/late delivery, serialization, schedule-edit propagation, or platform throttling can alter the effective interval.

For every turn, retain separately:

1. expected successor due;
2. actual successor observation timestamp;
3. canonical rearm success evidence;
4. predecessor last meaningful progress timestamp;
5. handoff/recovery timestamp when observable.

Do not manufacture a 900-second denominator from the intended schedule when the actual successor boundary is unknown.

## Design consequence

The fast path is best treated as an opportunistic rolling relay layered on top of an officially supported hourly recurring primitive. RRuleR should optimize the fast path aggressively, but its recovery model must remain correct if the platform only honors the documented hourly recurrence.
