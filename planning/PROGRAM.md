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

The current program P0 is **useful-work utilization**. Existing safety and correctness constraints remain guardrails, but should not consume the roadmap unless they materially advance the north-star outcome.

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

Reason: the runtime is not SaaS-competitive if scheduled availability exists but useful work occupies only a small fraction of it. Utilization is therefore the current bottleneck and must be solved before expanding feature breadth.

## Next project

Default: **P002 — Durable Recovery & Cold Resume Hardening**.

This is a default, not a sacred rule. At P001 exit, re-score the competitive dimensions and select the highest expected-effect project. If the evidence says another project is more valuable, update this roadmap.

## Program completion

PROGRAM_COMPLETE requires credible evidence across the success dimensions above. Completing one project, CI suite, document, experiment, or architecture layer is not program completion.
