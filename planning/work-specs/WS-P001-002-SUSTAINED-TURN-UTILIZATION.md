# WS-P001-002 — Sustained Turn Utilization

Status: **ACTIVE**  
Parent project: [P001 — Sustained Utilization & Continuous Execution](../projects/P001-SUSTAINED-UTILIZATION.md)

## Problem

Continuation survival is high, but useful-work occupancy must meet a SaaS-grade P0 target. Measurement freshness was previously broken, and after repairing it the active normal-continuation cadence was shown to have a theoretical utilization ceiling below the target.

## Outcome

Make bounded wakes spend most eligible wall-clock time on substantive authorized work and make normal cross-turn continuation exact. The active operator-locked P0 is two-part: **P0-A** sustain at least 10 minutes (600 observed elapsed seconds) on a normal nonterminal `CONTINUE` turn unless a truthful early-exit exception applies; **P0-B** currently canaries rearming the SAME enabled recurring MAIN at ACTUAL END + exactly 2 minutes (120 seconds), live-verifying the exact `DTSTART`, and measuring provider delivery/startup delay separately. Historical +1 minute (60 seconds) samples remain evidence and are not rewritten.

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

P0 requires 840/900 = 93.33% useful coverage. With a 600-second bounded useful turn, average non-useful cross-turn loss must stay <=42.9 seconds. Both the historical 1-minute (60-second) and current 2-minute (120-second) post-close offsets exceed that budget before scheduler delivery latency and startup/checkpoint overhead. The 2-minute value is therefore a stability canary, not a claim that it can satisfy the final utilization target by itself.

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

A live operator mutation proved that the SAME MAIN scheduler accepts an earlier recurring `DTSTART`; the long wait was not a platform minimum. The active policy itself had been arming the in-flight crash-insurance due at `target 10 minutes (600 seconds) + 3 minutes (180 seconds) safety = 13 minutes (780 seconds)`, which made a normal 10-minute (600-second) turn look like it needed a 13-minute (780-second) successor horizon.

The first attempted correction, routine `NOW + 2 minutes (120 seconds)` short rolling refresh, is **rejected as the normal strategy** because prior controlled A/B evidence showed an overlapping duplicate invocation under repeated short rolling. The selected v5.4 correction is therefore workload-relative rather than aggressively rolling:

- normal nonterminal turn hard floor remains 10 minutes (600 observed elapsed seconds);
- arm the SAME MAIN once at observed wake/arm reference + exactly 11 minutes (660 seconds) (10-minute / 600-second target + 1-minute / 60-second safety);
- normally perform no mid-turn schedule mutation;
- only if useful work or required close handling clearly threatens the provisional due, extend SAME MAIN once before collision, preferably to `NOW + exactly 3 minutes (180 seconds)`, and verify it;
- the current normal-close canary replaces the provisional due with exact observed `ACTUAL END + exactly 2 minutes (120 seconds)` on the SAME recurring MAIN;
- natural hourly recurrence remains cold fallback if a shifted occurrence fails before durable bootstrap;
- Watchdog remains disabled break-glass standby.

The 01:38 generation is the first live v5.4 verification turn. It durably wrote generation-matched `BOOT_STARTED`, live-verified SAME MAIN enabled recurring at 01:48:17 KST, and persisted `REARM_VERIFIED`. Fresh-policy audit then found two stale 780-second authorities outside the primary lifecycle: the integrated CI assertion and `control/runtime-continuity.v1.json`. Both were repaired forward; integrated control-plane validation subsequently passed after working-owner/handoff projection was reconciled. This demonstrates why fresh policy synchronization must include validators and secondary mandatory controls, not only the headline lifecycle artifact.

## v5.6.5 final-writer + observability correction

Epochs 89-90 established two separate facts that must not be conflated:

1. A shifted SAME MAIN recurring `DTSTART` can produce a same-hour eligible successor. Epoch 89 arrived 159 seconds after its shifted target; epoch 90 arrived 59 seconds after the epoch-89 final target. Provider delivery remains variable, but shifted RRULE execution is not categorically ignored.
2. Intermediate progress text from a scheduled invocation is not a reliable execution receipt. Durable work/state can advance even when no intermediate chat trace is visible. Therefore execution evidence and UI-delivery evidence are separate domains.

