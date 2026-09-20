# Durable State

`CURRENT.json` is the compact machine-readable projection of the current root job.

It is intentionally small. Detailed history belongs in Git commits, experiment records, task/spec documents, or future append-only event records.

Required properties:

- public-safe;
- sufficient for cold-start reconstruction;
- explicit owner/authority epoch;
- explicit latest checkpoint;
- explicit exact next action;
- explicit continuation mode;
- no secrets or private source material.

Chat output may summarize this state but cannot override it.
