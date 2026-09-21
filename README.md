# RRuleR

Persistent workspace and relay state for ChatGPT-driven R architecture research and automation experiments.

> **Persistence belongs to GitHub. Intelligence belongs to disposable ChatGPT sessions. No session is authoritative; durable state is.**

## Purpose

RRuleR is a public-safe durable control plane and workspace for long-running ChatGPT work. ChatGPT sessions are disposable. A fresh session must reconstruct current work from GitHub rather than relying on hidden conversational memory.

## Responsibility split

- **GitHub** — durable truth, checkpoints, control state, policy, evidence, history.
- **ChatGPT sessions** — disposable reasoning/execution workers.
- **ChatGPT Automations** — wake/continuation adapter, not dynamic policy authority.
- **GitHub Actions** — deterministic validation, reconciliation, testing, and housekeeping.
- **Private/external storage** — only for material that must not be public.

## Repository map

```text
/
├─ AGENTS.md
├─ planning/
│  ├─ PROGRAM.md
│  ├─ projects/
│  ├─ work-specs/
│  └─ evidence/
├─ control/
│  ├─ ACTIVE_CONTROLS.json
│  ├─ POLICY.md
│  ├─ relay-policy.v1.json
│  ├─ run-continuation-gate.v1.json
│  └─ ...
├─ state/
│  ├─ NOW.json
│  ├─ CURRENT.json
│  ├─ ACTIVITY.json
│  ├─ HANDOFF.json
│  ├─ TURN_PLAN.json
│  ├─ STARTUP_ACK.json
│  ├─ RUNS.jsonl
│  └─ ...
├─ schemas/
├─ docs/
├─ experiments/
├─ tests/
├─ tools/
└─ .github/workflows/
```

## Bootstrap order

A fresh wake/session:

1. reads fresh `state/NOW.json` and obeys explicit STOP/PAUSE/terminal state;
2. performs the minimum canonical/fence check and persists generation-matched `BOOT_STARTED`;
3. secures and verifies provisional recurring crash insurance on the SAME current MAIN and persists `REARM_VERIFIED`;
4. reloads fresh `control/ACTIVE_CONTROLS.json` and every artifact it currently marks mandatory;
5. reconstructs PROGRAM -> PROJECT -> WORK SPEC -> TURN_PLAN and current authority;
6. performs substantive authorized work.

Prior-wake cached policy must not override fresh active durable controls. Bootstrap/reservation text is a survival kernel; dynamic policy lives in GitHub except explicit operator and canonical-safety invariants.

## Current continuation semantics

Normal continuation is self-reliant SAME MAIN continuation:

`MAIN -> SAME MAIN at observed END+60 -> MAIN`

The current authoritative MAIN remains an enabled recurring hourly RRULE. During a turn it is provisionally moved beyond the bounded turn as crash insurance. At normal close, after actual END is observed, the SAME MAIN is shifted to exact `END+60s`, recurrence is preserved, and live metadata is re-read to verify same canonical + enabled + recurring + exact DTSTART.

The recurring RRULE itself is the cold fallback if a shifted fast wake is lost. Watchdog is disabled break-glass standby and is not a normal continuity dependency. Retired MAIN canonicals are never reactivated.

## Normal CONTINUE 10-minute hard floor

A normal nonterminal `CONTINUE` turn has a **600-second voluntary hard floor** and about a **720-second soft ceiling**.

Before 600 observed elapsed seconds:

- chain the next clear low-risk checkpointable authorized unit;
- decompose an oversized unit;
- if the primary path waits on CI/external evidence, choose an independent fallback/residual authorized unit;
- do not close merely because a packet, substep, checkpoint, CI result, or continuation setup completed;
- `nothing obvious` is not a close condition.

A voluntary normal `CONTINUE` close before 600 seconds is forbidden. Earlier end is reserved for explicit operator STOP/PAUSE, durable program terminal state, genuine BLOCKED/fail-closed authority/safety state with no safe authorized work, or platform-enforced termination. Never pad or invent busywork.

At/after 600 seconds, stop starting new large units, finish only the smallest safe in-flight unit, checkpoint, perform the exact SAME MAIN close gate, and end the bounded turn.

## Utilization measurement

Elapsed START-to-END is not automatically useful work. Accepted useful time requires observed artifact-backed evidence; missing time remains unknown.

The bounded 600-second turn and the P0 acceptance window are intentionally different concepts. Current P0 measurement uses fixed 900-second windows with >=840 seconds of evidenced useful coverage and requires multiple valid windows before PASS. Scheduler delivery, startup, authority, useful work, close, and next-wake timing are measured separately.

See `docs/UTILIZATION.md` and the active machine-readable controls for current details.

## Durable correctness layer

`docs/DURABLE_EXECUTION_MODEL.md` defines scheduler-independent correctness: fenced authority/leases, cold-start checkpoints, idempotent effect receipts, completion verification, liveness, and recovery. Scheduler mechanisms may change without weakening those invariants.

## Public-safety rule

This repository is public. Never persist secrets, session cookies, tokens, passwords, private conversation content, private-repository content, personal data, or other sensitive material. Persist only public-safe state, hashes, opaque references, or sanitized summaries.

## Program goals

1. Build RRuleR toward credible competitiveness with commercial long-running agent systems on persistence, recovery, orchestration, observability, verification, governance, usability, and sustained useful work.
2. P0 until proven: meet the active >=840/900 evidenced useful-coverage gate across the required valid windows without weakening correctness or hiding scheduler/startup loss.

See `planning/PROGRAM.md` for the roadmap, `state/NOW.json` for the active planning pointer, `state/PROGRAM_GOALS.json` for machine-readable goals, and `docs/COMPETITIVE_BASELINE.md` for the competitive reference baseline.
