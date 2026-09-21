# P001 Utilization Baseline — 2026-09-21

Status: **CURRENT BASELINE / NOT P0 PASS EVIDENCE**  
Parent: `WS-P001-002 — Sustained Turn Utilization`

## Measurement discipline

This baseline separates observed useful work, known non-useful work, and unknown time. Unknown time is never converted into useful time or idle time.

## Strict ledger baseline before resumed epoch 59

The accepted ledger contained 10 records covering authority epochs 34-43 with 582 observed useful seconds. It then had no accepted records for epochs 44-58. This does not prove those epochs were idle; it proves the strict useful-work measurement pipeline could not classify them.

## Resumed epoch 59 result

The resumed bounded turn ran from `15:49:58` to `16:00:24` KST (626 wall seconds). Five adjacent accepted intervals cover **557 strict useful seconds**, or **88.98% of turn wall time** and **92.83% of the 600-second useful-work target**.

This is a material improvement over the historical tiny-packet pattern and proves prospective capture is functioning again. It is still not a completed fixed 900-second P0 window.

## Epoch 60 fixed-window feasibility finding

Epoch 60 was first observed at `17:01:46` KST inside the canonical fixed `17:00:00-17:15:00` window. The first 106 seconds are therefore unknown. Even if every second from observed start through window end were useful, the maximum possible accepted useful time is only **794 seconds**, below the **840-second** target. This window cannot become P0 acceptance evidence and must not be gamed or backfilled.

More importantly, the active execution cadence has a structural ceiling:

- P0 target: `840 / 900 = 93.33%` useful coverage.
- Nominal bounded work target: 600 seconds.
- Current normal completion-relative rearm offset: 60 seconds.
- Idealized ceiling before any startup/checkpoint/scheduler jitter: `600 / (600 + 60) = 90.91%`.
- A prior production sample (`UTIL-EXP-011`) observed about 64 seconds of scheduler delivery delay after the due boundary.

Therefore **the current post-close continuation design cannot reliably satisfy the current P0 target even with perfect in-turn execution**. This is now the highest-effect utilization bottleneck. Weakening the P0 target would hide the problem rather than make the runtime SaaS-grade.

## Ranked causes

### 1. Normal continuation latency budget is structurally incompatible with P0 — highest current impact

A 600-second useful turn can tolerate at most about **42.9 seconds of average non-useful gap** and still reach 840/900. A 60-second post-close due already exceeds that budget before scheduler delivery latency and startup overhead are added.

Correction direction: `UTIL-EXP-018` tests **predictive same-canonical successor prearm**. The successor due is moved before the predecessor's target close so scheduler latency can be absorbed while the predecessor is still doing useful work. This does not create dual substantive ownership: the successor must fence and may not claim substantive authority while the predecessor remains fresh/conflicting.

The 780-second provisional cold-rescue horizon remains separate and unchanged.

### 2. Evidence capture was optional in practice — corrected, continue regression monitoring

Epochs 44-58 became unclassifiable because workers did not have an explicit forward-capture responsibility. Epoch 59 repaired this with guarded append tooling, tests, integrated CI, mandatory wake loading, and worker capture rules.

### 3. Historically short local work packets — materially improved, continue repeated-turn test

Epoch 59 sustained 557 strict useful seconds across a 626-second bounded turn. This is promising but one sample is insufficient. Epoch 60 remains the second repeated-turn retest.

### 4. Strategy drift toward nearby control-plane work — structurally corrected

The planning spine `PROGRAM -> PROJECT -> WORK SPEC -> NOW -> TURN_PLAN` now binds local work to P001 acceptance rather than nearby implementation context.

### 5. Bounded-turn close semantics contradiction — corrected

Gate v3 permits `VERIFIED_SAME_CANONICAL_CONTINUATION` as a run-end-only authority after bounded-close requirements while preserving program-level nonterminal semantics.

## Current experiment

`UTIL-EXP-018 — predictive successor prearm`

Hypothesis: if the same-canonical successor is armed before target close, normal scheduler latency can overlap the predecessor's still-useful work. The predecessor continues useful work to its bounded close. An early successor may read/fence/observe but cannot take over substantive authority until a fresh re-read proves a safe close or transfer.

Required canary evidence:

1. predictive due timestamp;
2. actual successor observation timestamp;
3. predecessor last useful boundary;
4. successor first useful boundary;
5. post-close gap;
6. whether any unsafe overlap, duplicate side effect, or schedule rollback occurred.

Promotion requires at least two safe canary handoffs with post-close gap <=42 seconds, then a valid fixed 900-second utilization window.

## Baseline conclusion

Evidence freshness and sustained in-turn execution have improved enough to reveal the next bottleneck: **normal continuation latency is now mathematically inconsistent with the P0 utilization target**. The next high-value work is not more generic control hardening. It is a measured predictive-prearm canary that tries to hide scheduler latency under useful predecessor work while retaining single substantive authority and cold-rescue safety.
