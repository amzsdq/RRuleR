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

## Active P0 action

1. Claim epoch 83 for `RUN-UTIL-20260922-070913` without rolling any scheduler generation backward.
2. Keep P0-A and P0-B as the only immediate objectives.
3. Treat epoch 82 as an invalid/incomplete prospective sample, not as a consecutive PASS.
4. Continue real checkpointable work for at least 10 minutes (600 observed elapsed seconds) on a normal nonterminal turn.
5. At actual close, mutate the SAME enabled recurring MAIN to ACTUAL END + exactly 1 minute (60 seconds), live-verify exact `DTSTART`, and persist one identical due across CURRENT / ACTIVITY / HANDOFF.
6. Measure scheduled due -> invocation/bootstrap delay separately from the local 1-minute (60-second) close offset.

No broader productization work is authorized to displace this P0 recovery/verification.
