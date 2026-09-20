# ADR-002 — GitHub Actions as an independent wake-pulse producer

Status: CANDIDATE, NOT ACTIVE
Date: 2026-09-21

## Finding

GitHub officially documents two properties relevant to RRuleR:

- scheduled Actions workflows have a minimum interval of **5 minutes**;
- standard GitHub-hosted Actions usage is free for public repositories.

RRuleR is public, so a small scheduled workflow could act as an independent **event producer**: every five minutes it could update the dedicated `event-wake-lab` PR branch, generating a PR commit-update event for a ChatGPT Work event-trigger task.

This is different from using Actions as the reasoning worker. The runner would only generate a public-safe wake pulse; ChatGPT remains the reasoning runtime and GitHub `main` remains durable state.

Sources checked 2026-09-21:
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- https://docs.github.com/en/billing/concepts/product-billing/github-actions

## Potential value

If a Work GitHub event trigger is provisioned and reliable, a five-minute independent pulse bounds worst-case wake delay much more tightly than the current quarter-hour fallback even when the prior reasoning invocation dies before it can emit its own successor event.

The best architecture may therefore be hybrid:

1. worker-controlled event chaining for fast handoff when the worker survives long enough to checkpoint;
2. GitHub Actions 5-minute pulse as liveness rescue when the worker disappears before emitting;
3. quarter-shift ChatGPT scheduled task as a slower independent fallback.

This forms three different failure domains rather than asking one mechanism to provide planning, liveness and recovery.

## Critical caveat

A wake is useful only if the event-triggered Work invocation can perform the durable RRuleR reads/writes it needs. Official standard ChatGPT GitHub app documentation describes normal repository access as read-only for analysis/search. Therefore **write capability of the triggered Work worker is a hard prerequisite**. Do not activate a pulse workflow until that capability is proven in a bounded test.

## Candidate pulse design

When/if the prerequisite passes:

- `on.schedule`: every 5 minutes (documented minimum);
- permissions: `contents: write` only, no secrets;
- target: dedicated `event-wake-lab` branch only;
- payload: generation-independent pulse ID + timestamp, no private data;
- no mutation of `main` workflow authority/state;
- pulse consumer deduplicates by PR head SHA/event ID;
- pulse cannot advance authority by itself;
- disable automatically after the bounded experiment window or on storm evidence.

## Decision

Do not activate yet. Keep as the highest-value rescue-producer candidate behind the event-triggered Work write-capability gate.
