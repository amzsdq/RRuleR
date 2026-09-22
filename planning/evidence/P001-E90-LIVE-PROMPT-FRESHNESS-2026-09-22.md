# P001 Epoch 90 — Live MAIN prompt freshness

At 11:06:40 KST, live automation metadata for canonical `6ab152b636748191a71873ba4d5ef551` showed a fresher bootstrap prompt: **v5.7.0 STRICT ORDERED RRULE SELF-UPDATE**, while this wake had begun from v5.6.5 text.

Decision: **preserve the fresher live v5.7.0 prompt and never write the older prompt back**. Scheduler updates in this wake therefore mutate only the `schedule`/enabled/timing fields required by the final-writer contract and do not include a prompt replacement.

Compatibility: v5.7.0 still requires SAME automation ID, complete recurring VEVENT with `RRULE:FREQ=HOURLY`, `is_enabled=true`, `exact_schedule`, 11-minute (660-second) provisional crash insurance, >=10-minute (600-second) normal work floor, and ACTUAL END + 1 minute (60 seconds) final RRULE write. Its immediate separate chat-trace request is treated as a delivery request; durable execution evidence remains independent so a host UI delivery omission cannot be misclassified as work failure.

This is a stale-prompt rollback prevention event, not a scheduler redesign.
