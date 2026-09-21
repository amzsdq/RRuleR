# RRuleR Program

Status: **ACTIVE**  
Program ID: `RRULER-PROGRAM-001`

## North-star goal

Build RRuleR into a **production-oriented autonomous agent runtime/control plane that can credibly compete with commercial agent SaaS for long-running autonomous work**.

This is the highest planning authority below explicit operator direction and safety/platform constraints.

## Success dimensions

RRuleR is judged on outcomes, not feature count:

- Useful-work utilization
- Persistence / cold-start continuation
- Failure recovery
- Safe orchestration and delegation
- Tool reach
- Observability and operator control
- Completion / side-effect verification
- Governance and security
- Usability and reproducibility

The current program has two operator-locked co-equal P0 blockers:

1. **P0-A — Turn worktime / sustained useful work:** normal nonterminal `CONTINUE` turns must sustain at least **10 minutes (600 observed elapsed seconds)** of chained authorized work unless a truthful early-exit exception applies, while useful-work evidence remains distinct from elapsed time.
2. **P0-B — Exact schedule rearm / continuation latency:** normal close must mutate the **SAME enabled recurring MAIN** to **ACTUAL END + exactly 1 minute (60 seconds)**, live-verify the exact `DTSTART`, persist the same due across durable projections, and measure provider delivery/startup latency separately.

Until both are stably proven and retained as regression gates, other product/runtime expansion is secondary unless it directly improves one of these two P0s or preserves required safety/correctness.

## Project roadmap

| Order | Project | Status | Progress | Exit / handoff condition |
|---|---|---|---|---|
| 1 | [P001 — Sustained Utilization & Continuous Execution](projects/P001-SUSTAINED-UTILIZATION.md) | **ACTIVE** | 1 / 3 committed work specs DONE | P0 sustained-useful-work gate passes and is retained as regression SLO |
| 2 | P002 — Durable Recovery & Cold Resume Hardening | READY AFTER P001 | not decomposed | Recovery/persistence are proven under abrupt loss, not merely designed |
| 3 | P003 — Safe Delegation & Parallel Orchestration | BACKLOG | not decomposed | Delegation improves throughput without authority/side-effect ambiguity |
| 4 | P004 — Observability & Operator UX | BACKLOG | not decomposed | Operator can rapidly see health, progress, failure, utilization and next action |
| 5 | P005 — Tool Reach & Adapter Productization | BACKLOG | not decomposed | Replaceable adapters cover useful external work surfaces |
| 6 | P006 — SaaS-grade Productization, Security & Reproducibility | BACKLOG | not decomposed | Fresh user/session can deploy and operate safely with low manual setup |

Project ordering after P001 may change if evidence shows a different remaining dimension has higher expected effect on SaaS competitiveness.

## Current project

**P001 — Sustained Utilization & Continuous Execution**

Reason: the current dominant defects are not feature breadth. They are (A) insufficient or prematurely terminated work inside a wake and (B) incorrect/ambiguous next-wake timing after close. P001 therefore treats sustained turn worktime and exact completion-relative schedule rearm as the two highest-priority runtime outcomes before broader productization.

## Next project

Default after both active P0 gates pass: **P002 — Durable Recovery & Cold Resume Hardening**.

This is a default, not a sacred rule. At P001 exit, re-score the competitive dimensions and select the highest expected-effect project. If the evidence says another project is more valuable, update this roadmap.

## Program completion

PROGRAM_COMPLETE requires credible evidence across the success dimensions above. Completing one project, CI suite, document, experiment, or architecture layer is not program completion.

## Product-direction discipline

Product/runtime design ideas are evaluated by expected effect on active goals, not by feature count. The current recursive-development loop is: observe a measured bottleneck -> check prior art / existing mechanisms -> generate a reversible candidate -> estimate benefit/cost/risk -> test -> verify against fixed evidence -> ADOPT / REVISE / ROLLBACK / REJECT. Stable objectives must not be rewritten merely to make an experiment pass.

Natural-language turn reporting is a **distribution UX contract**, not a replacement for precise internal telemetry. During runtime debugging/canaries, evidence-bound machine-style traces may remain visible. The eventual distribution renderer should summarize observed work time, completed work, status, and next action in natural language while preserving exact machine evidence underneath.
