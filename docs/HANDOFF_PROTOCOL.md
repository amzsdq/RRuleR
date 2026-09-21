# SAME MAIN Continuation / Handoff Protocol

## Status

The older concurrent successor-triggered 14+1 handoff protocol is retired for normal operation. Current normal continuation uses the SAME authoritative MAIN recurring automation and an exact completion-relative close.

## Objective

Preserve logical work continuity with minimal idle time while preventing duplicate substantive execution, stale schedule rollback, and false close claims.

## Working state

During an active bounded turn:

- `CURRENT.current_owner` identifies the active run/authority epoch;
- `ACTIVITY.status=WORKING` and `active_run_id` matches the current owner;
- `TURN_PLAN` belongs to the same run/epoch;
- the SAME MAIN has a verified provisional recurring crash-insurance due beyond the bounded turn;
- Watchdog remains disabled standby.

## 600-second admission rule

Before 600 observed elapsed seconds, a normal nonterminal `CONTINUE` owner keeps selecting safe authorized work. Packet/checkpoint/CI completion or a future wake does not trigger handoff. At/after 600 seconds, stop starting new large units and finish the smallest safe in-flight unit; ~720 seconds is the normal soft ceiling.

## Normal close sequence

1. Finish the smallest safe in-flight unit.
2. Persist the latest checkpoint/evidence and exact resume target.
3. Observe actual END.
4. Compute exact `END+60s`.
5. Update THIS SAME MAIN to that exact DTSTART while preserving recurring RRULE and `is_enabled=true`.
6. Re-read live automation metadata and verify same canonical + enabled + recurrence + exact DTSTART.
7. Publish one coherent non-WORKING close projection:
   - `CURRENT.run_state=HANDOFF_COMMITTED`;
   - `ACTIVITY.status=HANDOFF_READY`;
   - `ACTIVITY.active_run_id=null`;
   - `ACTIVITY.handoff_ready=true`;
   - `HANDOFF.handoff_state=COMMITTED`;
   - CURRENT/ACTIVITY/HANDOFF carry the same verified next due and predecessor run/epoch.
8. Validate the close projection.
9. Only then emit normal `STATUS=CONTINUE`.

A long provisional due cannot satisfy normal close.

## Next wake

The next SAME MAIN wake:

1. reads fresh NOW and minimum fence state;
2. writes generation-matched `BOOT_STARTED`;
3. provisional-arms/verifies the SAME MAIN recurring fallback and writes `REARM_VERIFIED`;
4. reloads fresh ACTIVE_CONTROLS and mandatory policy;
5. reconciles the committed predecessor close;
6. claims a fresh nonconflicting authority epoch;
7. marks WORKING and resumes the exact durable next action.

No separate successor automation is required for normal continuation.

## Lost fast wake

If the shifted END+60 wake is lost before successful bootstrap, the SAME MAIN natural recurring hourly occurrence is the cold fallback. It recovers forward from fresh durable state and must not restore an older schedule generation or authority.

## Fast rearm failure

Retry once when safe. If exact END+60 still cannot be proven but an older verified recurring SAME MAIN fallback remains, classify `DEGRADED_CONTINUATION`; do not claim normal close and do not create a replacement MAIN.

## Historical overlap experiments

Earlier quarter-phase/predictive-prearm/successor-observed protocols remain historical evidence. They may inform future latency experiments, but they are not current normal authority semantics and must not be reconstructed merely because old evidence describes them.

## Safety invariants

- one substantive owner per authority epoch;
- duplicate substantive side effects forbidden;
- ambiguous irreversible effects reconcile before replay;
- stale wakes recover forward;
- retired MAIN canonicals never reactivate;
- Watchdog is disabled break-glass standby;
- local packet/project/root completion is not program completion.
