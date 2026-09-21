# WS-P001-002 — Sustained Turn Utilization

Status: **ACTIVE**  
Parent project: [P001 — Sustained Utilization & Continuous Execution](../projects/P001-SUSTAINED-UTILIZATION.md)

## Problem

Continuation survival is high, but actual wake utilization is materially lower than the target. Recent work also showed the strict `WORK_EVIDENCE` ledger lagging far behind the current authority epoch, weakening visibility into whether the utilization objective is improving.

## Outcome

Make one bounded wake spend most of its available execution budget on substantive, authorized work, and keep measurement fresh enough to prove or falsify the improvement.

## Scope

- Establish a trustworthy baseline of real useful-work occupancy per wake.
- Repair/replace stale evidence capture so current turns are measurable without manual historical backfill.
- Identify the dominant causes of short turns / idle gaps.
- Implement the highest-expected-effect corrections.
- A/B or repeated-window test corrections where useful.
- Keep correctness, fencing, idempotency, public-repo safety, and cold-rescue constraints intact.

## Non-scope

- Adding controls merely because a theoretical edge case exists.
- Removing controls merely to reduce rule count.
- Feature breadth unrelated to the active utilization bottleneck.
- Treating scheduler survival as equivalent to useful-work utilization.

## Acceptance

- [x] Current-turn useful-work evidence is captured without multi-epoch lag.
- [ ] Baseline wake utilization is computed from durable evidence with unknown time left unknown.
- [ ] Dominant causes of under-utilization are ranked by measured impact.
- [ ] At least one correction is implemented against the highest-impact cause.
- [ ] The correction is retested across multiple valid windows/turns.
- [ ] Results either meet P001 thresholds or produce a durable next experiment based on evidence.

Acceptance progress: **1 / 6**

## Evidence-pipeline diagnosis and repair (2026-09-21)

`state/WORK_EVIDENCE.json` was a strict acceptance ledger, not an automatic activity feed. Its last accepted record was authority epoch 43 even though `state/CURRENT.json` advanced to epoch 58. No collector/generator existed under `tools/`; evidence insertion depended on the active worker explicitly persisting qualifying observed intervals. Later turns continued to create substantive artifacts without advancing this ledger. This was the direct cause of the multi-epoch freshness gap.

Repair applied:
- added `tools/append_work_evidence.py`, which computes duration from caller-supplied observed boundaries and rejects duplicate IDs, overlaps, naive timestamps, and invalid resulting ledgers;
- added focused regression tests and integrated them into control-plane CI;
- added forward evidence capture to the worker bootstrap contract;
- persisted `WE-20260921-E59-001` during the resumed turn, proving the ledger can advance with the active epoch without historical inference.

This fixes the capture-path omission, but does not retroactively claim epochs 44-58 as useful time. Those intervals remain unknown unless independently observed evidence already proves them.

## Exact resume step

1. Verify integrated CI for the new append path.
2. Produce a current baseline from durable run/activity/commit evidence without inventing missing time.
3. Rank the dominant causes of under-utilization from that baseline.
4. Choose the next intervention by expected effect on useful-work occupancy, not by proximity of the code being inspected.

## Decision rule

Any rule/control/process change is valid if its net expected contribution to the P001 outcome is positive. More rules are acceptable when they materially improve the outcome; fewer rules are preferable only when protection/effect is preserved or improved.
