# RRuleR Architecture

## Responsibility boundary

| Layer | Responsibility | Authoritative? |
|---|---|---|
| GitHub repository | durable state, checkpoints, policy, evidence, work history | Yes |
| ChatGPT scheduled session | reasoning and substantive work | No |
| ChatGPT automation | wake/continuation trigger | No |
| GitHub Actions | deterministic checks/reconciliation | Only for facts they verify |
| Chat STATUS output | human-visible handoff receipt | No |

## Cold-start requirement

A fresh successor must be able to answer from GitHub alone:

- What is the root goal?
- What is the current status?
- Who owns authority?
- What checkpoint is verified?
- What has already been attempted?
- Which side effects may already have occurred?
- What is the exact next action?
- What continuation mechanism should wake the next run?

If not, the previous run did not checkpoint enough state.

## Terms

- **TURN** — one logical ownership interval.
- **RUN** — one actual ChatGPT execution.
- **WORK UNIT** — smallest meaningful safely checkpointable unit.
- **CHECKPOINT** — durable continuation state.

Task phases do not need to align with TURN boundaries.

## Continuous-work principle

Workers do not stop merely because research ended, writing began, a milestone was crossed, or a schedule boundary approaches. Scheduler boundaries rotate executors; they do not define business phases.

## Runtime handoff

At handoff:

1. stop starting new large units;
2. finish current smallest safe unit;
3. persist checkpoint, duration/progress, and exact next action;
4. emit concise STATUS and end;
5. successor reconstructs and continues.

If same-automation overlap/queue is unsupported, use `clean-stop -> next scheduled wake -> resume` rather than depending on simultaneous predecessor/successor execution.
