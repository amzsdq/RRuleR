# WS-P001-002 — Sustained Turn Utilization

Status: **ACTIVE**  
Parent project: [P001 — Sustained Utilization & Continuous Execution](../projects/P001-SUSTAINED-UTILIZATION.md)

## Problem

Continuation survival is high, but useful-work occupancy must meet a SaaS-grade P0 target. Measurement freshness was previously broken, and after repairing it the active normal-continuation cadence was shown to have a theoretical utilization ceiling below the target.

## Outcome

Make bounded wakes spend most eligible wall-clock time on substantive authorized work, keep strict evidence current, and reduce normal cross-turn continuation loss enough that fixed 900-second P0 windows can actually pass.

## Scope

- trustworthy useful-work occupancy measurement;
- prospective evidence capture without historical inference;
- measured ranking of under-utilization causes;
- highest-effect corrections and canaries;
- repeated-turn/fixed-window retesting;
- correctness, fencing, idempotency, public-repo safety, and cold-rescue preservation.

## Non-scope

- controls added only for theoretical completeness;
- controls removed only to reduce rule count;
- unrelated feature breadth;
- treating scheduler survival as useful-work utilization;
- weakening the P0 threshold to accommodate an inefficient continuation design.

## Acceptance

- [x] Current-turn useful-work evidence is captured without multi-epoch lag.
- [x] Baseline wake utilization is computed from durable evidence with unknown time left unknown.
- [x] Dominant causes of under-utilization are ranked by measured impact.
- [x] At least one correction is implemented against the highest-impact cause.
- [ ] Corrections are retested across multiple valid turns/windows, including normal cross-turn continuation loss.
- [ ] Results either meet P001 thresholds or produce a durable next experiment based on evidence.

Acceptance progress: **4 / 6**

## Evidence-pipeline repair

The epoch-43 to epoch-58 measurement blackout was caused by missing explicit prospective capture responsibility, not by proof of idle time. Epoch 59 repaired this with guarded append tooling, focused tests, integrated CI, mandatory wake loading, and worker capture rules. Historical unknown time remains unknown.

## First resumed bounded-turn result

Epoch 59: 626 wall seconds, 557 strict useful seconds (88.98% wall coverage; 92.83% of the 600-second useful target). This materially improves the historical tiny-packet pattern but is not itself a fixed 900-second P0 window.

## Current dominant cause: continuation-latency ceiling

P0 requires 840/900 = 93.33% useful coverage. With a 600-second bounded useful turn, average non-useful cross-turn loss must stay <=42.9 seconds. The current nominal 60-second post-close rearm offset already exceeds that budget before scheduler delivery latency and startup/checkpoint overhead. A prior production sample observed about 64 seconds of scheduler delivery delay after due.

Therefore the active post-close continuation cadence cannot reliably pass P0 even with perfect in-turn execution.

## Active correction — UTIL-EXP-018

Guarded predictive same-canonical successor prearm:

1. retain the 780-second provisional cold-rescue horizon;
2. near bounded close, arm the same canonical successor for a due boundary before target close;
3. predecessor continues useful work through close rather than yielding to the arm;
4. if successor appears while predecessor is still fresh/conflicting, successor may fence/read/observe but cannot claim substantive authority or duplicate side effects;
5. measure predecessor last useful boundary -> successor first useful boundary directly;
6. rollback on unsafe overlap, duplicate side effect, schedule rollback, or missed successor.

Promotion requires at least two safe canary handoffs with post-close gap <=42 seconds, then a valid fixed 900-second window.

## Exact resume step

Complete `PREARM-CANARY-001` for epoch 60. Record predictive due, successor observation, predecessor last useful boundary, successor first useful boundary, post-close gap, and overlap/fence result. If safe and <=42 seconds, repeat once before promotion. If not, classify the measured failure and choose the next highest-effect correction rather than repeating blindly.

## Decision rule

Any rule/control/process change is valid if its net expected contribution to P001 is positive. More rules are acceptable when they materially improve the outcome; fewer rules are preferable only when protection/effect is preserved or improved.
