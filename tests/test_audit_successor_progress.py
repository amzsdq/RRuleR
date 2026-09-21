import unittest
from datetime import datetime

from audit_successor_progress import audit


NOW = datetime.fromisoformat("2026-09-21T20:00:00+09:00")


class AuditSuccessorProgressTests(unittest.TestCase):
    def test_observed_without_claim_is_flagged(self):
        data = {"samples": [{"sample_id": "S1", "successor_observed_at": "2026-09-21T19:55:00+09:00"}]}
        result = audit(data, NOW, 120)
        self.assertEqual(result["findings"][0]["code"], "MISSING_AUTHORITY_CLAIM_AFTER_INVOCATION")
        self.assertFalse(result["findings"][0]["promotion_eligible"])

    def test_claim_without_useful_is_flagged(self):
        data = {"next_sample": {"sample_id": "S2", "successor_observed_at": "2026-09-21T19:54:00+09:00", "authority_claim_at": "2026-09-21T19:56:00+09:00"}}
        result = audit(data, NOW, 120)
        self.assertEqual(result["findings"][0]["code"], "MISSING_FIRST_USEFUL_AFTER_CLAIM")

    def test_complete_sample_is_not_flagged(self):
        data = {"samples": [{"sample_id": "S3", "successor_observed_at": "2026-09-21T19:54:00+09:00", "authority_claim_at": "2026-09-21T19:55:00+09:00", "first_durable_useful_at": "2026-09-21T19:56:00+09:00"}]}
        self.assertEqual(audit(data, NOW, 120)["findings"], [])

    def test_recent_missing_boundary_waits_for_threshold(self):
        data = {"samples": [{"sample_id": "S4", "successor_observed_at": "2026-09-21T19:59:30+09:00"}]}
        self.assertEqual(audit(data, NOW, 120)["findings"], [])

    def test_existing_exclusion_is_preserved(self):
        data = {"samples": [{"sample_id": "S5", "successor_observed_at": "2026-09-21T19:50:00+09:00", "validity": "INCOMPLETE", "exclusion_reason": "MISSING_DURABLE_SUCCESSOR_PROGRESS"}]}
        finding = audit(data, NOW, 120)["findings"][0]
        self.assertEqual(finding["exclusion_reason"], "MISSING_DURABLE_SUCCESSOR_PROGRESS")

    def test_stage_tracked_invocation_without_boot_ack_is_distinct(self):
        data = {"samples": [{"sample_id": "S6", "successor_observed_at": "2026-09-21T19:50:00+09:00", "boot_started_at": None, "rearm_verified_at": None}]}
        finding = audit(data, NOW, 120)["findings"][0]
        self.assertEqual(finding["code"], "MISSING_BOOTSTRAP_ACK_AFTER_INVOCATION")

    def test_boot_without_verified_rearm_is_distinct(self):
        data = {"samples": [{"sample_id": "S7", "successor_observed_at": "2026-09-21T19:50:00+09:00", "boot_started_at": "2026-09-21T19:51:00+09:00", "rearm_verified_at": None}]}
        finding = audit(data, NOW, 120)["findings"][0]
        self.assertEqual(finding["code"], "MISSING_REARM_VERIFICATION_AFTER_BOOTSTRAP")

    def test_stage_complete_sample_reaches_existing_claim_check(self):
        data = {"samples": [{"sample_id": "S8", "successor_observed_at": "2026-09-21T19:50:00+09:00", "boot_started_at": "2026-09-21T19:50:10+09:00", "rearm_verified_at": "2026-09-21T19:50:20+09:00", "authority_claim_at": None}]}
        finding = audit(data, NOW, 120)["findings"][0]
        self.assertEqual(finding["code"], "MISSING_AUTHORITY_CLAIM_AFTER_INVOCATION")


if __name__ == "__main__":
    unittest.main()
