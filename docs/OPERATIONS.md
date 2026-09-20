# RRuleR Operations Runbook

## Bootstrap order for any fresh ChatGPT session

1. Read `AGENTS.md`.
2. Read `control/POLICY.md`.
3. Read `control/relay-policy.v1.json`.
4. Read `state/CURRENT.json` and `state/ACTIVITY.json`.
5. Read the document or experiment referenced by `checkpoint.next_action`.
6. If this is a scheduled relay wake, verify the same recurring automation before substantive work.
7. Mark activity WORKING and start substantive work immediately.

## Normal loop

```text
LOAD durable state
 -> VERIFY authority
 -> VERIFY recurring next wake
 -> ACTIVITY=WORKING
 -> WORK
 -> CHECKPOINT/ACTIVITY refresh when useful
 -> CONTINUE working
 -> current root complete?
      yes -> persist root terminal evidence
             -> materially useful next root exists?
                  yes -> persist/chains next root and continue
                  no  -> evaluate PROGRAM_COMPLETE
 -> successor actually observed?
      no  -> continue work
      yes -> finish smallest safe unit
             -> HANDOFF checkpoint + activity
             -> predecessor ends
```

## Stop conditions

A non-terminal program must not stop merely because:

- a file was completed;
- a milestone was reached;
- a checkpoint was written;
- a root job was completed;
- a recurrence boundary arrived;
- the next scheduled time is near.

Normal stop is allowed only for:

- verified `PROGRAM_COMPLETE`;
- explicit operator stop;
- proven `BLOCKED_EXTERNAL` with internal alternatives exhausted;
- successor-triggered handoff;
- platform-enforced runtime termination.

## Operator UI interpretation

The composer icon is useful but not authoritative:

- a stop button indicates the foreground turn is generating;
- a send button/idle composer indicates that foreground turn is over;
- a separate scheduled run may still be active even when the foreground is idle.

Operationally, however, a predecessor that still owns useful work should not voluntarily return to idle UI before a successor is observed. If idle UI is seen and `state/ACTIVITY.json` is stale with no successor, classify a utilization gap and restore continuation.

## Recovery

### Recurrence damaged but old RRULE intact

Record `DEGRADED_CONTINUATION`. Preserve the surviving recurrence as a recovery opportunity. Do not claim the preferred cadence succeeded.

### No valid continuation wake

Persist the incident in durable state. Do not pretend continuation exists. External/operator recovery is required.

### Ambiguous side effect

Do not replay. Reconcile durable evidence first.

## Public-repository hygiene

Never persist:

- credentials;
- access tokens;
- cookies/session storage;
- private chat content;
- private repository content;
- personal data.

Use public-safe opaque references where necessary.

## Program completion gate

Before `PROGRAM_COMPLETE`:

- current root is terminal with evidence;
- no materially useful authorized next root remains;
- final durable state is internally consistent;
- required documents validate;
- the same canonical automation is disabled;
- no successor is scheduled.

A root-level COMPLETE alone does not satisfy this gate.
