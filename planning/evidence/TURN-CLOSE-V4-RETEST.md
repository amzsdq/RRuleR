# Turn-close v4 retest

Scope: WS-P001-002. Operator-authorized repair of premature bounded-turn close.

## Implemented

- One close decision in run-continuation-gate v4; completing a small unit alone never permits close.
- Runnable primary/fallback/residual task selection in the existing TURN_PLAN.
- Pause check before write batches and scheduler mutation.
- Elapsed time separated from accepted useful work.
- New closed records validated in CI, including omitted duration/outcome and unsupported short-close reasons. Pre-migration observations remain historical evidence, not rewritten successes.
- Validation boundary: turns starting on or after 2026-09-21T09:35:00Z.

## Next worker's runnable work

Check fresh state before choosing; skip already accepted work.

1. Primary: implement `tools/summarize_turn_close.py` to report v4 closed-turn counts, unexcused short closes, known useful seconds, unknown-useful count and explicitly observed successor gaps from RUNS/SUCCESSOR_STARTUP. Acceptance: missing useful seconds and missing successor boundaries remain unknown, never zero; add focused fixtures. No future wake dependency. Estimate 3-5 minutes, checkpoint at pure function plus fixtures; conflict domain turn-close-reporting.
2. Independent fallback: implement a read-only STARTUP ledger consistency audit. Acceptance: flag predecessor last-useful later than that predecessor's recorded end; exclude operator-maintenance-interrupted samples from scheduler comparison, while preserving raw evidence. Target `tools/audit_startup_boundaries.py` and focused tests. No schedule mutation or future wake required. Estimate 2-4 minutes; checkpoint at audit plus fixtures; conflict domain startup-evidence-audit.
3. Residual item: inspect current bounded-close CI result and document concrete baseline/candidate evidence in this file. Acceptance: link exact commit/run result and separate local tests from Actions and live behavior. Estimate 1-2 minutes; checkpoint at evidence update. If CI is pending, select another acceptance item; do not repeatedly poll as useful work.

These are implementation candidates, not duplicate-work mandates. Record actual estimates and runnable status in TURN_PLAN. If all finish, choose the next unaccepted item within WS-P001-002. Do not end simply because this list completed.

## Retest implementation evidence

- Strict close summary: `tools/summarize_turn_close.py` and focused fixtures. It reports post-v4 closed turns, unexcused short CONTINUE closes, known useful seconds, unknown-useful count, and successor gaps only from complete observed boundaries.
- STARTUP consistency audit: `tools/audit_startup_boundaries.py` and focused fixtures. It resolves `RUN-...` predecessor IDs against `OBS-RUN-...` observations, preserves raw evidence, and excludes maintenance-interrupted or boundary-inconsistent samples from scheduler comparison.
- CI correction: the earlier `744eeeda5e3351ddb84bff95951c0ebe2061257a` write was a no-op despite returning a commit response. Commit `19d7f002fc4b8b22bd962deb3bb7ab07de301b5f` is the first blob-verified integration and fetches/executes turn-close summary, STARTUP audit, exact-second due computation, review generation, and their tests. External Actions result is not yet observed.
- Local execution: seven focused assertions passed via direct function invocation because pytest is unavailable in the current execution image. This is not an Actions pass and not live efficacy proof.
- Actual-ledger audit found STARTUP-002 invalid: its `predecessor_last_useful_at=18:15:00 KST` is later than the matched predecessor end `18:12:54 KST`. Raw timestamps remain unchanged; the sample is durably marked `BOUNDARY_INCONSISTENCY` and excluded. Therefore the previously cited 155-second scheduler estimate is not validated evidence.
- Post-v4 live closed-turn count was zero before this current turn closes. Three prospective valid turns permit only an initial review, not a conclusive efficacy claim or termination.

## Live acceptance

