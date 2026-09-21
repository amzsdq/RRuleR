# MAIN v5.2 Fresh-Policy-Sync / 600s Hard-Floor Rollback

Date: 2026-09-22 KST

## Purpose

Make the operator-requested v5.2 bootstrap/policy synchronization change explicitly reversible without reactivating retired MAIN canonicals.

## Current canonical invariant

- authoritative MAIN: `6ab152b636748191a71873ba4d5ef551`
- retired and never to be reactivated as MAIN: `6ab14f7951848191b65e4b5d4bc979d8`, `6aaf8a993eb08191b8d0ab1d9662e4b2`
- rollback MUST mutate the same current canonical; it MUST NOT reactivate a retired canonical.

## Repository rollback baseline

Branch `rollback/pre-policy-sync-bootstrap-20260922` is pinned to commit `e34d0a61483621ac85285d2993fd2737552789d7`.

That branch is the pre-v5.2 repository comparison/recovery point. Do not blindly reset operational state files from it after newer work; use it as a diff/recovery source and reconcile forward.

## Previous reservation bootstrap (v5.1)

The previous same-canonical prompt semantics were:

- fresh `state/NOW.json` first;
- generation-matched `BOOT_STARTED`;
- same-MAIN recurring provisional crash insurance and `REARM_VERIFIED`;
- load fresh artifacts required by NOW/ACTIVE_CONTROLS/current authorized work;
- target about 10 elapsed minutes with ~12-minute soft ceiling;
- exact actual END+60 same-MAIN recurring close verification;
- Watchdog disabled break-glass standby;
- retired A/B canonicals never reactivated.

v5.2 added two deliberate changes on top of this baseline:

1. explicit FRESH POLICY SYNC: reload fresh `control/ACTIVE_CONTROLS.json` and its mandatory artifacts every wake; prior-wake cached policy cannot override fresh durable policy;
2. explicit 600-second normal nonterminal CONTINUE voluntary hard floor: CI pending, packet/substep/checkpoint completion, secured continuation, or `nothing obvious` cannot authorize pre-600 voluntary CONTINUE close.

## Rollback procedure

If v5.2 causes a demonstrated regression:

1. keep current canonical `6ab152b636748191a71873ba4d5ef551` enabled; never reactivate retired canonicals;
2. compare main against `rollback/pre-policy-sync-bootstrap-20260922` and identify only the v5.2 regression-causing changes;
3. restore the affected bootstrap/policy semantics on the SAME current canonical and reconcile GitHub controls forward rather than restoring stale operational state wholesale;
4. preserve newer checkpoints/evidence unless they are themselves proven invalid;
5. verify same-MAIN recurrence, enabled state, current authority, and exact close behavior before declaring rollback complete.

## Safety note

This rollback point is not authority to weaken an explicit newer operator directive. If the operator changes the minimum-turn policy later, the newer directive wins and this document remains historical recovery evidence only.
