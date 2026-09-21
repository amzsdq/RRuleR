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

### v5.4 provisional-horizon correction

A live operator mutation proved that the SAME MAIN scheduler accepts an earlier recurring `DTSTART`; the long wait was not a platform minimum. The active policy itself had been arming the in-flight crash-insurance due at `target 600s + 180s safety = 780s`, which made a normal ~10-minute turn look like it needed a ~13-minute successor horizon.

The first attempted correction, routine `NOW+120s` short rolling refresh, is **rejected as the normal strategy** because prior controlled A/B evidence showed an overlapping duplicate invocation under repeated short rolling. The selected v5.4 correction is therefore workload-relative rather than aggressively rolling:

- normal nonterminal turn hard floor remains 600 observed elapsed seconds;
- arm the SAME MAIN once at observed wake/arm reference +660 seconds (600s target +60s safety);
- normally perform no mid-turn schedule mutation;
- only if useful work or required close handling clearly threatens the provisional due, extend SAME MAIN once before collision, preferably to `NOW+180s`, and verify it;
- normal close still replaces the provisional due with exact observed `END+60s` on the SAME recurring MAIN;
- natural hourly recurrence remains cold fallback if a shifted occurrence fails before durable bootstrap;
- Watchdog remains disabled break-glass standby.

The 01:38 generation is the first live v5.4 verification turn. It durably wrote generation-matched `BOOT_STARTED`, live-verified SAME MAIN enabled recurring at 01:48:17 KST, and persisted `REARM_VERIFIED`. Fresh-policy audit then found two stale 780-second authorities outside the primary lifecycle: the integrated CI assertion and `control/runtime-continuity.v1.json`. Both were repaired forward; integrated control-plane validation subsequently passed after working-owner/handoff projection was reconciled. This demonstrates why fresh policy synchronization must include validators and secondary mandatory controls, not only the headline lifecycle artifact.

## Exact resume step

Continue `UTIL-EXP-019` with five observed boundaries: invocation, `BOOT_STARTED`, provisional `REARM_VERIFIED`, authority claim, and first durable useful work. Treat the 01:38 v5.4 generation as a prospective provisional-horizon sample, but do not promote it until the turn closes normally at >=600s and the SAME MAIN exact `END+60` due is live-verified and projected consistently to CURRENT/ACTIVITY/HANDOFF. Preserve missing boundaries as unknown; do not infer scheduler or useful-work success from invocation metadata alone.

## Decision rule

Any rule/control/process change is valid if its net expected contribution to P001 is positive. More rules are acceptable when they materially improve the outcome; fewer rules are preferable only when protection/effect is preserved or improved.

## Chained-turn execution policy

Normal nonterminal `CONTINUE` has a **600-second voluntary hard floor**, not an 8-minute floor or a soft 10-minute target.

- Before 600 observed elapsed seconds, if a bounded unit completes, immediately execute the next clear low-risk checkpointable authorized unit from this work spec/project.
- If the next obvious unit is too large, decompose it and execute a smaller safe slice. If it is waiting on CI/external evidence, choose an independent fallback/residual authorized unit.
- CI pending, packet/substep/checkpoint completion, secured continuation, or `nothing obvious` do not authorize a voluntary pre-600s normal `CONTINUE` close.
- Earlier end is reserved for explicit operator STOP/PAUSE, durable program terminal state, a genuine BLOCKED/fail-closed authority or safety condition with no safe authorized work, or platform-enforced termination; record the corresponding status/reason rather than normal CONTINUE.
- At 600 elapsed seconds or later, do not start a new large unit; finish only the smallest safe in-flight unit, checkpoint, and hand off.
- Normal turns should usually close between 600 and about 720 elapsed seconds. Going beyond ~720 seconds requires a genuine in-flight safety/atomicity reason.

This policy increases useful work by pulling forward already-authorized work. It does not authorize padding, splitting trivial changes, fabricating activity, or fabricating timestamps.
