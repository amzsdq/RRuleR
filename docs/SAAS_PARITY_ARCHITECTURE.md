# Structural SaaS Parity Architecture

Status: target architecture and acceptance framework  
Date: 2026-09-21

## Scope

This document deliberately separates **model quality** from **runtime/control-plane quality**.

A commercial platform may use a stronger hosted model. RRuleR's structural target is different: if given a comparable reasoning model, the runtime should not be materially behind on persistence, recovery, scheduling, orchestration, side-effect safety, observability, operator control, governance, and reproducibility.

Model/provider quality is therefore an adapter dimension, not part of the structural parity score.

## External structural reference points

Current production systems establish several expectations:

- durable workflow systems persist execution state and resume after process or infrastructure failure;
- agent runtimes expose checkpoint/pause/resume and retry behavior;
- commercial agent products provide schedules and event triggers;
- agent products expose queues/task status and cancellation;
- multi-agent/subagent delegation is a normal capability;
- human approval can pause consequential actions and resume them later;
- operator views expose current tasks, history, failures, performance and resource use;
- permissions, app/tool restrictions and audit controls are product features rather than prompt conventions.

These are capability classes, not claims that every vendor implements each one identically.

## Architecture gates

### G1 Durable Resume

A disposable reasoning worker can disappear and a cold worker can reconstruct exact work from durable state.

Required evidence:
- checkpoint lineage;
- cold-start reconstruction test;
- no dependence on hidden chat memory.

### G2 Scheduling / Wake Adapters

Time-based, event-based and manual wakes feed the same durable continuation contract.

Required evidence:
- rolling time adapter accepted live;
- at least one independent event adapter accepted;
- scheduler swap does not change correctness semantics.

### G3 Side-effect Safety

At-least-once delivery is allowed; duplicate harmful execution is not.

Required evidence:
- authority fencing;
- idempotency key or effect receipt;
- ambiguity reconciliation before replay;
- stale-worker finalization test.

### G4 Recovery

Worker/session/tool/scheduler failure is detected and work continues without blind replay.

Required evidence:
- abrupt-loss fault injection;
- measured detection and recovery latency;
- preserved verified state.

### G5 Delegation

A coordinator can safely split independent work, assign workers, and reconcile results.

Required evidence:
- distinct worker identity/authority;
- dependency-aware fan-out;
- duplicate-claim prevention;
- convergence/acceptance proof.

### G6 Queue / Backpressure

Runnable work is represented as an explicit queue rather than implicit prompt selection.

Required evidence:
- priority ordering;
- concurrency/admission limit;
- cancellation;
- retry/exhaustion or quarantine;
- poison-task behavior;
- starvation check.

### G7 Human Control

Consequential actions may durably pause for approval or escalation without losing state.

Required evidence:
- approval request is durable;
- execution pauses before the guarded side effect;
- approve/deny resumes deterministically;
- timeout/escalation path is explicit.

### G8 Observability

An operator can answer quickly:

- what is running;
- who owns it;
- what packet is active;
- what completed;
- what failed;
- what is waiting;
- next action;
- utilization/recovery latency;
- queue pressure;
- tool/model/cost usage when available.

Required evidence:
- one machine-readable scorecard;
- reproducible report/dashboard source;
- no invented timing values.

### G9 Governance

Authority and tool reach are scoped and auditable.

Required evidence:
- role/capability contract;
- sensitive-data isolation;
- negative permission tests;
- approval boundaries for consequential effects;
- public-safe persistence.

### G10 Version / Replay Safety

An in-flight durable job survives policy/runtime upgrades without silently changing semantics.

Required evidence:
- versioned contracts;
- compatibility/migration rules;
- replay or deterministic historical-state test;
- incompatible migration fails closed.

### G11 Reproducibility

A fresh user/session can reconstruct the runtime from durable artifacts with low manual setup.

Required evidence:
- bootstrap acceptance test from a cold session;
- documented minimum setup;
- machine validation of mandatory artifacts.

## Current RRuleR position

### Relatively strong

- durable GitHub state;
- explicit authority/fencing concepts;
- cold-start checkpoint philosophy;
- completion evidence;
- side-effect reconciliation design;
- public-safe durable boundary;
- rolling continuation experiment and recovery-oriented scheduler design.

### Partial / still proving

- live recovery SLO;
- event wake adapter;
- delegation;
- unified observability;
- governance enforcement tests;
- rolling RRULE production evidence.

### Material structural gaps

1. explicit queue/backpressure controller;
2. durable human approval/interrupt-resume contract;
3. proven multi-worker fan-out/convergence;
4. version/replay compatibility suite;
5. unified operator scorecard including cost/tool/queue/approval state;
6. cold bootstrap acceptance test.

## Priority rule

Until utilization/recovery is stable, do not expand features in a way that reintroduces idle gaps or weakens correctness.

After that baseline is protected, choose the next gate by:

```text
expected structural risk reduction
x frequency of use
x competitive importance
/ implementation and regression cost
```

Do not optimize feature count.

## Near-term implementation sequence

1. Land rolling RRULE + predecessor-planned successor baton as the canonical continuation lifecycle.
2. Remove active quarter-cycle contradictions from policy/tests.
3. Add deterministic scheduler/baton regression tests.
4. Add explicit runnable queue + admission/backpressure contract.
5. Add durable approval interrupt/resume contract.
6. Prove delegation fan-out/convergence using the queue and authority fences.
7. Add version/replay compatibility tests.
8. Consolidate operator observability into a machine scorecard.
9. Prove a second independent trigger adapter.
10. Run a cold bootstrap/rebuild acceptance test.

## Parity claim rule

RRuleR may claim structural parity for a gate only from evidence.

Architecture documents, prompts, or policy prose alone are not sufficient.
