# Commercial Agent SaaS Competitive Baseline

Status: living reference, not a parity claim.

## Why this exists

RRuleR's program goal is not merely to keep a relay alive. It is to become a production-oriented autonomous agent runtime/control plane that can credibly compete with commercial agent SaaS for long-running work. This document records externally observed product capabilities that define the moving target.

## Current external reference points

Observed from current vendor/product documentation in September 2026:

- **ChatGPT Work**: can stay with complex projects for hours, break goals into smaller steps, work across apps/files, use a cloud browser, and continue after the user leaves; scheduled tasks can also keep work moving.
- **Manus**: Agent Mode autonomously plans/completes complex tasks; Cloud Computer provides an always-on persistent VM/filesystem for 24/7 applications, bots, and scripts.
- **Lindy 3.0**: emphasizes easy agent creation, cloud-computer/browser-style action through Autopilot, thousands of integrations, and centralized team deployment/monitoring.
- **Relevance AI Workforce**: emphasizes visual multi-agent orchestration, specialized agent teams, enterprise integrations, task observability, feedback, scaling and management.

Reference pages:
- https://openai.com/index/chatgpt-for-your-most-ambitious-work/
- https://help.openai.com/en/articles/20001280-using-cloud-browser-in-chatgpt
- https://help.manus.im/en/articles/15392111-what-is-the-cloud-computer
- https://www.lindy.ai/blog/lindy-3-0
- https://relevanceai.com/workforce

## Competitive dimensions

RRuleR should be measured against the following, not against feature-count alone:

1. **Useful-work utilization** — how much wall-clock relay time becomes substantive progress rather than dead air.
2. **Persistence** — can a fresh/disposable session reconstruct exact work and continue without conversational memory?
3. **Recovery** — does failure recover without duplicate harmful effects or long idle gaps?
4. **Orchestration** — can work be delegated/parallelized when doing so improves completion?
5. **Tool reach** — can adapters reach the systems needed for useful work?
6. **Observability/control** — can an operator understand current owner, progress, failure, utilization, handoff and next action quickly?
7. **Completion verification** — can the system prove outcome/receipt rather than trust self-report?
8. **Governance/security** — are authority, approvals, sensitive data and irreversible effects controlled?
9. **Usability/reproducibility** — can a fresh user/session operate or rebuild the runtime from durable artifacts?

## Current strategic judgment

**P0 = useful-work utilization.**

RRuleR already has substantial durable-state, fencing, recovery, handoff and validation machinery. Those mechanisms do not yield a competitive runtime if a worker routinely performs only a few minutes of useful work in each 15-minute opportunity. Therefore capability expansion must not distract from fixing utilization first.

Initial utilization acceptance target: >=840 seconds evidenced useful work in a 900-second intended turn, across >=3 valid turns with no unexplained internal progress gap >120 seconds.

After P0 passes, utilization remains a protected regression SLO while the program advances the weakest remaining competitive dimension.

## R&D rule

When a live intervention fails, do not merely restate the policy or retry it. Treat the failure as evidence. Localize the cause, inspect internal traces, consult external prior art when useful, generate alternatives, implement the highest-expected-effect correction, validate it, and retest live.
