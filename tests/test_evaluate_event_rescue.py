import unittest
from datetime import datetime

from evaluate_event_rescue import evaluate


NOW = datetime.fromisoformat("2026-09-21T21:00:00+09:00")


def base():
    return (
        {"program_status": "CONTINUE"},
        {"last_progress_at": "2026-09-21T20:59:30+09:00"},
        {"status": "ACTIVE", "consumer_status": "VERIFIED", "outstanding_generation": None},
        {"next_sample": {}},
    )


class EventRescueEvaluationTests(unittest.TestCase):
    def test_inactive_ledger_never_emits(self):
        current, activity, ledger, startup = base()
        ledger["status"] = "INACTIVE_CANDIDATE"
        self.assertEqual(evaluate(current, activity, ledger, startup, NOW)["reason"], "LEDGER_INACTIVE")

    def test_unverified_consumer_never_emits(self):
        current, activity, ledger, startup = base()
        ledger["consumer_status"] = "UNVERIFIED"
        self.assertEqual(evaluate(current, activity, ledger, startup, NOW)["reason"], "EVENT_CONSUMER_UNVERIFIED")

    def test_outstanding_generation_prevents_storm(self):
        current, activity, ledger, startup = base()
        ledger["outstanding_generation"] = 7
        self.assertEqual(evaluate(current, activity, ledger, startup, NOW)["reason"], "OUTSTANDING_GENERATION")

    def test_missing_boot_ack_becomes_rescue_reason(self):
        current, activity, ledger, startup = base()
        startup["next_sample"] = {"sample_id": "S6", "successor_observed_at": "2026-09-21T20:57:00+09:00", "boot_started_at": None}
        result = evaluate(current, activity, ledger, startup, NOW)
        self.assertTrue(result["emit"])
        self.assertEqual(result["event_reason"], "STARTUP_ACK_MISSING")

    def test_recent_missing_boot_ack_waits(self):
        current, activity, ledger, startup = base()
        startup["next_sample"] = {"sample_id": "S7", "successor_observed_at": "2026-09-21T20:59:00+09:00", "boot_started_at": None}
        self.assertFalse(evaluate(current, activity, ledger, startup, NOW)["emit"])

    def test_stale_owner_is_secondary_rescue_reason(self):
        current, activity, ledger, startup = base()
        activity["last_progress_at"] = "2026-09-21T20:56:00+09:00"
        result = evaluate(current, activity, ledger, startup, NOW)
        self.assertEqual(result["event_reason"], "STALE_ACTIVE_OWNER")

    def test_terminal_program_never_emits(self):
        current, activity, ledger, startup = base()
        current["program_status"] = "PROGRAM_COMPLETE"
        self.assertEqual(evaluate(current, activity, ledger, startup, NOW)["reason"], "PROGRAM_TERMINAL")


if __name__ == "__main__":
    unittest.main()
