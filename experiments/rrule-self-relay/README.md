# Experiment: RRULE Self-Relay

## Objective

Verify that one recurring ChatGPT automation can preserve its canonical ID and recurring RRULE while rotating `BYMINUTE` to produce an effective 15-minute relay, with GitHub as durable state.

## Previously observed evidence

The mechanism was previously short-run reproduced in live ChatGPT automation use:

- same canonical automation reused;
- recurring RRULE preserved;
- phase transitions `:00 -> :15 -> :30 -> :45` were successfully applied;
- later scheduled runs occurred;
- work was checkpointed and continued by subsequent scheduled runs;
- the automation was explicitly disabled after the earlier test.

## RRuleR validation ledger

Canonical automation:

`6aaf8a993eb08191b8d0ab1d9662e4b2`

### Bootstrap run — 2026-09-20 KST

1. Re-enabled the same canonical as recurring:
   `RRULE:FREQ=HOURLY;BYMINUTE=30;BYSECOND=0`.
2. Started substantive RRuleR work immediately rather than waiting for the scheduled boundary.
3. Created bootstrap/control/state/architecture/relay documents.
4. Added `.github/workflows/validate-control-plane.yml`.
5. GitHub Actions run `35505295915` completed with `success`.
6. While the bootstrap run remained active past the 19:30 boundary, automation metadata did not show a concurrent scheduled successor. Correctness therefore does **not** depend on same-canonical overlap/queue behavior.
7. The same recurring canonical was then moved to:
   `RRULE:FREQ=HOURLY;BYMINUTE=45;BYSECOND=0`,
   `DTSTART=2026-09-20 19:45 KST`.
8. Durable checkpoint `CP-BOOTSTRAP-002` instructs that scheduled successor to reconstruct from GitHub and continue.

### Checklist

- [x] Public-safe durable repo exists.
- [x] Bootstrap and relay reproduction guide persisted.
- [x] Same canonical automation re-enabled as recurring RRULE.
- [x] First RRuleR-era recurring phase transition recorded (`:30 -> :45`).
- [ ] Second RRuleR-era phase transition recorded by scheduled successor.
- [ ] A later scheduled wake reads `state/CURRENT.json` and continues substantive work.
- [ ] Final continuation cycle recorded without runtime-timeout loss.

## Correctness boundary

Queued or concurrent predecessor/successor execution is **not** required for PASS. The safe baseline is:

`durable checkpoint -> clean stop -> later scheduled wake -> GitHub reconstruction -> resume`.

Overlap, if ever observed, is an optimization only.

## Failure classification

If phase self-update fails but the previous hourly RRULE is verified intact, record `DEGRADED_CONTINUATION` and the expected fallback wake. If no valid wake remains, record a continuation failure requiring external recovery.
