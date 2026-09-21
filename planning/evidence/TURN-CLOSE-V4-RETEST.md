# Turn-close v4 retest

Scope: WS-P001-002. Operator-authorized repair of premature bounded-turn close.

## Implemented

- One close decision in run-continuation-gate v4; completing a small unit alone never permits close.
- Runnable primary/fallback/residual task selection in the existing TURN_PLAN.
- Pause check before write batches and scheduler mutation.
- Elapsed time separated from accepted useful work.
- New closed records validated in CI, including omitted duration/outcome and unsupported short-close reasons. Pre-migration observations remain historical evidence, not rewritten successes.
- Validation boundary: turns starting on or after 2026-09-21T09:35:00Z.

## Next worker's runnable work

Check fresh state before choosing; skip already accepted work.

1. Primary: implement `tools/summarize_turn_close.py` to report v4 closed-turn counts, unexcused short closes, known useful seconds, unknown-useful count and explicitly observed successor gaps from RUNS/SUCCESSOR_STARTUP. Acceptance: missing useful seconds and missing successor boundaries remain unknown, never zero; add focused fixtures. No future wake dependency. Estimate 3-5 minutes, checkpoint at pure function plus fixtures; conflict domain turn-close-reporting.
2. Independent fallback: implement a read-only STARTUP ledger consistency audit. Acceptance: flag predecessor last-useful later than that predecessor's recorded end; exclude operator-maintenance-interrupted samples from scheduler comparison, while preserving raw evidence. Target `tools/audit_startup_boundaries.py` and focused tests. No schedule mutation or future wake required. Estimate 2-4 minutes; checkpoint at audit plus fixtures; conflict domain startup-evidence-audit.
3. Residual item: inspect current bounded-close CI result and document concrete baseline/candidate evidence in this file. Acceptance: link exact commit/run result and separate local tests from Actions and live behavior. Estimate 1-2 minutes; checkpoint at evidence update. If CI is pending, select another acceptance item; do not repeatedly poll as useful work.

These are implementation candidates, not duplicate-work mandates. Record actual estimates and runnable status in TURN_PLAN. If all finish, choose the next unaccepted item within WS-P001-002. Do not end simply because this list completed.

## Live acceptance

Collect at least three valid completed post-repair turns with runnable backlog. Report each observed elapsed duration, known useful duration (or unknown), exception evidence, control/close overhead where observed, and successor gap where observed. Explicit pauses and forced termination are exclusions, not successes. No unexcused early CONTINUE close is allowed; do not call the repair effective solely because elapsed duration grew. Useful output must increase without duplicate/conflicting writes. Scheduler latency remains a separate outcome. Retain the 10-minute envelope and existing ownership fences. Do not promote scheduler timing from this repair.

Status: focused local tests passed; live retest pending.
