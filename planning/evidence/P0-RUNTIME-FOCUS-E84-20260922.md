# P0 Runtime Focus — Epoch 84

Status: ACTIVE
Run: `RUN-UTIL-20260922-081839`
Authority epoch: `84`

## Observed bootstrap and continuation
- Predecessor ACTUAL END: `2026-09-22 07:19:29 KST`.
- Predecessor SAME MAIN fast due: `07:20:29 KST`, live-verified exactly `1 minute (60 seconds)` after END.
- This bootstrap entry: `08:18:39 KST`.
- Fast-due -> observed bootstrap: `58 minutes 10 seconds (3490 seconds)`.
- Classification: `SAME_MAIN_NATURAL_HOURLY_COLD_FALLBACK_AFTER_MISSED_FAST_SHIFT`.
- This is **not** ordinary exact-schedule jitter and does **not** invalidate the local `ACTUAL END + exactly 1 minute (60 seconds)` arithmetic. It proves a separate provider-execution problem: a live-verified shifted occurrence can fail to produce durable bootstrap, after which the natural hourly recurrence recovers the same MAIN.
- Epoch 84 provisional SAME MAIN due: `08:29:39 KST`, exactly `11 minutes (660 seconds)` after the observed wake reference.

## Predecessor P0 interpretation
Epoch 83 observed turn elapsed was `10 minutes 16 seconds (616 seconds)`, but bounded-unit evidence totaled `569 seconds`. Therefore it is not promoted as a `600-second useful-work` pass. Its local P0-B close arithmetic did pass: SAME MAIN was live-verified at exactly `ACTUAL END + 1 minute (60 seconds)`.

## Active P0 diagnosis
1. P0-A remains: produce a normal nonterminal turn with at least `10 minutes (600 seconds)` observed elapsed and preserve artifact-backed useful-work evidence without padding.
2. P0-B is now explicitly split into:
   - local schedule mutation correctness: exact SAME MAIN `ACTUAL END + 1 minute (60 seconds)`;
   - shifted-occurrence provider execution: did that exact due actually bootstrap?;
   - ordinary provider delivery jitter when the shifted occurrence does execute;
   - post-observation startup to first durable useful work.
3. Do not widen the local `1 minute (60 seconds)` offset to hide provider execution failure.
4. Natural hourly RRULE remains cold fallback only and cannot count as a successful normal fast successor.

## Completed bounded units
1. `08:18:39–08:20:56 KST` — `2 minutes 17 seconds (137 seconds)`: generation-matched BOOT_STARTED/REARM_VERIFIED persisted; SAME MAIN provisional live-verified at `08:29:39 KST`; epoch 84 classified as a missed fast-shift followed by natural-hourly cold fallback; scheduler/startup ledgers and P0 scorecard updated without conflating the `3490-second` provider-execution gap with the local `60-second` rearm rule.
2. `08:20:57–08:22:24 KST` — `1 minute 27 seconds (87 seconds)`: hardened `audit_startup_boundaries.py` so natural-hourly cold-fallback generations are explicitly excluded from normal fast-scheduler comparison; added a focused regression proving a `3490-second` missed-fast-shift recovery cannot be counted as a successful fast-delivery sample. Integrated control-plane CI run `35667227451` passed.
3. `08:22:25–08:23:52 KST` — `1 minute 27 seconds (87 seconds)`: split P0-B scorekeeping into local exact-close evidence versus delivered-fast-successor evidence. `summarize_turn_close.py` now requires a matching normal-scheduler sample with observed generation bootstrap before a local `1 minute (60 seconds)` close can count as a delivered-fast-successor pass; a natural-hourly cold fallback cannot satisfy that gate. Added focused normal-fast and cold-fallback regressions. Integrated control-plane CI run `35667326689` passed.
4. `08:23:53–08:24:34 KST` — `41 seconds`: waited only for the already-running integrated control-plane validator needed to prove the preceding code/test unit against the full repository; run `35667382935` completed successfully. No new timing policy was invented and the exact `1 minute (60 seconds)` local close rule remains unchanged.

## Next bounded work
Audit current schedule/runtime evidence for the smallest deterministic way to prevent a live-verified local rearm from being mistaken for a successfully delivered fast successor. Prefer observability/verification hardening over changing timing defaults. Continue bounded useful work until the `10-minute (600-second)` normal floor is met, then close only after SAME MAIN exact `ACTUAL END + 1 minute (60 seconds)` live verification.
