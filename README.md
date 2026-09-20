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
│  ├─ POLICY.md
│  └─ relay-policy.v1.json
├─ state/
│  ├─ CURRENT.json
│  ├─ HANDOFF.json
│  ├─ EVENTS.jsonl
│  └─ README.md
├─ schemas/
│  ├─ current-state.schema.json
│  ├─ handoff.schema.json
│  ├─ relay-event.schema.json
│  └─ run-observation.schema.json
├─ docs/
│  ├─ ARCHITECTURE.md
│  ├─ FAILURE_RECOVERY.md
│  ├─ HANDOFF_PROTOCOL.md
│  ├─ OPERATIONS.md
│  ├─ RELAY_RRULE_SELF_UPDATE.md
│  ├─ SECURITY.md
│  ├─ STATE_MODEL.md
│  └─ UTILIZATION.md
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
3. on relay runs, `control/relay-policy.v1.json`
4. `state/CURRENT.json`
5. the referenced checkpoint/task/spec
6. `docs/RELAY_RRULE_SELF_UPDATE.md` when operating the relay

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
