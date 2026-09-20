# RRULE Self-Update Relay — Reproduction Guide

Status: **short-run mechanism reproduced; utilization semantics under live validation**

Purpose: one recurring ChatGPT automation acts as a one-slot relay clock while GitHub holds durable state.

## Mechanism

The same recurring automation keeps `RRULE:FREQ=HOURLY` and changes only its phase at each wake:

```text
:00 -> BYMINUTE=15
:15 -> BYMINUTE=30
:30 -> BYMINUTE=45
:45 -> BYMINUTE=0
```

The automation ID is unchanged. It does not become one-shot.

## Required invariants

- Exactly one `CANONICAL_AUTOMATION_ID`.
- Always recurring `RRULE:FREQ=HOURLY`.
- `timing_mode=exact_schedule`.
- No normal replacement automation.
- No one-shot conversion.
- NEXT WAKE FIRST: verify schedule update before substantive work.
- Durable work state lives in GitHub, never the automation prompt.
- Terminal completion disables the automation.
- After NEXT WAKE is secured, voluntary idle is forbidden while useful admissible work remains.
- Scheduled quarter arrival is not itself a stop signal.
- Handoff begins only when successor execution is actually observed.

## iCalendar example

```text
BEGIN:VEVENT
DTSTART;TZID=Asia/Seoul:20260920T181500
RRULE:FREQ=HOURLY;BYMINUTE=15;BYSECOND=0
END:VEVENT
```

`DTSTART` is the nearest future time matching the next phase.

## Wake algorithm

1. Determine current scheduled quarter marker: `00|15|30|45`.
2. Update the same automation to the next RRULE phase.
3. Verify the update succeeded.
4. Load `AGENTS.md`, `control/POLICY.md`, and `state/CURRENT.json`.
5. Reconstruct owner/checkpoint/exact next action.
6. Start substantive work immediately.
7. When a bounded unit completes, checkpoint if useful and immediately select the next admissible unit.
8. Do not yield because a phase/milestone/document/checkpoint/scheduled quarter boundary was crossed.
9. When successor execution is actually observed, stop starting new units.
10. Finish the current smallest safe checkpointable unit.
11. Persist checkpoint + evidence + duration/progress + exact next action.
12. Emit concise STATUS and end.
13. Successor waits for the durable handoff if necessary, then reconstructs from GitHub.

## Prompt template

```text
[RRULE SELF-UPDATE RELAY]
CANONICAL_AUTOMATION_ID=<ID>
REPO=<owner/repo>
TIMEZONE=<TZ>

ORDER IS MANDATORY

1. NEXT WAKE FIRST
- Same automation only.
- Keep recurring RRULE:FREQ=HOURLY.
- Keep exact_schedule.
- 00 -> 15 -> 30 -> 45 -> 00.
- Set DTSTART to nearest future matching quarter.
- Verify update before substantive work.

2. LOAD DURABLE STATE
- Read repo bootstrap/policy/current state.
- Chat history is non-authoritative.
- Resume the exact durable next action.

3. WORK CONTINUOUSLY
- Start immediately after next-wake verification.
- Continue while useful admissible work remains.
- When one unit finishes, start the next.
- Checkpointing does not itself authorize stopping.
- Do not stop because the next quarter arrived.

4. SUCCESSOR-TRIGGERED HANDOFF
- Handoff only after successor execution is actually observed.
- Then stop starting new units.
- Finish current smallest safe unit.
- Persist checkpoint/evidence/duration/next action.
- Emit concise STATUS and end.
- Successor resumes from durable state without duplicating predecessor work.

5. FAILURE
- If self-update fails, do not claim fast continuation succeeded.
- If the previous recurring RRULE is still verified alive, record DEGRADED_CONTINUATION and its fallback wake.

6. TERMINAL
- COMPLETE only with proven root acceptance.
- On COMPLETE disable this same automation and schedule no successor.
```

## Self-rescue property

If the current schedule is `FREQ=HOURLY;BYMINUTE=15` and the 18:15 attempt to move to `:30` fails, the old hourly RRULE may remain intact and wake again at 19:15.

```text
fast path:      18:15 -> update succeeds -> 18:30
degraded path:  18:15 -> update fails -> old RRULE -> 19:15 recovery opportunity
```

This is not full rescue. It cannot recover a disabled, deleted, missing, or platform-broken automation.

## Handoff / overlap finding

Do not assume the same canonical automation can execute predecessor and successor concurrently. Correctness must survive absence of overlap.

However, lack of proven overlap does **not** justify voluntary early stop. The predecessor continues useful work until either:

- successor execution is actually observed;
- the root becomes terminal;
- a genuine external blocker is proven; or
- the platform ends the run.

If the platform serializes same-canonical executions, the actual path may be:

```text
predecessor works until platform end
 -> durable latest checkpoint
 -> scheduled successor starts
 -> successor reconstructs
 -> continue
```

The optimization target is to minimize the idle interval between those events without weakening correctness.

## Reproduction acceptance

PASS when all are observed:

1. same canonical ID preserved;
2. recurring RRULE preserved;
3. at least two phase self-updates succeed;
4. at least one later scheduled wake actually fires;
5. successor resumes from durable GitHub state;
6. no duplicate substantive execution;
7. no runtime timeout breaks the verified continuation cycle;
8. predecessor does not voluntarily idle before successor/terminal condition;
9. measured handoff/runtime idle behavior is recorded.

Record evidence in `experiments/rrule-self-relay/README.md`.
