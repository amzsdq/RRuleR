# RRULE Self-Update Relay — Current Guide

Status: **completion-relative SAME MAIN mechanism active; quarter-phase rotation is historical**

## Current mechanism

One authoritative recurring ChatGPT automation is the normal MAIN continuation actor. GitHub holds durable state and dynamic policy. The current MAIN keeps a recurring hourly RRULE and self-shifts its DTSTART:

```text
wake
 -> minimum fence + BOOT_STARTED
 -> provisional SAME MAIN recurring crash-insurance beyond bounded turn
 -> REARM_VERIFIED
 -> fresh ACTIVE_CONTROLS policy sync
 -> bounded useful work
 -> actual END
 -> SAME MAIN exact END+60 while preserving recurrence
 -> live verify
 -> persist coherent close projection
 -> return CONTINUE
```

The automation ID does not change. Normal continuation never creates a replacement MAIN and never converts the current MAIN to one-shot.

## Required invariants

- exactly one current authoritative MAIN canonical;
- retired MAIN canonicals never reactivate;
- current MAIN remains enabled and recurring while program is nonterminal;
- `timing_mode=exact_schedule`;
- fresh GitHub durable state/policy is authoritative for dynamic execution;
- generation-matched `BOOT_STARTED` and `REARM_VERIFIED` are observed, not inferred;
- normal `CONTINUE` close requires live SAME MAIN exact END+60 verification;
- the recurring SAME MAIN RRULE is the cold fallback if a shifted fast wake is lost;
- Watchdog is disabled break-glass standby, not normal continuity;
- stale wakes recover forward and never roll schedule/authority/checkpoint backward;
- normal nonterminal `CONTINUE` has a 600-second voluntary hard floor;
- no padding, sleeping, fabricated timestamps, or invented work.

## Fresh-policy synchronization

Every wake reads fresh `control/ACTIVE_CONTROLS.json` and all artifacts it currently marks mandatory before substantive work. Prior-wake cached policy cannot override fresh durable policy. The reservation prompt is a bootstrap/survival kernel, not the dynamic policy authority, except explicit operator and canonical-safety invariants.

## 600-second bounded-turn rule

Before 600 observed elapsed seconds, a normal nonterminal `CONTINUE` owner chains the next clear low-risk checkpointable authorized unit. Oversized units are decomposed; CI/external waits use an independent fallback/residual unit when available.

Packet/substep/checkpoint completion, CI pending/success, secured continuation, schedule boundaries, or `nothing obvious` do not authorize voluntary pre-600 close.

Earlier end is only explicit STOP/PAUSE, durable program terminal, genuine BLOCKED/fail-closed authority/safety state with no safe authorized work, or platform-enforced termination. At/after 600 seconds, stop starting new large units and finish the smallest safe in-flight unit; ~720 seconds is the normal soft ceiling.

## Normal close algorithm

1. Persist the latest useful checkpoint.
2. Observe actual END.
3. Compute exact `END+60s`.
4. Update THIS SAME MAIN to that DTSTART while preserving its recurring RRULE and enabled state.
5. Re-read live metadata and require same canonical + `is_enabled=true` + recurrence + exact DTSTART.
6. Persist the same verified fast due to CURRENT/ACTIVITY/HANDOFF and validate the non-WORKING close projection.
7. Persist observed turn/evidence boundaries.
8. Only then emit normal `STATUS=CONTINUE`.

A long provisional due cannot satisfy normal close. If fast rearm fails, retry once when safe. If an older verified recurring fallback survives, classify `DEGRADED_CONTINUATION`; do not claim normal close and do not create a replacement MAIN.

## Cold fallback

If a shifted fast wake is lost before successful bootstrap, the SAME MAIN's natural recurring hourly occurrence is the cold recovery opportunity. It reads fresh durable state, fences against any live owner, preserves the newest schedule generation, and continues forward.

This cold fallback cannot guarantee recovery from a disabled/deleted/platform-broken automation. Watchdog remains an explicitly activated break-glass mechanism for diagnosed emergencies only.

## Historical quarter-phase mechanism

Earlier experiments rotated hourly RRULE phase through `:00 -> :15 -> :30 -> :45`. Those experiments remain useful historical evidence for same-canonical RRULE mutation, but quarter-phase rotation and successor-observed predecessor handoff are **not current production semantics** and must not be reconstructed from this repository's history.

## Measurement

Keep scheduled due, actual invocation, `BOOT_STARTED`, `REARM_VERIFIED`, authority claim, first durable useful work, predecessor useful boundaries, actual END, verified next due, and provider delivery delay distinct. START-to-END elapsed time is not automatically productive time. Missing evidence remains unknown.

## Reproduction / rollback

Use current machine-readable controls and tests for acceptance. For the v5.2 fresh-policy-sync/600-second-floor change, the pre-change repository baseline is preserved on `rollback/pre-policy-sync-bootstrap-20260922`; rollback must reconcile forward on the SAME current canonical rather than reactivating retired MAINs or restoring stale operational state wholesale.
