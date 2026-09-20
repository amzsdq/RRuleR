# Experiment: RRULE Self-Relay

## Objective

Verify that one recurring ChatGPT automation can preserve its canonical ID and recurring RRULE while rotating `BYMINUTE` to produce an effective 15-minute relay, with GitHub as durable state.

## Previously observed evidence

The mechanism has already been short-run reproduced in live ChatGPT automation use:

- same canonical automation reused;
- recurring RRULE preserved;
- phase transitions `:00 -> :15 -> :30 -> :45` were successfully applied;
- later scheduled runs occurred;
- work was checkpointed and continued by subsequent scheduled runs;
- the automation was later disabled explicitly after the test.

These observations establish mechanism feasibility. RRuleR will now record fresh repository-backed continuation evidence so a cold successor can reproduce the process from GitHub.

## Current RRuleR validation

Canonical automation:

`6aaf8a993eb08191b8d0ab1d9662e4b2`

Validation checklist:

- [x] Public-safe durable repo exists.
- [x] Bootstrap and relay reproduction guide persisted.
- [x] Same canonical automation re-enabled as recurring RRULE.
- [ ] Two RRuleR-era phase transitions recorded.
- [ ] A later scheduled wake reads `state/CURRENT.json` and continues work.
- [ ] Final continuation result recorded without runtime-timeout loss.

## Correctness boundary

Queued or concurrent predecessor/successor execution is **not** required for PASS. The correctness baseline is durable checkpoint + clean stop + later scheduled wake + resume.

## Failure classification

If phase self-update fails but the previous hourly RRULE is verified intact, record `DEGRADED_CONTINUATION` and the expected fallback wake. If no valid wake remains, record a continuation failure requiring external recovery.
