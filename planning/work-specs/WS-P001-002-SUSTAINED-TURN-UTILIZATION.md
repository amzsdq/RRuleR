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

## Continuation-latency ceiling

P0 requires 840/900 = 93.33% useful coverage. With a 600-second bounded useful turn, average non-useful cross-turn loss must stay <=42.9 seconds. A 60-second post-close rearm offset already exceeds that budget before scheduler delivery latency and startup/checkpoint overhead.

## UTIL-EXP-018 result — predictive prearm failed first canary

The first guarded predictive-prearm sample did not produce a P0-eligible handoff:

- predecessor last durable useful boundary: 17:11:53 KST;
- successor invocation observation: 17:11:58 KST;
- first durable useful successor mutation: 18:10:27 KST;
- predecessor-to-first-useful gap: 3514 seconds;
- duplicate substantive side effect observed: no;
- schedule rollback observed: no.

This falsifies predictive due placement as a sufficient correction for the observed path. The same intervention must not be repeated without new evidence.

## Active correction — UTIL-EXP-019

Separate successor startup into observed segments:

1. scheduled due -> successor invocation observation;
2. invocation observation -> nonconflicting authority claim;
3. authority claim -> first durable useful mutation.

`state/SUCCESSOR_STARTUP.json` is the prospective ledger. Missing boundaries remain unknown. Optimize the largest measured avoidable segment before changing scheduler due placement again.

Predictive prearm is rolled back; completion-relative same-canonical continuation is the active fallback while this experiment runs.

## Exact resume step

Continue `UTIL-EXP-019` with five observed boundaries: invocation, `BOOT_STARTED`, provisional `REARM_VERIFIED`, authority claim, and first durable useful work. `STARTUP-006` is the first confirmed `STARTUP_ACK_MISSING` sample and must retain unknown missing boundaries. The guarded event-rescue evaluator and workflow gate are implemented, but fast recovery is not active until a supported GitHub PR event consumer is provisioned, its bounded write probe passes, and an outstanding generation is atomically claimed. Do not report detection as recovery or repeat predictive prearm without new evidence.

## Decision rule

Any rule/control/process change is valid if its net expected contribution to P001 is positive. More rules are acceptable when they materially improve the outcome; fewer rules are preferable only when protection/effect is preserved or improved.

## Chained-turn execution policy

The primary utilization rule is now work-unit chaining rather than merely satisfying an 8-minute floor.

- If a bounded unit completes before 10 elapsed minutes, immediately execute the next clear, low-risk, checkpointable authorized unit from this work spec/project when it fits the remaining platform safety budget.
- If the next obvious unit is too large, decompose it and execute a smaller safe slice when possible.
- At 10 elapsed minutes or later, do not start a new large unit; finish only the smallest safe in-flight unit, checkpoint, and hand off.
- Normal turns should usually close between 10 and about 12 minutes. Going beyond ~12 minutes requires a genuine in-flight safety/atomicity reason.
- A CONTINUE close below 10 minutes must record why no safe next unit could be started; below 8 minutes remains a high-severity utilization failure unless an allowlisted exception applies.

This policy is intended to increase useful work by pulling forward already-authorized next work, not by padding, splitting trivial changes, or inventing activity.
