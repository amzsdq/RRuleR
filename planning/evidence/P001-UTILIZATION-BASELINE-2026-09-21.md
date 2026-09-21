# P001 Utilization Baseline — 2026-09-21

Status: **CURRENT BASELINE / NOT P0 PASS EVIDENCE**  
Parent: `WS-P001-002 — Sustained Turn Utilization`

## Measurement discipline

This baseline intentionally separates:

- **observed useful work** — intervals with observed boundaries and materially new artifacts accepted by `state/WORK_EVIDENCE.json`;
- **known non-useful work** — scheduler/heartbeat/wait/no-op evidence;
- **unknown time** — anything without enough evidence to classify.

Unknown time is not converted into useful time or idle time.

## Strict ledger baseline before resumed epoch 59

The accepted ledger contained 10 records covering authority epochs 34-43 with observed useful durations:

`76 + 57 + 190 + 49 + 47 + 14 + 67 + 18 + 31 + 33 = 582 seconds`.

The ledger then had no accepted records for epochs 44-58. This does **not** prove those epochs were idle. It proves the strict useful-work measurement pipeline could no longer classify their work time, so P0 could not be established from that interval.

## Resumed epoch 59 baseline

The resumed turn began at the automation-observed boundary `2026-09-21T15:49:58+09:00`.

`WE-20260921-E59-001` records an observed substantive interval through `15:51:55+09:00`, totaling **117 seconds**. The interval produced the work-spec activation/diagnosis, deterministic evidence append helper, focused tests, integrated-CI wiring, and bootstrap capture rule.

This is proof that prospective capture is working again. It is **not yet** a completed 900-second P0 window and must not be promoted as one.

## Ranked causes of under-utilization / unprovable utilization

### 1. Evidence capture was optional in practice — highest measured impact

Impact: **15 authority epochs (44-58) became unclassifiable in the strict ledger.**

The repository had validators but no deterministic append helper/collector, and the worker bootstrap did not explicitly require qualifying work to advance the ledger. This caused a measurement blackout even while substantive commits continued.

Correction applied in epoch 59:
- `tools/append_work_evidence.py`;
- `tests/test_append_work_evidence.py`;
- integrated CI coverage;
- explicit forward-capture bootstrap rule.

### 2. Turns historically ended after small local packets — high execution impact

The pre-resume strict ledger itself contains many very short accepted intervals (14s, 18s, 31s, 33s, 47s, 49s, 57s, 67s, 76s) and one 190s interval. These durations do not by themselves equal full-turn duration, but they are consistent with the previously observed pattern of committing one bounded change and then failing to establish sustained evidence across most of a 600-second useful-work target.

Correction already introduced at the runtime level: 10-minute bounded work target, no local-completion self-stop, and a related fallback unit. Epoch 59 must test whether this changes actual sustained occupancy rather than assuming the rule works.

### 3. Strategy drift toward nearby control-plane work — medium/high opportunity cost

Before the planning spine, the next packet remained continuation-policy workflow simplification even after utilization had become the stated P0. The work was technically valid but not clearly the highest-effect action against the active bottleneck.

Correction applied: `PROGRAM -> PROJECT -> WORK SPEC -> NOW -> TURN_PLAN`, with WS-P001-002 now authoritative.

### 4. Scheduler/continuation gaps — still relevant, but not currently proven dominant

Continuation survival is strong and the rolling same-canonical lifecycle already targets a completion-relative fast wake. Current evidence does not justify treating scheduler timing as the dominant remaining utilization loss ahead of execution occupancy/evidence freshness.

## Baseline conclusion

The first intervention should remain **prospective evidence freshness + sustained-turn execution**, not another scheduler/control redesign. The next valid turns should answer two questions with direct evidence:

1. Does a resumed worker sustain useful work for most of its 600-second target rather than stopping after a small packet?
2. Does every qualifying turn keep `WORK_EVIDENCE` current without fabricating unknown time?

If both hold, move to repeated-window P0 testing. If not, classify the largest observed gap in the failed turn and correct that cause next.