Selected correction: retain the minimal SAME MAIN full-VEVENT RRULE mechanism and change trace observability to **durable capture first, immediate delivery when supported, ordered final-response flush otherwise**. A missing intermediate UI message is no longer classified as execution failure when durable unit evidence exists. Conversely, a visible message never proves work unless the corresponding durable evidence exists.

This correction is deliberately narrow. It does not relax the 600-second P0-A floor. Recent short CONTINUE turns remain failures of sustained utilization even when their scheduler mutation and durable bookkeeping are correct.

## v5.7.1 +2-minute stability canary

The operator changed the final completion-relative offset from +1 minute (60 seconds) to +2 minutes (120 seconds) to test whether the larger gap improves actual wake stability. This is a controlled timing canary, not a new utilization target. Every eligible wake must still begin useful work even if provider invocation is early or late; clock mismatch alone is not a fence. Compare +120 against historical +60 using successful shifted-wake rate, actual provider offset, overlap/conflict rate, inter-turn idle gap, and useful-work duty cycle. Keep historical +60 observations intact for comparison.

## Exact resume step

Continue `UTIL-EXP-019` with five observed boundaries: invocation, `BOOT_STARTED`, provisional `REARM_VERIFIED`, authority claim, and first durable useful work. Preserve missing boundaries as unknown. Keep the v5.7.1 final-writer rule: provisional scheduling is crash insurance only; every normal nonterminal close must make the SAME MAIN full recurring VEVENT at observed ACTUAL END + exactly 2 minutes (120 seconds) the final scheduler mutation. Capture bounded-unit traces durably and flush them in the user-visible completion response if reliable intermediate delivery is unavailable.

## Decision rule

Any rule/control/process change is valid if its net expected contribution to P001 is positive. More rules are acceptable when they materially improve the outcome; fewer rules are preferable only when protection/effect is preserved or improved.

## Chained-turn execution policy

Normal nonterminal `CONTINUE` has a **10-minute (600-second) voluntary hard floor**, not an 8-minute (480-second) floor or a soft 10-minute (600-second) target.

- Before 10 minutes (600 observed elapsed seconds), if a bounded unit completes, immediately execute the next clear low-risk checkpointable authorized unit from this work spec/project.
- If the next obvious unit is too large, decompose it and execute a smaller safe slice. If it is waiting on CI/external evidence, choose an independent fallback/residual authorized unit.
- CI pending, packet/substep/checkpoint completion, secured continuation, or `nothing obvious` do not authorize a voluntary pre-10-minute (pre-600-second) normal `CONTINUE` close.
- Earlier end is reserved for explicit operator STOP/PAUSE, durable program terminal state, a genuine BLOCKED/fail-closed authority or safety condition with no safe authorized work, or platform-enforced termination; record the corresponding status/reason rather than normal CONTINUE.
- At 10 minutes (600 elapsed seconds) or later, do not start a new large unit; finish only the smallest safe in-flight unit, checkpoint, and hand off.
- Normal turns should usually close between 10 minutes (600 seconds) and about 12 minutes (720 seconds) elapsed. Going beyond about 12 minutes (720 seconds) requires a genuine in-flight safety/atomicity reason.

This policy increases useful work by pulling forward already-authorized work. It does not authorize padding, splitting trivial changes, fabricating activity, or fabricating timestamps.

## Operator-locked P0 decision procedure

Until superseded by explicit operator direction, every candidate change must be scored primarily against P0-A and P0-B:

1. Observe the current failure/bottleneck from durable evidence.
2. Separate turn-worktime loss from schedule/rearm/provider-delay loss.
3. Check existing/proven mechanisms before inventing a new one.
4. Prefer the smallest reversible candidate with the highest expected effect.
5. Keep the evaluator and acceptance target fixed while testing the candidate.
6. Compare before/after evidence and decide `ADOPT`, `REVISE`, `ROLLBACK`, `REJECT`, or `DO_NOTHING`.
7. Do not promote a change because configuration or CI changed; require live runtime evidence.

Broader productization remains deferred unless it directly advances one of these P0s or preserves a hard safety/correctness invariant.

## Distribution reporting note

The current evidence-bound chat trace is a debugging/canary surface. The intended distribution version preserves exact structured telemetry internally but renders each turn to the user in concise natural language covering observed work period, what was completed, current status, and what happens next. Scheduled runtimes must not depend on intermediate-message delivery for correctness: persist traces first, then deliver immediately if supported or flush them in order at final completion. Do not replace internal machine evidence with prose.
