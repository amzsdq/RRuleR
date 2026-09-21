# P001 PREARM-CANARY-001

Status: **PREDECESSOR CLOSED / awaiting observed successor**  
Experiment: `UTIL-EXP-018`  
Predecessor: `RUN-UTIL-20260921-170146` / authority epoch 60

## Question

Can the same canonical successor be armed before predecessor close so scheduler delivery latency overlaps still-useful predecessor work, while preserving exactly one substantive authority owner and reducing the post-close useful-work gap to <=42 seconds?

## Why this canary exists

P0 requires 840 useful seconds in a 900-second fixed window (93.33%). With a 600-second useful turn, average non-useful cross-turn loss must be <=42.9 seconds. The verified fallback's nominal 60-second post-close due already exceeds that budget before scheduler jitter/startup. A prior production sample observed about 64 seconds of scheduler delay after due.

A 30-second predictive lead would yield a predicted ~34-second post-close observation gap if that ~64-second delay repeated. This prediction is not evidence.

## Armed parameters

- predecessor observed start: `2026-09-21 17:01:46 KST`
- target bounded close: `2026-09-21 17:11:46 KST`
- predictive same-canonical due: `2026-09-21 17:11:16 KST`
- predictive lead: `30s`
- provisional cold-rescue horizon: unchanged at `780s`
- same canonical: `6aaf8a993eb08191b8d0ab1d9662e4b2`

## Predecessor close readiness audit

At the observed target-close boundary the active machine controls had been reconciled to the canary: scheduler fence classifies declared predictive wakes separately from stale wakes; handoff recovery forbids conflicting substantive takeover while predecessor is fresh; runtime continuity/runtime mode/relay policy preserve one substantive authority; the canary ledger and CI structural checks are present; the same canonical predictive due remained armed rather than being replaced by a second automation.

This is the predecessor's last materially useful canary boundary. The successor must use its own actual observation and first-useful timestamps; no successor timing is inferred here.

## Evidence to fill by successor

| Field | Observed value |
|---|---|
| predictive due | 17:11:16 KST |
| successor observed | **PENDING** |
| predecessor last useful | **17:11:46 KST** |
| predecessor durable close | **17:11:46 KST target boundary; commit timestamp is corroborating evidence** |
| successor first useful | **PENDING** |
| post-close useful-work gap | **PENDING** |
| early overlap observed | **PENDING** |
| fence result | **PENDING** |
| duplicate substantive side effect | **PENDING** |
| schedule rollback | **PENDING** |
| canary result | **PENDING** |

## Promotion rule

One success is insufficient. Require two safe handoffs with post-close gap <=42 seconds and no duplicate substantive side effect/schedule rollback, then demonstrate a valid fixed 900-second utilization window before broader promotion.
