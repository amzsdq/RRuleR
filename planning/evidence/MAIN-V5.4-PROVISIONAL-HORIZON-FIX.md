# MAIN v5.4 provisional horizon correction — 2026-09-22

## Incident
- Previous active policy armed the SAME MAIN at target work 600s + 180s margin = 780s (~13m), which exposed a next-due around 01:33 for a turn that began around 01:19.
- Operator live mutation proved the SAME recurring MAIN accepts materially earlier DTSTART values.
- A temporary v5.3 +2m rolling policy was tested/reviewed and immediately rejected before promotion.

## Evidence used
- Prior controlled reservation A/B in amzsdq/R issue #504:
  - SHORT_ROLLING (+2m repeated): FAIL; durable overlap/duplicate invocation evidence.
  - LONG_PROVISIONAL (+11m): PASS; >600s measured envelope, no observed overlap, no normal mid-turn mutation, final end+1m verified.
  - Foreman recommendation: ADAPTIVE_HYBRID / workload-relative long provisional.
- Current 01:30:15 MAIN occurrence recorded last_run_time about 01:30:17 but no generation-matched new BOOT_STARTED was durable by >01:33. Invocation metadata alone therefore remains insufficient bootstrap evidence.

## Adopted v5.4 policy
- Normal ~10m envelope: arm SAME MAIN once at wake +660s (~11m).
- No routine mid-turn schedule mutation.
- If useful work or required close handling clearly threatens the provisional due, extend SAME MAIN once before collision (preferred NOW+180s), then verify.
- Normal nonterminal CONTINUE voluntary hard floor remains 600 observed elapsed seconds.
- Normal close remains exact actual END+60 with SAME enabled recurring canonical.
- +780s/13m provisional retired as unnecessarily long.
- repeated +2m rolling provisional retired as unsafe default.
- Watchdog remains disabled break-glass standby.

## Rollback
Pre-v5.3 baseline is preserved at branch:
rollback/pre-short-rolling-provisional-20260922
