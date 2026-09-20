# RRULE Self-Relay Reproduction Checklist

Use this checklist to reproduce the mechanism with a fresh ChatGPT session.

## Preconditions

- One existing ChatGPT automation that may be updated.
- Its canonical automation ID is known.
- A durable GitHub repository is available.
- The automation must support recurring RRULE schedules and exact scheduling.
- The repository must already contain or bootstrap:
  - `AGENTS.md`
  - `control/POLICY.md`
  - `control/relay-policy.v1.json`
  - `state/CURRENT.json`
  - `state/RELAY_VALIDATION.json`

## Initial arm

Choose a quarter marker that is in the near future.

Example for a current time shortly before 19:30 KST:

```text
BEGIN:VEVENT
DTSTART;TZID=Asia/Seoul:20260920T193000
RRULE:FREQ=HOURLY;BYMINUTE=30;BYSECOND=0
END:VEVENT
```

Requirements:

- `timing_mode=exact_schedule`
- `is_enabled=true`
- same canonical automation ID
- no replacement automation
- no one-shot conversion

## Every wake

### 1. Update the same recurring automation first

Rotate:

```text
00 -> 15
15 -> 30
30 -> 45
45 -> 00
```

Set `DTSTART` to the nearest future time matching the next phase.

Verify the update succeeded.

### 2. Reconstruct durable state

Read in order:

1. `AGENTS.md`
2. `control/POLICY.md`
3. `control/relay-policy.v1.json`
4. `state/CURRENT.json`
5. `state/HANDOFF.json`
6. `state/RELAY_VALIDATION.json`
7. task-specific referenced material

Do not treat chat memory as authoritative state.

### 3. Work immediately and continuously

After wake verification:

- start substantive work immediately;
- keep selecting useful bounded units;
- checkpoint as necessary;
- do not idle merely because a checkpoint/document/milestone/scheduled quarter boundary is reached.

### 4. Observe successor

At the next scheduled boundary, distinguish:

- **clock arrived only** — predecessor keeps working;
- **successor actually observed** — initiate handoff.

Positive successor evidence is required. Never infer overlap merely because two run descriptions appear close in time.

### 5. Handoff

After successor observation:

Predecessor:

1. stops starting new substantive units;
2. finishes current smallest safe unit;
3. updates `state/HANDOFF.json` to `HANDOFF_DRAIN` when it still owns the handoff write;
4. updates `state/CURRENT.json` with final predecessor checkpoint and exact next action;
5. records event/run evidence with observed timestamps only;
6. commits handoff as `HANDOFF_COMMITTED`;
7. ends.

Successor:

1. must not duplicate predecessor active work;
2. reads durable handoff;
3. resumes exact next action after authority is valid;
4. marks itself active where the state model requires.

If the platform serializes executions and explicit predecessor drain cannot run, successor reconstructs from the latest durable checkpoint and records the platform-ended boundary where observable.

## Evidence discipline

For every acceptance claim:

- prefer automation metadata, Git commit SHA, Actions run ID, durable event timestamp, or durable run observation;
- record unknown timing as `null`, not an estimate;
- do not use chat prose alone as completion or concurrency evidence;
- update `state/RELAY_VALIDATION.json` so a fresh session can distinguish proven and pending criteria mechanically.

## Self-update failure test

If the phase update fails, check whether the old recurring RRULE is still intact.

If yes:

- classify `DEGRADED_CONTINUATION`;
- record the slower expected hourly wake;
- do not claim the 15-minute fast path succeeded.

If no valid wake remains:

- persist continuation failure;
- require external recovery.

## PASS gate

Do not claim reproduction PASS until the machine validation record shows adequate evidence for:

- [ ] same canonical automation ID across runs;
- [ ] RRULE remains recurring;
- [ ] at least two phase rotations succeed;
- [ ] at least one scheduled successor actually runs;
- [ ] successor reconstructs from GitHub durable state;
- [ ] additional continuation survives beyond the first cold handoff;
- [ ] no duplicate substantive execution is evidenced;
- [ ] predecessor no-voluntary-idle rule is durable and followed where observable;
- [ ] handoff/runtime behavior is recorded without fabricated precision;
- [ ] final CI/durable state is coherent.

Concurrency classification and precise idle-gap measurement are desirable live evidence. They must not be invented; if unavailable, preserve them as pending or scoped observations and state whether they block reproduction correctness.

## Terminal behavior

When the root goal itself is complete:

1. persist terminal durable state;
2. append terminal evidence;
3. set `state/RELAY_VALIDATION.json` to the justified terminal validation status;
4. disable the same canonical automation;
5. schedule no successor;
6. report COMPLETE.
