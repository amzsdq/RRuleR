# RRuleR

Persistent workspace and relay state for ChatGPT-driven R architecture research and automation experiments.

> **Persistence belongs to GitHub. Intelligence belongs to disposable ChatGPT sessions. No session is authoritative; durable state is.**

## Purpose

RRuleR is a public-safe durable control plane and workspace for long-running ChatGPT work. ChatGPT sessions are disposable. A fresh session must be able to reconstruct the current job from GitHub without relying on hidden conversational memory.

## Responsibility split

- **GitHub** — durable truth, checkpoints, control state, policy, evidence, history.
- **ChatGPT sessions** — disposable reasoning/execution workers.
- **ChatGPT Automations** — wake mechanism, never source of truth.
- **GitHub Actions** — deterministic validation, reconciliation, testing, and housekeeping.
- **Private/external storage** — only for material that must not be public.

## Repository map

```text
/
├─ AGENTS.md
├─ control/
│  └─ POLICY.md
├─ state/
│  ├─ CURRENT.json
│  ├─ EVENTS.jsonl
│  └─ README.md
├─ schemas/
│  ├─ current-state.schema.json
│  └─ relay-event.schema.json
├─ docs/
│  ├─ ARCHITECTURE.md
│  ├─ OPERATIONS.md
│  └─ RELAY_RRULE_SELF_UPDATE.md
├─ experiments/
│  └─ rrule-self-relay/
│     └─ README.md
└─ .github/workflows/
   └─ validate-control-plane.yml
```

## Bootstrap order

A fresh session reads:

1. `AGENTS.md`
2. `control/POLICY.md`
3. `state/CURRENT.json`
4. the referenced checkpoint/task/spec
5. `docs/RELAY_RRULE_SELF_UPDATE.md` when operating the relay

Then it reconstructs state, validates authority, establishes the next wake, and immediately performs substantive work.

## Utilization rule

After the next wake is secured, useful-work utilization is a first-class objective.

- Do not voluntarily idle while useful admissible work remains.
- Do not stop because a document, milestone, checkpoint, phase, or quarter-hour boundary was reached.
- Handoff starts only after successor execution is actually observed.
- Once successor is observed, finish the current smallest safe work unit, checkpoint, hand off, and end.
- Correctness invariants still outrank raw activity: no duplicate substantive execution, stale-authority writes, or blind replay of ambiguous effects.

## Public-safety rule

This repository is public. Never persist secrets, session cookies, tokens, passwords, private conversation content, private-repository content, personal data, or other sensitive material. Persist only public-safe state, hashes, opaque references, or sanitized summaries.