Collect at least three valid completed post-repair turns with runnable backlog. Report each observed elapsed duration, known useful duration (or unknown), exception evidence, control/close overhead where observed, and successor gap where observed. Explicit pauses and forced termination are exclusions, not successes. No unexcused early CONTINUE close is allowed; do not call the repair effective solely because elapsed duration grew. Useful output must increase without duplicate/conflicting writes. Scheduler latency remains a separate outcome. Retain the 10-minute envelope and existing ownership fences. Do not promote scheduler timing from this repair.


## Per-turn live review

| Run | Observed start → end | Elapsed | Accepted useful | Control/close | Successor gap | Close | Runnable alternatives | Validity | Artifact / CI evidence | Dominant supported cause | Next corrective action |
|---|---|---:|---:|---:|---:|---|---|---|---|---|---|
| OBS-RUN-UTIL-20260921-184232 | 18:42:32 → 18:51:46 KST | 554s | UNKNOWN | UNKNOWN | 387s (valid STARTUP-003) | BUDGET_EXHAUSTED; verified same-canonical continuation | CI result unavailable; STARTUP-003 future boundary; 900s window did not fit | ELIGIBLE CLOSED TURN; run validator passed; no pause/forced termination | reporting/audit tools, focused assertions, CI integration; Actions result not yet observed | useful-work measurement incomplete; elapsed improvement alone is not efficacy proof | correct end→due timing with exact-second +60s rearm; append prospective artifact-backed WORK_EVIDENCE |

| OBS-RUN-UTIL-20260921-185559 | 18:55:59 → 19:04:23 KST | 504s | 368s | UNKNOWN | UNKNOWN total; due→invocation 30s observed, claim/first-useful missing | BUDGET_EXHAUSTED; verified same-canonical continuation | Actions result unavailable; own review required successor; 900s window did not fit | ELIGIBLE CLOSED TURN; run validator passed; successor sample incomplete | 3 accepted WORK_EVIDENCE intervals; exact-second helper/policy; validity-aware review; blob-verified CI wiring | successor invoked but left no durable claim/useful progress; provider delivery itself was 30s | add missing-successor-progress diagnostic; collect a clean normal END+60 sample |\n\n| OBS-RUN-UTIL-20260921-193957 | 19:39:57 → 19:48:15 KST | 498s | 385s | UNKNOWN | 3890s to hourly-fallback first useful; normal due→invocation 73s then STARTUP_ACK_MISSING | BUDGET_EXHAUSTED; verified exact END+60 continuation | Actions unavailable; third review required successor; no additional bounded implementation fit close reserve | ELIGIBLE CLOSED TURN; run validator passed; successor reliability failure | 2 accepted WORK_EVIDENCE intervals; successor-progress audit; CI workflow repair | invoked normal successor left no durable bootstrap/rearm/claim/useful evidence; hourly fallback dominated total gap | add BOOT_STARTED/REARM_VERIFIED, STARTUP_ACK_MISSING detection, and guarded independent-wake consumer gate |

Eligible completed live turns recorded here: **3**. Continuous collection has no fixed sample-count limit.

Status: continuous relay and measurement active; initial review after three eligible turns, then rolling review indefinitely.

## Operator review contract: elapsed, useful work, and failure attribution

Continue the authorized relay and collect at least three valid completed turns; do not stop the program when the sample count is reached. Append a readable per-turn review table here after each closed turn and update the conclusion after three eligible turns. Columns: run reference, observed start/end, elapsed seconds, accepted useful seconds or UNKNOWN, observed control/close seconds or UNKNOWN, observed successor gap or UNKNOWN, close reason, runnable alternatives, validity/exclusion, artifact/CI evidence, dominant supported cause, next corrective action. Never infer idle time by subtracting incomplete useful-work evidence from elapsed time.

