# Clean MAIN startup generation fence — 2026-09-22

Scope: WS-P001-002 continuation reliability on authoritative clean MAIN `6ab152b636748191a71873ba4d5ef551`.

## Observed wake

- Expected generation: `DUE:2026-09-22T00:58:13+09:00`.
- Automation invocation entered this turn at 01:01:03 KST.
- Generation-matched `BOOT_STARTED` was persisted before broad restore/substantive work.
- SAME MAIN was then live-verified enabled with recurring `RRULE:FREQ=HOURLY` and provisional due 01:20:00 KST; `REARM_VERIFIED` was persisted.
- Both retired MAIN canonicals remained disabled. Watchdog remained disabled standby.

## Repair

`tools/audit_startup_boundaries.py` now binds a durable BOOT receipt to its scheduler generation: when `boot_started_at` and `generation_key` exist, `boot_started_authority_epoch` must equal `generation_key`. A mismatched receipt fails with `STARTUP_ACK_BOOT_EPOCH_GENERATION_MISMATCH`.

Focused regression coverage in `tests/test_audit_startup_boundaries.py` includes a stale BOOT receipt from the preceding generation and preserves valid early-delivery behavior when the receipt is generation-matched.

## Self-review correction

The first implementation rewrite unintentionally reduced the legacy startup-audit output/CLI surface. Commit-level diff review caught this before close. The tool was restored from the pre-change full implementation and the generation-fence change was reapplied as a narrow additive patch. Existing predecessor fields, unacknowledged-error handling, recovery/operator/canary counters, raw-evidence policy, and CLI contract are preserved.

A separate integrated-CI defect was also found in the custom-recurring validation branch: it referenced undefined variable `active` instead of the loaded `controls` registry. This was corrected with a one-line change.

## Validation status

- Exact remote commit diffs were inspected after restoration.
- GitHub Actions was observed starting on the restored source; no PASS is claimed until a completed successful run is observed.
- Local container execution could not be used because its network could not resolve github.com. This is recorded as an execution-path limitation, not as a test pass or product blocker.

## Next

Observe the integrated CI result without converting a pending/cancelled concurrency run into success. If the latest source fails, inspect the concrete failing invariant/test and repair forward. Continue rolling utilization evidence collection; this repair is not program completion.
