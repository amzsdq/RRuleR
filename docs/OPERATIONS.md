# RRuleR Operations Runbook

## Fresh-wake bootstrap

1. Read fresh `state/NOW.json`; obey explicit STOP/PAUSE/terminal state.
2. Perform minimum CURRENT/canonical/fence validation and persist generation-matched `BOOT_STARTED`.
3. Provisional-arm THIS SAME current MAIN beyond the bounded turn, verify enabled + recurring + intended due, then persist `REARM_VERIFIED`.
4. Read fresh `control/ACTIVE_CONTROLS.json` and every artifact it currently marks mandatory. Prior-wake cached policy is not authority.
5. Reconstruct PROGRAM -> PROJECT -> WORK SPEC -> TURN_PLAN and current authority.
6. Mark the active run WORKING and begin substantive authorized work.

## Normal loop

```text
NOW / minimum fence
 -> BOOT_STARTED
 -> provisional SAME MAIN recurring rearm + verify
 -> REARM_VERIFIED
 -> fresh ACTIVE_CONTROLS policy sync
 -> claim/verify authority
 -> WORKING
 -> bounded useful unit
 -> elapsed <600s ?
      yes -> select next safe authorized unit / decompose / fallback
      no  -> stop starting new large units
             -> finish smallest safe in-flight unit
             -> checkpoint
             -> observe actual END
             -> SAME MAIN exact END+60, preserve recurrence
             -> live verify + persist coherent close projection
             -> CONTINUE final
```

## 600-second normal CONTINUE hard floor

Normal nonterminal `CONTINUE` cannot voluntarily close before 600 observed elapsed seconds. Before 600 seconds, continue with the next clear low-risk checkpointable authorized unit. Oversized units are decomposed; CI/external waits use independent fallback/residual work when available.

The following are not pre-600 close conditions:

- packet/substep/checkpoint completion;
- CI pending or CI success;
- secured continuation;
- `nothing obvious`;
- a schedule boundary.

Earlier end is reserved for explicit operator STOP/PAUSE, durable program terminal state, genuine BLOCKED/fail-closed authority/safety state with no safe authorized work, or platform-enforced termination. Use the corresponding status/reason. Never pad or fabricate work.

At/after 600 seconds, finish only the smallest safe in-flight unit. ~720 seconds is the normal soft ceiling.

## Normal continuation topology

Normal continuation is self-reliant SAME MAIN continuation:

`MAIN -> SAME MAIN at actual END+60 -> MAIN`

The current MAIN remains recurring and enabled. The provisional due is in-flight crash insurance only. A normal close is not valid until live metadata proves same canonical + enabled + recurrence + exact END+60 DTSTART and that same due is persisted coherently to CURRENT/ACTIVITY/HANDOFF.

The recurring MAIN RRULE is the cold fallback if a shifted fast wake is lost. Watchdog is disabled break-glass standby and is not armed or synchronized during normal close. Never create a replacement MAIN merely to continue and never reactivate retired MAIN canonicals.

## Stop conditions

A nonterminal program must not stop merely because a file, milestone, checkpoint, root, CI run, local objective, or recurrence boundary completed.

Program-level end states are:

- verified `PROGRAM_COMPLETE`;
- explicit operator STOP/PAUSE;
- genuine external/safety BLOCKED state with internal alternatives exhausted;
- platform-enforced termination of the current invocation.

A normal bounded `CONTINUE` close is not program termination; it requires verified SAME MAIN continuation.

## Recovery

### Fast rearm fails but older recurring fallback remains

Retry the fast rearm once when safe. If exact END+60 still cannot be proven but an older verified recurring SAME MAIN fallback remains, record `DEGRADED_CONTINUATION`; do not claim normal close.

### Shifted fast wake is lost

Recover forward on the SAME MAIN natural recurring occurrence from fresh durable state. Do not require Watchdog and do not create a replacement MAIN.

### Ambiguous side effect

Do not replay blindly. Reconcile durable evidence and idempotency/fencing first.

### Stale wake

Preserve the newest verified schedule generation and authority. Never roll DTSTART, canonical lineage, checkpoint, or authority backward.

## Measurement

Record scheduled due, actual invocation, `BOOT_STARTED`, `REARM_VERIFIED`, authority claim, first durable useful work, actual END, verified next due, and provider delivery delay as distinct observations when available. START-to-END elapsed time is not automatically useful time.

## Public-repository hygiene

Never persist credentials, tokens, cookies/session state, private chat content, private-repository content, personal data, or other secrets. Use public-safe state and references only.

## Program completion gate

Before `PROGRAM_COMPLETE`, require durable evidence that overall program acceptance is met and no materially useful authorized continuation remains. Only then may the current MAIN be disabled. Local root/project completion alone is not sufficient.
