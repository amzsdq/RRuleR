# Event-trigger provisioning specification

Status: READY FOR BOUNDED PROVISIONING TEST — trigger itself not provisioned by the scheduled relay.

## Target

Create one ChatGPT Work event-triggered task for `amzsdq/RRuleR` draft PR #1 (`Event Wake Lab — controlled continuation lane`) using **pull-request commit updates** if that trigger is exposed in the account UI/schema.

Do not target all repository activity. Do not target `main` pushes. Keep the event surface isolated to PR #1 / `event-wake-lab` if the trigger condition supports that specificity.

## Trigger condition

Preferred:

- Connected app: GitHub
- Repository: `amzsdq/RRuleR`
- Event family: pull request activity
- Event: commit update / new commits on PR
- Condition: PR number == 1 (or head branch == `event-wake-lab`)

Fallback test events if commit-update is not exposed by the product surface: PR comment or ready-for-review transition, but do not adopt either for a self-chain until recursion and write semantics are re-evaluated.

## Worker prompt contract

The event-triggered worker must treat the event as a **wake pointer only**. It must:

1. Read fresh `AGENTS.md`, `state/CURRENT.json`, `control/runtime-continuity.v1.json`, `control/event-wake-candidate.v1.json`, `state/EVENT_WAKE_LEDGER.json`, `state/TURN_PLAN.json`, and relevant handoff/activity state.
2. Extract/derive the event identity supplied by the trigger. If a stable provider event ID is unavailable, derive a deterministic ID from PR number + observed head SHA.
3. Reject a duplicate event ID before substantive work.
4. Verify event generation / expected authority against durable state. Never roll authority backward.
5. Record event observation and latency evidence.
6. If the predecessor is fresh, request handoff or do only non-conflicting preparation. If stale, use the existing recovery contract.
7. Resume the same durable primary objective rather than starting a new unrelated objective.
8. After at least one meaningful checkpoint and only if the candidate test permits another generation, emit at most one next-generation commit to the dedicated PR lane.
9. Merely acknowledging the incoming event must never emit another event.
10. Keep the quarter-shift scheduled relay enabled as fallback throughout the test.

## Bounded first test

Maximum: 3 event generations.

Abort event emission immediately on any of:

- duplicate substantive execution;
- authority rollback or ambiguous owner;
- more than one unacknowledged generation;
- trigger storm / unexpected repeated delivery;
- event payload exposing sensitive material;
- event-to-first-work latency that is not materially better than the quarter baseline after enough samples to judge.

## Success evidence

For each generation record:

- source PR head SHA / event ID;
- source event timestamp when available;
- worker observed timestamp;
- first substantive progress timestamp;
- event-to-observation seconds;
- event-to-first-work seconds;
- useful work performed;
- predecessor/successor overlap;
- dedupe result;
- authority epoch before/after.

Promotion requires at least 3 safe generations, zero duplicate substantive executions, zero authority rollback, zero unbounded storm, and median event-to-first-work latency materially below the quarter-wake baseline.

## Why this is promising

Official OpenAI documentation currently states that eligible event-triggered tasks can run up to 30 times/hour and that GitHub PR activity may include commit updates. If the product exposes this trigger for the connected repository, the dedicated PR lane can act as a supported no-API wake bus while GitHub `main` remains the durable workflow state.
