# P001 Epoch 90 — Trace observability correction

## Finding

The prior failure classification conflated two independent surfaces:

1. **execution/durable progress** — GitHub state and artifacts can advance;
2. **host UI delivery** — an intermediate assistant progress message may not be surfaced as a distinct chat message during a scheduled invocation.

A missing intermediate UI trace therefore cannot, by itself, prove that the work or scheduler mutation failed.

## Correction

Adopt durable-first trace semantics:

- qualifying bounded unit completes;
- observed duration + artifact evidence are persisted;
- trace is appended to `state/TURN_TRACES.json` as `TRACE_DURABLY_RECORDED`;
- if reliable intermediate delivery exists, transition to `TRACE_INTERMEDIATE_DELIVERED`;
- otherwise retain the trace and flush it in order in the turn completion response as `TRACE_FINAL_FLUSH_DELIVERED`;
- trace state never grants close authority.

## Implementation evidence

- `AGENTS.md@f2f8cbb2db13e4617a8b21ad82afecb2547beaee` — portable scheduled-runtime trace contract and corrected scheduler adapter name.
- `state/TURN_TRACES.json@83cde5efede8b65a99c0d0952133461bc5196269` — ordered durable trace ledger.
- `schemas/turn-traces.schema.json@7e3d867af1c4d2dc0a4679f7afd85cee0c396608` — ledger schema.
- `tools/validate_turn_traces.py@98b2cf15ac9fee306cdece76f705b94503e262cf` — deterministic validation of identity, delivery-state declaration, evidence, chronology, and terminal final-flush phase.
- `tests/test_validate_turn_traces.py@3114b704b5a76f4935234207c68ef9b7e77d3226` — 10 focused validator regressions.
- `tools/append_turn_trace.py@d86571cfd7269b3b9b10df0134a515f2d9141359` + `tests/test_append_turn_trace.py@e44763c8c4555382f86f74716a45a480eac61b7d` — guarded append path and 3 focused tests.
- `.github/workflows/validate-turn-traces.yml@06cd795abcce77cc1da3fa0c66d3bee526336a22` — dedicated validation workflow.

## Scheduler evidence kept separate

Epoch 89 final due was `10:57:13 KST`; epoch 90 invocation was observed at `10:58:12 KST`, a provider delivery offset of **59 seconds late**. This is recorded in `state/SCHEDULER_OBSERVATIONS.json@af3934f673ec6b413f604b148aed76ee131dcdcf`. It supports the final-writer mechanism surviving return, but does not count as useful work.

## Decision

**ADOPT** durable-first/final-flush trace observability. **DO NOT** change the SAME MAIN full-VEVENT RRULE mechanism based on missing intermediate chat messages. The dominant remaining P0 failure is sustained work duration: a normal `CONTINUE` still must reach at least 10 minutes (600 observed elapsed seconds), and scheduler/trace bookkeeping alone must not be promoted as useful work.
