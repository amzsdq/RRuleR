# RRuleR Operations Runbook

## Bootstrap order for any fresh ChatGPT session

1. Read `AGENTS.md`.
2. Read `control/POLICY.md`.
3. Read `state/CURRENT.json`.
4. Read the document or experiment referenced by `checkpoint.next_action`.
5. If this is a scheduled relay wake, update and verify the same recurring automation before substantive work.
6. Start work immediately after wake verification.

## Normal loop

```text
LOAD durable state
 -> VERIFY authority
 -> ARM/VERIFY next wake
 -> WORK
 -> CHECKPOINT when useful
 -> CONTINUE working
 -> successor actually observed?
      no  -> continue work
      yes -> finish smallest safe unit
             -> HANDOFF checkpoint
             -> predecessor ends
```

## Stop conditions

A non-terminal run must not stop merely because:

- a file was completed;
- a milestone was reached;
- a checkpoint was written;
- the quarter-hour boundary arrived;
- the next scheduled time is near.

Normal stop is allowed only for:

- terminal `COMPLETE`;
- proven `BLOCKED_EXTERNAL`;
- successor-triggered handoff;
- platform-enforced runtime termination.

## Recovery

### Self-update failure with old RRULE intact

Record `DEGRADED_CONTINUATION`. Preserve the old recurring schedule as the slower recovery opportunity. Do not claim the fast 15-minute path succeeded.

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

## Completion gate

Before `COMPLETE`:

- final durable state is internally consistent;
- required documents validate;
- relay evidence satisfies the acceptance checklist;
- the same canonical automation is disabled;
- no successor is scheduled.