Raw sources remain authoritative:
- state/RUNS.jsonl: start/end, elapsed duration, outcome, close decision and exceptions.
- state/WORK_EVIDENCE.json: prospective accepted useful intervals linked to actual artifacts; append during natural work boundaries, not only at final close.
- state/SUCCESSOR_STARTUP.json: scheduled due, observed invocation, authority claim and first useful boundary, including exclusions.
- state/TURN_PLAN.json and state/ACTIVITY.json: current stage and last observed progress.
- tools/validate_run_records.py: new closed-record validity; tools/summarize_turn_close.py and tools/audit_startup_boundaries.py: review helpers, not proof of work by themselves.

Attribute failures separately: premature voluntary close; runnable backlog exhausted; external dependency wait; scheduler delivery; bootstrap/authority acquisition; control/checkpoint overhead; operator interruption; platform termination if actually evidenced; missing/inconsistent measurement. A missing record is a measurement gap, not proof of idle time. Commit timestamps alone do not prove continuous active work between commits. Preserve unknown time.

Before accepting a summary, ensure it preserves validity/exclusion fields and excludes INVALID or maintenance-interrupted samples from comparison; merely printing every sample's numeric gap is insufficient. STARTUP-002 is currently invalid due to predecessor boundary inconsistency, so its 155-second figure must not drive scheduler promotion.

At close, persist the run and accepted useful evidence, run the validators, then append the readable result. If a write fails, state exactly which record is missing and leave the interval unknown. Keep historical raw evidence intact. Every successor checks whether its predecessor's close record is missing and flags that gap without inventing an end time. If normal close bookkeeping cannot include its own final timestamp, label the measured boundary accurately rather than claiming an exact later response-delivery time.

## Continuous relay directive (supersedes finite retest wording)

The existing RRuleR actor owns ongoing work, measurement and bottleneck review. There is no three-turn limit and no automatic shutdown after a sample count or successful measurement. Continue under the existing scheduler and supported platform capabilities until explicit operator pause/STOP; retain safety/authority fences and honestly report genuine blockers. Each invocation remains bounded to the existing 10-minute work envelope. Do not create a separate reviewer or spend another Work session on routine validation.

Accumulate every turn's raw observations and artifact-backed useful intervals. Three eligible turns are the first descriptive check only. Thereafter maintain a rolling view of the latest ten eligible turns alongside lifetime counts and missing/invalid counts. Normal operation gets a short incremental update, not a full audit every turn.

Run a focused bottleneck inspection immediately on an unexcused short close, failed close validator, contradictory timestamps, missing predecessor close record, duplicate/conflicting effect, or missing verified continuation. For performance drift, inspect when three consecutive eligible turns worsen against the preceding valid baseline in known useful coverage or observed successor gap. Require comparable measurements; insufficient data triggers capture repair, never invented performance estimates. These are diagnostic triggers, not statistical significance or promotion criteria.

Inspection flow: identify affected stage -> cite raw observations and exclude interrupted/invalid samples -> rank measured loss -> implement one authorized targeted correction -> record change boundary -> compare subsequent eligible samples. During external wait, continue independent authorized work. If no safe authorized work exists, record that state honestly and preserve permitted continuation; never fabricate work to fill time.

Do not label the program COMPLETE because the initial review, one repair, or a work item is complete. Select the next authorized project/work-spec item. Explicit STOP/pause always wins. Report findings in this document and the existing actor's conversation; no automatic callback to a separate reviewer is assumed.


## Initial three-turn review conclusion

The first three eligible post-repair turns lasted 554s, 504s, and 498s. Accepted useful time is UNKNOWN, 368s, and 385s respectively, so the sample does not prove the P0 threshold or a utilization improvement. More importantly, the third turn's exact END+60 successor was invoked 73s after due but left no durable bootstrap acknowledgement or progress; useful work resumed only on the next hourly fallback, producing an observed 3890s predecessor-last-useful to recovery-first-useful gap. In-turn chaining is promising, but pre-bootstrap recovery is now the dominant evidenced availability failure. Continuous collection remains active; three turns are a review checkpoint, not a stop condition.
