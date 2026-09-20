# Utilization feasibility model

Date: 2026-09-21
Status: diagnostic model, not measured SLO evidence

## Purpose

Separate two causes of low utilization:

1. how long a reasoning invocation performs useful work before disappearing (`S`);
2. how long until another worker can start (`W`, effective wake/continuation interval including delivery latency).

A simple upper-bound intuition, ignoring overlap/latency/coordination overhead, is:

`coverage_fraction <= min(1, S / W)` when every wake starts one worker and workers do not overlap usefully.

This is not the production metric; real acceptance still requires evidenced useful intervals. It is a feasibility screen for wake architectures.

## Sensitivity using epoch-16 span

Epoch 16 produced only 145 seconds from substantive start to last meaningful progress.

- 15-minute / 900-second wake: 145 / 900 = **16.1%** theoretical span coverage.
- 5-minute / 300-second rescue pulse: 145 / 300 = **48.3%**.
- 2-minute / 120-second event cadence: 145 / 120 = **120.8%**, meaning overlap becomes possible and the wake interval is no longer the obvious limiting factor.

This explains why more policy cannot rescue a 145-second worker under a 900-second wake interval.

## Epoch-17 live signal

Epoch 17 started substantive work at 00:46:24 KST and had meaningful durable progress at least through 00:56:04 KST: endpoint span **580 seconds**. This is already 4x epoch 16's 145-second span, although it is not yet a valid 840-second coverage result because endpoint span cannot prove continuous work.

At `S = 580`:

- 900-second wake: 64.4% endpoint-span ceiling intuition;
- 300-second rescue pulse: wake interval is shorter than observed worker span, allowing overlap/recovery before expected worker death;
- 120-second event chain: ample overlap budget if delivery/action latency is low enough.

## Required target relation

To sustain >=840 useful seconds per 900-second window without useful overlap, the system needs either:

- a single invocation with evidenced useful span near 840 seconds; or
- continuation/wake latency sufficiently below the worker lifetime that successor generations cover the window with small gaps.

The architecture should therefore optimize the pair `(S, W)`, not `S` alone.

## Practical decision rule

- If `S` repeatedly approaches 840, prioritize long-objective execution and fast final handoff; event infrastructure becomes optional resilience.
- If `S` stabilizes well below 840 but above ~300, a 5-minute independent pulse may be enough to prevent long dead tails.
- If `S` stabilizes near 100-200 seconds, a 5-minute pulse cannot meet high utilization by itself; a lower-latency event chain/background worker substrate is required.
- If event-triggered Work cannot write durable state, reject self-chaining regardless of attractive trigger frequency.

## Measurement warning

Do not convert these ratios into reported utilization. They are architectural upper-bound heuristics. Actual P0 acceptance remains based on durable useful-work intervals, successor observation, and unexplained-gap exclusion in `state/UTILIZATION.json`.
