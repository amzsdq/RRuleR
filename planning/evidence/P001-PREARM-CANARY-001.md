# P001 PREARM-CANARY-001

Status: **ARMED / awaiting observed successor**  
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

## Safety contract

An early successor may read/fence/observe but must not claim conflicting substantive authority while the predecessor remains fresh. Authority advances only after a fresh durable read proves committed close/nonconflicting transfer or valid stale-owner recovery. Any duplicate substantive side effect, schedule rollback, unsafe overlap, or missed successor fails the canary and restores the verified completion-relative fallback.

## Evidence to fill by successor

| Field | Observed value |
|---|---|
| predictive due | 17:11:16 KST |
| successor observed | **PENDING** |
| predecessor last useful | **PENDING** |
| predecessor durable close | **PENDING** |
| successor first useful | **PENDING** |
| post-close useful-work gap | **PENDING** |
| early overlap observed | **PENDING** |
| fence result | **PENDING** |
| duplicate substantive side effect | **PENDING** |
| schedule rollback | **PENDING** |
| canary result | **PENDING** |

## Promotion rule

One success is insufficient. Require two safe handoffs with post-close gap <=42 seconds and no duplicate substantive side effect/schedule rollback, then demonstrate a valid fixed 900-second utilization window before broader promotion.
