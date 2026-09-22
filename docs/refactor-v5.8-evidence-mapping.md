# v5.8 Refactor Evidence Mapping

Status: candidate evidence note; not an active runtime contract.

## Operator-provided relay experiment summary

The supplied RRULE relay study materially strengthens the minimal-runtime direction. Its strongest experimentally grounded findings are:

- same automation ID can self-update successfully;
- recurring RRULE should remain present;
- clean normal turns favored one final scheduler mutation rather than repeated rolling mutations;
- the scheduler update return object can be sufficient verification on clean success, with extra read-back reserved for anomalies;
- the tested 3-minute lead class was more reliable than the tested 2-minute class, but is not a platform guarantee;
- minimal checkpoint/tail restore can replace full-state reads on normal turns;
- append-only or immutable evidence is safer than repeated whole-ledger rewrites;
- normal success logs can be compact while exception paths remain explicit;
- Git history is a useful recovery source;
- next research should emphasize fault injection, soak testing, concurrent-authority collisions, and actual useful-work duty cycle rather than more rule accumulation.

## Design consequence

These findings are treated as evidence-backed adaptive defaults, not immutable product laws.

The v5.8 candidate therefore keeps only a small invariant core, treats the RRULE mechanism as a replaceable adapter, uses the 3-minute class as an experimental baseline, shortens the normal scheduler path to one final mutation, and moves verbose verification/recovery work to exception paths.

## Still unproven

Do not generalize the current 3-minute class to all environments. The candidate still requires long-run soak testing, missed-wake and duplicate-invocation fault injection, scheduler/GitHub failure recovery tests, concurrent-authority tests, and direct useful-progress-per-wall-clock measurement before promotion.
