# Design Decisions

## D1 — GitHub is durable authority

**Decision:** ADOPT.

Persistent control state, checkpoints, policy, evidence, and resumable work state belong in GitHub. ChatGPT session context is non-authoritative.

**Reason:** sessions are disposable and may cold-start.

## D2 — Automation prompt is a wake/bootstrap pointer, not work memory

**Decision:** ADOPT.

The automation prompt may carry stable bootstrap instructions and canonical identity, but mutable substantive work state belongs in GitHub.

**Reason:** prompt-embedded work state becomes stale and makes recovery dependent on scheduler metadata.

## D3 — RRULE phase rotation for one-slot 15-minute effective cadence

**Decision:** ADOPT FOR CURRENT EXPERIMENT.

Keep one recurring hourly RRULE and rotate `BYMINUTE` through `00 -> 15 -> 30 -> 45 -> 00` using the same canonical automation.

**Reason:** it reuses one automation slot and, if an update fails while the old RRULE remains intact, retains a slower hourly recovery opportunity.

## D4 — One-shot conversion

**Decision:** REJECT for this mechanism.

Converting to one-shot removes the recurring fallback property and changes the mechanism being tested.

## D5 — Voluntary stop at quarter boundary

**Decision:** REJECT.

A scheduled boundary is a wake opportunity, not a work-duration quota. Predecessor continues useful work until successor execution is actually observed or another legitimate terminal/block condition occurs.

**Reason:** useful-work utilization is a first-class objective.

## D6 — Depend on same-canonical overlap

**Decision:** REJECT as correctness dependency.

Overlap/queue behavior may be measured and exploited if proven, but durable continuation must work even if the platform serializes same-canonical runs.

## D7 — Checkpoint means yield

**Decision:** REJECT.

Checkpointing preserves recoverability. It does not by itself authorize idle or end the run.

## D8 — Public repository may contain secrets because GitHub supports Secrets

**Decision:** REJECT.

RRuleR is designed as public-safe persistence. Secret-bearing state belongs outside the public durable control plane unless a future design introduces an explicit private boundary.

## D9 — Optimize utilization by allowing duplicate work

**Decision:** REJECT.

Utilization is optimized only after correctness constraints: authority, no duplicate substantive execution, reconciliation of ambiguous effects, and safe handoff.

## Review trigger

Revisit a decision only with new platform evidence, a demonstrated failure mode, or a material simplification that preserves the same safety property.
