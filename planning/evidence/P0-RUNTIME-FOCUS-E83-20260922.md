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

Existing runtime-continuity policy already defines this family as `RUNTIME_INVOCATION_ENDED_EARLY`; epoch 82 is therefore treated as that existing failure class with the observed subtype `STALE_WORKING_GENERATION_WITHOUT_VERIFIED_NORMAL_CLOSE`, rather than inventing a competing recovery mechanism.

## Completed bounded unit 1 — stale generation + scorecard repair
Observed unit START: `2026-09-22 07:09:56 KST`  
Observed unit END: `2026-09-22 07:11:37 KST`  
Observed duration: `1 minute 41 seconds (101 seconds)`

Material outputs: epoch 83 claimed forward; stale epoch 82 isolated; P0 scorecard stale 8-minute (480-second) threshold repaired to 10 minutes (600 seconds); exact 1-minute (60-second) P0-B semantics restored.

## Completed bounded unit 2 — make P0 timing drift fail deterministically
Observed unit START: `2026-09-22 07:11:38 KST`  
Observed unit END: `2026-09-22 07:13:24 KST`  
Observed duration: `1 minute 46 seconds (106 seconds)`

Material outputs: dedicated P0 scorecard validator added; initial unpinned checkout policy failure diagnosed and removed; live validator run `35661517829` passed; scorecard made mandatory-on-wake; epoch 83 delivery/startup budget recorded separately from local rearm.

## Completed bounded unit 3 — reconcile legacy enforcement and P0-B evidence separation
Observed unit START: `2026-09-22 07:13:25 KST`  
Observed unit END: `2026-09-22 07:15:06 KST`  
Observed duration: `1 minute 41 seconds (101 seconds)`

Material outputs: retired predictive-prearm compatibility fence restored without reactivation; aggregate utilization goal restored only as compatibility/regression objective under the P0-A/P0-B execution lock; epoch 83 scheduler delivery appended; scheduler observations and startup budget made mandatory before corrective timing experiments.

## Completed bounded unit 4 — reject the exact 60-minute failure mode in close projection
Observed unit START: `2026-09-22 07:15:07 KST`  
Observed unit END: `2026-09-22 07:16:58 KST`  
Observed duration: `1 minute 51 seconds (111 seconds)`

Material outputs:
- Strengthened `tools/validate_close_projection.py` so a `HANDOFF_COMMITTED` state is invalid unless `actual_end_at` and `verified_next_fast_due_at` exist, verified fast due equals the projected next due, and projected due is exactly `1 minute (60 seconds)` after observed actual END.
- Added explicit failure `CLOSED_NEXT_DUE_NOT_EXACTLY_1_MINUTE_60_SECONDS_AFTER_ACTUAL_END`.
- Added regression tests for missing actual END, missing verified fast due, mismatched verified due, and the exact historical ambiguity: a due `60 minutes` after END must fail even if CURRENT/ACTIVITY/HANDOFF all agree with each other.
- An earlier CI run on the tool-only commit correctly reached structural validation and failed only because it still had the pre-update test fixture. The subsequent test commit contains the corrected fixture and additional regression cases; integrated CI is still running and is not yet claimed as PASS in this unit.

Evidence commits: `d699c447c5be211917df1f181f08949249da0bca`, `ebd6b763e927c6c4302ef24374465fdd05d1524b`.

## Active P0 action

1. Keep P0-A and P0-B as the only immediate objectives.
2. Treat epoch 82 as an invalid/incomplete prospective sample, not as a consecutive PASS.
3. Continue real checkpointable work for at least 10 minutes (600 observed elapsed seconds) on a normal nonterminal turn.
4. At actual close, mutate the SAME enabled recurring MAIN to ACTUAL END + exactly 1 minute (60 seconds), live-verify exact `DTSTART`, and persist one identical due across CURRENT / ACTIVITY / HANDOFF.
5. Measure scheduled due -> invocation/bootstrap delay separately from the local 1-minute (60-second) close offset.

No broader productization work is authorized to displace this P0 recovery/verification.
