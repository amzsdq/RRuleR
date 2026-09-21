# RRuleR Planning Spine

This directory is the durable planning hierarchy between the program goal and turn-level execution.

## Hierarchy

```text
PROGRAM
  -> PROJECT
      -> WORK SPEC
          -> state/NOW.json
              -> state/TURN_PLAN.json
```

Reference model:
- Strategic initiatives group projects around an objective.
- Projects have a clear outcome and contain smaller execution units.
- Hierarchical work items make progress roll up from small work to the larger goal.

RRuleR keeps that model deliberately small: Program -> Project -> Work Spec -> NOW.

## Canonical responsibilities

### `planning/PROGRAM.md`
- North-star goal.
- Competitive success dimensions.
- Ordered project roadmap.
- Current project and next project.
- Project-level progress roll-up.

### `planning/projects/*.md`
- One outcome-oriented project.
- Why it advances the program.
- Completion criteria.
- Work specs belonging to the project.
- Project progress.

### `planning/work-specs/*.md`
- Implementable unit of work.
- Scope / non-scope.
- Acceptance checklist.
- Evidence.
- Current status and exact next step.

### `state/NOW.json`
- Single machine-readable pointer to the current program/project/work spec.
- Current execution state (including operator pause).
- Exact resume target.
- Must never become a second plan.

### `state/TURN_PLAN.json`
- The bounded plan for one execution turn only.
- It must implement the active work spec; it must not invent a different strategy.

## Status vocabulary

Use only:
- `BACKLOG`
- `READY`
- `ACTIVE`
- `BLOCKED`
- `PAUSED`
- `DONE`
- `CANCELED`

## Progress rule

Do not use subjective percent-complete as authoritative truth.

Progress is reported as:
- work spec: completed acceptance items / total acceptance items;
- project: DONE work specs / committed work specs;
- program: DONE projects / committed projects, plus competitive-dimension evidence.

A parent may not be marked DONE unless its documented acceptance criteria are satisfied.

## Anti-local-optimization rule

Before selecting substantive work, verify:

1. Which PROGRAM goal does this advance?
2. Which PROJECT owns the outcome?
3. Which WORK SPEC authorizes the work?
4. Is the proposed next step the highest-expected-effect runnable step for that work spec?

If a proposed action cannot answer those four questions, do not execute it merely because it is nearby or easy.

Rules, controls, tests, and process are means. Add, modify, consolidate, or retire them according to net contribution to the program objective, not according to rule count or age.

## Updating progress

When a durable result changes completion state:
1. update the relevant work-spec checklist/evidence;
2. update project roll-up if a work spec changes status;
3. update PROGRAM roadmap if a project changes status/order;
4. update `state/NOW.json`;
5. only then create/update the next `TURN_PLAN`.
