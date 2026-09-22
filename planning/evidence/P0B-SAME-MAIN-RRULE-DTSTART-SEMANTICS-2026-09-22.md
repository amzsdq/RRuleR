# P0-B SAME MAIN RRULE / DTSTART semantics diagnosis — 2026-09-22

Status: ACTIVE EVIDENCE NOTE

## Observed facts

1. Epoch 83 locally live-verified SAME MAIN at ACTUAL END + exactly 1 minute (60 seconds), due 07:20:29 KST. The next eligible bootstrap did not appear until 08:18:39 KST, 58 minutes 10 seconds (3490 seconds) after the intended fast due, consistent with natural-hourly cold fallback.
2. Epoch 84 locally live-verified SAME MAIN at ACTUAL END + exactly 1 minute (60 seconds), due 08:29:51 KST.
3. A separate invocation was observed at 08:28:42 KST, 1 minute 9 seconds (69 seconds) before that pending due. It was fenced and the pending 08:29:51 KST DTSTART was restored before expiry.
4. No eligible bootstrap appeared at 08:29:51 KST. The next eligible bootstrap appeared at 09:29:53 KST, 1 hour 0 minutes 2 seconds (3602 seconds) after the intended fast due, again consistent with the natural-hourly recurrence.
5. Therefore two independent samples now show: local mutation/live reread of a recurring DTSTART is not sufficient evidence that the provider will enqueue an imminent shifted occurrence.

## Prior-art / standards check

RFC 5545 iCalendar recurrence semantics define DTSTART as the first instance in a recurrence set, and FREQ=HOURLY with default INTERVAL=1 as an hourly recurrence anchored by DTSTART. That standard model makes the intended local representation coherent, but it does **not** prove that ChatGPT's automation scheduler dynamically re-enqueues an already-running recurring job when DTSTART is mutated close to now. The provider is allowed to implement scheduling/runtime behavior beyond the abstract iCalendar recurrence representation.

Reference: RFC 5545 sections 3.3.10 and 3.8.5.3.

## Current diagnosis

The dominant P0-B blocker is no longer arithmetic ambiguity. The local close calculation and persisted schedule representation are correct. The blocker is **provider execution semantics for an in-place mutation of a recurring automation while/after its current occurrence is executing**.

Two repeated identical fast-shift attempts have failed to produce an eligible shifted successor. Repeating the same experiment without a changed discriminating variable is low-value.

## Next discriminating experiment

Keep the operator-locked exact local close invariant at ACTUAL END + 1 minute (60 seconds). Do not silently widen it.

Use the already-armed provisional occurrence as a control signal:

- At eligible wake start, arm SAME MAIN to wake reference + exactly 11 minutes (660 seconds) and live-verify it.
- Sustain normal work for at least 10 minutes (600 observed elapsed seconds).
- At close, record whether the provisional occurrence was already accepted/enqueued by the provider before replacing DTSTART with ACTUAL END + exactly 1 minute (60 seconds).
- If the close-time 1-minute mutation again fails while a longer pre-armed occurrence is observed reliably in another controlled sample, the evidence points to a scheduler re-enqueue horizon / mutation-during-run limitation rather than recurrence arithmetic.
- Never permit both occurrences to obtain substantive authority; generation fencing remains mandatory.

## Decision rule

Do not promote a new mechanism until it improves actual eligible successor bootstrap, not merely live schedule metadata. Preserve SAME MAIN hourly recurrence as cold fallback throughout testing.
