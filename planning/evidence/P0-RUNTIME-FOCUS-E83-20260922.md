# P0 Runtime Focus — Epoch 83

Status: ACTIVE
Run: `RUN-UTIL-20260922-070913`
Authority epoch: `83`

## Observed bootstrap

- Scheduled due observed from automation runtime: `2026-09-22 07:07:30 KST`.
- Bootstrap entry observed: `2026-09-22 07:09:13 KST`.
- Provider delivery delay: `1 minute 43 seconds (103 seconds)`.
- SAME MAIN provisional recurrence was mutated and live-read back at `2026-09-22 07:20:13 KST`, exactly `11 minutes (660 seconds)` after the observed bootstrap reference.
- `state/STARTUP_ACK.json` was advanced to this generation before substantive work.

## Fresh-state diagnosis

Fresh durable state was materially stale relative to this wake. `state/NOW.json`, `state/CURRENT.json`, `state/ACTIVITY.json`, `state/HANDOFF.json`, and `state/TURN_PLAN.json` still described epoch 82 / `RUN-UTIL-20260922-030015`; CURRENT remained `WORKING`, with its old provisional/extension due around 03:11 KST and no durable normal close.

This is direct negative evidence for the previous generation's P0-A/P0-B acceptance: epoch 82 cannot be counted as a valid normal 10-minute (600-second) close and cannot be credited with an exact ACTUAL END + 1 minute (60 seconds) verified handoff. Missing boundaries remain unknown rather than inferred as useful work.

The failure class is therefore `STALE_WORKING_GENERATION_WITHOUT_VERIFIED_NORMAL_CLOSE`. The current wake must recover forward by claiming a strictly newer authority epoch; it must not restore epoch 82's old due or pretend that epoch 82 closed normally.

## Completed bounded unit 1 — stale generation + scorecard repair

Observed unit START: `2026-09-22 07:09:56 KST`  
Observed unit END: `2026-09-22 07:11:37 KST`  
Observed duration: `1 minute 41 seconds (101 seconds)`

Material outputs:

- Claimed epoch 83 in CURRENT/ACTIVITY/HANDOFF/TURN_PLAN/NOW after explicitly classifying epoch 82 as incomplete rather than silently overwriting its missing close.
- Audited `state/P0_SCORECARD.json` and found a stale active threshold: `minimum_continue_turn_seconds=480`, contradicting the operator-locked 10-minute (600-second) floor and fresh control policy.
- Repaired the scorecard to schema 2.4 with `minimum_continue_turn_seconds=600`, explicit `10 minutes (600 seconds)` human semantics, explicit `1 minute (60 seconds)` P0-B close semantics, epoch 83 as current, epoch 82 as incomplete, and consecutive pair gates reset rather than falsely inherited.
- Preserved the fixed 900-second / 840-second useful-work acceptance objective; the repair changes stale active runtime projection, not the success target.

Evidence commits: `2c548ba70b743739e8ede866fd750e967696dc15`, `cf77c74d361ae1fbcc0a7652afbc0da5766cf240`, `4e36cd57544794bdf91f6c9d112aa6ea728f62a5`, `647c7b415f7b6445b0ccb467d0650982c3e5fa3c`, `e7aa73b77511787d4333f905cb4da5c4ceff1186`, `22a6b784bf75c28b5de6c1879e9e052805df3565`.

## Active P0 action

1. Keep P0-A and P0-B as the only immediate objectives.
2. Treat epoch 82 as an invalid/incomplete prospective sample, not as a consecutive PASS.
3. Continue real checkpointable work for at least 10 minutes (600 observed elapsed seconds) on a normal nonterminal turn.
4. At actual close, mutate the SAME enabled recurring MAIN to ACTUAL END + exactly 1 minute (60 seconds), live-verify exact `DTSTART`, and persist one identical due across CURRENT / ACTIVITY / HANDOFF.
5. Measure scheduled due -> invocation/bootstrap delay separately from the local 1-minute (60-second) close offset.

No broader productization work is authorized to displace this P0 recovery/verification.
